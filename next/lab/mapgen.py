"""Deterministic independent map pools, encoded by the pinned official MapBuilder WASM."""
from __future__ import annotations

from collections import deque
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile

from . import core


def mirror(p, width, height):
    return width - 1 - p[0], height - 1 - p[1]


def validate(m: dict) -> None:
    w, h = m["width"], m["height"]
    if not (24 <= w <= 64 and 24 <= h <= 64 and m["champions"] in (3, 4, 5)):
        raise ValueError("Unsupported map dimensions or draft size")
    terrain = {k: {tuple(p) for p in m[k]} for k in ("walls", "holes", "bushes", "altars")}
    camps = {(x, y): t for t, x, y in m["camps"]}
    for tiles in terrain.values():
        if any(mirror(p, w, h) not in tiles for p in tiles):
            raise ValueError("Terrain symmetry is broken")
    if any(camps.get(mirror(p, w, h)) != t for p, t in camps.items()):
        raise ValueError("Camp symmetry is broken")
    spawn = {(x, y) for x in range(1, 4) for y in range(1, 4)}
    spawn |= {mirror(p, w, h) for p in list(spawn)}
    blocked = terrain["walls"] | terrain["holes"] | terrain["altars"] | camps.keys()
    if spawn & blocked:
        raise ValueError("Blocked spawn or camp in spawn")
    if len(terrain["altars"]) < 2:
        raise ValueError("Need at least two altars")
    if any(not (0 <= x < w and 0 <= y < h) for x, y in blocked | terrain["bushes"]):
        raise ValueError("Out-of-bounds terrain")
    if len(camps) != len(m["camps"]) or not camps:
        raise ValueError("Missing or overlapping camps")
    if terrain["walls"] & terrain["holes"] or (terrain["walls"] | terrain["holes"]) & (terrain["altars"] | camps.keys()):
        raise ValueError("Overlapping blocking terrain")
    visited = {(1, 1)}
    queue = deque(visited)
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b):
            p = (x + dx, y + dy)
            if 0 <= p[0] < w and 0 <= p[1] < h and p not in blocked and p not in visited:
                visited.add(p)
                queue.append(p)
    if not spawn <= visited:
        raise ValueError("Spawn areas disconnected")
    for x, y in camps.keys() | terrain["altars"]:
        if not any((x + dx, y + dy) in visited for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
            raise ValueError("Resource has no reachable melee approach")


def layout(seed: int) -> dict:
    """Generate without consulting match outcomes; rejected geometry uses deterministic retries."""
    rng = random.Random(seed)
    for _ in range(100):
        w, h = rng.choice((28, 32, 36, 40, 44, 48)), rng.choice((28, 32, 36, 40, 44, 48))
        cells = {k: set() for k in ("walls", "holes", "bushes", "altars")}
        for x, y in ((w // 2 - 3, h // 2), (w // 2 + 2, h // 2 - 1)):
            cells["altars"].add((x, y))
            cells["altars"].add(mirror((x, y), w, h))
        camps = {}
        for _ in range(rng.randint(7, 13)):
            p = rng.randrange(5, w - 5), rng.randrange(5, h - 5)
            other = mirror(p, w, h)
            if p in cells["altars"] or other == p or p in camps:
                continue
            # Local packs form real capture groups; all rewards come from the official rules.
            t = rng.choices(range(6), weights=(30, 20, 22, 18, 3, 7))[0]
            camps[p] = t
            camps[other] = t
        family = seed % 4
        for y in range(5, h - 5):
            for x in range(5, w - 5):
                p = (x, y)
                if p > mirror(p, w, h) or p in camps or p in cells["altars"]:
                    continue
                # Open diagonal travel and a cross-map corridor keep navigation tractable.
                corridor = abs(x / w - y / h) < .06 or abs(y - h // 2) <= 1
                v = rng.random()
                kind = "walls" if v < (.05 + family * .018) else "holes" if v < .10 + family * .018 else "bushes" if v < .22 else None
                if kind and not (corridor and kind in ("walls", "holes")):
                    cells[kind] |= {p, mirror(p, w, h)}
        result = {"seed": seed, "family": family, "width": w, "height": h,
                  "champions": rng.choice((3, 4, 5)), "spawn": [1, 1, 4, 4],
                  **{k: [list(p) for p in sorted(v)] for k, v in cells.items()},
                  "camps": [[t, *p] for p, t in sorted(camps.items())]}
        try:
            validate(result)
            return result
        except ValueError:
            continue
    raise ValueError(f"Could not generate valid geometry for seed {seed}")


def check_existing(path: Path, expected_sha: str) -> None:
    if path.exists() and core.sha(path) != expected_sha:
        raise ValueError(f"Refusing to overwrite a different map: {path}")


def seed_for(split: str, seed: int, index: int) -> int:
    key = f"g1/{split}/{seed}/{index}".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "little")


def engine_path() -> Path:
    expected = core.config()["stage1"]["engine_wasm_sha256"]
    explicit = os.environ.get("CAMBC_ENGINE_WASM")
    roots = [Path(os.environ.get("LOCALAPPDATA", "")) / "cambc/assets", Path.home() / ".cache/cambc/assets"]
    files = [Path(explicit)] if explicit else [p for root in roots for p in root.glob("*/mapeditor/assets/v1_0_0-*.wasm")]
    for p in files:
        if p.is_file() and core.sha(p) == expected:
            return p
    raise SystemExit("Pinned official engine WASM not found; run cambc mapeditor --no-browser once, or set CAMBC_ENGINE_WASM.")


def node() -> str:
    executable = os.environ.get("CAMBC_NODE") or shutil.which("node")
    if not executable:
        raise SystemExit("Node.js 22+ is required for the official engine WASM bridge; set CAMBC_NODE.")
    return executable


def run() -> dict:
    cfg = core.config()["stage1"]
    rows = []
    for split in ("screen", "confirm"):
        for i in range(cfg[f"{split}_maps"]):
            name = f"g1-{split}-{i:03}"
            m = layout(seed_for(split, cfg[f"{split}_seed"], i))
            m.update(name=name, output=str(core.MAPS / "generated" / split / (name + ".map26a")))
            rows.append(m)
    scratch = core.ROOT / ".cambc" / "tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        request = Path(tmp) / "maps.json"
        request.write_text(json.dumps(rows), encoding="utf-8")
        r = subprocess.run([node(), "--no-warnings", str(core.ROOT / "lab/engine.mjs"),
                            str(engine_path()), "maps", str(request)], capture_output=True,
                           text=True, encoding="utf-8", cwd=core.ROOT, timeout=120)
        if r.returncode:
            raise SystemExit(r.stderr[-3000:])
    manifest = {"generator": "g1", "engine_wasm_sha256": cfg["engine_wasm_sha256"],
                "screen_seed": cfg["screen_seed"], "confirm_seed": cfg["confirm_seed"],
                "maps": json.loads(r.stdout)}
    hashes = [r["sha256"] for r in manifest["maps"]]
    if len(hashes) != len(set(hashes)):
        raise SystemExit("Duplicate maps across the generated pools")
    out = core.ROOT / "mechanics/generated-maps-g1.json"
    if out.exists() and json.loads(out.read_text()) != manifest:
        raise SystemExit("Generated map manifest changed; use a new generator version, do not mutate g1.")
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

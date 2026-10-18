"""Freezing versions, playing games, and the results store.

Carson's rules for versions (cb-bc AGENTS.md): version, don't mutate; one change per version;
a changelog line on top. Our repo rule is that a new version is an edit of the bot folder, so
GitHub shows the diff. Both hold here: you edit `bots/<bot>/` in place, and `freeze` keeps an
exact copy of what was built (source + wasm) under `archive/<name>/`, which the league plays.

Every game is stored once, keyed by the two wasm hashes, the map hash, the side order and the
cambc version. The engine is deterministic, so a stored game never needs to be played again.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
import tomllib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from .stats import VERSION as STATS_VERSION, summarize

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive"
RESULTS = ROOT / "results" / "games"
MAPS = ROOT / "maps"
CLI = os.environ.get("CAMBC_CLI", "cambc")
ENV = {**os.environ, "CAMBC_NO_UPDATE_CHECK": "1",
       "CAMBC_WASMTIME_CACHE": os.environ.get("CAMBC_WASMTIME_CACHE", str(ROOT / ".cambc" / "wasmtime-cache"))}


def config() -> dict:
    with open(ROOT / "lab.toml", "rb") as f:
        return tomllib.load(f)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cli_version() -> str:
    return subprocess.run([CLI, "--version"], capture_output=True, text=True, env=ENV).stdout.strip()


# ---------------------------------------------------------------- versions

@dataclass
class Version:
    name: str
    wasm: Path
    meta: dict


def changelog_line(src: Path) -> str:
    """First `// name: text` comment line of src/main.cpp (the changelog line), if any."""
    main = src / "main.cpp"
    if main.exists():
        for line in main.read_text().splitlines()[:5]:
            if line.startswith("//"):
                return line.lstrip("/ ").strip()
    return ""


def freeze(bot_dir: str, name: str, note: str = "", parent: str | None = None) -> Version:
    """Build `bot_dir` in release mode (as on the platform) and store it as version `name`."""
    bot = (ROOT / bot_dir).resolve() if not Path(bot_dir).is_absolute() else Path(bot_dir)
    dest = ARCHIVE / name
    if dest.exists():
        raise SystemExit(f"{name} already exists. Versions are never overwritten; pick a new name.")
    r = subprocess.run([CLI, "build", "--release", str(bot)], capture_output=True, text=True, env=ENV)
    if r.returncode != 0:
        raise SystemExit(f"build failed for {bot}:\n{r.stdout[-3000:]}\n{r.stderr[-3000:]}")
    built = bot / ".cambc" / "build-release" / "bot-injected.wasm"
    dest.mkdir(parents=True)
    shutil.copytree(bot / "src", dest / "src")
    shutil.copy2(built, dest / "bot.wasm")
    git = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(bot)],
                           capture_output=True, text=True).stdout.strip()
    meta = {"name": name, "bot_dir": str(bot.relative_to(ROOT)) if bot.is_relative_to(ROOT) else str(bot),
            "wasm_sha256": sha(dest / "bot.wasm"), "git": git.stdout.strip() + ("+dirty" if dirty else ""),
            "changelog": note or changelog_line(bot / "src"), "cli": cli_version(),
            # the version this one was copied from: by default the champion of the day (lineage tree)
            "parent": config()["league"]["champion"] if parent is None else parent,
            "frozen_at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}
    (dest / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    return Version(name, dest / "bot.wasm", meta)


def version(name: str) -> Version:
    dest = ARCHIVE / name
    if not (dest / "bot.wasm").exists():
        raise SystemExit(f"unknown version {name}: freeze it first (python3 -m lab freeze BOT_DIR {name})")
    return Version(name, dest / "bot.wasm", json.loads((dest / "meta.json").read_text()))


def versions() -> list[str]:
    return sorted(p.name for p in ARCHIVE.iterdir() if (p / "bot.wasm").exists()) if ARCHIVE.exists() else []


# ---------------------------------------------------------------- games

def map_path(name: str) -> Path:
    p = MAPS / f"{name}.map26a"
    if not p.exists():
        raise SystemExit(f"missing map {p}")
    return p


def game_key(a: Version, b: Version, mp: Path, cli: str) -> str:
    h = hashlib.sha256(f"{a.meta['wasm_sha256']}|{b.meta['wasm_sha256']}|{sha(mp)}|{cli}|s{STATS_VERSION}".encode()).hexdigest()
    return h[:24]


TIMEOUT = 300  # seconds per game; a hung bot must not hang the league (Carson's elo.py uses 300 too)


def run_game(a: Version, b: Version, mp: Path, out_dir: str, logs: bool = False) -> tuple[dict | None, str]:
    """Run one game with cambc. Returns (match summary or None, error text)."""
    stats = Path(out_dir) / "stats.json"
    cmd = [CLI, "run", str(a.wasm), str(b.wasm), "--map", str(mp), "-o", out_dir,
           "--statistics", str(stats), "--json", "--release"] + ([] if logs else ["--log-limit", "0"])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, f"timeout after {TIMEOUT} s"
    if not stats.exists():
        return None, (r.stdout[-1500:] + r.stderr[-1500:]).strip() or f"exit code {r.returncode}"
    return json.loads(stats.read_text()), ""


def play_one(a: Version, b: Version, map_name: str, cli: str) -> dict:
    """Play a (side A) vs b (side B) on one map, or return the stored game."""
    mp = map_path(map_name)
    key = game_key(a, b, mp, cli)
    out = RESULTS / f"{key}.json"
    if out.exists():
        rec = json.loads(out.read_text())
    else:
        with tempfile.TemporaryDirectory() as tmp:
            summary, err = run_game(a, b, mp, tmp)
            # A game that does not finish is a result too: it is a crash we must see, never skip.
            rec = summarize(summary) if summary else {"error": err}
        rec.update(key=key, a=a.meta["wasm_sha256"], b=b.meta["wasm_sha256"], map=map_name, cli=cli)
        RESULTS.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rec) + "\n")
    # names are not part of the key (a renamed copy is the same bot), so attach them after loading
    return {**rec, "name_a": a.name, "name_b": b.name}


def default_jobs() -> int:
    return config()["league"].get("jobs") or os.cpu_count() or 4


def play(pairs: list[tuple[str, str]], map_names: list[str], jobs: int, progress=print) -> list[dict]:
    """Every pair on every map, from both sides. Returns one record per game."""
    cli = cli_version()
    vs = {n: version(n) for p in pairs for n in p}
    todo = []
    for x, y in pairs:
        for m in map_names:
            todo.append((vs[x], vs[y], m))
            if x != y:
                todo.append((vs[y], vs[x], m))
    done = []
    with ThreadPoolExecutor(jobs) as ex:
        for i, rec in enumerate(ex.map(lambda t: play_one(*t, cli), todo), 1):
            done.append(rec)
            if i % 20 == 0 or i == len(todo):
                progress(f"  {i}/{len(todo)} games")
    return done


def score_a(rec: dict) -> float | None:
    """Score of side A: 1 win, 0.5 draw, 0 loss; None if the game did not finish."""
    if "error" in rec:
        return None
    return {"teamA": 1.0, "teamB": 0.0}.get(rec["outcome"], 0.5)


def watch(a_name: str, b_name: str, map_name: str, out_dir: Path) -> Path:
    """Replay one game with logs kept and return the replay bundle (open it with `cambc view`).

    Games are deterministic, so this reproduces exactly the game the league stored.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, err = run_game(version(a_name), version(b_name), map_path(map_name), str(out_dir), logs=True)
    if summary is None:
        raise SystemExit(f"game did not finish: {err}")
    return max(out_dir.glob("*.repl26a"), key=lambda p: p.stat().st_mtime)


def bundle(name: str, out: Path) -> tuple[Path, bool]:
    """Zip a frozen version for upload, then rebuild the zip and check it gives the same wasm.

    After kaggriculture: the file you upload must be the bytes that passed the gate, proven by hash.
    """
    v = version(name)
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([CLI, "bundle", str(ARCHIVE / name), "--output", str(out)], capture_output=True, text=True, env=ENV)
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f"bundle failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    with tempfile.TemporaryDirectory() as tmp:
        bot = Path(tmp) / name
        with zipfile.ZipFile(out) as z:
            z.extractall(bot)
        if not (bot / "src").exists():  # some bundles put the files at the root
            (bot / "src").mkdir()
            for f in list(bot.iterdir()):
                if f.name != "src":
                    shutil.move(str(f), bot / "src" / f.name)
        b = subprocess.run([CLI, "build", "--release", str(bot)], capture_output=True, text=True, env=ENV)
        built = bot / ".cambc" / "build-release" / "bot-injected.wasm"
        same = b.returncode == 0 and built.exists() and sha(built) == v.meta["wasm_sha256"]
    return out, same

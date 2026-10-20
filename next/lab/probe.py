"""Regenerate mechanics from a completed release game on a screening map."""
from __future__ import annotations

import json
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

from . import core

FIELDS = ["vision", "move", "range", "hp", "hp growth", "strength", "strength growth",
          "focus", "focus growth", "camp damage x"]
CHAMPIONS = {"ryth", "vesper_vale", "vendetta", "cassi", "issac", "stellar", "prism",
             "marcella", "willow", "ren", "varg", "tavi", "heart_of_ruin"}
CAMPS = {"wolf", "elk", "golem", "gem_cluster", "gold_cluster", "monolith"}
REQUIRED_CONSTANTS = {"ward_cooldown", "altar_lock_hits", "kill_gold", "max_rounds", "winning_gems",
                      "shared_memory_bytes", "draft_memory_bytes", "prism_focus_per_gem",
                      "vesper_vale_bonus_gold_percent", "marcella_tribute_gold_per_gem",
                      "heart_of_ruin_missing_health_damage_max_bonus"}


def parse(text: str) -> dict:
    """Reject truncated/old probe logs rather than publishing an empty mechanics sheet."""
    data = {"constants": {}, "champions": {}, "camps": {}, "dash": [], "cc": []}
    fields = {"CHAMP": ("champions", FIELDS), "CAMP": ("camps", ["hp", "strength", "range"]),
              "DASH": ("dash", ["slot", "range", "radius", "modifier", "duration"]),
              "CC": ("cc", ["slot", "range", "modifier", "duration"])}
    for line in text.replace("\x00", "").splitlines():
        line = line.strip()
        if line.startswith("CONST "):
            _, key, value = line.split()
            if key in data["constants"]:
                raise ValueError(f"Duplicate constant: {key}")
            data["constants"][key] = float(value)
        elif line.split(" ", 1)[0] in fields:
            kind, rest = line.split(" ", 1)
            section, names = fields[kind]
            cells = [c.strip() for c in rest.split("|")]
            if len(cells) != len(names) + 1:
                raise ValueError(f"Incomplete {kind} row: {line}")
            row = dict(zip(names, map(float, cells[1:])))
            if isinstance(data[section], dict):
                if cells[0] in data[section]:
                    raise ValueError(f"Duplicate {kind}: {cells[0]}")
                data[section][cells[0]] = row
            else:
                data[section].append({"champion": cells[0], **row})
    if not REQUIRED_CONSTANTS <= data["constants"].keys():
        raise ValueError("Probe constants are incomplete")
    if set(data["champions"]) != CHAMPIONS or set(data["camps"]) != CAMPS:
        raise ValueError("Probe must cover all 13 champion bodies and all 6 camps")
    if not any(r["champion"] == "heart_of_ruin" for r in data["dash"]):
        raise ValueError("Missing Heart of Ruin dash metadata")
    if not any(r["champion"] == "tavi" for r in data["cc"]):
        raise ValueError("Missing Tavi CC metadata")
    return data


def _table(lines: list[str], heading: str, names: list[str], rows):
    lines += ["", f"## {heading}", "", "| name | " + " | ".join(names) + " |",
              "|---|" + "---|" * len(names)]
    lines += ["| " + name + " | " + " | ".join(f"{row[k]:g}" for k in names) + " |"
              for name, row in rows]


def run(map_name: str | None = None) -> Path:
    screen = core.config()["maps"]["screen"]
    map_name = map_name or ("00corners" if "00corners" in screen else screen[0])
    if map_name not in screen:
        raise SystemExit("The mechanics probe must use a screening map.")
    profile = core.runtime_identity()
    versions = []
    for name in ("probe", "dummy"):
        bot = core.ROOT / "bots" / name
        subprocess.run([core.CLI, "build", "--release", str(bot)], env=core.ENV, check=True,
                       capture_output=True, cwd=core.ROOT, timeout=core.TIMEOUT)
        versions.append(core.Version(name, bot / ".cambc" / "build-release" / "bot-injected.wasm", {}))
    with tempfile.TemporaryDirectory() as tmp:
        summary, error = core.run_game(*versions, core.map_path(map_name), tmp, logs=True, profile=profile)
        if summary is None:
            raise SystemExit(f"Mechanics probe failed: {error}")
        if any(summary["diagnostics"]["botFaults"].values()):
            raise SystemExit("Mechanics probe had bot faults; refusing to publish its output.")
        rep = next(Path(tmp).glob("*.repl26a"))
        with zipfile.ZipFile(rep) as archive:
            text = archive.read("team-a.stdout").decode("utf-8").replace("\x00", "")
    data = parse(text)
    data["provenance"] = {"runtime": profile, "map": map_name,
                          "map_sha256": core.sha(core.map_path(map_name)),
                          "observed_engine_build_hash": summary["match"]["engineBuildHash"],
                          "date_utc": time.strftime("%Y-%m-%d", time.gmtime())}
    out = core.ROOT / "mechanics" / "constants.md"
    out.parent.mkdir(exist_ok=True)
    lines = ["# Engine constants and designs", "",
             f"Printed in a completed release game on `{map_name}` with `{profile['cli']}`.",
             f"Engine build: `{summary['match']['engineBuildHash']}`.", "",
             "Regenerate with `python3 -m lab probe`. Numeric values also live in `constants.json`.",
             "Champion growth is per shard, as defined by the SDK. Camp rewards and respawn times "
             "are not exposed by the design ABI; consult the official patch notes for those fields."]
    _table(lines, "Constants", ["value"], ((k, {"value": v}) for k, v in data["constants"].items()))
    _table(lines, "Champion base stats (growth per shard)", FIELDS, data["champions"].items())
    _table(lines, "Camp base stats", ["hp", "strength", "range"], data["camps"].items())
    for key, names in (("dash", ["slot", "range", "radius", "modifier", "duration"]),
                       ("cc", ["slot", "range", "modifier", "duration"])):
        _table(lines, key.upper() + " abilities", names, ((r["champion"], r) for r in data[key]))
    out.with_suffix(".json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out

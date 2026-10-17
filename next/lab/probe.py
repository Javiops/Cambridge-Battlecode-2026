"""mechanics/constants.md, read from the engine rather than copied from the docs.

Carson's cb-bc keeps a mechanics/ folder of facts the bot relies on. Here the facts are printed by
bots/probe inside a real game, so the notes are regenerated, not remembered, when the engine changes.
"""
from __future__ import annotations

import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

from . import core

FIELDS = ["vision", "move", "range", "hp", "hp growth", "strength", "strength growth",
          "focus", "focus growth", "camp damage x"]


def run(map_name: str = "corners") -> Path:
    bot = core.ROOT / "bots" / "probe"
    subprocess.run([core.CLI, "build", "--release", str(bot)], env=core.ENV, check=True,
                   capture_output=True, cwd=core.ROOT)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([core.CLI, "run", str(bot), str(core.ROOT / "bots" / "dummy"), "--map",
                        str(core.map_path(map_name)), "--rounds", "3", "-o", tmp],
                       env=core.ENV, check=True, capture_output=True, cwd=core.ROOT)
        rep = next(Path(tmp).glob("*.repl26a"))
        text = zipfile.ZipFile(rep).read("team-a.stdout").decode().replace("\x00", "")
    consts, champs = [], []
    for line in (l.strip() for l in text.splitlines()):
        if line.startswith("CONST "):
            _, k, v = line.split(" ", 2)
            consts.append((k, v))
        elif line.startswith("CHAMP "):
            champs.append([c.strip() for c in line[6:].split("|")])
    out = core.ROOT / "mechanics" / "constants.md"
    out.parent.mkdir(exist_ok=True)
    lines = ["# Engine constants and champion stats", "",
             f"Printed by `bots/probe` inside a game ({map_name}, {core.cli_version()}, "
             f"{time.strftime('%Y-%m-%d')}). Regenerate with `python3 -m lab probe`; do not edit by hand.", "",
             "## Constants", "", "| name | value |", "|---|---|"]
    lines += [f"| `{k}` | {v} |" for k, v in consts]
    lines += ["", "## Champions (level 1, growth per level)", "",
              "| # | champion | " + " | ".join(FIELDS) + " |", "|---|---|" + "---|" * len(FIELDS)]
    lines += [f"| {i} | " + " | ".join(c) + " |" for i, c in enumerate(champs)]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out

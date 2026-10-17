"""The lab's command line. Run from next/:

  python3 -m lab freeze bots/dummy dummy-v1       build a bot and keep it as a frozen version
  python3 -m lab list                              frozen versions
  python3 -m lab league [VERSION ...]              round robin of the panel, the champion and VERSIONs on the screen maps
        --maps screen|confirm|all  --mirror (also play each version against itself)  --jobs N
  python3 -m lab gate VERSION                      promotion gate on the confirm maps
"""
from __future__ import annotations

import argparse
import json
import time

from . import core, gate, report


def main() -> None:
    p = argparse.ArgumentParser(prog="lab", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze"); f.add_argument("bot_dir"); f.add_argument("name"); f.add_argument("--note", default="")
    sub.add_parser("list")
    lg = sub.add_parser("league"); lg.add_argument("versions", nargs="*")
    lg.add_argument("--maps", default="screen", choices=["screen", "confirm", "all"])
    lg.add_argument("--mirror", action="store_true"); lg.add_argument("--jobs", type=int)
    lg.add_argument("--out", default="results/REPORT.md")
    g = sub.add_parser("gate"); g.add_argument("version"); g.add_argument("--jobs", type=int)
    a = p.parse_args()
    cfg = core.config()

    if a.cmd == "freeze":
        v = core.freeze(a.bot_dir, a.name, a.note)
        print(f"froze {v.name}: {v.meta['wasm_sha256'][:12]} git {v.meta['git']} · {v.meta['changelog']}")
    elif a.cmd == "list":
        for n in core.versions():
            m = core.version(n).meta
            print(f"{n:24s} {m['wasm_sha256'][:12]}  git {m['git']:14s} {m['changelog']}")
    elif a.cmd == "league":
        names = list(dict.fromkeys(cfg["league"]["panel"] + [cfg["league"]["champion"]] + a.versions))
        maps = cfg["maps"]["screen"] + cfg["maps"]["confirm"] if a.maps == "all" else cfg["maps"][a.maps]
        if a.maps != "screen":
            print("warning: confirm maps are for the gate. Looking at them while tuning turns them into screening maps.")
        pairs = [(x, y) for i, x in enumerate(names) for y in names[i + 1:]]
        if a.mirror:
            pairs += [(x, x) for x in names]
        print(f"league: {len(names)} versions, {len(pairs)} pairings, {len(maps)} maps ({a.maps}), both sides")
        t = time.time()
        games = core.play(pairs, maps, a.jobs or cfg["league"]["jobs"])
        text, summary = report.build(games, f"League report ({a.maps} maps)", cfg["league"]["panel_version"],
                                     cfg["league"]["champion"])
        out = core.ROOT / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        with open(core.ROOT / "results" / "history.jsonl", "a") as h:
            h.write(json.dumps({**summary, "maps": a.maps}) + "\n")
        print(text.split("## Win matrix")[0])
        print(f"{len(games)} games in {time.time() - t:.0f} s · full report: {out.relative_to(core.ROOT)}")
    elif a.cmd == "gate":
        core.version(a.version)
        passed, lines = gate.run(a.version, cfg, a.jobs or cfg["league"]["jobs"])
        out = core.ROOT / "results" / "gates" / f"{a.version}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n")
        print("\n".join(lines))
        raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()

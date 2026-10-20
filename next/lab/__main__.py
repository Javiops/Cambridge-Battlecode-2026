"""The lab's command line. Run from next/:

  python3 -m lab freeze bots/dummy dummy-v1 [--parent V]   build a bot and keep it as a frozen version
  python3 -m lab list                                       frozen versions with parent and changelog
  python3 -m lab league [VERSION ...]                       panel + champion + VERSIONs on the screen maps, both sides
        --maps screen|confirm|all  --mirror (each version also plays itself)  --jobs N
  python3 -m lab gate VERSION                               promotion gate on the confirm maps
  python3 -m lab watch A B MAP                              replay one game (A on side A) and open it in the visualiser
  python3 -m lab bundle VERSION                             upload zip, checked to rebuild the exact gated bytes
  python3 -m lab probe                                      regenerate mechanics/constants.md from the engine
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time

from . import core, dashboard, gate, probe, report


def load_history() -> list[dict]:
    p = core.ROOT / "results" / "history.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def main() -> None:
    p = argparse.ArgumentParser(prog="lab", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze"); f.add_argument("bot_dir"); f.add_argument("name")
    f.add_argument("--note", default=""); f.add_argument("--parent", default=None, help="version it was copied from (default: the champion; \"\" for none)")
    sub.add_parser("list")
    lg = sub.add_parser("league"); lg.add_argument("versions", nargs="*")
    lg.add_argument("--maps", default="screen", choices=["screen", "site", "confirm", "all"])
    lg.add_argument("--mirror", action="store_true"); lg.add_argument("--jobs", type=int)
    lg.add_argument("--out", default="results/REPORT.md")
    g = sub.add_parser("gate"); g.add_argument("version"); g.add_argument("--jobs", type=int)
    w = sub.add_parser("watch"); w.add_argument("a"); w.add_argument("b"); w.add_argument("map")
    w.add_argument("--no-view", action="store_true")
    b = sub.add_parser("bundle"); b.add_argument("version")
    sub.add_parser("probe")
    s = sub.add_parser("stage1")
    s.add_argument("check", choices=["maps", "verify", "benchmark", "calibrate", "ready"])
    a = p.parse_args()
    cfg = core.config()

    if a.cmd == "freeze":
        v = core.freeze(a.bot_dir, a.name, a.note, a.parent)
        print(f"froze {v.name}: {v.meta['wasm_sha256'][:12]} parent {v.meta['parent']} git {v.meta['git']} · {v.meta['changelog']}")
    elif a.cmd == "list":
        for n in core.versions():
            m = core.version(n).meta
            print(f"{n:20s} {m['wasm_sha256'][:12]}  parent {m.get('parent', ''):16s} {m['changelog']}")
    elif a.cmd == "league":
        names = list(dict.fromkeys(cfg["league"]["panel"] + [cfg["league"]["champion"]] + a.versions))
        maps = cfg["maps"]["screen"] + cfg["maps"]["confirm"] if a.maps == "all" else cfg["maps"][a.maps]
        if a.maps in ("confirm", "all"):
            print("warning: confirm maps are for the gate. Looking at them while tuning turns them into screening maps.")
        pairs = [(x, y) for i, x in enumerate(names) for y in names[i + 1:]]
        if a.mirror:
            pairs += [(x, x) for x in names]
        print(f"league: {len(names)} versions, {len(pairs)} pairings, {len(maps)} maps ({a.maps}), both sides")
        t = time.time()
        games = core.play(pairs, maps, a.jobs or core.default_jobs())
        history = load_history()
        text, summary = report.build(games, f"League report ({a.maps} maps)", cfg, history)
        out = core.ROOT / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        dash = out.parent / "dashboard.html"
        dashboard.write(dash, summary, history, text)
        if a.maps == "screen":  # the progression only compares like with like
            with open(core.ROOT / "results" / "history.jsonl", "a") as h:
                h.write(json.dumps({k: v for k, v in summary.items() if not k.startswith("_")} | {"maps": a.maps}) + "\n")
        print(text.split("## Win matrix")[0])
        print(f"{len(games)} games in {time.time() - t:.0f} s · report: {out.relative_to(core.ROOT)} · charts: {dash.relative_to(core.ROOT)}")
    elif a.cmd == "gate":
        v = core.version(a.version)
        passed, lines = gate.run(a.version, cfg, a.jobs or core.default_jobs())
        lines.insert(2, f"Frozen bytes: `bot.wasm` sha256 `{v.meta['wasm_sha256']}` (git {v.meta['git']}). "
                        "Upload only a bundle that `python3 -m lab bundle` proves rebuilds to these bytes.")
        lines.insert(3, "")
        out = core.ROOT / "results" / "gates" / f"{a.version}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines))
        raise SystemExit(0 if passed else 1)
    elif a.cmd == "watch":
        rep = core.watch(a.a, a.b, a.map, core.ROOT / "replays" / f"{a.a}_vs_{a.b}_{a.map}")
        print(f"replay: {rep}")
        if not a.no_view:
            subprocess.run([core.CLI, "view", str(rep)], env=core.ENV)
    elif a.cmd == "bundle":
        out, same = core.bundle(a.version, core.ROOT / "results" / "bundles" / f"{a.version}.zip")
        print(f"{out}: {'rebuilds to the frozen bytes' if same else 'DOES NOT rebuild to the frozen bytes: do not upload'}")
        raise SystemExit(0 if same else 1)
    elif a.cmd == "probe":
        print(f"wrote {probe.run().relative_to(core.ROOT)}")
    elif a.cmd == "stage1":
        from . import mapgen, stage1
        result = {"maps": mapgen.run, "verify": stage1.verify, "benchmark": stage1.benchmark,
                  "calibrate":stage1.calibrate,"ready":stage1.ready}[a.check]()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

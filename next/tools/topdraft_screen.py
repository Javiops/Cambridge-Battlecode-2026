"""Development comparison for a draft-only fork, using the official 1.0.1 runner.

Uses the existing lab statistics validator. Does not consume confirmation maps,
modify lab runtime pins, qualify a candidate, or change the live submission.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab import stats

DRAFT_NAMES = ["Ryth", "Vesper Vale", "Vendetta", "Cassi & Issac", "Stellar", "Prism",
               "Marcella", "Willow", "Ren", "Varg", "Tavi", "Heart of Ruin"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize_opponents(rows):
    """Allow an intentionally absent cohort without hiding missing/unknown games."""
    if not rows:
        raise ValueError("No completed games to summarize")
    if any(row["opponent"] not in ("starter", "baseline") for row in rows):
        raise ValueError("Unexpected opponent in completed captures")
    summaries = {}
    for foe in ("starter", "baseline"):
        group = [r for r in rows if r["opponent"] == foe]
        if not group:
            continue
        summaries[foe] = dict(games=len(group), wins=sum(r["won"] for r in group),
            faults=sum(r["our"]["faults"] for r in group),
            fuel_exhausted=sum(r["our"]["fuel_exhausted"] for r in group),
            opponent_faults=sum(r["foe"]["faults"] for r in group),
            by_seat={str(s): dict(games=sum(r["seat"] == s for r in group), wins=sum(r["won"] for r in group if r["seat"] == s)) for s in (0, 1)},
            mean_banked_gems=sum(r["our"]["gems"] for r in group)/len(group),
            mean_opponent_banked_gems=sum(r["foe"]["gems"] for r in group)/len(group))
    return summaries


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--runtime-project", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "experiments/topdraft-v1/lab.toml")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = tomllib.loads(args.config.read_text())
    runtime, cli, out = args.runtime_project.resolve(), args.cli.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    version = subprocess.run([str(cli), "--version"], capture_output=True, text=True, check=True).stdout.strip()
    if version != cfg["runtime"]["cli_version"]:
        raise ValueError(f"Unexpected runner: {version}")
    candidate = ROOT / "archive" / cfg["candidate"] / "bot.wasm"
    baseline = ROOT / "archive" / cfg["baseline"] / "bot.wasm"
    starter = runtime / "bots/starter-cpp/.cambc/build-release/bot-injected.wasm"
    identities = {n: sha(p) for n, p in [("candidate", candidate), ("baseline", baseline), ("starter", starter)]}
    meta = json.loads((candidate.parent / "meta.json").read_text())
    if identities["candidate"] != meta["wasm_sha256"]:
        raise ValueError("Frozen candidate WASM identity mismatch")
    frozen = candidate.parent / "src"
    if {p.name: sha(p) for p in frozen.iterdir()} != meta["source_sha256"]:
        raise ValueError("Frozen source identity mismatch")
    official = [("site", runtime / "maps" / (n + ".map26a")) for n in cfg["maps"]["site"]]
    generated = [("screen", ROOT / "maps" / (n + ".map26a")) for n in cfg["maps"]["screen"]]
    tasks = [(cohort, mp, foe, seat) for cohort, mp in official + generated
             for foe in (["starter", "baseline"] if cohort == "site" else ["baseline"])
             for seat in (0, 1)]
    expected = cfg["draft"]["priority"]
    env = {**os.environ, "CAMBC_NO_UPDATE_CHECK": "1",
           "CAMBC_WASMTIME_CACHE": str(out / "wasmtime-cache")}

    def run(task):
        cohort, mp, foe, seat = task
        folder = out / "matches" / foe / cohort / (mp.stem + "-" + str(seat))
        folder.mkdir(parents=True, exist_ok=True)
        identity = dict(wasm=identities, map_sha256=sha(mp), seat=seat, opponent=foe,
                        config_sha256=sha(args.config), cli=version)
        marker, rawpath = folder / "identity.json", folder / "stats.json"
        if not marker.exists() or json.loads(marker.read_text()) != identity or not rawpath.exists():
            opponent = starter if foe == "starter" else baseline
            a, b = (candidate, opponent) if seat == 0 else (opponent, candidate)
            command = [str(cli), "run", str(a), str(b), "--map", str(mp), "--release",
                       "--statistics", str(rawpath), "--json", "--log-limit", str(cfg["log_limit"]), "-o", str(folder)]
            result = subprocess.run(command, cwd=runtime, env=env, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=cfg["timeout_seconds"])
            (folder / "runner.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
            if result.returncode:
                raise ValueError(f"Match failed: {mp.stem}/{foe}/{seat}: {result.stderr[-1800:]}")
            marker.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
        raw = json.loads(rawpath.read_text())
        summary = stats.summarize(raw)  # Fails on incomplete capture or unfinished games.
        if raw["match"]["engineVersion"] != cfg["runtime"]["engine_version"] or raw["match"]["engineBuildHash"] != cfg["runtime"]["engine_build_hash"]:
            raise ValueError("Wrong engine rules or build")
        if raw["match"]["mapHash"] != identity["map_sha256"]:
            raise ValueError("Wrong map bytes")
        team, other = ("teamA", "teamB") if seat == 0 else ("teamB", "teamA")
        picks = []
        for pick in raw["roster"]["draft"]:
            if pick["team"] != team:
                continue
            name = pick["champion"]
            numeric = re.fullmatch(r"Unknown draft champion \((\d+)\)", name)
            picks.append(DRAFT_NAMES[int(numeric[1])] if numeric else name)
        if picks != expected[:len(picks)] or not picks:
            raise ValueError(f"Candidate did not use the intended draft: {picks}")
        bundles = list(folder.glob("*.repl26a"))
        if len(bundles) != 1:
            raise ValueError("Expected exactly one official release replay bundle")
        with zipfile.ZipFile(bundles[0]) as bundle:
            fuel = bundle.read("team-a.fuel" if seat == 0 else "team-b.fuel")
        if fuel[:11] != b"a62leuf\0\0\0\1" or (len(fuel) - 77) % 8:
            raise ValueError("Unsupported official fuel log")
        values = struct.unpack_from("<" + "Q" * ((len(fuel)-77)//8), fuel, 77)
        physical = sum(c["team"] == team for c in raw["champions"])
        return dict(cohort=cohort, map=mp.stem, map_sha256=identity["map_sha256"], seat=seat,
                    opponent=foe, won=summary["outcome"] == team, rounds=summary["rounds"],
                    picks=picks, our=summary["teams"][team], foe=summary["teams"][other],
                    own_champions=[c for c in raw["champions"] if c["team"] == team],
                    official_fuel=dict(draft_max=max(values[:len(picks)]),
                                       initial_max=max(values[len(picks):len(picks)+physical]),
                                       ordinary_max=max(values[len(picks)+physical:])),
                    statistics=rawpath.relative_to(out).as_posix(), statistics_sha256=sha(rawpath))

    started, rows = time.time(), []
    with ThreadPoolExecutor(cfg["jobs"]) as pool:
        for row in pool.map(run, tasks):
            rows.append(row)
            if len(rows) % 40 == 0:
                print(f"Top draft development {len(rows)}/{len(tasks)}", flush=True)
    summaries = summarize_opponents(rows)
    report = dict(schema=1, experiment=cfg["candidate"], parent=meta["parent"], baseline=cfg["baseline"], runtime=cfg["runtime"],
        identities=identities, config_sha256=sha(args.config), changes=meta["changelog"],
        status="development_only_not_promoted", sealed_confirmation_maps_used=False, promotion_gate_run=False, uploaded=False,
        draft_verified_games=len(rows), elapsed_seconds=time.time()-started, summary=summaries, games=rows)
    (out / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summaries, indent=2), flush=True)


if __name__ == "__main__":
    main()

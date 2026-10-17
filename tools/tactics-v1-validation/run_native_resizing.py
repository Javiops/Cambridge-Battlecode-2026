"""Controlled physical current-job self-release, not autonomous Bot::turn.

Both native sides earn the current camp's HP through actual attacks, establish
the typed current crew from a fresh sufficient proof and accepted hit, then call
the production resize adapter with an actual approximately 65k owner budget.
Actual permissions/order, normal gateways and reset receipts determine actions.
The script verifies two different physical recipients/camps and both real banks.
It does not project HP, stats, wallet, movement permission or payout into World.
Intent/staging is a controlled fixture; this is no opening/strength claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
SDK = "76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4"
ENGINE_FILE = "e123b59d9dea198762ab7a04db9b3cb6d06dfa991088e41c24750fc4cb88b947"
ENGINE_BUILD = "02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes(source):
    return {p.name: sha(p) for p in sorted(source.iterdir())
            if p.is_file() and p.suffix in (".h", ".cpp")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "output", "cli", "project", "node", "engine"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    source, output, cli, project, node, engine = [getattr(args, n).resolve()
        for n in ("source", "output", "cli", "project", "node", "engine")]
    if not (source / "resizing.h").is_file() or not (source / "main.cpp").is_file():
        raise ValueError("--source must be the production src directory with resizing.h/main.cpp")
    for executable in (cli, node):
        if not executable.is_file():
            raise ValueError(f"Missing executable: {executable}")
    output.mkdir(parents=True, exist_ok=False)
    commands = []

    def invoke(command, label):
        command = [str(x) for x in command]
        commands.append(command)
        result = subprocess.run(command, cwd=project,
            env={**os.environ, "CAMBC_NO_UPDATE_CHECK": "1"},
            capture_output=True, text=True, errors="replace", timeout=600)
        (output / (label + ".log")).write_text(result.stdout + result.stderr, encoding="utf8")
        if result.returncode:
            raise RuntimeError(f"{label}: exit {result.returncode}; preserved log in output")
        return result

    try:
        sdk = project / "sdk/cpp/cambc.h"
        fixture = HERE / "fixtures/native-resizing.cpp"
        map_path = HERE / "fixtures/native-resizing.map26a"
        metadata = json.loads((HERE / "fixtures/native-resizing.json").read_text(encoding="utf8"))
        if sha(sdk) != SDK or sha(engine) != ENGINE_FILE:
            raise ValueError("The SDK or native engine-file pin differs")
        if sha(fixture) != metadata["fixture_sha256"] or sha(map_path) != metadata["map_sha256"]:
            raise ValueError("Native resizing fixture/map bytes differ from their metadata")
        node_version = invoke([node, "--version"], "node-version").stdout.strip()
        hashes = source_hashes(source)
        (output / "source-input.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf8")
        bot = output / "bot"
        (bot / "src").mkdir(parents=True)
        for name in hashes:
            shutil.copy2(source / name, bot / "src" / ("retained-main.h" if name == "main.cpp" else name))
        shutil.copy2(fixture, bot / "src/main.cpp")
        invoke([cli, "build", bot], "build-normal")
        invoke([cli, "build", bot, "--release"], "build-release")
        game = output / "game"
        game.mkdir()
        invoke([cli, "run", bot, bot, "--map", map_path, "--release", "--json", "-o", game,
                "--statistics", game / "statistics.json"], "run")
        stats = game / "statistics.json"
        data = json.loads(stats.read_text(encoding="utf8"))
        actual_engine = data["match"]
        if (actual_engine["engineVersion"] != "0.0.2" or
                actual_engine["engineBuildHash"] != ENGINE_BUILD or
                actual_engine["mapHash"] != sha(map_path)):
            raise ValueError("Actual native engine/map identity differs from the pinned fixture")
        replay = next(game.glob("*.repl26a"))
        failures, cases = [], {}
        assertions = 0

        def check(value, name):
            nonlocal assertions
            assertions += 1
            if not value:
                failures.append(name)

        def events(kind, team):
            return [(e["owner"]["id"], x) for e in data["events"]
                    if e["kind"] == kind and e.get("owner", {}).get("team") == team
                    for x in e["entries"]]

        with zipfile.ZipFile(replay) as archive:
            check(archive.testzip() is None, "replay-crc")
            for side, team in (("a", "teamA"), ("b", "teamB")):
                text = archive.read("team-" + side + ".stdout").decode(errors="replace").replace(chr(0), "")
                (output / (side + ".stdout.txt")).write_text(text, encoding="utf8")
                markers = re.findall(r"RESIZE_[^\r\n]+", text)
                check(len(re.findall(r"RESIZE_SPLIT ", text)) == 1, side + ":single-release")
                check(len(re.findall(r"RESIZE_CAPTURE ", text)) == 2 and
                      len(re.findall(r"RESIZE_BANK ", text)) == 2, side + ":dual-completed-cycle-markers")
                check(not re.search(r"RESIZE_(FAIL|EXCEPTION)|TACTICS_ERROR|bot error:|\[err", text),
                      side + ":no-fixture-or-API-error")
                captures, banks = events("gemCollection", team), events("gemSubmission", team)
                check(len(captures) == len(banks) == 2, side + ":two-actual-captures-and-banks")
                check(len({x[0] for x in captures}) == 2 and
                      len({json.dumps(x[1]["target"], sort_keys=True) for x in captures}) == 2,
                      side + ":distinct-physical-recipients-and-camps")
                check(all(x[1]["value"] == "24" for x in captures + banks), side + ":actual24-shares")
                check(all(any(bid == cid and b["timestamp"]["round"] > c["timestamp"]["round"]
                      for bid, b in banks) for cid, c in captures), side + ":bank-after-own-capture")
                check(not events("death", team) and not events("gemLoss", team), side + ":no-death-or-gemloss")
                check(next(x for x in data["teams"] if x["team"] == team)["submittedGems"] == "48",
                      side + ":actual48-team-score")
                split = re.search(r"RESIZE_SPLIT (\d+) (\d+)", text)
                kill = re.search(r"RESIZE_REMAINING_KILL (\d+) (\d+)", text)
                check(bool(split and kill and split[2] == kill[2]) and
                      all(int(split[2]) < x["timestamp"]["round"] for _, x in captures),
                      side + ":same-round-release-clear-before-payout")
                runtime = re.search(r"RESIZE_RUNTIME (\d+) (\d+) fuel=(\d+),(\d+)", text)
                retained = re.search(r"RESIZE_RETAINED (\d+) (\d+) fuel=(\d+),(\d+)", text)
                check(bool(runtime and 65000 <= int(runtime[3]) <= 66000 and int(runtime[4]) >= 16000),
                      side + ":real65k-proof-with-action-reserve")
                check(bool(retained and 65000 <= int(retained[3]) <= 66000 and int(retained[4]) >= 16000),
                      side + ":real65k-retained-current-accepted-kill")
                first = (re.search(r"RESIZE_BUNDLE " + runtime[1] + " " + runtime[2] +
                         r" fuel=(\d+),(\d+) reset=0 deferred-refresh=1", text) if runtime else None)
                check(bool(first and int(first[2]) >= 16000), side + ":paid-proposal-to-accepted-first-basic")
                cases[side] = {"markers": markers, "actual_captures": captures, "actual_banks": banks,
                    "runtime_budget": list(map(int, runtime.groups())) if runtime else None,
                    "retained_budget": list(map(int, retained.groups())) if retained else None}
        fuel = sum(len(e["entries"]) for e in data["events"] if e["kind"] == "fuelExhausted")
        check(fuel == 0, "zero-native-fuel")
        check(not any(data["diagnostics"]["botFaults"].values()), "zero-native-faults")
        check(hashes == source_hashes(source), "source-unchanged")
        report = dict(passed=not failures, assertions=assertions, failures=failures,
            scope=__doc__, actual_bot_turn_exercised=False, retained_main_compiled=True,
            current_adapter_and_normal_gateway_exercised=True,
            wider_dynamic_resizing_verified=False, created_utc=datetime.now(timezone.utc).isoformat(),
            source_sha256=hashes, sdk_header_sha256=sha(sdk), node_version=node_version,
            engine_file_sha256=sha(engine), fixture_sha256=sha(fixture), map_sha256=sha(map_path),
            module_sha256=sha(bot / ".cambc/build-release/bot-injected.wasm"),
            statistics_sha256=sha(stats), replay_sha256=sha(replay), actual_engine=actual_engine,
            fuel_exhausted=fuel, native_faults=data["diagnostics"]["botFaults"], cases=cases, commands=commands)
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
        print(json.dumps({k: report[k] for k in ("passed", "assertions", "failures", "fuel_exhausted",
                                                "native_faults", "module_sha256")}, indent=2))
        if failures:
            raise SystemExit(1)
    except Exception as error:
        (output / "FAILED.json").write_text(json.dumps({"error": str(error), "commands": commands},
                                                      indent=2) + "\n", encoding="utf8")
        raise


if __name__ == "__main__":
    main()

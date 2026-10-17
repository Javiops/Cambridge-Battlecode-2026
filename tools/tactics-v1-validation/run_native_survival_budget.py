"""Test the actual coordinator's funded response to a wounded carrier.

HP, shield, bag, threat and mission cases are explicit World projections under the
official SDK. No projected action is executed. Whole-main development matches
are separate evidence; this is not a strength or physical-payout test.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cli", "project", "source", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    cli, project, source, output = [p.resolve() for p in
                                    (args.cli, args.project, args.source, args.output)]
    output.mkdir(parents=True, exist_ok=False)
    sdk = project / "sdk/cpp/cambc.h"
    if sha(sdk) != "76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4":
        raise ValueError("Unreviewed SDK")
    headers = {p.name: sha(p) for p in source.glob("*.h")}
    bot = output / "native-survival-budget"
    (bot / "src").mkdir(parents=True)
    for name in headers:
        shutil.copy2(source / name, bot / "src" / name)
    fixture = HERE / "fixtures/native-survival-budget.cpp"
    shutil.copy2(fixture, bot / "src/main.cpp")
    map_path = HERE / "fixtures/native-bank.map26a"
    metadata = json.loads((HERE / "fixtures/native-bank-map.json").read_text())
    if sha(map_path) != metadata["map_sha256"]:
        raise ValueError("Fixture map changed")
    commands = []

    def invoke(command, label):
        command = list(map(str, command))
        commands.append(command)
        result = subprocess.run(command, cwd=project,
                                env={**os.environ, "CAMBC_NO_UPDATE_CHECK": "1"},
                                capture_output=True, text=True, errors="replace", timeout=600)
        (output / (label + ".log")).write_text(result.stdout + result.stderr, encoding="utf8")
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    invoke([cli, "build", bot], "build-normal")
    invoke([cli, "build", bot, "--release"], "build-release")
    game = output / "game"
    game.mkdir()
    statistics = game / "statistics.json"
    invoke([cli, "run", bot, bot, "--map", map_path, "--release", "--json",
            "-o", game, "--statistics", statistics], "run")
    data = json.loads(statistics.read_text())
    replay = next(game.glob("*.repl26a"))
    failures, cases = [], {}
    expected = {0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15}
    pattern = re.compile(r"SURVIVAL_CASE (\d+) (\d+) (\d+) (\d+) (\d+) "
                         r"epoch=(\d+),(\d+) action=(-?\d+) phase=(-?\d+)")
    with zipfile.ZipFile(replay) as archive:
        if archive.testzip() is not None:
            raise ValueError("Replay CRC failure")
        for side in ("a", "b"):
            text = archive.read("team-" + side + ".stdout").decode(errors="replace").replace("\0", "")
            (output / ("team-" + side + ".stdout.txt")).write_text(text, encoding="utf8")
            rows = [dict(zip(("owner", "case", "round", "entry_fuel", "remaining_fuel",
                               "entry_epoch", "exit_epoch", "action", "phase"), map(int, row)))
                    for row in pattern.findall(text)]
            cases[side] = rows
            passed = re.findall(r"SURVIVAL_CASE_PASS (\d+) (\d+)", text)
            if len(rows) != len(expected) or {r["case"] for r in rows} != expected:
                failures.append(side + ":all-fifteen-cases-must-activate")
            if len(passed) != len(expected) or {int(row[1]) for row in passed} != expected:
                failures.append(side + ":all-fifteen-cases-must-pass")
            if any(r["entry_epoch"] != r["exit_epoch"] or r["remaining_fuel"] < 12000
                   for r in rows):
                failures.append(side + ":response-reserve-or-epoch")
            if re.search(r"SURVIVAL_FAIL|TACTICS_ERROR|bot error:|\[err", text):
                failures.append(side + ":error-marker")
    fuel = sum(len(e["entries"]) for e in data["events"] if e["kind"] == "fuelExhausted")
    if fuel or any(data["diagnostics"]["botFaults"].values()):
        failures.append("native-fault-or-fuel")
    if headers != {p.name: sha(p) for p in source.glob("*.h")}:
        failures.append("source-changed-during-run")
    if data["match"]["engineVersion"] != "0.0.2" or data["match"]["engineBuildHash"] != \
            "02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede":
        failures.append("native-engine-mismatch")
    report = dict(passed=not failures, created_utc=datetime.now(timezone.utc).isoformat(),
                  scope=__doc__.strip(), source_headers_sha256=headers,
                  fixture_sha256=sha(fixture), module_sha256=sha(bot / ".cambc/build-release/bot-injected.wasm"),
                  cli_sha256=sha(cli), sdk_header_sha256=sha(sdk), map_sha256=sha(map_path),
                  replay_sha256=sha(replay), statistics_sha256=sha(statistics),
                  actual_engine=data["match"], native_faults=data["diagnostics"]["botFaults"],
                  fuel_exhausted=fuel, failures=failures, cases=cases, commands=commands)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(json.dumps(dict(passed=not failures, failures=failures, cases=cases), indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

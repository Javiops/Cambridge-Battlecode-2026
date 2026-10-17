"""Real capture/Tribute and Ryth stun; only the deciding score is projected."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

SDK_SHA = "76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4"
CONTROL_EXPRESSION = "applies_control(self, spell) ? added_control_windows(target, spell.duration) : 0"
OLD_EXPRESSION = "spell.kind == 4 ? added_control_windows(target, spell.duration) : 0"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cli", "project", "source", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--existing", action="store_true", help="Recheck an existing run without rebuilding.")
    parser.add_argument("--old-expression", action="store_true", help="Restore only the former cheap-sequence control expression in the copied header; expect no deciding proposal.")
    args = parser.parse_args()
    cli, project, source, out = (getattr(args, name).resolve() for name in ("cli", "project", "source", "output"))
    here = Path(__file__).resolve().parent
    bot, game = out / "bot", out / "game"
    sdk_file = project / "sdk/cpp/cambc.h"
    if sha(sdk_file) != SDK_SHA:
        raise ValueError("Expected the official pinned SDK 2.2.2")
    if not args.existing:
        (bot / "src").mkdir(parents=True, exist_ok=False)
        for header in source.glob("*.h"):
            shutil.copy2(header, bot / "src" / header.name)
        fixture = (here / "fixture.cpp").read_text()
        if args.old_expression:
            header = bot / "src/combat.h"
            text = header.read_text()
            if text.count(CONTROL_EXPRESSION) != 1:
                raise ValueError("Expected exactly one production cheap control expression")
            header.write_text(text.replace(CONTROL_EXPRESSION, OLD_EXPRESSION, 1))
            fixture = fixture.replace("#define EXPECT_CONTROL 1", "#define EXPECT_CONTROL 0", 1)
        (bot / "src/main.cpp").write_text(fixture)
        shutil.copy2(here / "fixture.map26a", out / "fixture.map26a")

    def invoke(command, label):
        result = subprocess.run([str(x) for x in command], cwd=project,
                                env={**os.environ, "CAMBC_NO_UPDATE_CHECK": "1"},
                                capture_output=True, text=True, errors="replace", timeout=600)
        (out / (label + ".log")).write_text(result.stdout + result.stderr, encoding="utf8")
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    statistics = game / "statistics.json"
    if not args.existing:
        invoke([cli, "build", bot], "normal-build")
        invoke([cli, "build", bot, "--release"], "release-build")
        game.mkdir()
        invoke([cli, "run", bot, bot, "--map", out / "fixture.map26a", "--release", "--json",
                "-o", game, "--statistics", statistics], "run")
    data = json.loads(statistics.read_text())
    replay, = game.glob("*.repl26a")
    failures, markers, evidence = [], {}, None
    pattern = re.compile(r"RYTH_TRIBUTE_PASS mode=(\d+) round=(\d+) actualScore=(\d+) projectedScore=(\d+) bag=(\d+) entry=(\d+) exit=(\d+) priority=(-?\d+)")
    with zipfile.ZipFile(replay) as archive:
        for side in ("a", "b"):
            text = archive.read("team-" + side + ".stdout").decode(errors="replace").replace("\0", "")
            (out / ("stdout-" + side + ".txt")).write_text(text, encoding="utf8")
            markers[side] = re.findall(r"RYTH_TRIBUTE[^\r\n]+", text)
            matches = pattern.findall(text)
            if len(matches) != (1 if side == "a" else 0):
                failures.append(side + ":expected-native-cases")
            if side == "a" and len(matches) == 1:
                keys = ("mode", "round", "actual_score", "projected_score", "bag", "entry", "exit", "priority")
                evidence = dict(zip(keys, map(int, matches[0])))
                expected_mode = 0 if args.old_expression else 1
                if evidence["mode"] != expected_mode or evidence["priority"] != (0 if args.old_expression else 3):
                    failures.append("wrong-controlled-policy-outcome")
                if evidence["actual_score"] != 0 or evidence["bag"] <= 0 or evidence["projected_score"] + evidence["bag"] != 1000:
                    failures.append("wrong-projection-or-real-bag")
                if not (32000 <= evidence["entry"] < 45000 and evidence["exit"] > 24000 and evidence["entry"] < 60000):
                    failures.append("optional-budget-floor-not-exercised")
            if re.search(r"RYTH_TRIBUTE_(FAIL|EXCEPTION)|TACTICS_ERROR", text):
                failures.append(side + ":error-marker")
        native_trace = archive.read("replay.repl26a")
    if not any("RYTH_TRIBUTE_STARTED" in marker for marker in markers["b"]):
        failures.append("no-actual-opponent-tribute")
    fuel = sum(len(event["entries"]) for event in data["events"] if event["kind"] == "fuelExhausted")
    if fuel or any(data["diagnostics"]["botFaults"].values()):
        failures.append("native-fuel-or-fault")
    if data["match"]["engineVersion"] != "0.0.2" or data["match"]["engineBuildHash"] != "02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede":
        failures.append("native-engine-mismatch")
    (out / "native.repl26a").write_bytes(native_trace)
    report = {
        "passed": not failures,
        "scope": "Actual Vendetta farms/captures a real bag and starts real Tribute. Ryth, target metadata, positions, HP, bag and channel are native. Only World.enemy_score is projected to make the real bag deciding. Planning starts below its optional 60k floor. The positive executes a nonlethal native stun and verifies interruption; old-expression control performs no cast and verifies the channel continues. Not an actual winning-score game, whole Bot main test or strength benchmark.",
        "failures": failures, "fuel": fuel, "faults": data["diagnostics"]["botFaults"],
        "evidence": evidence, "markers": markers, "old_expression": args.old_expression,
        "source_sha256": {h.name: sha(h) for h in (bot / "src").iterdir()},
        "module_sha256": sha(bot / ".cambc/build-release/bot-injected.wasm"),
        "map_sha256": sha(out / "fixture.map26a"), "sdk_sha256": sha(sdk_file),
        "statistics_sha256": sha(statistics), "replay_sha256": sha(replay),
        "native_trace_sha256": sha(out / "native.repl26a"), "actual_engine": data["match"]}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("passed", "failures", "fuel", "faults", "evidence")}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

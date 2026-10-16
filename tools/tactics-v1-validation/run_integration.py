"""Explicit local-only release integration runner; no login/submission commands."""
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


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def invoke(command, project, log):
    result = subprocess.run([str(x) for x in command], cwd=project,
                            env={**os.environ, "CAMBC_NO_UPDATE_CHECK": "1"},
                            capture_output=True, text=True, errors="replace", timeout=600)
    log.write_text(result.stdout + result.stderr, encoding="utf8")
    if result.returncode:
        raise RuntimeError(f"Command failed: {log}\n{result.stdout}\n{result.stderr}")
    return [str(x) for x in command]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cli", type=Path, help="Official cambc executable; CAMBC or PATH fallback")
    p.add_argument("--project", required=True, type=Path, help="Existing cambc init project containing sdk/, cmake/, cambc.toml")
    p.add_argument("--candidate", required=True, type=Path, help="Bot directory containing src/main.cpp")
    p.add_argument("--opponent", required=True, type=Path)
    p.add_argument("--maps", required=True, nargs="+", type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    cli = args.cli or os.environ.get("CAMBC") or shutil.which("cambc")
    if not cli:
        raise ValueError("Supply --cli or CAMBC pointing to official cambc 2.2.2")
    cli = Path(cli).resolve()
    project, candidate, opponent, output = [v.resolve() for v in (args.project, args.candidate, args.opponent, args.output)]
    output.mkdir(parents=True, exist_ok=False)
    sdk_hash = sha(project / "sdk/cpp/cambc.h")
    if sdk_hash != "76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4":
        raise ValueError("Integration project SDK must be the reviewed official 2.2.2")
    source_pins = {}
    commands = []
    modules = {}
    for label, bot in (("candidate", candidate), ("opponent", opponent)):
        source_pins[label] = {str(f.relative_to(bot / "src")): sha(f) for f in sorted((bot / "src").rglob("*")) if f.is_file()}
        if not (bot / ".cambc/build/compile_commands.json").exists():
            commands.append(invoke([cli, "build", bot], project, output / f"{label}-normal-build.log"))
        commands.append(invoke([cli, "build", bot, "--release"], project, output / f"{label}-release-build.log"))
        modules[label] = sha(bot / ".cambc/build-release/bot-injected.wasm")
    games = []
    for map_index, raw_map in enumerate(args.maps):
        map_path = raw_map.resolve()
        for side in (0, 1):
            slot = output / f"map-{map_index}-candidate-{side}"
            slot.mkdir()
            a, b = (candidate, opponent) if side == 0 else (opponent, candidate)
            stats = slot / "statistics.json"
            command = invoke([cli, "run", a, b, "--map", map_path, "--release", "--json", "-o", slot,
                              "--statistics", stats], project, slot / "runner.log")
            data = json.loads(stats.read_text(encoding="utf8"))
            if data["match"]["engineVersion"] != "0.0.2":
                raise ValueError("Native runner used an unexpected engine")
            replay = list(slot.glob("*.repl26a"))
            if len(replay) != 1:
                raise ValueError("Expected one replay bundle")
            caught = {}
            with zipfile.ZipFile(replay[0]) as archive:
                if archive.testzip() is not None:
                    raise ValueError("Replay CRC failed")
                for letter in ("a", "b"):
                    text = archive.read("team-" + letter + ".stdout").decode("utf8", errors="replace").replace("\0", "")
                    caught[letter] = re.findall(r"(?:TACTICS_ERROR|bot error:|\[err[^\]]*\])[^\r\n]*", text)
            native_faults = data["diagnostics"]["botFaults"]
            own_side = "teamA" if side == 0 else "teamB"
            games.append({"map_sha256": sha(map_path), "candidate_side": side, "actual_match": data["match"],
                          "scores": data["teams"], "native_faults": native_faults,
                          "caught_errors_by_side": caught,
                          "candidate_no_native_faults": native_faults[own_side] == 0,
                          "candidate_no_caught_errors": not caught["a" if side == 0 else "b"],
                          "statistics_sha256": sha(stats), "replay_sha256": sha(replay[0]), "command": command})
    for label, bot in (("candidate", candidate), ("opponent", opponent)):
        if source_pins[label] != {str(f.relative_to(bot / "src")): sha(f) for f in sorted((bot / "src").rglob("*")) if f.is_file()}:
            raise ValueError("Source changed during integration")
        if modules[label] != sha(bot / ".cambc/build-release/bot-injected.wasm"):
            raise ValueError("Compiled module changed during integration")
    report = {"created_utc": datetime.now(timezone.utc).isoformat(), "cli_sha256": sha(cli),
              "sdk_header_sha256": sdk_hash, "source_pins": source_pins, "modules": modules,
              "commands": commands, "games": games,
              "interpretation": "All local games retained. No winrate-driven tuning, ladder-strength claim or competitive challenge. Inspect native fuelExhausted and tactic activation events inside each statistics.json; zero faults alone does not imply useful progress."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(f"Recorded {len(games)} local integration games in {output}")


if __name__ == "__main__":
    main()

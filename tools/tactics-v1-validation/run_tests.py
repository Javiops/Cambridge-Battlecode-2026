"""Portable correctness fixtures for the production tactics-v1 policy.

This script needs no account or network. Test assertions use explicit failure
paths, so release/NDEBUG never disables them. Native integration is separate.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime, timezone
from channel_fixture import generate_channel_fixture, extract_channel_function
from economy_fixtures import generate_economy_fixture, extract_economy_policy
from shopping_fixture import generate_shopping_investment_fixture, extract_shopping_investment
from shopping_gem_fixture import generate_shopping_gem_fixture, extract_shopping_gem
from shopping_cash_fixture import generate_shopping_cash_fixture, extract_shopping_cash
from shopping_cash_hint_fixture import generate_shopping_cash_hint_fixture, extract_shopping_cash_hint
from solo_basic_fixture import generate_solo_basic_fixture, extract_solo_basic_policy
from deny_fixture import generate_denial_fixture, extract_denial_proposal
from ward_exit_fixtures import generate_ward_exit_fixture, extract_ward_exit_policy
from vision_fixture import generate_vision_fixture, extract_vision_policy
from coordination_fixture import generate_squad_position_fixture, extract_squad_position
from alternative_fixture import generate_alternative_fixture, extract_alternative
from assembly_fixture import generate_assembly_arrival_fixture, extract_assembly_policy
from handshake_fixture import generate_handshake_fixture, extract_handshake
from lifecycle_fixture import generate_assembly_lifecycle, extract_assembly_lifecycle, extract_prepare_route
from solo_receipt_fixture import generate_solo_receipt_fixture, extract_solo_receipt_policy
from solo_entry_fixture import generate_solo_entry_fixture, extract_solo_entry
from solo_poke_fixture import generate_solo_poke_consumer, extract_solo_poke_consumer
from awake_entry_fixture import generate_pending_awake_fixture, extract_pending_awake
from observation_detour_fixture import generate_observation_detour_fixture, extract_observation_detour
from coarse_fallback_fixture import generate_coarse_fallback_fixture, extract_coarse_fallback
from current_cast_fixture import generate_cast_admission_fixture, extract_cast_admission, generate_current_cast_fixture, extract_current_cast
from receipt_snapshot_fixture import generate_receipt_snapshot_fixture, extract_receipt_snapshot
from solo_mode_fixture import generate_solo_mode_fixture, extract_solo_mode

HERE = Path(__file__).resolve().parent
EXPECTED_SDK_SHA256 = "76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def find_tool(explicit, environment, name, candidates=()):
    options = [explicit, os.environ.get(environment), shutil.which(name), *candidates]
    for value in options:
        if value and Path(value).is_file():
            return Path(value).resolve()
    raise ValueError(f"Cannot find {name}; supply an explicit tool path or {environment}.")


def compiler_path(explicit):
    binary = "clang++.exe" if os.name == "nt" else "clang++"
    roots = [os.environ.get("WASI_SDK_PATH"), os.environ.get("WASI_SDK_PREFIX")]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        roots += sorted((Path(local) / "cambc").glob("wasi-sdk-*"), reverse=True)
    roots += sorted((Path.home() / ".local/share/cambc").glob("wasi-sdk-*"), reverse=True)
    candidates = [Path(p) / "bin" / binary for p in roots if p]
    # A generic system clang may target the host rather than WASI; never choose
    # it by accident when a portable test specifically requires WASI.
    for value in [explicit, os.environ.get("CAMBC_WASI_CXX"), *candidates]:
        if value and Path(value).is_file():
            return Path(value).resolve()
    raise ValueError("WASI Clang not found; use --compiler or WASI_SDK_PATH pointing to wasi-sdk-33.")


def run(command, output, name, timeout=120):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True,
                            errors="replace", timeout=timeout)
    (output / f"{name}.stdout.txt").write_text(result.stdout, encoding="utf8")
    (output / f"{name}.stderr.txt").write_text(result.stderr, encoding="utf8")
    if result.returncode:
        raise RuntimeError(f"{name}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=HERE.parents[1] / "bots/tactics-v1/src")
    parser.add_argument("--compiler", type=Path)
    parser.add_argument("--node", type=Path)
    parser.add_argument("--sdk-root", type=Path,
                        help="Optional current CAMBC sdk/ directory; enables standalone header checks")
    parser.add_argument("--output", type=Path, default=HERE / ".results")
    args = parser.parse_args()
    source = args.source.resolve()
    if not (source / "types.h").is_file():
        raise ValueError("--source must contain the production tactics-v1 headers")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    compiler = compiler_path(args.compiler)
    node = find_tool(args.node, "NODE", "node")
    before = {p.name: sha(p) for p in sorted(source.glob("*.h"))}
    suites = []
    for name, pattern in (("policy", r"policy acceptance: (\d+) checks passed"),
                          ("combat", r"(\d+) combat checks passed"),
                          ("combat-sequence", r"(\d+) combat sequence checks passed"),
                          ("combat-reply", r"(\d+) common-endpoint checks passed"),
                          ("combat-peel", r"(\d+) peel eligibility checks passed"),
                          ("combat-reach", r"(\d+) local reach checks passed"),
                          ("squads", r"squad checks passed: (\d+)"),
                          ("camp-affordability", r"(\d+) camp affordability checks passed"),
                          ("solo-certificate", r"(\d+) solo certificate checks passed"),
                          ("observation-detour", r"(\d+) observation detour checks passed"),
                          ("observation-detour-caller", r"(\d+) observation detour caller checks passed"),
                          ("awake-entry", r"(\d+) awake entry lease checks passed"),
                          ("awake-arrival", r"(\d+) awake arrival checks passed"),
                          ("awake-entry-caller", r"(\d+) pending awake caller checks passed"),
                          ("solo-poke", r"(\d+) cast-only certificate checks passed"),
                          ("solo-poke-consumer", r"(\d+) typed solo consumer checks passed"),
                          ("solo-entry", r"(\d+) solo entry checks passed"),
                          ("solo-equivalence", r"(\d+) scalar singleton checks passed"),
                          ("solo-receipt", r"(\d+) solo receipt checks passed"),
                          ("resource", r"(\d+) resource eligibility checks passed"),
                          ("farm-readiness", r"(\d+) farm readiness checks passed"),
                          ("farm-observation", r"(\d+) purposeful farm observation checks passed"),
                          ("ranking", r"(\d+) ranking checks passed"),
                          ("assembly", r"(\d+) assembly checks passed"),
                          ("assembly-arrival", r"(\d+) assembly-arrival checks passed"),
                          ("assembly-handshake", r"(\d+) assembly handshake checks passed"),
                          ("assembly-lifecycle", r"(\d+) assembly lifecycle checks passed"),
                          ("channel", r"(\d+) channel-risk checks passed"),
                          ("recovery", r"(\d+) recovery checks passed"),
                          ("delivery", r"(\d+) delivery checks passed"),
                          ("coordination", r"(\d+) coordination checks passed"),
                          ("camp-actions", r"(\d+) camp action checks passed"),
                          ("camp-collateral", r"(\d+) camp collateral checks passed"),
                          ("camp-shield-clock", r"(\d+) camp shield clock checks passed"),
                          ("camp-basic", r"(\d+) camp basic checks passed"),
                          ("coarse-fallback", r"(\d+) exact ordinary fallback checks passed"),
                          ("cast-admission", r"(\d+) detailed-admission checks passed"),
                          ("current-cast", r"(\d+) funded-current-cast checks passed"),
                          ("crew-sequence", r"(\d+) crew sequence checks passed"),
                          ("crew-current", r"(\d+) current crew checks passed"),
                          ("resizing", r"(\d+) current-resizing checks passed"),
                          ("receipt-snapshot", r"(\d+) restricted receipt snapshot checks passed"),
                          ("solo-mode", r"(\d+) committed solo mode checks passed"),
                          ("squad-position", r"(\d+) squad-position checks passed"),
                          ("alternative", r"(\d+) separate-opportunity checks passed"),
                          ("vision", r"(\d+) vision checks passed"),
                          ("ward-exit", r"(\d+) ward/exit checks passed"),
                          ("information", r"(\d+) information checks passed"),
                          ("cycles", r"(\d+) cycle checks passed"),
                          ("chain", r"(\d+) bounded chain checks passed"),
                          ("shopping-investment", r"(\d+) shopping-investment checks passed"),
                          ("shopping-gem", r"(\d+) shopping-gem checks passed"),
                          ("shopping-cash", r"(\d+) finite cash investment checks passed"),
                          ("shopping-cash-hint", r"(\d+) cash route-hint checks passed"),
                          ("solo-basic", r"(\d+) pre-basic receipt checks passed"),
                          ("deny", r"(\d+) deny checks passed")):
        if name in ("combat-sequence", "coordination", "squad-position", "vision") and not (source / "coordination.h").is_file():
            continue  # Historical v12 does not contain the new model contracts.
        if name == "receipt-snapshot" and not re.search(r"bool\s+refresh_receipt_target\s*\(", (source / "sdk_world.h").read_text(encoding="utf8")):
            continue
        if name == "solo-mode" and "current_solo_dispatch" not in (source / "solo.h").read_text(encoding="utf8"):
            continue
        if name == "resizing" and not (source / "resizing_policy.h").is_file():
            continue
        if name == "camp-actions" and not (source / "camp_actions.h").is_file():
            continue
        if name == "camp-collateral" and not (source / "camp_collateral.h").is_file():
            continue
        if name == "camp-shield-clock" and "shield_ticks" not in (source / "types.h").read_text(encoding="utf8"):
            continue
        if name == "camp-basic" and not (source / "camp_basic.h").is_file():
            continue
        if name == "coarse-fallback" and "current_basic_farm_fallback" not in (source / "economy.h").read_text(encoding="utf8"):
            continue
        if name in ("cast-admission", "current-cast") and "early_current_cast_farm_proposal" not in (source / "economy.h").read_text(encoding="utf8"):
            continue
        if name == "assembly-handshake" and "assembly_handshake_proposal" not in (source / "coordinator.h").read_text(encoding="utf8"):
            continue
        if name == "crew-current" and "name_current_crew" not in (source / "coordination.h").read_text(encoding="utf8"):
            continue
        if name == "crew-sequence" and not (source / "crew_sequence.h").is_file():
            continue
        if name == "combat-peel" and "peel_target_eligible" not in (source / "combat.h").read_text(encoding="utf8"):
            continue
        if name == "combat-reply" and "marginal_reply_cost" not in (source / "combat.h").read_text(encoding="utf8"):
            continue
        if name == "combat-reach" and "ordinary_reachable_region" not in (source / "combat.h").read_text(encoding="utf8"):
            continue
        if name == "shopping-investment" and "named_return_payoff" not in (source / "shopping.h").read_text(encoding="utf8"):
            continue
        if name == "shopping-cash-hint" and "state.cash.capture" not in (source / "shopping.h").read_text(encoding="utf8"):
            continue
        if name == "shopping-cash" and "completed_cash_gem" not in (source / "shopping.h").read_text(encoding="utf8"):
            continue
        if name == "solo-basic" and "make_solo_basic_receipt" not in (source / "economy.h").read_text(encoding="utf8"):
            continue
        if name == "shopping-gem" and "completed_gem_return" not in (source / "shopping.h").read_text(encoding="utf8"):
            continue
        if name == "deny" and not (source / "deny.h").is_file():
            continue
        if name == "ranking" and not (source / "ranking.h").is_file():
            continue
        if name in ("assembly", "assembly-arrival") and not (source / "assembly.h").is_file():
            continue
        if name in ("solo-certificate", "solo-equivalence", "solo-receipt") and not (source / "solo.h").is_file():
            continue
        if name in ("solo-poke", "solo-poke-consumer") and not (source / "solo_poke.h").is_file():
            continue
        if name == "solo-entry" and not (source / "solo_routes.h").is_file():
            continue
        if name == "resource" and not (source / "resource.h").is_file():
            continue
        if name == "farm-observation" and not (source / "farm_observation.h").is_file():
            continue
        if name == "farm-readiness" and not (source / "farm_readiness.h").is_file():
            continue
        if name == "assembly-lifecycle" and "release_stalled_unnamed_assembly" not in (source / "coordinator.h").read_text(encoding="utf8"):
            continue
        if name == "chain" and not (source / "chain.h").is_file():
            continue
        if name in ("awake-entry", "awake-arrival", "awake-entry-caller") and not (source / "awake_entry.h").is_file():
            continue
        if name in ("observation-detour", "observation-detour-caller") and not (source / "observation_detour.h").is_file():
            continue
        template = HERE / "fixtures" / f"{name}.cpp"
        fixture = (generate_solo_mode_fixture(source, output) if name == "solo-mode" else
                   generate_receipt_snapshot_fixture(source, output) if name == "receipt-snapshot" else
                   generate_observation_detour_fixture(source, output) if name == "observation-detour-caller" else
                   generate_cast_admission_fixture(source, output) if name == "cast-admission" else
                   generate_current_cast_fixture(source, output) if name == "current-cast" else
                   generate_pending_awake_fixture(source, output) if name == "awake-entry-caller" else
                   generate_coarse_fallback_fixture(source, output) if name == "coarse-fallback" else
                   generate_channel_fixture(source, output) if name == "channel" else
                   generate_solo_receipt_fixture(source, output) if name == "solo-receipt" else
                   generate_solo_entry_fixture(source, output) if name == "solo-entry" else
                   generate_solo_poke_consumer(source, output) if name == "solo-poke-consumer" else
                   generate_assembly_arrival_fixture(source, output) if name == "assembly-arrival" else
                   generate_handshake_fixture(source, output) if name == "assembly-handshake" else
                   generate_assembly_lifecycle(source, output) if name == "assembly-lifecycle" else
                   generate_ward_exit_fixture(source, output) if name == "ward-exit" else
                   generate_shopping_investment_fixture(source, output) if name == "shopping-investment" else
                   generate_shopping_gem_fixture(source, output) if name == "shopping-gem" else
                   generate_shopping_cash_fixture(source, output) if name == "shopping-cash" else
                   generate_shopping_cash_hint_fixture(source, output) if name == "shopping-cash-hint" else
                   generate_solo_basic_fixture(source, output) if name == "solo-basic" else
                   generate_denial_fixture(source, output) if name == "deny" else
                   generate_vision_fixture(source, output) if name == "vision" else
                   generate_squad_position_fixture(source, output) if name == "squad-position" else
                   generate_alternative_fixture(source, output) if name == "alternative" else
                   generate_economy_fixture(name, source, output) if name in ("recovery", "delivery") else template)
        wasm = output / f"{name}.wasm"
        command = [compiler, "-std=c++20", "-O1", "-fwasm-exceptions", "-mllvm",
                   "-wasm-use-legacy-eh=false", "-I", source, fixture, "-lunwind", "-o", wasm]
        run(command, output, f"compile-{name}")
        execution = run([node, HERE / "run-wasi.mjs", wasm], output, f"run-{name}", timeout=30)
        matched = re.search(pattern, execution.stdout)
        if not matched:
            raise RuntimeError(f"Missing successful check marker: {name}")
        suites.append({"name": name, "checks": int(matched[1]), "stdout": execution.stdout.strip(),
                       "fixture_sha256": sha(fixture), "wasm_sha256": sha(wasm),
                       "template_sha256": sha(template),
                       "production_function_sha256": hashlib.sha256(
                           (extract_solo_mode(source) if name == "solo-mode" else
                            extract_receipt_snapshot(source) if name == "receipt-snapshot" else
                            extract_observation_detour(source) if name == "observation-detour-caller" else
                            extract_cast_admission(source) if name == "cast-admission" else
                            extract_current_cast(source) if name == "current-cast" else
                            extract_channel_function(source) if name == "channel" else
                            extract_coarse_fallback(source) if name == "coarse-fallback" else
                            extract_solo_receipt_policy(source) if name == "solo-receipt" else
                            extract_solo_entry(source) if name == "solo-entry" else
                            extract_solo_poke_consumer(source) if name == "solo-poke-consumer" else
                            extract_assembly_policy(source) if name == "assembly-arrival" else
                            extract_handshake(source) if name == "assembly-handshake" else
                            extract_assembly_lifecycle(source)+"\n"+extract_prepare_route(source) if name == "assembly-lifecycle" else
                            extract_ward_exit_policy(source) if name == "ward-exit" else
                            extract_vision_policy(source) if name == "vision" else
                            extract_squad_position(source) if name == "squad-position" else
                            extract_alternative(source) if name == "alternative" else
                            "\n".join(extract_shopping_investment(source)) if name == "shopping-investment" else
                            extract_shopping_gem(source) if name == "shopping-gem" else
                            extract_shopping_cash(source) if name == "shopping-cash" else
                            extract_shopping_cash_hint(source) if name == "shopping-cash-hint" else
                            extract_solo_basic_policy(source) if name == "solo-basic" else
                            extract_denial_proposal(source) if name == "deny" else
                            extract_economy_policy(name, source)).encode()).hexdigest()
                           if name in ("solo-mode", "receipt-snapshot", "cast-admission", "current-cast", "observation-detour-caller", "coarse-fallback", "channel", "recovery", "delivery", "vision", "ward-exit", "squad-position", "alternative", "shopping-investment", "shopping-gem", "shopping-cash", "shopping-cash-hint", "solo-basic", "solo-receipt", "solo-entry", "solo-poke-consumer", "deny", "assembly-arrival", "assembly-handshake", "assembly-lifecycle") else None,
                       "compile_command": [str(x) for x in command]})
    header_checks = []
    sdk_hash = None
    if args.sdk_root:
        sdk = args.sdk_root.resolve()
        sdk_hash = sha(sdk / "cpp/cambc.h")
        if sdk_hash != EXPECTED_SDK_SHA256:
            raise ValueError("SDK differs from reviewed CAMBC 2.2.2; review and update the explicit pin before crediting compatibility")
        jobs = []
        for name in ["all", *before]:
            headers = before if name == "all" else [name]
            fixture = output / f"header-{name}.cpp"
            fixture.write_text("".join(f'#include "{h}"\n' for h in headers) + "int main(){return 0;}\n", encoding="utf8")
            command = [compiler, "-std=c++20", "-fsyntax-only", "-fwasm-exceptions", "-mllvm",
                       "-wasm-use-legacy-eh=false", "-msimd128", "-I", sdk / "cpp", "-I", source, fixture]
            jobs.append((name, command))
        def header_one(job):
            name, command = job
            result = run(command, output, "header-" + name)
            return {"header": name, "returncode": 0, "stderr": result.stderr,
                    "command": [str(x) for x in command]}
        with ThreadPoolExecutor(max_workers=3) as pool:
            header_checks = list(pool.map(header_one, jobs))
    if before != {p.name: sha(p) for p in sorted(source.glob("*.h"))}:
        raise RuntimeError("Production headers changed while tests ran; rerun against a frozen artifact")
    report = {"passed": True, "created_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Actual pure policy helpers and optional SDK syntax checks. Native action activation, fuel, channels and captures require separate integration evidence.",
              "source_headers_sha256": before, "compiler_sha256": sha(compiler), "node_sha256": sha(node),
              "sdk_header_sha256": sdk_hash, "suites": suites, "header_checks": header_checks,
              "interpretation": "Most policy check count is exhaustive packed-field boundaries, not independent game scenarios."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"passed": True, "suites": [{"name": s["name"], "checks": s["checks"]} for s in suites],
                      "standalone_header_checks": len(header_checks)}, indent=2))


if __name__ == "__main__":
    main()

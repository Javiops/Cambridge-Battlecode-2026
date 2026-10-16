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
                          ("squads", r"squad checks passed: (\d+)"),
                          ("camp-affordability", r"(\d+) camp affordability checks passed"),
                          ("channel", r"(\d+) channel-risk checks passed"),
                          ("recovery", r"(\d+) recovery checks passed"),
                          ("delivery", r"(\d+) delivery checks passed")):
        template = HERE / "fixtures" / f"{name}.cpp"
        fixture = (generate_channel_fixture(source, output) if name == "channel" else
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
                           (extract_channel_function(source) if name == "channel" else
                            extract_economy_policy(name, source)).encode()).hexdigest()
                           if name in ("channel", "recovery", "delivery") else None,
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

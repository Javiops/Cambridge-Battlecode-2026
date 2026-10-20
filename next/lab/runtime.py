"""Identify the exact release experiment before building or reusing results."""
from __future__ import annotations

import hashlib
import json
import subprocess
import tomllib
from pathlib import Path


def cli_version(cli: str, env: dict, root: Path) -> str:
    try:
        result = subprocess.run([cli, "--version"], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", env=env, cwd=root, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SystemExit(f"Cannot identify CAMBC CLI {cli!r}: {exc}") from exc
    version = result.stdout.strip()
    if result.returncode or not version.startswith("cambc "):
        raise SystemExit(f"Cannot identify CAMBC CLI {cli!r}: {result.stderr.strip() or version}")
    return version


def file_sha(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def tree_sha(path: Path) -> str:
    files = sorted((p for p in path.rglob("*") if p.is_file()),
                   key=lambda p: p.relative_to(path).as_posix())
    if not files:
        raise SystemExit(f"Missing SDK at {path}; run cambc init --yes . with the pinned CLI.")
    entries = [(p.relative_to(path).as_posix(), file_sha(p)) for p in files]
    return hashlib.sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest()


def identity(root: Path, cli: str, env: dict, cfg: dict) -> dict:
    expected = cfg.get("runtime", {})
    version = cli_version(cli, env, root)
    if version != expected.get("cli_version"):
        raise SystemExit(f"Runtime requires {expected.get('cli_version', 'a [runtime] CLI pin')}; "
                         f"found {version}. Use the project environment and refresh its SDK.")
    with (root / "cambc.toml").open("rb") as source:
        sdk_version = tomllib.load(source).get("sdk_version")
    if sdk_version != version.removeprefix("cambc "):
        raise SystemExit(f"SDK {sdk_version!r} does not match {version}; run cambc init --yes .")
    engine_hash = expected.get("engine_build_hash", "")
    if len(engine_hash) != 64 or any(c not in "0123456789abcdef" for c in engine_hash):
        raise SystemExit("[runtime].engine_build_hash must pin the observed 64-character engine hash.")
    # CLI launchers differ across machines; the observed engine and SDK identify the rules.
    return {"cli": version,
            "sdk_sha256": tree_sha(root / "sdk" / "cpp"),
            "engine_build_hash": engine_hash, "ruleset": expected.get("ruleset", ""),
            "release": True}


def fingerprint(profile: dict) -> str:
    return hashlib.sha256(json.dumps(profile, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require_compatible(meta: dict, profile: dict) -> None:
    if meta.get("runtime") != profile:
        raise SystemExit(f"Frozen version {meta.get('name', '?')} belongs to another or unrecorded runtime. "
                         "Preserve it and freeze its source under a new name for this patch.")

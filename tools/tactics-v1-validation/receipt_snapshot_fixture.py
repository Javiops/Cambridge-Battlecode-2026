"""Extract actual restricted receipt snapshot and gateway boundaries.

The generated test substitutes recorded host records/API calls, not native
mechanics. Native same-owner cost/action evidence is a separate test.
"""
from pathlib import Path
import hashlib
import json
import re


def _block(text, pattern):
    match = re.search(pattern, text)
    if not match:
        raise ValueError("Missing production receipt snapshot boundary: " + pattern)
    start = match.start()
    cursor = text.index("{", match.end()) + 1
    depth = 1
    while depth:
        depth += (text[cursor] == "{") - (text[cursor] == "}")
        cursor += 1
    return text[start:cursor]


def _parts(source):
    source = Path(source)
    world = (source / "sdk_world.h").read_text(encoding="utf8")
    actions = (source / "actions.h").read_text(encoding="utf8")
    execute_start = re.search(r"inline\s+Execution\s+execute\s*\(", actions)
    if not execute_start:
        raise ValueError("Missing production execute gateway")
    return {
        "EXACT_RECEIPT_REFRESH": _block(world, r"bool\s+refresh_receipt_target\s*\("),
        "EXACT_ANY_BASIC_TARGET": _block(actions, r"inline\s+bool\s+any_basic_target\s*\("),
        "EXACT_RESTRICTED_GATEWAY": _block(actions[execute_start.end():],
            r"if\s*\(\s*w\.restricted_continuation_snapshot\s*\)"),
    }


def extract_receipt_snapshot(source):
    return "\n".join(_parts(source).values())


def generate_receipt_snapshot_fixture(source, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    text = (Path(__file__).parent / "fixtures/receipt-snapshot.cpp").read_text(encoding="utf8")
    parts = _parts(source)
    for name, value in parts.items():
        marker = "// " + name
        if text.count(marker) != 1:
            raise ValueError("Missing/duplicate receipt test marker: " + name)
        text = text.replace(marker, value)
    target = output / "receipt-snapshot-generated.cpp"
    target.write_text(text, encoding="utf8")
    proof = {name: hashlib.sha256(value.encode()).hexdigest() for name, value in parts.items()}
    (output / "receipt-snapshot-extracted.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf8")
    return target

import copy
import hashlib
import json

import pytest

from lab import mapgen


def test_layout_is_deterministic_and_seed_changes_gameplay():
    assert mapgen.layout(12) == mapgen.layout(12)
    assert mapgen.layout(12) != mapgen.layout(13)


def test_many_layouts_have_symmetric_reachable_resources():
    signatures = set()
    for seed in range(100):
        result = mapgen.layout(seed)
        mapgen.validate(result)
        signatures.add(hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest())
    assert len(signatures) == 100


def test_validator_rejects_broken_symmetry():
    result = mapgen.layout(7)
    result["walls"].append([0, 0])
    with pytest.raises(ValueError, match="symmetr"):
        mapgen.validate(result)


def test_validator_rejects_camps_in_spawn():
    result = mapgen.layout(7)
    result["camps"].append([0, 2, 2])
    result["camps"].append([0, result["width"] - 3, result["height"] - 3])
    with pytest.raises(ValueError, match="spawn"):
        mapgen.validate(result)


def test_validator_rejects_missing_altar():
    result = mapgen.layout(7)
    result["altars"] = []
    with pytest.raises(ValueError, match="altar"):
        mapgen.validate(result)


def test_immutable_map_output_checks_bytes(tmp_path):
    p = tmp_path / "f.map26a"
    p.write_bytes(b"original")
    mapgen.check_existing(p, hashlib.sha256(b"original").hexdigest())
    with pytest.raises(ValueError, match="different"):
        mapgen.check_existing(p, "0" * 64)


def test_adjacent_pool_seeds_cannot_overlap():
    screen = {mapgen.seed_for("screen", 2026102001, i) for i in range(100)}
    confirm = {mapgen.seed_for("confirm", 2026102002, i) for i in range(60)}
    assert len(screen) == 100 and len(confirm) == 60
    assert screen.isdisjoint(confirm)

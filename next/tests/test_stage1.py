import json
import struct
import zipfile

import pytest

from lab import core, stage1
from lab.environment import Environment


def test_binary_trace_roundtrip_and_duplicate_rejection(tmp_path):
    actions = json.dumps([{"action":{"kind":"wait"},"code":0,"result":True}]).encode()
    row = (b"S1B!" + struct.pack("<8I", 1, 0, 200000, 40000, 60000, 0, 1, len(actions))
           + struct.pack("<24f", *([1]*24)) + bytes(768) + bytes([1]+[0]*15)
           + bytes(64) + struct.pack("<2i", 2, 3) + actions)
    path = tmp_path/"probe.zip"
    def write(data):
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("team-a.stdout", bytes(4)+data)
            archive.writestr("team-b.stdout", b"")
    write(row)
    result = stage1.traces(path)[(1,0)]
    assert result["features"] == [1]*24
    assert result["moves"] == [[2,3]]
    assert result["actions"][0]["action"]["kind"] == "wait"
    write(row+row)
    with pytest.raises(ValueError, match="Duplicate"):
        stage1.traces(path)


def test_environment_rejects_holdout_before_worker_access():
    env = object.__new__(Environment)
    with pytest.raises(ValueError, match="sealed"):
        env.reset("generated/confirm/g1-confirm-000")
    with pytest.raises(ValueError, match="sealed"):
        env.reset(core.config()["maps"]["confirm"][0])
    path=core.MAPS/"generated/screen/../confirm/g1-confirm-000.map26a"
    with pytest.raises(ValueError,match="sealed"):
        Environment._validate_maps({"op":"batch","commands":[{"op":"reset","map":str(path)}]})


def test_float_comparison_rejects_shape_and_nan():
    assert not stage1.close_float([1,2],[1])
    assert not stage1.close_float(float("nan"),0)
    assert stage1.close_float([1],[1.000001])

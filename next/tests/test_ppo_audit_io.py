import importlib.util
from pathlib import Path
import numpy as np
import pytest


def test_audit_materialization_preserves_bits_dtypes_and_restores_numpy(tmp_path):
    path=Path(__file__).resolve().parents[1]/'tools/verify_ppo_captures.py'
    spec=importlib.util.spec_from_file_location('verify_ppo_captures',path);driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
    bits=np.array([0,0x80000000,1,0x3f800000,0x7f7fffff],np.uint32);mask=np.array([[True,False]])
    p=tmp_path/'shard.npz';np.savez_compressed(p,weights=bits.view(np.float32),mask=mask,action=np.array([-1,2],np.int16))
    original=np.load
    with pytest.raises(RuntimeError):
        with driver.materialized_reads():
            with np.load(p,allow_pickle=False) as d:
                for _ in range(3):np.testing.assert_array_equal(d['weights'].view(np.uint32),bits)
                np.testing.assert_array_equal(d['mask'],mask);assert d['action'].dtype==np.int16
            raise RuntimeError('interrupted audit')
    assert np.load is original

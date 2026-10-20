import copy
import numpy as np
import pytest
from lab import wealth_state as w,monotone_critic as m


def test_net_worth_is_preserved_by_native_shard_fusion(monkeypatch):
    monkeypatch.setattr(w.central,'make_state',lambda *args:np.zeros(68,np.float32))
    units=[dict(team=i,gold=500 if i==0 else 0,items=[0]*42) for i in (0,1)]
    o=dict(actor=dict(team=0,round=1000))
    before=w.make_state(o,units,{},None)
    units[0]['gold']=350;units[0]['items'][1]=1
    after=w.make_state(o,units,{},None)
    assert after[68]==pytest.approx(.03)
    assert after[69]==before[69]==pytest.approx(.1)
    assert after[71]==pytest.approx(.05)
    other=w.make_state(dict(actor=dict(team=1,round=1000)),units,{},None)
    np.testing.assert_array_equal(after[68:],-other[68:])


def test_inventory_rejects_missing_or_fractional_counts(monkeypatch):
    monkeypatch.setattr(w.central,'make_state',lambda *args:np.zeros(68,np.float32))
    units=[dict(team=i,gold=0,items=[0]*42) for i in (0,1)]
    units[0]['items'][3]=.5
    with pytest.raises(ValueError,match='inventory'):w.make_state(dict(actor=dict(team=0,round=1)),units,{},None)


def test_economy_features_remain_odd_under_team_swap():
    rng=np.random.default_rng(5);s=np.zeros((30,74),np.float32)
    s[:,26:28]=rng.uniform(0,.99,(30,2));s[:,0]=s[:,26]-s[:,27];s[:,1]=rng.uniform(0,1,30)
    s[:,44:]=rng.normal(size=(30,30));other=s.copy();other[:,26:28]=s[:,27:25:-1];other[:,0]*=-1;other[:,44:]*=-1
    for mode in ('wealth','wealth_banks','team_wealth','team_banks_wealth'):
        np.testing.assert_allclose(m.features(s,mode),-m.features(other,mode),atol=1e-6)

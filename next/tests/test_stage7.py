import pytest
from lab import stage7


def game(a,b,m,outcome='teamA',faults=0,fuel=0):
    return dict(name_a=a,name_b=b,map=m,outcome=outcome,teams={
        'teamA':dict(faults=faults,fuel_exhausted=fuel,gems=10),
        'teamB':dict(faults=0,fuel_exhausted=0,gems=0)})


def test_paired_gate_rejects_missing_duplicate_and_unfinished_games():
    rows=[game('new','starter','map'),game('starter','new','map','teamB')]
    assert stage7.assess(rows,'new','starter',['map'])['win_fraction']==1
    for bad in (rows[:1],rows+rows[:1],[rows[0],rows[1]|{'error':'timeout'}]):
        with pytest.raises(ValueError):stage7.assess(bad,'new','starter',['map'])


def test_runtime_and_strength_are_separate_requirements():
    rows=[game('new','starter','map',faults=1),game('starter','new','map','teamB')]
    report=stage7.assess(rows,'new','starter',['map'])
    assert report['win_fraction']==1 and report['faults']==1
    assert not stage7.accepts(report,.9,0,1)
    rows[0]['teams']['teamA'].update(faults=0,fuel_exhausted=3)
    assert not stage7.accepts(stage7.assess(rows,'new','starter',['map']),.9,0,1)


def test_seat_split_cannot_disguise_losses():
    rows=[game('new','starter','map'),game('starter','new','map')]
    r=stage7.assess(rows,'new','starter',['map'])
    assert r['as_a']==1 and r['as_b']==0 and r['win_fraction']==.5
    assert not stage7.accepts(r,.9,0,1)


def test_confirmation_can_resume_same_bytes_but_cannot_be_reused_for_tuning(tmp_path):
    path=tmp_path/'attempt.json';plan=dict(candidate='v1',wasm_sha256='aaa',map_sha256={'heldout':'bbb'})
    stage7.lock_confirmation(path,plan);stage7.lock_confirmation(path,plan)
    with pytest.raises(ValueError):stage7.lock_confirmation(path,plan|{'candidate':'v2'})
    with pytest.raises(ValueError):stage7.lock_confirmation(path,plan|{'map_sha256':{'heldout':'changed'}})


def test_replacement_pool_cannot_rename_consumed_maps():
    old=dict(map_sha256={'old-name':'already-used'})
    stage7.require_fresh_confirmation(dict(map_sha256={'fresh':'new-bytes'}),[old])
    with pytest.raises(ValueError):
        stage7.require_fresh_confirmation(dict(map_sha256={'renamed':'already-used'}),[old])


def test_replacement_gate_preserves_frozen_dataset_reservation_and_thresholds():
    base=dict(maps=dict(confirm=['original'],screen=['development']),gate=dict(vs_weak=.9))
    adapted=stage7.promotion_config(base,dict(confirmation_maps=['fresh']))
    assert adapted['maps']['confirm']==['fresh']
    assert base['maps']['confirm']==['original']
    assert adapted['maps']['screen']==base['maps']['screen']
    assert adapted['gate']==base['gate']

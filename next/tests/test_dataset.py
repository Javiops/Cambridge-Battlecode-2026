import pytest

from lab import dataset


def test_unsupported_action_keeps_null_label_instead_of_wait():
    encoded={'actions':[{'kind':'wait'},{'kind':'move','x':1,'y':2},None],'mask':[True,True,False]}
    assert dataset.proposal_label({'kind':'move','x':8,'y':9},encoded) is None
    assert dataset.proposal_label({'kind':'wait','reason':0},encoded)==0
    assert dataset.proposal_label({'kind':'wait','reason':1},encoded) is None


def test_partition_audit_rejects_map_or_lineage_leakage():
    episodes=[{'split':'train','map_sha256':'a','lineages':['ours','idle']},
              {'split':'validation','map_sha256':'b','lineages':['starter']}]
    dataset.validate_splits(episodes)
    episodes[1]['map_sha256']='a'
    with pytest.raises(ValueError,match='map'):dataset.validate_splits(episodes)
    episodes[1]['map_sha256']='b';episodes[1]['lineages']=['ours']
    with pytest.raises(ValueError,match='lineage'):dataset.validate_splits(episodes)


def test_validation_map_families_are_separate():
    episodes=[{'split':'train','map_sha256':'a','lineages':['ours'],'family':0},
              {'split':'validation','map_sha256':'b','lineages':['sdk'],'family':0}]
    with pytest.raises(ValueError,match='family'):dataset.validate_splits(episodes)


def test_fault_or_incomplete_game_cannot_get_a_training_label():
    with pytest.raises(ValueError,match='complete'):dataset.completed_outcome({'round':10,'outcome':'draw'})
    assert dataset.completed_outcome({'round':2000,'outcome':'teamB'})=='teamB'


def test_quarantine_keeps_schedule_but_excludes_both_seats():
    rows=[{'map_sha256':'m','wasm_sha256':['a','b'],'status':'quarantined'},
          {'map_sha256':'m','wasm_sha256':['b','a'],'status':'admitted'},
          {'map_sha256':'n','wasm_sha256':['a','b'],'status':'admitted'}]
    dataset.quarantine_pairs(rows)
    assert len(rows)==3
    assert [r['status'] for r in rows]==['quarantined','quarantined','admitted']

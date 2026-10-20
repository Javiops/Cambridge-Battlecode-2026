import copy

import pytest

from lab import stage1


def sample():
    panel={"starter":"a","seed":"b","skip":"c"}
    games=[dict(a=a,b=b,map="screen",outcome="teamB",teams={
        t:dict(faults=0,fuel_exhausted=0) for t in ("teamA","teamB")}) for a in panel.values() for b in panel.values()]
    return games,panel,["screen"],{"starter":100,"seed":95,"skip":80},["starter","seed"],["skip"]


def test_calibration_requires_complete_ordered_schedule():
    args=list(sample());assert stage1.check_calibration(*args)["games"]==9
    args[0]=args[0][:-1]
    with pytest.raises(ValueError,match="schedule"):stage1.check_calibration(*args)


@pytest.mark.parametrize("field",["faults","fuel_exhausted"])
def test_calibration_rejects_faults_and_fuel(field):
    args=list(sample());args[0][0]["teams"]["teamA"][field]=1
    with pytest.raises(ValueError,match="fault|fuel"):stage1.check_calibration(*args)


def test_calibration_must_resolve_control_ordering():
    args=list(sample());args[3]["skip"]=101
    with pytest.raises(ValueError,match="handicap"):stage1.check_calibration(*args)


def test_saved_proofs_are_bound_to_current_sources():
    proof={"passed":True,"sources":{"engine":"old"}}
    with pytest.raises(ValueError,match="stale"):stage1.require_proof(proof,{"engine":"new"})
    proof["sources"]={"engine":"new"};stage1.require_proof(proof,{"engine":"new"})
    proof["passed"]=False
    with pytest.raises(ValueError,match="failed"):stage1.require_proof(proof,{"engine":"new"})

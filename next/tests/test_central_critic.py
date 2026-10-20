import copy
import numpy as np
import pytest
from lab import central_critic as c,critic


def units():
    return [dict(id=i,team=i,x=2+10*i,y=2,health=500,max_health=600,strength=35,focus=80,state=2073,gold=100+100*i,gems=10+20*i) for i in (0,1)]


def test_team_features_are_current_perspective_antisymmetric_and_not_outcomes():
    u=units();terrain={'altars':[[8,8]]}
    a=c.team_features(u,0,terrain,100);b=c.team_features(u,1,terrain,100)
    np.testing.assert_array_equal(a,-b)
    altered=copy.deepcopy(u)
    for unit in altered:unit.update(future_gold=999999,terminal_win=True)
    np.testing.assert_array_equal(a,c.team_features(altered,0,terrain,100))
    altered[1]['gems']+=50
    assert c.team_features(altered,0,terrain,100)[0]<a[0]


def test_invalid_world_snapshot_fails_closed():
    with pytest.raises(ValueError,match='roster'):c.team_features(units()*2,0,{'altars':[[8,8]]},1)
    u=units();u[0]['gold']=np.nan
    with pytest.raises(ValueError,match='unit state'):c.team_features(u,0,{'altars':[[8,8]]},1)


def test_offset_gradient_and_hessian_match_finite_differences():
    rng=np.random.default_rng(15);x=rng.normal(size=(8,3));coef=rng.normal(size=3)
    offset=rng.normal(size=8);y=rng.integers(0,2,8,dtype=np.uint8);w=np.full(8,1/8)
    _,g,h=c.residual_objective(coef,x,y,w,.1,offset)
    for j in range(3):
        delta=np.zeros(3);delta[j]=1e-6
        a,ga,_=c.residual_objective(coef+delta,x,y,w,.1,offset)
        b,gb,_=c.residual_objective(coef-delta,x,y,w,.1,offset)
        assert g[j]==pytest.approx((a-b)/2e-6,abs=1e-8)
        np.testing.assert_allclose(h[:,j],(ga-gb)/2e-6,atol=1e-8)


def test_zero_shrinkage_preserves_the_unweakened_score_baseline():
    state=np.zeros((5,c.FEATURES),np.float32);state[:,0]=np.linspace(-1,1,5)
    base=dict(coef=np.array([2,0,0,0,.1],np.float32),mean=np.zeros(4,np.float32),scale=np.ones(4,np.float32))
    residual=dict(coef=np.ones(24,np.float32),scale=np.ones(24,np.float32),indexes=c.columns('team'))
    model=dict(baseline=base,residual=residual,shrinkage=0.)
    np.testing.assert_array_equal(c.predict(model,state),critic.predict(base,state))


def test_identical_team_states_have_zero_team_residual():
    state=np.zeros((1,c.FEATURES),np.float32)
    head=dict(indexes=c.columns('team'),coef=np.ones(24,np.float32),scale=np.ones(24,np.float32))
    np.testing.assert_array_equal(c.residual_logits(head,state),[0])
    with pytest.raises(ValueError,match='Unknown'):c.columns('future')


def test_acceptance_requires_both_proper_scores_against_both_references():
    scores=dict(constant=dict(brier=.25,log_loss=.693),score_time=dict(brier=.13,log_loss=.4),critic=dict(brier=.12,log_loss=.38))
    assert c.acceptance(scores)
    scores['critic']['log_loss']=.41
    assert not c.acceptance(scores)
    scores['critic']['log_loss']=.38;scores['critic']['brier']=.13
    assert not c.acceptance(scores)  # Equal is not an improvement.
    scores['critic']['brier']=np.nan
    with pytest.raises(ValueError,match='gate metric'):c.acceptance(scores)


def test_residual_fit_with_strong_new_signal_can_improve_a_frozen_baseline():
    rng=np.random.default_rng(55);state=np.zeros((100,c.FEATURES),np.float32)
    state[:,44]=rng.normal(size=100);y=(state[:,44]>0).astype(np.uint8);w=np.full(100,.01)
    base=dict(coef=np.zeros(5,np.float32),mean=np.zeros(4,np.float32),scale=np.ones(4,np.float32))
    cfg=dict(newton_iterations=50,newton_tolerance=1e-7,line_search_steps=24)
    original=copy.deepcopy(base);head=c.fit_residual(state,y,w,base,'team',.01,cfg)
    model=dict(baseline=base,residual=head,shrinkage=.5)
    assert critic.metrics(y,c.predict(model,state),w)['brier']<.15
    for key in base:np.testing.assert_array_equal(base[key],original[key])

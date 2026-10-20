import numpy as np
import pytest

from lab import cloning, critic, policy


def config():
    return dict(newton_iterations=50,newton_tolerance=1e-7,line_search_steps=24)


def test_only_complete_binary_outcomes_have_terminal_values():
    assert critic.terminal_value({'outcome':'teamA','round':20},0)==1
    assert critic.terminal_value({'outcome':'teamA','round':20},1)==-1
    assert critic.terminal_value({'outcome':'teamB','round':2000},1)==1
    for terminal in (None,{'outcome':'draw','round':2000},{'round':20}):
        with pytest.raises(ValueError,match='complete'):
            critic.terminal_value(terminal,0)


def test_games_and_both_seats_get_equal_weight_despite_frame_counts():
    episode=np.array(['a']*5+['b']*3);team=np.array([0,0,0,0,1,0,1,1])
    weights=critic.group_weights(episode,team)
    assert weights[:4].sum()==pytest.approx(.25)
    assert weights[4]==pytest.approx(.25)
    assert weights[5]==pytest.approx(.25)
    assert weights[6:].sum()==pytest.approx(.25)
    assert weights.sum()==pytest.approx(1)
    with pytest.raises(ValueError,match='missing a team'):
        critic.group_weights(np.array(['a','a']),np.array([0,0]))


def test_critic_gradient_and_hessian_match_finite_differences():
    rng=np.random.default_rng(3);x=np.c_[rng.normal(size=(12,4)),np.ones(12)]
    y=rng.integers(0,2,12);w=np.full(12,1/12);coef=rng.normal(size=5)
    _,gradient,hessian=critic.objective(coef,x,y,w,.1)
    for j in range(5):
        delta=np.zeros(5);delta[j]=1e-5
        plus,gplus,_=critic.objective(coef+delta,x,y,w,.1)
        minus,gminus,_=critic.objective(coef-delta,x,y,w,.1)
        assert gradient[j]==pytest.approx((plus-minus)/2e-5,abs=1e-8)
        np.testing.assert_allclose(hessian[:,j],(gplus-gminus)/2e-5,atol=1e-8)


def test_readout_learns_signal_and_handles_constant_features():
    x=np.c_[np.linspace(-2,2,80),np.ones(80)];y=(x[:,0]>0).astype(float);w=np.full(80,1/80)
    head=critic.fit(x,y,w,.01,config());p=critic.predict(head,x)
    assert np.mean((p>=.5)==y)>.95
    assert critic.metrics(y,p,w)['brier']<.1
    assert np.isfinite(head['coef']).all() and head['scale'][1]==1


def test_encoder_uses_frozen_bc_features_and_ignores_padding():
    rng=np.random.default_rng(12)
    f=rng.normal(size=(3,24)).astype(np.float32);c=rng.normal(size=(3,16,12)).astype(np.float32)
    mask=np.zeros((3,16),bool);mask[:,:4]=True;team=np.array([0,1,0]);w=np.array(policy.weights(),np.float32)
    original=w.copy();a=critic.encode(w,f,c,mask,team)
    c[:,4:]*=1000
    b=critic.encode(w,f,c,mask,team)
    np.testing.assert_array_equal(a,b);np.testing.assert_array_equal(w,original)
    assert a.shape==(3,44) and a.dtype==np.float32
    np.testing.assert_array_equal(a[:,2],[-1,1,-1])
    changed=critic.encode(w*2,f,c,mask,team)
    assert not np.array_equal(a[:,28:],changed[:,28:])


def test_exact_known_calibration_metrics_and_probability_validation():
    y=np.array([0,1]);w=np.array([.5,.5])
    constant=critic.metrics(y,np.array([.5,.5]),w)
    assert constant['brier']==.25 and constant['log_loss']==pytest.approx(np.log(2))
    assert constant['expected_calibration_error']==0
    perfect=critic.metrics(y,np.array([0.,1.]),w)
    assert perfect['brier']<1e-20
    for p in (np.array([np.nan,.5]),np.array([-.1,.5])):
        with pytest.raises(ValueError,match='probabilities'):
            critic.metrics(y,p,w)


def test_extreme_logits_are_stable():
    np.testing.assert_allclose(critic.sigmoid(np.array([-10000.,0.,10000.])),[0.,.5,1.])


def test_whole_map_development_is_required():
    data=dict(state=np.zeros((2,44),np.float32),win=np.array([0,1]),team=np.array([0,1]),
              episode=np.array(['game','game']),map=np.array(['one','one']),round=np.array([1,1]),weight=np.array([.5,.5]))
    with pytest.raises(ValueError,match='whole-map'):
        critic.select(data,{'development_maps':['one']},44)


def test_export_roundtrip_preserves_backbone_and_rejects_invalid_scale(tmp_path):
    path=tmp_path/'critic.npz';backbone=np.asarray(policy.weights(),np.float32)
    head=dict(coef=np.zeros(45,np.float32),mean=np.zeros(44,np.float32),scale=np.ones(44,np.float32))
    np.savez(path,**head,backbone=backbone)
    loaded,frozen=critic.load_export(path)
    np.testing.assert_array_equal(frozen,backbone)
    np.testing.assert_array_equal(critic.predict(loaded,np.zeros((2,44),np.float32)),[.5,.5])
    head['scale'][0]=0;np.savez(path,**head,backbone=backbone)
    with pytest.raises(ValueError,match='invalid exported'):
        critic.load_export(path)


def test_critic_estimate_is_separate_from_exact_terminal_result():
    head=dict(coef=np.zeros(45,np.float32),mean=np.zeros(44,np.float32),scale=np.ones(44,np.float32))
    p=critic.predict(head,np.zeros((1,44),np.float32))
    assert (2*p-1)[0]==0  # An uncertain estimate is allowed; it is not a draw label.
    assert critic.terminal_value({'outcome':'teamB','round':2000},0)==-1


def test_uint8_outcome_labels_cannot_wrap_on_negation_in_log_loss():
    y=np.array([0,1],np.uint8);p=np.array([.5,.5]);w=np.array([.5,.5])
    assert critic.metrics(y,p,w)['log_loss']==pytest.approx(np.log(2))
    rng=np.random.default_rng(51);p=rng.uniform(.01,.99,2)
    assert critic.metrics(y,p,w)==critic.metrics(y.astype(np.float64),p,w)

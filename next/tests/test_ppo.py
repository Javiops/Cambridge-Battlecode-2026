import numpy as np
import pytest
from lab import ppo_math as p,cloning,policy


def tensors():
    rng=np.random.default_rng(97);n=7
    x=rng.normal(size=(n,24));c=rng.normal(size=(n,16,12));mask=rng.random((n,16))>.3;mask[:,0]=True
    action=np.array([np.flatnonzero(m)[0] for m in mask]);w=np.array(policy.weights(),np.float64)
    scores=cloning.forward(w,x,c)[0];_,logp=p.distribution(scores,mask)
    data=dict(features=x,candidates=c,mask=mask,action=action,old_logits=scores+.03*rng.normal(size=scores.shape),
        old_logp=logp[np.arange(n),action]+.01,anchor_logits=scores+.1*rng.normal(size=scores.shape))
    return w,data,rng.normal(size=n)


def test_ppo_gradient_including_mask_entropy_and_bc_anchor():
    w,data,adv=tensors();cfg=dict(clip_ratio=.2,entropy_coefficient=.01,bc_kl_coefficient=.03)
    _,grad,_=p.loss_gradient(w,data,adv,cfg)
    for j in range(0,305,11):
        d=np.zeros_like(w);d[j]=1e-6
        a=p.loss_gradient(w+d,data,adv,cfg)[0];b=p.loss_gradient(w-d,data,adv,cfg)[0]
        assert grad[j]==pytest.approx((a-b)/2e-6,abs=1e-7)


def test_clipped_positive_and_negative_advantages_have_no_surrogate_gradient():
    w,data,adv=tensors();cfg=dict(clip_ratio=.2,entropy_coefficient=0.,bc_kl_coefficient=0.)
    scores=cloning.forward(w,data['features'],data['candidates'])[0];_,lp=p.distribution(scores,data['mask'])
    a=np.array([1.,-1.,1.,-1.,1.,-1.,1.]);ratio=np.where(a>0,1.5,.5)
    data['old_logp']=lp[np.arange(len(a)),data['action']]-np.log(ratio)
    _,gradient,measured=p.loss_gradient(w,data,a,cfg)
    np.testing.assert_allclose(gradient,0.,atol=1e-12);assert measured['clip_fraction']==1.


def test_gae_lambda_one_is_terminal_return_minus_old_value_for_each_champion():
    ep=np.array([0,0,0,0,1,1]);team=np.array([0,1,0,1,0,0]);actor=np.array([0,3,0,3,0,0]);r=np.array([1,1,500,500,1,2])
    v=np.array([.2,-.7,.5,-.1,.8,.2]);outcome=np.array([1,-1,1,-1,-1,-1])
    a,ret=p.advantages(ep,team,actor,r,v,outcome)
    np.testing.assert_allclose(a,outcome-v);np.testing.assert_allclose(ret,outcome)


def test_gae_uses_round_gaps_and_does_not_discount_twice_within_one_turn():
    a,_=p.advantages([0,0,0],[0,0,0],[0,0,0],[1,1,3],[0,0,0],[1,1,1],lam=.5)
    np.testing.assert_allclose(a,[.25,.25,1.])
    with pytest.raises(ValueError,match='complete'):p.advantages([0],[0],[0],[1],[0],[0])


def test_padding_is_never_a_probability_or_a_valid_training_action():
    prob,logp=p.distribution([[1.,2.,1e9]],[[True,True,False]])
    assert prob[0,2]==0 and np.isneginf(logp[0,2]);assert prob.sum()==pytest.approx(1.)
    w,data,adv=tensors();data['action'][0]=-1
    with pytest.raises(ValueError,match='Masked'):p.loss_gradient(w,data,adv,dict(clip_ratio=.2,entropy_coefficient=0,bc_kl_coefficient=0))


def test_kl_limit_rolls_back_weights_and_optimizer_state():
    w,data,adv=tensors();scores=cloning.forward(w,data['features'],data['candidates'])[0]
    data['old_logits']=scores.copy();_,lp=p.distribution(scores,data['mask']);data['old_logp']=lp[np.arange(len(adv)),data['action']]
    config=dict(clip_ratio=.2,entropy_coefficient=.01,bc_kl_coefficient=.01,epochs=2,batch_size=7,
        max_gradient_norm=.5,learning_rate=.1,maximum_kl=1e-7,target_kl=1e-8)
    updated,opt,report=p.update(w,data,adv,config,np.random.default_rng(21))
    np.testing.assert_array_equal(updated,w.astype(np.float32));assert opt[2]==0
    assert report['history'][0]['rolled_back'] and report['optimizer_updates']==0


def test_on_policy_critic_refit_starts_from_supplied_prior(monkeypatch):
    from lab import ppo
    rng=np.random.default_rng(9);x=np.c_[rng.normal(size=200),np.ones(200)]
    y=(x[:,0]>0).astype(np.uint8);weights=np.full(200,.005)
    monkeypatch.setattr(ppo,'design',lambda state:state)
    monkeypatch.setattr(ppo,'cfg',lambda:dict(value_l2=.01,value_iterations=80,value_tolerance=1e-6))
    fitted=ppo.value_fit(x,y,weights,np.array([0.,0.],np.float32))
    assert fitted[0]>1 and np.isfinite(fitted).all()
    with pytest.raises(ValueError,match='complete'):p.advantages([0],[0],[0],[1],[0],[1],gamma=.99)

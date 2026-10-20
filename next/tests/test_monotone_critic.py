import numpy as np
import pytest
from lab import monotone_critic as m,critic


def test_constrained_objective_gradient_and_hessian():
    rng=np.random.default_rng(98);x=rng.normal(size=(9,4));coef=rng.normal(size=4);y=rng.integers(0,2,9,dtype=np.uint8);w=np.full(9,1/9)
    _,gradient,hessian=m.box_objective(coef,x,y,w,.1)
    for j in range(4):
        delta=np.zeros(4);delta[j]=1e-6
        a,ga,_=m.box_objective(coef+delta,x,y,w,.1);b,gb,_=m.box_objective(coef-delta,x,y,w,.1)
        assert gradient[j]==pytest.approx((a-b)/2e-6,abs=1e-8)
        np.testing.assert_allclose(hessian[:,j],(ga-gb)/2e-6,atol=1e-8)


def test_banking_curves_are_odd_under_team_swap():
    rng=np.random.default_rng(13);s=np.zeros((20,68),np.float32)
    s[:,26:28]=rng.uniform(0,.99,(20,2));s[:,0]=s[:,26]-s[:,27];s[:,1]=rng.uniform(0,1,20)
    opposite=s.copy();opposite[:,26]=s[:,27];opposite[:,27]=s[:,26];opposite[:,0]*=-1
    np.testing.assert_allclose(m.features(s,'banks'),-m.features(opposite,'banks'),atol=1e-7)


def test_fit_never_learns_negative_advantage_coefficients():
    rng=np.random.default_rng(32);s=np.zeros((100,68),np.float32);s[:,44:68]=rng.normal(size=(100,24))
    y=(s[:,44]-s[:,45]>0).astype(np.uint8);w=np.full(100,.01)
    base=dict(coef=np.zeros(5,np.float32),mean=np.zeros(4,np.float32),scale=np.ones(4,np.float32))
    cfg=dict(temperature_bounds=[.25,2.],box_iterations=120,box_tolerance=1e-6,line_search_steps=24)
    head=m.fit(s,y,w,base,'team',.01,cfg)
    assert np.all(head['coef'][1:]>=0)
    assert .25<=head['coef'][0]<=2.
    model=dict(head=head,baseline=base,shrinkage=1.)
    p=m.predict(model,s);raised=s.copy();raised[:,44]+=1
    assert np.all(m.predict(model,raised)>=p)
    # The misleading feature was generated with the opposite sign; it is discarded.
    assert head['coef'][2]==0


def test_no_residual_with_identity_temperature_matches_baseline():
    s=np.zeros((3,68),np.float32);s[:,0]=[-1,0,1]
    base=dict(coef=np.array([2,0,0,0,0],np.float32),mean=np.zeros(4,np.float32),scale=np.ones(4,np.float32))
    model=dict(baseline=base,head=dict(mode='temperature',coef=np.array([1.],np.float32),scale=np.empty(0,np.float32)),shrinkage=.5)
    np.testing.assert_array_equal(m.predict(model,s),critic.predict(base,s))

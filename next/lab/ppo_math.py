"""Masked categorical PPO and per-champion, round-aware complete-episode GAE.

The 305-parameter actor and its inputs are unchanged from behavioural cloning.
Opponent decisions and deterministic controller actions never enter its gradient.
"""
from __future__ import annotations
import numpy as np
from . import cloning,policy


def distribution(scores,mask):
    scores=np.asarray(scores,np.float64);mask=np.asarray(mask,bool)
    if scores.shape!=mask.shape or not mask.any(axis=1).all() or not np.isfinite(scores).all():
        raise ValueError('Invalid masked categorical distribution')
    shifted=np.where(mask,scores,-np.inf);shifted-=shifted.max(axis=1,keepdims=True)
    logp=shifted-np.log(np.exp(shifted).sum(axis=1,keepdims=True))
    return np.exp(logp),logp


def loss_gradient(w,data,advantage,cfg):
    x,c,mask,action=(data[k] for k in ('features','candidates','mask','action'))
    if not mask[np.arange(len(x)),action].all() or np.any(action<0):raise ValueError('Masked PPO action')
    scores,z,h=cloning.forward(w,x,c);p,logp=distribution(scores,mask)
    old_p,old_all=distribution(data['old_logits'],mask)
    selected=logp[np.arange(len(x)),action]
    ratio=np.exp(selected-data['old_logp']);a=np.asarray(advantage,np.float64)
    clipped=np.clip(ratio,1-cfg['clip_ratio'],1+cfg['clip_ratio'])
    surrogate=np.minimum(ratio*a,clipped*a)
    active=np.where(a>=0,ratio<=1+cfg['clip_ratio'],ratio>=1-cfg['clip_ratio'])
    dscore=p.copy();dscore[np.arange(len(x)),action]-=1
    dscore*=((a*ratio*active)/len(x))[:,None]
    safe=np.where(mask,logp,0.);entropy=-np.sum(p*safe,axis=1)
    dscore+=cfg['entropy_coefficient']/len(x)*p*(safe+entropy[:,None])
    anchor_p,anchor_log=distribution(data['anchor_logits'],mask)
    anchor_kl=np.sum(anchor_p*(np.where(mask,anchor_log,0.)-safe),axis=1)
    dscore+=cfg['bc_kl_coefficient']/len(x)*(p-anchor_p)
    _,_,_,out,_=cloning.unpack(w)
    dz=dscore[:,:,None]*out*(z>0);context=dz.sum(axis=1)
    gradient=np.r_[(x.T@context).ravel(),np.einsum('bkc,bkh->ch',c,dz).ravel(),context.sum(axis=0),
        np.einsum('bk,bkh->h',dscore,h),0.]
    kl=np.sum(old_p*(np.where(mask,old_all,0.)-safe),axis=1)
    loss=-float(np.mean(surrogate))-cfg['entropy_coefficient']*float(entropy.mean())+cfg['bc_kl_coefficient']*float(anchor_kl.mean())
    return loss,gradient,dict(kl=float(np.mean(kl)),entropy=float(entropy.mean()),
        clip_fraction=float(np.mean(np.abs(ratio-1)>cfg['clip_ratio'])),ratio_max=float(ratio.max()),ratio_min=float(ratio.min()))


def advantages(episode,team,actor,round_number,value,outcome,gamma=1.,lam=1.):
    """Never bootstrap through another champion, enemy, or episode.

    Only complete episodes are admitted. The final sampled state receives the
    actual terminal team reward; subsampled gaps use elapsed rounds, not a new
    arbitrary discount per API call. With gamma=lambda=1 this is exactly R-V.
    """
    arrays=[np.asarray(v) for v in (episode,team,actor,round_number,value,outcome)]
    episode,team,actor,round_number,value,outcome=arrays
    if gamma!=1 or not 0<lam<=1 or len({len(v) for v in arrays})!=1 or not np.isin(outcome,(-1,1)).all():
        raise ValueError('GAE needs aligned complete binary outcomes')
    result=np.zeros(len(value),np.float64)
    keys=np.stack((episode,team,actor),axis=1)
    for key in np.unique(keys,axis=0):
        indices=np.flatnonzero(np.all(keys==key,axis=1));r=round_number[indices]
        if np.any(np.diff(r.astype(np.int64))<0) or len(np.unique(outcome[indices]))!=1:raise ValueError('Corrupt champion trajectory')
        acc=0.
        for j in range(len(indices)-1,-1,-1):
            i=indices[j]
            if j==len(indices)-1:delta=outcome[i]-value[i];acc=delta
            else:
                nxt=indices[j+1];elapsed=int(round_number[nxt])-int(round_number[i])
                discount=gamma**elapsed;delta=discount*value[nxt]-value[i]
                acc=delta+discount*lam**elapsed*acc
            result[i]=acc
    return result,result+value


def update(w,data,advantage,cfg,rng,optimizer=None):
    w=np.asarray(w,np.float64).copy();m,v,step=(np.zeros_like(w),np.zeros_like(w),0) if optimizer is None else optimizer
    a=np.asarray(advantage,np.float64);a=(a-a.mean())/max(float(a.std()),1e-8)
    history=[];updates=0;initial_step=step
    for epoch in range(cfg['epochs']):
        backup=(w.copy(),m.copy(),v.copy(),step)
        for indices in np.array_split(rng.permutation(len(a)),max(1,int(np.ceil(len(a)/cfg['batch_size'])))):
            batch={k:val[indices] for k,val in data.items()};_,gradient,_=loss_gradient(w,batch,a[indices],cfg)
            norm=float(np.linalg.norm(gradient));gradient*=min(1.,cfg['max_gradient_norm']/max(norm,1e-12))
            step+=1;m=.9*m+.1*gradient;v=.999*v+.001*gradient*gradient
            w-=cfg['learning_rate']*(m/(1-.9**step))/(np.sqrt(v/(1-.999**step))+1e-8);updates+=1
            if not np.isfinite(w).all():raise ValueError('Nonfinite PPO update')
        loss,_,measured=loss_gradient(w,data,a,cfg);row=dict(epoch=epoch+1,loss=loss,**measured)
        if measured['kl']>cfg['maximum_kl']:
            w,m,v,step=backup;row['rolled_back']=True;history.append(row);break
        history.append(row)
        if measured['kl']>cfg['target_kl']:break
    exported=w.astype(np.float32);_,_,final=loss_gradient(exported.astype(np.float64),data,a,cfg)
    if final['kl']>cfg['maximum_kl']+1e-6:raise ValueError('Export exceeds PPO KL bound')
    return exported,(m,v,step),dict(history=history,attempted_optimizer_updates=updates,optimizer_updates=step-initial_step,**final)

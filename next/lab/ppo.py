"""Stage 5: reproducible native self-play PPO from BC and the accepted outcome critic.

Native policy evaluation is a training milestone. Production WASM integration and
fuel certification remain Stage 6; this module never changes the live champion.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import numpy as np
from . import core,dataset,mapgen,policy,cloning,critic,monotone_critic as accepted,wealth_state,ppo_math


def cfg():return core.config()['stage5']
def root():return core.ROOT/'datasets'/cfg()['dataset']
def folder():return core.ROOT/'models'/cfg()['model']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,value):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');return value
def digest(value):return dataset.digest(value)
def source_hashes():
    paths=sorted((core.ROOT/'lab').glob('ppo*'))+[core.ROOT/'lab'/n for n in ('policy.py','cloning.py','engine.mjs','critic-inventory-state.mjs','critic-state.mjs','wealth_state.py','monotone_critic.py')]
    return {p.relative_to(core.ROOT).as_posix():hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest() for p in paths if p.is_file()}


def parents():
    actor=core.ROOT/'models'/cfg()['actor_parent']/'weights.f32';value=core.ROOT/'models'/cfg()['critic_parent']/'critic.npz'
    if core.sha(actor)!=cfg()['actor_sha256'] or core.sha(value)!=cfg()['critic_sha256']:raise ValueError('PPO starting model changed')
    passed=read(core.ROOT/'results/stage4-v5-ready.json')
    if not passed['passed'] or not passed['predictive_acceptance_passed'] or passed['model']!=cfg()['critic_parent']:raise ValueError('PPO requires an accepted critic')
    accepted.frozen();model=accepted.load_model()
    if model['shrinkage']!=1.:raise ValueError('Initialize the exact accepted critic, including shrinkage')
    return np.fromfile(actor,dtype='<f4'),model


def design(state):
    _,model=parents();x=accepted.features(state,model['head']['mode'])/model['head']['scale']
    return np.c_[accepted.central.base_logits(model['baseline'],state),x,np.ones(len(state))].astype(np.float64)


def initial_value():return np.r_[parents()[1]['head']['coef'],0.].astype(np.float32)
def value(theta,state):return 2*critic.sigmoid(design(state)@theta)-1


def value_fit(state,y,weight,prior):
    """On-policy binary outcome refit, regularized toward the preceding checkpoint.

    No labels from the batch enter the OLD values/GAE used for its actor update.
    Fixed normalization and the initial coefficients come from accepted outcome-v5.
    An initially zero intercept permits on-policy recalibration without changing it.
    """
    x=design(state);theta=np.asarray(prior,np.float64).copy();l2=cfg()['value_l2']
    def objective(t):
        z=x@t;p=critic.sigmoid(z);residual=t-prior
        loss=float(np.sum(weight*(np.logaddexp(0,z)-np.asarray(y,np.float64)*z))+.5*l2*np.dot(residual,residual))
        gradient=x.T@(weight*(p-y))+l2*residual
        hessian=x.T@((weight*p*(1-p))[:,None]*x)+l2*np.eye(len(t))
        return loss,gradient,hessian
    for _ in range(cfg()['value_iterations']):
        loss,g,h=objective(theta)
        if np.max(np.abs(g))<cfg()['value_tolerance']:break
        direction=np.linalg.solve(h,g);step=1.
        for _ in range(30):
            candidate=theta-step*direction
            if objective(candidate)[0]<=loss-1e-4*step*float(g@direction):theta=candidate;break
            step*=.5
        else:raise ValueError('On-policy critic line search failed')
    else:raise ValueError('On-policy critic failed to converge')
    return theta.astype(np.float32)


def maps():
    rows=[]
    for split,count in [('train',cfg()['training_maps']),('evaluation',cfg()['evaluation_maps'])]:
        for i in range(count):
            family=i%3 if split=='train' else 3
            seed=(mapgen.seed_for('ppo-v1-'+split,cfg()['map_seed'],i)&~3)|family
            name=f"generated/ppo-v1/{split}/ppo-{split}-{i:03d}";m=mapgen.layout(seed)
            m.update(name=name,output=str(core.MAPS/(name+'.map26a')));rows.append(m)
    with tempfile.TemporaryDirectory(dir=core.ROOT/'.cambc') as tmp:
        p=Path(tmp)/'maps.json';p.write_text(json.dumps(rows))
        r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/engine.mjs'),str(mapgen.engine_path()),'maps',str(p)],capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=120)
        if r.returncode:raise ValueError(r.stderr[-2000:])
    result=dict(generator='g1; separate PPO train/evaluation seed streams',maps=json.loads(r.stdout))
    dataset.immutable(core.ROOT/'mechanics/ppo-v1-maps.json',result);return result


def plan():
    actor,_=parents();generated=maps();c=cfg()
    if c['gamma']!=1. or c['gae_lambda']!=1.:raise ValueError('First PPO run uses complete undiscounted Monte Carlo GAE')
    if c['temperature']!=1.:raise ValueError('First PPO run keeps the transferred actor logit scale')
    result=dict(schema=1,config=c,parent_actor_sha256=c['actor_sha256'],parent_critic_sha256=c['critic_sha256'],
        parent_stage4_gate_sha256=core.sha(core.ROOT/'results/stage4-v5-ready.json'),engine_sha256=core.sha(mapgen.engine_path()),
        sources=source_hashes(),maps=generated['maps'],actor_inputs=['features','candidates','mask'],actor_parameters=len(actor),
        policy_selection='fixed final iteration, no fresh evaluation checkpoint selection',
        rewards='terminal binary team win/loss only; no gold/gem shaping',
        controller='same deterministic scouting, visible-camp routing and bank-return/submission controller for learner and every control/opponent',
        sampling='exogenous seeded round stride; both micro-actions at selected rounds; complete-game returns',
        value='accepted fixed baseline/design; copied head plus zero intercept, then on-policy outcome refits',
        gate=dict(pipeline='complete clean native games, masked PPO/GAE/old-policy checks, nonzero actor update, exact parent identity and exports',
            strength='fresh paired map bootstrap 90% lower win-fraction bound > 0.5 against unchanged BC with identical controller'),
        production_wasm_tested=False,confirmation_games=0,promoted=False)
    p=root()/'plan.json'
    if p.exists():
        old=read(p);result['parent_stage4_gate_sha256']=old['parent_stage4_gate_sha256']
    dataset.immutable(p,result);save(core.ROOT/'results/stage5-plan.json',result);return result


def check():
    parents();r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/ppo-native-check.mjs'),str(mapgen.engine_path()),str(core.map_path('00collision'))],capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=60)
    if r.returncode:raise ValueError(r.stderr[-2000:])
    return save(core.ROOT/'results/stage5-native-proof.json',json.loads(r.stdout)|dict(engine_sha256=core.sha(mapgen.engine_path()),sources=source_hashes()))


def checkpoint(index):return folder()/'checkpoints'/f'{index:03d}'


def write_checkpoint(index,w,theta,optimizer,report):
    dest=checkpoint(index)
    if dest.exists():raise ValueError('Never overwrite a frozen PPO checkpoint')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        tmp=Path(tmp);export=cloning.write_export(tmp,w)
        np.savez(tmp/'training-state.npz',theta=np.asarray(theta,np.float32),adam_m=optimizer[0],adam_v=optimizer[1],adam_step=np.array(optimizer[2]))
        r=dict(iteration=index,export=export,training_state_sha256=core.sha(tmp/'training-state.npz'),report=report,
            parent_actor_sha256=cfg()['actor_sha256'],parent_critic_sha256=cfg()['critic_sha256'],plan_sha256=core.sha(root()/'plan.json'),sources=source_hashes())
        dataset.immutable(tmp/'checkpoint.json',r);tmp.rename(dest)
    return r


def load_checkpoint(index):
    dest=checkpoint(index);r=read(dest/'checkpoint.json')
    if r['sources']!=source_hashes() or r['plan_sha256']!=core.sha(root()/'plan.json'):raise ValueError('PPO checkpoint source/plan changed')
    if core.sha(dest/'weights.f32')!=r['export']['weights_sha256'] or core.sha(dest/'training-state.npz')!=r['training_state_sha256']:raise ValueError('PPO checkpoint bytes changed')
    if core.sha(dest/'weights.h')!=r['export']['header_sha256']:raise ValueError('PPO C++ weight export changed')
    w=np.fromfile(dest/'weights.f32',dtype='<f4')
    if w.shape!=(cloning.N,) or not np.isfinite(w).all() or not np.array_equal(w,np.asarray(read(dest/'weights.json'),np.float32)):raise ValueError('Invalid PPO actor export')
    with np.load(dest/'training-state.npz',allow_pickle=False) as d:
        if d['theta'].shape!=initial_value().shape or not all(np.isfinite(d[k]).all() for k in ('theta','adam_m','adam_v')):raise ValueError('Invalid PPO optimizer/critic state')
        return w,d['theta'],(d['adam_m'],d['adam_v'],int(d['adam_step']))


def episode(map_entry,weights,learner,seed,split,theta):
    source=source_hashes()
    request=dict(map=str(core.map_path(map_entry['name'])),map_sha256=map_entry['sha256'],engine_sha256=core.config()['stage1']['engine_wasm_sha256'],
        weights=[str(p) for p in weights],actor_sha256=[core.sha(p) for p in weights],backbone=str(core.ROOT/'models'/cfg()['actor_parent']/'weights.f32'),
        critic_theta_sha256=hashlib.sha256(np.asarray(theta,'<f4').tobytes()).hexdigest(),picks=cfg()['picks'],learner_team=learner,
        seed=int(seed)&0xffffffff,temperature=cfg()['temperature'],round_stride=cfg()['round_stride'],controller=cfg()['controller'],maximum_decisions=cfg()['maximum_decisions'])
    identity={k:v for k,v in request.items() if k not in ('map','weights','backbone')};identity['split']=split
    episode_id=digest(identity)[:24];dest=root()/'episodes'/episode_id;dest.mkdir(parents=True,exist_ok=True)
    if not (dest/'episode.json').exists():
        request['output']=str(dest);save(dest/'request.json',request)
        r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/ppo-rollout.mjs'),str(mapgen.engine_path()),str(dest/'request.json')],capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,env=core.ENV,timeout=cfg()['episode_timeout'])
        if r.returncode:raise ValueError('PPO episode failed; no labels admitted: '+r.stderr[-2500:])
        native=read(dest/'native.json')
        if not native['completed'] or native['rejected_actions']:raise ValueError('Unsafe PPO rollout')
        if native['engine_sha256']!=request['engine_sha256'] or native['map_sha256']!=request['map_sha256'] or native['actor_sha256']!=request['actor_sha256']:raise ValueError('Wrong PPO runtime/actor capture')
        if source!=source_hashes():raise ValueError('PPO source changed during capture')
        frames=[]
        with gzip.open(dest/'frames.jsonl.gz','rt',encoding='utf-8') as stream:
            for line in stream:frames.append(json.loads(line))
        arrays={key:np.asarray([f[key] for f in frames],dtype) for key,dtype in
            [('features',np.float32),('candidates',np.float32),('mask',bool),('state',np.float32),('team',np.uint8),('actor',np.uint32),('round',np.uint32),
             ('action',np.int16),('old_logp',np.float64),('old_logits',np.float32),('learner',bool),('policy_action',bool)]}
        arrays['outcome']=np.asarray([critic.terminal_value(native['terminal'],int(t)) for t in arrays['team']],np.float32)
        arrays['old_value']=value(theta,arrays['state']).astype(np.float32)
        np.savez_compressed(dest/'rollout.npz',**arrays)
        meta=dict(episode_id=episode_id,split=split,map=map_entry['name'],map_sha256=map_entry['sha256'],identity=identity,rows=len(frames),
            path=(dest/'rollout.npz').relative_to(root()).as_posix(),sha256=core.sha(dest/'rollout.npz'),native=native,
            sources=source_hashes(),critic_theta=np.asarray(theta).tolist())
        dataset.immutable(dest/'episode.json',meta)
    meta=read(dest/'episode.json')
    if meta['identity']!=identity or meta['sources']!=source_hashes():raise ValueError('Stale PPO rollout source/identity')
    if core.sha(dest/'rollout.npz')!=meta['sha256']:raise ValueError('PPO shard changed')
    return meta


def collect(jobs,manifest):
    with ThreadPoolExecutor(cfg()['jobs']) as pool:
        episodes=[]
        for e in pool.map(lambda kw:episode(**kw),jobs):
            episodes.append(e);print(f"PPO {manifest} {len(episodes)}/{len(jobs)}",flush=True)
    result=dict(episodes=episodes,sources=source_hashes());dataset.immutable(root()/(manifest+'.json'),result);return episodes


def load(episodes):
    parts=[]
    for i,e in enumerate(episodes):
        if core.sha(root()/e['path'])!=e['sha256']:raise ValueError('PPO data hash mismatch')
        with np.load(root()/e['path'],allow_pickle=False) as d:part={k:d[k] for k in d.files}
        part['episode']=np.full(e['rows'],i,np.int32);parts.append(part)
    data={k:np.concatenate([p[k] for p in parts]) for k in parts[0]}
    data['weight']=critic.group_weights(data['episode'],data['team'])
    return data


def training_jobs(iteration,theta,warmup=False):
    planned=plan();maps=[e for e in planned['maps'] if '/train/' in e['name']];jobs=[]
    parent=core.ROOT/'models'/cfg()['actor_parent']/'weights.f32';current=parent if warmup else checkpoint(iteration-1)/'weights.f32'
    for j in range(cfg()['maps_per_iteration']):
        m=maps[((max(0,iteration-1)*cfg()['maps_per_iteration'])+j)%len(maps)];rng=np.random.default_rng(cfg()['seed']+iteration*100+j)
        choice=rng.choice(['current','bc','history'],p=cfg()['opponent_probabilities'])
        opponent=current if choice=='current' else parent
        if choice=='history' and iteration>2:opponent=checkpoint(int(rng.integers(1,iteration-1)))/'weights.f32'
        for seat in (0,1):
            weights=[opponent,opponent];weights[seat]=current
            jobs.append(dict(map_entry=m,weights=weights,learner=seat,seed=cfg()['seed']+iteration*10000+j*71,split='warmup' if warmup else 'train',theta=theta))
    return jobs


def warmup():
    w,_=parents();theta=initial_value();episodes=collect(training_jobs(0,theta,True),'warmup');data=load(episodes)
    fold=np.asarray([int(episodes[i]['map'].rsplit('-',1)[1])%3 for i in data['episode']]);p=np.empty(len(fold))
    for family in (0,1,2):
        train=fold!=family;dev=~train
        weight=critic.group_weights(data['episode'][train],data['team'][train])
        fitted=value_fit(data['state'][train],(data['outcome'][train]+1)/2,weight,theta)
        p[dev]=(value(fitted,data['state'][dev])+1)/2
    y=(data['outcome']+1)/2;initial=(data['old_value']+1)/2
    result=dict(games=len(episodes),states=len(y),cross_validation='leave training family out, complete maps and both seats grouped',
        initial=critic.metrics(y,initial,data['weight']),on_policy_oof=critic.metrics(y,p,data['weight']),actor_updates=0,
        note='GAE lambda=gamma=1 uses complete Monte Carlo returns, avoiding bias from an imperfect critic')
    fitted=value_fit(data['state'],y,data['weight'],theta);zero=np.zeros_like(w,np.float64)
    write_checkpoint(0,w,fitted,(zero,zero.copy(),0),result);save(core.ROOT/'results/stage5-warmup.json',result)
    return result


def train():
    planned=plan();check();started=time.perf_counter();folder().mkdir(parents=True,exist_ok=True)
    if (folder()/'training.json').exists():
        r=read(folder()/'training.json');load_checkpoint(cfg()['iterations'])
        if r['sources']!=source_hashes() or not r['training_complete']:raise ValueError('Changed completed PPO model')
        return r
    if not (checkpoint(0)/'checkpoint.json').exists():warmup()
    history=[]
    for iteration in range(1,cfg()['iterations']+1):
        if (checkpoint(iteration)/'checkpoint.json').exists():
            load_checkpoint(iteration);history.append(read(checkpoint(iteration)/'checkpoint.json')['report']);continue
        w,theta,optimizer=load_checkpoint(iteration-1)
        episodes=collect(training_jobs(iteration,theta),f'train-{iteration:03d}');data=load(episodes)
        advantage,_=ppo_math.advantages(data['episode'],data['team'],data['actor'],data['round'],data['old_value'],data['outcome'],cfg()['gamma'],cfg()['gae_lambda'])
        take=data['learner']&data['policy_action']
        if take.sum()<cfg()['minimum_policy_samples']:raise ValueError('Too few real on-policy decisions')
        actor={k:data[k][take] for k in ('features','candidates','mask','action','old_logits','old_logp')}
        scores=cloning.forward(w,actor['features'],actor['candidates'],exact=True)[0]
        _,old=ppo_math.distribution(scores,actor['mask']);error=float(np.max(np.abs(old[np.arange(take.sum()),actor['action']]-actor['old_logp'])))
        if error>cfg()['old_logp_tolerance']:raise ValueError('Rollout log probabilities do not match the frozen old policy')
        actor['anchor_logits']=cloning.forward(parents()[0],actor['features'],actor['candidates'],exact=True)[0]
        new,optimizer,metrics=ppo_math.update(w,actor,advantage[take],cfg(),np.random.default_rng(cfg()['seed']+iteration),optimizer)
        updated_value=value_fit(data['state'],(data['outcome']+1)/2,data['weight'],theta)
        learner_win=np.mean([critic.terminal_value(e['native']['terminal'],e['native']['learner_team'])>0 for e in episodes])
        row=dict(iteration=iteration,games=len(episodes),sampled_states=len(take),policy_samples=int(take.sum()),old_logp_max_error=error,
            actor_change_norm=float(np.linalg.norm(new-w)),distance_from_bc=float(np.linalg.norm(new-parents()[0])),critic_change_norm=float(np.linalg.norm(updated_value-theta)),
            learner_training_win_fraction=float(learner_win),
            critic_old_brier=critic.metrics((data['outcome']+1)/2,(data['old_value']+1)/2,data['weight'])['brier'],
            critic_refit_training_brier=critic.metrics((data['outcome']+1)/2,(value(updated_value,data['state'])+1)/2,data['weight'])['brier'],
            training_manifest_sha256=core.sha(root()/f'train-{iteration:03d}.json'),ppo=metrics)
        write_checkpoint(iteration,new,updated_value,optimizer,row);history.append(row);print(json.dumps(row),flush=True)
    final=checkpoint(cfg()['iterations']);w,theta,_=load_checkpoint(cfg()['iterations'])
    result=dict(training_complete=True,model=cfg()['model'],iterations=cfg()['iterations'],history=history,
        actor_sha256=core.sha(final/'weights.f32'),checkpoint=str(final.relative_to(core.ROOT)),actor_change_norm=float(np.linalg.norm(w-parents()[0])),
        parent_actor_sha256=cfg()['actor_sha256'],parent_critic_sha256=cfg()['critic_sha256'],
        plan_sha256=core.sha(root()/'plan.json'),sources=source_hashes(),elapsed_seconds=time.perf_counter()-started,
        evaluation_model_selections=0,production_wasm_tested=False,confirmation_games=0,promoted=False)
    dataset.immutable(folder()/'training.json',result);save(core.ROOT/'results/stage5-training.json',result);return result


def evaluate():
    planned=plan();training=read(folder()/'training.json');w,theta,_=load_checkpoint(cfg()['iterations'])
    if not training['training_complete'] or training['sources']!=source_hashes():raise ValueError('Incomplete/stale PPO model')
    current=checkpoint(cfg()['iterations'])/'weights.f32';parent=core.ROOT/'models'/cfg()['actor_parent']/'weights.f32';jobs=[]
    for i,m in enumerate(e for e in planned['maps'] if '/evaluation/' in e['name']):
        for repeat in range(cfg()['evaluation_seeds']):
            for seat in (0,1):
                weights=[parent,parent];weights[seat]=current
                jobs.append(dict(map_entry=m,weights=weights,learner=seat,seed=cfg()['evaluation_seed']+i*73+repeat*10000,split='evaluation',theta=theta))
    episodes=collect(jobs,'evaluation');scores=[];by_map={}
    for e in episodes:
        win=float(critic.terminal_value(e['native']['terminal'],e['native']['learner_team'])>0);scores.append(win);by_map.setdefault(e['map'],[]).append(win)
    map_scores=np.asarray([np.mean(v) for v in by_map.values()]);rng=np.random.default_rng(cfg()['evaluation_seed'])
    draws=rng.integers(len(map_scores),size=(cfg()['bootstrap_samples'],len(map_scores)))
    interval=np.quantile(map_scores[draws].mean(axis=1),[.05,.95]);data=load(episodes);y=(data['outcome']+1)/2
    predictions=(value(theta,data['state'])+1)/2
    result=dict(model=cfg()['model'],games=len(scores),maps=len(map_scores),win_fraction=float(np.mean(scores)),map_win_fractions=dict(zip(by_map,map_scores.tolist())),
        bootstrap_90=interval.tolist(),strength_gate_passed=bool(interval[0]>.5),
        critic=critic.metrics(y,predictions,data['weight']),actor_sha256=training['actor_sha256'],
        evaluation_manifest_sha256=core.sha(root()/'evaluation.json'),evaluation_model_selections=0,
        comparison='stochastic PPO vs unchanged BC; same banking controller, draft, temperature and decision cap; paired seats/seeds',
        native_rules_only=True,production_wasm_tested=False,confirmation_games=0,promoted=False)
    dataset.immutable(folder()/'evaluation.json',result);save(core.ROOT/'results/stage5-evaluation.json',result);return result


def actor_path(digest_value):
    candidates=[core.ROOT/'models'/cfg()['actor_parent']/'weights.f32']+[checkpoint(i)/'weights.f32' for i in range(cfg()['iterations']+1)]
    for p in candidates:
        if p.exists() and core.sha(p)==digest_value:return p
    raise ValueError('Unknown frozen rollout actor')


def audit_episode(e,native_terminal=True):
    """All old probabilities/values, plus causal native feature probes and terminal replay."""
    from . import replay
    dest=(root()/e['path']).parent;n=e['native']
    if e['sources']!=source_hashes() or core.sha(dest/'rollout.npz')!=e['sha256']:raise ValueError('PPO provenance changed')
    for name,key in [('game.repl26a','replay_sha256'),('frames.jsonl.gz','frames_sha256'),('probes.json.gz','probes_sha256')]:
        if core.sha(dest/name)!=n[key]:raise ValueError('PPO native capture changed')
    if core.sha(core.map_path(e['map']))!=e['map_sha256'] or not n['completed'] or n['rejected_actions']:raise ValueError('Unsafe PPO source game')
    actions=replay.decode((dest/'game.repl26a').read_bytes(),core.map_path(e['map']).read_bytes())
    if not actions:raise ValueError('Empty native replay')
    if native_terminal:
        p=dest/'audit-request.json';save(p,dict(replay=str(dest/'game.repl26a')))
        r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/ppo-replay-check.mjs'),str(mapgen.engine_path()),str(p)],capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=60)
        if r.returncode:raise ValueError('Native PPO terminal audit failed: '+r.stderr[-1000:])
        checked=json.loads(r.stdout)
        if checked['terminal']!=n['terminal'] or checked['engine_sha256']!=n['engine_sha256'] or checked['inputs']!=len(actions):raise ValueError('PPO terminal label differs from native replay')
    with np.load(dest/'rollout.npz',allow_pickle=False) as d:
        if d['features'].shape!=(e['rows'],24) or d['candidates'].shape!=(e['rows'],16,12) or d['state'].shape!=(e['rows'],74):raise ValueError('Wrong PPO tensor dimensions')
        if not all(np.isfinite(d[k]).all() for k in ('features','candidates','state','old_value','old_logp','old_logits')):raise ValueError('Nonfinite PPO tensors')
        outcomes=np.array([critic.terminal_value(n['terminal'],int(t)) for t in d['team']])
        if not np.array_equal(outcomes,d['outcome']):raise ValueError('PPO binary labels changed')
        if not np.array_equal(d['learner'],d['team']==n['learner_team']):raise ValueError('Wrong PPO learning team')
        theta=np.asarray(e['critic_theta'],np.float32)
        if not np.allclose(value(theta,d['state']),d['old_value'],atol=1e-7,rtol=0):raise ValueError('PPO old values changed')
        maximum=0.
        for team in (0,1):
            take=(d['team']==team)&d['policy_action'];w=np.fromfile(actor_path(n['actor_sha256'][team]),dtype='<f4')
            if take.any():
                scores=cloning.forward(w,d['features'][take],d['candidates'][take],exact=True)[0]
                if not np.allclose(scores/n['temperature'],d['old_logits'][take],atol=1e-6,rtol=0):raise ValueError('Rollout logits differ from exact actor')
                _,lp=ppo_math.distribution(scores/n['temperature'],d['mask'][take]);a=d['action'][take]
                if np.any(a<0) or not d['mask'][take][np.arange(len(a)),a].all():raise ValueError('PPO recorded a masked action')
                maximum=max(maximum,float(np.max(np.abs(lp[np.arange(len(a)),a]-d['old_logp'][take]))))
        if maximum>cfg()['old_logp_tolerance']:raise ValueError('PPO old log probabilities changed')
        with gzip.open(dest/'probes.json.gz','rt',encoding='utf-8') as stream:probes=json.load(stream)
        feature_error=0.
        for row in probes['probes']:
            j=row['row'];o=row['observation'];encoded=policy.encode(o,probes['terrain'])
            if not np.array_equal(np.asarray(encoded['features'],np.float32),d['features'][j]) or not np.array_equal(np.asarray(encoded['candidates'],np.float32),d['candidates'][j]) or not np.array_equal(encoded['mask'],d['mask'][j]):raise ValueError('Native actor feature parity failed')
            state=wealth_state.make_state(o,row['units'],probes['terrain'],parents()[0])
            feature_error=max(feature_error,float(np.max(np.abs(state-d['state'][j]))))
            if feature_error>cfg()['feature_tolerance']:raise ValueError('Native privileged critic feature parity failed')
    return dict(episode=e['episode_id'],rows=e['rows'],probes=len(probes['probes']),old_logp_max_error=maximum,critic_feature_max_error=feature_error)


def audit():
    plan();manifests=[root()/'warmup.json']+[root()/f'train-{i:03d}.json' for i in range(1,cfg()['iterations']+1)]+[root()/'evaluation.json']
    episodes=[e for p in manifests for e in read(p)['episodes']]
    with ThreadPoolExecutor(cfg()['jobs']) as pool:
        reports=[]
        for r in pool.map(audit_episode,episodes):reports.append(r);print(f"PPO audit {len(reports)}/{len(episodes)}",flush=True)
    result=dict(passed=True,games=len(reports),states=sum(r['rows'] for r in reports),native_probes=sum(r['probes'] for r in reports),
        old_logp_max_error=max(r['old_logp_max_error'] for r in reports),critic_feature_max_error=max(r['critic_feature_max_error'] for r in reports),
        manifest_sha256={p.name:core.sha(p) for p in manifests},sources=source_hashes(),all_native_terminals_checked=True)
    return save(core.ROOT/'results/stage5-audit.json',result)


def ready():
    accepted.ready();planned=plan();training=read(folder()/'training.json');evaluation=read(folder()/'evaluation.json')
    checked=read(core.ROOT/'results/stage5-audit.json');proof=read(core.ROOT/'results/stage5-native-proof.json')
    for r in (training,checked,proof):
        if r['sources']!=source_hashes():raise ValueError('Stale PPO source certificate')
    for name,digest_value in checked['manifest_sha256'].items():
        if core.sha(root()/name)!=digest_value:raise ValueError('PPO audited manifest changed')
    if not checked['passed'] or not proof['passed']:raise ValueError('PPO audit/protocol check failed')
    w,theta,_=load_checkpoint(cfg()['iterations']);initial=load_checkpoint(0)[0]
    if not np.array_equal(initial,parents()[0]) or np.linalg.norm(w-initial)<=1e-6:raise ValueError('PPO actor was not initialized exactly or did not update')
    if core.sha(checkpoint(cfg()['iterations'])/'weights.f32')!=training['actor_sha256'] or evaluation['actor_sha256']!=training['actor_sha256']:raise ValueError('PPO final actor identity changed')
    if evaluation['evaluation_manifest_sha256']!=core.sha(root()/'evaluation.json'):raise ValueError('PPO evaluation changed')
    by_map={}
    for e in read(root()/'evaluation.json')['episodes']:
        by_map.setdefault(e['map'],[]).append(float(critic.terminal_value(e['native']['terminal'],e['native']['learner_team'])>0))
    map_scores=np.array([np.mean(v) for v in by_map.values()]);rng=np.random.default_rng(cfg()['evaluation_seed'])
    draws=rng.integers(len(map_scores),size=(cfg()['bootstrap_samples'],len(map_scores)))
    interval=np.quantile(map_scores[draws].mean(axis=1),[.05,.95])
    if not np.allclose(interval,evaluation['bootstrap_90'],atol=1e-12,rtol=0) or abs(map_scores.mean()-evaluation['win_fraction'])>1e-12:raise ValueError('PPO held-out scores do not reproduce')
    pipeline=all(row['ppo']['kl']<=cfg()['maximum_kl']+1e-6 and row['old_logp_max_error']<=cfg()['old_logp_tolerance'] for row in training['history'])
    strength=bool(interval[0]>.5)
    if strength!=evaluation['strength_gate_passed']:raise ValueError('PPO strength gate changed')
    passed=bool(pipeline and strength)
    result=dict(passed=passed,pipeline_checks_passed=bool(pipeline),strength_gate_passed=bool(strength),stage=5,next_stage=6 if passed else 5,
        model=cfg()['model'],actor_sha256=training['actor_sha256'],parent_actor_sha256=cfg()['actor_sha256'],parent_critic_sha256=cfg()['critic_sha256'],
        actor_change_norm=training['actor_change_norm'],evaluation={k:evaluation[k] for k in ('games','maps','win_fraction','bootstrap_90','comparison')},
        audit={k:checked[k] for k in ('games','states','native_probes','old_logp_max_error','critic_feature_max_error')},
        warmup=read(core.ROOT/'results/stage5-warmup.json'),sources=source_hashes(),production_wasm_tested=False,confirmation_games=0,promoted=False)
    return save(core.ROOT/'results/stage5-ready.json',result)

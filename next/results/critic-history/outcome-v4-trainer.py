"""Stage 4 v4: calibrated score offset and monotone current-team advantages.

Negative strength/health coefficients in v3 were policy/draft shortcuts. This
version constrains advantage coefficients nonnegative and selects banking curves
and calibration on training-family cross-validation only. Actor stays frozen.
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
from . import core,critic,central_critic as central,dataset,mapgen,stats,stage1


def root():return core.ROOT/'datasets'/core.config()['stage4']['dataset']
def model_root():return core.ROOT/'models'/core.config()['stage4']['model']
def training_root():return core.ROOT/'datasets'/core.config()['stage4']['central_training_dataset']
def save(name,value):return central.save(name,value)
def modes():return core.config()['stage4']['monotone_modes']


def features(state,mode):
    margin=state[:,0];elapsed=state[:,1];a=state[:,26];b=state[:,27]
    signed_root=np.sign(margin)*np.sqrt(np.abs(margin))
    banking=np.stack((margin*(a+b),margin*np.abs(margin),margin*np.abs(margin)*elapsed,
        margin/(1.2-np.maximum(a,b)),signed_root*elapsed,signed_root*elapsed*elapsed,margin*elapsed*elapsed),axis=1)
    if mode=='temperature':return np.empty((len(state),0),np.float32)
    if mode=='banks':return banking.astype(np.float32)
    if mode=='team':return state[:,44:68].astype(np.float32)
    if mode=='team_banks':return np.c_[state[:,44:68],banking].astype(np.float32)
    raise ValueError('Unknown monotone critic features')


def box_objective(coef,design,y,weight,l2):
    z=design@coef;p=critic.sigmoid(z);prior=np.zeros_like(coef);prior[0]=1
    residual=coef-prior
    loss=float(np.sum(weight*(np.logaddexp(0,z)-np.asarray(y,np.float64)*z))+.5*l2*np.dot(residual,residual))
    gradient=design.T@(weight*(p-y))+l2*residual
    hessian=design.T@((weight*p*(1-p))[:,None]*design)+l2*np.eye(len(coef))
    return loss,gradient,hessian


def fit(state,y,weight,base,mode,l2,cfg):
    x=features(state,mode).astype(np.float64);scale=np.sqrt(np.sum(weight[:,None]*x*x,axis=0));scale=np.where(scale<1e-6,1.,scale)
    design=np.c_[central.base_logits(base,state).astype(np.float64),x/scale]
    coef=np.zeros(design.shape[1]);coef[0]=1.;lower=np.zeros_like(coef);lower[0]=cfg['temperature_bounds'][0]
    upper=np.full_like(coef,np.inf);upper[0]=cfg['temperature_bounds'][1]
    for iteration in range(cfg['box_iterations']):
        loss,gradient,hessian=box_objective(coef,design,y,weight,l2)
        active=((coef<=lower+1e-10)&(gradient>0))|((coef>=upper-1e-10)&(gradient<0))
        projected=gradient.copy();projected[active]=0
        if np.max(np.abs(projected))<cfg['box_tolerance']:break
        free=~active;direction=np.zeros_like(coef)
        direction[free]=np.linalg.solve(hessian[np.ix_(free,free)],gradient[free])
        accepted=False
        for direction in (direction,projected/np.diag(hessian)):
            step=1.
            for _ in range(cfg['line_search_steps']):
                candidate=np.clip(coef-step*direction,lower,upper)
                movement=coef-candidate;descent=float(np.dot(gradient,movement))
                if descent>0 and box_objective(candidate,design,y,weight,l2)[0]<=loss-1e-4*descent:
                    coef=candidate;accepted=True;break
                step*=.5
            if accepted:break
        if not accepted:
            if np.max(np.abs(projected))<cfg['box_tolerance']*10:break
            raise ValueError('Constrained critic line search failed')
    else:raise ValueError('Constrained critic did not converge')
    return dict(coef=coef.astype(np.float32),scale=scale.astype(np.float32),mode=mode,l2=l2,iterations=iteration+1)


def logits(head,state,base):
    return head['coef'][0]*central.base_logits(base,state)+(features(state,head['mode'])/head['scale'])@head['coef'][1:]


def predict(model,state):
    baseline=central.base_logits(model['baseline'],state);full=logits(model['head'],state,model['baseline'])
    return critic.sigmoid(baseline+model['shrinkage']*(full-baseline))


def read_data(folder,manifest_name,split):
    manifest=json.loads((folder/manifest_name).read_text());arrays={k:[] for k in ('state','win','team','round')};ids=[];maps=[];family=[]
    for e in manifest['episodes']:
        if e['split']!=split:continue
        p=folder/e['path']
        if core.sha(p)!=e['sha256']:raise ValueError('Monotone source shard changed')
        with np.load(p,allow_pickle=False) as d:
            if d['state'].shape!=(e['rows'],68) or not np.isfinite(d['state']).all():raise ValueError('Invalid monotone state')
            target=np.array([(critic.terminal_value(e['terminal'],int(t))+1)/2 for t in d['team']],np.uint8)
            if not np.array_equal(target,d['win']):raise ValueError('Monotone outcome labels changed')
            for k in arrays:arrays[k].append(d[k])
        ids.extend([e['episode_id']]*e['rows']);maps.extend([e['map']]*e['rows']);family.extend([e['family']]*e['rows'])
    if not ids:raise ValueError('Empty monotone partition')
    data={k:np.concatenate(v) for k,v in arrays.items()};data.update(episode=np.asarray(ids),map=np.asarray(maps),family=np.asarray(family))
    data['weight']=critic.group_weights(data['episode'],data['team']);return data


def select(data,cfg):
    if set(data['family'])!={0,1,2}:raise ValueError('Only training families may select critic')
    folds=[(critic.subset(data,data['family']!=f),critic.subset(data,data['family']==f),data['family']==f) for f in (0,1,2)]
    base_trials=[]
    for l2 in cfg['l2_grid']:
        p=np.zeros(len(data['win']))
        for train,dev,index in folds:
            base=critic.fit(train['state'][:,:4],train['win'],train['weight'],l2,cfg);p[index]=critic.predict(base,dev['state'])
        base_trials.append(dict(l2=l2,metrics=critic.metrics(data['win'],p,data['weight'],cfg['calibration_bins'])))
    chosen_base=min(base_trials,key=lambda x:x['metrics']['log_loss']);cache=[]
    for train,dev,index in folds:
        base=critic.fit(train['state'][:,:4],train['win'],train['weight'],chosen_base['l2'],cfg)
        cache.append((train,dev,index,base,central.base_logits(base,dev['state'])))
    trials=[]
    for mode in cfg['monotone_modes']:
        for l2 in cfg['residual_l2_grid']:
            components=[]
            for train,dev,index,base,base_z in cache:
                head=fit(train['state'],train['win'],train['weight'],base,mode,l2,cfg)
                components.append((index,base_z,logits(head,dev['state'],base)))
            for shrinkage in cfg['residual_shrinkage']:
                p=np.zeros(len(data['win']))
                for index,b,z in components:p[index]=critic.sigmoid(b+shrinkage*(z-b))
                measured=critic.metrics(data['win'],p,data['weight'],cfg['calibration_bins'])
                trials.append(dict(mode=mode,l2=l2,shrinkage=shrinkage,metrics=measured))
            print(f"Monotone CV {mode} L2={l2}",flush=True)
    eligible=[t for t in trials if t['metrics']['brier']+cfg['minimum_cv_brier_gain']<chosen_base['metrics']['brier'] and t['metrics']['log_loss']<chosen_base['metrics']['log_loss']]
    chosen=min(eligible,key=lambda t:t['metrics']['log_loss']) if eligible else min(trials,key=lambda t:t['metrics']['log_loss'])
    base=critic.fit(data['state'][:,:4],data['win'],data['weight'],chosen_base['l2'],cfg)
    head=fit(data['state'],data['win'],data['weight'],base,chosen['mode'],chosen['l2'],cfg)
    return dict(baseline=base,head=head,shrinkage=chosen['shrinkage']),dict(baseline_trials=base_trials,trials=trials,
        selected_baseline=chosen_base,selected_critic=chosen,internal_acceptance_passed=bool(eligible),selection='training-only leave-family-out CV; no outer model selection')


def maps():
    cfg=core.config()['stage4'];rows=[]
    for i,name in enumerate(cfg['fresh_validation_maps']):
        seed=(mapgen.seed_for('critic-v4-validation',cfg['validation_map_seed'],i)&~3)|3
        m=mapgen.layout(seed);m.update(name=name,output=str(core.MAPS/(name+'.map26a')));rows.append(m)
    with tempfile.TemporaryDirectory(dir=core.ROOT/'.cambc') as tmp:
        p=Path(tmp)/'maps.json';p.write_text(json.dumps(rows))
        r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/engine.mjs'),str(mapgen.engine_path()),'maps',str(p)],capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=120)
        if r.returncode:raise ValueError(r.stderr[-2000:])
    result=dict(generator='g1 geometry, independent critic-v4 seed stream, family 3',seed=cfg['validation_map_seed'],maps=json.loads(r.stdout),role='critic screening acceptance, not final confirmation')
    dataset.immutable(core.ROOT/'mechanics/critic-v4-maps.json',result);return result


def plan():
    cfg=core.config()['stage4'];critic.parent();maps();profile=core.runtime_identity();episodes=[]
    train=json.loads((training_root()/'training-manifest.json').read_text())
    for name in cfg['fresh_validation_maps']:
        for a,b in cfg['fresh_validation_pairs']:
            for x,y in ([(a,b)] if a==b else [(a,b),(b,a)]):
                versions=[core.version(n) for n in (x,y)];e=dict(split='fresh_validation',map=name,map_sha256=core.sha(core.map_path(name)),family=3,names=[x,y],
                    wasm_sha256=[v.meta['wasm_sha256'] for v in versions],runtime=profile,lineages=[core.config()['stage2']['lineages'][n] for n in (x,y)])
                e['episode_id']=dataset.digest(e)[:24];episodes.append(e)
    if {l for e in train['episodes'] for l in e['lineages']}&{l for e in episodes for l in e['lineages']}:raise ValueError('Outer lineage leakage')
    value=dict(schema=4,config=cfg,training_manifest_sha256=core.sha(training_root()/'training-manifest.json'),fresh_validation_episodes=episodes,
        parent_weights_sha256=cfg['parent_sha256'],runtime=profile,acceptance='unchanged strict Brier AND log loss superiority to constant AND score/time baseline',
        actor_updated=False,ppo_started=False,confirmation_games=0)
    dataset.immutable(root()/'plan.json',value);save('stage4-v4-plan.json',value);return value


def export(path,model):
    b=model['baseline'];h=model['head']
    np.savez(path,base_coef=b['coef'],base_mean=b['mean'],base_scale=b['scale'],head_coef=h['coef'],head_scale=h['scale'],mode=np.array(h['mode']),shrinkage=np.array(model['shrinkage'],np.float32),backbone=critic.parent())


def load_model():
    with np.load(model_root()/'critic.npz',allow_pickle=False) as d:
        model=dict(baseline=dict(coef=d['base_coef'],mean=d['base_mean'],scale=d['base_scale']),head=dict(coef=d['head_coef'],scale=d['head_scale'],mode=str(d['mode'])),shrinkage=float(d['shrinkage']))
        if not np.array_equal(d['backbone'],critic.parent()):raise ValueError('BC backbone changed')
    h=model['head'];cfg=core.config()['stage4']
    if h['mode'] not in cfg['monotone_modes'] or np.any(h['coef'][1:]<0) or not cfg['temperature_bounds'][0]<=h['coef'][0]<=cfg['temperature_bounds'][1]:raise ValueError('Monotonicity constraint failed')
    if np.any(h['scale']<=0) or not np.isfinite(h['coef']).all():raise ValueError('Invalid monotone export')
    return model


def train():
    planned=plan();cfg=core.config()['stage4'];folder=model_root()
    if folder.exists():raise ValueError('Preserve existing critic; use a new model name')
    data=read_data(training_root(),'training-manifest.json','train');started=time.perf_counter();model,selection=select(data,cfg)
    save('stage4-v4-development.json',selection)
    if not selection['internal_acceptance_passed']:raise ValueError('Monotone CV did not clear internal gate; fresh test remains sealed')
    folder.mkdir(parents=True);export(folder/'critic.npz',model);shutil.copyfile(core.ROOT/'models'/cfg['parent']/'weights.f32',folder/'actor.f32')
    frozen=dict(model=cfg['model'],model_sha256=core.sha(folder/'critic.npz'),actor_sha256=core.sha(folder/'actor.f32'),plan_sha256=core.sha(root()/'plan.json'),
        training_manifest_sha256=planned['training_manifest_sha256'],source_sha256=central.normalized_sha(Path(__file__)),helper_sources={n:central.normalized_sha(core.ROOT/n) for n in ('lab/central_critic.py','lab/critic.py')},
        selection=selection,training_games=len(np.unique(data['episode'])),training_maps=len(np.unique(data['map'])),training_states=len(data['win']),
        trainable_parameters=len(model['baseline']['coef'])+len(model['head']['coef']),elapsed_seconds=time.perf_counter()-started,
        parent_weights_sha256=cfg['parent_sha256'],actor_unchanged=True,outer_model_selections=0,ppo_started=False,confirmation_games=0)
    dataset.immutable(folder/'frozen.json',frozen);dataset.immutable(folder/'plan.json',planned);save('stage4-v4-frozen.json',frozen)
    return {k:frozen[k] for k in ('model','training_games','training_states','trainable_parameters','elapsed_seconds','model_sha256')}


def frozen():
    r=json.loads((model_root()/'frozen.json').read_text())
    if r['source_sha256']!=central.normalized_sha(Path(__file__)):raise ValueError('Monotone training source changed')
    for name,digest in r['helper_sources'].items():
        if central.normalized_sha(core.ROOT/name)!=digest:raise ValueError('Monotone helper source changed')
    for name,key in (('critic.npz','model_sha256'),('actor.f32','actor_sha256')):
        if core.sha(model_root()/name)!=r[key]:raise ValueError('Monotone frozen bytes changed')
    if core.sha(root()/'plan.json')!=r['plan_sha256'] or core.sha(training_root()/'training-manifest.json')!=r['training_manifest_sha256']:raise ValueError('Monotone training inputs changed')
    return r


def score(model,data):
    cfg=core.config()['stage4'];result={}
    predictions={'constant':np.full(len(data['win']),.5),'score_time':critic.predict(model['baseline'],data['state']),'critic':predict(model,data['state'])}
    a,b=cfg['phase_boundaries']
    for name,p in predictions.items():
        s=critic.metrics(data['win'],p,data['weight'],cfg['calibration_bins']);s.update(games=len(np.unique(data['episode'])),maps=len(np.unique(data['map'])),phases={})
        for phase,index in [('early',data['round']<=a),('middle',(data['round']>a)&(data['round']<=b)),('late',data['round']>b)]:
            if index.any():
                d=critic.subset(data,index);s['phases'][phase]=critic.metrics(d['win'],p[index],d['weight'],cfg['calibration_bins'])
        result[name]=s
    return result


def bootstrap(data,model):
    cfg=core.config()['stage4'];names=np.unique(data['map']);differences=[]
    for name in names:
        d=critic.subset(data,data['map']==name);s=score(model,d);differences.append(s['critic']['brier']-s['score_time']['brier'])
    rng=np.random.default_rng(cfg['seed']);draws=rng.integers(0,len(names),(cfg['bootstrap_samples'],len(names)))
    interval=np.quantile(np.asarray(differences)[draws].mean(axis=1),[.05,.95])
    return dict(unit='whole map with all seats/pairings retained',maps=len(names),mean_difference=float(np.mean(differences)),
        paired_brier_difference_by_map=dict(zip(names.tolist(),differences)),interval_90=interval.tolist(),superiority_supported=bool(interval[1]<0))


def evaluate():
    fixed=frozen();planned=plan();model=load_model();episodes=[]
    with ThreadPoolExecutor(core.config()['stage4']['jobs']) as pool:
        source=list(pool.map(central.run_episode,planned['fresh_validation_episodes']))
    with ThreadPoolExecutor(core.config()['stage4']['jobs']) as pool:
        for e in pool.map(lambda pair:central.extract(*pair),source):
            episodes.append(e);print(f"Monotone acceptance {len(episodes)}/{len(source)}",flush=True)
    dataset.immutable(root()/'evaluation-manifest.json',dict(episodes=episodes,model_sha256=fixed['model_sha256'],plan_sha256=fixed['plan_sha256']))
    data=read_data(root(),'evaluation-manifest.json','fresh_validation');measured=score(model,data);passed=central.acceptance(measured)
    r=dict(model=fixed['model'],passed=bool(passed),predictive_acceptance_passed=bool(passed),scores=measured,uncertainty=bootstrap(data,model),
        model_sha256=fixed['model_sha256'],evaluation_manifest_sha256=core.sha(root()/'evaluation-manifest.json'),
        outer_model_selections=0,actor_unchanged=True,ppo_started=False,confirmation_games=0,promoted=False)
    dataset.immutable(model_root()/'evaluation.json',r);save('stage4-v4-evaluation.json',r)
    return dict(passed=bool(passed),scores={name:{k:s[k] for k in ('brier','log_loss','accuracy','expected_calibration_error')} for name,s in measured.items()},uncertainty=r['uncertainty'])


def audit():
    fixed=frozen();backbone=critic.parent();games=0;rows=0
    for folder,manifest_name in ((training_root(),'training-manifest.json'),(root(),'evaluation-manifest.json')):
        manifest=json.loads((folder/manifest_name).read_text())
        for e in manifest['episodes']:
            p=folder/e['path'];stored=p.parent/'states.jsonl.gz';source=core.ROOT/e['source_dir']
            if core.sha(p)!=e['sha256'] or core.sha(stored)!=e['states_sha256']:raise ValueError('Monotone state provenance changed')
            blob=dataset.raw_bytes(max(source.glob('*.repl26a'),key=lambda p:p.stat().st_mtime))
            if hashlib.sha256(blob).hexdigest()!=e['source_replay_sha256']:raise ValueError('Native replay changed')
            raw=json.loads((source/'stats.json').read_text());compact=stats.summarize(raw)
            if raw['match']['engineBuildHash']!=e['runtime']['engine_build_hash'] or raw['match']['mapHash']!=e['map_sha256']:raise ValueError('Critic runtime/map changed')
            if any(t['faults'] or t['fuel_exhausted'] for t in compact['teams'].values()):raise ValueError('Faulty game supplies critic labels')
            terminal=dict(outcome=compact['outcome'],round=compact['rounds'],banks=[compact['teams'][t]['gems'] for t in ('teamA','teamB')])
            if terminal!=e['terminal']:raise ValueError('Critic terminal differs from release runner')
            with np.load(p,allow_pickle=False) as d,gzip.open(stored,'rt',encoding='utf-8') as stream:
                index=0
                for line in stream:
                    record=json.loads(line)
                    if record['type']=='metadata':terrain=record['terrain']
                    elif record['type']=='decision':
                        state=central.make_state(record['observation'],record['units'],terrain,backbone)
                        if not np.array_equal(state,d['state'][index]):raise ValueError('Critic state recomputation differs')
                        actor=record['actor'];label=(critic.terminal_value(terminal,actor['team'])+1)/2
                        if label!=d['win'][index] or actor['team']!=d['team'][index] or actor['round']!=d['round'][index] or record['input']!=d['input'][index]:raise ValueError('Critic observation/label alignment changed')
                        index+=1
                if index!=e['rows']:raise ValueError('Critic states incomplete')
            games+=1;rows+=index
    r=dict(passed=True,games=games,rows=rows,training_manifest_sha256=fixed['training_manifest_sha256'],
        evaluation_manifest_sha256=core.sha(root()/'evaluation-manifest.json'),source_sha256=fixed['source_sha256'],
        current_state_only=True,actor_unchanged=True,confirmation_games=0)
    return save('stage4-v4-audit.json',r)


def evaluate_snapshot(observation,units,terrain):
    state=central.make_state(observation,units,terrain,critic.parent())[None,:];p=float(predict(load_model(),state)[0])
    return dict(probability=p,value=2*p-1)


def ready():
    from . import stage3
    stage3.ready();fixed=frozen();plan();model=load_model();audit_result=json.loads((core.ROOT/'results/stage4-v4-audit.json').read_text())
    report=json.loads((model_root()/'evaluation.json').read_text());data=read_data(root(),'evaluation-manifest.json','fresh_validation');current=score(model,data)
    if not audit_result['passed'] or audit_result['source_sha256']!=fixed['source_sha256'] or audit_result['evaluation_manifest_sha256']!=report['evaluation_manifest_sha256']:raise ValueError('Monotone audit stale')
    if core.sha(root()/'evaluation-manifest.json')!=report['evaluation_manifest_sha256'] or report['model_sha256']!=fixed['model_sha256']:raise ValueError('Monotone evaluation identity changed')
    for name in current:
        for field in ('brier','log_loss'):
            if abs(current[name][field]-report['scores'][name][field])>1e-7:raise ValueError('Monotone exported metrics differ')
    base=model['baseline'];head=model['head'];state=data['state']
    normalized=(state[:,:4]-base['mean'])/base['scale'];z=normalized.astype(np.float64)@base['coef'][:-1].astype(np.float64)+float(base['coef'][-1])
    transformed=features(state,head['mode'])/head['scale'];full=float(head['coef'][0])*z+transformed.astype(np.float64)@head['coef'][1:].astype(np.float64)
    reference=critic.sigmoid(z+model['shrinkage']*(full-z));error=float(np.max(np.abs(reference-predict(model,state))))
    if error>1e-6:raise ValueError('Monotone probability export parity failed')
    if core.sha(model_root()/'actor.f32')!=core.config()['stage4']['parent_sha256']:raise ValueError('BC actor changed')
    native=json.loads((core.ROOT/'results/stage4-v3-native-proof.json').read_text())
    if not native['passed'] or not native['hidden_enemy_gold_does_not_change_actor']:raise ValueError('Missing actor/critic privacy check')
    passed=central.acceptance(current)
    value=dict(passed=bool(passed),pipeline_checks_passed=True,predictive_acceptance_passed=bool(passed),stage=4,next_stage=5 if passed else 4,model=fixed['model'],
        parent_weights_sha256=fixed['parent_weights_sha256'],actor_unchanged=True,training_games=fixed['training_games'],training_states=fixed['training_states'],
        fresh_validation_games=current['critic']['games'],fresh_validation_maps=current['critic']['maps'],
        scores={name:{k:s[k] for k in ('brier','log_loss','accuracy','expected_calibration_error')} for name,s in current.items()},
        uncertainty=report['uncertainty'],exported_probability_max_error=error,critic_privileged_state=head['mode'] in ('team','team_banks'),
        critic_in_actor_runtime=False,ppo_started=False,confirmation_games=0,promoted=False,sources=stage1.sources())
    save('stage4-v4-ready.json',value);save('stage4-ready.json',value);return value


def development():
    data=read_data(training_root(),'training-manifest.json','train');_,result=select(data,core.config()['stage4'])
    save('stage4-v4-development.json',result);return result


def prepare():
    plan();return dict(training_source='immutable '+core.config()['stage4']['central_training_dataset'],fresh_matches_unplayed=True)

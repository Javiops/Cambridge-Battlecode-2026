"""Stage 4 v3: critic-only team state with a frozen score/time offset and BC encoder.

The actor is unchanged. The critic may use current centralized training state;
terminal statistics and future timeline states never enter its feature function.
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
from threading import Timer

import numpy as np

from . import core, critic, dataset, mapgen, policy, cloning, replay, stage1, stats

TEAM_NAMES=('carried_gems','spendable_gold','alive_fraction','health_fraction','strength','focus','bank_ready_gems','channel_gems')
WORLD_START=44
WORLD_FEATURES=24
FEATURES=WORLD_START+WORLD_FEATURES


def root():return core.ROOT/'datasets'/core.config()['stage4']['dataset']
def model_root():return core.ROOT/'models'/core.config()['stage4']['model']
def normalized_sha(path):return hashlib.sha256(path.read_text(encoding='utf-8').encode()).hexdigest()
def save(name,value):
    (core.ROOT/'results'/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');return value


def team_features(units,team,terrain,round_number):
    if team not in (0,1) or not units or len({u['id'] for u in units})!=len(units):raise ValueError('Invalid centralized roster')
    aggregates=[]
    for side in (0,1):
        selected=[u for u in units if u['team']==side]
        if not selected:raise ValueError('Centralized snapshot lacks a team')
        out=np.zeros(len(TEAM_NAMES),np.float64)
        for u in selected:
            values=[u[k] for k in ('gold','gems','health','max_health','strength','focus','x','y')]
            if not np.isfinite(values).all() or min(u['gold'],u['gems'],u['health'])<0:raise ValueError('Invalid current unit state')
            alive=bool(u['state']&1);health=max(0,u['health'])/max(1,u['max_health']) if alive else 0
            distance=min(max(abs(u['x']-p[0]),abs(u['y']-p[1])) for p in terrain['altars'])
            out += [u['gems']/1000,u['gold']/5000,alive/len(selected),health/len(selected),
                    u['strength']/1000,u['focus']/1000,u['gems']/1000/(1+distance),
                    u['gems']/1000 if u['state']&4 else 0]
        aggregates.append(out)
    margin=aggregates[team]-aggregates[1-team];elapsed=round_number/2000
    # Odd signed compression preserves opponent complementarity and bounds large bags.
    compressed=np.sign(margin)*np.log1p(np.abs(margin))
    result=np.r_[margin,margin*elapsed,compressed].astype(np.float32)
    if not np.isfinite(result).all():raise ValueError('Invalid team feature vector')
    return result


def make_state(observation,units,terrain,backbone):
    encoded=policy.encode(observation,terrain)
    local=critic.encode(backbone,[encoded['features']],[encoded['candidates']],[encoded['mask']],np.array([observation['actor']['team']]))[0]
    central=team_features(units,observation['actor']['team'],terrain,observation['actor']['round'])
    return np.r_[local,central].astype(np.float32)


def native_check():
    r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/critic-state-check.mjs'),str(mapgen.engine_path()),
        str(core.map_path('00collision'))],capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=30)
    if r.returncode:raise ValueError(r.stderr[-2000:])
    result=json.loads(r.stdout);result['engine_sha256']=core.sha(mapgen.engine_path())
    return save('stage4-v3-native-proof.json',result)


def extract(episode,source):
    if episode['status']!='admitted':raise ValueError('Faulty or quarantined critic source')
    cfg=core.config()['stage4'];destination=root()/'episodes'/episode['episode_id'];destination.mkdir(parents=True,exist_ok=True)
    meta_path=destination/'episode.json'
    if meta_path.exists():
        meta=json.loads(meta_path.read_text())
        if core.sha(destination/'critic.npz')!=meta['sha256'] or core.sha(destination/'states.jsonl.gz')!=meta['states_sha256']:
            raise ValueError('Central critic cache changed')
        if meta['extractor_sha256']!=normalized_sha(core.ROOT/'lab/critic-world.mjs') or meta['state_reader_sha256']!=normalized_sha(core.ROOT/'lab/critic-state.mjs'):
            raise ValueError('Central state reader changed; use a new dataset version')
        return meta
    replay_file=max(source.glob('*.repl26a'),key=lambda p:p.stat().st_mtime);blob=dataset.raw_bytes(replay_file)
    actions=replay.decode(blob,core.map_path(episode['map']).read_bytes());arrays={k:[] for k in ('state','win','team','round','actor','input')}
    backbone=critic.parent();finished=False;metadata=None;terminal=episode.get('terminal')
    with tempfile.TemporaryDirectory(dir=destination) as tmp:
        tmp=Path(tmp);(tmp/'raw.repl26a').write_bytes(blob)
        request=dict(replay=str(tmp/'raw.repl26a'),map=str(core.map_path(episode['map'])),actions=actions,round_stride=cfg['world_round_stride'])
        (tmp/'request.json').write_text(json.dumps(request))
        with (tmp/'errors.txt').open('w',encoding='utf-8') as errors,gzip.open(tmp/'states.jsonl.gz','wt',encoding='utf-8') as archive:
            process=subprocess.Popen([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/critic-world.mjs'),str(mapgen.engine_path()),str(tmp/'request.json')],
                cwd=core.ROOT,env=core.ENV,stdout=subprocess.PIPE,stderr=errors,text=True,encoding='utf-8')
            watchdog=Timer(core.TIMEOUT,process.kill);watchdog.start()
            try:
                for line in process.stdout:
                    row=json.loads(line)
                    if row['type']=='metadata':
                        metadata=row;dataset.completed_outcome(row['terminal'])
                        if terminal and terminal!=row['terminal']:raise ValueError('Central source terminal mismatch')
                        terminal=row['terminal']
                        if row['engine_sha256']!=core.config()['stage1']['engine_wasm_sha256']:raise ValueError('Wrong world engine')
                        archive.write(line)
                    elif row['type']=='decision':
                        o=row['observation'];state=make_state(o,row['units'],metadata['terrain'],backbone)
                        for k,v in dict(state=state,win=(critic.terminal_value(terminal,o['actor']['team'])+1)/2,
                            team=o['actor']['team'],round=o['actor']['round'],actor=o['actor']['champion'],input=row['input']).items():arrays[k].append(v)
                        archive.write(line)
                    elif row['type']=='complete':finished=True;archive.write(line)
                code=process.wait(timeout=30)
            except BaseException:
                process.kill();process.wait();raise
            finally:watchdog.cancel();process.stdout.close()
        if code or not finished:raise ValueError('Central critic extraction failed: '+(tmp/'errors.txt').read_text()[-2000:])
        if not arrays['win'] or set(arrays['team'])!={0,1}:raise ValueError('Incomplete central critic perspectives')
        np.savez_compressed(tmp/'critic.npz',**{k:np.asarray(v,dtype=np.float32 if k=='state' else np.uint8 if k in ('win','team') else np.uint32) for k,v in arrays.items()})
        shutil.copyfile(tmp/'critic.npz',destination/'critic.npz');shutil.copyfile(tmp/'states.jsonl.gz',destination/'states.jsonl.gz')
    meta=dict(episode_id=episode['episode_id'],split=episode['split'],map=episode['map'],map_sha256=episode['map_sha256'],
        family=episode['family'],lineages=episode['lineages'],runtime=episode['runtime'],terminal=terminal,rows=len(arrays['win']),
        path=(destination/'critic.npz').relative_to(root()).as_posix(),sha256=core.sha(destination/'critic.npz'),
        states_sha256=core.sha(destination/'states.jsonl.gz'),source_replay_sha256=hashlib.sha256(blob).hexdigest(),
        source_dir=source.relative_to(core.ROOT).as_posix(),extractor_sha256=normalized_sha(core.ROOT/'lab/critic-world.mjs'),
        state_reader_sha256=normalized_sha(core.ROOT/'lab/critic-state.mjs'))
    dataset.immutable(meta_path,meta);return meta


def load(split,manifest_name='training-sources.json'):
    manifest=json.loads((root()/manifest_name).read_text());arrays={k:[] for k in ('state','win','team','round')};ids=[];maps=[];families=[]
    for e in manifest['episodes']:
        if e['split']!=split:continue
        path=root()/e['path']
        if core.sha(path)!=e['sha256']:raise ValueError('Central critic shard hash mismatch')
        with np.load(path,allow_pickle=False) as data:
            if data['state'].shape!=(e['rows'],FEATURES) or not np.isfinite(data['state']).all():raise ValueError('Invalid central critic shape')
            target=np.array([(critic.terminal_value(e['terminal'],int(t))+1)/2 for t in data['team']],np.uint8)
            if not np.array_equal(target,data['win']):raise ValueError('Central critic labels changed')
            for k in arrays:arrays[k].append(data[k])
        ids.extend([e['episode_id']]*e['rows']);maps.extend([e['map']]*e['rows']);families.extend([e['family']]*e['rows'])
    if not ids:raise ValueError('Empty central critic partition')
    data={k:np.concatenate(v) for k,v in arrays.items()};data.update(episode=np.asarray(ids),map=np.asarray(maps),family=np.asarray(families))
    data['weight']=critic.group_weights(data['episode'],data['team']);return data


def columns(mode):
    if mode=='team':return np.arange(WORLD_START,FEATURES)
    if mode=='team_bc':return np.r_[np.arange(28,44),np.arange(WORLD_START,FEATURES)]
    raise ValueError('Unknown residual feature contract')


def base_logits(head,state):
    normalized=(state[:,:4].astype(np.float32)-head['mean'])/head['scale']
    return normalized@head['coef'][:-1]+head['coef'][-1]


def residual_objective(coef,design,y,weight,l2,offset):
    z=offset+design@coef;p=critic.sigmoid(z)
    loss=float(np.sum(weight*(np.logaddexp(0,z)-y*z))+.5*l2*np.dot(coef,coef))
    gradient=design.T@(weight*(p-y))+l2*coef
    hessian=design.T@((weight*p*(1-p))[:,None]*design)+np.eye(len(coef))*l2
    return loss,gradient,hessian


def fit_residual(state,y,weight,baseline,mode,l2,cfg):
    indexes=columns(mode);x=state[:,indexes].astype(np.float64)
    # Zero-centered RMS scaling preserves zero residual when both teams are equal.
    scale=np.sqrt(np.sum(weight[:,None]*x*x,axis=0));scale=np.where(scale<1e-6,1.,scale)
    design=x/scale;offset=base_logits(baseline,state).astype(np.float64);coef=np.zeros(len(indexes))
    for iteration in range(cfg['newton_iterations']):
        loss,gradient,hessian=residual_objective(coef,design,y,weight,l2,offset)
        if np.max(np.abs(gradient))<cfg['newton_tolerance']:break
        direction=np.linalg.solve(hessian,gradient);step=1.
        for _ in range(cfg['line_search_steps']):
            candidate=coef-step*direction
            if residual_objective(candidate,design,y,weight,l2,offset)[0]<=loss-1e-4*step*np.dot(gradient,direction):coef=candidate;break
            step*=.5
        else:raise ValueError('Residual optimizer line search failed')
    else:raise ValueError('Residual optimizer failed to converge')
    return dict(coef=coef.astype(np.float32),scale=scale.astype(np.float32),indexes=indexes,l2=l2,mode=mode,iterations=iteration+1)


def residual_logits(head,state):return (state[:,head['indexes']].astype(np.float32)/head['scale'])@head['coef']


def predict(model,state):
    return critic.sigmoid(base_logits(model['baseline'],state)+model['shrinkage']*residual_logits(model['residual'],state))


def cross_validate(data,cfg):
    families=sorted(np.unique(data['family']).tolist())
    if families!=[0,1,2]:raise ValueError('Training-only leave-family-out selection requires families 0/1/2')
    folds=[]
    for family in families:
        selected=data['family']==family
        folds.append((critic.subset(data,~selected),critic.subset(data,selected),selected))
    baseline_trials=[]
    for l2 in cfg['l2_grid']:
        oof=np.zeros(len(data['win']))
        for train,dev,index in folds:
            head=critic.fit(train['state'][:,:4],train['win'],train['weight'],l2,cfg)
            oof[index]=critic.predict(head,dev['state'])
        baseline_trials.append(dict(l2=l2,metrics=critic.metrics(data['win'],oof,data['weight'],cfg['calibration_bins'])))
    base_choice=min(baseline_trials,key=lambda t:t['metrics']['log_loss']);cached=[]
    for train,dev,index in folds:
        base=critic.fit(train['state'][:,:4],train['win'],train['weight'],base_choice['l2'],cfg)
        cached.append((train,dev,index,base,base_logits(base,dev['state'])))
    residual_trials=[]
    for mode in cfg['residual_modes']:
        for l2 in cfg['residual_l2_grid']:
            components=[]
            for train,dev,index,base,offset in cached:
                head=fit_residual(train['state'],train['win'],train['weight'],base,mode,l2,cfg)
                components.append((index,offset,residual_logits(head,dev['state'])))
            for shrinkage in cfg['residual_shrinkage']:
                oof=np.zeros(len(data['win']))
                for index,offset,residual in components:oof[index]=critic.sigmoid(offset+shrinkage*residual)
                measured=critic.metrics(data['win'],oof,data['weight'],cfg['calibration_bins'])
                residual_trials.append(dict(mode=mode,l2=l2,shrinkage=shrinkage,metrics=measured,
                    selection_objective=measured['log_loss']+(cfg['bc_complexity_penalty'] if mode=='team_bc' else 0)))
            print(f"CV residual {mode} L2={l2}",flush=True)
    selected=min(residual_trials,key=lambda t:t['selection_objective'])
    base=critic.fit(data['state'][:,:4],data['win'],data['weight'],base_choice['l2'],cfg)
    residual=fit_residual(data['state'],data['win'],data['weight'],base,selected['mode'],selected['l2'],cfg)
    passed=(selected['metrics']['brier']+cfg['minimum_cv_brier_gain']<base_choice['metrics']['brier']
        and selected['metrics']['log_loss']<base_choice['metrics']['log_loss'])
    return dict(baseline=base,residual=residual,shrinkage=selected['shrinkage']),dict(
        selection='leave-one-training-family-out; no outer evaluation data',baseline_trials=baseline_trials,
        residual_trials=residual_trials,selected_baseline=base_choice,selected_residual=selected,
        internal_acceptance_passed=bool(passed),families=families)


def development():
    manifest='training-manifest.json' if (root()/'training-manifest.json').exists() else 'training-sources.json'
    data=load('train',manifest);model,result=cross_validate(data,core.config()['stage4'])
    save('stage4-v3-development.json',result)
    return dict(passed=result['internal_acceptance_passed'],baseline=result['selected_baseline']['metrics'],candidate=result['selected_residual'])


def maps():
    cfg=core.config()['stage4'];rows=[]
    for i,name in enumerate(cfg['fresh_validation_maps']):
        seed=(mapgen.seed_for('critic-v3-validation',cfg['validation_map_seed'],i)&~3)|3
        m=mapgen.layout(seed);m.update(name=name,output=str(core.MAPS/(name+'.map26a')))
        rows.append(m)
    with tempfile.TemporaryDirectory(dir=core.ROOT/'.cambc') as tmp:
        request=Path(tmp)/'maps.json';request.write_text(json.dumps(rows))
        result=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/engine.mjs'),str(mapgen.engine_path()),'maps',str(request)],
            capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=120)
        if result.returncode:raise ValueError(result.stderr[-2000:])
    result=dict(generator='g1 geometry, independent critic-v3 seed stream, family 3',seed=cfg['validation_map_seed'],
        engine_sha256=core.sha(mapgen.engine_path()),maps=json.loads(result.stdout),role='screening-only critic acceptance; never final confirmation')
    dataset.immutable(core.ROOT/'mechanics/critic-v3-maps.json',result);return result


def sources():
    inherited=[]
    for e,path in dataset.shards('train'):inherited.append((e,path.parent))
    previous=core.ROOT/'datasets'/core.config()['stage4']['source_dataset']
    for path in sorted((previous/'fresh').glob('*/episode.json')):
        e=json.loads(path.read_text())
        if e['split']=='train' and e['status']=='admitted':inherited.append((e,path.parent))
    return inherited


def plan():
    cfg=core.config()['stage4'];critic.parent();maps();inherited=sources();used={e['map'] for e,_ in inherited}
    previous=json.loads((core.ROOT/'datasets'/cfg['source_dataset']/'manifest.json').read_text())
    used|={e['map'] for e in previous['extra_training_quarantine']}
    family={name:mapgen.layout(mapgen.seed_for('screen',core.config()['stage1']['screen_seed'],i))['family'] for i,name in enumerate(core.config()['maps']['screen'])}
    extra=[];profile=core.runtime_identity()
    for f in (0,1,2):
        selected=[name for name in core.config()['maps']['screen'] if family[name]==f and name not in used][:cfg['additional_maps_per_training_family']]
        for name in selected:
            v=core.version('online-v76-week2-v1')
            e=dict(split='train',map=name,map_sha256=core.sha(core.map_path(name)),family=f,names=[v.name]*2,
                wasm_sha256=[v.meta['wasm_sha256']]*2,runtime=profile,lineages=['live-love-larp-v76']*2)
            e['episode_id']=dataset.digest(e)[:24];extra.append(e)
    validation=[]
    for name in cfg['fresh_validation_maps']:
        for a,b in cfg['fresh_validation_pairs']:
            for x,y in ([(a,b)] if a==b else [(a,b),(b,a)]):
                versions=[core.version(n) for n in (x,y)]
                e=dict(split='fresh_validation',map=name,map_sha256=core.sha(core.map_path(name)),family=3,names=[x,y],
                    wasm_sha256=[v.meta['wasm_sha256'] for v in versions],runtime=profile,
                    lineages=[core.config()['stage2']['lineages'][n] for n in (x,y)])
                e['episode_id']=dataset.digest(e)[:24];validation.append(e)
    train_lineages={l for e,_ in inherited for l in e['lineages']}|{l for e in extra for l in e['lineages']}
    if train_lineages&{l for e in validation for l in e['lineages']}:raise ValueError('Outer lineage leakage')
    if ({e['map_sha256'] for e,_ in inherited}|{e['map_sha256'] for e in extra}) & {e['map_sha256'] for e in validation}:raise ValueError('Outer map leakage')
    value=dict(schema=3,config=cfg,parent_weights_sha256=cfg['parent_sha256'],runtime=profile,
        inherited_sources=[dict(episode_id=e['episode_id'],map=e['map'],source_dir=p.relative_to(core.ROOT).as_posix(),replay_sha256=e['replay_sha256']) for e,p in inherited],
        extra_training_episodes=extra,fresh_validation_episodes=validation,map_manifest_sha256=core.sha(core.ROOT/'mechanics/critic-v3-maps.json'),
        acceptance='strictly lower game/team-weighted Brier AND log loss than constant AND independently selected score/time baseline; unchanged from v2',
        selection='training families 0/1/2 leave-one-family-out; freeze before any fresh acceptance match',
        critic_privileged_state=True,actor_updated=False,ppo_started=False,confirmation_games=0)
    dataset.immutable(root()/'plan.json',value);save('stage4-v3-plan.json',value);return value


def run_episode(e):
    source=root()/'raw'/e['episode_id'];source.mkdir(parents=True,exist_ok=True);meta=source/'episode.json'
    if meta.exists():return json.loads(meta.read_text()),source
    raw,error=core.run_game(*[core.version(n) for n in e['names']],core.map_path(e['map']),str(source),profile=e['runtime'])
    if raw is None:raise ValueError('Unfinished critic game: '+error)
    compact=stats.summarize(raw)
    bad=any(t['faults'] or t['fuel_exhausted'] for t in compact['teams'].values())
    if bad and e['split']!='train':raise ValueError('Acceptance game failed release execution')
    value=e|dict(status='quarantined' if bad else 'admitted',
        diagnostics={t:{k:v[k] for k in ('faults','fuel_exhausted')} for t,v in compact['teams'].items()})
    if not bad:value['terminal']=dict(outcome=compact['outcome'],round=compact['rounds'],banks=[compact['teams'][t]['gems'] for t in ('teamA','teamB')])
    dataset.immutable(meta,value);return value,source


def prepare():
    planned=plan();native_check();all_sources=sources();rejected=[]
    with ThreadPoolExecutor(core.config()['stage4']['jobs']) as pool:
        for e,p in pool.map(run_episode,planned['extra_training_episodes']):
            if e['status']=='admitted':all_sources.append((e,p))
            else:rejected.append(e)
    episodes=[]
    with ThreadPoolExecutor(core.config()['stage4']['jobs']) as pool:
        for e in pool.map(lambda pair:extract(*pair),all_sources):
            episodes.append(e);print(f"Prepared {len(episodes)}/{len(all_sources)} training games",flush=True)
    result=dict(episodes=episodes,quarantined_new_games=rejected,source_dataset=core.config()['stage4']['source_dataset'],
        rows=sum(e['rows'] for e in episodes),plan_sha256=core.sha(root()/'plan.json'))
    dataset.immutable(root()/'training-manifest.json',result);save('stage4-v3-dataset.json',result)
    return dict(games=len(episodes),rows=result['rows'],quarantined_new_games=len(rejected))


def export_model(path,model):
    base=model['baseline'];res=model['residual']
    np.savez(path,base_coef=base['coef'],base_mean=base['mean'],base_scale=base['scale'],
        residual_coef=res['coef'],residual_scale=res['scale'],residual_indexes=res['indexes'].astype(np.int32),
        shrinkage=np.asarray(model['shrinkage'],np.float32),backbone=critic.parent())


def load_model(path=None):
    with np.load(path or model_root()/'critic.npz',allow_pickle=False) as d:
        model=dict(baseline=dict(coef=d['base_coef'],mean=d['base_mean'],scale=d['base_scale']),
            residual=dict(coef=d['residual_coef'],scale=d['residual_scale'],indexes=d['residual_indexes']),shrinkage=float(d['shrinkage']))
        if not np.array_equal(d['backbone'],critic.parent()):raise ValueError('Central critic BC backbone changed')
    base=model['baseline'];res=model['residual']
    if base['coef'].shape!=(5,) or base['mean'].shape!=(4,) or base['scale'].shape!=(4,) or np.any(base['scale']<=0):raise ValueError('Invalid score baseline export')
    if res['coef'].shape!=res['scale'].shape or res['coef'].shape!=res['indexes'].shape or np.any(res['scale']<=0):raise ValueError('Invalid residual export')
    if not any(np.array_equal(res['indexes'],columns(mode)) for mode in ('team','team_bc')):raise ValueError('Invalid privileged feature indexes')
    if not all(np.isfinite(x).all() for x in (*base.values(),*res.values())) or not 0<=model['shrinkage']<=1:raise ValueError('Nonfinite central critic export')
    return model


def evaluate_snapshot(observation,units,terrain):
    """Training-time API; units must come from the SAME current state, critic-only."""
    model=load_model();state=make_state(observation,units,terrain,critic.parent())[None,:]
    p=float(predict(model,state)[0]);return dict(probability=p,value=2*p-1)


def train():
    cfg=core.config()['stage4'];planned=plan();folder=model_root()
    if folder.exists():raise ValueError('Critic version exists; preserve it and choose a new name')
    data=load('train','training-manifest.json');started=time.perf_counter()
    model,selection=cross_validate(data,cfg)
    save('stage4-v3-development.json',selection)
    if not selection['internal_acceptance_passed']:raise ValueError('Training-only cross-validation did not clear improvement floor; outer evaluation stays sealed')
    folder.mkdir(parents=True);export_model(folder/'critic.npz',model)
    shutil.copyfile(core.ROOT/'models'/cfg['parent']/'weights.f32',folder/'actor.f32')
    model=load_model();prediction=predict(model,data['state'])
    frozen=dict(model=cfg['model'],parent=cfg['parent'],parent_weights_sha256=cfg['parent_sha256'],actor_unchanged=True,
        backbone_frozen=True,model_sha256=core.sha(folder/'critic.npz'),actor_sha256=core.sha(folder/'actor.f32'),
        plan_sha256=core.sha(root()/'plan.json'),training_manifest_sha256=core.sha(root()/'training-manifest.json'),
        source_sha256=normalized_sha(Path(__file__)),helper_source_sha256=normalized_sha(core.ROOT/'lab/critic.py'),
        selection=selection,training=critic.metrics(data['win'],prediction,data['weight'],cfg['calibration_bins']),
        training_games=len(np.unique(data['episode'])),training_maps=len(np.unique(data['map'])),training_states=len(data['win']),
        elapsed_seconds=time.perf_counter()-started,trainable_parameters=len(model['baseline']['coef'])+len(model['residual']['coef']),
        critic_privileged_state=True,outer_matches_seen=0,outer_model_selections=0,ppo_started=False,confirmation_games=0)
    dataset.immutable(folder/'frozen.json',frozen);dataset.immutable(folder/'plan.json',planned)
    save('stage4-v3-frozen.json',frozen)
    return {k:frozen[k] for k in ('model','training_games','training_maps','training_states','trainable_parameters','model_sha256','elapsed_seconds')}


def scores(model,data):
    cfg=core.config()['stage4'];result={}
    probabilities={'constant':np.full(len(data['win']),.5),'score_time':critic.predict(model['baseline'],data['state']),'critic':predict(model,data['state'])}
    for name,p in probabilities.items():
        value=critic.metrics(data['win'],p,data['weight'],cfg['calibration_bins']);value.update(games=len(np.unique(data['episode'])),maps=len(np.unique(data['map'])),phases={})
        a,b=cfg['phase_boundaries']
        for phase,index in [('early',data['round']<=a),('middle',(data['round']>a)&(data['round']<=b)),('late',data['round']>b)]:
            if index.any():
                d=critic.subset(data,index);value['phases'][phase]=critic.metrics(d['win'],p[index],d['weight'],cfg['calibration_bins'])
        result[name]=value
    return result


def acceptance(measured):
    for name in ('constant','score_time','critic'):
        for field in ('brier','log_loss'):
            if not np.isfinite(measured[name][field]) or measured[name][field]<0:raise ValueError('Invalid predictive gate metric')
    return all(measured['critic'][field]<measured[name][field] for field in ('brier','log_loss') for name in ('constant','score_time'))


def bootstrap(data,model):
    cfg=core.config()['stage4'];names=np.unique(data['map']);differences=[]
    for name in names:
        d=critic.subset(data,data['map']==name);s=scores(model,d);differences.append(s['critic']['brier']-s['score_time']['brier'])
    rng=np.random.default_rng(cfg['seed']);indexes=rng.integers(0,len(names),(cfg['bootstrap_samples'],len(names)))
    interval=np.quantile(np.asarray(differences)[indexes].mean(axis=1),[.05,.95])
    return dict(unit='whole map, both seats and all pairings retained',maps=len(names),mean_difference=float(np.mean(differences)),
        paired_brier_difference_by_map=dict(zip(names.tolist(),differences)),interval_90=interval.tolist(),superiority_supported=bool(interval[1]<0))


def frozen():
    folder=model_root();value=json.loads((folder/'frozen.json').read_text())
    if core.sha(folder/'critic.npz')!=value['model_sha256'] or core.sha(folder/'actor.f32')!=value['actor_sha256']:raise ValueError('Frozen critic weights changed')
    if normalized_sha(Path(__file__))!=value['source_sha256'] or normalized_sha(core.ROOT/'lab/critic.py')!=value['helper_source_sha256']:
        raise ValueError('Frozen training source changed')
    if core.sha(root()/'plan.json')!=value['plan_sha256'] or core.sha(root()/'training-manifest.json')!=value['training_manifest_sha256']:
        raise ValueError('Frozen training inputs changed')
    return value


def evaluate():
    value=frozen();planned=plan();model=load_model();episodes=[]
    with ThreadPoolExecutor(core.config()['stage4']['jobs']) as pool:
        sources_eval=list(pool.map(run_episode,planned['fresh_validation_episodes']))
    with ThreadPoolExecutor(core.config()['stage4']['jobs']) as pool:
        for e in pool.map(lambda pair:extract(*pair),sources_eval):
            episodes.append(e);print(f"Acceptance replay {len(episodes)}/{len(sources_eval)}",flush=True)
    dataset.immutable(root()/'evaluation-manifest.json',dict(episodes=episodes,model_sha256=value['model_sha256'],plan_sha256=value['plan_sha256']))
    data=load('fresh_validation','evaluation-manifest.json');measured=scores(model,data)
    passed=acceptance(measured)
    report=dict(model=value['model'],passed=bool(passed),predictive_acceptance_passed=bool(passed),scores=measured,uncertainty=bootstrap(data,model),
        frozen_model_sha256=value['model_sha256'],evaluation_manifest_sha256=core.sha(root()/'evaluation-manifest.json'),
        outer_model_selections=0,actor_unchanged=True,critic_privileged_state=True,ppo_started=False,confirmation_games=0,promoted=False)
    dataset.immutable(model_root()/'evaluation.json',report);save('stage4-v3-evaluation.json',report)
    return dict(passed=passed,scores={name:{field:s[field] for field in ('brier','log_loss','accuracy','expected_calibration_error')} for name,s in measured.items()},uncertainty=report['uncertainty'])


def audit():
    value=frozen();backbone=critic.parent();count=0;games=0
    for name in ('training-manifest.json','evaluation-manifest.json'):
        manifest=json.loads((root()/name).read_text())
        for e in manifest['episodes']:
            p=root()/e['path'];archive=p.parent/'states.jsonl.gz'
            if core.sha(p)!=e['sha256'] or core.sha(archive)!=e['states_sha256']:raise ValueError('Central dataset hash changed')
            source=core.ROOT/e['source_dir'];raw=json.loads((source/'stats.json').read_text());compact=stats.summarize(raw)
            if raw['match']['engineBuildHash']!=e['runtime']['engine_build_hash'] or raw['match']['mapHash']!=e['map_sha256']:raise ValueError('Central source provenance changed')
            if any(t['faults'] or t['fuel_exhausted'] for t in compact['teams'].values()):raise ValueError('Faulty source in central critic audit')
            if e['terminal']!=dict(outcome=compact['outcome'],round=compact['rounds'],banks=[compact['teams'][t]['gems'] for t in ('teamA','teamB')]):raise ValueError('Central target differs from release result')
            with np.load(p,allow_pickle=False) as data,gzip.open(archive,'rt',encoding='utf-8') as stream:
                index=0
                for line in stream:
                    row=json.loads(line)
                    if row['type']=='metadata':terrain=row['terrain']
                    elif row['type']=='decision':
                        state=make_state(row['observation'],row['units'],terrain,backbone)
                        if not np.array_equal(state,data['state'][index]):raise ValueError('Central feature reconstruction failed')
                        actor=row['actor'];target=(critic.terminal_value(e['terminal'],actor['team'])+1)/2
                        if target!=data['win'][index] or actor['team']!=data['team'][index] or actor['round']!=data['round'][index] or row['input']!=data['input'][index]:raise ValueError('Central row alignment failed')
                        index+=1
                if index!=e['rows']:raise ValueError('Missing central critic rows')
            games+=1;count+=index
    return save('stage4-v3-audit.json',dict(passed=True,games=games,rows=count,actor_unchanged=True,
        source_sha256=value['source_sha256'],training_manifest_sha256=value['training_manifest_sha256'],evaluation_manifest_sha256=core.sha(root()/'evaluation-manifest.json')))


def ready():
    from . import stage3
    stage3.ready();value=frozen();plan();model=load_model();audit_result=json.loads((core.ROOT/'results/stage4-v3-audit.json').read_text())
    if not audit_result['passed'] or audit_result['source_sha256']!=value['source_sha256']:raise ValueError('Central critic audit is stale')
    measured=json.loads((model_root()/'evaluation.json').read_text());data=load('fresh_validation','evaluation-manifest.json');current=scores(model,data)
    for name in current:
        for field in ('brier','log_loss'):
            if abs(current[name][field]-measured['scores'][name][field])>1e-7:raise ValueError('Exported central critic does not reproduce gate')
    if core.sha(root()/'evaluation-manifest.json')!=measured['evaluation_manifest_sha256'] or measured['frozen_model_sha256']!=value['model_sha256']:raise ValueError('Central evaluation changed')
    if core.sha(model_root()/'actor.f32')!=core.config()['stage4']['parent_sha256']:raise ValueError('BC starting actor changed')
    # Independent double accumulation of the exported float32 model.
    base=model['baseline'];res=model['residual'];s=data['state']
    b=(s[:,:4]-base['mean'])/base['scale'];r=s[:,res['indexes']]/res['scale']
    reference=critic.sigmoid(b.astype(np.float64)@base['coef'][:-1].astype(np.float64)+float(base['coef'][-1])+
        model['shrinkage']*(r.astype(np.float64)@res['coef'].astype(np.float64)))
    error=float(np.max(np.abs(reference-predict(model,s))))
    if error>1e-6:raise ValueError('Central export probability parity failed')
    native=json.loads((core.ROOT/'results/stage4-v3-native-proof.json').read_text())
    if not native['passed'] or not native['hidden_enemy_gold_does_not_change_actor']:raise ValueError('Missing actor/critic separation proof')
    passed=acceptance(current)
    result=dict(passed=bool(passed),pipeline_checks_passed=True,predictive_acceptance_passed=bool(passed),stage=4,next_stage=5 if passed else 4,
        model=value['model'],parent=value['parent'],parent_weights_sha256=value['parent_weights_sha256'],actor_unchanged=True,
        scores={name:{field:score[field] for field in ('brier','log_loss','accuracy','expected_calibration_error')} for name,score in current.items()},
        training_games=value['training_games'],training_states=value['training_states'],fresh_validation_games=current['critic']['games'],
        fresh_validation_maps=current['critic']['maps'],exported_probability_max_error=error,uncertainty=measured['uncertainty'],
        critic_privileged_state=True,critic_in_actor_runtime=False,ppo_started=False,confirmation_games=0,promoted=False,sources=stage1.sources())
    save('stage4-v3-ready.json',result);save('stage4-ready.json',result);return result

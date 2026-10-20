"""Binary outcome critic: frozen BC state encoder plus a regularized logistic head.

Predicts an undiscounted completed-game win under the replay behavior mixture.
This is an offline critic initialization, not an on-policy PPO value guarantee.
Actor weights, preprocessing and deployment remain unchanged.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import time

import numpy as np

from . import cloning, core, dataset, mapgen, policy, replay, stats

FEATURES = 44
BASE_FEATURES = 4


def root():
    return core.ROOT/'datasets'/core.config()['stage4']['dataset']


def model_root():
    return core.ROOT/'models'/core.config()['stage4']['model']


def save(name, data):
    (core.ROOT/'results'/name).write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    return data


def parent():
    cfg = core.config()['stage4']
    path = core.ROOT/'models'/cfg['parent']/'weights.f32'
    if core.sha(path) != cfg['parent_sha256']:
        raise ValueError('BC starting weights changed')
    w = np.fromfile(path, dtype='<f4')
    if w.shape != (cloning.N,) or not np.isfinite(w).all():
        raise ValueError('Invalid BC starting model')
    return w


def terminal_value(terminal, team):
    if team not in (0, 1):
        raise ValueError('Invalid actor team')
    outcome = dataset.completed_outcome(terminal or {})
    return 1.0 if outcome == ('teamA' if team == 0 else 'teamB') else -1.0


def encode(w, features, candidates, mask, teams):
    """All inputs are known at the decision; no outcomes, future state or action label."""
    features = np.asarray(features, np.float32); candidates = np.asarray(candidates, np.float32)
    mask = np.asarray(mask, bool); teams = np.asarray(teams)
    n = len(features)
    if features.shape != (n, policy.G) or candidates.shape != (n, policy.K, policy.C) or mask.shape != (n, policy.K):
        raise ValueError('Invalid critic encoder shape')
    if teams.shape != (n,) or not np.isin(teams, (0, 1)).all() or not mask.any(axis=1).all():
        raise ValueError('Invalid critic team or empty candidate mask')
    if not np.isfinite(features).all() or not np.isfinite(candidates).all():
        raise ValueError('Nonfinite critic input')
    _, _, hidden = cloning.forward(w, features, candidates, exact=True)
    mean = (hidden*mask[:, :, None]).sum(axis=1)/mask.sum(axis=1)[:, None]
    maximum = np.where(mask[:, :, None], hidden, -np.inf).max(axis=1)
    margin = features[:, 22]-features[:, 23]; elapsed = features[:, 7]
    # Seat is an actor-known fact. It belongs to the critic only; tie resolution favors B.
    baseline = np.stack((margin, elapsed, teams*2.0-1.0, margin*elapsed), axis=1)
    result = np.concatenate((baseline, features, mean, maximum), axis=1).astype(np.float32)
    if result.shape != (n, FEATURES) or not np.isfinite(result).all():
        raise ValueError('Invalid encoded critic state')
    return result


def group_weights(episodes, teams):
    """Equal game weight, then equal team weight, then equal frames within that team."""
    episodes = np.asarray(episodes); teams = np.asarray(teams)
    if len(episodes) == 0 or episodes.shape != teams.shape or not np.isin(teams, (0, 1)).all():
        raise ValueError('Invalid outcome weighting groups')
    result = np.zeros(len(episodes), np.float64)
    for episode in np.unique(episodes):
        for team in (0, 1):
            selected = (episodes==episode)&(teams==team)
            if not selected.any():
                raise ValueError('Outcome episode is missing a team')
            result[selected] = 1/(len(np.unique(episodes))*2*selected.sum())
    return result


def sigmoid(z):
    z = np.asarray(z, np.float64)
    return np.exp(-np.logaddexp(0, -z))


def objective(coef, design, y, weight, l2):
    z = design@coef; p = sigmoid(z)
    penalty = coef.copy(); penalty[-1] = 0
    loss = np.sum(weight*(np.logaddexp(0, z)-y*z)) + .5*l2*np.dot(penalty, penalty)
    gradient = design.T@(weight*(p-y)) + l2*penalty
    hessian = design.T@((weight*p*(1-p))[:, None]*design)
    hessian += np.diag(np.r_[np.full(len(coef)-1, l2), 0.])
    return float(loss), gradient, hessian


def fit(x, y, weight, l2, cfg):
    if l2 <= 0 or not np.isin(y, (0, 1)).all() or not np.isfinite(x).all() or not np.isclose(weight.sum(), 1):
        raise ValueError('Invalid critic fitting data')
    mean = np.sum(weight[:, None]*x, axis=0)
    scale = np.sqrt(np.sum(weight[:, None]*(x-mean)**2, axis=0))
    scale = np.where(scale < 1e-6, 1., scale)
    design = np.c_[(x-mean)/scale, np.ones(len(x))]
    coef = np.zeros(design.shape[1]); history = []
    for iteration in range(cfg['newton_iterations']):
        loss, gradient, hessian = objective(coef, design, y, weight, l2)
        history.append(loss)
        if np.max(np.abs(gradient)) < cfg['newton_tolerance']:
            break
        direction = np.linalg.solve(hessian, gradient)
        step = 1.
        for _ in range(cfg['line_search_steps']):
            proposed = coef-step*direction
            if objective(proposed, design, y, weight, l2)[0] <= loss-1e-4*step*np.dot(gradient, direction):
                coef = proposed
                break
            step *= .5
        else:
            raise ValueError('Critic optimizer line search failed')
    else:
        raise ValueError('Critic optimizer failed to converge')
    return dict(coef=coef.astype(np.float32), mean=mean.astype(np.float32), scale=scale.astype(np.float32),
                l2=float(l2), iterations=iteration+1, final_gradient_max=float(np.max(np.abs(gradient))), loss_history=history)


def predict(head, x):
    n = len(head['mean'])
    # Float32 exported readout. Inputs to the sigmoid are bounded only numerically,
    # not artificially clipped to give favorable calibration metrics.
    normalized = (np.asarray(x[:, :n], np.float32)-head['mean'])/head['scale']
    logits = normalized@head['coef'][:-1]+head['coef'][-1]
    return sigmoid(logits)


def metrics(y, probabilities, weight, bins=10):
    # uint8 target arrays must be cast BEFORE unary minus; -uint8(1) wraps to 255.
    y = np.asarray(y, np.float64); p = np.asarray(probabilities, np.float64)
    if p.shape != y.shape or not np.isfinite(p).all() or np.any(p<0) or np.any(p>1):
        raise ValueError('Invalid win probabilities')
    weight = weight/weight.sum(); p = np.clip(p, 1e-12, 1-1e-12)
    reliability = []; ece = 0.
    assigned = np.minimum((p*bins).astype(int), bins-1)
    for b in range(bins):
        selected = assigned==b; mass = float(weight[selected].sum())
        if mass:
            predicted = float(np.average(p[selected], weights=weight[selected])); actual = float(np.average(y[selected], weights=weight[selected]))
            ece += mass*abs(predicted-actual)
            reliability.append(dict(bin=b, weight=mass, rows=int(selected.sum()), predicted_win=predicted, actual_win=actual))
    return dict(rows=len(y), log_loss=float(np.sum(weight*(-y*np.log(p)-(1-y)*np.log1p(-p)))),
                brier=float(np.sum(weight*(p-y)**2)), accuracy=float(np.sum(weight*((p>=.5)==y))),
                expected_calibration_error=float(ece), mean_prediction=float(np.sum(weight*p)),
                win_fraction=float(np.sum(weight*y)), reliability=reliability)


def plan():
    cfg = core.config()['stage4']; parent()
    audit = json.loads((core.ROOT/'results/stage2-audit.json').read_text())
    if not audit['passed'] or core.sha(dataset.root()/'manifest.json') != audit['manifest_sha256']:
        raise ValueError('Stage 2 dataset certificate changed')
    for source, digest in audit['validator_sources'].items():
        if hashlib.sha256((core.ROOT/source).read_text().encode()).hexdigest() != digest:
            raise ValueError('Stage 2 importer changed; audit before using outcomes')
    used = {e['map'] for split in ('train', 'validation') for e, _ in dataset.shards(split)}
    if set(cfg['fresh_validation_maps'])&used or set(cfg['fresh_validation_maps'])-set(core.config()['maps']['screen']):
        raise ValueError('Fresh critic validation maps overlap or are not screening maps')
    families = {name:mapgen.layout(mapgen.seed_for('screen',core.config()['stage1']['screen_seed'],i))['family']
                for i,name in enumerate(core.config()['maps']['screen'])}
    episodes = []
    for name in cfg['fresh_validation_maps']:
        if families[name] not in core.config()['stage2']['validation_families']:
            raise ValueError('Critic validation family overlaps training')
        for a, b in cfg['fresh_validation_pairs']:
            for x, y in ([(a, b)] if a==b else [(a, b), (b, a)]):
                versions = [core.version(v) for v in (x, y)]
                episode = dict(split='fresh_validation', map=name, map_sha256=core.sha(core.map_path(name)), family=families[name],
                    names=[x, y], wasm_sha256=[v.meta['wasm_sha256'] for v in versions], runtime=core.runtime_identity(),
                    lineages=[core.config()['stage2']['lineages'][v] for v in (x, y)], teacher_teams=[0, 1])
                episode['episode_id'] = dataset.digest(episode)[:24]; episodes.append(episode)
    extra=[]
    for name in cfg['extra_training_maps']:
        if name not in families or families[name] not in core.config()['stage2']['train_families'] or name in used:
            raise ValueError('Extra critic training map leaks or is not from a training family')
        for a,b in cfg['extra_training_pairs']:
            for x,y in ([(a,b)] if a==b else [(a,b),(b,a)]):
                versions=[core.version(v) for v in (x,y)]
                episode=dict(split='train',map=name,map_sha256=core.sha(core.map_path(name)),family=families[name],
                    names=[x,y],wasm_sha256=[v.meta['wasm_sha256'] for v in versions],runtime=core.runtime_identity(),
                    lineages=[core.config()['stage2']['lineages'][v] for v in (x,y)],teacher_teams=[0,1])
                episode['episode_id']=dataset.digest(episode)[:24];extra.append(episode)
    train_episodes = [e for e, _ in dataset.shards('train')]
    if {l for e in train_episodes+extra for l in e['lineages']}&{l for e in episodes for l in e['lineages']}:
        raise ValueError('Critic validation lineage overlaps training')
    result = dict(schema=1, config=cfg, parent_weights_sha256=cfg['parent_sha256'], source_manifest_sha256=audit['manifest_sha256'],
        runtime=core.runtime_identity(), fresh_validation_episodes=episodes,extra_training_episodes=extra,
        sampling='first decision per sampled actor turn, both teams, alive and dead, complete admitted games only',
        weighting='equal game, then equal team, then equal sampled actor frames',
        selection='minimum development log loss, first/smallest regularizer wins exact ties; refit all train games before outer validation',
        outcome='binary terminal win; V=2P(win)-1; undiscounted; unfinished is never a draw',
        actor_update=False, ppo_started=False, confirmation_games=0)
    dataset.immutable(root()/'plan.json', result)
    save('stage4-plan.json', result)
    return result


def collect_fresh(episode):
    destination = root()/'fresh'/episode['episode_id']; destination.mkdir(parents=True, exist_ok=True)
    if (destination/'episode.json').exists():
        return json.loads((destination/'episode.json').read_text())
    raw, error = core.run_game(*[core.version(n) for n in episode['names']], core.map_path(episode['map']), str(destination), profile=episode['runtime'])
    if raw is None:
        raise ValueError('Incomplete critic validation game: '+error)
    summary = stats.summarize(raw)
    if any(t['faults'] or t['fuel_exhausted'] for t in summary['teams'].values()):
        if episode['split']=='train':
            rejected=episode|dict(status='quarantined',rows=0,reason='Release fault or fuel exhaustion; no critic labels',
                diagnostics={t:{k:v[k] for k in ('faults','fuel_exhausted')} for t,v in summary['teams'].items()})
            dataset.immutable(destination/'episode.json',rejected)
            return rejected
        raise ValueError('Critic validation game fault or fuel exhaustion; no outcome labels admitted')
    expected = dict(outcome=summary['outcome'], round=summary['rounds'], banks=[summary['teams'][t]['gems'] for t in ('teamA', 'teamB')])
    replay_file = max(destination.glob('*.repl26a'), key=lambda p:p.stat().st_mtime)
    result = dataset.extract(replay_file, episode['map'], destination, expected, (0, 1))|episode|dict(status='admitted')
    blob = dataset.raw_bytes(replay_file)
    actions = replay.decode(blob, core.map_path(episode['map']).read_bytes())
    metadata = dataset.run_replay_engine(blob, episode['map'], actions, metadata_only=True)[0]
    dataset.immutable(destination/'terrain.json', metadata['terrain'])
    dataset.immutable(destination/'episode.json', result)
    return result


def extract(episode, source, w):
    if episode['status'] != 'admitted':
        raise ValueError('Quarantined critic episode cannot be labelled')
    if core.sha(source/'decisions.jsonl.gz') != episode['decisions.jsonl.gz_sha256']:
        raise ValueError('Critic observation source changed')
    terrain_path = source/'terrain.json'
    if terrain_path.exists():
        terrain = json.loads(terrain_path.read_text())
    else:
        raise ValueError('Missing critic public terrain')
    f=[]; c=[]; mask=[]; teams=[]; rounds=[]; actors=[]; seen=set()
    with gzip.open(source/'decisions.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for line in stream:
            row=json.loads(line)
            if row['decision_index'] != 0:
                continue
            o=row['observation']; actor=o['actor']; key=(actor['team'], actor['champion'], actor['round'])
            if key in seen:
                raise ValueError('Duplicate critic actor turn')
            seen.add(key)
            encoded=policy.encode(o, terrain)
            if encoded != row['encoding']:
                raise ValueError('Critic state cannot reconstruct the authenticated observation')
            f.append(encoded['features']); c.append(encoded['candidates']); mask.append(encoded['mask'])
            teams.append(actor['team']); rounds.append(actor['round']); actors.append(actor['champion'])
    teams=np.asarray(teams, np.uint8); rounds=np.asarray(rounds, np.uint16)
    state=encode(w, f, c, mask, teams)
    y=np.asarray([(terminal_value(episode['terminal'], int(t))+1)/2 for t in teams], np.uint8)
    if set(teams.tolist()) != {0, 1}:
        raise ValueError('Critic episode lacks both perspectives')
    destination=root()/'shards'/f"{episode['split']}-{episode['episode_id']}.npz"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        np.savez_compressed(destination, state=state, win=y, team=teams, round=rounds, actor=np.asarray(actors, np.uint32))
    else:
        with np.load(destination, allow_pickle=False) as old:
            for k,v in dict(state=state, win=y, team=teams, round=rounds, actor=np.asarray(actors, np.uint32)).items():
                if not np.array_equal(old[k],v):raise ValueError('Frozen critic shard changed')
    return dict(episode_id=episode['episode_id'], map=episode['map'], family=episode['family'], split=episode['split'],
        rows=len(y), terminal=episode['terminal'], teams={str(t):n for t,n in Counter(int(t) for t in teams).items()},
        path=destination.relative_to(root()).as_posix(), sha256=core.sha(destination),
        observation_source_sha256=episode['decisions.jsonl.gz_sha256'], lineages=episode['lineages'],
        runtime=episode['runtime'], map_sha256=episode['map_sha256'])


def collect():
    planned=plan(); w=parent(); episodes=[]
    for split in ('train','validation'):
        for episode,path in dataset.shards(split):
            episodes.append(extract(episode,path.parent,w))
    with ThreadPoolExecutor(core.config()['stage4']['jobs']) as pool:
        fresh=list(pool.map(collect_fresh,planned['extra_training_episodes']+planned['fresh_validation_episodes']))
    for episode in fresh:
        if episode['status']=='admitted':episodes.append(extract(episode,root()/'fresh'/episode['episode_id'],w))
    quarantined=[e for e in fresh if e['status']=='quarantined']
    result=dict(schema=1, passed=True, parent_weights_sha256=planned['parent_weights_sha256'],
        source_manifest_sha256=planned['source_manifest_sha256'], plan_sha256=core.sha(root()/'plan.json'),
        episodes=episodes,extra_training_quarantine=quarantined,excluded_quarantined_games=1+len(quarantined),excluded_external_sparring_games=20,
        feature_count=FEATURES, terminal_labels_only=True, actor_updated=False, confirmation_games=0)
    dataset.immutable(root()/'manifest.json',result)
    save('stage4-dataset.json',result)
    return {s:dict(games=sum(e['split']==s for e in episodes), rows=sum(e['rows'] for e in episodes if e['split']==s)) for s in ('train','validation','fresh_validation')}


def load(split):
    manifest=json.loads((root()/'manifest.json').read_text()); arrays={k:[] for k in ('state','win','team','round')}; ids=[]; maps=[]
    for e in manifest['episodes']:
        if e['split'] != split:continue
        path=root()/e['path']
        if core.sha(path) != e['sha256']:raise ValueError('Critic shard hash mismatch')
        with np.load(path,allow_pickle=False) as data:
            if data['state'].shape != (e['rows'],FEATURES) or not np.isfinite(data['state']).all():raise ValueError('Invalid critic shard')
            expected=np.asarray([(terminal_value(e['terminal'],int(t))+1)/2 for t in data['team']],np.uint8)
            if not np.array_equal(expected,data['win']):raise ValueError('Critic terminal target mismatch')
            for k in arrays:arrays[k].append(data[k])
        ids.extend([e['episode_id']]*e['rows']); maps.extend([e['map']]*e['rows'])
    if not ids:raise ValueError('Empty critic partition')
    result={k:np.concatenate(v) for k,v in arrays.items()}
    result.update(episode=np.asarray(ids),map=np.asarray(maps)); result['weight']=group_weights(result['episode'],result['team'])
    if not np.isclose(np.sum(result['weight']*result['win']),.5):raise ValueError('Both-team game weighting is unbalanced')
    return result


def subset(data, selected):
    result={k:v[selected] for k,v in data.items() if k!='weight'}
    result['weight']=group_weights(result['episode'],result['team'])
    return result


def select(data, cfg, dimensions):
    dev=np.isin(data['map'],cfg['development_maps'])
    if not dev.any() or dev.all():raise ValueError('Invalid whole-map critic development split')
    fit_data=subset(data,~dev); development=subset(data,dev); results=[]
    for l2 in cfg['l2_grid']:
        head=fit(fit_data['state'][:,:dimensions],fit_data['win'],fit_data['weight'],l2,cfg)
        measured=metrics(development['win'],predict(head,development['state']),development['weight'],cfg['calibration_bins'])
        results.append(dict(l2=l2,development=measured))
    chosen=min(results,key=lambda r:r['development']['log_loss'])
    head=fit(data['state'][:,:dimensions],data['win'],data['weight'],chosen['l2'],cfg)
    return head,dict(trials=results,selected_l2=chosen['l2'],fit_games=len(np.unique(fit_data['episode'])),development_games=len(np.unique(development['episode'])))


def measure(head, data, cfg):
    p=np.full(len(data['win']),.5) if head is None else predict(head,data['state'])
    result=metrics(data['win'],p,data['weight'],cfg['calibration_bins'])
    result['games']=len(np.unique(data['episode'])); result['maps']=len(np.unique(data['map']))
    result['phases']={}
    bounds=cfg['phase_boundaries']
    for name,selected in (('early',data['round']<=bounds[0]),('middle',(data['round']>bounds[0])&(data['round']<=bounds[1])),('late',data['round']>bounds[1])):
        if selected.any():
            phase=subset(data,selected)
            result['phases'][name]=metrics(phase['win'],p[selected],phase['weight'],cfg['calibration_bins'])
    return result


def bootstrap(data, critic, baseline, cfg):
    maps=np.unique(data['map']); rng=np.random.default_rng(cfg['seed']); per_map=[]
    for name in maps:
        d=subset(data,data['map']==name)
        per_map.append(measure(critic,d,cfg)['brier']-measure(baseline,d,cfg)['brier'])
    differences=np.asarray(per_map); draws=rng.integers(0,len(maps),(cfg['bootstrap_samples'],len(maps)))
    interval=np.quantile(differences[draws].mean(axis=1),[.05,.95])
    return dict(unit='whole map, retaining both seats and all pairings',maps=len(maps),
        paired_brier_difference_by_map=dict(zip(maps.tolist(),differences.tolist())),
        mean_difference=float(differences.mean()),interval_90=interval.tolist(),
        superiority_supported=bool(interval[1]<0),note='Only four fresh maps; uncertainty is not estimated from independent frames')


def train():
    cfg=core.config()['stage4']; folder=model_root()
    if folder.exists():raise ValueError('Critic model version exists; choose a new name')
    planned=plan(); manifest=json.loads((root()/'manifest.json').read_text())
    if core.sha(root()/'plan.json') != manifest['plan_sha256']:raise ValueError('Critic data plan changed')
    folder.mkdir(parents=True)
    dataset.immutable(folder/'plan.json',planned|dict(dataset_manifest_sha256=core.sha(root()/'manifest.json')))
    started=time.perf_counter(); training=load('train')
    head,selection=select(training,cfg,FEATURES); baseline,baseline_selection=select(training,cfg,BASE_FEATURES)
    np.savez(folder/'critic.npz',coef=head['coef'],mean=head['mean'],scale=head['scale'],backbone=parent())
    np.savez(folder/'score-time.npz',coef=baseline['coef'],mean=baseline['mean'],scale=baseline['scale'])
    shutil.copyfile(core.ROOT/'models'/cfg['parent']/'weights.f32',folder/'actor.f32')
    # Freeze parameters before loading either outer validation partition.
    partitions={}
    for split in ('train','validation','fresh_validation'):
        data=training if split=='train' else load(split)
        partitions[split]={name:measure(h,data,cfg) for name,h in (('constant',None),('score_time',baseline),('critic',head))}
    fresh=load('fresh_validation'); uncertainty=bootstrap(fresh,head,baseline,cfg)
    test=partitions['fresh_validation']; passed=all(test['critic'][metric]<test[name][metric]
        for metric in ('brier','log_loss') for name in ('constant','score_time'))
    result=dict(schema=1,model=cfg['model'],training_complete=True,predictive_acceptance_passed=bool(passed),
        elapsed_seconds=time.perf_counter()-started,parent=cfg['parent'],parent_weights_sha256=cfg['parent_sha256'],
        actor_unchanged=core.sha(folder/'actor.f32')==cfg['parent_sha256'],backbone_frozen=True,
        frozen_backbone_parameters=cloning.N,trainable_head_parameters=len(head['coef']),critic_state_features=FEATURES,
        selection=selection,score_time_selection=baseline_selection,partitions=partitions,uncertainty=uncertainty,
        optimizer=dict(iterations=head['iterations'],final_gradient_max=head['final_gradient_max'],loss_history=head['loss_history']),
        exports={p.name:core.sha(p) for p in (folder/'critic.npz',folder/'score-time.npz',folder/'actor.f32')},
        dataset_manifest_sha256=core.sha(root()/'manifest.json'),plan_sha256=core.sha(folder/'plan.json'),
        source_sha256=hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        outer_validation_model_selections=0,ppo_started=False,confirmation_games=0,promoted=False,
        value_target='2 * P(eventual completed-game win under replay behavior mixture) - 1; undiscounted',
        limitations=['Offline behavior mixture; recalibrate/refit on on-policy trajectories for PPO',
            f"Training has only {len(np.unique(training['episode']))} independent games on {len(np.unique(training['map']))} maps; critic observations are local",
            'Stage 2 validation was already inspected; fresh validation uses four additional screening maps',
            'No actor update, macro repair, centralized hidden state, live upload or strength claim'])
    dataset.immutable(folder/'training.json',result); save('stage4-training.json',result)
    return {k:result[k] for k in ('model','training_complete','predictive_acceptance_passed','elapsed_seconds','actor_unchanged','partitions','uncertainty')}


def load_export(path):
    with np.load(path,allow_pickle=False) as data:
        head={k:data[k] for k in ('coef','mean','scale')};backbone=data['backbone']
    if head['coef'].shape!=(FEATURES+1,) or head['mean'].shape!=(FEATURES,) or head['scale'].shape!=(FEATURES,):
        raise ValueError('Invalid exported critic shape')
    if backbone.shape!=(cloning.N,) or any(not np.isfinite(v).all() for v in (*head.values(),backbone)) or np.any(head['scale']<=0):
        raise ValueError('Nonfinite or invalid exported critic')
    return head,backbone


def evaluate_observations(observations,terrain,export_path=None):
    """Training-time live value API; this does not change the C++ actor."""
    head,backbone=load_export(export_path or model_root()/'critic.npz')
    encoded=[policy.encode(o,terrain) for o in observations]
    state=encode(backbone,[e['features'] for e in encoded],[e['candidates'] for e in encoded],
                 [e['mask'] for e in encoded],[o['actor']['team'] for o in observations])
    probability=predict(head,state)
    return dict(probability=probability,value=2*probability-1)


def audit():
    """Recompute all derived states/labels from hashed actor-scoped replay records."""
    planned=plan();manifest=json.loads((root()/'manifest.json').read_text());w=parent();actual=[]
    for split in ('train','validation'):
        for episode,path in dataset.shards(split):
            actual.append(extract(episode,path.parent,w))
    rejected=[]
    for episode in planned['extra_training_episodes']+planned['fresh_validation_episodes']:
        source=root()/'fresh'/episode['episode_id']
        full=json.loads((source/'episode.json').read_text())
        # Identity and terminal/fault provenance cannot be supplied by a changed metadata file.
        for key,value in episode.items():
            if full.get(key)!=value:raise ValueError('Fresh critic episode identity changed')
        raw=json.loads((source/'stats.json').read_text());summary=stats.summarize(raw)
        if raw['match']['engineBuildHash']!=episode['runtime']['engine_build_hash'] or raw['match']['mapHash']!=episode['map_sha256']:
            raise ValueError('Fresh critic runtime or map changed')
        if any(t['faults'] or t['fuel_exhausted'] for t in summary['teams'].values()):
            if full['status']=='quarantined' and episode['split']=='train':
                rejected.append(full);continue
            raise ValueError('Faulty fresh game cannot supply critic targets')
        expected=dict(outcome=summary['outcome'],round=summary['rounds'],banks=[summary['teams'][t]['gems'] for t in ('teamA','teamB')])
        if full['terminal']!=expected:raise ValueError('Fresh critic terminal differs from release runner')
        actual.append(extract(full,source,w))
    if actual!=manifest['episodes'] or rejected!=manifest['extra_training_quarantine']:raise ValueError('Critic manifest/reconstruction differs')
    return save('stage4-audit.json',dict(passed=True,games=len(actual),rows=sum(e['rows'] for e in actual),
        manifest_sha256=core.sha(root()/'manifest.json'),parent_weights_sha256=planned['parent_weights_sha256'],
        recomputed_actor_states=True,complete_binary_targets=True,confirmation_games=0,
        source_sha256=hashlib.sha256(Path(__file__).read_text().encode()).hexdigest()))


def ready():
    from . import stage1,stage3
    stage3.ready()
    planned=plan();folder=model_root();training=json.loads((folder/'training.json').read_text())
    audit_result=json.loads((core.ROOT/'results/stage4-audit.json').read_text())
    source_sha=hashlib.sha256(Path(__file__).read_text().encode()).hexdigest()
    if source_sha!=training['source_sha256'] or source_sha!=audit_result['source_sha256']:
        raise ValueError('Critic training/audit source changed')
    digest=core.sha(root()/'manifest.json')
    if digest!=training['dataset_manifest_sha256'] or digest!=audit_result['manifest_sha256'] or not audit_result['passed']:
        raise ValueError('Critic dataset audit changed')
    if core.sha(folder/'plan.json')!=training['plan_sha256']:
        raise ValueError('Critic model plan changed')
    model_plan=json.loads((folder/'plan.json').read_text())
    if model_plan['config']!=planned['config']:
        raise ValueError('Critic settings changed after model selection')
    for name,digest in training['exports'].items():
        if core.sha(folder/name)!=digest:raise ValueError('Critic export changed')
    head,backbone=load_export(folder/'critic.npz')
    if not np.array_equal(backbone,parent()) or core.sha(folder/'actor.f32')!=planned['parent_weights_sha256']:
        raise ValueError('Critic changed its BC starting actor')
    fresh=load('fresh_validation');measured=measure(head,fresh,core.config()['stage4'])
    for field in ('log_loss','brier','expected_calibration_error'):
        if abs(measured[field]-training['partitions']['fresh_validation']['critic'][field])>1e-7:
            raise ValueError('Export does not reproduce held-out critic metrics')
    # Independent float64 accumulation validates the exported float32 readout.
    normalized=(fresh['state']-head['mean'])/head['scale']
    reference=sigmoid(normalized.astype(np.float64)@head['coef'][:-1].astype(np.float64)+float(head['coef'][-1]))
    error=float(np.max(np.abs(reference-predict(head,fresh['state']))))
    if error>1e-6:raise ValueError('Critic export probability parity failed')
    result=dict(passed=training['predictive_acceptance_passed'],pipeline_checks_passed=True,stage=4,
        next_stage=5 if training['predictive_acceptance_passed'] else 4,model=training['model'],
        parent=training['parent'],parent_weights_sha256=training['parent_weights_sha256'],actor_unchanged=True,
        predictive_acceptance_passed=training['predictive_acceptance_passed'],fresh_validation_games=measured['games'],
        fresh_validation_maps=measured['maps'],fresh_brier=measured['brier'],fresh_log_loss=measured['log_loss'],
        exported_probability_max_error=error,bootstrap=training['uncertainty'],
        critic_in_actor_runtime=False,ppo_started=False,confirmation_games=0,promoted=False,
        sources=stage1.sources())
    return save('stage4-ready.json',result)

"""Immutable Stage 2 baseline episodes and actor-only demonstration shards."""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
from threading import Timer
import zipfile

import numpy as np

from . import core, mapgen, policy, replay, stats


def canonical(action):
    return {k:v for k,v in action.items() if k!='reason'}


def proposal_label(action,encoded):
    if action.get('reason',0)!=0:return None
    action=canonical(action)
    return next((i for i,a in enumerate(encoded['actions']) if a==action and encoded['mask'][i]),None)


def completed_outcome(terminal):
    if terminal.get('outcome') not in ('teamA','teamB') or not 1<=terminal.get('round',0)<=2000:
        raise ValueError('Replay has no complete native outcome')
    return terminal['outcome']


def validate_splits(episodes):
    train=[e for e in episodes if e['split']=='train'];val=[e for e in episodes if e['split']=='validation']
    if {e['map_sha256'] for e in train}&{e['map_sha256'] for e in val}:raise ValueError('Training/validation map leakage')
    if {x for e in train for x in e['lineages']}&{x for e in val for x in e['lineages']}:raise ValueError('Training/validation lineage leakage')
    if {e['family'] for e in train if 'family' in e}&{e['family'] for e in val if 'family' in e}:raise ValueError('Training/validation map family leakage')


def quarantine_pairs(results):
    failed={(r['map_sha256'],tuple(sorted(r['wasm_sha256']))) for r in results if r['status']=='quarantined'}
    for row in results:
        if (row['map_sha256'],tuple(sorted(row['wasm_sha256']))) in failed:row['status']='quarantined'


def root():
    return core.ROOT/'datasets'/core.config()['stage2']['dataset']


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def immutable(path,value):
    if path.exists() and json.loads(path.read_text())!=value:raise ValueError(f'Refusing to mutate frozen dataset artifact: {path}')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def plan():
    cfg=core.config()['stage2'];profile=core.runtime_identity();episodes=[]
    family_maps={i:[] for i in range(4)}
    for i,name in enumerate(core.config()['maps']['screen']):
        family=mapgen.layout(mapgen.seed_for('screen',core.config()['stage1']['screen_seed'],i))['family']
        family_maps[family].append(name)
    for split,families,num in [('train',cfg['train_families'],cfg['maps_per_train_family']),
                               ('validation',cfg['validation_families'],cfg['validation_maps'])]:
        for family in families:
            for name in family_maps[family][:num]:
                for a,b in cfg[f'{split}_pairs']:
                    for x,y in ([(a,b),(b,a)] if a!=b else [(a,b)]):
                        versions=[core.version(n) for n in (x,y)]
                        rec=dict(split=split,map=name,map_sha256=core.sha(core.map_path(name)),family=family,
                                 names=[x,y],wasm_sha256=[v.meta['wasm_sha256'] for v in versions],
                                 lineages=[cfg['lineages'][n] for n in (x,y)],runtime=profile,
                                 teacher_teams=[i for i,n in enumerate((x,y)) if n in cfg[f'{split}_teachers']])
                        rec['episode_id']=digest(rec)[:24];episodes.append(rec)
    validate_splits(episodes)
    result=dict(schema=1,name=cfg['dataset'],episodes=episodes,sampling=dict(round_stride=cfg['round_stride'],
                max_actions_per_turn=cfg['max_actions_per_turn'],phase='(round - 1) mod stride == 0'),
                actor_schema=1,model_shape=[policy.G,policy.K,policy.C,policy.H],
                sealed_maps=core.config()['maps']['confirm'],partition_policy='whole map family and both actor/opponent lineages')
    immutable(root()/'plan.json',result)
    (core.ROOT/'results/stage2-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def raw_bytes(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:return z.read('replay.repl26a')
    return path.read_bytes()


def extract(replay_file,map_name,destination,expected=None,teacher_teams=(0,1)):
    """Stream bounded actor observations; completion is checked by native WASM before rows emit."""
    cfg=core.config()['stage2'];blob=raw_bytes(replay_file)
    actions=replay.decode(blob,core.map_path(map_name).read_bytes())
    destination.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination) as tmp:
        tmp=Path(tmp);(tmp/'raw.repl26a').write_bytes(blob)
        request=dict(replay=str(tmp/'raw.repl26a'),map=str(core.map_path(map_name)),actions=actions,
                     round_stride=cfg['round_stride'],max_actions_per_turn=cfg['max_actions_per_turn'])
        (tmp/'request.json').write_text(json.dumps(request),encoding='utf-8')
        counts=Counter();coverage=Counter();F=[];C=[];M=[];Y=[];T=[];I=[];outcomes=[];meta=None;finished=False;rows=0
        stderr=tmp/'stderr.txt'
        with stderr.open('w',encoding='utf-8') as errors, gzip.open(tmp/'decisions.jsonl.gz','wt',encoding='utf-8') as output:
            process=subprocess.Popen([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/replay-engine.mjs'),
                                      str(mapgen.engine_path()),str(tmp/'request.json')],cwd=core.ROOT,env=core.ENV,
                                     stdout=subprocess.PIPE,stderr=errors,text=True,encoding='utf-8')
            watchdog=Timer(core.TIMEOUT,process.kill);watchdog.start()
            try:
                for line in process.stdout:
                    row=json.loads(line)
                    if row['type']=='metadata':
                        meta=row;completed_outcome(meta['terminal'])
                        if expected and meta['terminal']!=expected:raise ValueError('Native replay does not match release terminal statistics')
                        if row['engine_sha256']!=core.config()['stage1']['engine_wasm_sha256']:raise ValueError('Wrong replay rules module')
                    elif row['type']=='complete':finished=True
                    elif row['type']=='decision':
                        rows+=1;o=row['observation'];encoded=policy.encode(o,meta['terrain'])
                        action=row['action'];label=proposal_label(action,encoded)
                        # Exact replay observations are preserved, but full-turn history can exceed our certified two-pass actor.
                        eligible=(o['actor']['team'] in teacher_teams and label is not None and row['micro_action'] and row['micro_decision_index']<2
                                  and bool(o['self']['state']&1) and action.get('reason',0)==0)
                        counts[action['kind']]+=1;coverage['covered' if label is not None else 'unsupported']+=1
                        coverage['eligible']+=int(eligible);coverage['rows']+=1
                        row.update(candidate_label=label,bc_eligible=eligible,encoding=encoded,
                                   result=dict(native_error_code=0 if action.get('reason',0)==0 else None,
                                               boolean_return=None,source='serialized_input; boolean return is not recorded'))
                        output.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n')
                        if eligible:
                            F.append(encoded['features']);C.append(encoded['candidates']);M.append(encoded['mask']);Y.append(label)
                            T.append(o['actor']['team']);I.append(row['input']);outcomes.append(int(meta['terminal']['outcome']==('teamA' if o['actor']['team']==0 else 'teamB')))
                code=process.wait(timeout=30)
            except BaseException:
                process.kill();process.wait();raise
            finally:watchdog.cancel();process.stdout.close()
        if code or not finished:raise ValueError('Native replay extraction failed: '+stderr.read_text()[-1800:])
        if not rows:raise ValueError('Replay yielded no actor demonstrations')
        np.savez_compressed(tmp/'bc.npz',features=np.asarray(F,dtype=np.float32).reshape(-1,policy.G),
             candidates=np.asarray(C,dtype=np.float32).reshape(-1,policy.K,policy.C),mask=np.asarray(M,dtype=np.bool_).reshape(-1,policy.K),
             label=np.asarray(Y,dtype=np.int64),team=np.asarray(T,dtype=np.uint8),input=np.asarray(I,dtype=np.int64),
             win=np.asarray(outcomes,dtype=np.uint8))
        result=dict(schema=1,records=rows,eligible=len(Y),action_counts=dict(counts),coverage=dict(coverage),
                    terminal=meta['terminal'],replay_sha256=hashlib.sha256(blob).hexdigest(),
                    engine_wasm_sha256=meta['engine_sha256'],map_sha256=core.sha(core.map_path(map_name)),
                    unavailable_fields=['guest_private_ram','shared_memory_writes','native_boolean_returns'])
        for name in ('decisions.jsonl.gz','bc.npz'):
            target=destination/name
            if target.exists():raise ValueError('Refusing to overwrite an existing demonstration shard')
            (tmp/name).replace(target);result[name+'_sha256']=core.sha(target)
        immutable(destination/'summary.json',result)
        return result


def collect_one(episode):
    folder=root()/'episodes'/episode['episode_id'];folder.mkdir(parents=True,exist_ok=True)
    if (folder/'summary.json').exists():return json.loads((folder/'summary.json').read_text())|episode|dict(status='admitted')
    a,b=[core.version(n) for n in episode['names']]
    if (folder/'stats.json').exists():
        raw=json.loads((folder/'stats.json').read_text());error=''
        stats.validate(raw)
        if raw['match']['engineBuildHash']!=episode['runtime']['engine_build_hash'] or raw['match']['mapHash']!=episode['map_sha256']:
            raise ValueError('Cached raw episode provenance mismatch')
    else:raw,error=core.run_game(a,b,core.map_path(episode['map']),str(folder),profile=episode['runtime'])
    if raw is None:raise ValueError(error)
    compact=stats.summarize(raw)
    if any(t['faults'] or t['fuel_exhausted'] for t in compact['teams'].values()):
        rejected=dict(status='quarantined',error='Baseline release faults or fuel exhaustion',records=0,eligible=0,
                      diagnostics={t:{k:v[k] for k in ('faults','fuel_exhausted')} for t,v in compact['teams'].items()})
        immutable(folder/'quarantine.json',rejected)
        return rejected|episode
    replay_file=max(folder.glob('*.repl26a'),key=lambda p:p.stat().st_mtime)
    expected=dict(outcome=compact['outcome'],round=compact['rounds'],banks=[compact['teams'][t]['gems'] for t in ('teamA','teamB')])
    result=extract(replay_file,episode['map'],folder,expected,episode['teacher_teams'])
    immutable(folder/'episode.json',episode)
    return result|episode|dict(status='admitted')


def collect():
    planned=plan();results=[]
    with ThreadPoolExecutor(core.config()['stage2']['jobs']) as pool:
        for result in pool.map(collect_one,planned['episodes']):
            results.append(result);print(f"{len(results)}/{len(planned['episodes'])}: {result['split']} {result['status']} {result['records']} frames, {result['eligible']} eligible",flush=True)
    validate_splits(results)
    quarantine_pairs(results)
    by_split={}
    for split in ('train','validation'):
        selected=[r for r in results if r['split']==split and r['status']=='admitted']
        eligible=sum(r['eligible'] for r in selected)
        if eligible<core.config()['stage2'][f'min_eligible_{split}']:raise ValueError('Not enough eligible demonstrations')
        counts=Counter();coverage=Counter()
        for r in selected:counts.update(r['action_counts']);coverage.update(r['coverage'])
        by_split[split]=dict(games=len(selected),records=sum(r['records'] for r in selected),eligible=eligible,
                            action_counts=dict(counts),coverage=dict(coverage))
    if {r['map_sha256'] for r in results if r['status']=='admitted'}!={r['map_sha256'] for r in results}:
        raise ValueError('Quarantine removed all demonstrations for a reserved map')
    result=dict(schema=1,passed=True,dataset=planned['name'],plan_sha256=core.sha(root()/'plan.json'),
                planned_games=len(results),quarantined_games=sum(r['status']=='quarantined' for r in results),
                splits=by_split,episodes=results,stage3_started=False)
    immutable(root()/'manifest.json',result)
    (core.ROOT/'results/stage2-dataset.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def shards(split):
    manifest=json.loads((root()/'manifest.json').read_text())
    for episode in manifest['episodes']:
        if episode['split']==split and episode['status']=='admitted':
            path=root()/'episodes'/episode['episode_id']/'bc.npz'
            if core.sha(path)!=episode['bc.npz_sha256']:raise ValueError('Training shard hash mismatch')
            yield episode,path


def run_replay_engine(blob,map_name,actions,**options):
    scratch=core.ROOT/'.cambc';scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        tmp=Path(tmp);(tmp/'raw.repl26a').write_bytes(blob)
        request=dict(replay=str(tmp/'raw.repl26a'),map=str(core.map_path(map_name)),actions=actions,
                     round_stride=1,max_actions_per_turn=64,**options)
        (tmp/'request.json').write_text(json.dumps(request),encoding='utf-8')
        process=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/replay-engine.mjs'),
                                str(mapgen.engine_path()),str(tmp/'request.json')],cwd=core.ROOT,env=core.ENV,
                               capture_output=True,text=True,encoding='utf-8',timeout=core.TIMEOUT)
        if process.returncode:raise ValueError(process.stderr[-2000:])
        return [json.loads(line) for line in process.stdout.splitlines()]


def proof():
    """Independently compare replay decoding/reconstruction with release-bot logs."""
    from . import stage1
    checks=[]
    for name in core.config()['stage1']['parity_maps']:
        folder=core.ROOT/'.cambc/stage1'/name.replace('/','_')
        replay_file=max(folder.glob('*.repl26a'),key=lambda p:p.stat().st_mtime)
        traces=stage1.traces(replay_file);blob=raw_bytes(replay_file)
        actions=replay.decode(blob,core.map_path(name).read_bytes())
        records=run_replay_engine(blob,name,actions,max_round=80)
        seen=set();actual={}
        for row in records:
            if row['type']!='decision':continue
            o=row['observation'];key=(o['actor']['round'],o['actor']['champion']);trace=traces[key]
            if key not in seen:
                encoded=policy.encode(o,records[0]['terrain'])
                for field in ('features','candidates','mask'):
                    if not stage1.close_float(encoded[field],trace[field]):raise ValueError(f'Replay observation parity failed: {key} {field}')
                if sorted(o['moves'])!=sorted(trace['moves']):raise ValueError('Replay movement parity failed')
                seen.add(key)
            if row['action']['kind']!='wait':actual.setdefault(key,[]).append(canonical(row['action']))
        for key,trace in traces.items():
            expected=[a['action'] for a in trace['actions'] if a['code']==0]
            if actual.get(key,[])!=expected:raise ValueError(f'Decoded replay action differs from SDK trace: {key}')
        if len(seen)!=len(traces):raise ValueError('Incomplete replay parity coverage')
        checks.append(dict(map=name,observations=len(seen),replay_sha256=hashlib.sha256(blob).hexdigest()))
    result=dict(passed=True,maps=checks,observations=sum(c['observations'] for c in checks),
                memory_contract='unrecorded guest memory is null; actor-v1 features do not use it')
    (core.ROOT/'results/stage2-replay-proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


ONLINE_GROUPS=[
    ('9b05598c-5761-4a4c-a4b9-4feceec94e7a','Nyx',0,['00ambush','00collision','00corners','00eight','00lanes'],[1135,1124,1176,1167,930],[[442,1001],[146,1011],[695,1003],[505,1017],[132,1008]]),
    ('bfce0895-aad8-4129-aa9d-0b8f6c92e358','Nyx',1,['00ambush','00collision','00corners','00eight','00lanes'],[1195,1239,1087,1051,932],[[1004,545],[1009,202],[1016,424],[1020,329],[1003,131]]),
    ('a71ac20b-ce61-4461-a1e7-582339cc67c4','Sneaky Bush Campers',0,['00elkring','00expanse','00fragment','00monolith','00interlock'],[763,1019,1709,979,1413],[[330,1012],[693,1037],[158,1014],[262,1004],[372,1001]]),
    ('cc9471f4-2f67-438f-bddb-96ae139eb391','Sneaky Bush Campers',1,['00elkring','00expanse','00fragment','00monolith','00interlock'],[809,1031,1501,983,1245],[[1012,220],[1026,514],[1001,80],[1003,247],[1020,167]])]


def online():
    result=[]
    source=core.ROOT/'datasets/stage2-v1/raw/online'
    for group,opponent,seat,maps,rounds,banks in ONLINE_GROUPS:
        archive=source/f'match-group-{group}.zip'
        with zipfile.ZipFile(archive) as outer:
            for i,entry in enumerate(sorted(outer.namelist())):
                with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as inner:blob=inner.read('replay.repl26a')
                actions=replay.decode(blob,core.map_path(maps[i]).read_bytes())
                native=run_replay_engine(blob,maps[i],actions,metadata_only=True)[0]
                expected=dict(outcome='teamB' if seat==0 else 'teamA',round=rounds[i],banks=banks[i])
                if native['terminal']!=expected:raise ValueError('Online replay differs from observed website terminal')
                result.append(dict(group_id=group,url='https://2026a.battlecode.co.uk/game/match-groups/'+group,
                    opponent=opponent,our_version=76,our_seat=seat,map=maps[i],terminal=expected,
                    statistics=native['statistics'],input_actions=dict(Counter(a['kind'] for a in actions)),
                    replay_sha256=hashlib.sha256(blob).hexdigest(),download_sha256=core.sha(archive),
                    engine_build_hash=None,decoder_engine_sha256=native['engine_sha256'],
                    partition='external_diagnostics',training_eligible=False,
                    reason='Download omits exact server build/submission WASM identity and guest memory writes'))
    output=dict(schema=1,passed=True,games=len(result),groups=4,our_wins=0,our_losses=20,
                confirmation_games=0,our_submission_changed=False,matches=result)
    (core.ROOT/'results/stage2-online.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    return output


def audit():
    manifest=json.loads((root()/'manifest.json').read_text());validate_splits(manifest['episodes'])
    proof_result=json.loads((core.ROOT/'results/stage2-replay-proof.json').read_text())
    if not proof_result['passed'] or proof_result['observations']!=2560:raise ValueError('Replay importer lacks its release proof')
    report={}
    for split in ('train','validation'):
        rows=0;eligible=0;actions=Counter();drafts=Counter();seats=Counter();wins=Counter();unsupported=Counter()
        for episode,path in shards(split):
            folder=path.parent
            terrain_file=folder/'terrain.json'
            if not terrain_file.exists():
                source=max(folder.glob('*.repl26a'),key=lambda p:p.stat().st_mtime)
                blob=raw_bytes(source);decoded=replay.decode(blob,core.map_path(episode['map']).read_bytes())
                immutable(terrain_file,run_replay_engine(blob,episode['map'],decoded,metadata_only=True)[0]['terrain'])
            terrain=json.loads(terrain_file.read_text())
            if core.sha(folder/'decisions.jsonl.gz')!=episode['decisions.jsonl.gz_sha256']:raise ValueError('Observation shard hash mismatch')
            with np.load(path,allow_pickle=False) as data:
                if data['features'].shape!=(len(data['label']),24) or data['candidates'].shape!=(len(data['label']),16,12):raise ValueError('Invalid model tensor shape')
                if not np.isfinite(data['features']).all() or not np.isfinite(data['candidates']).all():raise ValueError('Nonfinite model tensor')
                if not data['mask'][np.arange(len(data['label'])),data['label']].all():raise ValueError('Masked teacher label')
                seats.update(data['team'].tolist());wins.update(data['win'].tolist());n=len(data['label'])
                tensors={k:data[k] for k in data.files}
            kept=0
            with gzip.open(folder/'decisions.jsonl.gz','rt',encoding='utf-8') as f:
                for line in f:
                    row=json.loads(line);o=row['observation'];encoded=policy.encode(o,terrain)
                    if encoded!=row['encoding']:raise ValueError('Actor features changed on recomputation')
                    label=proposal_label(row['action'],encoded)
                    if label!=row['candidate_label']:raise ValueError('Unsupported action was relabelled')
                    rows+=1
                    if row['bc_eligible']:
                        if o['actor']['team'] not in episode['teacher_teams'] or row['micro_decision_index']>=2:raise ValueError('Unqualified teacher row')
                        for field in ('features','candidates','mask'):
                            if not np.array_equal(tensors[field][kept],np.asarray(encoded[field],dtype=tensors[field].dtype)):
                                raise ValueError('Actor rows and model tensor values differ')
                        if int(tensors['label'][kept])!=label or int(tensors['input'][kept])!=row['input'] or int(tensors['team'][kept])!=o['actor']['team']:
                            raise ValueError('Actor rows and model labels differ')
                        kept+=1;actions[row['action']['kind']]+=1;drafts[o['self']['type']]+=1
                    elif label is None:unsupported[row['action']['kind']]+=1
            if kept!=n or kept!=episode['eligible']:raise ValueError('NPZ and actor row count differ')
            eligible+=kept
        report[split]=dict(records=rows,eligible=eligible,eligible_actions=dict(actions),body_types=dict(drafts),
                           seats=dict(seats),terminal_labels=dict(wins),unsupported_actions=dict(unsupported))
    result=dict(schema=1,passed=True,planned_games=manifest['planned_games'],quarantined_games=manifest['quarantined_games'],
                admitted_games=sum(e['status']=='admitted' for e in manifest['episodes']),splits=report,
                map_and_lineage_leakage=False,confirmation_games=0,stage3_started=False,
                manifest_sha256=core.sha(root()/'manifest.json'))
    result['validator_sources']={p:hashlib.sha256((core.ROOT/p).read_text().encode()).hexdigest()
                                for p in ('lab/dataset.py','lab/replay.py','lab/replay-engine.mjs','lab/policy.py','lab/engine.mjs')}
    (core.ROOT/'results/stage2-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def ready():
    from . import stage1
    stage1.ready()
    plan()  # Reconstructs settings/identities and rejects changes to the immutable schedule.
    result=json.loads((core.ROOT/'results/stage2-audit.json').read_text())
    for file,expected in result['validator_sources'].items():
        if hashlib.sha256((core.ROOT/file).read_text().encode()).hexdigest()!=expected:
            raise ValueError('Dataset validator changed; rerun the audit')
    if core.sha(root()/'manifest.json')!=result['manifest_sha256']:raise ValueError('Dataset manifest changed')
    online_result=json.loads((core.ROOT/'results/stage2-online.json').read_text())
    if not online_result['passed'] or online_result['games']!=20:raise ValueError('Sparring replay audit is incomplete')
    for split in ('train','validation'):
        if sum(episode['eligible'] for episode,_ in shards(split))!=result['splits'][split]['eligible']:
            raise ValueError('Admitted dataset counts changed')
    output=dict(passed=True,stage=2,admitted_games=result['admitted_games'],quarantined_games=result['quarantined_games'],
                train_samples=result['splits']['train']['eligible'],validation_samples=result['splits']['validation']['eligible'],
                live_sparring_games=online_result['games'],stage3_started=False,manifest_sha256=result['manifest_sha256'])
    (core.ROOT/'results/stage2-ready.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    return output

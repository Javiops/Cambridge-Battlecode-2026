"""Frozen PPO actor deployment: independent native replay parity and release fuel gates."""
from __future__ import annotations
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import zipfile
import numpy as np
from . import core, dataset, mapgen, policy, replay, stage1, stage3, stats


def next_random(seed):
    return (1664525*seed+1013904223)&0xffffffff


def map_seed(terrain):
    seed=2166136261
    values=[terrain['width'],terrain['height']]
    for tag,kind in enumerate(('walls','holes','altars'),1):
        values.append(tag)
        packed=bytearray((terrain['width']*terrain['height']+7)//8)
        for x,y in terrain[kind]:
            k=y*terrain['width']+x;packed[k//8]|=1<<(k%8)
        values.extend(packed)
    for value in values:seed=((seed^value)*16777619)&0xffffffff
    return seed


def parse_log(data):
    chunks=[]
    for line in data.replace(b'\0',b'').splitlines():
        if line[:4] not in (b'S6D!',b'S6F!'):raise ValueError('Unknown runtime record')
        try:payload=bytes.fromhex(line[4:].decode('ascii'))
        except (ValueError,UnicodeError) as exc:raise ValueError('Invalid runtime hex') from exc
        expected=20 if line[:4]==b'S6F!' else (1000 if len(payload)>=56 and struct.unpack_from('<I',payload,48)[0]==1 else 56)
        if len(payload)!=expected:raise ValueError('Truncated runtime record')
        chunks.append(line[:4]+payload)
    data=b''.join(chunks)
    decisions={};footers={};pos=0
    while pos<len(data):
        tag=data[pos:pos+4];pos+=4
        try:
            if tag==b'S6D!':
                row=struct.unpack_from('<14I',data,pos);pos+=56
                r,c,d,kind,pick,a,b,before,after,controller,kernel,used,probe,budget=row
                key=f'{r}/{c}/{d}'
                if key in decisions:raise ValueError('Duplicate runtime decision')
                result=dict(round=r,champion=c,decision=d,kind=kind,pick=pick if pick!=0xffffffff else -1,a=a,b=b,
                            before=before,after=after,controller=controller,kernel=kernel,used=used,budget=budget)
                if probe:
                    if probe!=1:raise ValueError('Invalid probe flag')
                    n=policy.G+policy.K*policy.C
                    numbers=np.frombuffer(data,dtype='<f4',count=n,offset=pos);pos+=n*4
                    result['features']=numbers[:policy.G].tolist();result['candidates']=numbers[policy.G:].reshape(policy.K,policy.C).tolist()
                    result['mask']=np.frombuffer(data,dtype='u1',count=policy.K,offset=pos).astype(bool).tolist();pos+=policy.K
                    result['scores']=np.frombuffer(data,dtype='<f4',count=policy.K,offset=pos).tolist();pos+=policy.K*4
                decisions[key]=result
            elif tag==b'S6F!':
                r,c,budget,used,count=struct.unpack_from('<5I',data,pos);pos+=20;key=f'{r}/{c}'
                if key in footers:raise ValueError('Duplicate runtime turn')
                footers[key]=dict(budget=budget,used=used,count=count)
            else:raise ValueError('Unknown/truncated runtime trace')
        except (struct.error,ValueError) as exc:
            raise ValueError('Invalid runtime trace at byte '+str(pos)) from exc
    return decisions,footers


def fuel_summary(decisions,footers,ordinary_limit,initial_limit):
    expected=Counter('/'.join(k.split('/')[:2]) for k in decisions)
    if set(expected)!=set(footers) or any(expected[k]!=v['count'] for k,v in footers.items()):
        raise ValueError('Missing runtime decision or turn footer')
    if not footers:raise ValueError('Empty runtime trace')
    for k,f in footers.items():
        if f['budget'] not in (100000,200000) or not 1<=f['count']<=2:raise ValueError('Invalid runtime turn envelope')
        if f['used']>(initial_limit if f['budget']==200000 else ordinary_limit):raise ValueError('Runtime fuel headroom failed: '+k)
        for i in range(f['count']):
            d=decisions[f'{k}/{i}']
            if not 0<=d['controller']<=d['kernel']<=d['used']<=f['used'] or d['budget']!=f['budget']:raise ValueError('Nonmonotone runtime fuel accounting')
    initial=[f['used'] for f in footers.values() if f['budget']==200000]
    ordinary=[f['used'] for f in footers.values() if f['budget']==100000]
    return dict(turns=len(footers),decisions=len(decisions),ordinary_turns=len(ordinary),initial_turns=len(initial),
                ordinary_max=max(ordinary,default=0),first_turn_max=max(initial,default=0),
                kernel_max=max(d['kernel'] for d in decisions.values()),controller_max=max(d['controller'] for d in decisions.values()))


def cfg():return core.config()['stage6']
def save(name,value):return stage3.save('stage6-'+name+'.json',value)


def official_fuel(data,footers,ordinary_limit,initial_limit):
    if len(data)<77 or data[:11]!=b'a62leuf\0\0\0\1' or (len(data)-77)%8:raise ValueError('Invalid official fuel stream')
    limits=[struct.unpack_from('<4Q',data,o) for o in (13,45)]
    if any(v[2:]!=(200000,100000) for v in limits):raise ValueError('Unexpected official fuel budgets')
    values=list(struct.unpack_from('<'+'Q'*((len(data)-77)//8),data,77))
    # Draft fuel is first; gameplay footers cover each later turn in execution order.
    drafts=len(values)-len(footers)
    if drafts not in (3,4,5):raise ValueError('Official fuel/turn coverage differs')
    initial=[];ordinary=[]
    for (key,footer),used in zip(footers.items(),values[drafts:]):
        limit=initial_limit if footer['budget']==200000 else ordinary_limit
        if used<footer['used'] or used>limit:raise ValueError(f'Official total-turn fuel gate failed {key}: {used}')
        (initial if footer['budget']==200000 else ordinary).append(used)
    return dict(ordinary_max=max(ordinary,default=0),initial_max=max(initial,default=0),turns=len(footers),
                draft_turns=drafts,includes_trace_and_end_turn=True)


def sources():
    import hashlib
    paths=list((core.ROOT/'bots/ppo-actor/src').glob('*'))+[core.ROOT/'lab/stage6.py',core.ROOT/'lab/runtime-check.mjs',core.ROOT/'lab/ppo-actor.mjs',core.ROOT/'lab/engine.mjs',core.ROOT/'lab.toml']
    return {p.relative_to(core.ROOT).as_posix():hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest() for p in paths}


def parent():
    path=core.ROOT/cfg()['checkpoint'];w=np.fromfile(path/'weights.f32',dtype='<f4')
    if core.sha(path/'weights.f32')!=cfg()['weights_sha256'] or w.shape!=(305,) or not np.isfinite(w).all():raise ValueError('Wrong PPO model')
    if (path/'weights.h').read_bytes()!=(core.ROOT/'bots/ppo-actor/src/weights.h').read_bytes():raise ValueError('C++ PPO header changed')
    return w


def prepare():
    parent();name=cfg()['version'];bot=core.ROOT/'bots/ppo-actor'
    if not (core.ARCHIVE/name).exists():core.freeze('bots/ppo-actor',name,parent='bc-actor-v1',note='Stage 6 frozen PPO policy and unchanged farming/banking controller; runtime integration only')
    v=core.version(name)
    if {p.name:p.read_bytes() for p in (bot/'src').iterdir()}!={p.name:p.read_bytes() for p in (v.wasm.parent/'src').iterdir()}:raise ValueError('Frozen PPO runtime sources changed')
    return v


def run_release(name,opponent,seat,out,version):
    """High log cap is necessary: every deployed decision and turn is audited."""
    out.mkdir(parents=True,exist_ok=True);mp=core.map_path(name);profile=core.runtime_identity()
    identity=dict(map_sha256=core.sha(mp),actor_sha256=core.sha(version.wasm),opponent_sha256=core.sha(opponent.wasm),seat=seat,runtime=profile)
    if (out/'identity.json').exists() and json.loads((out/'identity.json').read_text())==identity and (out/'stats.json').exists():
        raw=json.loads((out/'stats.json').read_text());stats.validate(raw);return raw
    a,b=(version,opponent) if seat==0 else (opponent,version)
    cmd=[core.CLI,'run',str(a.wasm),str(b.wasm),'--map',str(mp),'-o',str(out),'--statistics',str(out/'stats.json'),'--json','--release','--log-limit','100000000']
    r=subprocess.run(cmd,cwd=core.ROOT,env=core.ENV,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=core.TIMEOUT)
    (out/'runner.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
    if r.returncode or not (out/'stats.json').exists():raise ValueError('Release match failed: '+r.stdout[-1000:]+r.stderr[-1000:])
    raw=json.loads((out/'stats.json').read_text());stats.validate(raw)
    if raw['match']['engineBuildHash']!=profile['engine_build_hash']:raise ValueError('Wrong release runtime')
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8');return raw


def audit_game(name,opponent_name,seat,version=None):
    version=version or prepare();opponent=version if opponent_name==cfg()['version'] else core.version(opponent_name)
    out=core.ROOT/'.cambc/stage6'/f"{name.replace('/','_')}-{opponent_name}-{seat}"
    raw=run_release(name,opponent,seat,out,version);summary=stats.summarize(raw)
    if any(t['faults'] or t['fuel_exhausted'] for t in summary['teams'].values()):raise ValueError('Release runtime fault/fuel exhaustion: '+str(out))
    replay_file=max((p for p in out.glob('*.repl26a') if p.name!='raw.repl26a'),key=lambda p:p.stat().st_mtime)
    with zipfile.ZipFile(replay_file) as z:
        decisions,footers=parse_log(z.read('team-a.stdout' if seat==0 else 'team-b.stdout'))
        full_fuel=official_fuel(z.read('team-a.fuel' if seat==0 else 'team-b.fuel'),footers,cfg()['max_turn_fuel'],cfg()['max_initial_fuel'])
    fuel=fuel_summary(decisions,footers,cfg()['max_turn_fuel'],cfg()['max_initial_fuel'])
    blob=dataset.raw_bytes(replay_file);actions=replay.decode(blob,core.map_path(name).read_bytes())
    (out/'raw.repl26a').write_bytes(blob)
    request=dict(replay=str(out/'raw.repl26a'),map=str(core.map_path(name)),actions=actions,traces=decisions,footers=footers,seat=seat,
                 weights=str(core.ROOT/cfg()['checkpoint']/'weights.f32'),controller=core.config()['stage5']['controller'],picks=core.config()['stage5']['picks'][seat])
    (out/'request.json').write_text(json.dumps(request),encoding='utf-8')
    r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/runtime-check.mjs'),str(mapgen.engine_path()),str(out/'request.json')],
                     cwd=core.ROOT,env=core.ENV,capture_output=True,text=True,encoding='utf-8',timeout=core.TIMEOUT)
    if r.returncode:raise ValueError('Native runtime parity failed: '+r.stderr[-3500:])
    parity=json.loads(r.stdout)
    if parity['terminal']!=dict(outcome=summary['outcome'],round=summary['rounds'],banks=[summary['teams'][t]['gems'] for t in ('teamA','teamB')]):
        raise ValueError('Native replay terminal differs from official release statistics')
    (out/'parity.json').write_text(json.dumps(parity,indent=2)+'\n',encoding='utf-8')
    return dict(map=name,opponent=opponent_name,seat=seat,map_sha256=core.sha(core.map_path(name)),replay=replay_file.relative_to(core.ROOT).as_posix(),
                replay_sha256=core.sha(replay_file),fuel=fuel,official_fuel=full_fuel,parity=parity,summary=summary)


def release():
    if set(cfg()['maps'])&set(core.config()['maps']['confirm']):raise ValueError('Stage 6 diagnostics must preserve sealed confirmation maps')
    v=prepare();tasks=[(m,o,s) for m in cfg()['maps'] for o in cfg()['opponents'] for s in (0,1)]
    with ThreadPoolExecutor(cfg()['jobs']) as pool:
        rows=[]
        for row in pool.map(lambda t:audit_game(*t,v),tasks):
            rows.append(row);print(f"Stage 6 {len(rows)}/{len(tasks)}: {row['map']} seat {row['seat']}",flush=True)
    bundle=core.ROOT/'results/bundles'/f"{cfg()['version']}.zip"
    with tempfile.TemporaryDirectory(dir=core.ROOT/'.cambc') as tmp:
        fresh,same=core.bundle(v.name,Path(tmp)/'verified.zip')
        if not same:raise ValueError('PPO source bundle does not reproduce frozen WASM')
        stage3.preserve_bundle(bundle,fresh)
    return save('release',dict(passed=True,games=rows,runtime=core.runtime_identity(),weights_sha256=cfg()['weights_sha256'],wasm_sha256=core.sha(v.wasm),
        bundle=dict(path=bundle.relative_to(core.ROOT).as_posix(),sha256=core.sha(bundle),rebuild_identical=True),sources=sources(),confirmation_games=0,promoted=False))


def ready():
    from . import ppo
    prerequisite=ppo.ready()
    if not prerequisite['passed']:raise ValueError('Stage 5 gate failed')
    v=prepare();r=json.loads((core.ROOT/'results/stage6-release.json').read_text());parent()
    if not r['passed'] or r['sources']!=sources() or r['runtime']!=core.runtime_identity() or r['wasm_sha256']!=core.sha(v.wasm):raise ValueError('Stale Stage 6 certificate')
    expected={(m,o,s) for m in cfg()['maps'] for o in cfg()['opponents'] for s in (0,1)}
    if len(r['games'])!=len(expected) or {(g['map'],g['opponent'],g['seat']) for g in r['games']}!=expected:raise ValueError('Stage 6 release schedule incomplete')
    for g in r['games']:
        if core.sha(core.ROOT/g['replay'])!=g['replay_sha256'] or core.sha(core.map_path(g['map']))!=g['map_sha256']:raise ValueError('Stage 6 evidence changed')
        if not g['parity']['passed'] or any(t['faults'] or t['fuel_exhausted'] for t in g['summary']['teams'].values()):raise ValueError('Stage 6 runtime gate failed')
    if {t for g in r['games'] for t in g['parity']['actor_types']}!={0,3,4,6,11,12}:raise ValueError('Stage 6 physical champion coverage incomplete')
    if not sum(g['parity']['actions'].get('submit',0) for g in r['games']):raise ValueError('No deployed banking path exercised')
    bundle=core.ROOT/r['bundle']['path']
    if core.sha(bundle)!=r['bundle']['sha256'] or not r['bundle']['rebuild_identical']:raise ValueError('Stage 6 source bundle changed')
    actions=Counter()
    for g in r['games']:actions.update(g['parity']['actions'])
    return save('ready',dict(passed=True,stage=6,next_stage=7,version=v.name,weights_sha256=r['weights_sha256'],wasm_sha256=r['wasm_sha256'],
        release_games=len(r['games']),turns=sum(g['fuel']['turns'] for g in r['games']),decisions=sum(g['fuel']['decisions'] for g in r['games']),
        logit_probes=sum(g['parity']['probes'] for g in r['games']),bit_identical_logits=sum(g['parity']['bit_identical_logits'] for g in r['games']),
        actions=dict(actions),actor_types=sorted({t for g in r['games'] for t in g['parity']['actor_types']}),
        diagnostic_wins=sum(g['summary']['outcome']==('teamA' if g['seat']==0 else 'teamB') for g in r['games']),
        ordinary_fuel_max=max(g['official_fuel']['ordinary_max'] for g in r['games']),initial_fuel_max=max(g['official_fuel']['initial_max'] for g in r['games']),
        faults=0,fuel_exhausted=0,confirmation_games=0,promoted=False,bundle=r['bundle'],sources=sources(),
        acceptance='runtime integration only; no new strength claim, live upload or promotion'))

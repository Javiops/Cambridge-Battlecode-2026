"""Screen a frozen PPO hybrid, then run the unchanged sealed promotion gate once."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct
from concurrent.futures import ThreadPoolExecutor
import tempfile
import zipfile
import numpy as np
from . import core, dataset, replay as replay_codec, stats, gate as promotion, stage3, mapgen


def cfg():return core.config()['stage7']
def read(p):return json.loads(Path(p).read_text())
def save(name,value):return stage3.save('stage7-'+name+'.json',value)
def sources():
    files=list((core.ROOT/'bots/ppo-league/src').glob('*'))+[core.ROOT/n for n in ('lab/stage7.py','lab/gate.py','lab/core.py','lab/stats.py','lab.toml')]
    return {p.relative_to(core.ROOT).as_posix():hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest() for p in files}


def assess(games,candidate,opponent,maps):
    if not maps or len(maps)!=len(set(maps)) or candidate==opponent:raise ValueError('Invalid paired schedule definition')
    expected={(m,a,b) for m in maps for a,b in ((candidate,opponent),(opponent,candidate))}
    keys=[(g.get('map'),g.get('name_a'),g.get('name_b')) for g in games]
    if len(keys)!=len(expected) or set(keys)!=expected:raise ValueError('Incomplete or duplicate paired schedule')
    scores=[];own=[];a=[];b=[];opponent_faults=0
    for g in games:
        if g.get('error') or g.get('outcome') not in ('teamA','teamB'):raise ValueError('Unfinished screening/gate match')
        seat='teamA' if g['name_a']==candidate else 'teamB'
        score=float(g['outcome']==seat);scores.append(score);(a if seat=='teamA' else b).append(score)
        t=g['teams'][seat];own.append(t);opponent_faults+=g['teams']['teamB' if seat=='teamA' else 'teamA']['faults']
    return dict(games=len(games),maps=len(maps),wins=int(sum(scores)),win_fraction=float(np.mean(scores)),as_a=float(np.mean(a)),as_b=float(np.mean(b)),
        faults=sum(t['faults'] for t in own),fuel_lost=sum(t['fuel_exhausted'] for t in own),fuel_per_game=float(np.mean([t['fuel_exhausted'] for t in own])),
        mean_banked_gems=float(np.mean([t['gems'] for t in own])),opponent_faults=opponent_faults)


def accepts(r,minimum,max_faults,max_fuel):
    return bool(r['win_fraction']>=minimum and r['faults']<=max_faults and r['fuel_per_game']<=max_fuel and not r['opponent_faults'])


def lock_confirmation(path,plan):
    if path.exists() and read(path)!=plan:raise ValueError('This confirmation cohort was already used; create fresh holdouts before a different candidate')
    path.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')


def require_fresh_confirmation(plan,history):
    current=set(plan['map_sha256'].values())
    if any(current & set(old['map_sha256'].values()) for old in history):
        raise ValueError('Replacement confirmation pool overlaps a consumed cohort')


def promotion_config(base,settings):
    # Earlier immutable datasets retain their original reservation cohort.
    return base | {'maps':base['maps'] | {'confirm':settings['confirmation_maps']}}


def maps():
    """Generate a predeclared replacement pool without looking at match outcomes."""
    c=core.config();rows=[]
    if len(cfg()['confirmation_maps'])!=cfg()['confirmation_count']:raise ValueError('Wrong fresh confirmation count')
    for i,name in enumerate(cfg()['confirmation_maps']):
        row=mapgen.layout(mapgen.seed_for('stage7-confirm-r2',cfg()['confirmation_seed'],i))
        row.update(name=name.rsplit('/',1)[-1],output=str(core.MAPS/(name+'.map26a')))
        rows.append(row)
    folder=core.ROOT/'.cambc';folder.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder) as tmp:
        request=Path(tmp)/'maps.json';request.write_text(json.dumps(rows),encoding='utf-8')
        r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/engine.mjs'),str(mapgen.engine_path()),'maps',str(request)],capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=120)
        if r.returncode:raise ValueError('Fresh map generation failed: '+r.stderr[-2000:])
    manifest=dict(generator='g1',split='stage7-confirm-r2',seed=cfg()['confirmation_seed'],engine_wasm_sha256=core.sha(mapgen.engine_path()),maps=json.loads(r.stdout))
    hashes=[row['sha256'] for row in manifest['maps']]
    if len(hashes)!=len(set(hashes)):raise ValueError('Duplicate fresh maps')
    require_fresh_confirmation(dict(map_sha256=dict(enumerate(hashes))),[read(core.ROOT/p) for p in cfg()['retired_attempts']])
    path=core.ROOT/'mechanics/generated-maps-stage7-r2.json'
    if path.exists() and read(path)!=manifest:raise ValueError('Fresh confirmation manifest changed')
    path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return dict(passed=True,manifest=path.relative_to(core.ROOT).as_posix(),maps=len(hashes))


def identity():
    v=core.version(cfg()['candidate'])
    if core.sha(v.wasm)!=v.meta['wasm_sha256']:raise ValueError('Frozen candidate changed')
    current=core.ROOT/'bots/ppo-league/src'
    if {p.name:p.read_bytes() for p in current.iterdir()}!={p.name:p.read_bytes() for p in (v.wasm.parent/'src').iterdir()}:raise ValueError('Candidate sources differ from frozen version')
    model=core.ROOT/'models/ppo-v1/checkpoints/012'
    if core.sha(model/'weights.f32')!='94c1399f470e7c64f65a203a46d4bd14dff4527057d6eb12fc26fffb79b5402f':raise ValueError('PPO parent changed')
    if (current/'weights.h').read_bytes()!=(model/'weights.h').read_bytes():raise ValueError('PPO header changed')
    if (current/'policy.h').read_text()!=(core.ROOT/'bots/ppo-actor/src/policy.h').read_text():raise ValueError('Certified inference kernel changed')
    return dict(candidate=v.name,wasm_sha256=core.sha(v.wasm),weights_sha256=core.sha(model/'weights.f32'),runtime=core.runtime_identity(),sources=sources())


def bundle():
    """Reject nonreproducible builds before consuming any confirmation games."""
    proof=identity();destination=core.ROOT/f"results/bundles/{proof['candidate']}.zip"
    with tempfile.TemporaryDirectory(dir=core.ROOT/'.cambc') as tmp:
        fresh,same=core.bundle(proof['candidate'],Path(tmp)/'source.zip')
        if not same:raise ValueError('Source bundle does not reproduce candidate WASM')
        stage3.preserve_bundle(destination,fresh)
    return save('bundle',proof|dict(passed=True,bundle=dict(path=destination.relative_to(core.ROOT).as_posix(),sha256=core.sha(destination),rebuild_identical=True)))


def screen():
    proof=identity();c=core.config();name=cfg()['candidate'];opp=cfg()['opponent'];maps=c['maps']['screen'];stress=cfg()['stress_maps']
    if set(maps+stress)&set(c['maps']['confirm']+cfg()['confirmation_maps']):raise ValueError('Screen/confirmation leakage')
    reports={}
    for version in (name,cfg()['ablation'],cfg()['baseline']):
        games=core.play([(version,opp)],maps,cfg()['jobs']);r=assess(games,version,opp,maps)
        reports[version]=dict(summary=r,games=games)
    stress_games=core.play([(name,opp)],stress,cfg()['jobs']);stress_report=assess(stress_games,name,opp,stress)
    limits=c['gate'];passed=accepts(reports[name]['summary'],cfg()['minimum_screen'],limits['max_faults'],limits['max_fuel_exhausted_per_game']) and accepts(stress_report,cfg()['minimum_stress'],limits['max_faults'],limits['max_fuel_exhausted_per_game'])
    noise_games=core.play([tuple(c['league']['noise_pair'])],maps,cfg()['jobs']);noise=assess(noise_games,*c['league']['noise_pair'],maps)
    def map_scores(version):
        return np.array([np.mean([g['outcome']==('teamA' if g['name_a']==version else 'teamB') for g in reports[version]['games'] if g['map']==m]) for m in maps])
    delta=map_scores(name)-map_scores(cfg()['ablation']);rng=np.random.default_rng(cfg()['seed']);draws=rng.integers(len(maps),size=(5000,len(maps)))
    return save('screen',proof|dict(passed=bool(passed),reports=reports,stress=dict(summary=stress_report,games=stress_games),noise=noise,
        actor_ablation=dict(mean_win_difference=float(delta.mean()),map_bootstrap_90=np.quantile(delta[draws].mean(axis=1),[.05,.95]).tolist(),
                            interpretation='Controller improvement is not attributed to PPO; this paired ablation estimates the incremental actor effect'),confirmation_games=0))


def canary():
    proof=identity();rows=[];name=cfg()['candidate'];opp=cfg()['opponent']
    for m in cfg()['canary_maps']:
        for seat in (0,1):
            out=core.ROOT/'.cambc/stage7-proof'/f"{m.replace('/','_')}-{seat}";a,b=(name,opp) if seat==0 else (opp,name)
            path=core.watch(a,b,m,out)
            with zipfile.ZipFile(path) as z:text=z.read('team-a.stdout' if seat==0 else 'team-b.stdout').replace(b'\0',b'').decode('utf-8')
            counters={}
            for r,champ,calls,changes,choices in re.findall(r'S7P (\d+) (\d+) (\d+) (\d+) (\d+)',text):counters[int(champ)]=dict(calls=int(calls),changes=int(changes),choices=int(choices))
            if not counters:raise ValueError('Missing PPO activity trace')
            rows.append(dict(map=m,seat=seat,replay=path.relative_to(core.ROOT).as_posix(),sha256=core.sha(path),champions=counters))
    calls=sum(t['calls'] for row in rows for t in row['champions'].values());changes=sum(t['changes'] for row in rows for t in row['champions'].values())
    if calls<cfg()['minimum_policy_calls'] or not changes:raise ValueError('Learned actor is inactive')
    return save('canary',proof|dict(passed=True,games=rows,policy_calls=calls,changed_targets=changes))


def gate():
    proof=identity();screened=read(core.ROOT/'results/stage7-screen.json');observed=read(core.ROOT/'results/stage7-canary.json');rebuilt=read(core.ROOT/'results/stage7-bundle.json')
    for r in (screened,observed,rebuilt):
        if not r['passed'] or any(r[k]!=proof[k] for k in proof):raise ValueError('Screen or PPO canary is stale/failed')
    c=promotion_config(core.config(),cfg());name=cfg()['candidate'];attempt=core.ROOT/cfg()['confirmation_attempt']
    plan=dict(candidate=name,wasm_sha256=proof['wasm_sha256'],maps=c['maps']['confirm'],map_sha256={m:core.sha(core.map_path(m)) for m in c['maps']['confirm']},
              gate=c['gate'],champion=c['league']['champion'],runtime=proof['runtime'])
    require_fresh_confirmation(plan,[read(core.ROOT/p) for p in cfg()['retired_attempts']])
    lock_confirmation(attempt,plan)
    passed,lines=promotion.run(name,c,cfg()['jobs']);(core.ROOT/'results/stage7-gate.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    opponents=set((c['league']['champion'],c['gate']['weak']))-{name};reports={}
    for opp in opponents:
        games=core.play([(name,opp)],c['maps']['confirm'],cfg()['jobs']);reports[opp]=dict(summary=assess(games,name,opp,c['maps']['confirm']),games=games)
    captures=[]
    if passed:
        tasks=[g for r in reports.values() for g in r['games']]
        with ThreadPoolExecutor(cfg()['jobs']) as pool:
            for result in pool.map(lambda g:archive_match(g,proof),tasks):captures.append(result)
    return save('gate',proof|dict(passed=passed,plan=plan,reports=reports,captures=captures,promotion_markdown_sha256=core.sha(core.ROOT/'results/stage7-gate.md'),uploaded=False))


def archive_match(g,proof):
    """Keep a reproducible replay/statistics record after the frozen candidate passes."""
    name=proof['candidate'];seat=0 if g['name_a']==name else 1
    out=core.ROOT/'.cambc/stage7-promotion'/f"{g['map'].replace('/','_')}-{seat}"
    out.mkdir(parents=True,exist_ok=True)
    expected=dict(candidate_sha256=proof['wasm_sha256'],map_sha256=core.sha(core.map_path(g['map'])),seat=seat)
    marker=out/'identity.json'
    if not marker.exists() or read(marker)!=expected or not (out/'stats.json').exists():
        raw,error=core.run_game(core.version(g['name_a']),core.version(g['name_b']),core.map_path(g['map']),str(out),logs=True,profile=proof['runtime'])
        if raw is None:raise ValueError('Promotion replay capture failed: '+error)
        marker.write_text(json.dumps(expected,indent=2)+'\n',encoding='utf-8')
    raw=read(out/'stats.json');summary=stats.summarize(raw)
    if any(summary[k]!=g[k] for k in ('outcome','rounds','teams')):raise ValueError('Captured promotion replay does not reproduce gated match')
    path=max(out.glob('*.repl26a'),key=lambda p:p.stat().st_mtime)
    actions=replay_codec.decode(dataset.raw_bytes(path),core.map_path(g['map']).read_bytes());drafts=sum(a['kind']=='draft' for a in actions)//2
    physical=sum(c['team']==('teamA' if seat==0 else 'teamB') for c in raw['champions'])
    with zipfile.ZipFile(path) as z:data=z.read('team-a.fuel' if seat==0 else 'team-b.fuel')
    if data[:11]!=b'a62leuf\0\0\0\1' or (len(data)-77)%8:raise ValueError('Malformed official promotion fuel stream')
    values=struct.unpack_from('<'+'Q'*((len(data)-77)//8),data,77)
    return dict(map=g['map'],seat=seat,replay=path.relative_to(core.ROOT).as_posix(),replay_sha256=core.sha(path),
                statistics= (out/'stats.json').relative_to(core.ROOT).as_posix(),statistics_sha256=core.sha(out/'stats.json'),
                first_fuel_max=max(values[drafts:drafts+physical]),ordinary_fuel_max=max(values[drafts+physical:]),
                official_fuel_turns=len(values)-drafts)


def ready():
    proof=identity();reports={n:read(core.ROOT/f'results/stage7-{n}.json') for n in ('screen','canary','gate')}
    for name,r in reports.items():
        if not r['passed'] or any(r[k]!=proof[k] for k in proof):raise ValueError('Stage 7 proof is stale/failed: '+name)
    if core.sha(core.ROOT/'results/stage7-gate.md')!=reports['gate']['promotion_markdown_sha256']:raise ValueError('Promotion verdict changed')
    captures=reports['gate']['captures']
    if len(captures)!=sum(r['summary']['games'] for r in reports['gate']['reports'].values()):raise ValueError('Promotion replay archive incomplete')
    for capture in captures:
        if core.sha(core.ROOT/capture['replay'])!=capture['replay_sha256'] or core.sha(core.ROOT/capture['statistics'])!=capture['statistics_sha256']:raise ValueError('Promotion evidence changed')
    bundle=core.ROOT/f"results/bundles/{proof['candidate']}.zip"
    with tempfile.TemporaryDirectory(dir=core.ROOT/'.cambc') as tmp:
        fresh,same=core.bundle(proof['candidate'],Path(tmp)/'source.zip')
        if not same:raise ValueError('Source bundle does not reproduce qualified WASM')
        stage3.preserve_bundle(bundle,fresh)
    return save('ready',proof|dict(passed=True,stage=7,promotion_gate_passed=True,
        screening=reports['screen']['reports'][proof['candidate']]['summary'],stress=reports['screen']['stress']['summary'],
        promotion={n:r['summary'] for n,r in reports['gate']['reports'].items()},policy_calls=reports['canary']['policy_calls'],
        changed_targets=reports['canary']['changed_targets'],actor_ablation=reports['screen']['actor_ablation'],
        archived_promotion_games=len(captures),ordinary_fuel_max=max(c['ordinary_fuel_max'] for c in captures),initial_fuel_max=max(c['first_fuel_max'] for c in captures),
        bundle=dict(path=bundle.relative_to(core.ROOT).as_posix(),sha256=core.sha(bundle),rebuild_identical=True),uploaded=False,champion_changed=False))

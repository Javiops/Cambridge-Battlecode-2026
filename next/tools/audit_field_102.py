"""Audit collected curriculum groups with native replay reconstruction."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, hashlib, io, json, re, struct, subprocess, sys, zipfile

parser=argparse.ArgumentParser(__doc__)
parser.add_argument('--journal',type=Path,required=True)
parser.add_argument('--maps',type=Path,required=True)
parser.add_argument('--engine',type=Path,required=True)
parser.add_argument('--node',type=Path,required=True)
args=parser.parse_args()
repo=Path(__file__).resolve().parents[1];sys.path.insert(0,str(repo))
from lab import stats
live=args.journal.resolve().parent;batch=json.loads(args.journal.read_text())
engine=args.engine.resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(engine)=='742919b4454b427912eece99e5675752791fe5d83167b2fee1766c908e9cccee','Wrong official1.0.2 engine bytes'
maps={sha(p):p.resolve() for p in args.maps.glob('*.map26a')}
expected_build='ff41468c05c7be716f7647aaf7ea7314633f7038815386c806fafcec98629114'
assert not batch['pending'],'Resolve unknown request before auditing'
assert len({g['id'] for g in batch['groups']})==len(batch['groups']),'Duplicate group IDs'

def audit(task):
    group,filename=task;folder=live/group['id'];rawpath=folder/filename
    raw=json.loads(rawpath.read_text());summary=stats.summarize(raw)
    assert raw['match']['engineBuildHash']==expected_build and raw['match']['engineVersion']=='1.0.2'
    mp=maps[raw['match']['mapHash']];mid=rawpath.stem
    assert mp.stem in {name.replace('_','-') for name in group['maps']}
    team='teamA' if group['seat']=='A' else 'teamB';other='teamB' if team=='teamA' else 'teamA'
    assert group['completedVersionVerified']==group['version']
    if group.get('initiatedByThisAgent'):assert group['queuedVersionVerified']==group['version']
    else:assert group['versionEvidence']=='completed_group_page'
    assert batch['stages'][group['stage']]['platform_version']==group['version']
    with zipfile.ZipFile(folder/'replays.zip') as outer:
        names=[name for name in outer.namelist() if mid in name];assert len(names)==1
        inner=outer.read(names[0])
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        replay=z.read('replay.repl26a')
        stdout=z.read('team-a.stdout' if team=='teamA' else 'team-b.stdout').replace(b'\0',b'').decode('utf-8')
        fuel=z.read('team-a.fuel' if team=='teamA' else 'team-b.fuel')
    assert len(replay)>100
    game=folder/mid;game.mkdir(exist_ok=True)
    (game/'raw.repl26a').write_bytes(replay)
    request=game/'request.json';request.write_text(json.dumps(dict(replay=str(game/'raw.repl26a'),map=str(mp))),encoding='utf-8')
    native_path=game/'native.json'
    if native_path.exists():native=json.loads(native_path.read_text())
    else:
        result=subprocess.run([str(args.node.resolve()),'--no-warnings',str(repo/'tools/native/replay_metadata_102.mjs'),str(engine),str(request)],cwd=repo,capture_output=True,text=True,encoding='utf-8',timeout=300)
        if result.returncode:raise ValueError(mid+': '+result.stderr[-2000:])
        native=[json.loads(line) for line in result.stdout.splitlines()]
    terminal=dict(outcome=summary['outcome'],round=summary['rounds'],banks=[summary['teams'][t]['gems'] for t in ('teamA','teamB')])
    assert native[0]['engine_sha256']==sha(engine) and native[0]['replay_format']==131073
    assert len(native)==2 and native[0]['terminal']==native[1]['terminal']==terminal
    for champion in native[0]['statistics']:
        original=next(c for c in raw['champions'] if c['id']==champion['id'])['metrics']
        assert all(champion[a]==int(original[b]) for a,b in [('kills','kills'),('deaths','deaths'),('gold','earnedGold'),('submitted_gems','submittedGems'),('collected_gems','collectedGems')])
    (game/'native.json').write_text(json.dumps(native,indent=2)+'\n',encoding='utf-8')
    counters={unit:dict(round=int(r),calls=int(calls),changes=int(changes),choices=int(choices)) for r,unit,calls,changes,choices in re.findall(r'S7P (\d+) (\d+) (\d+) (\d+) (\d+)',stdout)}
    assert fuel[:11]==b'a62leuf\0\0\0\1' and (len(fuel)-77)%8==0
    values=struct.unpack_from('<'+'Q'*((len(fuel)-77)//8),fuel,77)
    drafts=sum(p['team']==team for p in raw['roster']['draft']);physical=sum(c['team']==team for c in raw['champions'])
    return dict(id=mid,group_id=group['id'],stage=group['stage'],candidate=batch['stages'][group['stage']]['candidate'],opponent=group['opponent'],map=mp.stem,seat=group['seat'],platform_version=group['version'],cohort=group['cohort'],
        kind=group.get('kind',batch.get('kind','unranked')),initiatedByThisAgent=group.get('initiatedByThisAgent'),won=summary['outcome']==team,rounds=summary['rounds'],our=summary['teams'][team],foe=summary['teams'][other],
        collected_gems={t:sum(float(c['metrics']['collectedGems']) for c in raw['champions'] if c['team']==t) for t in (team,other)},
        carried_gems={t:sum(float(c['metrics']['gems']) for c in raw['champions'] if c['team']==t) for t in (team,other)},
        draft=raw['roster']['draft'],native_verified=True,statistics_sha256=sha(rawpath),replay_sha256=hashlib.sha256(replay).hexdigest(),
        ppo_logged_calls=sum(c['calls'] for c in counters.values()),ppo_logged_changes=sum(c['changes'] for c in counters.values()),
        official_fuel=dict(initial_max=max(values[drafts:drafts+physical]),ordinary_max=max(values[drafts+physical:])))

batch['groups']=[g for g in batch['groups'] if g.get('collectionStatus')=='complete']
assert all(len(g['summaryFiles'])==5 for g in batch['groups'])
assert batch['groups'], 'No completed groups to audit'
tasks=[(g,f) for g in batch['groups'] for f in g['summaryFiles']]
with ThreadPoolExecutor(4) as pool:
    rows=[]
    for row in pool.map(audit,tasks):
        rows.append(row)
        if len(rows)%20==0:print(f'Hourly native verification {len(rows)}/{len(tasks)}',flush=True)
def summarize(rows):
    return dict(games=len(rows),wins=sum(r['won'] for r in rows),faults=sum(r['our']['faults'] for r in rows),
        fuel_exhausted=sum(r['our']['fuel_exhausted'] for r in rows),opponent_faults=sum(r['foe']['faults'] for r in rows),
        mean_banked_gems=sum(r['our']['gems'] for r in rows)/len(rows),mean_opponent_banked_gems=sum(r['foe']['gems'] for r in rows)/len(rows),
        zero_bank_games=sum(r['our']['gems']==0 for r in rows),ppo_logged_calls=sum(r['ppo_logged_calls'] for r in rows),ppo_logged_changes=sum(r['ppo_logged_changes'] for r in rows))
report=dict(schema=2,platform_versions=sorted(set(g['version'] for g in batch['groups'])),candidates={str(i):stage['candidate'] for i,stage in enumerate(batch['stages'])},engine_build_hash=expected_build,decoder_wasm_sha256=sha(engine),
    kind=batch.get('kind','unranked'),collected_groups=len(batch['groups']),challenged_groups=sum(g.get('initiatedByThisAgent',False) for g in batch['groups']),allowance_before=batch['initialAllowance'],allowance_after=batch.get('finalAllowance'),maps=len(set(r['map'] for r in rows)),
    native_verified_games=len(rows),summary=summarize(rows),
    by_stage={str(i):summarize([r for r in rows if r['stage']==i]) for i in sorted(set(r['stage'] for r in rows))},
    by_cohort={name:summarize([r for r in rows if r['cohort']==name]) for name in dict.fromkeys(r['cohort'] for r in rows)},
    by_map={name:summarize([r for r in rows if r['map']==name]) for name in sorted(set(r['map'] for r in rows))},
    by_opponent={name:summarize([r for r in rows if r['opponent']==name]) for name in dict.fromkeys(r['opponent'] for r in rows)},games=rows,
    interpretation=batch['purpose']+' Runtime, acquisition and deposits accompany wins. PPO counters are log lower bounds; no controlled strength estimate.')
(live/'results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('challenged_groups','maps','native_verified_games','summary','by_cohort')},indent=2),flush=True)

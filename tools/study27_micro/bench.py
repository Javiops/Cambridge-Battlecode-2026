#!/usr/bin/env python3
"""Reproduce immutable study27 farming ablations from local Git history.

Initialize the clone with ``cambc init --yes`` before building, then run:
  python tools/study27_micro/bench.py --candidate volley-backoff \
      --features farm_volley_backoff --maps "maps/*.map26a" "maps_gen/*.map26a"

The default is candidate vs original/spar11/spar12/spar16, and unchanged original
vs each spar on identical map sides (14 slots/map). --prepare-only starts no CLI
or games. This script never fetches Git history, submits bots or changes tracked
bot source. All writes stay under out/study27-micro in the supplied clone.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
import glob
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
import zipfile

# Do not create imported patch bytecode next to checked-in tools or sources.
sys.dont_write_bytecode=True

BASE_COMMIT='c462346d4ace741bfd8f5251fb0e5e2eee69b800'
SPAR_COMMIT='43d003323cd16059cda6a54de14ed86e2da3b788'
SPARS=('spar11','spar12','spar16')
BASE_SHA256={
    'de_rules.h':'3e50429c96765f325ea3804c2bbb5c13ce26a4119fc7b8694f58def60531221b',
    'fight.h':'2e5bb46e20258e7eebc8ca3e2a62fbbdd3e1fd216813c15270569f419a2a022b',
    'main.cpp':'0650eda916f8f2fe16ae69923d239d15e916e738205e90060113fac65a85453f',
    'opening_replace.h':'ca6680bae82b74b89fd0bb65573904246df8761d8b22e3ce8cb6bd93207207e7',
    'params.h':'5cc4bcda14dde61df979267dd5485abd89753f2d8b27f7e5b98ba3b0496ddda8',
    'utility.h':'5e48af1229195c4b356a617fd7323f49efe2af3a09728f6eda91ed4975c2b580',
}
SPAR_SHA256={
    'spar11':{
        'fight.h':'40e22492d61a9a79907b20e26ae536787952759d2fe4333771aa2415a461b362',
        'main.cpp':'0bf959d3143110e3e6c29bae8c8bb035b60131230dd8d92912ed5fa8d3769684',
        'params.h':'73e598fae85e7f68e127543bc358b10715c234e8887d0966fdd84569f06b20d5'},
    'spar12':{
        'fight.h':'40e22492d61a9a79907b20e26ae536787952759d2fe4333771aa2415a461b362',
        'main.cpp':'0bf959d3143110e3e6c29bae8c8bb035b60131230dd8d92912ed5fa8d3769684',
        'params.h':'0c8fdf62cabab7d1aa462d791f9680405c00132d6d324dbeb59f1749a7d003cf'},
    'spar16':{
        'fight.h':'82eac085aa0eef23f311ff49972709801e5b009ee5b495710ddd20d0ea8c5169',
        'main.cpp':'56c1771b6fcc83eafbf6afd237b15741738958f2b4e0d8eaa4732e410e8dcc25',
        'params.h':'f9b7b55d7958bd012accf0e18aaef5fba91ed3d21fc06330094844b57bb9ccaf'},
}
ORIGINAL_FEATURES=tuple(f'farm_{m}_{r}' for m in ('outnumbered','volley','contested') for r in ('hold','backoff'))+('reserve_cc3','reserve_cc6')
REFINED_FEATURES=('start_only_backoff','start_only_retarget','no_contact_dash','reserve_cc_contact5','reserve_cc_contact3')
CORNERS_FEATURES=('corners_lone','corners_reentry','corners_flee','corners_lone_reentry','corners_lone_flee','corners_reentry_flee','corners_v39')
REENTRY_FEATURES=('reentry16','reentry32')
ACTIVE_REENTRY_FEATURES=('reentry16_active','reentry32_active')
FEATURES=ORIGINAL_FEATURES+REFINED_FEATURES+CORNERS_FEATURES+REENTRY_FEATURES+ACTIVE_REENTRY_FEATURES
OUTPUT_ROOT=None
OUTPUT_REPO=None

def require(condition,message):
    if not condition:raise RuntimeError(message)
def now():return datetime.now(timezone.utc).isoformat()
def sha_bytes(data):return hashlib.sha256(data).hexdigest()
def sha(path):return sha_bytes(Path(path).read_bytes())
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def reject_redirects(path,boundary):
    path=Path(path).absolute();boundary=Path(boundary).absolute()
    require(path.is_relative_to(boundary),'Output is outside the intended boundary')
    cursor=path
    while True:
        try:
            observed=cursor.lstat()
        except FileNotFoundError:
            observed=None
        if observed is not None:
            require(not stat.S_ISLNK(observed.st_mode) and not (getattr(observed,'st_file_attributes',0)&0x400),
                    'Refusing output symlink/junction/reparse point: '+str(cursor))
        if cursor==boundary:break
        cursor=cursor.parent
    require(path.resolve()==path,'Output path redirects away from its intended lexical location: '+str(path))
def guard(path):
    path=Path(path)
    if OUTPUT_ROOT is not None:
        reject_redirects(path,OUTPUT_REPO or OUTPUT_ROOT)
        require(path.resolve().is_relative_to(OUTPUT_ROOT),'Output escapes task directory: '+str(path))
    return path
def write(path,value):
    path=guard(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=guard(path.with_name(path.name+f'.{os.getpid()}.{threading.get_ident()}.tmp'))
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temporary,path)
def valid_name(name):
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',name) is not None,'Invalid output bot name')
def ordered_features(features):
    require(len(set(features))==len(features) and all(f in FEATURES for f in features),'Unknown/duplicate feature')
    corners=[f for f in features if f in CORNERS_FEATURES]
    reserves=[f for f in features if f in ('reserve_cc3','reserve_cc6')]
    policies=[f for f in features if f not in CORNERS_FEATURES and f not in ('reserve_cc3','reserve_cc6')]
    require(len(corners)<=1 and len(policies)<=1 and len(reserves)<=1,
            'Select at most one corners component set, one generic policy and one global CC reserve')
    require(not (any(f.startswith('reserve_cc_contact') for f in policies) and reserves),
            'Contact-only CC policies cannot be combined with another CC reserve')
    # Corners verifies the complete original main/params pins and must run first.
    return corners+policies+reserves
def source_hashes(path):
    children=list(Path(path).iterdir())
    require(all(p.is_file() for p in children),'Unexpected source subdirectory')
    return {p.name:sha(guard(p)) for p in sorted(children)}

@contextmanager
def exclusive(path,timeout=1200):
    path=guard(path);path.parent.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    while True:
        try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY);break
        except FileExistsError:
            require(time.monotonic()-start<timeout,'Timed out on lock '+str(path)+'. Check active processes before removing a stale lock.')
            time.sleep(.1)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:stream.write(json.dumps({'pid':os.getpid(),'created_utc':now()}))
        yield
    finally:guard(path).unlink(missing_ok=True)

def git(repo,*args):
    proc=subprocess.run(['git','-C',str(repo),*args],capture_output=True)
    require(proc.returncode==0,'Local Git failed: '+proc.stderr.decode('utf-8',errors='replace').strip())
    return proc.stdout
def find_repo(requested):
    for choice in ([Path(requested)] if requested else [Path.cwd(),Path(__file__).resolve().parent]):
        proc=subprocess.run(['git','-C',str(choice),'rev-parse','--show-toplevel'],capture_output=True,text=True)
        if proc.returncode==0:return Path(proc.stdout.strip()).resolve()
    raise RuntimeError('Run in a Git clone or use --repo. Both pinned commits must already exist locally.')
def pinned_source(repo,commit,path,expected):
    require(git(repo,'rev-parse','--verify',commit+'^{commit}').decode().strip()==commit,'Pinned commit unavailable')
    names=git(repo,'ls-tree','-r','--name-only',f'{commit}:{path}').decode().splitlines()
    require(set(names)==set(expected),'Pinned source file list differs: '+path)
    files={name:git(repo,'show',f'{commit}:{path}/{name}') for name in names}
    require({name:sha_bytes(content) for name,content in files.items()}==expected,'Pinned source SHA256 differs: '+path)
    return files

def patched_source(original,features):
    features=ordered_features(features)
    decoded={name:content.decode('utf-8').replace('\r\n','\n').replace('\r','\n') for name,content in original.items()}
    files=dict(decoded);module_pins={}
    modules={}
    for feature in features:
        module_name=('patch_corners.py' if feature in CORNERS_FEATURES else
                     'patch_reentry_active.py' if feature in ACTIVE_REENTRY_FEATURES else
                     'patch_reentry.py' if feature in REENTRY_FEATURES else
                     'patch_farm_refined.py' if feature in REFINED_FEATURES else 'patch_farm.py')
        module_path=Path(__file__).resolve().with_name(module_name)
        require(module_path.is_file(),'Missing neighboring '+module_name)
        if module_name not in modules:
            spec=importlib.util.spec_from_file_location('study27_'+module_path.stem,module_path)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            modules[module_name]=module
            module_pins[module_name]=sha(module_path)
        if feature in ('start_only_backoff','start_only_retarget'):
            dependency=module_path.with_name('patch_farm.py')
            require(dependency.is_file(),'Missing transitive start-only dependency patch_farm.py')
            module_pins[dependency.name]=sha(dependency)
        if feature in ACTIVE_REENTRY_FEATURES:
            dependency=module_path.with_name('patch_reentry.py')
            require(dependency.is_file(),'Missing transitive active re-entry dependency patch_reentry.py')
            module_pins[dependency.name]=sha(dependency)
        files=modules[module_name].apply(files,feature=feature)
        require(isinstance(files,dict),'Transform did not return source files')
    require(set(files)==set(original),'Transform added or removed source files')
    return {name:original[name] if value==decoded[name] else value.encode('utf-8') for name,value in files.items()},module_pins

def prepare(root,name,features,original,commit,base_path):
    features=ordered_features(features)
    payload,module_pins=patched_source(original,features)
    pins={name:sha_bytes(content) for name,content in sorted(payload.items())}
    target=guard(root/'bots'/name/'src')
    metadata={'name':name,'features':features,'base_commit':commit,'base_path':base_path,
        'base_source_sha256':{name:sha_bytes(content) for name,content in sorted(original.items())},
        'patch_modules_sha256':module_pins,'source_sha256':pins}
    record=guard(target.parent/'source-manifest.json')
    if target.exists():
        require(source_hashes(target)==pins,'Existing source differs; choose a new --candidate name: '+str(target))
        require(record.exists() and read(record)==metadata,'Existing provenance differs; choose a new --candidate name')
    else:
        target.mkdir(parents=True)
        for filename,content in payload.items():guard(target/filename).write_bytes(content)
        write(record,metadata)
    return target.parent,metadata

def find_cli():
    value=os.environ.get('CAMBC_CLI') or shutil.which('cambc') or shutil.which('cambc.exe')
    require(value,'Set CAMBC_CLI to the executable path or add cambc to PATH')
    path=Path(shutil.which(value) or value).expanduser().resolve()
    require(path.is_file(),'CAMBC_CLI must be one executable path')
    return path
def permission_failure(text):
    return any(token in text.lower() for token in ('access is denied','permission denied','permissiondenied','winerror 5'))
def command(args,repo,env,log_prefix,timeout,retries=3):
    attempts=[]
    for attempt in range(retries+1):
        try:proc=subprocess.run([str(a) for a in args],cwd=repo,env=env,capture_output=True,text=True,errors='replace',timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            write(log_prefix.with_suffix('.timeout.json'),{'command':list(map(str,args)),'timeout_seconds':timeout})
            raise RuntimeError('CLI command timed out: '+str(log_prefix)) from exc
        text=proc.stdout+proc.stderr
        log=guard(log_prefix.with_name(log_prefix.name+f'.attempt-{attempt+1}.log'));log.parent.mkdir(parents=True,exist_ok=True)
        log.write_text(text,encoding='utf-8')
        attempts.append({'returncode':proc.returncode,'log':str(log),'access_denied_retry':proc.returncode!=0 and permission_failure(text)})
        if proc.returncode==0:return attempts
        require(attempt<retries and permission_failure(text),'CLI command failed; see '+str(log)+'\n'+text[-2200:])
        time.sleep(.25*(attempt+1))
    raise AssertionError('Unreachable')

def collect_maps(repo,patterns):
    maps={}
    for pattern in patterns:
        expanded=Path(pattern).expanduser()
        if not expanded.is_absolute():expanded=repo/expanded
        paths=sorted(Path(p).resolve() for p in glob.glob(str(expanded),recursive=True) if Path(p).is_file())
        require(paths,'Map glob matched no files: '+pattern)
        for path in paths:
            require(path.suffix=='.map26a','Expected .map26a map: '+str(path))
            digest=sha(path);entry=maps.setdefault(digest,{'path':path,'sha256':digest,'aliases':[]})
            if str(path) not in entry['aliases']:entry['aliases'].append(str(path))
    return list(maps.values())
def statistics_fields(data):
    require(data.get('outcome') in ('teamA','teamB','draw'),'Invalid completed-game outcome')
    require(type(data.get('round')) is int and 1<=data['round']<=2000,'Invalid completed-game round')
    require(data.get('engineVersion')=='0.0.1' and data.get('schemaVersion')==2,'Unexpected engine/statistics version')
    faults=data.get('botFaults')
    require(isinstance(faults,list) and len(faults)==2 and all(type(n) is int and n>=0 for n in faults),'Unsupported botFaults schema')
    require(len(data.get('teams',[]))==2,'Expected two teams')
    return {'outcome':data['outcome'],'rounds':data['round'],'gems':[t['submittedGems'] for t in data['teams']],
        'deaths':[sum(c['deaths'] for c in data['champions'] if c['team']==t) for t in (0,1)],
        'faults':faults,'engine_version':data['engineVersion'],'statistics_schema':data['schemaVersion']}
def audit_stdout(text):
    text=text.replace('\0','');initial=dict(Counter(re.findall(r'\[init\] (\S+)',text)))
    active=None;farm={}
    for line in text.splitlines():
        body=re.search(r'^\[(?:init|r\d+)\] (\S+)',line)
        if body:active=body.group(1)
        status=re.search(r'\[farmguard\] r=(\d+) checks=(\d+) blocks=(\d+)',line)
        if status:
            val=farm.setdefault(active or 'unknown_body',{'checks':0,'blocks':0,'last_round':0,'samples':0})
            val['checks']=max(val['checks'],int(status[2]));val['blocks']=max(val['blocks'],int(status[3]))
            val['last_round']=max(val['last_round'],int(status[1]));val['samples']+=1
    return {'initializations':initial,'reinitializations_observed':sum(max(0,n-1) for n in initial.values()),
        'caught_errors':dict(Counter(re.findall(r'\[err #\d+\] ([^\r\n]+)',text))),
        'low_fuel_logged':len(re.findall('mode=low-fuel',text)),'farm_guard_cumulative_samples':farm,
        'sha256':sha_bytes(text.encode())}
def cached(root,key,identity):
    path=guard(root/'cache'/(key+'.json'))
    if not path.exists():return None
    row=read(path)
    require(row.get('schema_version')==1 and row.get('key')==key and row.get('identity')==identity,'Cached identity mismatch')
    stats=guard(root/'cache'/(key+'.statistics.json'))
    require(stats.is_file() and sha(stats)==row['statistics_sha256'],'Cached statistics changed')
    fields=statistics_fields(read(stats))
    require(all(row.get(k)==v for k,v in fields.items()),'Cached outcome differs from statistics')
    if row.get('retained_replay'):
        require(sha(guard(root/row['retained_replay']))==row['replay_sha256'],'Retained replay changed')
    return row
def sign_p(w,l):
    n=w+l
    return min(1.,2*sum(math.comb(n,k) for k in range(min(w,l)+1))/2**n) if n else 1.
def summary(rows):
    output={}
    for name in sorted({r['candidate'] for r in rows}):
        output[name]={}
        for opponent in sorted({r['opponent'] for r in rows if r['candidate']==name}):
            rs=[r for r in rows if r['candidate']==name and r['opponent']==opponent]
            pairs={};counts=Counter();gd=dd=0
            for row in rs:
                side=row['side'];winner={'teamA':0,'teamB':1,'draw':-1}[row['outcome']]
                result='D' if winner<0 else 'W' if winner==side else 'L';counts[result]+=1
                pair=pairs.setdefault(row['map_sha256'],{});require(side not in pair,'Duplicate paired slot');pair[side]=result
                gd+=row['gems'][side]-row['gems'][1-side];dd+=row['deaths'][side]-row['deaths'][1-side]
            require(all(set(p)=={0,1} for p in pairs.values()),'Incomplete paired map')
            bw=sum(v[0]==v[1]=='W' for v in pairs.values());bl=sum(v[0]==v[1]=='L' for v in pairs.values())
            output[name][opponent]={'maps':len(pairs),'games':len(rs),'wins':counts['W'],'losses':counts['L'],'draws':counts['D'],
                'both_won':bw,'both_lost':bl,'p_two_sided':sign_p(bw,bl),
                'mean_gem_difference':gd/len(rs),'mean_death_difference':dd/len(rs)}
    return output

def main():
    global OUTPUT_ROOT,OUTPUT_REPO
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--repo');p.add_argument('--candidate',required=True)
    p.add_argument('--features',required=True,help='Comma-separated: '+','.join(FEATURES)+'; empty string gives control')
    p.add_argument('--opponents',default='original,spar11,spar12,spar16',help='Comma-separated pinned opponent names')
    p.add_argument('--no-baseline-panel',action='store_true',help='Skip original vs selected spar opponents')
    p.add_argument('--maps',nargs='+',action='append',metavar='GLOB');p.add_argument('--jobs',type=int,default=1)
    p.add_argument('--timeout',type=int,default=240);p.add_argument('--prepare-only',action='store_true')
    a=p.parse_args();valid_name(a.candidate)
    require(a.candidate not in ('original',*SPARS),'Candidate name is reserved')
    features=ordered_features([s.strip() for s in a.features.split(',') if s.strip()])
    opponents=[s.strip() for s in a.opponents.split(',') if s.strip()]
    require(opponents and len(set(opponents))==len(opponents) and all(o in ('original',*SPARS) for o in opponents),'Invalid/duplicate opponent')
    require(1<=a.jobs<=32 and a.timeout>0,'Require jobs1..32 and positive timeout')
    repo=find_repo(a.repo);root=repo/'out/study27-micro'
    reject_redirects(root,repo)
    OUTPUT_ROOT=root;OUTPUT_REPO=repo
    selected_spars=[s for s in SPARS if s in opponents]
    originals={'original':pinned_source(repo,BASE_COMMIT,'bots/study27/src',BASE_SHA256)}
    for spar in selected_spars:originals[spar]=pinned_source(repo,SPAR_COMMIT,f'bots/{spar}/src',SPAR_SHA256[spar])
    prepared={}
    with exclusive(root/'locks/prepare.lock'):
        prepared['original']=prepare(root,'original',[],originals['original'],BASE_COMMIT,'bots/study27/src')
        prepared[a.candidate]=prepare(root,a.candidate,features,originals['original'],BASE_COMMIT,'bots/study27/src')
        for spar in selected_spars:prepared[spar]=prepare(root,spar,[],originals[spar],SPAR_COMMIT,f'bots/{spar}/src')
    print('Prepared immutable sources:',root/'bots',flush=True)
    if a.prepare_only:
        print('Source-only preparation complete; no CLI/build/games started.');return 0
    require((repo/'cambc.toml').is_file() and (repo/'sdk/cpp/cambc.h').is_file(),'Run cambc init --yes in the clone before builds')
    cli=find_cli();env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1','CAMBC_WASMTIME_CACHE':str(guard(root/'wasmtime-cache'))}
    guard(root/'wasmtime-cache').mkdir(parents=True,exist_ok=True)
    for child in (root/'wasmtime-cache').rglob('*'):guard(child)
    runtime={'cli_version':subprocess.run([str(cli),'--version'],cwd=repo,env=env,capture_output=True,text=True,check=True).stdout.strip(),
        'cli_sha256':sha(cli),'project_config_sha256':sha(repo/'cambc.toml'),'sdk_header_sha256':sha(repo/'sdk/cpp/cambc.h'),
        'engine_version':'0.0.1','statistics_schema':2,'settings':'CLI-default-fuel/full-game/cpp/update-check-disabled',
        'engine_pin_limit':'CLI exposes no engine-file selector; actual engine version is verified from completed-game statistics.'}
    require(runtime['cli_version'],'Empty CLI version')
    patterns=[pat for group in a.maps for pat in group] if a.maps else ['maps/*.map26a','maps_gen/*.map26a','maps_dev200/*.map26a']
    maps=collect_maps(repo,patterns);builds={}
    stamp=now().replace(':','').replace('+','_')+'-'+a.candidate
    run_dir=guard(root/'runs'/stamp)
    with exclusive(root/'locks/build.lock'):
        for name,(bot,meta) in prepared.items():
            for child in bot.rglob('*'):guard(child)
            builds[name]=command([cli,'build',bot],repo,env,run_dir/'logs'/('build-'+name),a.timeout)
    wasm={name:sha(guard(bot/'.cambc/build/bot-injected.wasm')) for name,(bot,meta) in prepared.items()}
    for name,(bot,meta) in prepared.items():require(source_hashes(bot/'src')==meta['source_sha256'],'Source changed during build')
    pairs=[(a.candidate,o) for o in opponents]
    if not a.no_baseline_panel:pairs += [('original',o) for o in selected_spars]
    physical={};slots=[]
    for name,opponent in pairs:
        for index,m in enumerate(maps):
            for side in (0,1):
                an,bn=(name,opponent) if side==0 else (opponent,name)
                identity={'wasm_a_sha256':wasm[an],'wasm_b_sha256':wasm[bn],'map_sha256':m['sha256'],'runtime':runtime}
                key=sha_bytes(json.dumps(identity,sort_keys=True,separators=(',',':')).encode())
                physical.setdefault(key,{'key':key,'identity':identity,'map':m['path'],'bot_a':prepared[an][0],'bot_b':prepared[bn][0],'retain':index==0})
                slots.append({'candidate':name,'opponent':opponent,'side':side,'map_path':str(m['path']),'map_sha256':m['sha256'],'key':key})
    plan={'created_utc':now(),'base_commit':BASE_COMMIT,'spar_commit':SPAR_COMMIT,'candidate':a.candidate,'features':features,
        'sources':{name:meta for name,(bot,meta) in prepared.items()},'wasm_sha256':wasm,'runtime':runtime,
        'maps':[{'path':str(m['path']),'sha256':m['sha256'],'aliases':m['aliases']} for m in maps],
        'semantic_games':len(slots),'unique_physical_games':len(physical),'slots':slots,'build_attempts':builds,
        'unit':'Two sides per map/opponent. Aggregate panel comparisons must cluster all spar/side deltas by map.',
        'independence_limit':'Exact file reuse is deduplicated; correlated/cosmetic map variants need an additional geometry audit.'}
    write(run_dir/'plan.json',plan)

    def unchanged(job):
        require(sha(repo/'cambc.toml')==runtime['project_config_sha256'],'Config changed after planning')
        require(sha(job['map'])==job['identity']['map_sha256'],'Map changed after planning')
        for team in ('a','b'):
            require(sha(guard(job['bot_'+team]/'.cambc/build/bot-injected.wasm'))==job['identity']['wasm_'+team+'_sha256'],'WASM changed after planning')

    def execute(job):
        key,identity=job['key'],job['identity']
        with exclusive(root/'locks'/(key+'.lock'),timeout=a.timeout*5+60):
            unchanged(job);row=cached(root,key,identity)
            if row is not None:return row,False
            execution=time.time_ns();attempts=[]
            for retry in range(4):
                out=guard(root/'games'/key/f'run-{execution}-attempt-{retry+1}');out.mkdir(parents=True,exist_ok=False)
                stats=out/'statistics.json'
                try:proc=subprocess.run([str(cli),'run',str(job['bot_a']),str(job['bot_b']),'--map',str(job['map']),'-o',str(out),'--statistics',str(stats)],cwd=repo,env=env,capture_output=True,text=True,errors='replace',timeout=a.timeout)
                except subprocess.TimeoutExpired as exc:
                    write(out/'timeout.json',{'timeout_seconds':a.timeout});raise RuntimeError('Game timed out '+key) from exc
                text=proc.stdout+proc.stderr
                log=guard(out/'cli.log');log.write_text(text,encoding='utf-8')
                denied=proc.returncode!=0 and not stats.exists() and 'failed to persist temporary file: Access is denied' in text
                attempts.append({'returncode':proc.returncode,'log':str(log),'pre_game_access_denied_retry':denied})
                if denied and retry<3:continue
                require(proc.returncode==0 and stats.is_file(),'Game failed; see '+str(log)+'\n'+text[-2200:]);break
            unchanged(job);data=read(stats);fields=statistics_fields(data)
            replays=list(out.glob('*.repl26a'));require(len(replays)==1,'Expected one replay bundle')
            replay=guard(replays[0]);stdout={}
            with zipfile.ZipFile(replay) as archive:
                require(archive.testzip() is None,'Replay ZIP CRC failure')
                for team in ('a','b'):stdout[team]=audit_stdout(archive.read('team-'+team+'.stdout').decode('utf-8',errors='replace'))
            row={'schema_version':1,'valid':True,'key':key,'identity':identity,'created_utc':now(),**fields,
                'statistics_sha256':sha(stats),'replay_sha256':sha(replay),'stdout':stdout,'execution_attempts':attempts}
            if job['retain'] or any(fields['faults']) or any(v['reinitializations_observed'] for v in stdout.values()):
                retained=guard(root/'retained-replays'/(key+'.repl26a'));retained.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(replay,retained);row['retained_replay']=str(retained.relative_to(root))
            guard(root/'cache').mkdir(exist_ok=True)
            shutil.copyfile(stats,guard(root/'cache'/(key+'.statistics.json')));write(root/'cache'/(key+'.json'),row)
            replay.unlink();stats.unlink()
            return row,True

    results={};new=set()
    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        futures={pool.submit(execute,job):key for key,job in physical.items()}
        for future in as_completed(futures):
            key=futures[future];row,fresh=future.result();results[key]=row
            if fresh:new.add(key)
            if len(results)%20==0 or len(results)==len(physical):print(f'{len(results)}/{len(physical)} unique games resolved ({len(new)} new)',flush=True)
    require(len(results)==len(physical),'Incomplete physical game coverage')
    require(sha(cli)==runtime['cli_sha256'] and sha(repo/'cambc.toml')==runtime['project_config_sha256'] and sha(repo/'sdk/cpp/cambc.h')==runtime['sdk_header_sha256'],'Runtime/config/SDK changed during stage')
    for name,(bot,meta) in prepared.items():
        require(source_hashes(bot/'src')==meta['source_sha256'],'Source changed during stage')
        require(sha(guard(bot/'.cambc/build/bot-injected.wasm'))==wasm[name],'WASM changed during stage')
    for m in maps:require(sha(m['path'])==m['sha256'],'Map changed during stage')
    rows=[{**results[s['key']],**s,'cached':s['key'] not in new} for s in slots]
    fault_games=sum(any(r['faults']) for r in results.values())
    reinit_games=sum(any(t['reinitializations_observed'] for t in r['stdout'].values()) for r in results.values())
    report={'candidate':a.candidate,'features':features,'summary':summary(rows),'completed_utc':now(),'plan_sha256':sha(run_dir/'plan.json'),
        'semantic_games':len(slots),'unique_physical_games':len(physical),'new_unique_games':len(new),'cached_unique_games':len(physical)-len(new),
        'fault_games':fault_games,'reinitialization_games':reinit_games,
        'quality_gate_limit':'Reported botFaults and observed repeated init markers; caught SDK errors and periodic low-fuel status samples are not exact native FuelExhausted counts.',
        'games':rows}
    write(run_dir/'results.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='games'},indent=2));print('Evidence:',run_dir/'results.json')
    print('Use neighboring compare.py on this results file for map-clustered spar-panel outcome deltas.')
    return 0 if fault_games==0 and reinit_games==0 else 2

if __name__=='__main__':
    try:raise SystemExit(main())
    except (RuntimeError,OSError,ValueError,subprocess.CalledProcessError) as exc:
        print('ERROR:',exc,file=sys.stderr);raise SystemExit(1)

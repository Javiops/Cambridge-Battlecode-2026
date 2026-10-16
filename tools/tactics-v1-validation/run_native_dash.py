"""Run actual Ren/Issac dash path and production mutation-gateway regressions locally."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cli',required=True,type=Path)
    p.add_argument('--project',required=True,type=Path)
    p.add_argument('--source',type=Path,default=HERE.parents[1]/'bots/tactics-v1/src')
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    cli,project,source,output=[v.resolve()for v in (args.cli,args.project,args.source,args.output)]
    output.mkdir(parents=True,exist_ok=False)
    sdk=project/'sdk/cpp/cambc.h'
    if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':
        raise ValueError('Review SDK pin before crediting native dash regression')
    headers={v.name:sha(v)for v in source.glob('*.h')}
    commands=[]
    def invoke(command,label):
        result=subprocess.run([str(v)for v in command],cwd=project,
            env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
        (output/(label+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
        commands.append([str(v)for v in command])
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    bots={}
    def build_fixture(name):
        if name in bots:return bots[name]
        bot=output/Path(name).stem;(bot/'src').mkdir(parents=True)
        for header in headers:shutil.copy2(source/header,bot/'src'/header)
        fixture=HERE/'fixtures'/name;shutil.copy2(fixture,bot/'src/main.cpp')
        invoke([cli,'build',bot],Path(name).stem+'-build-normal')
        invoke([cli,'build',bot,'--release'],Path(name).stem+'-build-release')
        bots[name]=(bot,fixture)
        return bot,fixture
    manifest=json.loads((HERE/'fixtures/native-dash-maps.json').read_text())
    games=[]
    for case in manifest['maps']:
        bot,fixture=build_fixture(case.get('fixture','native-dash.cpp'))
        map_path=HERE/'fixtures'/case['file']
        if sha(map_path)!=case['sha256']:raise ValueError('Native dash map changed')
        game=output/case['case'];game.mkdir();stats=game/'statistics.json'
        invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',stats],case['case'])
        data=json.loads(stats.read_text())
        if data['match']['engineVersion']!='0.0.2':raise ValueError('Unexpected native engine')
        replay=list(game.glob('*.repl26a'))
        if len(replay)!=1:raise ValueError('Expected one native replay')
        markers={}
        with zipfile.ZipFile(replay[0])as archive:
            if archive.testzip()is not None:raise ValueError('Replay CRC failed')
            for letter,body in [('a',0),('b',1)]:
                text=archive.read('team-'+letter+'.stdout').decode('utf8',errors='replace').replace('\0','')
                markers[letter]=re.findall(r'NATIVE_(?:DASH_GATEWAY|DASH_OCCUPIED|MUTATION_BUDGET)_PASS [^\r\n]+',text)
                expected=case.get('markers',{}).get(letter,[f"NATIVE_DASH_GATEWAY_PASS {body} {int(case['case']=='wall-barrier')}"])
                if sorted(markers[letter])!=sorted(expected):raise ValueError(f'Missing gateway checks: {case}: {markers}')
                if re.search(r'TACTICS_ERROR|bot error:|\[err',text):raise ValueError('Native fixture error')
        if any(data['diagnostics']['botFaults'].values()):raise ValueError('Native fault')
        fuel=sum(len(event['entries'])for event in data['events']if event['kind']=='fuelExhausted')
        if fuel:raise ValueError('Native fixture fuel exhaustion')
        games.append({'case':case['case'],'map_sha256':sha(map_path),'replay_sha256':sha(replay[0]),
            'statistics_sha256':sha(stats),'actual_match':data['match'],'markers':markers,
            'fixture_sha256':sha(fixture),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),
            'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel})
    if headers!={v.name:sha(v)for v in source.glob('*.h')}:raise ValueError('Production source changed during check')
    report={'passed':True,'created_utc':datetime.now(timezone.utc).isoformat(),'source_headers_sha256':headers,
        'cli_sha256':sha(cli),'sdk_header_sha256':sha(sdk),'games':games,'commands':commands,
        'scope':'Actual SDK range masks, wall/occupied unique-diagonal path rejection, legal hole crossing and bent paths, stale-epoch and secondary mutation-budget gates. Scripted correctness fixture, not strength evidence.'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'passed':True,'games':len(games),'markers':[v['markers']for v in games]},indent=2))

if __name__=='__main__':main()

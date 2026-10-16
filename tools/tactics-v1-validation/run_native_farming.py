"""Run the actual native farming-policy projection regression locally."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli',required=True,type=Path)
    parser.add_argument('--project',required=True,type=Path)
    parser.add_argument('--source',type=Path,default=HERE.parents[1]/'bots/tactics-v1/src')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    cli,project,source,output=[p.resolve()for p in (args.cli,args.project,args.source,args.output)]
    output.mkdir(parents=True,exist_ok=False)
    sdk=project/'sdk/cpp/cambc.h'
    if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':
        raise ValueError('Native fixture requires reviewed official SDK2.2.2')
    headers={p.name:sha(p)for p in source.glob('*.h')}
    bot=output/'native-farming';(bot/'src').mkdir(parents=True)
    for name in headers:
        shutil.copy2(source/name,bot/'src'/name)
    shutil.copy2(HERE/'fixtures/native-farming.cpp',bot/'src/main.cpp')
    map_path=HERE/'fixtures/native-lifecycle.map26a'
    meta=json.loads((HERE/'fixtures/native-lifecycle-map.json').read_text())
    if sha(map_path)!=meta['map_sha256']:
        raise ValueError('Native scenario map changed')
    commands=[]
    def invoke(command,label):
        result=subprocess.run([str(x)for x in command],cwd=project,
            env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
        (output/(label+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
        commands.append([str(x)for x in command])
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    invoke([cli,'build',bot],'build-normal')
    invoke([cli,'build',bot,'--release'],'build-release')
    game=output/'game';game.mkdir();statistics=game/'statistics.json'
    invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',statistics],'run')
    data=json.loads(statistics.read_text())
    if data['match']['engineVersion']!='0.0.2':raise ValueError('Unexpected actual engine')
    replay=list(game.glob('*.repl26a'))
    if len(replay)!=1:raise ValueError('Expected one native replay')
    markers={}
    with zipfile.ZipFile(replay[0])as archive:
        if archive.testzip()is not None:raise ValueError('Replay CRC failed')
        for letter,body in [('a',0),('b',1)]:
            text=archive.read('team-'+letter+'.stdout').decode('utf8',errors='replace').replace('\0','')
            markers[letter]=re.findall(r'NATIVE_FARM_POLICY_PASS [^\r\n]+',text)
            if len(markers[letter])!=1 or markers[letter][0]!=f'NATIVE_FARM_POLICY_PASS {body}':
                raise ValueError(f'Missing native farming marker: {markers[letter]}')
            for case in ('suppressed-incumbent','first-clear-arrival','deadline-zero-ready','spent-move-observation','spawn-heal-before-delivery'):
                if text.count('NATIVE_FARM_POLICY_CASE_PASS '+case)!=1:
                    raise ValueError(f'Missing/duplicate farming policy case {case}: team {letter}')
            if re.search(r'TACTICS_ERROR|bot error:|\[err',text):raise ValueError('Native fixture caught an error')
    if any(data['diagnostics']['botFaults'].values()):raise ValueError('Native fault')
    fuel=sum(len(event['entries'])for event in data['events']if event['kind']=='fuelExhausted')
    if fuel:raise ValueError('Native fixture fuel-exhausted')

    if headers!={p.name:sha(p)for p in source.glob('*.h')}:raise ValueError('Production source changed during native validation')
    result={'passed':True,'created_utc':datetime.now(timezone.utc).isoformat(),'source_headers_sha256':headers,
            'cli_sha256':sha(cli),'sdk_header_sha256':sha(sdk),'fixture_sha256':sha(HERE/'fixtures/native-farming.cpp'),
            'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'map_sha256':sha(map_path),
            'replay_sha256':sha(replay[0]),'statistics_sha256':sha(statistics),'actual_engine':data['match'],
            'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel,'markers':markers,'commands':commands,
            'scope':'Actual production farming policy with explicit projected World inputs under initialized native SDK. Failed-incumbent suppression, first-clear arrival, and deadline-zero-ready ranking assertions; not physical camp clear/payout or strength evidence.'}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'passed':True,'markers':markers,'native_faults':result['native_faults'],'fuel_exhausted':fuel},indent=2))


if __name__=='__main__':main()

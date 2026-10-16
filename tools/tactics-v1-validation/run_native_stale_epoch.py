"""Native stale-world guards, real dead-owner mask control, and retained live dash."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, zipfile
from pathlib import Path
from datetime import datetime, timezone
HERE=Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('cli','project','source','output'): p.add_argument('--'+name, required=True,type=Path)
    a=p.parse_args(); cli,project,source,output=[x.resolve()for x in(a.cli,a.project,a.source,a.output)]
    output.mkdir(parents=True,exist_ok=False)
    sdk=project/'sdk/cpp/cambc.h'
    if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4': raise ValueError('Unreviewed SDK')
    headers={x.name:sha(x)for x in source.glob('*.h')}
    fixture=HERE/'fixtures/native-stale-epoch.cpp';bot=output/'native-stale-epoch';(bot/'src').mkdir(parents=True)
    for name in headers: shutil.copy2(source/name,bot/'src'/name)
    shutil.copy2(fixture,bot/'src/main.cpp')
    map_path=HERE/'fixtures/native-lifecycle.map26a'
    if sha(map_path)!=json.loads((HERE/'fixtures/native-lifecycle-map.json').read_text())['map_sha256']:raise ValueError('Map changed')
    commands=[]
    def invoke(command,label):
        command=[str(x)for x in command];commands.append(command)
        r=subprocess.run(command,cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
        (output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    invoke([cli,'build',bot],'build-normal');invoke([cli,'build',bot,'--release'],'build-release')
    game=output/'game';game.mkdir();statistics=game/'statistics.json'
    invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',statistics],'run')
    data=json.loads(statistics.read_text());replay=list(game.glob('*.repl26a'))
    if data['match']['engineVersion']!='0.0.2' or len(replay)!=1:raise ValueError('Unexpected native version/replay')
    markers={};failures=[]
    with zipfile.ZipFile(replay[0])as z:
        if z.testzip() is not None:raise ValueError('Replay CRC')
        for side in('a','b'):
            text=z.read('team-'+side+'.stdout').decode('utf8',errors='replace').replace('\0','')
            markers[side]=re.findall(r'NATIVE_EPOCH[^\r\n]+',text)
            for case in('live-dash-selected','expected-dead-mask-5','old-alive-all-decline','low-budget-declines'):
                if text.count('NATIVE_EPOCH_CASE_PASS '+case)!=1:failures.append(side+':'+case)
            if text.count('NATIVE_EPOCH_PASS ')!=1 or re.search(r'NATIVE_EPOCH_FAIL|TACTICS_ERROR|bot error:|\[err',text):failures.append(side+':fault-marker')
    fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
    if fuel or any(data['diagnostics']['botFaults'].values()):failures.append('native-fault-or-fuel')
    if headers!={x.name:sha(x)for x in source.glob('*.h')}:failures.append('source-changed')
    report={'passed':not failures,'created_utc':datetime.now(timezone.utc).isoformat(),'source_headers_sha256':headers,'fixture_sha256':sha(fixture),'sdk_header_sha256':sha(sdk),'cli_sha256':sha(cli),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'map_sha256':sha(map_path),'replay_sha256':sha(replay[0]),'statistics_sha256':sha(statistics),'actual_engine':data['match'],'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel,'expected_caught_control_error_code':5,'unexpected_errors':failures,'markers':markers,'commands':commands,'scope':'Actual Ren death from awake elk; official SDK dead-owner valid_tiles control must throw5. Actual production helpers decline old-epoch alive projections and an explicitly contradictory unfunded live projection; funded current-epoch dash selection remains reachable under a synthetic awake-camp threat. Scripted fixture, not strength or unmodified production main evidence.'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':report['passed'],'failures':failures,'markers':markers,'fuel':fuel},indent=2))
    if failures:raise SystemExit(1)
if __name__=='__main__':main()

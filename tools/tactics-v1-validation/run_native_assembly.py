"""Native physical assembly rendezvous, readiness and capture under actual SDK."""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('cli','project','source','output'):p.add_argument('--'+name,required=True,type=Path)
 a=p.parse_args();cli,project,source,output=[x.resolve()for x in(a.cli,a.project,a.source,a.output)];output.mkdir(parents=True,exist_ok=False)
 sdk=project/'sdk/cpp/cambc.h'
 if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('Unreviewed SDK')
 hashes={x.name:sha(x)for x in source.glob('*.h')};bot=output/'native-assembly';(bot/'src').mkdir(parents=True)
 for name in hashes:shutil.copy2(source/name,bot/'src'/name)
 fixture=HERE/'fixtures/native-assembly.cpp';shutil.copy2(fixture,bot/'src/main.cpp');map_path=HERE/'fixtures/native-assembly.map26a'
 if sha(map_path)!='1ba7731349d9e84cbb02943c00537c20671e9cb75933bd3156b550006c8475a9':raise ValueError('Map changed')
 commands=[]
 def invoke(c,label):
  c=[str(x)for x in c];commands.append(c);r=subprocess.run(c,cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600);(output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 invoke([cli,'build',bot],'build-normal');invoke([cli,'build',bot,'--release'],'build-release');game=output/'game';game.mkdir();stats=game/'statistics.json'
 invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',stats],'run')
 d=json.loads(stats.read_text());replay=next(game.glob('*.repl26a'));failures=[];markers={}
 with zipfile.ZipFile(replay)as z:
  for side in('a','b'):
   text=z.read('team-'+side+'.stdout').decode(errors='replace').replace(chr(0),'');markers[side]=re.findall(r'NATIVE_ASSEMBLY[^\r\n]+',text)
   for case in('physical-helper-stage','real-upgrade-healed','actual-claimed-pair-ready','actual-first-hit','actual-clear','actual-capture-payout'):
    if text.count('NATIVE_ASSEMBLY_CASE_PASS '+case)!=1:failures.append(side+':'+case)
   if text.count('NATIVE_ASSEMBLY_PASS ')!=1 or re.search(r'NATIVE_ASSEMBLY_FAIL|TACTICS_ERROR|bot error:|\[err',text):failures.append(side+':fault-marker')
 fuel=sum(len(e['entries'])for e in d['events']if e['kind']=='fuelExhausted')
 if fuel or any(d['diagnostics']['botFaults'].values()):failures.append('native-fault-or-fuel')
 if hashes!={x.name:sha(x)for x in source.glob('*.h')}:failures.append('source-changed')
 report={'passed':not failures,'created_utc':datetime.now(timezone.utc).isoformat(),'source_headers_sha256':hashes,'fixture_sha256':sha(bot/'src/main.cpp'),'sdk_header_sha256':sha(sdk),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'map_sha256':sha(map_path),'replay_sha256':sha(replay),'statistics_sha256':sha(stats),'actual_engine':d['match'],'native_faults':d['diagnostics']['botFaults'],'fuel_exhausted':fuel,'failures':failures,'markers':markers,'commands':commands,'scope':'Actual Vendetta/Willow bodies, legal harmless gold capture, one real Health shard, spawn heal, physical staging and shared claims; production current local readiness authorizes actual gateway first hit; scripted actual teammate heal/damage then clear and capture payout. Optional actual priced producer reported separately. No World projections. Macro strength and global production farming arbitration not established.'}
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':not failures,'failures':failures,'markers':{s:x[:14]for s,x in markers.items()},'fuel':fuel},indent=2))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()






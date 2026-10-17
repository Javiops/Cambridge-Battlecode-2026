"""Run exact bank policy/coordinator projections with the official native SDK."""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('cli','project','source','output'):p.add_argument('--'+name,required=True,type=Path)
 a=p.parse_args();cli,project,source,output=[x.resolve()for x in(a.cli,a.project,a.source,a.output)]
 output.mkdir(parents=True,exist_ok=False);sdk=project/'sdk/cpp/cambc.h'
 if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('Unreviewed SDK')
 hashes={x.name:sha(x)for x in source.glob('*.h')};bot=output/'native-bank';(bot/'src').mkdir(parents=True)
 for name in hashes:shutil.copy2(source/name,bot/'src'/name)
 fixture=HERE/'fixtures/native-bank.cpp';shutil.copy2(fixture,bot/'src/main.cpp')
 map_path=HERE/'fixtures/native-bank.map26a'
 if sha(map_path)!=json.loads((HERE/'fixtures/native-bank-map.json').read_text())['map_sha256']:raise ValueError('Native map changed')
 commands=[]
 def invoke(c,label):
  c=[str(x)for x in c];commands.append(c);r=subprocess.run(c,cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600);(output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 invoke([cli,'build',bot],'build-normal');invoke([cli,'build',bot,'--release'],'build-release')
 game=output/'game';game.mkdir();stats=game/'statistics.json'
 invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',stats],'run')
 d=json.loads(stats.read_text());replay=next(game.glob('*.repl26a'));markers={};failures=[]
 with zipfile.ZipFile(replay)as z:
  if z.testzip()is not None:raise ValueError('Replay CRC')
  for side in('a','b'):
   text=z.read('team-'+side+'.stdout').decode(errors='replace').replace(chr(0),'');markers[side]=re.findall(r'NATIVE_BANK[^\r\n]+',text)
   for case in('ring-coordinator','recovery-hook','healed-backoff','accepted-start-not-complete','completed-bank-reentry','bounded-cost'):
    if text.count('NATIVE_BANK_CASE_PASS '+case)!=1:failures.append(side+':'+case)
   if text.count('NATIVE_BANK_PASS ')!=1 or re.search(r'NATIVE_BANK_FAIL|TACTICS_ERROR|bot error:|\[err',text):failures.append(side+':fault-marker')
 fuel=sum(len(e['entries'])for e in d['events']if e['kind']=='fuelExhausted')
 if fuel or any(d['diagnostics']['botFaults'].values()):failures.append('native-fault-or-fuel')
 if hashes!={x.name:sha(x)for x in source.glob('*.h')}:failures.append('source-changed')
 report={'passed':not failures,'created_utc':datetime.now(timezone.utc).isoformat(),'source_headers_sha256':hashes,'fixture_sha256':sha(fixture),'sdk_header_sha256':sha(sdk),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'map_sha256':sha(map_path),'replay_sha256':sha(replay),'statistics_sha256':sha(stats),'actual_engine':d['match'],'native_faults':d['diagnostics']['botFaults'],'fuel_exhausted':fuel,'failures':failures,'markers':markers,'commands':commands,'scope':'Actual production choose_mission/delivery/observe_progress under explicit World threat/position/life/bag projections. SDK initialized and actual public terrain/altars; no projected action executed. Confirms coordinator ring priority, actual recovery-selection hook, finite uncertainty backoff and accepted-start versus completed-bank observation input. Does not prove real payout, physical movement or strength; separate actual cycle fixture/integration required.'}
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':not failures,'failures':failures,'markers':{s:x[:12]for s,x in markers.items()},'fuel':fuel},indent=2))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()

"""Actual Varg shield carry and expiry against one native Wolf20."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in['cli','project','source','output']:p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--existing',action='store_true');p.add_argument('--map',type=Path);p.add_argument('--fixture',type=Path);p.add_argument('--expect-raw',action='store_true');a=p.parse_args();cli,project,source,out=[getattr(a,n).resolve()for n in['cli','project','source','output']];here=Path(__file__).resolve().parent;bot=out/'bot';game=out/'game';mapfile=a.map.resolve()if a.map else here/'fixture.map26a'
 if not a.existing:
  (bot/'src').mkdir(parents=True,exist_ok=False)
  for h in source.glob('*.h'):shutil.copy2(h,bot/'src'/h.name)
  shutil.copy2(a.fixture.resolve()if a.fixture else here/'fixture.cpp',bot/'src/main.cpp')
  shutil.copy2(mapfile,out/'fixture.map26a')
 def invoke(cmd,label):
  r=subprocess.run([str(x)for x in cmd],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600);(out/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 stats=game/'statistics.json'
 if not a.existing:
  invoke([cli,'build',bot],'normal-build');invoke([cli,'build',bot,'--release'],'release-build');game.mkdir();invoke([cli,'run',bot,bot,'--map',mapfile,'--release','--json','-o',game,'--statistics',stats],'run')
 data=json.loads(stats.read_text());repl,=game.glob('*.repl26a');texts={};failures=[];allmarkers={}
 with zipfile.ZipFile(repl)as z:
  for side in ['a','b']:
   t=z.read('team-'+side+'.stdout').decode(errors='replace').replace('\0','');texts[side]=t;(out/('stdout-'+side+'.txt')).write_text(t,encoding='utf8');markers=re.findall(r'(?:CREW_PHYSICAL|RAW_STRIDE18|PREPARED18|SHIELD_CLOCK)[^\r\n]+',t);allmarkers[side]=markers
   if t.count('SHIELD_CLOCK_PASS') != (1 if side=='a' else 0): failures.append(side+':expected-native-cases')
   if re.search('CREW_PHYSICAL_FAIL|CREW_PHYSICAL_EXCEPTION|SHIELD_CLOCK_FAIL|SHIELD_CLOCK_EXCEPTION|TACTICS_ERROR',t):failures.append(side+':error-marker')
  raw=z.read('replay.repl26a')
 rows=re.findall(r'SHIELD_CLOCK (IMMEDIATE|NEXT) round=(\d+) actor=(\d+) hp=([\d.]+) shield=([\d.]+) ticks=(-?\d+) read=([\d.]+),(-?\d+)',texts['a'])
 expected=[(1000.,250.,5),(1000.,230.,4),(1000.,210.,3),(1000.,190.,2),(1000.,170.,1),(1000.,0.,-1),(980.,0.,-1)]
 if len(rows)!=7:failures.append('shield-clock-ledger-count')
 else:
  for i,row in enumerate(rows):
   phase,epoch,actor,hp,shield,ticks,read,readticks=row
   if (float(hp),float(shield),int(ticks))!=expected[i] or (float(read),int(readticks))!=(float(shield),int(ticks)) or int(epoch)!=int(rows[0][1])+i:failures.append('shield-clock-ledger-value')
 fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
 if fuel or any(data['diagnostics']['botFaults'].values()):failures.append('native-fuel-or-fault')
 trace=out/'native-trace';trace.mkdir(exist_ok=True);rf=trace/'crew-physical.repl26a';rf.write_bytes(raw)
 req={'id':'crew-physical','raw':str(rf),'raw_sha256':sha(rf),'map':'controlled-three-camp','kind':'native-physical-crew','created_at':None,'teams':{'a':{'teamId':'candidate-a','name':'candidate-a'},'b':{'teamId':'candidate-b','name':'candidate-b'}},'replay_patch':'0.0.2','game':{'rounds':data['match']['roundsStarted'],'sides':[{'side':'a','teamId':'candidate-a','score':int(data['teams'][0]['submittedGems']),'draft':[]},{'side':'b','teamId':'candidate-b','score':int(data['teams'][1]['submittedGems']),'draft':[]}]}}
 (trace/'manifest.json').write_text(json.dumps({'requests':[req]},indent=2)+'\n')
 scope='Actual Varg shield with known duration5 against one actual native Wolf20. Scripted legal approach, real shield and basic; subsequent actual SDK snapshots measure carry and expiry. Team B idles.'
 report={'passed':not failures,'scope':scope,'failures':failures,'fuel':fuel,'faults':data['diagnostics']['botFaults'],'markers':allmarkers,'source_sha256':{h.name:sha(h)for h in(bot/'src').iterdir()},'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'map_sha256':sha(mapfile),'statistics_sha256':sha(stats),'replay_sha256':sha(repl),'sdk_sha256':sha(project/'sdk/cpp/cambc.h')}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['passed','failures','fuel','faults']},indent=2))
if __name__=='__main__':main()

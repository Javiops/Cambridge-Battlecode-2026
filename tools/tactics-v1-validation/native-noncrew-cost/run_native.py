"""Native microbenchmark of unflagged coalition receipt construction and caller admission."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in['cli','project','source','output']:p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--existing',action='store_true');p.add_argument('--map',type=Path);p.add_argument('--fixture',type=Path);p.add_argument('--expect-raw',action='store_true');a=p.parse_args();cli,project,source,out=[getattr(a,n).resolve()for n in['cli','project','source','output']];here=Path(__file__).resolve().parent;bot=out/'bot';game=out/'game';mapfile=a.map.resolve()if a.map else here/'fixture.map26a'
 if sha(project/'sdk/cpp/cambc.h')!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('Expected official SDK 2.2.2')
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
   t=z.read('team-'+side+'.stdout').decode(errors='replace').replace('\0','');texts[side]=t;(out/('stdout-'+side+'.txt')).write_text(t,encoding='utf8');markers=re.findall(r'(?:CREW_PHYSICAL|RAW_STRIDE18|PREPARED18|NONCREW18)[^\r\n]+',t);allmarkers[side]=markers
   if t.count('NONCREW18 actor=') != (3 if side=='a' else 0): failures.append(side+':expected-native-cases')
   if re.search('CREW_PHYSICAL_FAIL|CREW_PHYSICAL_EXCEPTION|TACTICS_ERROR',t):failures.append(side+':error-marker')
  raw=z.read('replay.repl26a')
 samples=re.findall(r'NONCREW18 actor=(\d+) nativeCost=(\d+) valid=(\d+) required=(\d+)',texts['a'])
 gated=re.findall(r'NONCREW18_GATED actor=(\d+) nativeCost=(\d+) valid=(\d+) required=(\d+)',texts['a'])
 if len(samples)!=3 or len(gated)!=3 or any(row[2:]!=('0','0') for row in samples+gated):failures.append('receipt-flags-or-samples')
 fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
 if fuel or any(data['diagnostics']['botFaults'].values()):failures.append('native-fuel-or-fault')
 trace=out/'native-trace';trace.mkdir(exist_ok=True);rf=trace/'crew-physical.repl26a';rf.write_bytes(raw)
 req={'id':'crew-physical','raw':str(rf),'raw_sha256':sha(rf),'map':'controlled-three-camp','kind':'native-physical-crew','created_at':None,'teams':{'a':{'teamId':'candidate-a','name':'candidate-a'},'b':{'teamId':'candidate-b','name':'candidate-b'}},'replay_patch':'0.0.2','game':{'rounds':data['match']['roundsStarted'],'sides':[{'side':'a','teamId':'candidate-a','score':int(data['teams'][0]['submittedGems']),'draft':[]},{'side':'b','teamId':'candidate-b','score':int(data['teams'][1]['submittedGems']),'draft':[]}]}}
 (trace/'manifest.json').write_text(json.dumps({'requests':[req]},indent=2)+'\n')
 scope='Native microbenchmark: actual SDK World snapshot and an opaque synthetic runtime unflagged Proposal. Measures unchanged production receipt helper versus a caller validity gate; no production chooser, executed action or whole-main behavior proof.'
 report={'samples':samples,'gated_samples':gated,'passed':not failures,'scope':scope,'failures':failures,'fuel':fuel,'faults':data['diagnostics']['botFaults'],'markers':allmarkers,'source_sha256':{h.name:sha(h)for h in(bot/'src').iterdir()},'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'map_sha256':sha(mapfile),'statistics_sha256':sha(stats),'replay_sha256':sha(repl),'sdk_sha256':sha(project/'sdk/cpp/cambc.h')}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in['passed','failures','fuel','faults']},indent=2))
if __name__=='__main__':main()

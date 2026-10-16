"""Build/run the scoped actual-SDK out-of-range farm-readiness regression.

The fixture uses real map geometry, kit, permissions and native movements. It
is not the Bot main class or a gameplay-strength benchmark. If one side's
scripted observation path meets another camp's reply zone, that side safely
stops; at least one side must exercise the exact quote and seven-owner wait.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['cli','project','source','output']:p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--existing',action='store_true')
 a=p.parse_args();cli,project,source,output=[getattr(a,n).resolve()for n in ['cli','project','source','output']]
 bot=output/'bot';commands=[]
 if not a.existing:
  output.mkdir(parents=True,exist_ok=False);(bot/'src').mkdir(parents=True)
  before={h.name:sha(h)for h in source.glob('*.h')}
  for h in source.glob('*.h'):shutil.copy2(h,bot/'src'/h.name)
  if before!={h.name:sha(h)for h in source.glob('*.h')}:raise RuntimeError('Source changed while copying; use a frozen source')
  shutil.copy2(HERE/'fixtures/native-farm-readiness.cpp',bot/'src/main.cpp')
 def invoke(cmd,label):
  commands.append([str(v)for v in cmd]);r=subprocess.run(commands[-1],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
  (output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 game=output/'game';stats=game/'statistics.json'
 if not a.existing:
  invoke([cli,'build',bot],'normal');invoke([cli,'build',bot,'--release'],'release');game.mkdir()
  invoke([cli,'run',bot,bot,'--map',project/'maps/corners.map26a','--release','--json','-o',game,'--statistics',stats],'run')
 data=json.loads(stats.read_text());markers={}
 with zipfile.ZipFile(next(game.glob('*.repl26a')))as archive:
  for team in ['a','b']:
   text=archive.read('team-'+team+'.stdout').decode(errors='replace').replace('\0','');(game/('team-'+team+'.stdout.txt')).write_text(text,encoding='utf8')
   assert 'NATIVE_FARM_READY_FAIL'not in text,text[:1000]
   markers[team]={name:re.findall(pattern+r' ([^\r\n]+)',text)for name,pattern in [('quote','NATIVE_FARM_READY_QUOTE'),('pass','NATIVE_FARM_READY_PASS'),('script_blocked','NATIVE_FARM_READY_SCRIPT_BLOCKED')]}
 assert any(m['pass']for m in markers.values()),markers
 fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted');assert fuel==0,fuel
 assert not any(data['diagnostics']['botFaults'].values()),data['diagnostics']['botFaults']
 report={'passed':True,'scope':__doc__,'markers':markers,'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel,'source_sha256':{h.name:sha(h)for h in(bot/'src').glob('*.h')},'fixture_sha256':sha(bot/'src/main.cpp'),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'actual_engine':data['match'],'commands':commands,'retained_reanalysis':a.existing}
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':True,'markers':markers,'fuel':fuel},indent=2))
if __name__=='__main__':main()

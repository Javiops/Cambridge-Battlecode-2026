from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for n in ['cli','project','source','output']:p.add_argument('--'+n,required=True,type=Path)
 a=p.parse_args();cli,project,source,output=[getattr(a,n).resolve()for n in ['cli','project','source','output']];output.mkdir(parents=True,exist_ok=False)
 bot=output/'bot';(bot/'src').mkdir(parents=True)
 for h in source.glob('*.h'):shutil.copy2(h,bot/'src'/h.name)
 shutil.copy2(HERE/'fixtures/native-early-solo.cpp',bot/'src/main.cpp');commands=[]
 def run(args,label):
  commands.append(list(map(str,args)));r=subprocess.run(commands[-1],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600);(output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 run([cli,'build',bot],'normal');run([cli,'build',bot,'--release'],'release');game=output/'game';game.mkdir();stats=game/'statistics.json'
 run([cli,'run',bot,bot,'--map',project/'maps/lanes.map26a','--release','--json','-o',game,'--statistics',stats],'run')
 data=json.loads(stats.read_text());replay,=game.glob('*.repl26a');markers={};fail=[]
 with zipfile.ZipFile(replay)as z:
  for side in ['a','b']:
   text=z.read('team-'+side+'.stdout').decode(errors='replace').replace(chr(0),'');(game/('team-'+side+'.stdout.txt')).write_text(text,encoding='utf8');markers[side]=re.findall(r'EARLY_SOLO[^\r\n]+',text)
   if len(re.findall(r'EARLY_SOLO_PASS',text))!=1 or re.search(r'EARLY_SOLO_FAIL|TACTICS_ERROR|bot error:|\[err',text):fail.append(side+':markers')
 fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
 if fuel or any(data['diagnostics']['botFaults'].values()):fail.append('fault-or-fuel')
 report={'passed':not fail,'failures':fail,'markers':markers,'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel,'source_sha256':{h.name:sha(h)for h in(bot/'src').glob('*.h')},'fixture_sha256':sha(bot/'src/main.cpp'),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'actual_engine':data['match'],'commands':commands,'scope':'Actual native Issac900HP/40STR legally walks to an actual1350HP singleton Wolf. Cold completed-field removal uses the bounded visible local route with no partial fullcache insertion; at62k warm production full-cycle quote and common/early SOLO proposal produce current basic with reserve. Proposal NOT executed; physical whole-main proof is separate.'}
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if fail:raise SystemExit(1)
if __name__=='__main__':main()

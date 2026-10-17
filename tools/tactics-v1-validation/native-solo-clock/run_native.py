"""Actual unupgraded Cassi basic/damage schedule against native Wolf20."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in('cli','project','source','output'):p.add_argument('--'+name,required=True,type=Path)
 p.add_argument('--map',type=Path);p.add_argument('--fixture',type=Path)
 a=p.parse_args();cli,project,source,out=(getattr(a,n).resolve()for n in('cli','project','source','output'));here=Path(__file__).resolve().parent;mapfile=a.map.resolve()if a.map else here/'fixture.map26a';fixture=a.fixture.resolve()if a.fixture else here/'fixture.cpp';bot=out/'bot';game=out/'game'
 if sha(project/'sdk/cpp/cambc.h')!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('Expected officialSDK2.2.2')
 (bot/'src').mkdir(parents=True,exist_ok=False)
 for h in source.glob('*.h'):shutil.copy2(h,bot/'src'/h.name)
 shutil.copy2(fixture,bot/'src/main.cpp');shutil.copy2(mapfile,out/'fixture.map26a')
 def invoke(cmd,label):
  r=subprocess.run(list(map(str,cmd)),cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600);(out/(label+'.log')).write_text(r.stdout+r.stderr)
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 invoke([cli,'build',bot],'normal-build');invoke([cli,'build',bot,'--release'],'release-build');game.mkdir();stats=game/'statistics.json';invoke([cli,'run',bot,bot,'--map',mapfile,'--release','--json','-o',game,'--statistics',stats],'run')
 data=json.loads(stats.read_text());replay,=game.glob('*.repl26a');markers={};failures=[]
 with zipfile.ZipFile(replay)as z:
  for side in('a','b'):
   text=z.read('team-'+side+'.stdout').decode(errors='replace').replace('\0','');(out/('stdout-'+side+'.txt')).write_text(text);markers[side]=re.findall(r'SOLO_CLOCK[^\r\n]+',text)
   if text.count('SOLO_CLOCK_PASS')!=(1 if side=='a' else 0):failures.append(side+':missing-native-proof')
   if re.search(r'SOLO_CLOCK_(FAIL|EXCEPTION)|TACTICS_ERROR',text):failures.append(side+':error-marker')
 fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
 if fuel or any(data['diagnostics']['botFaults'].values()):failures.append('native-fuel-or-fault')
 if data['match']['engineVersion']!='0.0.2'or data['match']['engineBuildHash']!='02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede':failures.append('native-engine-mismatch')
 report={'passed':not failures,'scope':__doc__+' Actual native metadata, movement, HP, actions and camp phases; no World/stat/HP/score projections. Scripted stationary clear, not whole Bot main activation.','failures':failures,'fuel':fuel,'faults':data['diagnostics']['botFaults'],'markers':markers,'source_sha256':{h.name:sha(h)for h in(bot/'src').iterdir()},'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'map_sha256':sha(mapfile),'sdk_sha256':sha(project/'sdk/cpp/cambc.h'),'statistics_sha256':sha(stats),'replay_sha256':sha(replay),'engine':data['match']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in('passed','fuel','faults','markers','failures')},indent=2))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()

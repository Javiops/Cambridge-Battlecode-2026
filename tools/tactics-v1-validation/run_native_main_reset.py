"""Validate actual full-main certified basic/reset/basic activation locally.

Uses the supplied unmodified production main.cpp on official Lanes against an
opponent that drafts and otherwise idles. Every accepted certified farming
reset must have a damaging-basic command before it and the consumed-once
receipt basic immediately afterwards in the same owner round. Successful SDK
mutation logs are checked here; independent native replay decoding can be run
on the retained replay/manifest. This is activation, not a strength comparison.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent
SDK_SHA='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['cli','project','source','output']:p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--existing',action='store_true')
 a=p.parse_args();cli,project,source,output=[getattr(a,n).resolve()for n in ['cli','project','source','output']]
 if sha(project/'sdk/cpp/cambc.h')!=SDK_SHA:raise ValueError('Native proof requires reviewed official SDK2.2.2')
 bot=output/'bot';quiet=output/'quiet';commands=[]
 if not a.existing:
  output.mkdir(parents=True,exist_ok=False);(bot/'src').mkdir(parents=True);(quiet/'src').mkdir(parents=True)
  before={h.name:sha(h)for h in source.iterdir()if h.is_file()and(h.suffix=='.h'or h.name=='main.cpp')}
  for name in before:shutil.copy2(source/name,bot/'src'/name)
  if before!={h.name:sha(h)for h in source.iterdir()if h.is_file()and(h.suffix=='.h'or h.name=='main.cpp')}:raise RuntimeError('Source changed while copying; use a frozen source')
  shutil.copy2(HERE/'fixtures/native-quiet.cpp',quiet/'src/main.cpp')
 def invoke(cmd,label):
  commands.append([str(v)for v in cmd]);r=subprocess.run(commands[-1],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
  (output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 game=output/'game';statistics=game/'statistics.json';mapfile=project/'maps/lanes.map26a'
 if not a.existing:
  for name,folder in [('candidate',bot),('quiet',quiet)]:
   invoke([cli,'build',folder],name+'-normal');invoke([cli,'build',folder,'--release'],name+'-release')
  game.mkdir();invoke([cli,'run',bot,quiet,'--map',mapfile,'--release','--json','-o',game,'--statistics',statistics],'run')
 data=json.loads(statistics.read_text());replay,=game.glob('*.repl26a');rows=[]
 with zipfile.ZipFile(replay)as z:
  text=z.read('team-a.stdout').decode(errors='replace').replace('\0','');(game/'team-a.stdout.txt').write_text(text,encoding='utf8');raw=z.read('replay.repl26a')
 if 'TACTICS_ERROR'in text:raise ValueError('Caught production error')
 for line in text.splitlines():
  fields=line.split()
  if len(fields)==8 and fields[0]=='T1':rows.append({'r':int(fields[1]),'id':int(fields[2]),'kind':int(fields[4]),'outcome':int(fields[5]),'error':int(fields[6]),'reason':fields[7]})
  elif len(fields)==11 and fields[0]=='T1X'and rows:rows[-1]['fuel']=int(fields[-1])
 triples=[];missing=[];resets=[]
 for i,row in enumerate(rows):
  if row['reason']!='farm-certified-solo-live-reset':continue
  resets.append(row);prior=[r for r in rows[:i]if r['r']==row['r']and r['id']==row['id']];after=[r for r in rows[i+1:]if r['r']==row['r']and r['id']==row['id']]
  if prior and prior[-1]['kind']==3 and after and after[0]['kind']==3 and after[0]['reason']=='farm-certified-reset-receipt-basic':triples.append([prior[-1],row,after[0]])
  else:missing.append(row)
 fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted');errors=[r for r in rows if r['error']or r['outcome']not in[2,3,5,7]]
 if not resets or missing or errors or fuel or any(data['diagnostics']['botFaults'].values()):raise ValueError(json.dumps({'resets':len(resets),'missing':missing,'errors':errors,'fuel':fuel,'faults':data['diagnostics']['botFaults']}))
 trace=output/'native-trace';trace.mkdir(exist_ok=True);rawfile=trace/'full-main-reset.repl26a';rawfile.write_bytes(raw)
 req={'id':'full-main-reset','raw':str(rawfile),'raw_sha256':sha(rawfile),'map':'lanes','kind':'native-full-main-regression','created_at':None,'teams':{'a':{'teamId':'candidate','name':'candidate'},'b':{'teamId':'quiet','name':'quiet'}},'replay_patch':'0.0.2','game':{'rounds':data['match']['roundsStarted'],'sides':[{'side':'a','teamId':'candidate','score':int(data['teams'][0]['submittedGems']),'draft':[]},{'side':'b','teamId':'quiet','score':int(data['teams'][1]['submittedGems']),'draft':[]}]}}
 (trace/'manifest.json').write_text(json.dumps({'requests':[req]},indent=2)+'\n',encoding='utf8')
 report={'passed':True,'scope':__doc__,'accepted_certified_resets':len(resets),'complete_same_owner_triples':len(triples),'triples':triples,'missing_extra_basics':missing,'fuel_exhausted':fuel,'native_faults':data['diagnostics']['botFaults'],'action_errors':errors,'source_sha256':{h.name:sha(h)for h in(bot/'src').iterdir()if h.is_file()},'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'sdk_sha256':SDK_SHA,'cli_sha256':sha(cli),'map_sha256':sha(mapfile),'replay_sha256':sha(replay),'statistics_sha256':sha(statistics),'actual_engine':data['match'],'commands':commands,'retained_reanalysis':a.existing}
 (output/'runner-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':True,'accepted_resets':len(resets),'same_owner_triples':len(triples),'fuel':fuel,'faults':data['diagnostics']['botFaults']},indent=2))
if __name__=='__main__':main()

"""Real production-main paid continuation at a measured native fuel boundary.

The copy changes no World, stats, wallet, camp, mission or selected proposal.
It waits for an actual paid Damage continuation, burns guest fuel immediately
before its admission, then records a deferred marker after the owner finishes.
Positive proves Basic -> actual restricted snapshot -> required damage through
the real main loop. Negative proves that an unfunded required first hit declines.
Both sides use official Lanes and a drafting/yielding opponent; this is scoped
correctness activation, not a strength benchmark or a projected-world fixture.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent
SDK_SHA='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4'
CLI_SHA='a4262675695e4716ec5355712d21d2ec71e78cc8371dca28990bf1de84480da3'
MAP_SHA='bf50fd858a0f4d89a86b90228e77df6ee16bcaf05c627ba4d79460eab904f184'
ENGINE_BUILD='02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sources(p):return {x.name:sha(x)for x in sorted(Path(p).iterdir())if x.suffix=='.h'or x.name=='main.cpp'}
HEADER=r'''#pragma once
#include <cambc.h>
#include <charconv>
#include <cstdio>
namespace Boundary27 {
inline bool used=false,pending=false;inline int values[16]{};
inline void burn(unsigned target){volatile unsigned value=1;while(cambc::fuel_remaining()>target+350){value=value*1664525u+1013904223u;} }
inline void emit(){if(!pending)return;pending=false;char b[1024];char*p=b;for(const char*s="SEQB";*s;)*p++=*s++;for(int v:values){*p++=' ';p=std::to_chars(p,b+sizeof(b)-1,v).ptr;}*p++='\n';std::fwrite(b,1,p-b,stdout);}
}
'''
def instrument(source,dest,target,positive):
 before=sources(source);dest.mkdir(parents=True)
 for name in before:shutil.copy2(source/name,dest/name)
 if before!=sources(source):raise ValueError('Source changed during read; freeze first')
 (dest/'boundary27.h').write_text(HEADER)
 p=dest/'economy.h';s=p.read_text();start=s.index('inline SoloBasicReceipt make_solo_basic_receipt(');end=s.index('solo_basic_reset_followup(',start)
 prefix=s[:start];body=s[start:end];suffix=s[end:]
 pattern=r'(?m)^\s*const\s+unsigned\s+admission\s*=\s*out\.continuation'
 matches=list(re.finditer(pattern,body))
 if len(matches)!=1:raise ValueError('Required typed receipt admission anchor changed; review runner')
 at=matches[0].start();code='''
    if(!Boundary27::used && actor.type==11 && out.continuation==SoloBasicContinuation::Damage && bc::fuel_remaining()>50000){
        Boundary27::used=Boundary27::pending=true;
        auto &v=Boundary27::values;v[0]=w.round;v[1]=actor.id;v[2]=int(bc::fuel_remaining());
        Boundary27::burn(TARGET);
        v[3]=int(bc::fuel_remaining());v[4]=int(selected.solo_current_followup);v[5]=selected.solo_current_slot;
        v[6]=actor.pos.x;v[7]=actor.pos.y;v[8]=int(actor.hp);v[9]=camp.id;v[10]=int(camp.hp);v[11]=MODE;
    }
'''.replace('TARGET',str(target)).replace('MODE','1'if positive else'0')
 p.write_text('#include "boundary27.h"\n'+prefix+body[:at]+code+body[at:]+suffix)
 p=dest/'main.cpp';s=p.read_text();s,count=re.subn(r'(?m)^(\s*)cambc::end_turn\(\);',r'\1Boundary27::emit();\n\1cambc::end_turn();',s)
 if count!=1:raise ValueError('Production main end_turn anchor changed')
 p.write_text(s)
 return before
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in('cli','project','source','output'):p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--mode',choices=('positive','negative'),required=True)
 a=p.parse_args();cli,project,source,output=[getattr(a,n).resolve()for n in('cli','project','source','output')]
 sdk=project/'sdk/cpp/cambc.h';mapfile=project/'maps/lanes.map26a';quiet_src=HERE.parent/'fixtures/native-quiet.cpp'
 if sha(cli)!=CLI_SHA or sha(sdk)!=SDK_SHA or sha(mapfile)!=MAP_SHA:raise ValueError('Reviewed CLI2.2.2/SDK2.2.2/official Lanes pin differs')
 output.mkdir(parents=True,exist_ok=False);bot=output/'bot';quiet=output/'quiet';(quiet/'src').mkdir(parents=True)
 production=instrument(source,bot/'src',40000 if a.mode=='positive' else 39000,a.mode=='positive')
 shutil.copy2(quiet_src,quiet/'src/main.cpp');commands=[]
 def invoke(command,label):
  cmd=[str(x)for x in command];commands.append(cmd);r=subprocess.run(cmd,cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600);(output/(label+'.log')).write_text(r.stdout+r.stderr)
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 for name,folder in(('candidate',bot),('quiet',quiet)):
  invoke([cli,'build',folder],name+'-normal');invoke([cli,'build',folder,'--release'],name+'-release')
 module=sha(bot/'.cambc/build-release/bot-injected.wasm');games=[]
 for side in(0,1):
  game=output/f'side{side}';game.mkdir();first,second=(bot,quiet)if side==0 else(quiet,bot)
  invoke([cli,'run',first,second,'--map',mapfile,'--release','--json','-o',game,'--statistics',game/'statistics.json'],f'run-side{side}')
  data=json.loads((game/'statistics.json').read_text());match=data['match'];replay,=game.glob('*.repl26a');letter='a'if side==0 else'b';team='teamA'if side==0 else'teamB'
  with zipfile.ZipFile(replay)as z:stdout=z.read(f'team-{letter}.stdout').decode(errors='replace').replace('\0','')
  (game/'candidate.stdout.txt').write_text(stdout);markers=[list(map(int,line.split()[1:]))for line in stdout.splitlines()if line.startswith('SEQB ')]
  rows=[]
  for line in stdout.splitlines():
   fields=line.split()
   if len(fields)==8 and fields[0]=='T1':rows.append({'round':int(fields[1]),'owner':int(fields[2]),'kind':int(fields[4]),'outcome':int(fields[5]),'error':int(fields[6]),'reason':fields[7]})
   elif fields and fields[0]=='T1X'and rows:rows[-1]['fuel_after']=int(fields[-1])
  faults=data['diagnostics']['botFaults'];fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted'and e['owner']['team']==team)
  errors=[r for r in rows if r['error']];caught=re.findall(r'(?:TACTICS_ERROR|bot error:)[^\r\n]*',stdout)
  case={'side':side,'markers':markers,'native_faults':faults,'own_fuel_exhausted':fuel,'action_errors':errors,'caught_errors':caught,'module_sha256':module,'map_sha256':sha(mapfile),'replay_sha256':sha(replay),'statistics_sha256':sha(game/'statistics.json'),'actual_engine':match,'passed':False}
  if len(markers)==1:
   marker=markers[0];actions=[r for r in rows if(r['round'],r['owner'])==(marker[0],marker[1])];case['same_owner_actions']=actions;case['measured_maker_admission_budget']=marker[3]
   low,high=(40000,41000)if a.mode=='positive'else(39000,40000)
   relevant=[r for r in actions if r['kind']in(3,7,8)]
   activation=(len(relevant)==2 and relevant[0]['kind']==3 and relevant[1]['reason']=='farm-certified-solo-basic-damage-receipt'and all(r['outcome']==2 for r in relevant))if a.mode=='positive'else not relevant
   case['passed']=low<=marker[3]<high and marker[2]>50000 and activation
  case['passed']=case['passed']and not fuel and not errors and not caught and not any(faults.values())and match['engineVersion']=='0.0.2'and match['engineBuildHash']==ENGINE_BUILD
  games.append(case)
  (output/'progress.json').write_text(json.dumps({'mode':a.mode,'games':games},indent=2)+'\n')
 if production!=sources(source):raise ValueError('Production source changed during native test')
 report={'passed':all(g['passed']for g in games),'scope':__doc__,'mode':a.mode,'not_independent_strength_games':True,'production_main_exercised':True,'production_main_modified_only_for_deferred_marker':True,'production_main_sha256':production['main.cpp'],'instrumented_copy_main_sha256':sha(bot/'src/main.cpp'),'source_sha256':production,'instrumented_source_sha256':sources(bot/'src'),'source_delta':'economy: real fuel burn only before actual required Damage admission; main: deferred marker only; extra diagnostics header. No projected World or forced actions.','runtime_pins':{'cli_sha256':sha(cli),'sdk_header_sha256':sha(sdk),'project_config_sha256':sha(project/'cambc.toml'),'actual_engine_build':ENGINE_BUILD},'quiet_fixture_sha256':sha(quiet_src),'runner_sha256':sha(__file__),'games':games,'commands':commands}
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'mode':a.mode,'cases':[{'side':g['side'],'passed':g['passed'],'markers':g['markers'],'fuel':g['own_fuel_exhausted']}for g in games]},indent=2))
 if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()

"""Real partial-emblem prelude, then unchanged production cash→shop→Elk→bank caller.

This native activation fixture earns every coin and physically buys its starting
inventory. It never projects a wallet/Actor into production World. The scalar
before/after preview is explicitly hypothetical and installs nothing. Quiet one
pick setup; wrapper module differs from the competitive module; no strength claim.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent
ENGINE='02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('cli','project','source','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reuse-bot',type=Path);p.add_argument('--reuse-game',type=Path)
 a=p.parse_args();cli,project,source,output=[x.resolve()for x in[a.cli,a.project,a.source,a.output]]
 if bool(a.reuse_bot)!=bool(a.reuse_game):raise ValueError('Reuse requires both bot and game')
 output.mkdir(parents=True,exist_ok=False);sdk=project/'sdk/cpp/cambc.h'
 if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('SDK pin differs')
 hashes={x.name:sha(x)for x in source.glob('*.h')};hashes['main.cpp']=sha(source/'main.cpp')
 fixture=HERE/'fixtures/native-cash-partial.cpp';map_path=HERE/'fixtures/native-cash-partial.map26a';metadata=json.loads((HERE/'fixtures/native-cash-partial-map.json').read_text())
 if sha(map_path)!=metadata['map_sha256']or sha(fixture)!=metadata['fixture_sha256']:raise ValueError('Fixture bytes changed')
 commands=[]
 def invoke(command,label):
  c=[str(x)for x in command];commands.append(c);r=subprocess.run(c,cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600);(output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 if a.reuse_bot:
  bot=a.reuse_bot.resolve();game=a.reuse_game.resolve()
  if sha(bot/'src/main.cpp')!=sha(fixture)or sha(bot/'src/retained-main.h')!=hashes['main.cpp']:raise ValueError('Retained fixture/main bytes differ')
  if any(sha(bot/'src'/name)!=value for name,value in hashes.items()if name!='main.cpp'):raise ValueError('Retained source headers differ')
  record=game/'record.json'
  if not record.is_file():raise ValueError('Retained local game record missing')
  retained=json.loads(record.read_text());module=sha(bot/'.cambc/build-release/bot-injected.wasm')
  if retained['identity']['a']!=module or retained['identity']['b']!=module:raise ValueError('Retained record module mismatch')
 else:
  bot=output/'bot';(bot/'src').mkdir(parents=True)
  for name in hashes:
   shutil.copy2(source/name,bot/'src'/('retained-main.h'if name=='main.cpp'else name))
  shutil.copy2(fixture,bot/'src/main.cpp');invoke([cli,'build',bot],'build-normal');invoke([cli,'build',bot,'--release'],'build-release')
  game=output/'game';game.mkdir();invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',game/'statistics.json'],'run')
 d=json.loads((game/'statistics.json').read_text());replay=next(game.glob('*.repl26a'))
 if d['match']['engineVersion']!='0.0.2'or d['match']['engineBuildHash']!=ENGINE or d['match']['mapHash']!=sha(map_path):raise ValueError('Native engine/map identity differs')
 def events(kind,team):return[x for e in d['events']if e['kind']==kind and e.get('owner',{}).get('team')==team for x in e['entries']]
 failures=[];cases={};fuel=sum(len(e['entries'])for e in d['events']if e['kind']=='fuelExhausted')
 with zipfile.ZipFile(replay)as z:
  if z.testzip()is not None:raise ValueError('Replay CRC')
  for side,team in [('a','teamA'),('b','teamB')]:
   text=z.read('team-'+side+'.stdout').decode(errors='replace').replace(chr(0),'');markers=[x for x in text.splitlines()if x.startswith('PC20_')]
   preview=re.search(r'PC20_PREVIEW (\d+) known=1,1 feasible=0,1 ',text);prelude=re.search(r'PC20_PRELUDE (\d+) (\d+) wallet=0 jungleShards=4 powerShards=3 emblem=0 HP=1900 STR=57',text);handover=re.search(r'PC20_HANDOVER (\d+) (\d+) wallet=0 cashAlive=1',text)
   if not(preview and prelude and handover):failures.append(side+':native-starting-precondition');cases[side]={'markers':markers};continue
   start=int(prelude[2]);hand=int(handover[2]);at=lambda x:x['timestamp']['round']
   buys=events('buyItem',team);initial_jungle=[x for x in buys if at(x)==start and x.get('target',{}).get('name')=='Jungle Shard of Health'and x['value']=='4'and x['amount']==120 and x['context']=='210'];initial_power=[x for x in buys if at(x)==start and x.get('target',{}).get('name')=='Power Shard of Health'and x['value']=='3'and x['amount']==90 and x['context']=='90']
   pre_captures=[x for x in events('gemCollection',team)if at(x)<start and x['value']=='0'];cash=[x for x in events('gemCollection',team)if at(x)>hand and x['value']=='0'];bought=[x for x in buys if at(x)>hand and x.get('target',{}).get('name')=='Jungle Shard of Health'and x['value']=='1'and x['amount']==30 and x['context']=='35'];combined=[x for x in events('itemCombination',team)if at(x)>hand and x.get('target',{}).get('name')=='Jungle Emblem of Health'];gems=[x for x in events('gemCollection',team)if at(x)>hand and x['value']=='36'];banks=[x for x in events('gemSubmission',team)if at(x)>hand and x['value']=='36']
   ordered=bool(cash and bought and combined and gems and banks)and hand<at(cash[0])<at(bought[0])==at(combined[0])<at(gems[0])<at(banks[0])
   named=bool(re.search(r'^T1 \d+ \d+ \S+ 14 2 0 install-priced-return-bundle$',text,re.M));errors=bool(re.search(r'TACTICS_ERROR|PC20_ERROR|bot error:|\[err',text))or any(int(x)>0 for x in re.findall(r'^T1 \d+ \d+ \S+ \d+ \d+ (-?\d+) ',text,re.M))
   if len(pre_captures)!=6 or len(initial_jungle)!=1 or len(initial_power)!=1:failures.append(side+':real210gold-prelude-ledger')
   if not ordered or not named or 'PC20_COMPLETE 'not in text:failures.append(side+':actual-named-chain-incomplete')
   if errors or events('death',team)or events('gemLoss',team):failures.append(side+':caller-error-death-or-gemloss')
   cases[side]={'markers':markers,'prelude_round':start,'handover_round':hand,'actual_pre_cash_receipts':len(pre_captures),'prelude_native_purchases':initial_jungle+initial_power,'actual_cash_receipt':cash[:1],'actual_named_purchase':bought[:1],'actual_emblem_combination':combined[:1],'actual_gem_receipt':gems[:1],'actual_bank':banks[:1],'named_production_action_verified':named,'ordered':ordered}
 if fuel or any(d['diagnostics']['botFaults'].values()):failures.append('native-fault-or-fuel')
 if hashes!={**{x.name:sha(x)for x in source.glob('*.h')},'main.cpp':sha(source/'main.cpp')}:failures.append('source-changed')
 report=dict(passed=not failures,scope=__doc__,created_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashes,sdk_header_sha256=sha(sdk),module_sha256=sha(bot/'.cambc/build-release/bot-injected.wasm'),fixture_sha256=sha(fixture),map_sha256=sha(map_path),statistics_sha256=sha(game/'statistics.json'),replay_sha256=sha(replay),actual_engine=d['match'],native_faults=d['diagnostics']['botFaults'],fuel_exhausted=fuel,failures=failures,cases=cases,commands=commands,reused_existing_local_native_game=bool(a.reuse_bot),existing_game=str(game)if a.reuse_bot else None)
 (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':not failures,'failures':failures,'fuel':fuel,'cases':{s:{k:v for k,v in c.items()if k in['prelude_round','handover_round','actual_pre_cash_receipts','named_production_action_verified','ordered']}for s,c in cases.items()}},indent=2))
 if failures:raise SystemExit(1)
if __name__=='__main__':main()

"""Native finite zero-wallet investment: real producer budget and complete main caller.

The producer checks actual observed cash35 -> one exact30gold Health shard ->
Wolf22gem receipt at65k, with no projected wallet/inventory installed. The main
fixture calls unchanged production Bot::turn for Cassi; allied Issac idles to
isolate the required solo payout. It must physically clear/capture cash, recall,
buy the named shard, clear/capture a Wolf and actually bank22. No sandbox income
or actor-stat injection. Scripted one-pick map is scoped native evidence, not a
competitive opponent or tournament draft/map sample.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cli',required=True,type=Path);p.add_argument('--project',required=True,type=Path)
    p.add_argument('--source',type=Path,default=HERE.parents[1]/'bots/tactics-v1/src')
    p.add_argument('--output',required=True,type=Path);p.add_argument('--mode',choices=['all','producer','main'],default='all')
    args=p.parse_args();cli,project,source,output=[x.resolve()for x in [args.cli,args.project,args.source,args.output]]
    output.mkdir(parents=True,exist_ok=False);sdk=project/'sdk/cpp/cambc.h'
    if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('SDK pin mismatch')
    captured={x.name:sha(x)for x in source.glob('*.h')};captured['main.cpp']=sha(source/'main.cpp')
    maps={'producer':HERE/'fixtures/native-cash.map26a','main':HERE/'fixtures/native-cash-main.map26a'}
    metadata={'producer':HERE/'fixtures/native-cash-map.json','main':HERE/'fixtures/native-cash-main-map.json'}
    reports=[]
    for mode in (['producer','main']if args.mode=='all'else[args.mode]):
        map_path=maps[mode];meta=json.loads(metadata[mode].read_text())
        if sha(map_path)!=meta['map_sha256']:raise ValueError('Fixture map changed')
        case=output/mode;case.mkdir();bot=case/'bot';(bot/'src').mkdir(parents=True)
        for f in source.glob('*.h'):shutil.copy2(f,bot/'src'/f.name)
        fixture=HERE/f'fixtures/native-cash-{mode}.cpp';shutil.copy2(fixture,bot/'src/main.cpp')
        if mode=='main':shutil.copy2(source/'main.cpp',bot/'src/retained-main.h')
        commands=[]
        def invoke(command,label):
            r=subprocess.run([str(x)for x in command],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
            (case/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8');commands.append([str(x)for x in command])
            if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        invoke([cli,'build',bot],'build-normal');invoke([cli,'build',bot,'--release'],'build-release')
        game=case/'game';game.mkdir();stats=game/'statistics.json'
        invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',stats],'run')
        data=json.loads(stats.read_text());replays=list(game.glob('*.repl26a'))
        if data['match']['engineVersion']!='0.0.2'or len(replays)!=1:raise ValueError('Native engine/replay mismatch')
        if data['match']['engineBuildHash']!='02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede':raise ValueError('Engine build differs')
        markers={};budgets={};timeline={}
        with zipfile.ZipFile(replays[0])as archive:
            if archive.testzip()is not None:raise ValueError('Replay CRC failure')
            for side,team,body,cash_group,gem_group in [('a','teamA',0,0,2),('b','teamB',2,1,3)]:
                text=archive.read(f'team-{side}.stdout').decode('utf8',errors='replace').replace('\0','')
                (case/f'team-{side}.stdout.txt').write_text(text,encoding='utf8')
                if re.search(r'TACTICS_ERROR|bot error:|\[err|CASH_\w*(?:ERROR|FAIL)',text):raise ValueError('Caught/assertion error')
                markers[side]=[line for line in text.splitlines()if 'CASH_'in line or'install-priced-return-bundle'in line or'recovery-priced-private-upgrade-return'in line]
                if mode=='producer':
                    quotes=[tuple(map(int,row))for row in re.findall(r'CASH_PRODUCER_QUOTE (\d+) (\d+) (\d+) (\d+) (-?\d+)',text)]
                    success=[tuple(map(int,row))for row in re.findall(r'CASH_PRODUCER_PASS (\d+) (\d+) (\d+) (\d+) (\d+)',text)]
                    if len(success)!=1 or success[0][0]!=body or success[0][-1]!=gem_group:raise ValueError('Actual empty-wallet producer did not activate')
                    for owner,round,start,end,group in quotes:
                        if owner!=body or not 64000<=start<=65000 or end<40000 or start-end>18000:raise ValueError('65k producer did not retain bounded core budget')
                    budgets[side]=dict(quote_count=len(quotes),funded_cost=success[0][2]-success[0][3],funded_remaining=success[0][3])
                else:
                    if f'CASH_MAIN_ACTUAL_CALLER {body}'not in text or'install-priced-return-bundle'not in text:raise ValueError('Actual main or named purchase path missing')
                    def entries(kind):return [v for e in data['events']if e['kind']==kind and e['owner'].get('id')==body and e['owner'].get('team')==team for v in e['entries']]
                    buys=entries('buyItem');collect=entries('gemCollection');submits=entries('gemSubmission');clears=entries('campClear')
                    if not buys or buys[0]['target']['name']!='Jungle Shard of Health'or int(buys[0]['value'])!=1 or int(buys[0]['amount'])!=30 or int(buys[0]['context'])!=35:raise ValueError('Actual exact cash35 wallet/shard receipt differs')
                    cash=[e for e in collect if e['target'].get('id')==cash_group and int(e['value'])==0]
                    gems=[e for e in collect if e['target'].get('id')==gem_group and int(e['value'])==22]
                    bank=[e for e in submits if int(e['value'])==22]
                    if not cash or not gems or not bank:raise ValueError('Real cash capture/gem capture/bank missing')
                    times=[cash[0]['timestamp']['round'],buys[0]['timestamp']['round'],gems[0]['timestamp']['round'],bank[0]['timestamp']['round']]
                    if times!=sorted(times)or len(set(times))!=4:raise ValueError('Finite cash ->actual item ->gem ->bank chronology broken')
                    timeline[side]=dict(cash_capture=times[0],actual_bundle_purchase=times[1],gem_capture=times[2],actual_bank=times[3],first_buy=buys[0],first_bank=bank[0])
        faults=data['diagnostics']['botFaults'];fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
        if any(faults.values())or fuel:raise ValueError('Native fault/fuel exhaust')
        reports.append(dict(mode=mode,map_sha256=sha(map_path),fixture_sha256=sha(fixture),module_sha256=sha(bot/'.cambc/build-release/bot-injected.wasm'),
            replay_sha256=sha(replays[0]),statistics_sha256=sha(stats),actual_engine=data['match'],native_faults=faults,fuel_exhausted=fuel,
            markers=markers,producer_budget=budgets,completed_chronology=timeline,commands=commands))
    current={x.name:sha(x)for x in source.glob('*.h')};current['main.cpp']=sha(source/'main.cpp')
    if current!=captured:raise ValueError("Production source changed during validation")
    result=dict(passed=True,created_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__.strip(),source_sha256=captured,
        current_source_matches=current==captured,cli_sha256=sha(cli),sdk_header_sha256=sha(sdk),maps_sha256={name:sha(path)for name,path in maps.items()},reports=reports,
        limitations=['Other Issac bodies idle to isolate solo payout; not opponent strength.','One official cash singleton and one Wolf, not broad multi-camp investment.','Future quiet target availability is a policy assumption; arrival revalidates actual native state.'])
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(passed=True,reports=[{k:r[k]for k in ['mode','native_faults','fuel_exhausted','producer_budget','completed_chronology']}for r in reports]),indent=2))
if __name__=='__main__':main()

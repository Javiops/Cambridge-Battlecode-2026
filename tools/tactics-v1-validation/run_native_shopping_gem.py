"""Actual native private-wallet investment followed by one completed gem cycle.

Scripted tactical main with unchanged production shopping, solo model, SDKWorld
and mutation gateway. Gold is physically earned, both item bundles are actually
bought, and the final resource is physically cleared, captured and banked. This
is not full production arbiter activation or evidence of competitive strength.
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
    p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    cli,project,source,output=[x.resolve()for x in [args.cli,args.project,args.source,args.output]]
    output.mkdir(parents=True,exist_ok=False)
    sdk=project/'sdk/cpp/cambc.h'
    if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('SDK pin mismatch')
    captured={x.name:sha(x)for x in source.glob('*.h')}
    bot=output/'native-shopping-gem';(bot/'src').mkdir(parents=True)
    for name in captured:shutil.copy2(source/name,bot/'src'/name)
    fixture=HERE/'fixtures/native-shopping-gem.cpp';shutil.copy2(fixture,bot/'src/main.cpp')
    map_path=HERE/'fixtures/native-shopping-gem.map26a';meta=json.loads((HERE/'fixtures/native-shopping-gem-map.json').read_text())
    if sha(map_path)!=meta['map_sha256']:raise ValueError('Fixture map changed')
    commands=[]
    def invoke(command,label):
        r=subprocess.run([str(x)for x in command],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
        (output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8');commands.append([str(x)for x in command])
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    invoke([cli,'build',bot],'build-normal');invoke([cli,'build',bot,'--release'],'build-release')
    game=output/'game';game.mkdir();stats=game/'statistics.json'
    invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',stats],'run')
    data=json.loads(stats.read_text())
    if data['match']['engineVersion']!='0.0.2':raise ValueError('Actual engine version differs')
    replay=list(game.glob('*.repl26a'))
    if len(replay)!=1:raise ValueError('Expected one complete native replay')
    markers={};budgets={}
    with zipfile.ZipFile(replay[0])as archive:
        if archive.testzip()is not None:raise ValueError('Replay CRC failed')
        for letter,body in [('a',0),('b',1)]:
            text=archive.read('team-'+letter+'.stdout').decode('utf8',errors='replace').replace('\0','')
            (output/('team-'+letter+'.stdout.txt')).write_text(text,encoding='utf8')
            markers[letter]=re.findall(r'SHOP_GEM_[^\r\n]+',text)
            if re.search(r'TACTICS_ERROR|bot error:|\[err|SHOP_GEM_FAIL',text):raise ValueError('Caught/assertion error in native fixture')
            plans=[tuple(map(int,row))for row in re.findall(r'SHOP_GEM_PLAN (\d+) (\d+) (\d+) (-?\d+) (-?\d+) (-?\d+) ([01])',text)]
            installs=re.findall(r'SHOP_GEM_INSTALL (\d+) (\d+) (\d+) (\d+) (\d+)',text)
            completed=re.findall(r'SHOP_GEM_PASS (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)',text)
            if not plans or len(installs)!=1 or len(completed)!=1:raise ValueError('Missing actual plan/install/full-cycle markers')
            for owner,start,end,item,group,origin,unlock in plans:
                if owner!=body or not 64000<=start<=65000 or end<40000 or start-end>18000:raise ValueError('Realistic-entry bounded planner budget failed')
            if plans[-1][3]<0 or plans[-1][4]==plans[-1][5]or plans[-1][6]!=1:raise ValueError('Named actual gem unlock was not retained separately')
            if int(installs[0][0])!=body or int(installs[0][2])!=15:raise ValueError('Exact actual bundle wallet receipt failed')
            if int(completed[0][0])!=body or int(completed[0][3])!=36 or int(completed[0][4])!=2300:raise ValueError('Actual bank+recovery endpoint failed')
            budgets[letter]={'owner_plans':len(plans),'maximum_spent':max(start-end for _,start,end,*_ in plans),'funded_plan_spent':plans[-1][1]-plans[-1][2],'funded_plan_remaining':plans[-1][2]}
    if any(data['diagnostics']['botFaults'].values()):raise ValueError('Native bot fault')
    fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
    if fuel:raise ValueError('Native fixture exhausted fuel')
    economic={}
    for team in ['teamA','teamB']:
        economic[team]={kind:[entry for e in data['events']if e['kind']==kind and e['owner']['team']==team for entry in e['entries']]for kind in ['gemCollection','gemSubmission']}
        submits=economic[team]['gemSubmission']
        if len(submits)!=1 or int(submits[0]['value'])!=36:raise ValueError('Expected one real36gem bank event for '+team)
    current={x.name:sha(x)for x in source.glob('*.h')}
    result={'passed':True,'created_utc':datetime.now(timezone.utc).isoformat(),'source_headers_sha256':captured,
        'current_source_headers_match':captured==current,'cli_sha256':sha(cli),'sdk_header_sha256':sha(sdk),
        'fixture_sha256':sha(fixture),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),
        'map_sha256':sha(map_path),'replay_sha256':sha(replay[0]),'statistics_sha256':sha(stats),'actual_engine':data['match'],
        'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel,'markers':markers,'economic_events':economic,
        'production_helpers':['plan_upgrade_return','plan_gold_gem_return','completed_gem_return','certify_solo_clear','project_bundle_actor','shopping_proposal','shopping_after_action','execute','World.refresh'],
        'planner_budgets':budgets,'scope':__doc__.strip(),
        'limitations':['Old same-camp reserve certificate rejects the unupgraded kit; this is not proof all other tactics cannot clear it.','Resource remains available in this scripted quiet scenario; future visibility/ownership in a competitive game is revalidated.','Scripted tactical main; full production arbiter and strength require separate local development and holdout matches.'],
        'commands':commands}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k]for k in ['passed','current_source_headers_match','native_faults','fuel_exhausted','markers']},indent=2))
if __name__=='__main__':main()

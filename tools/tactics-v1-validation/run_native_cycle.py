"""Actual native single-holder capture/normal-recall/tribute regression.

Uses a scripted fixture main plus unchanged copied production policy headers.
This validates timing/observation helpers and actual SDK outcomes, not the full
production arbiter, all Home/contest cases or competitive strategy strength.
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
    bot=output/'native-cycle';(bot/'src').mkdir(parents=True)
    for name in captured:shutil.copy2(source/name,bot/'src'/name)
    fixture=HERE/'fixtures/native-cycle.cpp';shutil.copy2(fixture,bot/'src/main.cpp')
    map_path=HERE/'fixtures/native-cycle.map26a';meta=json.loads((HERE/'fixtures/native-cycle-map.json').read_text())
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
    markers={};prefixes=['NATIVE_IMMEDIATE_RECALL_STARTED','NATIVE_EARLY_DEPARTURE_NO_PAYOUT','NATIVE_GUARDED_OVERLAP_STARTED','NATIVE_CAPTURE_BEFORE_RECALL_DEPARTURE','NATIVE_TRIBUTE_STARTED_NOT_BANKED','NATIVE_ACTUAL_BANK_COMPLETED']
    with zipfile.ZipFile(replay[0])as archive:
        if archive.testzip()is not None:raise ValueError('Replay CRC failed')
        for letter,body in [('a',0),('b',1)]:
            text=archive.read('team-'+letter+'.stdout').decode('utf8',errors='replace').replace('\0','')
            (output/('team-'+letter+'.stdout.txt')).write_text(text,encoding='utf8')
            markers[letter]=re.findall(r'NATIVE_[^\r\n]+',text)
            if len(markers[letter])!=len(prefixes)or any(not line.startswith(prefix+' '+str(body)+' ')for line,prefix in zip(markers[letter],prefixes)):
                raise ValueError('Missing actual native phase markers: '+repr(markers[letter]))
            if re.search(r'TACTICS_ERROR|bot error:|\[err',text):raise ValueError('Caught error in native fixture')
            if len(re.findall(r'T1C \d+ '+str(body)+r' completed 1\b',text))!=2:raise ValueError('Production observer did not recognize two actual recall completions')
            if len(re.findall(r'T1C \d+ '+str(body)+r' completed 2\b',text))!=1:raise ValueError('Production observer did not recognize actual tribute completion')
    if any(data['diagnostics']['botFaults'].values()):raise ValueError('Native bot fault')
    fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
    if fuel:raise ValueError('Native fixture exhausted fuel')
    economic={}
    for team in ['teamA','teamB']:
        economic[team]={kind:[entry for e in data['events']if e['kind']==kind and e['owner']['team']==team for entry in e['entries']]for kind in ['gemCollection','gemSubmission']}
        for kind,entries in economic[team].items():
            # These integer resource events expose the actual count in value;
            # amount is the separate floating metric and is zero here.
            if len(entries)!=1 or int(entries[0]['value'])!=22:raise ValueError('Expected exactly one real 22-gem '+kind+' for '+team+': '+repr(entries))
    current={x.name:sha(x)for x in source.glob('*.h')}
    result={'passed':True,'created_utc':datetime.now(timezone.utc).isoformat(),'source_headers_sha256':captured,
        'current_source_headers_match':captured==current,'cli_sha256':sha(cli),'sdk_header_sha256':sha(sdk),
        'fixture_sha256':sha(fixture),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),
        'map_sha256':sha(map_path),'replay_sha256':sha(replay[0]),'statistics_sha256':sha(stats),'actual_engine':data['match'],
        'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel,'markers':markers,'economic_events':economic,
        'production_helpers':['overlap_hold','current_recall_ticks','current_tribute_ticks','observe_progress','observe_hold','remember','execute','World.refresh'],
        'scope':__doc__.strip(),'limitations':['Normal recall only; Home timing remains covered by separate mechanics/unit evidence, not this native fixture.','Single occupied spawn tile, no enemy contest or damage interruption in this scenario.','Fixture main uses actual production helpers/observer/gateway; it is not full production arbiter activation or a final competitive bot module.'],
        'commands':commands}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k]for k in ['passed','current_source_headers_match','native_faults','fuel_exhausted','markers']},indent=2))
if __name__=='__main__':main()

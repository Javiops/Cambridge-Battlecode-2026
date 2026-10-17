"""Actual SDK solo-farm quote and projected local-assembly budget fixture."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['cli','project','source','output']:p.add_argument('--'+n,required=True,type=Path)
    p.add_argument('--existing',action='store_true',help='Re-analyze the retained completed native run without another match.')
    a=p.parse_args();cli,project,source,output=[getattr(a,n).resolve()for n in ['cli','project','source','output']]
    bot=output/'bot';commands=[]
    if not a.existing:
        output.mkdir(parents=True,exist_ok=False);(bot/'src').mkdir(parents=True)
        for h in source.glob('*.h'):shutil.copy2(h,bot/'src'/h.name)
        shutil.copy2(HERE/'fixtures/native-solo-consumer.cpp',bot/'src/main.cpp')
    def invoke(command,label):
        commands.append([str(v)for v in command]);r=subprocess.run(commands[-1],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
        (output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    game=output/'game';stats=game/'statistics.json'
    if not a.existing:
        invoke([cli,'build',bot],'normal');invoke([cli,'build',bot,'--release'],'release')
        game.mkdir()
        invoke([cli,'run',bot,bot,'--map',project/'maps/lanes.map26a','--release','--json','-o',game,'--statistics',stats],'run')
    data=json.loads(stats.read_text());replay,=game.glob('*.repl26a');markers={}
    with zipfile.ZipFile(replay)as archive:
        for team in ['a','b']:
            text=archive.read('team-'+team+'.stdout').decode(errors='replace').replace('\0','')
            (game/('team-'+team+'.stdout.txt')).write_text(text,encoding='utf8')
            assert 'NATIVE_SOLO_FAIL'not in text,text[:5000]
            markers[team]={'metadata':re.findall(r'NATIVE_SOLO_METADATA ([^\r\n]+)',text),'begin':re.findall(r'NATIVE_SOLO_CONSUMER_BEGIN ([^\r\n]+)',text),'complete':re.findall(r'NATIVE_SOLO_CONSUMER_PASS ([^\r\n]+)',text),'hold':re.findall(r'NATIVE_SOLO_CONSUMER_HOLD ([^\r\n]+)',text),'combo':re.findall(r'NATIVE_SOLO_COMBO_PASS ([^\r\n]+)',text),'schedule':re.findall(r'NATIVE_SOLO_SCHEDULE_PASS ([^\r\n]+)',text),'actions':re.findall(r'NATIVE_SOLO_ACTION_BUDGET ([^\r\n]+)',text)}
            assert len(markers[team]['begin'])==1,markers[team]
            assert len(markers[team]['complete'])==1,markers[team]
            assert len(markers[team]['combo'])==1 and markers[team]['combo'][0].split()[1:]==['1','1'],markers[team]
            assert len(markers[team]['schedule'])==1,markers[team]
            schedule=list(map(int,markers[team]['schedule'][0].split()))
            assert schedule[1]>0 and schedule[1]==schedule[2] and schedule[4]<=schedule[3] and schedule[6]>=schedule[5],schedule
    fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
    assert fuel==0,fuel
    assert not any(data['diagnostics']['botFaults'].values()),data['diagnostics']['botFaults']
    report={'passed':True,'scope':'Actual SDK Issac travels legally to a singleton wolf with a seeded real-target mission. Production solo certificate/farming and current-clear followups choose real basic/reset actions; native accepted effects refresh through production-admitted local/self paths. At least one actual owner executes basic/reset/basic, below55percentHP choose_mission continues the affordable incumbent, and spent permissions hold. Every accepted reset receives its certified same-owner basic through a consumed-once receipt; rejected and reused receipts grant none. Actual clear owner ends are at most forecast clear ticks, and actual finalHP is at least forecast reserve; exact values are in schedule markers. No projected enemy/helper or gameplay strength claim.','markers':markers,'native_faults':data['diagnostics']['botFaults'],'fuel_exhausted':fuel,'source_sha256':{h.name:sha(h)for h in(bot/'src').glob('*.h')},'fixture_sha256':sha(bot/'src/main.cpp'),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'actual_engine':data['match'],'retained_reanalysis':a.existing,'commands':commands}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps({'passed':True,'markers':markers,'fuel':fuel},indent=2))
if __name__=='__main__':main()

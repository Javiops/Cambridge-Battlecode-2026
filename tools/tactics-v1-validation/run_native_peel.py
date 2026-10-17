"""Actual native lethal-peel section regression and optional old/new cost comparison.

Only the exact production lethal-peel block and its exact take callback are
extracted. World snapshots, incoming forecasts, SDK kit/range and mutation
execution remain the production implementations. This isolates work that later
optional combat movement would otherwise spend. It is not full-arbiter or
competitive-strength evidence. The empty/immune cases are explicit projections;
far-range and positive cases use physical actors and real native HP/cooldowns.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract(source):
    text=(source/'combat.h').read_text(encoding='utf8')
    start=text.index('    auto take = ',text.index('combat_proposal(World &w'))
    brace=text.index('{',start);depth=0
    for i in range(brace,len(text)):
        depth+=int(text[i]=='{')-int(text[i]=='}')
        if depth==0:
            take=text[start:i+2];break
    start=text.index('    if (w.self.can_cast && incoming < w.self.hp && optional_work())',i)
    end=text.index('    if (best && best->priority >= Priority::Survival)',start)
    peel=text[start:end]
    if 'protect-lethal-peel' not in peel:raise ValueError('Production peel extraction missing')
    wrapper='''// Exact production peel block + take callback; actual SDKWorld and forecasts.
inline std::optional<Proposal> exact_peel(World&w,Memory&memory,double incoming,int floor){
using namespace combat_detail;
auto optional_work=[&](){return int(bc::fuel_remaining())>floor&&w.round==int(bc::round_number());};
std::optional<Proposal>best;int best_target=std::numeric_limits<int>::max();
'''+take+'\n'+peel+'\nreturn best;\n}\n'
    return wrapper,{'combat_sha256':sha(source/'combat.h'),'take_sha256':hashlib.sha256(take.encode()).hexdigest(),'peel_sha256':hashlib.sha256(peel.encode()).hexdigest()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cli',required=True,type=Path);p.add_argument('--project',required=True,type=Path)
    p.add_argument('--source',type=Path,default=HERE.parents[1]/'bots/tactics-v1/src')
    p.add_argument('--baseline-source',type=Path,help='Optional frozen earlier source tree for cost comparison')
    p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    cli,project,source,output=[x.resolve()for x in [args.cli,args.project,args.source,args.output]]
    output.mkdir(parents=True,exist_ok=False);sdk=project/'sdk/cpp/cambc.h'
    if sha(sdk)!='76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4':raise ValueError('SDK pin mismatch')
    map_path=HERE/'fixtures/native-peel.map26a';meta=json.loads((HERE/'fixtures/native-peel-map.json').read_text())
    if sha(map_path)!=meta['map_sha256']:raise ValueError('Fixture map changed')
    fixture=HERE/'fixtures/native-peel.cpp';results=[]
    variants=([('baseline',args.baseline_source.resolve())]if args.baseline_source else[])+[('candidate',source)]
    for label,src in variants:
        case=output/label;case.mkdir();bot=case/'bot';(bot/'src').mkdir(parents=True)
        captured={x.name:sha(x)for x in src.glob('*.h')}
        for name in captured:shutil.copy2(src/name,bot/'src'/name)
        shutil.copy2(fixture,bot/'src/main.cpp');wrapper,extraction=extract(src)
        (bot/'src/peel-extracted.h').write_text(wrapper,encoding='utf8');commands=[]
        def invoke(command,name):
            r=subprocess.run([str(x)for x in command],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
            (case/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf8');commands.append([str(x)for x in command])
            if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        invoke([cli,'build',bot],'build-normal');invoke([cli,'build',bot,'--release'],'build-release')
        game=case/'game';game.mkdir();stats=game/'statistics.json'
        invoke([cli,'run',bot,bot,'--map',map_path,'--release','--json','-o',game,'--statistics',stats],'run')
        data=json.loads(stats.read_text());replays=list(game.glob('*.repl26a'))
        if len(replays)!=1 or data['match']['engineVersion']!='0.0.2':raise ValueError('Actual native engine/replay mismatch')
        streams={}
        with zipfile.ZipFile(replays[0])as archive:
            if archive.testzip()is not None:raise ValueError('Replay CRC failure')
            for s in ('a','b'):
                text=archive.read(f'team-{s}.stdout').decode('utf8',errors='replace').replace('\0','');streams[s]=text
                (case/f'team-{s}.stdout.txt').write_text(text,encoding='utf8')
                if re.search(r'TACTICS_ERROR|bot error:|\[err|NATIVE_PEEL_FAIL',text):raise ValueError('Native assertion/caught error')
        text=streams['a'];rows=re.findall(r'NATIVE_PEEL_CASE (\w+) (\d+) (\d+) (\d+) (-?\d+) (\d+)',text)
        if len(rows)!=4 or 'NATIVE_PEEL_PASS 4'not in text or 'NATIVE_PEEL_RANGE_REJECTED'not in text:raise ValueError('Missing native scenario activation')
        cases=[]
        for name,start,end,kind,target,priority in rows:
            start,end,kind,target,priority=map(int,(start,end,kind,target,priority))
            if not 64000<=start<=65000:raise ValueError('Not realistic65k entry')
            expected=(6,5,2)if name=='positive'else(0,-1,0)
            if (kind,target,priority)!=expected:raise ValueError('Legal proposal changed')
            cases.append(dict(name=name,start=start,end=end,cost=start-end,kind=kind,target=target,priority=priority))
        faults=data['diagnostics']['botFaults'];fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
        if any(faults.values())or fuel:raise ValueError('Native fault/fuel exhaust')
        current={x.name:sha(x)for x in src.glob('*.h')}
        results.append(dict(label=label,cases=cases,source_headers_sha256=captured,current_source_headers_match=captured==current,
            extraction=extraction,module_sha256=sha(bot/'.cambc/build-release/bot-injected.wasm'),replay_sha256=sha(replays[0]),
            statistics_sha256=sha(stats),native_faults=faults,fuel_exhausted=fuel,actual_engine=data['match'],commands=commands))
    comparison=[]
    if len(results)==2:
        for old,new in zip(results[0]['cases'],results[1]['cases']):
            if (old['name'],old['kind'],old['target'],old['priority'])!=(new['name'],new['kind'],new['target'],new['priority']):raise ValueError('Native legal proposal differs')
            comparison.append(dict(name=old['name'],old_cost=old['cost'],new_cost=new['cost'],saved=old['cost']-new['cost']))
    report=dict(passed=True,created_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__.strip(),variants=results,
        cli_sha256=sha(cli),sdk_header_sha256=sha(sdk),fixture_sha256=sha(fixture),map_sha256=sha(map_path),comparison=comparison,
        limitations=['Only exact peel section, not full combat arbiter activation.','Empty/immune cases are projections; far and positive actor positions/HP are physical.','Pure randomized checks are predicate equivalence, not independent matches.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(passed=True,comparison=comparison,variants=[dict(label=r['label'],cases=r['cases'],native_faults=r['native_faults'],fuel_exhausted=r['fuel_exhausted'])for r in results]),indent=2))
if __name__=='__main__':main()

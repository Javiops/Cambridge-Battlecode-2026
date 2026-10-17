"""Actual earned-bag -> production one-extra -> completed bank, plus shorter-bank control."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, zipfile
HERE=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('cli','project','source','output'):
        p.add_argument('--'+key,required=True,type=Path)
    a=p.parse_args();cli,project,source,output=[getattr(a,key).resolve()for key in ('cli','project','source','output')]
    output.mkdir(parents=True,exist_ok=False)
    fixture=HERE/'fixtures/native-chain';bot=output/'bot';quiet=output/'quiet'
    (bot/'src').mkdir(parents=True);(quiet/'src').mkdir(parents=True)
    for h in source.glob('*.h'):shutil.copy2(h,bot/'src'/h.name)
    shutil.copy2(source/'main.cpp',bot/'src/production_main.inc')
    shutil.copy2(fixture/'native-chain.cpp',bot/'src/main.cpp')
    shutil.copy2(fixture/'quiet.cpp',quiet/'src/main.cpp')
    commands=[]
    def run(args,label):
        commands.append(list(map(str,args)))
        r=subprocess.run(commands[-1],cwd=project,env={**os.environ,'CAMBC_NO_UPDATE_CHECK':'1'},capture_output=True,text=True,errors='replace',timeout=600)
        (output/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    for name,who in [('bot',bot),('quiet',quiet)]:
        run([cli,'build',who],name+'-normal');run([cli,'build',who,'--release'],name+'-release')
    results=[]
    for name,expected in [('visible-hole-chain',48),('open-bank-control',24)]:
        game=output/name;game.mkdir();stats=game/'statistics.json'
        run([cli,'run',bot,quiet,'--map',fixture/(name+'.map26a'),'--release','--json','-o',game,'--statistics',stats],name)
        data=json.loads(stats.read_text());replay,=game.glob('*.repl26a')
        with zipfile.ZipFile(replay)as z:
            text=z.read('team-a.stdout').decode(errors='replace').replace(chr(0),'')
            other=z.read('team-b.stdout').decode(errors='replace').replace(chr(0),'')
        (game/'team-a.stdout.txt').write_text(text,encoding='utf8')
        events={e['kind']:e['entries']for e in data['events']if e['owner'].get('team')=='teamA'}
        counts={k:len(v)for k,v in events.items()}
        fuel=sum(len(e['entries'])for e in data['events']if e['kind']=='fuelExhausted')
        score=int(next(t['submittedGems']for t in data['teams']if t['team']=='teamA'))
        early=re.findall(r'T1J (\d+) 0 one-reward-funded-early (\d+)',text)
        handoff=re.findall(r'CHAIN_LAWFUL_HANDOFF (\d+) 0 5 12 800\.00 24',text)
        aborts=re.findall(r'T1J [^\r\n]*chain-abort-to-bank[^\r\n]*',text)
        errors=bool(re.search(r'TACTICS_ERROR|CHAIN_FIXTURE_ERROR|bot error:|\[err',text+other))
        accepted_stage=bool(re.search(r'T1 [^\r\n]*chain-early-funded-stage-move\r?\nT1X [^\r\n]* \d+ 0 \d+',text))
        # Actual complete event counters supplement, rather than replace, the distinct new producer marker.
        positive=(name=='visible-hole-chain')
        checks={'completed_game':data['match']['roundsCompleted']==2000,
                'no_faults':not any(data['diagnostics']['botFaults'].values()),
                'no_fuel':fuel==0,'no_caught_errors':not errors,
                'actual_earned_handoff':bool(handoff),'no_loss':counts.get('gemLoss',0)==0}
        if positive:
            counts_ok=counts.get('campClear')==2 and counts.get('gemCollection')==2 and counts.get('gemSubmission')==1
            ordered=counts_ok and len(early)==1 and bool(handoff)
            if ordered:
                ordered=int(handoff[0])<int(early[0][0])<=events['campClear'][1]['timestamp']['round']<events['gemCollection'][1]['timestamp']['round']<events['gemSubmission'][0]['timestamp']['round']
            checks.update({'new_early_marker':len(early)==1,'accepted_early_stage':accepted_stage,
                           'single_extra':counts.get('campClear')==counts.get('gemCollection')==2,
                           'single_combined_bank':counts.get('gemSubmission')==1 and score==expected,
                           'strict_actual_order':ordered,'no_abort':not aborts})
        else:
            checks.update({'new_chain_declined':not early,
                           'no_extra':counts.get('campClear')==counts.get('gemCollection')==1,
                           'ordinary_bank':counts.get('gemSubmission')==1 and score==expected})
        results.append({'map':name,'passed':all(checks.values()),'checks':checks,'assertions':len(checks),
                        'score':score,'counts':counts,'fuel':fuel,'faults':data['diagnostics']['botFaults'],
                        'caught_api_error':errors,'handoff':handoff,'early_marker':early,
                        'accepted_early_stage':accepted_stage,'aborts':aborts,
                        'timeline_events':{k:v for k,v in events.items()if k in ('campClear','gemCollection','gemSubmission')},
                        'map_sha256':sha(fixture/(name+'.map26a')),'replay_sha256':sha(replay),
                        'statistics_sha256':sha(stats),'actual_engine':data['match']})

    report={'passed':all(r['passed']for r in results),'results':results,'source_sha256':{h.name:sha(h)for h in source.glob('*')if h.suffix in ('.h','.cpp')},'fixture_sha256':sha(fixture/'native-chain.cpp'),'module_sha256':sha(bot/'.cambc/build-release/bot-injected.wasm'),'commands':commands,'scope':'Lawful actual Vendetta basic attacks/capture earn first24Gem, then a fresh production Bot controls every subsequent decision. No actor/World/wallet/permission/mission injection. Quiet fixed-map controller integration, not autonomous opening or competitive-strength evidence. Ordinary-walking comparator only.'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()

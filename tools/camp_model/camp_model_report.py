#!/usr/bin/env python3
"""Analyze bounded [camp-model]/[camp-observed] messages from --keep output.

Usage: python3 tools/camp_model_report.py out/ab/exp_camp_model_shadow_vs_exp_mate_no_prism/official
No predictions are credited as true until measured. Handles Windows/Unix paths and sparse logs.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean,median

MODEL = re.compile(r'^\[camp-model\]\s+(.*)')
OBS = re.compile(r'^\[camp-observed\]\s+(.*)')
PAIR = re.compile(r'(\w+)=(-?[\d.]+)')

def parse(s):
    return {k: float(v) if '.' in v else int(v) for k,v in PAIR.findall(s)}

def choose_candidate_log(d):
    # In a paired A/B test the candidate is team A in *_A and team B in *_B.
    suffix=d.name.rsplit('_',1)[-1]
    fn='team-a.stdout' if suffix=='A' else 'team-b.stdout' if suffix=='B' else None
    return d/fn if fn else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('directory',type=Path)
    args=ap.parse_args()
    root=args.directory
    games=0; model=[]; seen=[]; observed=[]; dead=[]; fuel_faults=0
    errors=[]
    for d in sorted(root.rglob('stats.json')):
        folder=d.parent
        logfile=choose_candidate_log(folder)
        if logfile is None or not logfile.exists(): continue
        try: stats=json.loads(d.read_text(encoding='utf-8'))
        except (OSError, ValueError): continue
        games+=1
        side='teamA' if folder.name.endswith('_A') else 'teamB'
        champ_deaths=sum(int(c.get('metrics',{}).get('deaths',0)) for c in stats.get('champions',[]) if c.get('team')==side)
        dmg_taken=sum(float(c.get('metrics',{}).get('monsterDamageTaken',0)) for c in stats.get('champions',[]) if c.get('team')==side)
        dead.append((folder.name,champ_deaths,dmg_taken))
        try: lines=logfile.read_text(encoding='utf-8',errors='replace').splitlines()
        except OSError:continue
        preds={}
        for line in lines:
            match=MODEL.search(line)
            if match:
                vals=parse(match.group(1))
                if {'r','camp','slot','clear','death'}.issubset(vals):
                    model.append((folder.name,vals));preds[(vals['r'],vals['camp'],vals['slot'])]=vals
            match=OBS.search(line)
            if match:
                vals=parse(match.group(1))
                if {'start','camp','slot','hp','rem'}.issubset(vals):
                    observed.append((folder.name,vals))
                    p=preds.get((vals['start'],vals['camp'],vals['slot']))
                    if p and p.get('hp4',-1)>=0:
                        seen.append((folder.name,p,vals))
        try:
            faults=stats.get('diagnostics',{}).get('botFaults',[])
            if isinstance(faults,list):
                fuel_faults+=sum('fuel' in str(e).lower() for e in faults)
        except (TypeError,ValueError):pass
    print('CAMP MODEL — SHADOW VALIDATION (no strategy changes)')
    print(f'Candidate matches with logs: {games}; forecasts: {len(model)}; observed follow-ups: {len(observed)}; paired: {len(seen)}')
    print(f'Engine champion deaths (candidate): {sum(x[1] for x in dead)}; monster damage taken: {sum(x[2] for x in dead):,.0f}')
    if not model:
        print('No forecasts found. Check build, bot directory, fuel threshold, and --keep.');return
    print('Forecasted outcomes:', dict(Counter(('clear' if p['clear'] else 'incomplete', 'death' if p['death']>0 else 'no predicted death') for _,p in model)))
    print('Complete stationary forecast cases:', sum(p.get('confident')==1 for _,p in model))
    print('Forecasts with other allied attackers:', sum(p.get('allies',1)>1 for _,p in model))
    if seen:
        hp_mae=mean(abs(p['hp4']-o['hp']) for _,p,o in seen)
        camp_mae=mean(abs(p['rem4']-o['rem']) for _,p,o in seen)
        print(f'Four-round MAE (only comparable observed episodes): self HP {hp_mae:.1f}, remaining monster HP {camp_mae:.1f}')
        examples=sorted(seen,key=lambda x:abs(x[1]['rem4']-x[2]['rem']),reverse=True)[:7]
        print('Largest prediction errors (inspect replays for spells/walls/enemies):')
        for name,p,o in examples:
            print(f'  {name} r={p["r"]} slot={p["slot"]} group={p["camp"]} '
                  f'pred HP={p["hp4"]:.0f} actual={o["hp"]:.0f}; '
                  f'pred monster={p["rem4"]:.0f} actual={o["rem"]:.0f}; '
                  f'awake={p.get("awake")} confident={p.get("confident")}')
    else:
        print('No four-round matched observations yet. The result does not validate camp damage or clear timing.')
    print('Important: these model-only logs do not attribute deaths to camps; verify suspected cases in replay engine events.')

if __name__=='__main__':main()

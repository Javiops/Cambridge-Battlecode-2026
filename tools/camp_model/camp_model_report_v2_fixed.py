#!/usr/bin/env python3
"""Repair the V2 shadow model log audit WITHOUT rerunning any matches.

Reads the candidate's team stdout on both sides of an A/B test and joins
[camp-model] with [camp-observed] by game, body slot, camp and start round.
Unlike the original script, a join never requires hp4 >= 0: unavailable
four-round predictions are identified separately rather than silently lost.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import re
import statistics

MODEL = re.compile(r'\[camp-model\]\s*(.*)')
OBS = re.compile(r'\[camp-observed\]\s*(.*)')
FIELD = re.compile(r'([a-zA-Z][a-zA-Z0-9_]*)=(-?(?:\d+(?:\.\d+)?|\.\d+))')

def fields(line: str) -> dict[str, float | int]:
    data = {}
    for key, value in FIELD.findall(line):
        data[key] = float(value) if '.' in value else int(value)
    return data

def collect(root: Path):
    dirs = sorted(p for p in root.rglob('stats.json'))
    if not dirs:
        # If stats files are not retained, allow use with logs alone.
        dirs = sorted(p for p in root.rglob('team-a.stdout'))
    records = []
    for sf in dirs:
        folder = sf.parent
        side = folder.name.rsplit('_', 1)[-1]
        if side not in ('A','B'): continue
        log = folder / ('team-a.stdout' if side == 'A' else 'team-b.stdout')
        if not log.exists(): continue
        pred, obs = {}, []
        for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
            m = MODEL.search(line)
            if m:
                d = fields(m.group(1))
                if all(k in d for k in ('r','slot','camp')):
                    pred[(d['r'], d['slot'], d['camp'])] = d
            m = OBS.search(line)
            if m:
                d = fields(m.group(1))
                if all(k in d for k in ('start','slot','camp')): obs.append(d)
        records.append((folder.name, pred, obs))
    return records

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='out/ab/exp_camp_model_shadow_vs_exp_mate_no_prism/official')
    args=parser.parse_args()
    if not args.directory.exists(): parser.error('Not found: '+str(args.directory))
    data=collect(args.directory)
    if not data:
        print('No candidate game stdout files found. Check --keep and folder path.'); return
    prediction_n=sum(len(pred) for _,pred,_ in data)
    observed_n=sum(len(obs) for _,_,obs in data)
    pair=[]; unpaired=[]; invalid=[]
    for game, pred, obs in data:
        for o in obs:
            key=(o['start'],o['slot'],o['camp'])
            p=pred.get(key)
            if p is None: unpaired.append((game,o)); continue
            pair.append((game,p,o))
            if p.get('hp4',-1)<0 or p.get('rem4',-1)<0:
                invalid.append((game,p,o))
    compared=[(game,p,o) for game,p,o in pair if p.get('hp4',-1)>=0 and p.get('rem4',-1)>=0]
    print('CAMP MODEL — FORECAST/FOLLOW-UP JOIN AUDIT (EXISTING LOGS)')
    print(f'Candidate match logs: {len(data)}; forecast keys: {prediction_n}; follow-ups: {observed_n}')
    print(f'RAW MATCHED KEYS: {len(pair)}; unmatched follow-ups: {len(unpaired)}')
    print(f'Matched but prediction never reached round 4: {len(invalid)}')
    print(f'Matched with both round-4 forecast values: {len(compared)}')
    all_preds=[p for _,mp,_ in data for p in mp.values()]
    print('All forecasts: predicted deaths=',sum(p.get('death',-1)>0 for p in all_preds),
          'early clear or stop (turns < 4)=',sum(p.get('turns',99)<4 for p in all_preds),
          'hp4 missing=',sum(p.get('hp4',-1)<0 for p in all_preds),
          'complete stationary=',sum(p.get('confident',0)==1 for p in all_preds))
    reason=Counter()
    for _,p,_ in invalid:
        reason['simulated fewer than 4 turns' if p.get('turns',99)<4 else 'ran >=4 turns but no four-round forecast']+=1
    if reason: print('Why matched predictions are unusable:',dict(reason))
    if compared:
        h_err=[abs(p['hp4']-o.get('hp',p['hp4'])) for _,p,o in compared]
        m_err=[abs(p['rem4']-o.get('rem',p['rem4'])) for _,p,o in compared]
        print(f'Naive 4-round MAE: self HP {statistics.mean(h_err):.1f}; monster remaining HP {statistics.mean(m_err):.1f}')
        print('CAUTION: follow-up is logged only when the champion is still farming the same live camp;')
        print('the model assumes simplified timing, spells and movement, so this is a biased subset.')
    print('\nMatched examples:')
    for game,p,o in pair[:8]:
        print(f" {game} body={p['slot']} group={p['camp']} start={p['r']} obs_r={o.get('r','?')} "
              f"pred_turns={p.get('turns','?')} pred_clear={p.get('clear','?')} "
              f"pred_hp4={p.get('hp4','?')} pred_rem4={p.get('rem4','?')} "
              f"actual_hp={o.get('hp','?')} actual_rem={o.get('rem','?')}")
    if unpaired:
        print('\nUnmatched follow-up examples:')
        for game,o in unpaired[:8]:
            print(f" {game} body={o['slot']} camp={o['camp']} forecast_start={o['start']} observed_r={o.get('r','?')}")
    if len(pair)==0:
        print('\nNo raw keys match. Please upload 1-2 team-*.stdout files; the logger/parser mismatch needs inspection.')
    elif not compared:
        print('\nThere ARE matching event keys, but the 4-round forecast is unavailable. The current')
        print('validation design needs a shorter prediction horizon and observation outside farm().')
    else:
        print('\nThis audit diagnoses the reporting issue; it does not yet validate the combat model.')

if __name__=='__main__': main()

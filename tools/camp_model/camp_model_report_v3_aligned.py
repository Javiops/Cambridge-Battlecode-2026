#!/usr/bin/env python3
"""Camp shadow forecast audit with CORRECT forecast horizon alignment.

Read stdout from A/B --keep and join [camp-model] with [camp-observed].
Prior analyzers compared every observation at start+4...start+10 against hp4/rem4,
which artificially inflates error as fighting proceeds. Only start+4 is a valid
4-round comparison. Logs need not be re-generated for this audit.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import re
import statistics

MODEL = re.compile(r'\[camp-model\]\s*(.*)')
OBS = re.compile(r'\[camp-observed\]\s*(.*)')
FIELD = re.compile(r'([a-zA-Z][a-zA-Z0-9_]*)=(-?(?:\d+(?:\.\d+)?|\.\d+))')

def parse(line):
    return {k: float(v) if '.' in v else int(v) for k,v in FIELD.findall(line)}

def stats(rows):
    if not rows: return 'no observations'
    def fmt(vals):
        return f'MAE={statistics.mean(abs(x) for x in vals):.1f}, bias={statistics.mean(vals):+.1f}, median AE={statistics.median(abs(x) for x in vals):.1f}'
    hp=[p['hp4']-o['hp'] for _,p,o in rows]
    rem=[p['rem4']-o['rem'] for _,p,o in rows]
    return f'HP {fmt(hp)}; remaining monster HP {fmt(rem)}'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path, help='A/B set folder, e.g. out/ab/.../official')
    ap.add_argument('--examples', type=int, default=8, help='Largest exactly-four-round errors to display')
    args=ap.parse_args()
    if not args.directory.is_dir(): ap.error(f'Directory not found: {args.directory}')
    matched=[]; all_pred=[]; unmatched=0; total_obs=0; games=0; duplicate_keys=0
    for log in sorted(args.directory.rglob('team-*.stdout')):
        side=log.parent.name.rsplit('_',1)[-1]
        if side not in ('A','B') or log.name != ('team-a.stdout' if side=='A' else 'team-b.stdout'): continue
        games+=1
        pred={}
        obs=[]
        for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
            m=MODEL.search(line)
            if m:
                p=parse(m.group(1))
                if all(k in p for k in ('r','slot','camp')):
                    key=(p['r'],p['slot'],p['camp'])
                    duplicate_keys += int(key in pred)
                    pred[key]=p
            m=OBS.search(line)
            if m:
                o=parse(m.group(1))
                if all(k in o for k in ('r','start','slot','camp')):obs.append(o)
        all_pred.extend(pred.values()); total_obs+=len(obs)
        for o in obs:
            p=pred.get((o['start'],o['slot'],o['camp']))
            if p is None: unmatched+=1
            else: matched.append((log.parent.name,p,o))
    lag=Counter(int(o['r']-o['start']) for _,p,o in matched)
    comparable=[(g,p,o) for g,p,o in matched if p.get('hp4',-1)>=0 and p.get('rem4',-1)>=0]
    exact=[r for r in comparable if r[2]['r']-r[2]['start']==4]
    late=[r for r in comparable if r[2]['r']-r[2]['start']>4]
    print('CAMP MODEL — TIME-ALIGNED SHADOW VALIDATION')
    print(f'Games with logs: {games}; forecasts: {len(all_pred)}; observations: {total_obs}; matched: {len(matched)}; unmatched: {unmatched}')
    print(f'Duplicate forecast keys: {duplicate_keys}; forecasts predicting death: {sum(p.get("death",-1)>0 for p in all_pred)}')
    print('Follow-up offset r - start:', ' '.join(f'+{d}:{lag[d]}' for d in sorted(lag)))
    print(f'Both 4-round values present: {len(comparable)}; exact +4: {len(exact)}; later than +4: {len(late)}')
    print('UNALIGNED prior calculation (invalid if delta > 4):')
    print(' ',stats(comparable))
    print('TIME-ALIGNED +4 comparisons (valid horizon):')
    print(' ',stats(exact))
    for label,filter_fn in [
        ('Complete visibility and no invented movement',lambda p:p.get('confident',0)==1),
        ('Movement predicted or incomplete visibility',lambda p:p.get('confident',0)!=1),
        ('One participating champion',lambda p:p.get('allies',0)==1),
        ('Multiple participating champions',lambda p:p.get('allies',0)>1),
        ('Already damaged camp',lambda p:p.get('awake',0)==1),
        ('Unopened camp',lambda p:p.get('awake',0)==0),
    ]:
        rows=[r for r in exact if filter_fn(r[1])]
        print(f'  {label}: {len(rows)}; {stats(rows)}')
    if len(exact)<50:
        print('WARNING: too few exact +4 samples for a reliable calibration. Do not apply hard camp rejection.')
        print('Next shadow bot should log forecasts for every elapsed turn or sample exact +4.')
    print('Largest exact +4 monster-HP errors:')
    for g,p,o in sorted(exact,key=lambda r: abs(r[1]['rem4']-r[2]['rem']),reverse=True)[:max(0,args.examples)]:
        print(f' {g} slot={p["slot"]} camp={p["camp"]} r={p["r"]}->{o["r"]}'
              f' enemies_seen={p.get("seen","?")}, predicted_allies={p.get("allies","?")}'
              f' move={p.get("move","?")} confident={p.get("confident","?")}'
              f' HP={p["hp4"]:.0f}/{o["hp"]:.0f}'
              f' monster_remaining={p["rem4"]:.0f}/{o["rem"]:.0f}')
    print('\nIMPORTANT: +4 alignment fixes one error, but only continuing camp fights are observed;')
    print('not cleared/abandoned camps. The model still omits spells, exact movement and other actors.')

if __name__=='__main__': main()

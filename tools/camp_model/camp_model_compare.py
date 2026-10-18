#!/usr/bin/env python3
"""Compare basic-only vs ability-aware camp forecasts on exact +4 follow-ups.

Does not treat continuing fights as representative of all camp attempts.
Both forecasts use the same initial observed camp/champion state.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import re
import statistics

M = re.compile(r'\[camp-model\]\s*(.*)')
O = re.compile(r'\[camp-observed\]\s*(.*)')
F = re.compile(r'([a-zA-Z][a-zA-Z0-9_]*)=(-?(?:\d+(?:\.\d+)?|\.\d+))')

def parse(x):
    return {k: float(v) if '.' in v else int(v) for k,v in F.findall(x)}

def report(label, rows):
    print(f'  {label}: {len(rows)} observations')
    if not rows: return
    for metric,truth,original,new in [('Champion HP','hp','hp4','hp4skills'),
                                       ('Monster HP','rem','rem4','rem4skills')]:
        rows_=[(p,o) for p,o in rows if p.get(original,-1)>=0 and p.get(new,-1)>=0]
        if not rows_:
            print(f'    {metric}: no paired numeric predictions')
            continue
        e1=[p[original]-o[truth] for p,o in rows_]
        e2=[p[new]-o[truth] for p,o in rows_]
        a1=statistics.mean(abs(x) for x in e1)
        a2=statistics.mean(abs(x) for x in e2)
        improved=sum(abs(b)<abs(a) for a,b in zip(e1,e2))
        worse=sum(abs(b)>abs(a) for a,b in zip(e1,e2))
        changed=sum(b!=a for a,b in zip(e1,e2))
        print(f'    {metric}: old MAE {a1:.1f}, new MAE {a2:.1f} '
              f'({a2-a1:+.1f}), old bias {statistics.mean(e1):+.1f}, new bias {statistics.mean(e2):+.1f}; '
              f'changed={changed}, better/worse={improved}/{worse}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder', type=Path)
    a=p.parse_args()
    if not a.folder.is_dir(): p.error('missing folder: '+str(a.folder))
    matches=[]; other_offsets=Counter(); games=0; unpaired=0; total=0
    for log in sorted(a.folder.rglob('team-*.stdout')):
        side=log.parent.name.rsplit('_',1)[-1]
        if side not in ('A','B') or log.name != ('team-a.stdout' if side=='A' else 'team-b.stdout'): continue
        games+=1; forecasts={}
        observations=[]
        for line in log.read_text(encoding='utf-8',errors='replace').splitlines():
            m=M.search(line)
            if m:
                f=parse(m[1]);
                if all(k in f for k in ('r','slot','camp')):
                    forecasts[(f['r'],f['slot'],f['camp'])]=f
            m=O.search(line)
            if m:
                f=parse(m[1]);
                if all(k in f for k in ('r','start','slot','camp')):
                    observations.append(f)
        total+=len(observations)
        for obs in observations:
            pred=forecasts.get((obs['start'],obs['slot'],obs['camp']))
            if not pred:
                unpaired+=1;continue
            offset=obs['r']-obs['start'];other_offsets[offset]+=1
            if offset==4:matches.append((pred,obs))
    print('CAMP MODEL — SIDE-BY-SIDE FOUR-ROUND COMPARISON (SHADOW ONLY)')
    print(f'Games={games}; observations={total}; unmatched={unpaired}; exact +4={len(matches)}')
    print('All follow-up offsets:',dict(sorted(other_offsets.items())))
    report('All exact-four-round cases', matches)
    report('Full monster visibility, no modeled walking',[(p,o) for p,o in matches if p.get('confident',0)==1])
    report('One predicted ally',[(p,o) for p,o in matches if p.get('allies',0)==1])
    report('Two or more predicted allies',[(p,o) for p,o in matches if p.get('allies',0)>1])
    report('No enemy in personal vision',[(p,o) for p,o in matches if p.get('foe8',1)==0])
    report('Visible enemy within 8',[(p,o) for p,o in matches if p.get('foe8',0)==1])
    if len(matches)<100:
        print('WARNING: too few exact-four-round cases; do not enable camp gating.')
    print('LIMITATION: observations exist only for surviving champions who keep fighting the same visible camp.')
    print('Better four-round damage forecasts do NOT yet prove that the model predicts full clear/deaths/capture.')

if __name__=='__main__': main()

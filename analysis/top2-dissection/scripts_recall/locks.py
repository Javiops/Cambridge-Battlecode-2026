import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
import collections
sel=load_sel()
own=collections.Counter(); opp=collections.Counter(); after=collections.defaultdict(collections.Counter); ex=collections.defaultdict(list)
for g in sel:
    m=load_map(g['map']); al=altars(m); side=0 if g['side']=='a' else 1
    rounds,order,events,types,camps=load_game(g['match'])
    evs=[(r,e) for r in order for e in events[r] if e['ak']==1]
    for r,e in evs:
        if e['k']!=20: continue
        t=types[e['a']][0]; p=tuple(e['apos'])
        alt=min(al,key=lambda a:cheb(p,a)) if al else None
        if t==side: own[g['team']]+=1; continue
        opp[g['team']]+=1
        # our team's behaviour at that altar in the next 60 rounds
        k12=[r2 for r2,e2 in evs if r<r2<=r+60 and e2['k']==12 and types[e2['a']][0]==side and cheb(tuple(e2['apos']),alt)<=1]
        k18=[r2 for r2,e2 in evs if r<r2<=r+60 and e2['k']==18 and types[e2['a']][0]==side and cheb(tuple(e2['apos']),alt)<=1]
        k5n=[r2 for r2,e2 in evs if r<r2<=r+60 and e2['k']==5 and not e2['eff'] and not e2['keff'] and types[e2['a']][0]==side and cheb(tuple(e2['apos']),alt)<=2]
        near=[r2 for r2 in order if r<r2<=r+60 and any(c['team']==side and c['alive'] and cheb((c['x'],c['y']),alt)<=2 for c in rounds[r2].values())]
        key='no_visit' if not near else ('tributed' if k18 else ('attacked_lock' if k5n else ('tried_k12_only' if k12 else 'visited_no_action')))
        after[g['team']][key]+=1
        if len(ex[(g['team'],key)])<3: ex[(g['team'],key)].append((g['match'][:8],g['map'],r,alt,len(k12),len(k5n),len(k18)))
print('own k20 (lock placements) per team:',own,' opponents k20 vs team:',opp)
for t in ('mite','uni'): print(t,'after opponent lock:',dict(after[t])); 
for k,v in ex.items(): print(k,v)

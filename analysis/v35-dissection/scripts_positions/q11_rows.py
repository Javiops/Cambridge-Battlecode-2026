"""Q11 rows/expanse: per group clearing: rounds from first hit to capture, distinct hitters, hitters at the kill round; capture->tribute delay. us vs opp."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
CL = collections.defaultdict(list); TD = collections.defaultdict(list)
for rec, g in games():
    if rec['map'] not in ('rows', 'expanse', 'monolith', 'lanes'): continue
    # per camp index -> group; track first hit round per (group, cycle)
    first = {}; hitters = collections.defaultdict(set)
    campgrp = {k['i']: k['grp'] for k in g.camps[0].values()}
    for r in g.order:
        for e in g.events[r]:
            if e['ak'] == 1 and e['keff']:
                for x in e['keff']:
                    if x.get('hp', 0) < 0:
                        gi = campgrp.get(x['i'])
                        if gi is None: continue
                        t = g.types[e['a']][0]
                        if (gi, t) not in first: first[(gi, t)] = r
                        hitters[(gi, t)].add(e['a'])
        for (rr, i, gm) in [c for c in g.caps if c[0] == r]:
            t = g.types[i][0]; who = 'us' if t == g.us else 'opp'
            c = g.rounds[r].get(i)
            if c['x'] < 0: c = g.rounds[g.order[g.ridx[r]-1]][i]
            gi = g.camptiles.get((c['x'], c['y']))
            if gi is None: gi = min(g.gtiles, key=lambda gg: min(cheb((c['x'], c['y']), q) for q in g.gtiles[gg]))
            if (gi, t) in first:
                CL[(rec['map'], who)].append((r - first[(gi, t)], len(hitters[(gi, t)])))
                del first[(gi, t)]; hitters[(gi, t)] = set()
            # other team's partial state reset too
            for tt in (0, 1):
                if (gi, tt) in first and tt != t: del first[(gi, tt)]; hitters[(gi, tt)] = set()
    # capture -> tribute delay per champion
    pend = {}
    for r in g.order:
        for (rr, i, gm) in [c for c in g.caps if c[0] == r]:
            if i not in pend: pend[i] = r
        for e in g.events[r]:
            if e['ak'] == 1 and e['k'] == 18 and e['a'] in pend:
                who = 'us' if g.types[e['a']][0] == g.us else 'opp'
                TD[(rec['map'], who)].append(r - pend[e['a']]); del pend[e['a']]
            for x in e['eff']:
                if x.get('alive') == 0 and x['i'] in pend: del pend[x['i']]
print('## group clearing on farm maps: rounds from the team\'s first hit on the group to its capture (median/mean), distinct hitters (mean), share cleared by 1 / 2 / 3+ hitters; capture -> tribute delay per champion (median/mean rounds)')
print('| map | who | clearings | first hit->capture med/mean | hitters mean | 1 / 2 / 3+ hitters | tribute delay med/mean (n) |'); print('|---|---|---|---|---|---|---|')
for m in ('rows', 'expanse', 'monolith', 'lanes'):
    for who in ('us', 'opp'):
        L = CL[(m, who)]; T = TD[(m, who)]
        if not L: continue
        print('| %s | %s | %d | %d / %.1f | %.2f | %d%% / %d%% / %d%% | %d / %.1f (%d) |' % (m, who, len(L), st.median([x[0] for x in L]), st.mean([x[0] for x in L]), st.mean([x[1] for x in L]), *(round(100*sum(1 for x in L if min(x[1], 3) == k)/len(L)) for k in (1, 2, 3)), st.median(T) if T else 0, st.mean(T) if T else 0, len(T)))

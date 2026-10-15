"""Q13 stacking: for every capture, the group's initial total hp (>=3000 = 'big' = the study27 stacking threshold), distinct hitters, concurrent hitters
(max number of the team's champions hitting the group in one round), first hit -> capture rounds. Per map x hp class x who. Also: per round, when the team hits a big group, how many hit it that round."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
CAP = collections.defaultdict(list); CONC = collections.defaultdict(collections.Counter); NG = collections.Counter(); PG = collections.defaultdict(collections.Counter)
for rec, g in games():
    NG[rec['map']] += 1
    campgrp = {k['i']: k['grp'] for k in g.camps[0].values()}
    ghp = collections.Counter()
    for k in g.camps[0].values(): ghp[k['grp']] += k['hp']
    first = {}; hitters = collections.defaultdict(set); conc = collections.defaultdict(int)
    for r in g.order:
        per = collections.defaultdict(set)
        for e in g.events[r]:
            if e['ak'] == 1 and e['keff']:
                for x in e['keff']:
                    if x.get('hp', 0) < 0:
                        gi = campgrp.get(x['i'])
                        if gi is None: continue
                        t = g.types[e['a']][0]
                        if (gi, t) not in first: first[(gi, t)] = r
                        hitters[(gi, t)].add(e['a']); per[(gi, t)].add(e['a'])
        for (gi, t), s in per.items():
            conc[(gi, t)] = max(conc[(gi, t)], len(s))
            who = 'us' if t == g.us else 'opp'; big = 'big' if ghp[gi] >= 3000 else 'small'
            CONC[(rec['map'], who, big)][len(s)] += 1
            CONC[('ALL', who, big)][len(s)] += 1
        for (rr, i, gm) in [c for c in g.caps if c[0] == r]:
            t = g.types[i][0]; who = 'us' if t == g.us else 'opp'
            c = g.rounds[r].get(i)
            if c['x'] < 0: c = g.rounds[g.order[g.ridx[r]-1]][i]
            gi = g.camptiles.get((c['x'], c['y']))
            if gi is None: gi = min(g.gtiles, key=lambda gg: min(cheb((c['x'], c['y']), q) for q in g.gtiles[gg]))
            big = 'big' if ghp[gi] >= 3000 else 'small'
            if (gi, t) in first:
                d = (r - first[(gi, t)], len(hitters[(gi, t)]), conc[(gi, t)], gm, ghp[gi])
                CAP[(rec['map'], who, big)].append(d); CAP[('ALL', who, big)].append(d)
                PG[(rec['match'][:8], who)]['caps_'+big] += 1; PG[(rec['match'][:8], who)]['hit3_'+big] += conc[(gi, t)] >= 3
                del first[(gi, t)]; hitters[(gi, t)] = set(); conc[(gi, t)] = 0
            for tt in (0, 1):
                if (gi, tt) in first and tt != t: del first[(gi, tt)]; hitters[(gi, tt)] = set(); conc[(gi, tt)] = 0
print('## captures by group hp class (big = initial group hp >= 3000): n, per game, first hit->capture med/mean, distinct hitters mean, max concurrent hitters mean, share with max concurrent 1/2/3/4+, gems per capture')
print('| map | who | class | captures | per game | first hit->cap med/mean | distinct hitters | max concurrent | conc 1/2/3/4+ | gems/cap |'); print('|---'*11 + '|')
maps = ['ALL'] + sorted(m for m in NG)
for m in maps:
    for big in ('big', 'small'):
        for who in ('us', 'opp'):
            L = CAP[(m, who, big)]
            if not L: continue
            n = len(L); ng = sum(NG.values()) if m == 'ALL' else NG[m]
            print('| %s | %s | %s | %d | %.1f | %d / %.1f | %.2f | %.2f | %d/%d/%d/%d%% | %.0f |' % (m, who, big, n, n/ng, st.median([x[0] for x in L]), st.mean([x[0] for x in L]), st.mean([x[1] for x in L]), st.mean([x[2] for x in L]), *(round(100*sum(1 for x in L if min(x[2], 4) == k)/n) for k in (1, 2, 3, 4)), st.mean([x[3] for x in L])))
print('\n## group-rounds under attack: how many of the team\'s champions hit the group in the same round (share of group-rounds with >=1 hitter)')
print('| map | who | class | group-rounds | 1 | 2 | 3 | 4+ |'); print('|---'*8 + '|')
for m in maps:
    for big in ('big', 'small'):
        for who in ('us', 'opp'):
            c = CONC[(m, who, big)]; n = sum(c.values())
            if not n: continue
            print('| %s | %s | %s | %d | %d%% | %d%% | %d%% | %d%% |' % (m, who, big, n, 100*c[1]/n, 100*c[2]/n, 100*c[3]/n, 100*sum(v for k, v in c.items() if k >= 4)/n))

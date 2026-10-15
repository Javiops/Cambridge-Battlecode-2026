"""Q7: where and how champions die: territory, near camp (awake?), allies/enemies within 6 at death and 5 rounds before, what the victim was doing 3 rounds before, gems lost. us vs opp."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
D = collections.defaultdict(list)
for rec, g in games():
    mp = g.mp; keys = split_keys(rec)
    for (r, i) in g.deaths:
        t = g.types[i][0]; who = 'us' if t == g.us else 'opp'
        k = g.ridx[r]; pr = g.order[k-1]; sn = g.rounds[pr]; c = sn[i]
        r5 = g.order[max(0, k-6)]; s5 = g.rounds[r5]; c5 = s5[i]
        allies = sum(1 for o in sn.values() if o['team'] == t and o['alive'] and o['i'] != i and cheb((o['x'], o['y']), (c['x'], c['y'])) <= 6)
        ens = sum(1 for o in sn.values() if o['team'] != t and o['alive'] and cheb((o['x'], o['y']), (c['x'], c['y'])) <= 6)
        allies5 = sum(1 for o in s5.values() if o['team'] == t and o['alive'] and o['i'] != i and cheb((o['x'], o['y']), (c5['x'], c5['y'])) <= 6) if c5['alive'] else None
        ens5 = sum(1 for o in s5.values() if o['team'] != t and o['alive'] and cheb((o['x'], o['y']), (c5['x'], c5['y'])) <= 6) if c5['alive'] else None
        tr = terr(mp, c['x'], c['y'], t)
        nc = any(k_['alive'] and cheb((c['x'], c['y']), (k_['x'], k_['y'])) <= 2 for k_ in g.camps[pr].values())
        campdmg = any(r_ in range(r5, r+1) for r_ in [])
        # was the victim hit by camps in the last 5 rounds / was it attacking a camp
        acts5 = collections.Counter()
        for rr in g.order[max(0, k-5):k]:
            acts5[primary(g.acts[i][rr])] += 1
        camphit = 0
        for rr in g.order[max(0, k-5):k+1]:
            for e in g.events[rr]:
                if e['ak'] == 2 and any(x['i'] == i and x.get('hp', 0) < 0 for x in e['eff']): camphit += 1
        # killer count: distinct enemies that damaged victim in last 5 rounds
        killers = set(h['a'] for h in g.hits if h['v'] == i and r5 <= h['r'] <= r)
        d = dict(r=r, ty=c['ty'], tr=tr, nc=nc, allies=allies, ens=ens, allies5=allies5, ens5=ens5, gems=c['gems'], camphit=camphit, killers=len(killers), farming=acts5['attack camp']+acts5['cast@camp'], recall=acts5['recall'], hp5=c5['hp']/c5['mhp'] if c5['alive'] else None, sd=spawn_dist(mp, c['x'], c['y'], t), m=rec['match'][:8], map=rec['map'], pos=(c['x'], c['y']))
        for kk in keys: D[(kk, who)].append(d)
print('## deaths: n, per game, territory own/mid/enemy, next to a living camp, allies within 6 at death (0 / 1 / 2+), enemies within 6 (1 / 2 / 3+), 5 rounds earlier allies within 6 = 0, farming a camp in the 5 rounds before (>=2 rounds), hit by a camp in the last 5 rounds, median gems lost, distinct attackers, median dist to own spawn')
print('| split | who | n | per game | own/mid/enemy | at camp | allies 0/1/2+ | enemies 1/2/3+ | alone 5r before | farming before | camp-hit before | gems lost (med/mean) | attackers med | spawn dist med |')
print('|---'*15 + '|')
NG = collections.Counter()
for rec in SEL:
    for kk in split_keys(rec): NG[kk] += 1
for k in ['ALL', 'res:win', 'res:loss', 'opp:top10', 'opp:r11-30'] + sorted(set(x[0] for x in D if x[0].startswith('map:'))):
    for who in ('us', 'opp'):
        L = D[(k, who)]; n = len(L) or 1
        if not L: continue
        print('| %s | %s | %d | %.1f | %d/%d/%d | %d%% | %d/%d/%d | %d/%d/%d | %d%% | %d%% | %d%% | %d/%.0f | %d | %d |' % (k, who, len(L), len(L)/NG[k], *(round(100*sum(d['tr'] == x for d in L)/n) for x in ('own', 'mid', 'enemy')), 100*sum(d['nc'] for d in L)/n,
              *(round(100*sum(min(d['allies'], 2) == x for d in L)/n) for x in (0, 1, 2)), *(round(100*sum(min(d['ens'], 3) == x for d in L)/n) for x in (1, 2, 3)),
              100*sum(d['allies5'] == 0 for d in L)/n, 100*sum(d['farming'] >= 2 for d in L)/n, 100*sum(d['camphit'] > 0 for d in L)/n, st.median([d['gems'] for d in L]), st.mean([d['gems'] for d in L]), st.median([d['killers'] for d in L]), st.median([d['sd'] for d in L])))
print('\n## our deaths by champion type')
cnt = collections.Counter(d['ty'] for d in D[('ALL', 'us')]); cnto = collections.Counter(d['ty'] for d in D[('ALL', 'opp')])
print('us', cnt.most_common()); print('opp', cnto.most_common())
print('\n## our deaths: alone (no ally within 6) share by map and by type')
for m in sorted(set(d['map'] for d in D[('ALL', 'us')])):
    L = [d for d in D[('ALL', 'us')] if d['map'] == m]; Lo = [d for d in D[('ALL', 'opp')] if d['map'] == m]
    print('| %s | us %d deaths, alone %d%%, farming-before %d%%, gems lost mean %.0f | opp %d deaths, alone %d%%, farming-before %d%%, gems lost mean %.0f |' % (m, len(L), 100*sum(d['allies'] == 0 for d in L)/(len(L) or 1), 100*sum(d['farming'] >= 2 for d in L)/(len(L) or 1), st.mean([d['gems'] for d in L]) if L else 0, len(Lo), 100*sum(d['allies'] == 0 for d in Lo)/(len(Lo) or 1), 100*sum(d['farming'] >= 2 for d in Lo)/(len(Lo) or 1), st.mean([d['gems'] for d in Lo]) if Lo else 0))
print('\n## our deaths by round bin (per game)')
for b in range(10):
    L = [d for d in D[('ALL', 'us')] if rbin(d['r']) == b]; Lo = [d for d in D[('ALL', 'opp')] if rbin(d['r']) == b]
    print('| %s | us %d | opp %d |' % (BINS[b], len(L), len(Lo)))

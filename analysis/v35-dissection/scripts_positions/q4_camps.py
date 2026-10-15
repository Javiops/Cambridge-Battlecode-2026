"""Q4: territory over time via captures: who captures mid/own/enemy groups by 50-round bin; enemy-half farming; own-half camps lost; relation to result."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
CAP = collections.defaultdict(collections.Counter)   # (split, who, bin) -> terr -> captures
GEM = collections.defaultdict(collections.Counter)
LOST = collections.defaultdict(list)  # split -> first round an own-half group was captured by enemy
PERGAME = []
ng = 0
for rec, g in games():
    ng += 1; keys = split_keys(rec)
    first_lost = None; cnt = collections.Counter(); gems = collections.Counter()
    for (r, i, gm) in g.caps:
        t = g.types[i][0]; who = 'us' if t == g.us else 'opp'
        c = g.rounds[r].get(i)
        if not c or c['x'] < 0:
            c = g.rounds[g.order[g.ridx[r]-1]].get(i)
        # group by tile (champion stands on a camp tile)
        gi = g.camptiles.get((c['x'], c['y']))
        if gi is None:
            # nearest group tile
            gi = min(g.gtiles, key=lambda gg: min(cheb((c['x'], c['y']), tt) for tt in g.gtiles[gg]))
        tr = g.gterr[gi][t]
        b = rbin(r)
        for k in keys:
            CAP[(k, who, b)][tr] += 1; CAP[(k, who, b)]['n'] += 1
            GEM[(k, who, b)][tr] += gm
        cnt[(who, tr)] += 1; gems[(who, tr)] += gm
        if who == 'opp' and tr == 'enemy' and first_lost is None: first_lost = r
    if first_lost is not None:
        for k in keys: LOST[k].append(first_lost)
    for k in keys: LOST[k+'_games'].append(1)
    PERGAME.append(dict(m=rec['match'][:8], map=rec['map'], res=rec['res'], opp=rec['opp'], orank=rec['orank'], rounds=rec['rounds'], score=rec['score'], oscore=rec['oscore'],
                        us_own=cnt[('us', 'own')], us_mid=cnt[('us', 'mid')], us_en=cnt[('us', 'enemy')], op_own=cnt[('opp', 'own')], op_mid=cnt[('opp', 'mid')], op_en=cnt[('opp', 'enemy')],
                        g_us_mid=gems[('us', 'mid')], g_op_mid=gems[('opp', 'mid')], g_us_en=gems[('us', 'enemy')], g_op_en=gems[('opp', 'enemy')], first_lost=first_lost))
print('games', ng)
print('\n## captures by territory of the group (own/mid/enemy from the capturer\'s point of view), by 50-round bin')
print('| split | who | ' + ' | '.join(BINS) + ' | total own/mid/enemy | gems own/mid/enemy |'); print('|---'*14 + '|')
for k in ['ALL'] + sorted(set(x[0] for x in CAP if x[0] != 'ALL')):
    for who in ('us', 'opp'):
        out = []; tot = collections.Counter(); gt = collections.Counter()
        for b in range(10):
            c = CAP[(k, who, b)]; tot += c; gt += GEM[(k, who, b)]
            out.append('%d/%d/%d' % (c['own'], c['mid'], c['enemy']) if c['n'] else '-')
        print('| %s | %s | %s | %d/%d/%d | %d/%d/%d |' % (k, who, ' | '.join(out), tot['own'], tot['mid'], tot['enemy'], gt['own'], gt['mid'], gt['enemy']))
print('\n## own-half camps captured by the enemy: games where it happens, first round')
print('| split | games | games with own-half group lost | first loss round median / min / p25 |'); print('|---|---|---|---|')
for k in ['ALL'] + sorted(set(x for x in LOST if not x.endswith('_games') and x != 'ALL')):
    L = LOST[k]; n = len(LOST[k+'_games'])
    if L: print('| %s | %d | %d (%d%%) | %d / %d / %d |' % (k, n, len(L), 100*len(L)/n, st.median(L), min(L), sorted(L)[len(L)//4]))
    else: print('| %s | %d | 0 | - |' % (k, n))
print('\n## per-game mid/enemy captures vs result (mean per game)')
print('| split | games | us mid caps | opp mid caps | us enemy-half caps | opp enemy-half caps (=our camps lost) | us own | opp own | us mid gems | opp mid gems | opp gems from our half |'); print('|---'*12 + '|')
def agg(L, name):
    n = len(L) or 1
    print('| %s | %d | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f | %.0f | %.0f | %.0f |' % (name, len(L), sum(d['us_mid'] for d in L)/n, sum(d['op_mid'] for d in L)/n, sum(d['us_en'] for d in L)/n, sum(d['op_en'] for d in L)/n, sum(d['us_own'] for d in L)/n, sum(d['op_own'] for d in L)/n, sum(d['g_us_mid'] for d in L)/n, sum(d['g_op_mid'] for d in L)/n, sum(d['g_op_en'] for d in L)/n))
agg(PERGAME, 'ALL')
for res in ('win', 'loss'): agg([d for d in PERGAME if d['res'] == res], 'res:'+res)
for m in sorted(set(d['map'] for d in PERGAME)):
    for res in ('win', 'loss'): agg([d for d in PERGAME if d['map'] == m and d['res'] == res], 'map:%s %s' % (m, res))
print('\n## mid-camp balance vs result: games grouped by (us mid caps - opp mid caps)')
for lo, hi in ((-99, -6), (-5, -1), (0, 0), (1, 5), (6, 99)):
    L = [d for d in PERGAME if lo <= d['us_mid']-d['op_mid'] <= hi]
    if L: print('| diff %d..%d | %d games | win %d%% |' % (lo, hi, len(L), 100*sum(d['res'] == 'win' for d in L)/len(L)))
print('\n## games where the opponent took most from our half (opp enemy-half caps, gems)')
for d in sorted(PERGAME, key=lambda d: -d['g_op_en'])[:15]: print(d)

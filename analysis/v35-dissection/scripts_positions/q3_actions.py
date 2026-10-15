"""Q3: what each champion type does per round (share of alive rounds), ours vs theirs; where idle rounds happen."""
import sys, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
ACT = collections.defaultdict(collections.Counter)   # (split, who, type) -> label counts
IDLE = collections.defaultdict(collections.Counter)  # (split, who) -> where idle
IDLEX = []  # examples of long idle streaks (us)
DEAD = collections.defaultdict(collections.Counter)
LABS = ['move', 'attack camp', 'cast@camp', 'attack champ', 'cast@champ', 'dash', 'ability(no eff)', 'tribute', 'recall', 'buy', 'nothing', 'arrive', 'attack(miss)']
ng = 0
for rec, g in games():
    ng += 1; keys = split_keys(rec); mp = g.mp
    for who, t in (('us', g.us), ('opp', g.them)):
        streak = {}
        for r in g.order[1:]:
            sn = g.rounds[r]
            ens = [c for c in sn.values() if c['team'] != t and c['alive']]
            for i in g.ids[t]:
                c = sn[i]
                for k in keys: DEAD[(k, who)]['total'] += 1
                if not c['alive']:
                    for k in keys: DEAD[(k, who)]['dead'] += 1
                    continue
                lab = primary(g.acts[i][r])
                for k in keys:
                    ACT[(k, who, c['ty'])][lab] += 1; ACT[(k, who, c['ty'])]['_n'] += 1
                    ACT[(k, who, 'ALL')][lab] += 1; ACT[(k, who, 'ALL')]['_n'] += 1
                if lab == 'nothing':
                    sd = spawn_dist(mp, c['x'], c['y'], t); tr = terr(mp, c['x'], c['y'], t)
                    nc = any(k_['alive'] and cheb((c['x'], c['y']), (k_['x'], k_['y'])) <= 2 for k_ in g.camps[r].values())
                    ne = min([cheb((c['x'], c['y']), (e['x'], e['y'])) for e in ens], default=99)
                    ad = altar_dist(mp, c['x'], c['y'])
                    hpf = c['hp']/c['mhp']
                    where = 'spawn' if sd <= 2 else ('altar' if ad <= 2 else ('camp' if nc else tr))
                    for k in keys:
                        IDLE[(k, who)][where] += 1; IDLE[(k, who)]['_n'] += 1
                        if ne <= 8: IDLE[(k, who)]['enemy<=8'] += 1
                        if ne <= 3: IDLE[(k, who)]['enemy<=3'] += 1
                        if hpf < 0.5: IDLE[(k, who)]['hp<50%'] += 1
                        if c['gems'] > 0: IDLE[(k, who)]['carrying gems'] += 1
                        if nc and g.camps[r] and any(k_['alive'] and k_['awake'] and cheb((c['x'], c['y']), (k_['x'], k_['y'])) <= 2 for k_ in g.camps[r].values()): IDLE[(k, who)]['camp awake'] += 1
                    streak[i] = streak.get(i, 0) + 1
                else:
                    if who == 'us' and streak.get(i, 0) >= 8:
                        IDLEX.append((streak[i], rec['match'][:8], rec['map'], r - streak[i], c['ty'], (c['x'], c['y']), tr if 'tr' in dir() else '', rec['res']))
                    streak[i] = 0
print('games', ng)
print('\n## action share per champion type (% of alive champion-rounds). dead = % of champion-rounds dead')
print('| split | who | type | n rounds | ' + ' | '.join(LABS) + ' |'); print('|---'*(len(LABS)+4) + '|')
for k in ['ALL', 'res:win', 'res:loss', 'opp:top10', 'opp:r11-30']:
    for who in ('us', 'opp'):
        tys = sorted(set(x[2] for x in ACT if x[0] == k and x[1] == who and x[2] != 'ALL'))
        for ty in ['ALL'] + tys:
            a = ACT[(k, who, ty)]; n = a['_n'] or 1
            if a['_n'] < 500: continue
            print('| %s | %s | %s | %d | %s |' % (k, who, ty, a['_n'], ' | '.join('%d' % round(100*a[l]/n) for l in LABS)))
print('\n## dead share of champion-rounds')
for k in ['ALL', 'res:win', 'res:loss', 'opp:top10', 'opp:r11-30'] + sorted(set(x[0] for x in DEAD if x[0].startswith('map:'))):
    print('| %s | us %d%% | opp %d%% |' % (k, 100*DEAD[(k, 'us')]['dead']/DEAD[(k, 'us')]['total'], 100*DEAD[(k, 'opp')]['dead']/DEAD[(k, 'opp')]['total']))
print('\n## where "nothing" rounds happen (% of idle champion-rounds): at spawn / near altar / near living camp / own / mid / enemy; context flags')
print('| split | who | idle rounds | spawn | altar | camp | own | mid | enemy | enemy<=8 | enemy<=3 | hp<50% | carrying gems | camp awake next to it |')
print('|---'*14 + '|')
for k in ['ALL', 'res:win', 'res:loss', 'opp:top10', 'opp:r11-30'] + sorted(set(x[0] for x in IDLE if x[0].startswith('map:'))):
    for who in ('us', 'opp'):
        a = IDLE[(k, who)]; n = a['_n'] or 1
        print('| %s | %s | %d | %s |' % (k, who, a['_n'], ' | '.join('%d%%' % round(100*a[x]/n) for x in ('spawn', 'altar', 'camp', 'own', 'mid', 'enemy', 'enemy<=8', 'enemy<=3', 'hp<50%', 'carrying gems', 'camp awake'))))
print('\n## our longest idle streaks (len, match, map, start r, type, tile, res)')
for x in sorted(IDLEX, reverse=True)[:25]: print(x)
import statistics
print('idle streaks >=8 (us):', len(IDLEX), 'per game %.1f' % (len(IDLEX)/ng))

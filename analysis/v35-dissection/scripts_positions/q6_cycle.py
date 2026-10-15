"""Q6: farming-cycle efficiency on farm maps (rows/expanse/lanes/monolith/elkring): for every camp group capture, latency from the group's (re)spawn to its capture,
champions standing idle next to a dead camp (waiting), bag size at tribute, trips. us vs opp, per map."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
LAT = collections.defaultdict(list); WAIT = collections.defaultdict(collections.Counter); BAG = collections.defaultdict(list); PG = []
for rec, g in games():
    if rec['map'] not in ('rows', 'expanse', 'lanes', 'monolith', 'elkring', 'interlock'): continue
    # group alive state per round: group alive if any camp of it alive
    galive = {}
    spawn_r = {}   # group -> round it (re)spawned (first round all alive after being dead)
    lat = {'us': [], 'opp': []}; wait = collections.Counter(); bags = {'us': [], 'opp': []}
    prev = None
    capr = collections.defaultdict(list)
    for (r, i, gm) in g.caps:
        c = g.rounds[r].get(i)
        if c['x'] < 0: c = g.rounds[g.order[g.ridx[r]-1]][i]
        gi = g.camptiles.get((c['x'], c['y']))
        if gi is None: gi = min(g.gtiles, key=lambda gg: min(cheb((c['x'], c['y']), q) for q in g.gtiles[gg]))
        capr[r].append((gi, 'us' if g.types[i][0] == g.us else 'opp', c['ty'], c['i']))
    for r in g.order:
        cur = {}
        for k in g.camps[r].values(): cur[k['grp']] = cur.get(k['grp'], False) or bool(k['alive'])
        if prev is not None:
            for gi in cur:
                if cur[gi] and not prev.get(gi, True): spawn_r[gi] = r
        else:
            for gi in cur: spawn_r[gi] = 0
        for gi, who, ty, i in capr.get(r, []):
            if gi in spawn_r:
                lat[who].append(r - spawn_r[gi]); LAT[(rec['map'], who)].append(r - spawn_r[gi])
                LAT[(rec['map'], who, g.gterr[gi][g.us if who == 'us' else g.them])].append(r - spawn_r[gi])
        # waiting: champion idle (nothing/move<=1?) within 3 of a dead group's tiles
        sn = g.rounds[r]
        for c in sn.values():
            if not c['alive']: continue
            who = 'us' if c['team'] == g.us else 'opp'
            lab = primary(g.acts[c['i']][r])
            if lab == 'nothing':
                deadnear = any(not cur.get(gi, True) and min(cheb((c['x'], c['y']), q) for q in ts) <= 3 for gi, ts in g.gtiles.items())
                if deadnear: wait[who] += 1; WAIT[(rec['map'], who)]['wait_dead_camp'] += 1
                WAIT[(rec['map'], who)]['idle'] += 1
            WAIT[(rec['map'], who)]['n'] += 1
        prev = cur
        for e in g.events[r]:
            if e['ak'] == 1 and e['k'] == 18:
                for x in e['eff']:
                    if x.get('gems', 0) < 0:
                        who = 'us' if g.types[e['a']][0] == g.us else 'opp'
                        bags[who].append(-x['gems']); BAG[(rec['map'], who)].append(-x['gems'])
    PG.append((rec['map'], rec['match'][:8], rec['res'], rec['opp'][:10], rec['orank'], rec['score'], rec['oscore'], rec['rounds'], st.median(lat['us']) if lat['us'] else None, st.median(lat['opp']) if lat['opp'] else None, len(lat['us']), len(lat['opp']), wait['us'], wait['opp'], len(bags['us']), st.median(bags['us']) if bags['us'] else 0, len(bags['opp']), st.median(bags['opp']) if bags['opp'] else 0))
print('## capture latency = rounds from group (re)spawn to capture (median / mean / p75), champion-rounds idle next to a dead camp (waiting) per game, idle share, tributes per game and median bag')
print('| map | who | captures | latency med/mean/p75 | own-half latency med | waiting at dead camp (champ-rounds per game) | idle share | tributes/game | median bag | p90 bag |')
print('|---'*10 + '|')
for m in ('rows', 'expanse', 'lanes', 'monolith', 'elkring', 'interlock'):
    ng = len([p for p in PG if p[0] == m])
    for who in ('us', 'opp'):
        L = LAT[(m, who)]; W = WAIT[(m, who)]; B = BAG[(m, who)]
        if not L: continue
        Lo = LAT[(m, who, 'own')]
        print('| %s | %s | %d | %d / %.1f / %d | %d | %.0f | %d%% | %.1f | %d | %d |' % (m, who, len(L), st.median(L), st.mean(L), sorted(L)[3*len(L)//4], st.median(Lo) if Lo else 0, W['wait_dead_camp']/ng, 100*W['idle']/(W['n'] or 1), len(B)/ng, st.median(B) if B else 0, sorted(B)[9*len(B)//10] if B else 0))
print('\n## per game (map, match, res, opp, rank, score, oscore, rounds, med latency us/opp, caps us/opp, waiting us/opp, tributes us n/med, opp n/med)')
for p in sorted(PG): print(p)

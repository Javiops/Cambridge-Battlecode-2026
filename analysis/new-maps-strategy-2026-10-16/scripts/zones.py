#!/usr/bin/env python3
"""Where each side plays on the new maps, by phase (2026-10-16, new-maps strategy thread).

Reads the decoded replays of the morning study (/mnt/project-files/analysis/new-maps-2026-10-16/data/compact + games.json)
and prints per map and class (top-10 winners, top-10 losers, us, our opponents): share of champion-rounds in our third /
the middle third / their third of the spawn-to-spawn axis, captures and deaths per zone, banks per zone, team spread,
and the opening route (zones of the first 6 captures). Zone = position of a tile between the two spawn centres:
t = d_own / (d_own + d_enemy) (Chebyshev); own t < 0.4, middle 0.4-0.6, enemy > 0.6.
usage: python3 zones.py [--json out.json]
"""
import gzip, json, collections, statistics as st, sys
D = '/mnt/project-files/analysis/new-maps-2026-10-16/data/'
games = json.load(open(D + 'games.json'))
def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
PH = [(0, 150), (150, 400), (400, 9999)]
def zone(p, own, en):
    a, b = cheb(p, own), cheb(p, en)
    t = a / max(a + b, 1)
    return 0 if t < 0.4 else (1 if t <= 0.6 else 2)
cache = {}
agg = collections.defaultdict(lambda: collections.defaultdict(list))
for g in games:
    cls = {'top': 'win' if g['win'] else 'lose', 'us': 'us', 'opp': 'opp'}[g['who']]
    mid = g['match']
    if mid not in cache:
        try: cache[mid] = json.load(gzip.open(D + 'compact/' + mid + '.json.gz', 'rt'))
        except FileNotFoundError: cache[mid] = None
    d = cache[mid]
    if d is None: continue
    t = 'ab'.index(g['side']); R = d['R']; CH = d['champs']
    me = [i for i, c in enumerate(CH) if c[1] == t]; th = [i for i, c in enumerate(CH) if c[1] != t]
    sc = {}
    for tt in (0, 1):
        ps = [R[0][3][i][:2] for i, c in enumerate(CH) if c[1] == tt and R[0][3][i][0] >= 0]
        if not ps: ps = [R[1][3][i][:2] for i, c in enumerate(CH) if c[1] == tt]
        sc[tt] = (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
    own, en = sc[t], sc[1 - t]
    A = agg[(g['map'], cls)]
    occ = [[0, 0, 0] for _ in PH]; spread = []
    banks = [0, 0, 0]; deaths = [[0, 0, 0] for _ in PH]
    for k in range(1, len(R)):
        r = R[k][0]; a = R[k - 1][3]; b = R[k][3]
        ph = 0 if r < 150 else (1 if r < 400 else 2)
        alive = [b[i][:2] for i in me if b[i][6]]
        for i in me:
            if b[i][6]: occ[ph][zone(b[i][:2], own, en)] += 1
            if a[i][6] and not b[i][6]: deaths[ph][zone(a[i][:2], own, en)] += 1
            if a[i][6] and b[i][6] and a[i][4] > 0 and b[i][4] == 0 and cheb(b[i][:2], own) > 4: banks[zone(b[i][:2], own, en)] += 1
        if len(alive) >= 2 and k % 10 == 0:
            cx = sum(p[0] for p in alive) / len(alive); cy = sum(p[1] for p in alive) / len(alive)
            spread.append(st.mean(cheb(p, (cx, cy)) for p in alive))
    caps = [[0, 0, 0] for _ in PH]
    for c in g['cap_seq']:
        r = c[0]; ph = 0 if r < 150 else (1 if r < 400 else 2)
        caps[ph][zone((c[4], c[5]), own, en)] += 1
    A['occ'].append(occ); A['deaths'].append(deaths); A['banks'].append(banks); A['caps'].append(caps)
    A['spread'].append(st.mean(spread) if spread else 0)
    A['route'].append(''.join('OME'[zone((c[4], c[5]), own, en)] + ('g' if c[2] == 0 else '') for c in g['cap_seq'][:6]))
    A['first_gold_buy'].append(g['first_buy'] or 0); A['n'].append(1)
    A['gold'].append(g['gold']); A['kills'].append(g['kills']); A['ndeaths'].append(g['deaths'])
out = {}
maps = sorted({k[0] for k in agg})
for m in maps:
    print(f'\n## {m}')
    print('| class | n | time own/mid/enemy r0-150 | r150-400 | r400+ | caps own/mid/enemy (all game) | deaths own/mid/enemy | banks own/mid/enemy | spread | gold | kills/deaths | typical opening |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for cls in ('win', 'lose', 'us', 'opp'):
        A = agg.get((m, cls))
        if not A: continue
        n = len(A['n'])
        def pct(ph):
            s = [sum(x[ph][z] for x in A['occ']) for z in range(3)]; T = max(sum(s), 1)
            return '/'.join(f'{100 * v / T:.0f}' for v in s)
        cz = [sum(x[ph][z] for x in A['caps'] for ph in range(3)) / n for z in range(3)]
        dz = [sum(x[ph][z] for x in A['deaths'] for ph in range(3)) / n for z in range(3)]
        bz = [sum(x[z] for x in A['banks']) / n for z in range(3)]
        rt = collections.Counter(A['route']).most_common(2)
        row = dict(n=n, occ=[pct(0), pct(1), pct(2)], caps=cz, deaths=dz, banks=bz, spread=st.mean(A['spread']),
                   gold=st.median(A['gold']), kills=st.mean(A['kills']), nd=st.mean(A['ndeaths']), route=rt)
        out[f'{m}/{cls}'] = row
        f = lambda v: '/'.join(f'{x:.1f}' for x in v)
        print(f"| {cls} | {n} | {row['occ'][0]} | {row['occ'][1]} | {row['occ'][2]} | {f(cz)} | {f(dz)} | {f(bz)} | {row['spread']:.1f} | {row['gold']:.0f} | {row['kills']:.1f}/{row['nd']:.1f} | {', '.join(f'{r} x{c}' for r, c in rt)} |")
if '--json' in sys.argv: json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)

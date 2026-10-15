import sys, json, collections, statistics as st
S = sys.argv[1]
d = json.load(open(f'{S}/reports/scripts_draft/shop.json'))
maps = {m: json.load(open(f'{S}/ws/mapsj/{m}.json')) for m in 'collision corners elkring expanse interlock lanes monolith packs rows'.split()}
def med(v): return round(st.median(v), 1) if v else None
def mean(v): return round(st.mean(v), 1) if v else None
def spawn_tiles(mp, side):
    x0, y0, x1, y1 = mp['spawnA']; w, h = mp['w'], mp['h']; s = mp['sym']
    def mir(p):
        x, y = p
        if side == 0: return p
        if s == 'V': return (x, h - 1 - y)
        if s == 'H': return (w - 1 - x, y)
        return (w - 1 - x, h - 1 - y)
    return set(mir((x, y)) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))
near_altar = collections.Counter(); per_cons = collections.Counter(); k20_after = collections.Counter(); kcount = collections.Counter()
stay = collections.defaultdict(list); left_after = collections.defaultdict(list); gaps_hi = collections.defaultdict(list)
dead_shop_delay = collections.defaultdict(list)
k20_stun_interrupt = 0
for g in d:
    team = g['team']; tm = 0 if g['side'] == 'a' else 1
    mp = maps[g['map']]; sp = spawn_tiles(mp, tm)
    altars = [(x, y) for y in range(mp['h']) for x in range(mp['w']) if mp['grid'][y][x] == 'A']
    ev = collections.defaultdict(list); rounds = {}
    for line in open(f"{S}/ws/steps/{g['match']}.c.jsonl"):
        x = json.loads(line)
        if x['t'] == 'ev': ev[x['r']].append(x)
        elif x['t'] == 'round': rounds[x['r']] = x
    order = sorted(rounds)
    for i, c in g['champs'].items():
        i = int(i)
        acts = collections.defaultdict(list)
        for r in order:
            for e in ev[r]:
                if e['ak'] == 1 and e['a'] == i and e['k'] in (20, 23, 11, 12, 26):
                    acts[e['k']].append((r, tuple(e['apos'])))
        for k, l in acts.items(): kcount[(team, k)] += len(l)
        for k in (20, 23):
            for r, p in acts[k]:
                dalt = min((max(abs(p[0] - a[0]), abs(p[1] - a[1])) for a in altars), default=99)
                near_altar[(team, k, 'altar<=2' if dalt <= 2 else 'far', 'spawn' if p in sp else 'out')] += 1
        ncons = sum(c.get('consumables', [])); per_cons[(team, 'cons', ncons)] += 1
        k20_after[(team, 'k20', len(acts[20]), 'cons', ncons)] += 1
        # spawn stays after high-hp recall arrivals
        pos = {r: None for r in order}
        for rc in c['recalls']:
            if rc['hp'] / rc['mhp'] < 0.7: continue
            r0 = rc['r']; n = 0
            for r in order:
                if r < r0: continue
                cc = [x for x in rounds[r]['champs'] if x[0] == i][0]
                if (cc[3], cc[4]) in sp and cc[9]: n += 1
                else: break
            stay[team].append(n)
        # gold left after each trip
        byr = collections.defaultdict(list)
        for b in c['buys']: byr[b['r']].append(b)
        for r, bl in byr.items(): left_after[team].append(min(b['after'] for b in bl))
        # dead shopping delay: rounds from death to purchase while dead
        for dr in c['deaths']:
            cand = [b['r'] - dr for b in c['buys'] if b['dead'] and dr <= b['r'] <= dr + 61]
            if cand: dead_shop_delay[team].append(min(cand))
print('action counts (team,kind):', sorted(kcount.items()))
print('k20/k23 position vs altar/spawn:', sorted(near_altar.items()))
print('consumables bought per champion-game:', sorted(per_cons.items()))
print('k20 uses vs consumables bought:', sorted(k20_after.items())[:30])
for team in ('mite', 'uni'):
    print(team, 'rounds on spawn after a recall arriving with hp>=70%: median', med(stay[team]), 'mean', mean(stay[team]), 'dist', sorted(collections.Counter(stay[team]).items())[:15])
    print(team, 'gold left right after a shopping turn: median', med(left_after[team]), 'share 0:', round(100 * sum(x == 0 for x in left_after[team]) / len(left_after[team])), '% share<30:', round(100 * sum(x < 30 for x in left_after[team]) / len(left_after[team])), '% dist', sorted(collections.Counter(left_after[team]).items())[:14])
    print(team, 'rounds from death to dead-shop:', med(dead_shop_delay[team]), sorted(collections.Counter(dead_shop_delay[team]).items())[:10])

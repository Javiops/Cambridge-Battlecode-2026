r"""shop13.py DECDIR [DECDIR...] [--index index.json] [--r0 30] [--r1 150]
Per team role (us = the bot of the batch, rival = the other side) and per champion type, from shop13dec.py files:
damage to camps per hit, hits per hitter-round, hitter-rounds / bodies / rounds per gold-group capture, hp / max hp /
strength / focus at rounds, purchases by round (shard buys detected from the per-round item counts), same-camp hitters.
The side of the bot comes from the index (side a = team 0); a game missing from the index is skipped. Without --index
(local h2h.sh replays decoded with shop13dec.py) the side is the file suffix: _a = team 0, _b = team 1.
"""
import sys, os, json, gzip, collections, statistics as st
TYPES = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HoR']
FAM = ['monster', 'power', 'durab', 'treasure', 'jungle', 'home', 'bruiser', 'tribute', 'capture', 'prospector', 'hunter', 'skirmish', 'greed', 'collectors']
STAT = 'sfh'
def iname(i): return f"{FAM[i // 6]}-{STAT[(i % 6) // 2]}"
args = sys.argv[1:]; dirs = []; index = None; R0, R1 = 30, 150
i = 0
while i < len(args):
    if args[i] == '--index': index = args[i + 1]; i += 2
    elif args[i] == '--r0': R0 = int(args[i + 1]); i += 2
    elif args[i] == '--r1': R1 = int(args[i + 1]); i += 2
    else: dirs.append(args[i]); i += 1
side = {}
if index:
    for x in json.load(open(index)): side[x['file']] = 0 if x['side'] == 'a' else 1
WIN = [(30, 60), (60, 100), (100, 150), (150, 300), (300, 600)]
A = collections.defaultdict(lambda: collections.defaultdict(float))     # (role, type) -> metric sums
G = collections.defaultdict(lambda: collections.defaultdict(float))     # role -> team metrics
PUR = collections.defaultdict(list)       # (role, type) -> list of per-champion purchase sequences [(round, gold_before, item, n)]
STATR = collections.defaultdict(list)     # (role, type, round) -> (hp, mhp, str, foc, gold)
CAPS = collections.defaultdict(list)      # role -> per gold capture (hitter_rounds, bodies, phase, hp_group, gold)
SAME = collections.defaultdict(collections.Counter)  # role -> hitters on the most-hit camp per round (rounds with >=1 hitter)
HIT_N = collections.defaultdict(collections.Counter)  # role -> number of hitters per round
ngames = collections.Counter()
for d in dirs:
    bot = os.path.basename(d.rstrip('/'))
    for fn in sorted(os.listdir(d)):
        key = f"{bot}/{fn.replace('.json.gz', '.repl26a')}"
        if index and key not in side: continue
        us = side[key] if index else (1 if fn.endswith('_b.json.gz') else 0)  # local h2h.sh: _a = bot is team 0, _b = team 1
        D = json.load(gzip.open(os.path.join(d, fn)))
        rounds = {r['r']: r for r in D['rounds']}
        if not rounds: continue
        ngames[bot] += 1
        ch = {c[0]: (c[1], c[2]) for c in D['rounds'][0]['c']}
        role = lambda team: 'us' if team == us else 'rival'
        camp = {k[0]: k for k in D['camps']}
        gold_of = {}; hp_of = collections.Counter()
        for k in D['camps']: gold_of[k[2]] = k[6]; hp_of[k[2]] += k[7]
        # hits
        hr = collections.defaultdict(set)   # (champ) -> rounds with a hit (window)
        per_round = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))  # r -> team -> camp -> hitters set size
        hits_by_g = collections.defaultdict(list)   # (team, group) -> [(r, actor)]
        for r, a, k, dmg, kind in D['ck']:
            if a not in ch or k not in camp: continue
            team, typ = ch[a]; g = camp[k][2]
            hits_by_g[(team, g)].append((r, a))
            if R0 <= r <= R1:
                key2 = (role(team), TYPES[typ])
                A[key2]['hits'] += 1; A[key2]['dmg'] += dmg; A[key2]['k' + str(kind)] += 1
                hr[a].add(r)
                per_round[r][team][k] = per_round[r][team][k] | {a} if isinstance(per_round[r][team][k], set) else {a}
        for a, rs in hr.items():
            team, typ = ch[a]; A[(role(team), TYPES[typ])]['hrounds'] += len(rs)
        for r in range(R0, R1 + 1):
            for team in (0, 1):
                camps_hit = per_round.get(r, {}).get(team, {})
                hitters = set().union(*camps_hit.values()) if camps_hit else set()
                HIT_N[role(team)][len(hitters)] += 1
                if hitters: SAME[role(team)][max(len(v) for v in camps_hit.values())] += 1
        # gold captures
        last_cap = collections.defaultdict(int)
        for g, team, r in sorted(D['caps'], key=lambda x: x[2]):
            if team not in (0, 1): continue
            if gold_of.get(g, 0) >= 20 and R0 <= r <= R1:
                hs = [(rr, a) for rr, a in hits_by_g[(team, g)] if last_cap[g] < rr <= r]
                hrs = len(set(hs)); bodies = len({a for _, a in hs}); first = min((rr for rr, _ in hs), default=r)
                # group dead = first round its state is 2 after first hit
                dead = r
                for rr in range(first, r + 1):
                    if rounds.get(rr, {}).get('gs', {}).get(str(g)) == 2: dead = rr; break
                CAPS[role(team)].append((hrs, bodies, dead - first, hp_of[g], gold_of[g], r - first))
            last_cap[g] = r
        # per-round champion stats and purchases
        prev = {}
        for rr in D['rounds']:
            r = rr['r']
            for c in rr['c']:
                idx, team, typ = c[0], c[1], c[2]
                if r in (30, 60, 100, 150, 300, 600): STATR[(role(team), TYPES[typ], r)].append((c[5], c[6], c[10], c[11], c[8], c[9]))
                if idx in prev:
                    p = prev[idx]; pi = p[12]; ci = c[12]
                    for i in range(84):
                        if i % 2: continue
                        ds = ci.get(str(i), 0) - pi.get(str(i), 0); de = ci.get(str(i + 1), 0) - pi.get(str(i + 1), 0)
                        n = ds + 5 * de
                        if n > 0: PUR[(role(team), TYPES[typ])].append((idx, r, p[8], iname(i), n, bot, fn))
                prev[idx] = c
        for team in (0, 1):
            G[role(team)]['games'] += 1
def mean(v): return sum(v) / len(v) if v else float('nan')
print(f"games per batch: {dict(ngames)}; window r{R0}-{R1}; roles: us = the batch's bot side, rival = the other side")
print("\n## Per champion type: damage to camps per hit, hits per hitter-round, hitter-rounds per game (window)")
print("| role | type | hits/game | dmg/hit | hits/hitter-round | hitter-rounds/game | ability hits % |")
print("|---|---|---|---|---|---|---|")
ng = {role: G[role]['games'] for role in ('rival', 'us')}
for typ in TYPES:
    for role in ('rival', 'us'):
        a = A.get((role, typ))
        if not a or a['hits'] < 50: continue
        # champion-games of this type: count from STATR at r30
        cg = len(STATR.get((role, typ, 30), [])) or 1
        print(f"| {role} | {typ} | {a['hits']/cg:.1f} | {a['dmg']/a['hits']:.1f} | {a['hits']/max(a['hrounds'],1):.2f} | {a['hrounds']/cg:.1f} | {100*a.get('k6',0)/a['hits']:.0f} |")
print("\n## Gold-group captures (gold>=20) inside the window, per team role")
print("| role | captures/game | hitter-rounds/capture | bodies/capture | hitting phase (first hit -> group dead) | first hit -> capture | group hp | gold |")
print("|---|---|---|---|---|---|---|---|")
for role in ('rival', 'us'):
    v = CAPS[role]
    if not v: continue
    print(f"| {role} | {len(v)/ng[role]:.2f} | {mean([x[0] for x in v]):.1f} | {mean([x[1] for x in v]):.2f} | {mean([x[2] for x in v]):.1f} / med {st.median([x[2] for x in v]):.0f} | {mean([x[5] for x in v]):.1f} | {mean([x[3] for x in v]):.0f} | {mean([x[4] for x in v]):.0f} |")
print("\n## Hitters per round (window), share of rounds; same-camp = hitters on the most-hit camp in rounds with >=1 hitter")
for role in ('rival', 'us'):
    tot = sum(HIT_N[role].values()); ts = sum(SAME[role].values())
    print(f"- {role}: hitters 0/1/2/3/4/5: " + ' / '.join(f"{100*HIT_N[role][k]/tot:.1f}" for k in range(6)) + f"%; same camp 1/2/3/4/5: " + ' / '.join(f"{100*SAME[role][k]/ts:.1f}" for k in range(1, 6)) + f"%; mean same-camp {sum(k*v for k,v in SAME[role].items())/ts:.2f}")
print("\n## Champion stats by round (alive champions), mean hp / max hp / strength / focus / gold")
print("| role | type | r30 | r60 | r100 | r150 | r300 | r600 |")
print("|---|---|---|---|---|---|---|---|")
for typ in TYPES:
    for role in ('rival', 'us'):
        if not STATR.get((role, typ, 30)): continue
        cells = []
        for r in (30, 60, 100, 150, 300, 600):
            v = [x for x in STATR.get((role, typ, r), []) if x[5]]
            cells.append(f"{mean([x[0] for x in v]):.0f}/{mean([x[1] for x in v]):.0f}/{mean([x[2] for x in v]):.0f}/{mean([x[3] for x in v]):.0f}/{mean([x[4] for x in v]):.0f}" if v else '-')
        print(f"| {role} | {typ} (n={len(STATR[(role, typ, 30)])}) | " + ' | '.join(cells) + ' |')
print("\n## Purchases (shards; an emblem counts as its 5th shard) per champion-game by round window, by family-stat")
for typ in TYPES:
    for role in ('rival', 'us'):
        P = PUR.get((role, typ))
        if not P: continue
        cg = len(STATR.get((role, typ, 30), [])) or 1
        print(f"\n### {role} {typ} (champion-games {cg}, shards bought <=600: {sum(x[4] for x in P)/cg:.1f} per champion-game, gold at purchase mean {mean([x[2] for x in P]):.0f})")
        for w0, w1 in [(0, 30)] + WIN:
            c = collections.Counter()
            for x in P:
                if w0 < x[1] <= w1: c[x[3]] += x[4]
            tot = sum(c.values())
            print(f"- r{w0}-{w1}: {tot/cg:.1f} shards/champion-game: " + ', '.join(f"{k} {v/cg:.1f}" for k, v in c.most_common(8)))
        # order: the k-th shard-buy event per champion (by idx within game)
        seq = collections.defaultdict(list)
        for x in sorted(P, key=lambda x: (x[5], x[6], x[0], x[1])): seq[(x[5], x[6], x[0])].append(x)
        print("- order of the first 8 purchase events (most common item at each position, share; median round; mean gold before):")
        for k in range(8):
            ev = [s[k] for s in seq.values() if len(s) > k]
            if len(ev) < 5: break
            c = collections.Counter(e[3] for e in ev)
            top = c.most_common(3)
            print(f"  - #{k+1} (n={len(ev)}): " + ', '.join(f"{a} {100*b/len(ev):.0f}%" for a, b in top) + f"; round med {st.median([e[1] for e in ev]):.0f}; gold {mean([e[2] for e in ev]):.0f}; shards in event {mean([e[4] for e in ev]):.1f}")

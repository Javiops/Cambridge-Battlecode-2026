r"""shop13plan.py DECDIR... --index index.json : the rival side's purchase sequence per champion type, as a plan.
For each champion type: modal item at purchase events #1..#8 (events = rounds with a shard buy of that champion; an emblem
counts as 5 shards), median round and gold-before percentiles (p25/p50/p75) per event, shards per family-stat by window,
and the derived v13 plan: the modal items in order of first appearance (deduplicated), then the r300-600 top items as fill.
"""
import sys, os, json, gzip, collections, statistics as st
TYPES = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HoR']
FAM = ['monster', 'power', 'durab', 'treasure', 'jungle', 'home', 'bruiser', 'tribute', 'capture', 'prospector', 'hunter', 'skirmish', 'greed', 'collectors']
def iname(i): return f"{FAM[i // 6]}-{'sfh'[(i % 6) // 2]}"
args = sys.argv[1:]; dirs = [a for a in args if not a.startswith('--') and not a.endswith('.json')]
index = args[args.index('--index') + 1]
side = {x['file']: 0 if x['side'] == 'a' else 1 for x in json.load(open(index))}
SEQ = collections.defaultdict(list)   # type -> list of per-champion sequences [(r, gold_before, item, n)]
WINS = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
CG = collections.Counter()
for d in dirs:
    bot = os.path.basename(d.rstrip('/'))
    for fn in sorted(os.listdir(d)):
        key = f"{bot}/{fn.replace('.json.gz', '.repl26a')}"
        if key not in side: continue
        us = side[key]
        D = json.load(gzip.open(os.path.join(d, fn)))
        prev = {}; seq = collections.defaultdict(list)
        for rr in D['rounds']:
            r = rr['r']
            for c in rr['c']:
                idx, team, typ = c[0], c[1], c[2]
                if team == us: continue
                if r == 30: CG[TYPES[typ]] += 1
                if idx in prev:
                    p = prev[idx]; pi = p[12]; ci = c[12]; bought = []
                    for i in range(0, 84, 2):
                        n = ci.get(str(i), 0) - pi.get(str(i), 0) + 5 * (ci.get(str(i + 1), 0) - pi.get(str(i + 1), 0))
                        if n > 0: bought.append((iname(i), n))
                    for it, n in bought:
                        seq[idx].append((r, p[8], it, n))
                        for w0, w1 in [(0, 30), (30, 60), (60, 100), (100, 150), (150, 300), (300, 600)]:
                            if w0 < r <= w1: WINS[TYPES[typ]][(w0, w1)][it] += n
                prev[idx] = c
        for idx, s in seq.items(): SEQ[TYPES[prev[idx][2]]].append(s)
def pct(v, q): v = sorted(v); return v[min(len(v) - 1, int(q * len(v)))] if v else float('nan')
plans = {}
for typ in ['Vesper', 'Marcella', 'Ryth', 'Vendetta', 'HoR', 'Ren']:
    S = SEQ.get(typ, []); cg = CG[typ]
    if not S: continue
    print(f"\n## rival {typ}: champion-games {cg}, with purchases {len(S)}, shards/champion-game <=600: {sum(x[3] for s in S for x in s)/cg:.1f}")
    print("| event | n | modal items (share) | round med | gold before p25/p50/p75 | shards |")
    print("|---|---|---|---|---|---|")
    order = []
    for k in range(10):
        ev = [s[k] for s in S if len(s) > k]
        if len(ev) < 8: break
        c = collections.Counter(e[2] for e in ev)
        print(f"| #{k+1} | {len(ev)} | " + ', '.join(f"{a} {100*b/len(ev):.0f}%" for a, b in c.most_common(4)) + f" | {st.median([e[0] for e in ev]):.0f} | {pct([e[1] for e in ev], .25):.0f}/{pct([e[1] for e in ev], .5):.0f}/{pct([e[1] for e in ev], .75):.0f} | {sum(e[3] for e in ev)/len(ev):.1f} |")
        if c.most_common(1)[0][0] not in order: order.append(c.most_common(1)[0][0])
    print("windows (shards per champion-game): " + '; '.join(f"r{w0}-{w1}: " + ', '.join(f"{k} {v/cg:.1f}" for k, v in WINS[typ][(w0, w1)].most_common(5)) for (w0, w1) in [(30, 60), (60, 100), (100, 150), (150, 300), (300, 600)]))
    # gold thresholds: purchases before r300 and from r300
    g_early = [x[1] for s in S for x in s if x[0] < 300]; g_late = [x[1] for s in S for x in s if x[0] >= 300]
    first = [s[0] for s in S]
    print(f"gold before purchase: first event p25/p50 {pct([e[1] for e in first], .25):.0f}/{pct([e[1] for e in first], .5):.0f}; r<300 p25/p50 {pct(g_early, .25):.0f}/{pct(g_early, .5):.0f}; r>=300 p25/p50 {pct(g_late, .25):.0f}/{pct(g_late, .5):.0f}")
    late = WINS[typ][(300, 600)].most_common(3)
    plans[typ] = {'order': order, 'late': [(k, v / cg) for k, v in late], 'gold_p25_first': pct([e[1] for e in first], .25), 'gold_p25_early': pct(g_early, .25)}
    print(f"v13 plan: {order} then fill {late}")
print(json.dumps(plans, indent=1))

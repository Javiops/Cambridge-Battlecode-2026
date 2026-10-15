import sys, json, collections, statistics as st
# usage: python3 -I analyze_shop.py $S  -> shop tables per team / champion type
S = sys.argv[1]
d = json.load(open(f'{S}/reports/scripts_draft/shop.json'))
def med(v): return round(st.median(v), 1) if v else None
def mean(v): return round(st.mean(v), 1) if v else None

for team in ('mite', 'uni'):
    print('=' * 20, team)
    games = [g for g in d if g['team'] == team]
    byty = collections.defaultdict(list)
    for g in games:
        for i, c in g['champs'].items():
            byty[c['ty']].append((g, c))
    print(f"{'type':8s} n  items(family_stat shards: games)                        emblems/g  firstbuy  buys/g  trips/g gap   dead% spawn% field%  earned spent end  unsp%  after0%  cons")
    for ty, lst in sorted(byty.items(), key=lambda x: -len(x[1])):
        n = len(lst)
        comp = collections.Counter(); emb = 0; first = []; nb = []; trips = []; gaps = []; dead = spawn = field = 0; earned = spent = end = 0
        after = []; cons = collections.Counter(); batch = []
        for g, c in lst:
            for k, v in c.get('items', {}).items():
                fam, kind, _, stat = k.split('_')
                if kind == 'shard': comp[f'{fam}_{stat}'] += 1  # count games where bought
                else: emb += v
            if c['buys']:
                first.append(c['buys'][0]['r'])
                rs = sorted(set(b['r'] for b in c['buys']))
                trips.append(len(rs)); gaps += [b - a for a, b in zip(rs, rs[1:])]
                # gold left after the last purchase of each trip
                lastb = {}
                for b in c['buys']: lastb[b['r']] = b
                after += [b['after'] for b in lastb.values()]
                batch += [sum(b['gold'] for b in c['buys'] if b['r'] == r) for r in rs]
            nb.append(len(c['buys']))
            for b in c['buys']:
                if b['dead']: dead += 1
                elif b['onspawn']: spawn += 1
                else: field += 1
            earned += c.get('earnedGold', 0); spent += c.get('spentGold', 0); end += c.get('goldEnd', 0)
            for k, v in enumerate(c.get('consumables', [])): cons[k] += v
        tot = dead + spawn + field or 1
        comps = ', '.join(f'{k}:{v}' for k, v in comp.most_common(6))
        print(f"{ty:8s} {n:2d} {comps:55s} {emb/n:5.2f}    {med(first)!s:6s}   {mean(nb)!s:5s}  {mean(trips)!s:5s} {med(gaps)!s:5s} {100*dead/tot:4.0f}% {100*spawn/tot:4.0f}% {100*field/tot:4.0f}%   {earned/n:5.0f} {spent/n:5.0f} {end/n:4.0f} {100*end/max(earned,1):4.0f}%  {100*sum(a==0 for a in after)/max(len(after),1):4.0f}%  {dict(cons)}")
    # batch size distribution per trip
    allb = collections.Counter()
    for g in games:
        for c in g['champs'].values():
            rs = collections.defaultdict(int)
            for b in c['buys']: rs[b['r']] += b['gold']
            for v in rs.values(): allb[v] += 1
    print('gold spent per shopping turn:', sorted(allb.items()))
    # buy-order: first family bought per type (by round) and sequence of families
    print('-- family order per type (first 3 distinct shard families bought, by purchase order in summary cannot be known; use maxhp signal: health shards show maxhp)')
    seqs = collections.defaultdict(collections.Counter)
    for g in games:
        for c in g['champs'].values():
            s = ''.join('H' if b['maxhp'] > 0 else 'x' for b in c['buys'])
            seqs[c['ty']][s] += 1
    for ty, cnt in seqs.items(): print(f'   {ty:8s}', cnt.most_common(5))

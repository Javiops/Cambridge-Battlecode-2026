# Per-map tables: top-10 vs top-10 games (deduped) vs our games on the same maps.
import collections, statistics as st, sys, json
import load
med = lambda xs: st.median(xs) if xs else float('nan')
def dedupe(rs):
    seen = set(); out = []
    for r in rs:
        k = (r['map'], r['team'], r['opp'], r['side'], r['gems'], r['ogems'], r['rounds'])
        if k in seen: continue
        seen.add(k); out.append(r)
    return out
T = dedupe(load.top_rows()); O = load.our_rows()
maps = sys.argv[1:] or load.NEW
def line(rs, tag):
    if not rs: return f'  {tag}: none'
    w = [r for r in rs if r['win']]
    return (f"  {tag}: n={len(rs)} win {len(w)/len(rs):.0%} | rounds {med([r['rounds'] for r in rs]):.0f} | gems {med([r['gems'] for r in rs]):.0f}"
            f" vs {med([r['ogems'] for r in rs]):.0f} | kills {st.mean(r['kills'] for r in rs):.1f} deaths {st.mean(r['deaths'] for r in rs):.1f}"
            f" | gold earned {med([r['gold'] for r in rs]):.0f} (opp {med([r['ogold'] for r in rs]):.0f}) | collected {med([r['collected'] for r in rs]):.0f}"
            f" | monster dmg {med([r['mdmg'] for r in rs])/1000:.0f}k champ dmg {med([r['cdmg'] for r in rs])/1000:.1f}k")
for mp in maps:
    t = [r for r in T if r['map'] == mp]; o = [r for r in O if r['map'] == mp]
    print(f'=== {mp}: top-10 vs top-10 games {len(t)//2 if t else 0} (team-rows {len(t)})')
    print(line([r for r in t if r['win']], 'top winners'))
    print(line([r for r in t if not r['win']], 'top losers '))
    print(line(o, 'us (all opp)'))
    ot = [r for r in o if r['opp'] in {x['team'] for x in t}]
    print(line(ot, 'us vs top-10'))
    # end condition: 1000 gems reached or round limit
    fin = collections.Counter('1000' if max(r['gems'], r['ogems']) >= 1000 else 'r2000' for r in t if r['win'])
    print('  how top games end:', dict(fin), '| our wins/losses end:', dict(collections.Counter(('W' if r['win'] else 'L') + ('1000' if max(r['gems'], r['ogems']) >= 1000 else 'r' + str(r['rounds'])) [:5] for r in o)))
    # teams
    byteam = collections.defaultdict(list)
    for r in t: byteam[r['team']].append(r)
    print('  team W-L, most common draft, kills/deaths per game:')
    for tm, rs in sorted(byteam.items(), key=lambda kv: -sum(r['win'] for r in kv[1]) / len(kv[1])):
        dc = collections.Counter(tuple(r['draft']) for r in rs).most_common(2)
        print(f"    {tm[:22]:22s} {sum(r['win'] for r in rs):3d}-{sum(not r['win'] for r in rs):<3d} {dc}  k {st.mean(r['kills'] for r in rs):.1f} d {st.mean(r['deaths'] for r in rs):.1f}")
    print('  our drafts:', collections.Counter(tuple(r['draft']) for r in o).most_common(3))
    # items by winners: share of champions buying each item family
    def items(rs):
        c = collections.Counter(); n = 0
        for r in rs:
            for ch in r['champs']:
                n += 1
                for it, k in ch['items'].items(): c[it] += k
        return {k: round(v / max(n, 1), 2) for k, v in c.most_common(8)}
    print('  items per champion, top winners:', items([r for r in t if r['win']]))
    print('  items per champion, us         :', items(o))
    print()

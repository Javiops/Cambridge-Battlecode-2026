import json, glob, collections, statistics as S, sys
from evaluator import evaluate
# Mite/uni captures per group per game from groupset.json keyed by features; recompute directly by group tiles instead
from legs import team_of
from geo import Geo
def caps_by_tile(team):
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in glob.glob('compact/*.json'):
        d = json.load(open(f)); G = {int(k): v for k, v in d['groups'].items()}
        for s in d['sel']:
            if s['team'] != team: continue
            t = team_of(d, s); last = {}; c = collections.Counter()
            for r, gid, st, ct in d['gev']:
                if st == 'reward_available': last[gid] = ct
                if st == 'respawning' and last.get(gid) == t: c[gid] += 1
            for gid, v in G.items():
                key = tuple(sorted(map(tuple, v['tiles'])))
                # normalise to side A view: if we are side b, the same group is the mirror -> store under our-side key via flag
                out[s['map']][(key, s['side'])].append(c[gid])
    return out
def main(team='mite', K=150):
    C = caps_by_tile(team)
    tot = collections.Counter()
    for p in sorted(glob.glob('mapsj/*.json')):
        name = p.split('/')[-1][:-5]; res, rows = evaluate(p)
        m = json.load(open(p))
        from evaluator import full_groups
        G = full_groups(m)
        print(f'== {name} d={res["d"]}')
        for r in sorted(rows, key=lambda r: r['dO']):
            gr = G[r['k']]; key = tuple(sorted(map(tuple, gr['tiles'])))
            obs = C[name].get((key, 'a'))
            if obs is None: continue
            hp = sum({'WOLF':1350,'ELK':2400,'GEM_CLUSTER':500,'GOLD_CLUSTER':500,'MONOLITH':20000}[t] for t in gr['types'])
            if r['gems'] <= 0 or r['monolith']: worth = 0
            else:
                bank = min(r['walk'], r['rec'])
                worth = r['gems'] / (r['dO'] + hp / K + 5 + bank)
            own = r['dO'] < r['dE']
            mc = S.mean(obs)
            pred = own and worth >= 0.5
            got = mc >= 1.0
            tot[(pred, got)] += 1
            print(f"   {gr['types'][0][:5]:6} gems {r['gems']:4} dO {r['dO']:3} dE {r['dE']:3} bank {min(r['walk'], r['rec']):3} worth {worth:5.2f} own {int(own)}  {team} caps/game {mc:5.2f}  {'OK' if pred == got else 'MISS'}")
    n = sum(tot.values()); print('accuracy', (tot[(True, True)] + tot[(False, False)]) / n, dict(tot))
main(*(sys.argv[1:2] or ['mite']))

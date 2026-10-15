"""Per-map strategy from map features only, compared with what Mite (the #1) does."""
import json, glob, collections, statistics as S, itertools, sys
from evaluator import evaluate, full_groups
STR = {'WOLF': 20, 'ELK': 60, 'GEM_CLUSTER': 0, 'GOLD_CLUSTER': 0, 'MONOLITH': 200}
HPT = {'WOLF': 1350, 'ELK': 2400, 'GEM_CLUSTER': 500, 'GOLD_CLUSTER': 500, 'MONOLITH': 20000}
MAPS = {}
for p in sorted(glob.glob('mapsj/*.json')):
    name = p.split('/')[-1][:-5]; res, rows = evaluate(p); m = json.load(open(p)); G = full_groups(m)
    for r in rows:
        gr = G[r['k']]; r['key'] = json.dumps(sorted([list(t) for t in gr['tiles']])).replace(' ', '')
        r['hp'] = sum(HPT[t] for t in gr['types']); r['str'] = sum(STR[t] for t in gr['types'])
    MAPS[name] = (res, rows)
CAPS = json.load(open('mite_caps.json'))
def label(name):
    out = {}
    for k, v in CAPS[name].items():
        kk = json.dumps(sorted([list(t) for t in json.loads(k)])).replace(' ', '')
        out[kk] = S.mean(v)
    return out
def farm_set(res, rows, K=150, theta=0.5, side0=0, near_alt=2, side1=4, dmgw=1.0):
    pick = set()
    for r in rows:
        if r['gems'] <= 0 or r['monolith']: continue
        kill = r['hp'] / K
        bank = min(r['walk'], r['rec'])
        dmg = r['str'] * kill / 900.0 * (r['dO'] + 5) * dmgw      # hp lost -> share of a trip home to heal
        worth = r['gems'] / (r['dO'] + kill + 5 + bank + dmg)
        side = r['side']
        ok = side <= side0 or (bank <= near_alt and side <= side1)
        if ok and worth >= theta: pick.add(r['key'])
    return pick
def score(params, verbose=False):
    exact = 0; good = 0; tot = 0; per = {}
    for name, (res, rows) in MAPS.items():
        lab = label(name); P = farm_set(res, rows, **params)
        truth = {k for k, v in lab.items() if v >= 1.5}
        keys = [r['key'] for r in rows if r['key'] in lab]
        wrong = [k for k in keys if (k in P) != (k in truth)]
        per[name] = (len(keys) - len(wrong), len(keys), wrong)
        exact += not wrong; good += len(keys) - len(wrong); tot += len(keys)
    return exact, good / tot, per
if __name__ == '__main__':
    best = None
    grid = dict(K=[100, 150, 200, 300], theta=[0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6], side0=[-4, -2, 0, 2, 4], near_alt=[0, 2, 3], side1=[2, 4, 8], dmgw=[0, 0.5, 1, 2, 4])
    for vals in itertools.product(*grid.values()):
        p = dict(zip(grid.keys(), vals)); e, a, _ = score(p)
        if best is None or (e, a) > best[0]: best = ((e, a), p)
    print('best', best)
    e, a, per = score(best[1])
    for n, v in per.items(): print(n, v[0], '/', v[1], 'misses', len(v[2]))

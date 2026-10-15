"""Greedy cycle-set builder: camps join the farm set by worth, where travel = distance from home or from a camp already in the set."""
import json, glob, collections, statistics as S, itertools, sys
from evaluator import evaluate, full_groups, mirror
from geo import Geo
from strategy import MAPS, label, STR
EXTRA = {}
for name, (res, rows) in MAPS.items():
    m = json.load(open(f'mapsj/{name}.json')); g = Geo(m); G = full_groups(m)
    x0, y0, x1, y1 = m['spawnA']; spA = [(x, y) for x in range(x0, x1) for y in range(y0, y1) if not g.block[y][x]]
    spB = [mirror(m, x, y) for x, y in spA]; dA, dB = g.bfs(spA), g.bfs(spB)
    # pairwise camp distances
    idx = {r['k']: i for i, r in enumerate(rows)}
    D = {}
    for r in rows:
        F = g.d_to_group(G[r['k']]['tiles'])
        D[r['k']] = {q['k']: min(F[y][x] for x, y in G[q['k']]['tiles']) for q in rows}
    # contested altar: altar with the smallest |dA-dB|, distance from each camp to it
    best = None
    for a in g.altars:
        nb = g.near([a], 1)
        da = min(dA[y][x] for x, y in nb); db = min(dB[y][x] for x, y in nb)
        if best is None or (abs(da - db), da) < best[0]: best = ((abs(da - db), da), a, nb)
    FA = g.bfs(best[2])
    for r in rows: r['dC'] = min(FA[y][x] for x, y in G[r['k']]['tiles'])
    EXTRA[name] = dict(D=D, cont=best[0])
def farm_set(name, bw=1.0, aF=None, rel=0.0, maxbank=99, dmgwF=None, K=100, theta=0.4, thetaF=None, a=1.0, side0=0, near_alt=2, side1=2, dmgw=0.5, anchor_fight=1, fightd=45):
    res, rows = MAPS[name]; D = EXTRA[name]['D']
    fight = res['d'] <= fightd
    cand = [r for r in rows if r['gems'] > 0 and not r['monolith'] and (r['side'] <= side0 or (min(r['walk'], r['rec']) <= near_alt and r['side'] <= side1))]
    chosen = []
    top = [0.0]
    def worth(r):
        home = r['dO']
        if fight and anchor_fight == 1: home = min(home, r['dC'])
        if fight and anchor_fight == 2: home = r['dC']
        if fight and anchor_fight == 4: home = max(0, r['dO'] + r['dC'] - EXTRA[name]['cont'][1])
        if fight and anchor_fight == 5: home = min(r['dC'], max(0, r['dO'] + r['dC'] - EXTRA[name]['cont'][1]))
        if fight and anchor_fight == 3: home = (r['dO'] + r['dC']) / 2
        hop = home
        for c in chosen: hop = min(hop, D[c['k']][r['k']])
        aa = aF if (fight and aF is not None) else a
        hop = aa * home + (1 - aa) * hop
        kill = r['hp'] / K; bank0 = min(r['walk'], r['rec']); bank = bw * bank0
        dmg = r['str'] * kill / 900.0 * (r['dO'] + 5) * (dmgwF if (fight and dmgwF is not None) else dmgw)
        if bank0 > maxbank: return 0
        return r['gems'] / (hop + kill + 5 + bank + dmg)
    while True:
        rest = [r for r in cand if r not in chosen]
        if not rest: break
        b = max(rest, key=worth)
        wb = worth(b)
        if len(chosen) < res['nch']: top[0] = wb
        if wb < max(rel * top[0], (thetaF if (fight and thetaF is not None) else theta)): break
        chosen.append(b)
    return {r['key'] for r in chosen}, chosen
def score(params):
    exact = 0; good = 0; tot = 0; per = {}
    for name, (res, rows) in MAPS.items():
        lab = label(name); P, _ = farm_set(name, **params)
        truth = {k for k, v in lab.items() if v >= 1.5}
        keys = [r['key'] for r in rows if r['key'] in lab]
        wrong = [k for k in keys if (k in P) != (k in truth)]
        per[name] = (len(keys) - len(wrong), len(keys)); exact += not wrong; good += len(keys) - len(wrong); tot += len(keys)
    return exact, good / tot, per
if __name__ == '__main__':
    grid = dict(K=[100, 150], theta=[0.3, 0.35, 0.4, 0.45, 0.5], thetaF=[0.4, 0.45, 0.5, 0.55, 0.6, 0.7], a=[0.5, 0.7, 1.0], side0=[0], near_alt=[2], side1=[2], dmgw=[0, 0.5, 1], anchor_fight=[0, 1])
    best = None
    for vals in itertools.product(*grid.values()):
        p = dict(zip(grid.keys(), vals)); e, a, per = score(p)
        if best is None or (e, a) > best[0]: best = ((e, a), p, per)
    print(best)

def score_core(params, hi=3.0, lo=1.0):
    """map correct when every camp Mite takes >= hi times a game is in the set and no camp in the set is taken < lo times"""
    exact = 0; per = {}
    for name, (res, rows) in MAPS.items():
        lab = label(name); P, _ = farm_set(name, **params)
        miss = [k for k, v in lab.items() if v >= hi and k not in P]
        extra = [k for k in P if k in lab and lab[k] < lo]
        per[name] = (len(miss), len(extra)); exact += not miss and not extra
    return exact, per

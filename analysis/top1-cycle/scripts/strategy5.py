"""Camp set = greedy by worth, cut relative to the map's own best camps.
worth = gems / (travel + kill + 5 + bank + damage taken), damage = str * kill * (dO+5) / 900 * dmgw.
Stop when worth < rho * median(worth of the nch best camps); rho differs for fight maps (champions also fight)
and farm maps."""
import json, statistics as S, itertools
from collections import Counter
from strategy2 import MAPS, EXTRA, label
def farm_set(name, K=150, bw=1.0, dmgw=2.5, a=0.5, aF=0.7, side_farm=0.1, side_fight=2, maxbank=20,
             rho_fight=0.55, rho_farm=0.3, fightd=45, with_worth=False, theta=0.0):
    res, rows = MAPS[name]; D = EXTRA[name]['D']; d = res['d']; fight = d <= fightd; dHC = EXTRA[name]['cont'][1]
    cand = [r for r in rows if r['gems'] > 0 and not r['monolith'] and min(r['walk'], r['rec']) <= maxbank
            and r['side'] <= (side_fight if fight else -side_farm * d)]
    chosen = []
    def worth(r):
        home = max(0, r['dO'] + r['dC'] - dHC) if fight else r['dO']
        hop = min([home] + [D[c['k']][r['k']] for c in chosen])
        aa = aF if fight else a
        travel = aa * home + (1 - aa) * hop
        kill = r['hp'] / K; bank = bw * min(r['walk'], r['rec'])
        dmg = r['str'] * kill / 900.0 * (r['dO'] + 5) * dmgw
        return r['gems'] / (travel + kill + 5 + bank + dmg)
    w0 = sorted((worth(r) for r in cand), reverse=True)
    ref = S.median(w0[:res['nch']]) if w0 else 0
    cut = max(theta, (rho_fight if fight else rho_farm) * ref)
    ws = []
    while True:
        rest = [r for r in cand if r not in chosen]
        if not rest: break
        b = max(rest, key=worth); w = worth(b)
        if w < cut: break
        chosen.append(b); ws.append(w)
    out = {r['key'] for r in chosen}
    return (out, list(zip(chosen, ws)), cut) if with_worth else out
def evaluate_maps(params, hi=3.0, lo=1.0, maps=None):
    ok = 0; per = {}; good = tot = 0
    for name in (maps or MAPS):
        lab = label(name); P = farm_set(name, **params)
        miss = [k for k, v in lab.items() if v >= hi and k not in P]
        junk = [k for k in P if lab.get(k, 0) < lo]
        per[name] = (len(miss), len(junk)); ok += not miss and not junk
        truth = {k for k, v in lab.items() if v >= 1.5}
        good += sum((k in P) == (k in truth) for k in lab); tot += len(lab)
    return ok, good / tot, per
GRID = dict(K=[100, 150, 200], bw=[1, 1.5], dmgw=[1, 1.5, 2, 2.5, 3, 4], a=[0.5, 0.7, 1.0], aF=[0.7, 1.0],
            side_farm=[0, 0.1, 0.2], side_fight=[0, 2], maxbank=[20, 99],
            rho_fight=[0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7], rho_farm=[0.2, 0.25, 0.3, 0.35, 0.4, 0.5])
if __name__ == '__main__':
    res = []
    for vals in itertools.product(*GRID.values()):
        p = dict(zip(GRID.keys(), vals)); ok, acc, per = evaluate_maps(p); res.append((ok, acc, p, per))
    res.sort(key=lambda t: (t[0], t[1]), reverse=True)
    for r in res[:5]: print(r[0], round(r[1], 3), r[2], {k: v for k, v in r[3].items() if v != (0, 0)})
    print('ok histogram', sorted(Counter(r[0] for r in res).items()))
    nine = [r[2] for r in res if r[0] == 9]
    print('combos with 9/9:', len(nine), 'of', len(res))
    for k in GRID: print(' ', k, sorted(Counter(p[k] for p in nine).items()))
    json.dump(nine, open('nine5.json', 'w'))

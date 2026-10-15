"""Strategy card for any map, from map features only (rules fitted to Mite, the #1, on the 9 official maps).
usage: python3 card.py MAP.json [...]   (JSON from tools/mapjson.js)"""
import json, sys, statistics as S
from evaluator import evaluate, full_groups, mirror
from geo import Geo
import strategy, strategy2, strategy5
BEST = dict(K=150, bw=1, dmgw=3, a=0.5, aF=0.7, side_farm=0.1, side_fight=2, maxbank=99, rho_fight=0.55, rho_farm=0.25)
def load(path):
    name = path.split('/')[-1][:-5]
    if name in strategy.MAPS: return name
    res, rows = evaluate(path); m = json.load(open(path)); G = full_groups(m)
    for r in rows:
        gr = G[r['k']]; r['key'] = json.dumps(sorted([list(t) for t in gr['tiles']])).replace(' ', '')
        r['hp'] = sum(strategy.HPT[t] for t in gr['types']); r['str'] = sum(strategy.STR[t] for t in gr['types'])
    g = Geo(m); x0, y0, x1, y1 = m['spawnA']
    spA = [(x, y) for x in range(x0, x1) for y in range(y0, y1) if not g.block[y][x]]
    dA, dB = g.bfs(spA), g.bfs([mirror(m, x, y) for x, y in spA])
    D = {}
    for r in rows:
        F = g.d_to_group(G[r['k']]['tiles']); D[r['k']] = {q['k']: min(F[y][x] for x, y in G[q['k']]['tiles']) for q in rows}
    best = None
    for a in g.altars:
        nb = g.near([a], 1); da = min(dA[y][x] for x, y in nb); db = min(dB[y][x] for x, y in nb)
        if best is None or (abs(da - db), da) < best[0]: best = ((abs(da - db), da), a, nb)
    FA = g.bfs(best[2])
    for r in rows: r['dC'] = min(FA[y][x] for x, y in G[r['k']]['tiles'])
    strategy.MAPS[name] = (res, rows); strategy2.EXTRA[name] = dict(D=D, cont=best[0])
    return name
def draft(nch, sa):
    near = sa <= 8   # an altar next to home: recall banking, casters
    if nch == 3: return ['Ren', 'Stellar', 'Cassi'] if near else ['Varg', 'Ryth', 'Cassi']
    if nch == 4: return ['Varg', 'Ryth', 'Cassi', 'Ren']        # no near-altar 4-pick map seen yet
    return ['Varg', 'Stellar', 'Cassi', 'Tavi' if near else 'Ryth', 'Ren']
def card(name, p=BEST):
    res, rows = strategy.MAPS[name]; D = strategy2.EXTRA[name]['D']
    _, cw, cut = strategy5.farm_set(name, with_worth=True, **p)
    sa = res['sp2alt']
    camps = []
    for r, w in cw:
        bank = 'recall' if sa < r['walk'] else 'walk'      # = 5 + home->altar < walk + 5
        camps.append(dict(key=r['key'], k=r['k'], types=r['types'], gems=r['gems'], dO=r['dO'], walk=r['walk'], rec=r['rec'], worth=round(w, 2), bank=bank))
    # illustrative cycle: nearest-neighbour from home through the set (in game: nearest camp that is up)
    order, left, cur = [], [c['k'] for c in camps], None
    while left:
        nxt = min(left, key=lambda k: (next(c['dO'] for c in camps if c['k'] == k) if cur is None else D[cur][k]))
        order.append(nxt); left.remove(nxt); cur = nxt
    nrec = sum(c['bank'] == 'recall' for c in camps)
    return dict(map=name, w=res['w'], h=res['h'], nch=res['nch'], d=res['d'], mode='fight' if res['d'] <= 45 else 'farm',
                sp2alt=sa, draft=draft(res['nch'], sa), bank_mode='recall' if camps and nrec * 2 >= len(camps) else 'walk', recall_share=round(nrec / max(1, len(camps)), 2),
                n_set=len(camps), cut=round(cut, 2), camps=camps, cycle=order)
if __name__ == '__main__':
    for p in sys.argv[1:]:
        c = card(load(p))
        print(f"{c['map']:10} {c['w']}x{c['h']} nch{c['nch']} d{c['d']:3} {c['mode']:5} sa{c['sp2alt']:3} bank={c['bank_mode']:6} set={c['n_set']:2} draft={','.join(c['draft'])}")
        print('    ', ' '.join(f"{''.join(t[0] for t in x['types'])}@{x['dO']}:{x['bank'][0]}" for x in c['camps']))

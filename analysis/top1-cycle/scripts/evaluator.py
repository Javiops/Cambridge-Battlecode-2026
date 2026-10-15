"""Map evaluator: features computed only from the map (what the bot can see at game start)."""
import json, sys, statistics as S
from geo import Geo
def mirror(m, x, y):
    w, h = m['w'], m['h']
    return {'H': (w-1-x, y), 'V': (x, h-1-y), 'R180': (w-1-x, h-1-y)}[m['sym']]
def full_groups(m):
    out = []
    for gi, g in enumerate(m['groups']):
        tiles = [(m['camps'][c]['x'], m['camps'][c]['y']) for c in g['camps']]
        types = [m['camps'][c]['type'] for c in g['camps']]
        for mir in (False, True):
            t = [mirror(m, x, y) for x, y in tiles] if mir else tiles
            out.append(dict(tiles=t, types=types, gems=g['gems'], gold=g['gold'], respawn=g['respawn']))
    return out
HP = {'WOLF': 1350, 'ELK': 2400, 'GEM_CLUSTER': 500, 'GOLD_CLUSTER': 500, 'MONOLITH': 20000}   # rough, only the ranking matters
def evaluate(path):
    m = json.load(open(path)); g = Geo(m)
    x0, y0, x1, y1 = m['spawnA']
    spA = [(x, y) for x in range(x0, x1) for y in range(y0, y1) if not g.block[y][x]]
    spB = [mirror(m, x, y) for x, y in spA]
    dA, dB = g.bfs(spA), g.bfs(spB)
    d = min(dB[y][x] for x, y in spA)
    alt = g.altars; dAl = [g.d_to_altar(a) for a in alt]
    sp2alt = min(min(D[y][x] for x, y in spA) for D in dAl)
    G = full_groups(m)
    rows = []
    for k, gr in enumerate(G):
        x, y = gr['tiles'][0]
        if dA[y][x] >= 10**6: continue
        walk = min(D[y][x] for D in dAl)
        monolith = 'MONOLITH' in gr['types']
        rows.append(dict(k=k, gems=gr['gems'], gold=gr['gold'], types=gr['types'], dO=dA[y][x], dE=dB[y][x], walk=walk, rec=5 + sp2alt, monolith=monolith,
                         side=dA[y][x] - dB[y][x]))
    farm = [r for r in rows if r['gems'] > 0 and not r['monolith']]
    own = [r for r in farm if r['side'] < -d/6]
    mid = [r for r in farm if abs(r['side']) <= d/6]
    def hop(rs):
        hs = []
        for r in rs:
            D = g.d_to_group(G[r['k']]['tiles'])
            o = [D[G[q['k']]['tiles'][0][1]][G[q['k']]['tiles'][0][0]] for q in rs if q['k'] != r['k']]
            if o: hs.append(min(o))
        return S.median(hs) if hs else 0
    res = dict(map=path.split('/')[-1].replace('.json', ''), w=m['w'], h=m['h'], nch=m['nch'], d=d, altars=len(alt), sp2alt=sp2alt,
               n_own=len(own), n_mid=len(mid), gems_own=sum(r['gems'] for r in own), gems_mid=sum(r['gems'] for r in mid),
               bank_walk=S.median(r['walk'] for r in own) if own else 0, bank_rec=5 + sp2alt,
               rec_better=sum(1 for r in own if r['rec'] + 3 < r['walk']) / max(1, len(own)),
               hop=hop(own), own_near_spawn=S.median(r['dO'] for r in own) if own else 0,
               mid_altar=min([r['walk'] for r in mid] or [99]))
    return res, rows
if __name__ == '__main__':
    out = []
    for p in sys.argv[1:]:
        r, _ = evaluate(p); out.append(r)
    keys = list(out[0].keys())
    print(' '.join(f"{k[:9]:>9}" for k in keys))
    for r in out: print(' '.join(f"{(round(v,2) if isinstance(v,float) else v)!s:>9}"[:9].rjust(9) for v in r.values()))

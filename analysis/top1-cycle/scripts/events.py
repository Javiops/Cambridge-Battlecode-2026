import json, glob, math, collections
def load_map(name): return json.load(open(f'mapsj/{name}.json'))
def altars(m): return [(x, y) for y, row in enumerate(m['grid']) for x, ch in enumerate(row) if ch == 'A']
def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
def extract(d, team):
    """per-champion event lists for one team: (round, kind, where, amount)"""
    mapname = d['sel'][0]['map']; m = load_map(mapname); A = altars(m)
    R = d['rounds']; ch = d['champs']; G = {int(k): v for k, v in d['groups'].items()}
    idx = [i for i, c in enumerate(ch) if c[0] == team]
    spawn0 = {i: (R[0]['c'][i][0], R[0]['c'][i][1]) for i in idx}
    sx = sum(p[0] for p in spawn0.values())/len(idx); sy = sum(p[1] for p in spawn0.values())/len(idx)
    def near_spawn(p): return cheb(p, (sx, sy)) <= 4
    def group_at(p):
        best, bd = None, 99
        for g, v in G.items():
            dd = min(cheb(p, t) for t in v['tiles'])
            if dd < bd: bd, best = dd, g
        return best, bd
    ev = {i: [] for i in idx}
    for k in range(1, len(R)):
        for i in idx:
            x0, y0, h0, g0, o0, a0 = R[k-1]['c'][i]; x1, y1, h1, g1, o1, a1 = R[k]['c'][i]; r = R[k]['r']
            if a0 and not a1: ev[i].append((r, 'death', (x0, y0), g0)); continue
            if not a0 and a1: ev[i].append((r, 'respawn', (x1, y1), 0)); continue
            if not a1: continue
            if g1 > g0:
                g, dd = group_at((x1, y1))
                ev[i].append((r, 'cap' if dd <= 3 else 'loot', g if dd <= 3 else (x1, y1), g1-g0))
            elif g1 < g0:
                da = min(cheb((x1, y1), a) for a in A) if A else 99
                ev[i].append((r, 'trib' if da <= 3 else 'drop', (x1, y1), g0-g1))
            if cheb((x0, y0), (x1, y1)) > 2:
                ev[i].append((r, 'recall' if near_spawn((x1, y1)) else 'jump', (x1, y1), g1))
            if o1 < o0: ev[i].append((r, 'shop', (x1, y1), o0-o1))
    return ev, idx, (sx, sy), A, G
if __name__ == '__main__':
    import sys
    d = json.load(open(sys.argv[1])); s = d['sel'][0]
    team = 0 if s['side'] == 'a' else 1
    ev, idx, sp, A, G = extract(d, team)
    print(s['map'], s['team'], 'vs', s['opp'], s['res'], s['score'], s['oscore'], 'spawn', sp, 'altars', A)
    for g, v in sorted(G.items()): print(' g', g, v['tiles'][:3], v['types'][0], v['gems'], v['gold'], v['respawn'])
    for i in idx:
        print(d['champs'][i][1], ' '.join(f"{e[0]}:{e[1]}{'' if e[1] in ('shop',) else ''}{e[2] if e[1] in ('cap',) else ''}{'+'+str(e[3]) if e[1] in ('cap','trib','loot') else ''}" for e in ev[i] if e[1] != 'shop'))

import json, glob, collections
from events import extract, cheb
from geo import Geo
from legs import team_of
maps = {}
def geo(name):
    if name not in maps: maps[name] = Geo(json.load(open(f'mapsj/{name}.json')))
    return maps[name]
res = collections.defaultdict(collections.Counter)
for f in sorted(glob.glob('compact/*.json')):
    d = json.load(open(f))
    for s in d['sel']:
        t = team_of(d, s); ev, idx, sp, A, G = extract(d, t); g = geo(s['map'])
        R = d['rounds']
        spt = [(R[0]['c'][i][0], R[0]['c'][i][1]) for i in idx]
        dsp = g.bfs(spt)
        sp2alt = min(min(dsp[y][x] for (x, y) in g.near([a], 2)) for a in A)
        key = (s['map'], s['team'])
        for i in idx:
            E = [e for e in ev[i] if e[1] in ('cap', 'trib', 'recall', 'death')]
            for k, e in enumerate(E):
                if e[1] != 'cap': continue
                nxt = E[k+1][1] if k+1 < len(E) else 'end'
                x, y = R[e[0]]['c'][i][0], R[e[0]]['c'][i][1] if e[0] < len(R) else (0, 0)
                walk = min(g.d_to_altar(a)[y][x] for a in A)
                rec = 5 + sp2alt
                better = 'recallbetter' if rec < walk else 'walkbetter'
                res[key][(nxt, better)] += 1
                res[key]['n'] += 1
for key in sorted(res):
    C = res[key]; n = C['n']
    tot = lambda b: sum(v for (k, v) in C.items() if isinstance(k, tuple) and k[1] == b)
    print(f"{key[0]:10}{key[1]:5} caps {n:4}  when RECALL is shorter ({tot('recallbetter'):3}): recall {C[('recall','recallbetter')]:3} trib {C[('trib','recallbetter')]:3} cap {C[('cap','recallbetter')]:3} | when WALK shorter ({tot('walkbetter'):3}): recall {C[('recall','walkbetter')]:3} trib {C[('trib','walkbetter')]:3} cap {C[('cap','walkbetter')]:3} death {C[('death','walkbetter')]+C[('death','recallbetter')]}")

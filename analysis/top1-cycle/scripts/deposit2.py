import json, glob, collections, statistics as S
from events import extract
from geo import Geo
from legs import team_of
maps = {}
def geo(name):
    if name not in maps: maps[name] = Geo(json.load(open(f'mapsj/{name}.json')))
    return maps[name]
rows = []
for f in sorted(glob.glob(__import__('os').environ.get('COMPACT','compact')+'/*.json')):
    d = json.load(open(f))
    for s in d['sel']:
        t = team_of(d, s); ev, idx, sp, A, G = extract(d, t); g = geo(s['map']); R = d['rounds']
        dsp = g.bfs([(R[0]['c'][i][0], R[0]['c'][i][1]) for i in idx])
        sp2alt = min(min(dsp[y][x] for (x, y) in g.near([a], 2)) for a in A)
        for i in idx:
            E = [e for e in ev[i] if e[1] in ('cap', 'trib', 'recall', 'death')]
            for k, e in enumerate(E):
                if e[1] != 'cap' or k+1 >= len(E): continue
                nxt = E[k+1]
                if nxt[1] not in ('recall', 'trib'): continue
                c = R[e[0]]['c'][i]; x, y = c[0], c[1]
                walk = min(g.d_to_altar(a)[y][x] for a in A); rec = 5 + sp2alt
                dsp_here = dsp[y][x]
                rows.append(dict(map=s['map'], team=s['team'], nxt=nxt[1], hp=c[2]/d['champs'][i][2], gems=c[3], walk=walk, rec=rec, dsp=dsp_here, champ=d['champs'][i][1], wait=nxt[0]-e[0]))
json.dump(rows, open('deposit_rows.json', 'w'))
by = collections.defaultdict(list)
for r in rows: by[(r['map'], r['team'], r['nxt'])].append(r)
for k in sorted(by):
    v = by[k]
    print(f"{k[0]:10}{k[1]:5}{k[2]:7} n={len(v):3} hp={S.mean(r['hp'] for r in v):.2f} gems={S.mean(r['gems'] for r in v):5.0f} walk={S.mean(r['walk'] for r in v):5.1f} rec={S.mean(r['rec'] for r in v):5.1f} delay={S.median(r['wait'] for r in v):4.0f}")

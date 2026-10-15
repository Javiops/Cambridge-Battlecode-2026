import json, glob, collections, statistics as S, sys
from events import extract
from geo import Geo
from legs import team_of
maps = {}
def geo(name):
    if name not in maps: maps[name] = Geo(json.load(open(f'mapsj/{name}.json')))
    return maps[name]
def group_timeline(d):
    """ready[g] = list of (round_from, state) ; returns function ready_at(g, r) -> round when group is alive (or None)"""
    G = {int(k): v for k, v in d['groups'].items()}
    tl = collections.defaultdict(list)
    for r, g, st, ct in d['gev']: tl[g].append((r, st))
    def ready_at(g, r):
        st, since = 'alive', 0
        for rr, s in tl[g]:
            if rr <= r: st, since = s, rr
            else: break
        if st == 'alive': return r
        if st == 'respawning': return since + G[g]['respawn']
        return None   # reward pending / being taken
    return G, ready_at
DEC = []
for f in sorted(glob.glob(__import__('os').environ.get('COMPACT','compact')+'/*.json')):
    d = json.load(open(f))
    G, ready_at = group_timeline(d)
    for s in d['sel']:
        t = team_of(d, s); ev, idx, sp, A, Gx = extract(d, t); g = geo(s['map']); R = d['rounds']
        spt = [(R[0]['c'][i][0], R[0]['c'][i][1]) for i in idx]; dsp = g.bfs(spt)
        enemy = [(R[0]['c'][i][0], R[0]['c'][i][1]) for i in range(len(d['champs'])) if d['champs'][i][0] != t]; den = g.bfs(enemy)
        sp2alt = min(min(dsp[y][x] for (x, y) in g.near([a], 2)) for a in A)
        dG = {gid: g.d_to_group(v['tiles']) for gid, v in G.items()}
        dAl = [g.d_to_altar(a) for a in A]
        tcaps = [(e[0], e[2], j) for j in idx for e in ev[j] if e[1] == 'cap' and isinstance(e[2], int)]
        for i in idx:
            E = [e for e in ev[i] if e[1] in ('cap', 'trib', 'recall', 'respawn')]
            prev = (0, 'start')
            for e in E:
                if e[1] == 'cap' and isinstance(e[2], int):
                    r0 = prev[0]; c = R[min(r0, len(R)-1)]['c'][i]; x, y = c[0], c[1]
                    if x < 0: prev = e; continue
                    cands = []
                    for gid, v in G.items():
                        tr = dG[gid][y][x]
                        if tr >= 10**6: continue
                        ra = ready_at(gid, r0)
                        if ra is None and gid != e[2]: continue
                        wait = max(0, (ra or r0) - (r0 + tr))
                        gx, gy = v['tiles'][0]
                        walkdep = min(D[gy][gx] for D in dAl); dep = min(walkdep, 5 + sp2alt)
                        cands.append(dict(g=gid, tr=tr, wait=wait, gems=v['gems'] or 0, gold=v['gold'] or 0, hp=v['hp'], dep=dep,
                                          side=dsp[gy][gx] - den[gy][gx], dsp=dsp[gy][gx], mate=any(j != i and gg == gid and r0 < rr <= r0 + tr + 15 for rr, gg, j in tcaps)))
                    if any(c_['g'] == e[2] for c_ in cands) and len(cands) > 1:
                        DEC.append(dict(map=s['map'], team=s['team'], champ=d['champs'][i][1], r=r0, prev=prev[1], chosen=e[2], cands=cands, carried=c[3], hp=c[2]/d['champs'][i][2]))
                prev = e
json.dump(DEC, open('decisions.json', 'w'))
print(len(DEC))

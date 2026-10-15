import json, glob, collections, statistics as S
from legs import team_of
from geo import Geo
maps = {}
def geo(name):
    if name not in maps: maps[name] = Geo(json.load(open(f'mapsj/{name}.json')))
    return maps[name]
agg = collections.defaultdict(lambda: collections.defaultdict(list))
for f in sorted(glob.glob(__import__('os').environ.get('COMPACT','compact')+'/*.json')):
    d = json.load(open(f)); G = {int(k): v for k, v in d['groups'].items()}; R = d['rounds']
    for s in d['sel']:
        t = team_of(d, s); key = (s['map'], s['team']); g = geo(s['map'])
        own = [(R[0]['c'][i][0], R[0]['c'][i][1]) for i in range(len(d['champs'])) if d['champs'][i][0] == t]
        enm = [(R[0]['c'][i][0], R[0]['c'][i][1]) for i in range(len(d['champs'])) if d['champs'][i][0] != t]
        dO, dE = g.bfs(own), g.bfs(enm)
        caps = collections.defaultdict(list)
        # who captured: group goes 'respawning' and the reward_available row before has captureTeam == t
        last_ct = {}
        for r, gid, st, ct in d['gev']:
            if st == 'reward_available': last_ct[gid] = ct
            if st == 'respawning' and last_ct.get(gid) == t: caps[gid].append(r)
        A = agg[key]; A['games'].append(1)
        for gid, rs in caps.items():
            x, y = G[gid]['tiles'][0]; side = dO[y][x] - dE[y][x]
            zone = 'own' if side < -6 else 'enemy' if side > 6 else 'mid'
            A['caps_' + zone].append(len(rs))
            for a, b in zip(rs, rs[1:]): A['ratio'].append((b - a) / G[gid]['respawn']); A['gap_minus_respawn'].append(b - a - G[gid]['respawn'])
        A['ngroups'].append(len(caps)); A['allgroups'].append(len(G))
for key in sorted(agg):
    A = agg[key]; n = len(A['games'])
    gm = A['gap_minus_respawn']
    print(f"{key[0]:10}{key[1]:5} groups used {S.mean(A['ngroups']):4.1f}/{S.mean(A['allgroups']):4.0f}  caps/game own {sum(A['caps_own'])/n:5.1f} mid {sum(A['caps_mid'])/n:5.1f} enemy {sum(A['caps_enemy'])/n:5.1f} | revisit gap - respawn: median {S.median(gm) if gm else 0:5.0f} p25 {S.quantiles(gm,n=4)[0] if len(gm)>3 else 0:5.0f} p75 {S.quantiles(gm,n=4)[2] if len(gm)>3 else 0:5.0f}  within 15 rounds of respawn: {sum(1 for v in gm if v<=15)/max(1,len(gm)):.2f}")

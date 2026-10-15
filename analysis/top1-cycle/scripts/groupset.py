import json, glob, collections, statistics as S, sys
from legs import team_of
from geo import Geo
maps = {}
def geo(name):
    if name not in maps: maps[name] = Geo(json.load(open(f'mapsj/{name}.json')))
    return maps[name]
rows = collections.defaultdict(lambda: collections.defaultdict(list))
for f in sorted(glob.glob(__import__('os').environ.get('COMPACT','compact')+'/*.json')):
    d = json.load(open(f)); G = {int(k): v for k, v in d['groups'].items()}; R = d['rounds']
    for s in d['sel']:
        t = team_of(d, s); g = geo(s['map'])
        own = [(R[0]['c'][i][0], R[0]['c'][i][1]) for i in range(len(d['champs'])) if d['champs'][i][0] == t]
        enm = [(R[0]['c'][i][0], R[0]['c'][i][1]) for i in range(len(d['champs'])) if d['champs'][i][0] != t]
        dO, dE = g.bfs(own), g.bfs(enm)
        sp2alt = min(min(dO[y][x] for (x, y) in g.near([a], 1)) for a in g.altars)
        last_ct = {}; caps = collections.Counter(); ecaps = collections.Counter()
        for r, gid, st, ct in d['gev']:
            if st == 'reward_available': last_ct[gid] = ct
            if st == 'respawning':
                if last_ct.get(gid) == t: caps[gid] += 1
                elif last_ct.get(gid) == 1 - t: ecaps[gid] += 1
        for gid, v in G.items():
            x, y = v['tiles'][0]
            walk = min(g.d_to_altar(a)[y][x] for a in g.altars)
            feat = (v['types'][0], v['gems'], v['hp'], v['respawn'], dO[y][x], dE[y][x], walk, 5 + sp2alt)
            rows[(s['map'], s['team'])][feat].append((caps[gid], ecaps[gid], d['final']['round']))
json.dump({f"{k[0]}|{k[1]}": {json.dumps(ft): v for ft, v in vv.items()} for k, vv in rows.items()}, open('groupset.json', 'w'))
want = sys.argv[1] if len(sys.argv) > 1 else 'mite'
for k in sorted(rows):
    if k[1] != want: continue
    print('==', k[0])
    for ft, v in sorted(rows[k].items(), key=lambda kv: kv[0][4]):
        c = S.mean(a for a, b, r in v); e = S.mean(b for a, b, r in v); rr = S.mean(r for a, b, r in v)
        print(f"   {ft[0][:5]:6} gems {ft[1]:4} hp {ft[2]:6} resp {ft[3]:4} dOwn {ft[4]:3} dEnemy {ft[5]:3} altar {ft[6]:3} | caps/game {c:5.2f} (rate {c/(rr/ (ft[3]+1)):.2f} of max) enemy {e:5.2f}")

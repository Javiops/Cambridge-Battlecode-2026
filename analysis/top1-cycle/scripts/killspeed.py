import json, glob, collections, statistics as S
from events import extract, cheb
from legs import team_of
out = collections.defaultdict(list); helpers = collections.defaultdict(list)
for f in sorted(glob.glob(__import__('os').environ.get('COMPACT','compact')+'/*.json')):
    d = json.load(open(f)); G = {int(k): v for k, v in d['groups'].items()}
    ra = {}
    for r, g, st, ct in d['gev']:
        if st == 'reward_available' and g not in ra: ra[g] = []
        if st == 'reward_available': ra[g].append(r)
    for s in d['sel']:
        t = team_of(d, s); ev, idx, sp, A, Gx = extract(d, t); R = d['rounds']
        for i in idx:
            for e in ev[i]:
                if e[1] != 'cap' or not isinstance(e[2], int): continue
                g = e[2]; tiles = G[g]['tiles']; rc = e[0]
                # cleared round: last reward_available before capture
                cl = max([r for r in ra.get(g, []) if r <= rc] or [rc - 5])
                # arrival: walk back from cleared round while this champion within 3 of the group
                a = cl
                while a > 0 and R[a-1]['c'][i][5] and min(cheb((R[a-1]['c'][i][0], R[a-1]['c'][i][1]), tt) for tt in tiles) <= 4: a -= 1
                n_help = sum(1 for j in idx if R[cl]['c'][j][5] and min(cheb((R[cl]['c'][j][0], R[cl]['c'][j][1]), tt) for tt in tiles) <= 4)
                if cl - a >= 1:
                    out[(s['map'], s['team'], G[g]['hp'])].append(G[g]['hp'] / (cl - a)); helpers[(s['map'], s['team'], G[g]['hp'])].append(n_help)
for k in sorted(out):
    v = out[k]
    if len(v) >= 5: print(k, len(v), 'hp/round median', round(S.median(v)), 'champs near', round(S.mean(helpers[k]), 1), 'rounds', round(k[2]/S.median(v)))

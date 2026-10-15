import json, glob, sys
from legs import legs_for, team_of
from events import extract
def leg_str(lg):
    ev = [(r, f"g{w}") for r, w, a in lg['caps']] + [(r, 'T') for r, a in lg['tribs']]
    ev.sort(); e = lg['end']
    return f"[{lg['start']}]" + ','.join(x for _, x in ev) + (f">{e[1][0].upper()}{int(e[2]*100) if e[2] is not None else ''}" if e else '')
mapn, teamn = sys.argv[1], sys.argv[2]; nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 2
k = 0
for f in sorted(glob.glob('compact/*.json')):
    d = json.load(open(f))
    for s in d['sel']:
        if s['map'] != mapn or s['team'] != teamn: continue
        k += 1
        if k > nmax: continue
        t = team_of(d, s); L, G, sp, A = legs_for(d, t)
        print(f"== {s['opp']} {s['res']} {s['score']}-{s['oscore']} r{d['final']['round']}")
        for i, legs in L.items(): print(f"  {d['champs'][i][1]:8} " + ' '.join(leg_str(l) for l in legs))

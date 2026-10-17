#!/usr/bin/env python3
"""Per-map deaths/kills/win of OUR bot in local arena runs next to the online target (gamestats rows of 'us').
usage: permap.py OURBOT ONLINE_ROWS.jsonl ARENA.json [...]"""
import json, sys, collections
our, rows_f, files = sys.argv[1], sys.argv[2], sys.argv[3:]
on = collections.defaultdict(lambda: [0, 0, 0, 0])
for l in open(rows_f):
    x = json.loads(l)
    if x['tag'] != 'us': continue
    a = on[x['map'].replace('_', '-')]; a[0] += 1; a[1] += x['deaths']; a[2] += x['kills']; a[3] += x['win']
loc = {}
for f in files:
    R = json.load(open(f)); rs = R['results'] if isinstance(R, dict) else R
    d = collections.defaultdict(lambda: [0, 0, 0, 0])
    for x in rs:
        if not x.get('ok'): continue
        t = 0 if x['a'].rstrip('/').endswith(our) else 1
        m = x['map'].split('/')[-1].split('.')[0]
        a = d[m]; a[0] += 1
        a[1] += sum(c['deaths'] for c in x['champs'] if c['team'] == t)
        a[2] += sum(c['kills'] for c in x['champs'] if c['team'] == t)
        a[3] += x['outcome'] == ('teamA' if t == 0 else 'teamB')
    loc[f.split('/')[-1].replace('.json', '').replace('on_', '')] = d
names = list(loc)
print(f"{'map':12s} {'online d/k win%':>17s} " + ' '.join(f'{n[:11]:>17s}' for n in names))
tot = collections.defaultdict(lambda: [0, 0, 0, 0])
for m in sorted(on):
    o = on[m]
    line = f"{m:12s} {o[1]/o[0]:5.1f}/{o[2]/o[0]:4.1f} {100*o[3]/o[0]:4.0f}%  "
    for n in names:
        a = loc[n].get(m)
        if a and a[0]:
            line += f"{a[1]/a[0]:6.1f}/{a[2]/a[0]:4.1f} {100*a[3]/a[0]:4.0f}% "
            for i in range(4): tot[n][i] += a[i]
        else: line += ' ' * 18
    print(line)
# correlation of per-map our deaths and of per-map win rate: online vs each local opponent
def corr(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sx = sum((x-mx)**2 for x in xs) ** .5; sy = sum((y-my)**2 for y in ys) ** .5
    return sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / (sx*sy) if sx and sy else float('nan')
print()
for n in names:
    ms = [m for m in on if m in loc[n] and loc[n][m][0]]
    cd = corr([on[m][1]/on[m][0] for m in ms], [loc[n][m][1]/loc[n][m][0] for m in ms])
    cw = corr([on[m][3]/on[m][0] for m in ms], [loc[n][m][3]/loc[n][m][0] for m in ms])
    t = tot[n]
    print(f"{n:12s} our deaths/game {t[1]/t[0]:5.1f} kills {t[2]/t[0]:5.1f} win {100*t[3]/t[0]:3.0f}% | per-map corr with online: deaths {cd:+.2f}, win {cw:+.2f}")
o = [sum(v[i] for v in on.values()) for i in range(4)]
print(f"{'ONLINE':12s} our deaths/game {o[1]/o[0]:5.1f} kills {o[2]/o[0]:5.1f} win {100*o[3]/o[0]:3.0f}%  (vs top 30)")

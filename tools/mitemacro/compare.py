# Compare our game against Mite's script game, champion by champion: when positions first differ, and the
# capture / recall / tribute timeline side by side. Usage: compare.py OURS.c.jsonl MITE.c.jsonl MAPSJ/map.json side(a|b) mite_side(a|b)
import json, sys, collections, importlib.util
spec = importlib.util.spec_from_file_location('ex', __file__.replace('compare.py', 'extract.py'))
ours, mite, mapf, side, mside = sys.argv[1:6]
def rounds(f):
    R = {}
    for l in open(f):
        d = json.loads(l)
        if d['t'] == 'round': R[d['r']] = d
    return R
m = json.load(open(mapf)); w, h, sym = m['w'], m['h'], m['sym']
def tf(p):
    x, y = p
    if side != mside:
        if sym in ('H', 'R180'): x = w - 1 - x
        if sym in ('V', 'R180'): y = h - 1 - y
    return (x, y)
A = rounds(ours); B = rounds(mite)
ta = 0 if side == 'a' else 1; tb = 0 if mside == 'a' else 1
def champs(R, t):
    return {c[2].lower(): c[0] for c in R[0]['champs'] if c[1] == t}
ca, cb = champs(A, ta), champs(B, tb)
for name in ca:
    if name not in cb: continue
    first = None; lag = []
    for r in range(1, min(max(A), max(B)) + 1):
        if r not in A or r not in B: continue
        pa = next(c for c in A[r]['champs'] if c[0] == ca[name]); pb = next(c for c in B[r]['champs'] if c[0] == cb[name])
        if first is None and (pa[3], pa[4]) != tf((pb[3], pb[4])): first = r
    def ev(R, i):
        out = []; prev = None
        for r in sorted(R):
            c = next(c for c in R[r]['champs'] if c[0] == i)
            if prev and c[7] > prev[7] + 0: out.append(f'+{c[7]-prev[7]}g@{r}')
            if prev and c[7] < prev[7] and c[9]: out.append(f'bank{prev[7]}@{r}')
            if prev and not c[9] and prev[9]: out.append(f'DIED@{r}')
            prev = c
        return out
    print(f'== {name}: first different tile at round {first}')
    print('   ours:', ' '.join(ev(A, ca[name])[:22]))
    print('   mite:', ' '.join(ev(B, cb[name])[:22]))
print('banked ours', A[max(A)]['sub'][ta], 'at', max(A), '| mite', B[max(B)]['sub'][tb], 'at', max(B))
for r in (100, 200, 300):
    if r in A and r in B: print(f'r{r}: banked ours {A[r]["sub"][ta]} mite {B[r]["sub"][tb]}')

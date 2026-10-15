import itertools, json, pickle
from strategy5 import GRID, MAPS, farm_set, label
names = list(MAPS); rows = []
for vals in itertools.product(*GRID.values()):
    p = dict(zip(GRID.keys(), vals)); bits = []; acc = []
    for n in names:
        lab = label(n); P = farm_set(n, **p)
        bits.append(not [k for k, v in lab.items() if v >= 3 and k not in P] and not [k for k in P if lab.get(k, 0) < 1])
        truth = {k for k, v in lab.items() if v >= 1.5}; acc.append((sum((k in P) == (k in truth) for k in lab), len(lab)))
    rows.append((p, bits, acc))
pickle.dump((names, rows), open('lomo5.pkl', 'wb'))
for i, n in enumerate(names):
    def score(r): return (sum(b for j, b in enumerate(r[1]) if j != i), sum(a for j, (a, t) in enumerate(r[2]) if j != i))
    best = max(score(r) for r in rows)
    top = [r for r in rows if score(r) == best]
    print(f"{n:10} fit on other 8: {best[0]}/8 ({len(top)} tied best)  held-out OK in {sum(r[1][i] for r in top)}/{len(top)}")

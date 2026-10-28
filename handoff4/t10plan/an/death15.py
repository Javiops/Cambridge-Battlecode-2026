r"""death15.py DECDIR [--index index.json]: classify our deaths r30-150 from the 20 rounds before (no stdout needed).
leave condition (v14_judge proxy): first round in r-20..r-1 with 2+ foes within 6, or alone (no ally <=6) <50% hp with a foe <=6.
fled  = after that round the champion got closer to its own spawn in >= half of its moves (proxy for a firing leave).
Classes: camp      : < 50% of hp lost in the last 10 rounds is champion damage (alone / with allies split)
         fled-*    : condition met and fled; caught by: dash (killer moved >= 2 tiles in a round within the last 3), ranged
                     (all champion damage of the last 5 rounds from cheb >= 2), else chase (adjacent melee caught up)
         nolv-1foe : never 2+ foes within 6 and never alone<50%: 1 foe only (ratio path)
         nolv-unseen: condition met < 3 rounds before death (foes arrived late / burst)
         stayed    : condition met >= 3 rounds before, champion did not flee (ratio >= 0.8 or still engaged)
"""
import sys, os, json, gzip, collections
TYPES = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HoR']
a = sys.argv[1:]; index = None; dirs = []
while a:
    x = a.pop(0)
    if x == '--index': index = a.pop(0)
    else: dirs.append(x)
side = {}
if index:
    for x in json.load(open(index)): side[x['file']] = 0 if x['side'] == 'a' else 1
def cheb(p, q): return max(abs(p[0] - q[0]), abs(p[1] - q[1]))
CL = collections.Counter(); KILL = collections.Counter(); n = 0; ex = []
for d in dirs:
    bot = os.path.basename(d.rstrip('/'))
    for fn in sorted(os.listdir(d)):
        key = f"{bot}/{fn.replace('.json.gz', '.repl26a')}"
        if index and key not in side: continue
        us = side[key] if index else (1 if fn.endswith('_b.json.gz') else 0)
        D = json.load(gzip.open(os.path.join(d, fn))); R = D['rounds']
        if not R: continue
        n += 1
        byr = {rr['r']: {c[0]: c for c in rr['c']} for rr in R}
        spawn = {}
        for c in R[0]['c']: spawn.setdefault(c[1], (c[3], c[4]))
        cc = collections.defaultdict(list)
        for r, at, t, dmg in D['cc']: cc[t].append((r, at, dmg))
        for idx in [c[0] for c in R[0]['c'] if c[1] == us]:
            sp = spawn[us]
            for r in range(30, 151):
                if r not in byr or r - 1 not in byr or idx not in byr[r]: continue
                if not (byr[r - 1][idx][9] and not byr[r][idx][9]): continue
                hp10 = byr[r - 10][idx][5] if r - 10 in byr and byr[r - 10][idx][9] else byr[r - 1][idx][5]
                cd = sum(dm for q, at, dm in cc[idx] if r - 10 <= q <= r)
                cat = None; t0 = None
                for q in range(r - 20, r):
                    if q not in byr or not byr[q][idx][9]: continue
                    me = byr[q][idx]; p = me[3:5]
                    fo = [c for c in byr[q].values() if c[1] != us and c[9] and cheb(c[3:5], p) <= 6 and cheb(c[3:5], spawn[1 - us]) > 2]
                    al = [c for c in byr[q].values() if c[1] == us and c[0] != idx and c[9] and cheb(c[3:5], p) <= 6]
                    if len(fo) >= 2 or (not al and fo and me[5] < 0.5 * me[6]): t0 = q; break
                al5 = sum(1 for c in byr.get(r - 5, {}).values() if c[1] == us and c[0] != idx and c[9] and cheb(c[3:5], byr[r - 5][idx][3:5]) <= 6) if r - 5 in byr else 0
                if cd < 0.5 * max(hp10, 1):
                    cat = 'camp-alone' if al5 == 0 else 'camp-allies'
                elif t0 is None:
                    cat = 'nolv-1foe'
                else:
                    mv = home = 0
                    for q in range(t0 + 1, r):
                        if q in byr and q - 1 in byr and byr[q][idx][9]:
                            p0, p1 = byr[q - 1][idx][3:5], byr[q][idx][3:5]
                            if p0 != p1: mv += 1; home += cheb(p1, sp) < cheb(p0, sp)
                    fled = mv >= 2 and home * 2 >= mv
                    if not fled: cat = 'nolv-late' if r - t0 < 3 else 'stayed'
                    else:
                        hits = [(q, at, dm) for q, at, dm in cc[idx] if r - 5 <= q <= r]
                        killer = max({at for _, at, _ in hits}, key=lambda k: sum(dm for _, a2, dm in hits if a2 == k)) if hits else None
                        dash = ranged = False
                        if killer is not None:
                            for q in range(r - 3, r + 1):
                                if q in byr and q - 1 in byr and killer in byr[q] and byr[q][killer][9] and byr[q - 1][killer][9] and cheb(byr[q][killer][3:5], byr[q - 1][killer][3:5]) >= 2 and cheb(byr[q][killer][3:5], byr[q - 1][killer][3:5]) <= 4: dash = True
                            ranged = all(q - 1 in byr and at in byr[q - 1] and cheb(byr[q - 1][at][3:5], byr[q - 1][idx][3:5]) >= 2 for q, at, _ in hits)
                            KILL[TYPES[byr[r][killer][2]]] += 1
                        cat = 'fled-dash' if dash else 'fled-ranged' if ranged else 'fled-chase'
                CL[cat] += 1; ex.append((fn, r, TYPES[byr[r][idx][2]], cat))
print(f"{n} games, deaths r30-150 {sum(CL.values())/max(n,1):.2f}/game")
print("| class | n | per game | share |"); print("|---|---|---|---|")
for k in ['fled-chase', 'fled-dash', 'fled-ranged', 'stayed', 'nolv-late', 'nolv-1foe', 'camp-alone', 'camp-allies']:
    print(f"| {k} | {CL[k]} | {CL[k]/max(n,1):.2f} | {100*CL[k]/max(1,sum(CL.values())):.0f}% |")
print("killers of fled deaths:", dict(KILL.most_common()))
if os.environ.get('EX'): [print(*e) for e in ex]

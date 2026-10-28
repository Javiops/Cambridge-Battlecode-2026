# capdur.py TAG [MIN=40]: our captures of groups worth MIN+ gems r<=600 in dec/TAG: rounds from the first hit of the
# capturing episode (hits <=15 rounds apart) to the capture, bodies that hit, and the carries' strength stat at r100/r300.
import json, gzip, glob, os, sys, collections
W = '/tmp/claude-0/w'; T = sys.argv[1]; MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 40
durs = []; bodies = []; n = 0; att = 0; first = []
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    us = 0 if f.endswith('_a.json.gz') else 1; D = json.load(gzip.open(f)); n += 1
    team = {c[0]: c[1] for c in D['rounds'][0]['c']}
    grp = {k[0]: k[2] for k in D['camps']}; gv = {}
    for k in D['camps']: gv[k[2]] = max(gv.get(k[2], 0), k[5] or 0)
    big = {g for g, v in gv.items() if v >= MIN}
    hits = collections.defaultdict(lambda: collections.defaultdict(set))
    for r, dd in D['ck'].items():
        r = int(r)
        if r > 600: continue
        for k, v in dd.items():
            a, ci = map(int, k.split('>')); g = grp.get(ci)
            if g in big and team.get(a) == us: hits[g][r].add(a)
    caps = {g: r for g, t, r in D['caps'] if t == us and g in big and r <= 600}
    for g, rs in hits.items():
        rr = sorted(rs); eps = []; cur = [rr[0]]
        for r in rr[1:]:
            if r - cur[-1] <= 15: cur.append(r)
            else: eps.append(cur); cur = [r]
        eps.append(cur); att += len(eps)
        for ep in eps:
            if g in caps and ep[0] <= caps[g] <= ep[-1] + 10:
                durs.append(caps[g] - ep[0]); bodies.append(len(set().union(*(rs[r] for r in ep)))); first.append(caps[g])
if durs:
    durs.sort()
    print(f'{T}: games {n}; {MIN}+ captures {len(durs)} ({len(durs)/n:.2f}/game) of {att} attempts ({att/n:.2f}/game); '
          f'rounds first hit->capture mean {sum(durs)/len(durs):.1f} median {durs[len(durs)//2]}; bodies {sum(bodies)/len(bodies):.2f}; '
          f'capture round median {sorted(first)[len(first)//2]}')
else: print(f'{T}: games {n}; no {MIN}+ captures')

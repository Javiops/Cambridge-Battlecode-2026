# feat.py: per game, per team, per champion, per 50-round bin features from a dec json.gz (ext.py format)
import json, gzip, sys, os, pickle
from collections import defaultdict
BINS = 50
def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
def feats(path, rmax=1000):
    D = json.load(gzip.open(path))
    R = D['rounds']; camps = D['camps'] or []
    c0 = R[0]['c']
    team = {c[0]: c[1] for c in c0}; typ = {c[0]: c[2] for c in c0}
    sp = {}
    for t in (0, 1):
        P = [(c[3], c[4]) for c in c0 if c[1] == t]; sp[t] = (sum(p[0] for p in P)/len(P), sum(p[1] for p in P)/len(P))
    S = cheb(sp[0], sp[1])
    grp = defaultdict(lambda: {'gems': 0, 'gold': 0, 'hp': 0, 'n': 0, 'x': 0, 'y': 0, 'ty': []})
    campgrp = {}
    for k in camps:
        g = grp[k[2]]; campgrp[k[0]] = k[2]
        g['gems'] = max(g['gems'], k[5] or 0); g['gold'] = max(g['gold'], k[6] or 0)   # group reward carried by each camp (never sum)
        g['hp'] += k[7]; g['n'] += 1; g['ty'].append(k[1]); g['x'] += k[3]; g['y'] += k[4]
    for g in grp.values(): g['x'] /= g['n']; g['y'] /= g['n']
    # group position along own->enemy axis per team
    def frac(t, p):
        a = cheb(p, sp[t]); b = cheb(p, sp[1-t]); return a/(a+b+1e-9)
    out = {'S': S, 'team': team, 'typ': typ, 'final': D['meta']['final'], 'gems': D['meta']['gems'], 'outcome': D['meta']['outcome'],
           'grp': {gi: dict(g) for gi, g in grp.items()}}
    F = defaultdict(lambda: defaultdict(float))  # (idx, bin) -> metrics
    T = defaultdict(lambda: defaultdict(float))  # (team, bin)
    hits = []   # (round, idx, group)
    prev_alive = {}
    ck = D['ck']
    for row in R:
        r = row['r']
        if r > rmax: break
        b = r // BINS
        C = row['c']
        alive = [c for c in C if c[9]]
        for t in (0, 1):
            A = [c for c in alive if c[1] == t]
            # clusters link <= 4
            comp = []; seen = set()
            for c in A:
                if c[0] in seen: continue
                st = [c]; seen.add(c[0]); n = 0
                while st:
                    x = st.pop(); n += 1
                    for y in A:
                        if y[0] not in seen and cheb((x[3], x[4]), (y[3], y[4])) <= 4: seen.add(y[0]); st.append(y)
                comp.append(n)
            T[(t, b)]['n'] += 1; T[(t, b)]['alive'] += len(A); T[(t, b)]['ncl'] += len(comp); T[(t, b)]['big'] += max(comp) if comp else 0
        for c in C:
            i = c[0]; t = c[1]; f = F[(i, b)]
            f['n'] += 1
            if prev_alive.get(i, 1) and not c[9]: f['death'] += 1
            prev_alive[i] = c[9]
            if not c[9]: f['dead'] += 1; continue
            p = (c[3], c[4]); fr = frac(t, p)
            f['alive'] += 1; f['fr'] += fr; f['own'] += fr < 0.5
            f['home'] += cheb(p, sp[t]) <= 3
            al = sum(1 for y in alive if y[1] == t and y[0] != i and cheb(p, (y[3], y[4])) <= 4)
            fo = sum(1 for y in alive if y[1] != t and cheb(p, (y[3], y[4])) <= 4)
            f['al4'] += al; f['fo4'] += fo
            if fo: f['contact'] += 1; f['outn'] += fo > al + 1; f['supn'] += al + 1 > fo
            f['hp'] += c[5]/c[6]; f['gems'] += c[7]; f['gold'] += c[8]
        for key, v in (ck.get(str(r)) or {}).items():
            a, k = key.split('>'); a = int(a); k = int(k)
            g = campgrp.get(k)
            if g is not None: hits.append((r, a, g))
    # captures
    caps = [(g, t, r) for g, t, r in D['caps'] if r <= rmax]
    out['F'] = {k: dict(v) for k, v in F.items()}; out['T'] = {k: dict(v) for k, v in T.items()}
    out['hits'] = hits; out['caps'] = caps; out['sp'] = sp
    # submitted gems per bin per team
    sg = {}
    for row in R:
        if row['r'] % BINS == 0 and row['r'] <= rmax: sg[row['r'] // BINS] = row['sg']
    out['sg'] = sg
    return out
if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    pickle.dump(feats(src), open(dst, 'wb'))

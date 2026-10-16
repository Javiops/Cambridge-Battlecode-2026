#!/usr/bin/env python3
"""Deaths with no enemy champion within 7 tiles (killed by a camp) per map and champion, from out/lz compact games.
usage: python3 tools/nm/campdeaths.py bots/US --opps sp_farm,sp_castera --maps ambush,eight  (games from localzones.py)"""
import argparse, collections, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ab  # noqa
p = argparse.ArgumentParser(); p.add_argument('bots', nargs='+'); p.add_argument('--opps', default='sp_farm'); p.add_argument('--maps', default='ambush'); A = p.parse_args()
cheb = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1]))
for b in A.bots:
    for mn in A.maps.split(','):
        camp = collections.Counter(); fight = collections.Counter(); early = 0; n = 0
        for o in A.opps.split(','):
            o = 'bots/' + o
            for side in 'AB':
                x, y = (b, o) if side == 'A' else (o, b)
                f = f"out/lz/{mn}_{ab.sha(ab.wasm_of(x)) + ab.sha(ab.wasm_of(y))}/compact.json"
                if not os.path.exists(f): continue
                d = json.load(open(f)); t = 0 if side == 'A' else 1; n += 1
                CH = d['champs']; R = d['R']
                me = [i for i, c in enumerate(CH) if c[1] == t]; th = [i for i, c in enumerate(CH) if c[1] != t]
                for k in range(1, len(R)):
                    a, c = R[k - 1][3], R[k][3]
                    for i in me:
                        if a[i][6] and not c[i][6]:
                            near = any(a[j][6] and cheb(a[i][:2], a[j][:2]) <= 7 for j in th)
                            (fight if near else camp)[CH[i][2]] += 1
                            if not near and R[k][0] < 300: early += 1
        print(f"{os.path.basename(b):12s} {mn:12s} games={n} camp deaths={sum(camp.values())} ({early} before r300) {dict(camp)} | fight deaths={sum(fight.values())} {dict(fight)}")

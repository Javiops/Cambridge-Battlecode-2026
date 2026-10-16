#!/usr/bin/env python3
"""Per-map panel table (2026-10-16, new-maps thread): every bot vs every specialist on every map, both sides.

usage (repo root): python3 tools/nm/permap.py bots/BASE bots/CAND [...] [--maps 'maps/*.map26a'] [--opps ...]

For each map prints, per bot, the games won out of (2 sides x specialists), the deaths per game and our gems, and
for each candidate the games that flip vs the first bot (won by one, lost by the other; same opponent+map+side).
Shares the out/ab-cache with ab.py, gate.py and panel.py, so games already played are not replayed.
"""
import argparse, glob, hashlib, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ab  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument('bots', nargs='+')
p.add_argument('--opps', default='sp_castera,sp_casterh,sp_hunt,sp_centre,sp_farm')
p.add_argument('--maps', default='maps/*.map26a')
p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
p.add_argument('--only', default='', help='comma list of map names to show (others still summed in "all")')
A = p.parse_args()
bots = [b.rstrip('/') for b in A.bots]
opps = ['bots/' + o if '/' not in o else o for o in A.opps.split(',')]
with ThreadPoolExecutor(4) as ex:
    list(ex.map(ab.build, bots + opps))
ver = subprocess.run([ab.CLI, '--version'], capture_output=True, text=True, env=ab.ENV).stdout.strip()
maps = sorted(m for pat in A.maps.split(',') for m in glob.glob(pat))
h = {b: ab.sha(ab.wasm_of(b)) for b in bots + opps}
cache = os.path.join('out', 'ab-cache'); os.makedirs(cache, exist_ok=True)
jobs, idx = [], []
for b in bots:
    for o in opps:
        for m in maps:
            hm = hashlib.sha256((ab.sha(m) + ver).encode()).hexdigest()[:8]
            for side in 'AB':
                x, y = (b, o) if side == 'A' else (o, b)
                jobs.append((x, y, m, f'{h[x]}_{h[y]}_{hm}', cache, os.path.join('out', 'panel', f'{os.path.basename(x)}_{os.path.basename(y)}_{os.path.basename(m)}'), False))
                idx.append((b, o, m, side))
with ThreadPoolExecutor(A.jobs) as ex:
    res = list(ex.map(ab.play, jobs))
R = {}
for (b, o, m, side), r in zip(idx, res):
    if not r.get('ok'):
        continue
    me = 0 if side == 'A' else 1
    R[(b, o, m, side)] = (r['outcome'] == ('teamA' if me == 0 else 'teamB'), r['deaths'][me], r['gems'][me], r['gems'][1 - me])
name = lambda b: os.path.basename(b)
only = set(A.only.split(',')) if A.only else None
print(f"{'map':14s} " + ' '.join(f'{name(b)[:16]:>22s}' for b in bots) + '   flips vs ' + name(bots[0]))
tot = {b: [0, 0] for b in bots}
for m in maps:
    mn = os.path.basename(m).replace('.map26a', '')
    cells, flips = [], []
    for b in bots:
        ks = [(b, o, m, s) for o in opps for s in 'AB' if (b, o, m, s) in R]
        w = sum(R[k][0] for k in ks); n = len(ks)
        d = sum(R[k][1] for k in ks) / max(n, 1); g = sum(R[k][2] for k in ks) / max(n, 1)
        tot[b][0] += w; tot[b][1] += n
        cells.append(f'{w:2d}/{n:<2d} d{d:4.1f} g{g:5.0f}')
        if b != bots[0]:
            up = sum(1 for o in opps for s in 'AB' if (b, o, m, s) in R and (bots[0], o, m, s) in R and R[(b, o, m, s)][0] and not R[(bots[0], o, m, s)][0])
            dn = sum(1 for o in opps for s in 'AB' if (b, o, m, s) in R and (bots[0], o, m, s) in R and not R[(b, o, m, s)][0] and R[(bots[0], o, m, s)][0])
            flips.append(f'{up}-{dn}')
    if only is None or mn in only:
        print(f'{mn:14s} ' + ' '.join(f'{c:>22s}' for c in cells) + '   ' + ' '.join(flips))
print(f"{'all':14s} " + ' '.join(f'{tot[b][0]:>9d}/{tot[b][1]:<4d} {100 * tot[b][0] / max(tot[b][1], 1):5.1f}%   ' for b in bots))

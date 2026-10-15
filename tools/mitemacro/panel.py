#!/usr/bin/env python3
"""Micro test bench for P_MITEMACRO bots: every candidate plays the 9 official maps from both sides against a fixed
panel of opponents. With the macro fixed (Mite's script), the differences between two candidates come from micro and
mid-game decisions. A map-opponent pair counts for a candidate when it wins it from both sides.

usage: python3 tools/mitemacro/panel.py bots/CAND1 bots/CAND2 [--panel bots/x,bots/y] [--jobs 4]
"""
import argparse, glob, hashlib, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ab  # build(), play(), sha(), wasm_of(), sign_p(): same cache as ab.py

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('cands', nargs='+')
p.add_argument('--panel', default='bots/study28,bots/spar11,bots/spar12,bots/spar16,bots/v30,bots/study25')
p.add_argument('--maps', default='maps/*.map26a')
p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
A = p.parse_args()
cands = [c.rstrip('/') for c in A.cands]; panel = [x.rstrip('/') for x in A.panel.split(',')]
with ThreadPoolExecutor(4) as ex: list(ex.map(ab.build, sorted(set(cands + panel))))
ver = subprocess.run([ab.CLI, '--version'], capture_output=True, text=True, env=ab.ENV).stdout.strip()
h = {b: ab.sha(ab.wasm_of(b)) for b in cands + panel}
cache = os.path.join('out', 'ab-cache'); os.makedirs(cache, exist_ok=True)
maps = sorted(glob.glob(A.maps))
jobs, idx = [], []
for c in cands:
    for o in panel:
        for m in maps:
            hm = hashlib.sha256((ab.sha(m) + ver).encode()).hexdigest()[:8]
            name = os.path.splitext(os.path.basename(m))[0]
            for side, (x, y) in (('A', (c, o)), ('B', (o, c))):
                jobs.append((x, y, m, f'{h[x]}_{h[y]}_{hm}', cache, os.path.join('out', 'panel', os.path.basename(c), os.path.basename(o), f'{name}_{side}'), False))
                idx.append((c, o, name, side))
with ThreadPoolExecutor(A.jobs) as ex: res = list(ex.map(ab.play, jobs))
won = {}
for (c, o, name, side), r in zip(idx, res):
    if not r.get('ok'): print('FAIL', c, o, name, side); continue
    me = 0 if side == 'A' else 1
    win = r['outcome'] == ('teamA' if me == 0 else 'teamB')
    d = won.setdefault((c, o, name), {})
    d[side] = (win, r['gems'][me], r['gems'][1 - me], r['deaths'][me], r['deaths'][1 - me])
mapsn = [os.path.splitext(os.path.basename(m))[0] for m in maps]
for c in cands:
    print(f'\n== {c}: per opponent, maps won both sides / lost both / split (games won), deaths ours-theirs')
    tot = [0, 0, 0, 0, 0, 0]
    for o in panel:
        wb = lb = sp = g = dm = dt = 0
        for n in mapsn:
            d = won.get((c, o, n), {})
            ws = [d[s][0] for s in d]
            g += sum(ws); dm += sum(d[s][3] for s in d); dt += sum(d[s][4] for s in d)
            if len(ws) == 2: wb += all(ws); lb += not any(ws); sp += ws[0] != ws[1]
        tot = [a + b for a, b in zip(tot, [wb, lb, sp, g, dm, dt])]
        print(f'   vs {os.path.basename(o):10s} {wb}/{lb}/{sp}  games {g}-{2 * len(mapsn) - g}  deaths {dm}-{dt}')
    print(f'   TOTAL        {tot[0]}/{tot[1]}/{tot[2]}  games {tot[3]}-{2 * len(mapsn) * len(panel) - tot[3]}  deaths {tot[4]}-{tot[5]}')
    print('   per map (games won of', 2 * len(panel), '):', ' '.join(f"{n}:{sum(won.get((c, o, n), {}).get(s, (0,))[0] for o in panel for s in 'AB')}" for n in mapsn))
if len(cands) == 2:  # head to head on the panel: pairs (opponent, map, side) where exactly one candidate won
    a, b = cands; wa = wb = 0
    for o in panel:
        for n in mapsn:
            for s in 'AB':
                ra, rb = won.get((a, o, n), {}).get(s), won.get((b, o, n), {}).get(s)
                if ra and rb and ra[0] != rb[0]: wa += ra[0]; wb += rb[0]
    print(f'\n{os.path.basename(a)} vs {os.path.basename(b)} on the same games: {wa} won only by {os.path.basename(a)}, {wb} only by {os.path.basename(b)}, sign test p={ab.sign_p(wa, wa + wb):.2f}')

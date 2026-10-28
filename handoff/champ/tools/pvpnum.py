#!/usr/bin/env python3
"""pvpnum.py OUT.json TEAM:REPLAY [TEAM:REPLAY ...] | --list FILE (lines "replay team", team 0 = side A, 1 = side B)

Champion-vs-champion rounds and the numbers in them ("Mejorar cada campeón en su fichero", 10-24).
A PvP round = a round r < 400 in which one of our living champions has a living rival champion within 4 tiles
(Chebyshev) AND no living camp monster within 3 tiles of it (so camp fights are left out), and it was alive the round before.
num = 1 + (our other living champions within 3 tiles of it) - (living rival champions within 3 tiles of it), clipped to [-2, +2].
"Superando en 2" = num = +2 (e.g. 3 of ours vs 1 of theirs within 3 tiles). Each champion counts its own rounds.
Also: distance to the nearest rival (1..4), hp lost per round, moved. Phases r<150 and r150-400.
Online 10-24 (near maps, t10_near_40 vs v20_near_80): num=+2 Vesper 41% vs 21%, Marcella 43% vs 19%, Vendetta 36% vs 12%.
Needs node; replaydump.js and the engine wasm are in this folder (1.0.3 first, then 1.0.2)."""
import sys, os, json, subprocess, collections, shutil, tempfile
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.environ.get('REPLAYDUMP', os.path.join(HERE, 'replaydump.js'))
WASMS = [os.path.join(HERE, 'v1_0_3-DRqNt1t2.wasm'), os.path.join(HERE, 'v1_0_2-BIJCVwNu.wasm')]
def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
def dump(z):
    tmp = os.path.join(tempfile.gettempdir(), 'pvp_%d_%s' % (os.getpid(), os.path.basename(z))); shutil.copyfile(z, tmp)
    try:
        for w in WASMS:
            p = subprocess.run(['node', DUMP, tmp, '--camps'], capture_output=True, text=True, timeout=300, env=dict(os.environ, CAMBC_VIS_WASM=w))
            rows = [json.loads(l) for l in p.stdout.splitlines() if l.startswith('{')]
            rows = [r for r in rows if 'champions' in r and 'camps' in r and not r.get('draft')]
            if rows: return rows
    finally:
        try: os.remove(tmp)
        except OSError: pass
    return None
def one(a):
    z, team = a
    rows = dump(z)
    if not rows: return None
    out = collections.Counter(); prev = {}
    for r in rows:
        rd = r['round']
        if rd >= 400: break
        mons = [(m['x'], m['y']) for m in r['camps'] if m['alive'] and m['x'] >= 0]
        cs = {(c['team'], c['index']): c for c in r['champions']}
        for k, c in cs.items():
            if c['team'] != team or not c['alive']: continue
            p = (c['x'], c['y'])
            foes = [(cheb(p, (f['x'], f['y'])), f) for f in r['champions'] if f['team'] != team and f['alive']]
            if not foes: continue
            d = min(x[0] for x in foes)
            if d > 4 or (mons and min(cheb(p, m) for m in mons) <= 3): continue
            pc = prev.get(k)
            if not pc or not pc['alive']: continue
            nfo = sum(1 for dd, f in foes if dd <= 3)
            nal = sum(1 for o in r['champions'] if o['team'] == team and o['alive'] and o['index'] != c['index'] and cheb(p, (o['x'], o['y'])) <= 3)
            ph = 'r<150' if rd < 150 else 'r150-400'; t = c['typeName']
            out[json.dumps([t, ph, 'n'])] += 1
            out[json.dumps([t, ph, 'd', min(d, 4)])] += 1
            out[json.dumps([t, ph, 'num', max(-2, min(2, 1 + nal - nfo))])] += 1
            out[json.dumps([t, ph, 'lost'])] += max(0, pc['health'] - c['health'])
            out[json.dumps([t, ph, 'mhp'])] += c['maxHealth']
            out[json.dumps([t, ph, 'mv'])] += (pc['x'], pc['y']) != p
        prev = cs
    return out
def table(C):
    C = {tuple(json.loads(k)) if isinstance(k, str) else k: v for k, v in C.items()}
    types = sorted({k[0] for k in C})
    for t in types:
        for ph in ['r<150', 'r150-400']:
            n = C.get((t, ph, 'n'), 0)
            if n < 20: continue
            g = lambda *k: C.get((t, ph) + k, 0)
            print(f"{t:11s} {ph:8s} n{n:5d} dist " + ' '.join(f"{d}:{g('d', d)/n:.0%}" for d in (1, 2, 3, 4)) +
                  " | num " + ' '.join(f"{x:+d}:{g('num', x)/n:.0%}" for x in (-2, -1, 0, 1, 2)) +
                  f" | lost/rd {g('lost')/n:.0f} ({g('lost')/max(1, g('mhp'))*100:.1f}% mhp) | moved {g('mv')/n:.0%}")
if __name__ == '__main__':
    out = sys.argv[1]
    if sys.argv[2] == '--list': jobs = [(l.split()[0], int(l.split()[1])) for l in open(sys.argv[3]) if l.strip()]
    else: jobs = [(a.split(':', 1)[1], int(a.split(':', 1)[0])) for a in sys.argv[2:]]
    C = collections.Counter()
    with ProcessPoolExecutor(int(os.environ.get('NW', '4'))) as ex:
        for res in ex.map(one, jobs):
            if res: C.update(res)
    json.dump(C, open(out, 'w')); table(C)

#!/usr/bin/env python3
"""I020: why every recall happened, how far from home, and how much gold it spent at home (P_LOGRECALL stdout logs).
usage: python3 analysis/four-fixes/recalllog.py out/ab/x_log_vs_study28"""
import glob, os, re, sys, statistics as st
from collections import defaultdict
root = sys.argv[1]
rec = []
for f in glob.glob(os.path.join(root, '**', 'team-*.stdout'), recursive=True):
    side = os.path.basename(os.path.dirname(f))[-1]
    if (side == 'A') != f.endswith('team-a.stdout'): continue
    last = {}
    for l in open(f, errors='replace').read().replace('\x00', '\n').splitlines():
        m = re.match(r'\[recall\] r(\d+) (\S+) (\S+) hp=(\d+)% gold=(\d+) gems=(\d+) home=(\d+)', l)
        if m:
            r = dict(round=int(m[1]), who=m[2], why=m[3], hp=int(m[4]), gold=int(m[5]), gems=int(m[6]), home=int(m[7]), spent=None)
            rec.append(r); last[m[2]] = r; continue
        m = re.match(r'\[spent\] r(\d+) (\S+) after=(\d+) gold (\d+) -> (\d+)', l)
        if m and m[2] in last and last[m[2]]['spent'] is None:
            last[m[2]]['spent'] = int(m[4]) - int(m[5])
print(len(rec), 'recalls')
def kind(r):
    w = r['why']
    if r['hp'] < 55: return w.replace('+shop', '') + ' (hp<55%)'
    if '+shop' in w or (w == 'cap-recall' and r['gold'] >= 90 and r['hp'] >= 90): return w.replace('+shop', '') + ' (gold only)'
    return w + ' (hp 55-90%)'
by = defaultdict(list)
for r in rec: by[kind(r)].append(r)
print(f"{'reason':34s} {'n':>5s} {'home walk':>9s} {'gold':>6s} {'spent':>6s} {'spent 0':>8s}")
for k, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    sp = [r['spent'] for r in rs if r['spent'] is not None]
    print(f"{k:34s} {len(rs):5d} {st.mean(r['home'] for r in rs):9.1f} {st.mean(r['gold'] for r in rs):6.0f} "
          f"{(st.mean(sp) if sp else 0):6.0f} {100*sum(x <= 0 for x in sp)/max(1,len(sp)):7.0f}%")
g = [r for r in rec if kind(r).endswith('(gold only)') and r['spent'] is not None]
if g:
    print('\ngold-only recalls by walk home: n, gold spent per tile of walk back')
    for lo, hi in ((0, 10), (10, 20), (20, 30), (30, 45), (45, 999)):
        rs = [r for r in g if lo <= r['home'] < hi]
        if rs: print(f"  home {lo:2d}-{hi:3d}: {len(rs):4d}  spent {st.mean(r['spent'] for r in rs):5.0f}  gold/tile {st.mean(r['spent']/max(1,r['home']) for r in rs):5.1f}")

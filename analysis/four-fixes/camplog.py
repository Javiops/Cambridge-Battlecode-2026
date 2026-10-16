#!/usr/bin/env python3
"""I021: predicted vs actual camp damage from P_LOGCAMP stdout logs.
usage: python3 analysis/four-fixes/camplog.py out/ab/x_log_vs_study28   (reads every team-?.stdout of the logging bot)"""
import glob, os, re, sys, statistics as st
root = sys.argv[1]
rows = []
for f in glob.glob(os.path.join(root, '**', 'team-*.stdout'), recursive=True):
    side = os.path.basename(os.path.dirname(f))[-1]          # the logging bot is team a on side A, team b on side B
    if (side == 'A') != f.endswith('team-a.stdout'): continue
    for l in open(f, errors='replace').read().replace('\x00', '\n').splitlines():
        if not l.startswith('[camp]'): continue
        d = dict(kv.split('=', 1) for kv in l.split() if '=' in kv)
        t = l.split()
        rows.append({k: (float(v) if re.match(r'^-?[\d.]+$', v) else v) for k, v in d.items()} |
                    {'map': f, 'r': int(t[1][1:]), 'who': t[2], 'g': int(t[3][1:])})
print(len(rows), 'camp fights logged')
def summ(rs, label):
    if not rs: return
    lost = [r['lost'] for r in rs]; old = [r['old'] for r in rs]; tank = [r['tank'] for r in rs]
    ratio_o = [r['lost'] / r['old'] for r in rs if r['old'] > 1]
    ratio_t = [r['lost'] / r['tank'] for r in rs if r['tank'] > 1]
    under_o = sum(r['lost'] > r['old'] * 1.1 + 10 for r in rs); under_t = sum(r['lost'] > r['tank'] * 1.1 + 10 for r in rs)
    over_hp = sum(r['old'] > r['hp0'] for r in rs)
    print(f"{label:28s} n={len(rs):5d} lost avg {st.mean(lost):6.0f} | old pred {st.mean(old):6.0f} (lost/old median {st.median(ratio_o) if ratio_o else 0:.2f}, "
          f"under-predicted {100*under_o/len(rs):3.0f}%) | tank pred {st.mean(tank):6.0f} (lost/tank median {st.median(ratio_t) if ratio_t else 0:.2f}, "
          f"under {100*under_t/len(rs):3.0f}%) | old pred > hp at start {100*over_hp/len(rs):.0f}%")
done = [r for r in rows if r['end'] == 'cleared' and r['gstr'] > 0]
summ(done, 'cleared, monsters')
for n in (1, 2, 3):
    summ([r for r in done if r['n'] == n], f'  cleared, n max={n}')
summ([r for r in done if r['n'] >= 4], '  cleared, n max>=4')
for lo, hi in ((0, 1000), (1000, 2000), (2000, 3000), (3000, 99999)):
    summ([r for r in done if lo <= r['ghp'] < hi], f'  cleared, camp hp {lo}-{hi}')
for e in ('died', 'left', 'switched'):
    rs = [r for r in rows if r['end'] == e and r['gstr'] > 0]
    summ(rs, e)
died = [r for r in rows if r['end'] == 'died' and r['gstr'] > 0]
print('deaths in camp fights:', len(died), ' of which the old model predicted < hp at start:', sum(r['old'] < r['hp0'] for r in died),
      ' tank model predicted < hp at start:', sum(r['tank'] < r['hp0'] for r in died))

# The front champion: champions of one squad on one camp kill share (game, group) and overlapping rounds.
# Take the one that lost the most hp and compare with what the model predicted for it.
from collections import defaultdict
fights = defaultdict(list)
for r in rows:
    if r['gstr'] <= 0: continue
    fights[(r['map'], r['g'])].append(r)
front = []
for k, rs in fights.items():
    rs.sort(key=lambda r: r['r'] if isinstance(r['r'], float) else 0)
    cur = []
    for r in rs:
        if cur and r['r'] > max(c['r'] + c['rounds'] for c in cur) + 2:
            front.append(cur); cur = []
        cur.append(r)
    if cur: front.append(cur)
print()
print('squads (camp fights by one or more champions):', len(front))
def row(lbl, sq):
    if not sq: return
    tops = [max(s, key=lambda r: r['lost']) for s in sq]
    share = [t['lost'] / max(1, sum(r['lost'] for r in s)) for t, s in zip(tops, sq)]
    print(f"{lbl:22s} n={len(sq):5d} front lost avg {st.mean(t['lost'] for t in tops):5.0f} | its old pred {st.mean(t['old'] for t in tops):5.0f} "
          f"(front lost > old pred in {100*sum(t['lost'] > t['old']*1.1+10 for t in tops)/len(tops):3.0f}%) | tank pred {st.mean(t['tank'] for t in tops):5.0f} "
          f"(> tank in {100*sum(t['lost'] > t['tank']*1.1+10 for t in tops)/len(tops):3.0f}%) | front's share of the squad's damage {100*st.mean(share):3.0f}% "
          f"| front died {100*sum(t['end']=='died' for t in tops)/len(tops):3.0f}%")
for n in (1, 2, 3, 4):
    row(f'squad of {n}' + ('+' if n == 4 else ''), [s for s in front if (len(s) == n if n < 4 else len(s) >= 4)])
row('all', front)

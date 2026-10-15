"""cmp_games.py <dirA> <dirB> [labA labB]: per-game metrics (q5_rows.json of both batches) per map: mean +- se for usA, usB, oppA, oppB and z = (usA-usB)/sqrt(seA^2+seB^2). Flags |z|>=2."""
import sys, json, statistics as st, math, collections, os
A, B = sys.argv[1], sys.argv[2]; LA, LB = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ('27', '26')
RA = json.load(open(os.path.join(A, 'q5_rows.json'))); RB = json.load(open(os.path.join(B, 'q5_rows.json')))
M = ['own', 'mid', 'en', 'depth', 'pd', 'alone', 'idle', 'spawn', 'camp', 'fight', 'trib', 'deaths', 'caps', 'cap_own', 'cap_mid', 'cap_en', 'gpr']
def ms(v):
    if not v: return (0, 0)
    return (st.mean(v), (st.stdev(v)/math.sqrt(len(v))) if len(v) > 1 else 0)
def fmt(m, s): return '%.1f±%.1f' % (m, s)
print('| map | metric | us%s | us%s | z | opp%s | opp%s |' % (LA, LB, LA, LB)); print('|---|---|---|---|---|---|---|')
FLAG = []
for mapn in ['ALL'] + sorted(set(d['map'] for d in RA + RB)):
    La = [d for d in RA if mapn == 'ALL' or d['map'] == mapn]; Lb = [d for d in RB if mapn == 'ALL' or d['map'] == mapn]
    for k in M:
        ua = ms([d['us'][k] for d in La]); ub = ms([d['us'][k] for d in Lb]); oa = ms([d['opp'][k] for d in La]); ob = ms([d['opp'][k] for d in Lb])
        se = math.sqrt(ua[1]**2 + ub[1]**2); z = (ua[0]-ub[0])/se if se > 0 else 0
        mark = ' **' if abs(z) >= 2 else ''
        print('| %s (%d/%d) | %s | %s | %s | %+.1f%s | %s | %s |' % (mapn, len(La), len(Lb), k, fmt(*ua), fmt(*ub), z, mark, fmt(*oa), fmt(*ob)))
        if abs(z) >= 2: FLAG.append((mapn, k, ua[0], ub[0], z, len(La), len(Lb)))
print('\n## flagged |z|>=2 (map, metric, usA, usB, z, nA, nB)')
for f in FLAG: print(f)
print('\n## win/loss per map')
for mapn in sorted(set(d['map'] for d in RA + RB)):
    La = [d for d in RA if d['map'] == mapn]; Lb = [d for d in RB if d['map'] == mapn]
    print('| %s | %s: %d-%d | %s: %d-%d |' % (mapn, LA, sum(d['res'] == 'win' for d in La), sum(d['res'] == 'loss' for d in La), LB, sum(d['res'] == 'win' for d in Lb), sum(d['res'] == 'loss' for d in Lb)))

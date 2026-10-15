"""Q10: is our opening a fixed script? distinct position sets at r10/r20/r30 per map, us vs opp; plus rows: gems carried at game end and uncaptured."""
import sys, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
POS = collections.defaultdict(lambda: collections.defaultdict(set)); N = collections.Counter(); ROWS = []
for rec, g in games():
    N[rec['map']] += 1
    for r in (10, 20, 30, 40):
        if r not in g.rounds: continue
        for who, t in (('us', g.us), ('opp', g.them)):
            key = tuple(sorted((c['ty'], mirror(g.mp, c['x'], c['y']) if (t == 1) else (c['x'], c['y'])) for c in g.rounds[r].values() if c['team'] == t))
            POS[(rec['map'], who, r)][key].add(rec['match'][:8])
    if rec['map'] == 'rows':
        last = g.rounds[g.order[-1]]
        ROWS.append((rec['match'][:8], rec['res'], rec['score'], rec['oscore'], rec['rounds'], sum(c['gems'] for c in last.values() if c['team'] == g.us), sum(c['gems'] for c in last.values() if c['team'] != g.us)))
print('## distinct position patterns (type+tile, mirrored to side A frame) at rounds 10/20/30/40, per map: us vs opp (number of distinct patterns / games)')
print('| map | games | us r10 | us r20 | us r30 | us r40 | opp r10 | opp r20 | opp r30 | opp r40 |'); print('|---'*10 + '|')
for m in sorted(N):
    print('| %s | %d | %s | %s |' % (m, N[m], ' | '.join(str(len(POS[(m, 'us', r)])) for r in (10, 20, 30, 40)), ' | '.join(str(len(POS[(m, 'opp', r)])) for r in (10, 20, 30, 40))))
print('\n## rows: gems still carried at game end (us / opp)')
for x in sorted(ROWS, key=lambda x: x[1]): print(x)

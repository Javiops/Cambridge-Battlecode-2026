"""Q15 rows: per game, round of the 16th capture (=1056 if all tributed) for us and the opponent, our last tribute round, gems carried at the end, score, and
the latency of the last captures; also captures per 50-round bin for both."""
import sys, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
print('| match | opp | rank | res | score | rounds | us caps (r of 16th) | opp caps (r of 16th) | us last tribute r | us gems carried at end | us earned (score+carried) | us caps by 100r | opp caps by 100r |')
print('|---'*13 + '|')
for rec, g in games():
    if rec['map'] != 'rows': continue
    caps = {'us': [], 'opp': []}
    for r, i, gm in g.caps: caps['us' if g.types[i][0] == g.us else 'opp'].append(r)
    last_trib = max([r for r in g.order for e in g.events[r] if e['ak'] == 1 and e['k'] == 18 and g.types[e['a']][0] == g.us], default=None)
    last = g.rounds[g.order[-1]]; carried = sum(c['gems'] for c in last.values() if c['team'] == g.us)
    def r16(L): return sorted(L)[15] if len(L) >= 16 else '-'
    def bins(L): return '/'.join(str(sum(1 for r in L if 100*k <= r < 100*k+100)) for k in range(5))
    print('| %s | %s | %d | %s | %d-%d | %d | %d (%s) | %d (%s) | %s | %d | %d | %s | %s |' % (rec['match'][:8], rec['opp'][:12], rec['orank'], rec['res'], rec['score'], rec['oscore'], rec['rounds'], len(caps['us']), r16(caps['us']), len(caps['opp']), r16(caps['opp']), last_trib, carried, rec['score']+carried, bins(caps['us']), bins(caps['opp'])))

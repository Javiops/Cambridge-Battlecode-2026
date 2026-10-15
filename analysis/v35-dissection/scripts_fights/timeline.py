"""timeline.py <match-prefix> <r0> <r1>: round-by-round positions/hp/actions of all champions within 10 of the action."""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_fights')
from common import *
pre, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rec = [r for r in selected() if r['match'].startswith(pre)][0]
g = load_game(rec); usi = g.us
print(rec['map'], rec['match'][:8], 'vs', rec['opp'], '(rank %d)' % rec['orank'], rec['res'], '| we are team', usi)
for rr in [x for x in g.order if r0 <= x <= r1]:
    s = g.rounds[rr]
    cells = []
    for i in sorted(s):
        c = s[i]
        if not c['alive']: continue
        foes = [e for e in s.values() if e['team'] != c['team'] and e['alive']]
        d = min((cheb((e['x'], e['y']), (c['x'], c['y'])) for e in foes), default=99)
        if d > 10: continue
        acts = ','.join(g.acts[i].get(rr, [])) or '-'
        if rr in g.recall_start[i]: acts += ',RECALL'
        if rr in g.tribute_start[i]: acts += ',TRIB'
        dealt = g.dealt[i].get(rr, 0); taken = g.taken[i].get(rr, 0)
        cells.append('%s%s%d@%d,%d hp%d%%%s%s %s d%d' % ('*' if c['team'] == usi else ' ', c['ty'][:4], i, c['x'], c['y'], round(100*c['hp']/c['mhp']), ' +%d' % dealt if dealt else '', ' -%d' % taken if taken else '', acts, d))
    print('r%d: ' % rr + ' | '.join(cells))

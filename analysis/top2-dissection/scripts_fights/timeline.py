"""Print a round-by-round timeline of one fight: timeline.py <match-prefix> <team mite|uni> <r0> <r1>"""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_fights')
from common import *
pref, team, r0, r1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rec = [r for r in selected() if r['match'].startswith(pref) and r['team'] == team][0]
g = load_game(rec); us = g.us
print(rec['map'], rec['match'], team, 'is team', us, 'vs', rec['opp'], rec['res'])
for rr in [x for x in g.order if r0 <= x <= r1]:
    s = g.rounds[rr]
    live = [c for c in s.values() if c['alive']]
    def near(c): return min([cheb((e['x'], e['y']), (c['x'], c['y'])) for e in live if e['team'] != c['team']], default=99)
    show = [c for c in live if near(c) <= 9]
    if not show: continue
    parts = []
    for t in (us, 1-us):
        for c in sorted(show, key=lambda c: c['i']):
            if c['team'] != t: continue
            acts = g.acts[c['i']].get(rr, [])
            a = '/'.join(acts) if acts else '-'
            dd = g.dealt[c['i']].get(rr, 0); tk = g.taken[c['i']].get(rr, 0)
            rc = 'REC' if rr in g.recall_start[c['i']] else ('ARR' if rr in g.recall_arrive[c['i']] else '')
            parts.append('%s%s(%d,%d)%d%%d%d %s%s%s%s' % ('*' if t == us else '', c['ty'][:4], c['x'], c['y'], round(100*c['hp']/c['mhp']), near(c), a, ('+%d' % dd) if dd else '', ('-%d' % tk) if tk else '', rc))
    dead = [c['ty'][:4] for c in s.values() if not c['alive'] and any(d[0] == rr and d[1] == c['i'] for d in g.deaths)]
    print('r%-4d %s %s' % (rr, ' | '.join(parts), ('DEAD:' + ','.join(dead)) if dead else ''))

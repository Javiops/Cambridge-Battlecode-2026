"""Q6: do the teams open identically on the same map? First round where the mirrored champion positions differ between games."""
import sys, json, collections, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_opening')
from openlib import *
UP = 80
games = collections.defaultdict(list)
for rec in SEL: games[(rec['map'], rec['team'])].append(rec)
def canon(g, team, r):
    """sorted tuple of (type, canonical pos) for team's champs at round r (mirrored to side A frame)"""
    out = []
    for i in g.champs[team]:
        c = g.rounds[r]['champs'][i]
        p = (c['x'], c['y'])
        if team == 1: p = g.map.mirror(p)
        out.append((g.types[i][1], p if c['alive'] else None))
    return tuple(sorted(out, key=lambda x: (x[0], str(x[1]))))
def enemy_near(g, team, r, R=8):
    best = 99
    for i in g.champs[team]:
        c = g.rounds[r]['champs'][i]
        if not c['alive']: continue
        for j in g.champs[1-team]:
            e = g.rounds[r]['champs'][j]
            if e['alive']: best = min(best, cheb((c['x'], c['y']), (e['x'], e['y'])))
    return best
for key in sorted(games):
    recs = games[key]
    loaded = []
    for rec in recs:
        g = Game(rec['match']); team = 0 if rec['side'] == 'a' else 1
        loaded.append((rec, g, team))
    print('=== %s %s' % key)
    drafts = [tuple(sorted(g.types[i][1] for i in g.champs[t])) for _, g, t in loaded]
    base = loaded[0]
    for (rec, g, team) in loaded:
        d = tuple(sorted(g.types[i][1] for i in g.champs[team]))
        same_draft = d == drafts[0]
        div = None
        if same_draft and rec is not base[0]:
            for r in range(1, UP+1):
                if r not in g.rounds or r not in base[1].rounds: break
                if canon(g, team, r) != canon(base[1], base[2], r): div = r; break
        # enemy proximity at divergence
        en = enemy_near(g, team, div) if div else None
        en_b = enemy_near(base[1], base[2], div) if div else None
        print('  %s side %s vs %-16s draft %-30s first_divergence_vs_game1=%s  nearest_enemy_at_div: this=%s base=%s' % (
            rec['match'][:8], rec['side'], rec['opp'][:16], ','.join(x[:4] for x in d), div if rec is not base[0] else '(base)', en, en_b))

"""Per-champion compact timelines (rounds 1-60) for representative games."""
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_opening')
from openlib import *
UP = int(sys.argv[1]) if len(sys.argv) > 1 else 60
picks = {}   # map -> list of match prefixes
for rec in SEL:
    picks.setdefault(rec['map'], {}).setdefault(rec['team'], []).append(rec)
out = []
for m in ['rows', 'expanse', 'lanes', 'monolith', 'packs', 'collision', 'corners', 'elkring', 'interlock']:
    chosen = []
    both = [r for r in picks[m]['mite'] if r['opp'].startswith('Univardisty')]
    if both: chosen.append((both[0]['match'], 'mite+uni'))
    for t in ('mite', 'uni'):
        others = [r for r in picks[m][t] if not (r['opp'].startswith('Univardisty') or r['opp'] == 'Mite')]
        chosen.append((others[0]['match'], t))
        if t == 'uni' and len(others) > 1 and not both: chosen.append((others[1]['match'], t))
    for match, which in chosen:
        g = Game(match)
        out.append('\n### %s  match %s  (%s)' % (m, match, ' vs '.join('%s=%s' % ('AB'[t], g.teams.get(t, BYMATCH[match][0]['opp'])) for t in (0, 1))))
        for team in (0, 1):
            tn = g.teams.get(team)
            if tn not in ('mite', 'uni'): continue
            if which != 'mite+uni' and tn != which: continue
            tl, an = g.timeline(team, UP)
            out.append('**%s (team %s, side %s)**  result %s' % (tn, team, 'ab'[team], [r['res'] for r in BYMATCH[match] if r['team'] == tn][0]))
            for i, runs in tl.items():
                out.append('- ' + fmt_runs(g, i, runs, team))
            ks = [k for k in an['keys'] if k[1] in ('capture', 'tribute_start', 'tribute_done', 'recall_start', 'death', 'buy') and k[0] <= UP]
            out.append('- events: ' + '; '.join('r%d %s %s%s' % (k[0], k[1], g.name(k[2]['i']), (' %s' % k[2].get('gems', k[2].get('bag', k[2].get('gold', '')))) ) for k in ks))
open(S + '/reports/scripts_opening/timelines.md', 'w').write('\n'.join(out))
print(len(out))

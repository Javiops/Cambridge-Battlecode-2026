"""Condensed timelines (no coordinates, short walk/idle runs merged) for the report."""
import sys, re, json
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_opening')
from openlib import *
UP = 60
def short_runs(g, i, runs, team):
    # merge: walk/idle/spawn -> 'walk'; consecutive same-camp runs separated by 1-2 round walks -> one camp run
    seq = []
    for r0, lab, r1, p0, p1, gems in runs:
        l = lab
        if lab in ('idle', 'spawn'): l = 'walk'
        if lab.startswith('camp'):
            gi = int(lab[4:]); info = g.ginfo[gi]
            l = 'camp g%d %s(%s,d%d)' % (gi, '+'.join(t[:4] for t in info['types']), M_side(g, team, info), info['dA'] if team == 0 else info['dB'])
        if seq and seq[-1][0] == l: seq[-1][2] = r1; continue
        if seq and len(seq) >= 2 and l.startswith('camp') and seq[-2][0] == l and seq[-1][0] == 'walk' and seq[-1][2] - seq[-1][1] <= 1:
            seq.pop(); seq[-1][2] = r1; continue
        seq.append([l, r0, r1])
    # drop walk runs shorter than 3 rounds between other activities (keep the first walk)
    out = []
    for k, (l, r0, r1) in enumerate(seq):
        if l == 'walk' and k > 0 and r1 - r0 < 2 and k < len(seq) - 1: continue
        out.append('%s r%d-%d' % (l, r0, r1) if r1 > r0 else '%s r%d' % (l, r0))
    return '%s: ' % g.name(i) + ' > '.join(out)
def M_side(g, team, info): return g.map.side_of(team, info['side'])
picks = {}
for rec in SEL: picks.setdefault(rec['map'], {}).setdefault(rec['team'], []).append(rec)
out = []
for m in ['rows', 'expanse', 'lanes', 'monolith', 'packs', 'collision', 'corners', 'elkring', 'interlock']:
    chosen = []
    both = [r for r in picks[m]['mite'] if r['opp'].startswith('Univardisty')]
    if both: chosen.append((both[0]['match'], 'mite+uni'))
    for t in ('mite', 'uni'):
        others = [r for r in picks[m][t] if not (r['opp'].startswith('Univardisty') or r['opp'] == 'Mite')]
        chosen.append((others[0]['match'], t))
    out.append('\n#### %s' % m)
    for match, which in chosen:
        g = Game(match)
        for team in (0, 1):
            tn = g.teams.get(team)
            if tn not in ('mite', 'uni') or (which != 'mite+uni' and tn != which): continue
            tl, an = g.timeline(team, UP)
            res = [r['res'] for r in BYMATCH[match] if r['team'] == tn][0]
            out.append('**%s** (side %s) vs %s, match `%s`, %s:' % (tn, 'ab'[team], g.teams.get(1-team, BYMATCH[match][0]['opp']), match[:8], res))
            for i, runs in tl.items(): out.append('- ' + short_runs(g, i, runs, team))
            ks = [k for k in an['keys'] if k[1] in ('capture', 'tribute_start', 'recall_start', 'death') and k[0] <= UP]
            out.append('- key events: ' + '; '.join('r%d %s %s%s' % (k[0], k[1].replace('_start', ''), g.name(k[2]['i']), (' %s' % k[2]['gems']) if 'gems' in k[2] else ((' %s' % k[2]['bag']) if 'bag' in k[2] else '')) for k in ks))
open(S + '/reports/scripts_opening/timelines_short.md', 'w').write('\n'.join(out))
print(len('\n'.join(out)))

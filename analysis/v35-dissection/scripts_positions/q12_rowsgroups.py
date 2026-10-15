"""Q12 rows: per-group latency (respawn->capture) by group, camp hits on monolith/gold groups, and a per-group timeline of one loss."""
import sys, os, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
LAT = collections.defaultdict(list); HITS = collections.Counter(); TL = {}
for rec, g in games():
    if rec['map'] != 'rows': continue
    campgrp = {k['i']: k['grp'] for k in g.camps[0].values()}
    spawn_r = {gi: 0 for gi in g.gtiles}; prev = None; tl = collections.defaultdict(list)
    for r in g.order:
        cur = {}
        for k in g.camps[r].values(): cur[k['grp']] = cur.get(k['grp'], False) or bool(k['alive'])
        if prev is not None:
            for gi in cur:
                if cur[gi] and not prev.get(gi, True): spawn_r[gi] = r; tl[gi].append(('spawn', r))
        prev = cur
        for e in g.events[r]:
            if e['ak'] == 1 and e['keff']:
                for x in e['keff']:
                    if x.get('hp', 0) < 0:
                        gi = campgrp.get(x['i']); who = 'us' if g.types[e['a']][0] == g.us else 'opp'
                        HITS[(who, g.gterr[gi][g.us if who == 'us' else g.them], g.gtiles[gi] and sorted(g.gtiles[gi])[0])] += 1
        for (rr, i, gm) in [c for c in g.caps if c[0] == r]:
            who = 'us' if g.types[i][0] == g.us else 'opp'
            c = g.rounds[r].get(i)
            if c['x'] < 0: c = g.rounds[g.order[g.ridx[r]-1]][i]
            gi = g.camptiles.get((c['x'], c['y']))
            if gi is None: gi = min(g.gtiles, key=lambda gg: min(cheb((c['x'], c['y']), q) for q in g.gtiles[gg]))
            tile = sorted(g.gtiles[gi])[0]
            # normalise group by its mirrored tile for opp
            key = tile if who == 'us' else mirror(g.mp, *tile)
            LAT[(who, key)].append(r - spawn_r[gi]); tl[gi].append(('cap_' + who, r, r - spawn_r[gi]))
    if any(rec['match'].startswith(x) for x in os.environ.get('TL_MATCHES', '604a6cf6,c3eed638').split(',')): TL[rec['match'][:8]] = (rec, tl, g)
print('## rows: respawn->capture latency by group (group named by its team-A-frame tile), us vs opp: n, median, mean, max')
for key in sorted(set(k[1] for k in LAT)):
    a = LAT[('us', key)]; b = LAT[('opp', key)]
    print('| %s | us n=%d med %d mean %.1f max %d | opp n=%d med %d mean %.1f max %d |' % (key, len(a), st.median(a) if a else 0, st.mean(a) if a else 0, max(a) if a else 0, len(b), st.median(b) if b else 0, st.mean(b) if b else 0, max(b) if b else 0))
print('\n## camp hits by (who, territory, group tile)'); 
for k, v in sorted(HITS.items()): print(k, v)
for m, (rec, tl, g) in TL.items():
    print('\n## timeline', m, rec['res'], rec['score'], rec['oscore'], rec['rounds'])
    for gi in sorted(tl): print(gi, sorted(g.gtiles[gi])[0], g.gterr[gi][g.us], tl[gi])

"""Q9: opening fight (deaths before r100) vs result; numbers at contact: for each round where an enemy is within 8 of one of ours, local counts (ours vs theirs within 8 of that champion); outnumbered share, ours vs theirs; deaths when outnumbered."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
OP = []; LOCAL = collections.defaultdict(collections.Counter); DL = collections.defaultdict(collections.Counter)
for rec, g in games():
    du = sum(1 for r, i in g.deaths if g.types[i][0] == g.us and r < 100); do = sum(1 for r, i in g.deaths if g.types[i][0] != g.us and r < 100)
    fd = min([r for r, i in g.deaths], default=None)
    OP.append((rec['map'], rec['res'], du, do, fd, rec['match'][:8], rec['opp'][:10]))
    keys = split_keys(rec)
    deathr = {(r, i) for r, i in g.deaths}
    for r in g.order[1:]:
        if r % 2: continue
        sn = g.rounds[r]
        al = [c for c in sn.values() if c['alive']]
        for c in al:
            who = 'us' if c['team'] == g.us else 'opp'
            ens = [e for e in al if e['team'] != c['team'] and cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8]
            if not ens: continue
            mine = 1 + sum(1 for o in al if o['team'] == c['team'] and o is not c and cheb((c['x'], c['y']), (o['x'], o['y'])) <= 8)
            k = 'out' if mine < len(ens) else ('even' if mine == len(ens) else 'up')
            for kk in keys: LOCAL[(kk, who)][k] += 1; LOCAL[(kk, who)]['n'] += 1
    for r, i in g.deaths:
        pr = g.order[g.ridx[r]-1]; sn = g.rounds[pr]; c = sn[i]; who = 'us' if g.types[i][0] == g.us else 'opp'
        al = [x for x in sn.values() if x['alive']]
        ens = sum(1 for e in al if e['team'] != c['team'] and cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8)
        mine = 1 + sum(1 for o in al if o['team'] == c['team'] and o['i'] != i and cheb((c['x'], c['y']), (o['x'], o['y'])) <= 8)
        k = 'out' if mine < ens else ('even' if mine == ens else 'up')
        for kk in keys: DL[(kk, who)][k] += 1; DL[(kk, who)]['n'] += 1
print('## opening: deaths before round 100 (us / opp) vs result, per map')
print('| map | games | our deaths <r100 (W / L) | their deaths <r100 (W / L) | win% when we lose more champions before r100 | win% when we lose fewer | win% when equal |'); print('|---|---|---|---|---|---|---|')
for m in ['ALL'] + sorted(set(o[0] for o in OP)):
    L = [o for o in OP if m == 'ALL' or o[0] == m]; W = [o for o in L if o[1] == 'win']; Lo = [o for o in L if o[1] == 'loss']
    def wr(sel): return ('%d%% (n=%d)' % (100*sum(o[1] == 'win' for o in sel)/len(sel), len(sel))) if sel else '-'
    print('| %s | %d | %.1f / %.1f | %.1f / %.1f | %s | %s | %s |' % (m, len(L), st.mean([o[2] for o in W]) if W else 0, st.mean([o[2] for o in Lo]) if Lo else 0, st.mean([o[3] for o in W]) if W else 0, st.mean([o[3] for o in Lo]) if Lo else 0, wr([o for o in L if o[2] > o[3]]), wr([o for o in L if o[2] < o[3]]), wr([o for o in L if o[2] == o[3]])))
print('\n## local numbers when an enemy is within 8 (every 2nd round): share of champion-rounds outnumbered / even / outnumbering (allies within 8 of the champion, incl. itself, vs enemies within 8)')
print('| split | who | champ-rounds | outnumbered | even | outnumbering | deaths n | deaths while outnumbered | even | outnumbering |'); print('|---'*10 + '|')
for k in ['ALL', 'res:win', 'res:loss', 'opp:top10', 'opp:r11-30'] + sorted(set(x[0] for x in LOCAL if x[0].startswith('map:'))):
    for who in ('us', 'opp'):
        a = LOCAL[(k, who)]; n = a['n'] or 1; d = DL[(k, who)]; dn = d['n'] or 1
        if a['n'] < 100: continue
        print('| %s | %s | %d | %d%% | %d%% | %d%% | %d | %d%% | %d%% | %d%% |' % (k, who, a['n'], 100*a['out']/n, 100*a['even']/n, 100*a['up']/n, d['n'], 100*d['out']/dn, 100*d['even']/dn, 100*d['up']/dn))

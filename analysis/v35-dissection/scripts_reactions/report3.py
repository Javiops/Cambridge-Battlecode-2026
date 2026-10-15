"""Q6: 10 worst games by gems lost to our deaths, with round-by-round data of the deciding deaths."""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_reactions')
from common import *
R = json.load(open(W + '/scripts_reactions/rows.json'))
sel = load_sel(); byid = {s['match']: s for s in sel}
D = [d for d in R['deaths'] if d['us']]
lost = collections.Counter()
for d in D: lost[d['match']] += d['gems']
top = lost.most_common(10)
print('## Q6. The 10 worst games by gems lost to our deaths\n')
print('| # | match | map | opponent (rank) | result | score us-opp | our deaths | gems lost | opp deaths / gems lost | biggest losses (type r round gems) |')
print('|---|---|---|---|---|---|---|---|---|---|')
for k, (m, g) in enumerate(top, 1):
    s = byid[m]; X = [d for d in D if d['match'] == m]; O = [d for d in R['deaths'] if d['match'] == m and not d['us']]
    big = sorted(X, key=lambda d: -d['gems'])[:4]
    print('| %d | %s | %s | %s (%d) | %s | %d-%d | %d | %d | %d / %d | %s |' % (k, m[:8], s['map'], s['opp'], s['orank'], s['res'], s['score'], s['oscore'], len(X), g, len(O), sum(d['gems'] for d in O), ', '.join('%s r%d %dg%s' % (d['ty'], d['r'], d['gems'], ' (pair)' if d['pair'] else '') for d in big)))
print()
NARR = int(sys.argv[1]) if len(sys.argv) > 1 else 2
for k, (m, g) in enumerate(top, 1):
    s = byid[m]; G = Game(s); side = G.side
    X = sorted([d for d in D if d['match'] == m and not d['pair']], key=lambda d: -d['gems'])[:NARR]
    print('### %d. %s %s vs %s (%s %d-%d): %d gems lost\n' % (k, m[:8], s['map'], s['opp'], s['res'], s['score'], s['oscore'], g))
    for d in X:
        i = d['i']; r0 = d['r0']; rd = d['r']
        print('**%s (idx %d) dies r%d with %d gems, killer %s; doing before: %s; first hit at r%d with hp %d%%; zone %s, %d from own spawn, %d from altar; allies within 6 at death: %d.**\n' % (d['ty'], i, rd, d['gems'], d['killer'], d['before'], r0, d['hp_first'], d['zone'], d['dspawn'], d['daltar'], d['allies6']))
        print('| round | pos | hp% | gems | action | dmg taken (source) | nearest foe (dist) | foes within 8 | allies within 6 (dist) | recall/tribute |')
        print('|---|---|---|---|---|---|---|---|---|---|')
        for r in range(max(1, r0 - 4), rd + 1):
            if r not in G.rounds: continue
            pr = r - 1
            if not G.alive(pr, i): continue
            p = G.pos(r, i) if G.alive(r, i) else G.pos(pr, i)
            hp = G.hpp(r, i) if G.alive(r, i) else 0
            dm = G.dmg[r][i]; dms = ', '.join('%d %s%s' % (v, 'camp' if sidx == 'camp' else G.ty(sidx), '' if kk == 'camp' else ('/sp' if kk == 'spell' else '/atk')) for sidx, v, kk in dm)
            nf = G.nearest_foe(pr, i); nfs = '%s %d' % (G.ty(nf[1]), nf[0]) if nf[1] is not None else '-'
            f8 = sum(1 for f in G.foes(pr, i) if cheb(G.pos(pr, i), (f['x'], f['y'])) <= 8)
            al = sorted((cheb(G.pos(pr, i), (a['x'], a['y'])), G.ty(a['i'])) for a in G.allies(pr, i) if cheb(G.pos(pr, i), (a['x'], a['y'])) <= 6)
            ch = ('recall(r%d)' % G.recall_active(r, i)) if G.recall_active(r, i) is not None else (('tribute(r%d)' % G.tribute_active(r, i)) if G.tribute_active(r, i) is not None else '')
            if r in G.recall_start[i]: ch = 'RECALL START'
            if r in G.tribute_start[i]: ch = 'TRIBUTE START'
            cl = G.classify(r, i) if G.alive(r, i) else 'DEAD'
            a = G.act[r][i]
            print('| %d | %d,%d | %d | %d | %s %s | %s | %s | %d | %s | %s |' % (r, p[0], p[1], hp, G.rounds[pr][i]['gems'], cl, '(' + ','.join(sorted(a)) + ')' if a else '', dms, nfs, f8, ' '.join('%s@%d' % (t, dd) for dd, t in al), ch))
        print()

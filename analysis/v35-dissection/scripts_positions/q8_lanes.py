"""Q8 lanes: lane allocation per round (top y<=8, mid 9..20, bottom y>=21) on our side (x<45 for side a) : our count vs enemy count; max enemy stack in one lane on our side and our count in that lane."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
def lane(y): return 'top' if y <= 8 else ('bot' if y >= 21 else 'mid')
ALLOC = collections.defaultdict(collections.Counter); STACK = collections.defaultdict(list); PG = []
for rec, g in games():
    if rec['map'] != 'lanes': continue
    ourside = (lambda x: x < 45) if g.us == 0 else (lambda x: x > 44)
    theirside = (lambda x: x > 44) if g.us == 0 else (lambda x: x < 45)
    n = 0; cnt = collections.Counter(); stacks = []; respond = []
    for r in g.order[1:]:
        if r > 350: break
        sn = g.rounds[r]; b = 0 if r < 100 else (1 if r < 250 else 2)
        mine = [c for c in sn.values() if c['team'] == g.us and c['alive']]
        ens = [c for c in sn.values() if c['team'] != g.us and c['alive']]
        for c in mine: ALLOC[('us', b)][lane(c['y']) + ('_our' if ourside(c['x']) else ('_their' if theirside(c['x']) else '_mid'))] += 1; ALLOC[('us', b)]['n'] += 1
        for c in ens: ALLOC[('opp', b)][lane(c['y']) + ('_their' if ourside(c['x']) else ('_our' if theirside(c['x']) else '_mid'))] += 1; ALLOC[('opp', b)]['n'] += 1
        # enemy stacks on our side by lane
        for L in ('top', 'bot'):
            es = [c for c in ens if ourside(c['x']) and lane(c['y']) == L]
            if es:
                ms = [c for c in mine if lane(c['y']) == L and ourside(c['x'])]
                near = [c for c in mine if any(cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8 for e in es)]
                STACK[('inv', len(es))].append(len(ms)); stacks.append((r, L, len(es), len(ms), len(near)))
                ALLOC[('inv', rec['res'])]['rounds'] += 1
                ALLOC[('inv', rec['res'])]['enemy>=3'] += len(es) >= 3
                ALLOC[('inv', rec['res'])]['we_outnumbered_in_lane'] += len(ms) < len(es)
                ALLOC[('inv', rec['res'])]['nobody_near'] += len(near) == 0
    inv = [s for s in stacks]
    PG.append((rec['match'][:8], rec['res'], rec['opp'][:10], rec['orank'], len(inv), sum(1 for s in inv if s[2] >= 3), sum(1 for s in inv if s[3] < s[2]), sum(1 for s in inv if s[4] == 0)))
print('## lanes (18 games, rounds 1-350): share of alive champion-rounds by lane x side. side = our half / their half / middle (x 45..44)')
print('| who | phase | top our/mid/their | mid-lane our/mid/their | bottom our/mid/their |'); print('|---|---|---|---|---|')
for who in ('us', 'opp'):
    for b, nm in enumerate(('1-99', '100-249', '250-350')):
        a = ALLOC[(who, b)]; n = a['n'] or 1
        print('| %s | %s | %d/%d/%d | %d/%d/%d | %d/%d/%d |' % (who, nm, *(round(100*a[L+'_'+s]/n) for L in ('top', 'mid', 'bot') for s in ('our', 'mid', 'their'))))
print('\n## rounds with enemy champions in one of OUR lanes (top or bottom, our side of x=45): our champions in that lane vs invaders')
print('| invaders in lane | rounds | mean ours in lane | ours < invaders | ours = 0 |'); print('|---|---|---|---|---|')
for k in sorted(STACK):
    L = STACK[k]; print('| %d | %d | %.2f | %d%% | %d%% |' % (k[1], len(L), st.mean(L), 100*sum(1 for x in L if x < k[1])/len(L), 100*sum(1 for x in L if x == 0)/len(L)))
for res in ('win', 'loss'):
    a = ALLOC[('inv', res)]; n = a['rounds'] or 1
    print('%s: lane-invasion rounds %d, invaders>=3 %d%%, we outnumbered in lane %d%%, none of ours within 8 of them %d%%' % (res, a['rounds'], 100*a['enemy>=3']/n, 100*a['we_outnumbered_in_lane']/n, 100*a['nobody_near']/n))
print('\nper game (match,res,opp,rank, invasion lane-rounds, with >=3 invaders, we outnumbered, nobody near)')
for p in sorted(PG, key=lambda p: p[1]): print(p)

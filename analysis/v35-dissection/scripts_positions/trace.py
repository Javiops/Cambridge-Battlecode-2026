"""trace.py <match prefix> [step] [r0 r1]: round-by-round compact description of a game (positions, territory, actions, score, deaths, captures)."""
import sys, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
pre = sys.argv[1]; step = int(sys.argv[2]) if len(sys.argv) > 2 else 10
r0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0; r1 = int(sys.argv[4]) if len(sys.argv) > 4 else 9999
rec = next(r for r in SEL if r['match'].startswith(pre)); g = load_game(rec); mp = g.mp
print('match', rec['match'], rec['map'], 'vs', rec['opp'], 'rank', rec['orank'], rec['res'], rec['score'], '-', rec['oscore'], 'rounds', rec['rounds'], 'us side', rec['side'], 'draft', rec['draft'], 'odraft', rec['odraft'])
print('spawn us', mp['sp'][g.us][0], 'them', mp['sp'][g.them][0], 'altars', mp['altars'])
print('groups:', {gi: (sorted(ts), 'terr(us)=' + g.gterr[gi][g.us]) for gi, ts in g.gtiles.items()})
deaths = collections.defaultdict(list)
for r, i in g.deaths: deaths[r].append(i)
caps = collections.defaultdict(list)
for r, i, gm in g.caps: caps[r].append((i, gm))
SH = {'move': 'mv', 'attack camp': 'camp', 'cast@camp': 'Ccamp', 'attack champ': 'ATK', 'cast@champ': 'CAST', 'dash': 'dash', 'ability(no eff)': 'ab', 'tribute': 'trib', 'recall': 'rec', 'buy': 'buy', 'nothing': '..', 'arrive': 'arr', 'attack(miss)': 'miss'}
for r in g.order:
    if r < r0 or r > r1: continue
    ev = [x for x in range(r-step+1, r+1) if x in deaths or x in caps]
    if r % step: continue
    sn = g.rounds[r]
    def desc(t):
        out = []
        for i in g.ids[t]:
            c = sn[i]
            if not c['alive']: out.append('%s%d:DEAD' % (c['ty'][:3], i)); continue
            lab = SH[primary(g.acts[i][r])]
            tr = terr(mp, c['x'], c['y'], t)[0]
            out.append('%s%d@%d,%d%s%s hp%d%% g%d %s' % (c['ty'][:3], i, c['x'], c['y'], tr, '!' if g.taken[i].get(r, 0) else '', 100*c['hp']//c['mhp'], c['gems'], lab))
        return ' '.join(out)
    extra = ''
    for x in range(r-step+1, r+1):
        if x in deaths: extra += ' DEATH r%d:%s' % (x, deaths[x])
        if x in caps: extra += ' CAP r%d:%s' % (x, caps[x])
    print('r%d score %s | US: %s | THEM: %s%s' % (r, g.sub[r], desc(g.us), desc(g.them), extra))

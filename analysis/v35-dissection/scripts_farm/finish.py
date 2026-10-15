import sys,os; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
B=[json.load(open(f)) for f in sorted(glob.glob(sys.argv[1]+'/*.json'))]
print('### Finish line: round at which a team banks 1000 (median over games where it happened); our finishing round in wins vs the opponents\' in losses, 27 vs 26; and our banked gems when the opponent finished (losses)\n')
def fin(g,team):
    t=g['t'] if team=='us' else 1-g['t']
    return next((r for r,s in enumerate(g['sub']) if s[t]>=1000),None)
rows=[]
for m in MAPS:
    r=[m]
    for lab,gs in (('27',[g for g in G if g['map']==m]),('26',[g for g in B if g['map']==m])):
        fu=[fin(g,'us') for g in gs if g['res']=='win']; fo=[fin(g,'opp') for g in gs if g['res']=='loss']
        short=[1000-g['sub'][-1][g['t']] for g in gs if g['res']=='loss']; carried=[sum(c['gems_end'] for c in champs(g,'us')) for g in gs if g['res']=='loss']
        r.append(f"{len(fu)}: {med([x for x in fu if x]):.0f} ; {len(fo)}: {med([x for x in fo if x]):.0f} ; short {med(short):.0f} (in hand {med(carried):.0f})")
    rows.append(r)
tbl(['map','27 wins: our 1000 round ; losses: opp 1000 round ; gems short in losses (ours in hand)','26 same'],rows)

import sys, json, collections, itertools
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
games=collections.defaultdict(list)
for rec in SEL:
    if rec['team']!='mite' or rec['map'] not in ('expanse','interlock','elkring','rows','lanes','monolith'): continue
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    def canon(x,y): return (x,y) if t==0 else mirror(mp,x,y)
    ecomp=tuple(sorted(c['ty'] for c in g.rounds[0].values() if c['team']!=t))
    track={r:sorted((c['ty'],)+canon(c['x'],c['y']) if c['alive'] else (c['ty'],-1,-1) for c in g.rounds[r].values() if c['team']==t) for r in g.order}
    games[rec['map']].append((rec,ecomp,track))
for m,L in games.items():
    print('###',m)
    for rec,ec,_ in L: print('  ',rec['opp'][:14],rec['side'],ec)
    for (ra,ea,ta),(rb,eb,tb) in itertools.combinations(L,2):
        if ra['side']!=rb['side']: continue
        fd=None
        for r in sorted(ta):
            if r in tb and ta[r]!=tb[r]: fd=r; break
        if fd is None: continue
        diff=[(x,y) for x,y in zip(ta[fd],tb[fd]) if x!=y]
        print('  pair %s/%s first diff r%d enemy comp same=%s diff=%s'%(ra['opp'][:10],rb['opp'][:10],fd,ea==eb,diff[:2]))

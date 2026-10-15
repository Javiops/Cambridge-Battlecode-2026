import sys, json, collections, statistics, itertools
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
FIGHT={'corners','interlock','elkring','packs','collision'}
games=collections.defaultdict(list)
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    # canonical positions: mirror if side b
    def canon(x,y): return (x,y) if t==0 else mirror(mp,x,y)
    track={}
    for r in g.order:
        sn=g.rounds[r]
        mine=sorted((c['ty'],)+canon(c['x'],c['y']) if c['alive'] else (c['ty'],-1,-1) for c in sn.values() if c['team']==t)
        ens=[c for c in sn.values() if c['team']!=t and c['alive']]
        mn=[c for c in sn.values() if c['team']==t and c['alive']]
        ne=min([cheb((a['x'],a['y']),(e['x'],e['y'])) for a in mn for e in ens],default=99)
        ein=sum(terr(mp,e['x'],e['y'],1-t)=='enemy' for e in ens)
        track[r]=(tuple(mine),ne,ein,[ (e['ty'],)+canon(e['x'],e['y']) for e in ens])
    deaths=collections.Counter(); kills=0
    prev=None
    for r in g.order:
        sn=g.rounds[r]
        if prev:
            for c in sn.values():
                if prev[c['i']]['alive'] and not c['alive']:
                    if c['team']==t: deaths['mine']+=1
                    else: deaths['theirs']+=1
        prev=sn
    games[(rec['team'],rec['map'])].append(dict(rec=rec,track=track,draft=tuple(rec['draft']),deaths=deaths,last=g.last))
print('## Q7 first round where the team\'s own positions differ between two games on the same map (positions mirrored to side A)')
print('| team | map | game 1 opp (side) | game 2 opp (side) | same draft | first diff round | nearest enemy at that round (g1/g2) | enemies in our half (g1/g2) | an enemy was within 8 of one of ours before/at that round (g1/g2) |')
print('|---|---|---|---|---|---|---|---|---|')
summ=collections.defaultdict(list)
for key,L in sorted(games.items()):
    for a,b in itertools.combinations(L,2):
        if a['draft']!=b['draft']:
            print('| %s | %s | %s | %s | no | 0 (draft differs) | | | |'%(key[0],key[1],a['rec']['opp'][:14]+' ('+a['rec']['side']+')',b['rec']['opp'][:14]+' ('+b['rec']['side']+')')); summ[key].append(0); continue
        fd=None
        for r in sorted(a['track']):
            if r not in b['track']: break
            if a['track'][r][0]!=b['track'][r][0]: fd=r; break
        if fd is None: print('| %s | %s | %s | %s | yes | never (%d rounds) | | | |'%(key[0],key[1],a['rec']['opp'][:14]+' ('+a['rec']['side']+')',b['rec']['opp'][:14]+' ('+b['rec']['side']+')',min(a['last'],b['last']))); continue
        # was an enemy within 8 (seen) at or before fd
        seenA=min(a['track'][r][1] for r in range(max(0,fd-3),fd+1) if r in a['track'])
        seenB=min(b['track'][r][1] for r in range(max(0,fd-3),fd+1) if r in b['track'])
        print('| %s | %s | %s | %s | yes | %d | %d / %d | %d / %d | %s / %s |'%(key[0],key[1],a['rec']['opp'][:14]+' ('+a['rec']['side']+')',b['rec']['opp'][:14]+' ('+b['rec']['side']+')',fd,a['track'][fd][1],b['track'][fd][1],a['track'][fd][2],b['track'][fd][2],'yes' if seenA<=8 else 'no','yes' if seenB<=8 else 'no'))
        summ[key].append(fd)
print()
print('## per-game summary per team/map (opponent, result, score, deaths, kills, enemy-half share)')
print('| team | map | opp | rank | side | res | score | deaths | kills | rounds | draft |')
print('|---|---|---|---|---|---|---|---|---|---|')
for key,L in sorted(games.items()):
    for a in sorted(L,key=lambda z:z['rec']['orank']):
        r=a['rec']; print('| %s | %s | %s | %d | %s | %s | %d-%d | %d | %d | %d | %s |'%(key[0],key[1],r['opp'][:16],r['orank'],r['side'],r['res'],r['score'],r['oscore'],a['deaths']['mine'],a['deaths']['theirs'],a['last'],r['draft']))
print()
print('## same-side, same-draft pairs only: first divergence round per team/map')
print('| team | map | pairs | first-diff rounds | pairs where an enemy was within 8 of one of ours in the 3 rounds before the divergence |')
print('|---|---|---|---|---|')
for key,L in sorted(games.items()):
    fds=[]; seen=0
    for a,b in itertools.combinations(L,2):
        if a['draft']!=b['draft'] or a['rec']['side']!=b['rec']['side']: continue
        fd=None
        for r in sorted(a['track']):
            if r not in b['track']: break
            if a['track'][r][0]!=b['track'][r][0]: fd=r; break
        if fd is None: fds.append('never'); continue
        fds.append(fd)
        sA=min(a['track'][r][1] for r in range(max(0,fd-3),fd+1) if r in a['track']); sB=min(b['track'][r][1] for r in range(max(0,fd-3),fd+1) if r in b['track'])
        if min(sA,sB)<=8: seen+=1
    if fds: print('| %s | %s | %d | %s | %d |'%(key[0],key[1],len(fds),' '.join(map(str,sorted(fds,key=lambda z: 10**6 if z=='never' else z))),seen))

import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
from common import Game, SEL, load_map, cheb
import math
print('## Q7 follow-ups\n')
# (a) recall classification with gold/hp at arrival, from raw snapshots
cls=collections.defaultdict(collections.Counter); cost=collections.defaultdict(float); costn=collections.Counter(); goldarr=collections.defaultdict(list); hpstart=collections.defaultdict(list)
noreason=collections.Counter(); noreason_rounds=collections.Counter()
trib_cause=collections.defaultdict(collections.Counter)
rows_legs=[]
byid={g['match']:g for g in G}
for rec in SEL:
    g=byid[rec['match']]; Gm=Game(rec); R=Gm.R; mp=Gm.map
    hits_by_round=collections.defaultdict(set)   # (i) hit by champion/monster at round r
    moved=collections.defaultdict(set)
    for r,evs in Gm.ev.items():
        for e in evs:
            for x in e.get('eff',[]):
                if x.get('hp',0)<0: hits_by_round[x['i']].add(r)
            if e['ak']==1 and e['k']==4: moved[e['a']].add(r)
    for c in g['champs']:
        i=c['i']; team=c['team']; tm=Gm.teamof[i]
        caps=sorted(c['captures'],key=lambda x:x['r']); tribs=sorted([t for t in c['tributes'] if t.get('done')],key=lambda t:t['done'])
        for rc in c['recalls']:
            if rc.get('done') is None: continue
            d=rc['done']; snap=R[d] if d in R else None
            ga=next((cc[8] for cc in snap['champs'] if cc[0]==i),0) if snap else 0
            goldarr[team].append(ga); hpstart[team].append(rc['hp']/rc['mhp'])
            buy=any(d<=b['r']<=d+3 for b in c['buys'])
            gems_at_arr=next((cc[7] for cc in snap['champs'] if cc[0]==i),0) if snap else 0
            trib_after=any(d<t['done']<=d+mp and True for t in tribs for mp in [5+g['spawn_alt'][str(tm)]+10])
            if rc['hp']<0.5*rc['mhp']: k='heal(hp<50%)'
            elif buy and ga>=90: k='shop(hp>=50%, buys)'
            elif gems_at_arr>=10 and trib_after: k='teleport(carries gems, tributes after)'
            elif buy: k='shop small (<90 gold)'
            else: k='other (no buy, no gems, hp>=50%)'
            cls[team][k]+=1
            if k.startswith('other'): noreason[team]+=1
        # cost of recalls after captures where walking was shorter: rounds lost = (5 + spawnAlt) - dAlt
        recs=sorted(rc['r0'] for rc in c['recalls'])
        for cp in caps:
            if cp['recall'] and cp['dAlt'] is not None and 5+cp['spawnAlt']>cp['dAlt']:
                cost[team]+= (5+cp['spawnAlt'])-cp['dAlt']; costn[team]+=1
        # tribute interruptions
        for t in c['tributes']:
            if t.get('r0') is not None and t.get('done') is None:
                r0=t['r0']; dur=math.ceil(max(t['gems'],1)/10)
                hit=any(r0<=r<=r0+dur+1 for r in hits_by_round[i]); mv=any(r0<r<=r0+dur+1 for r in moved[i])
                k='died' if t.get('died') else ('hit during channel' if hit else ('moved away' if mv else 'no hit, no move (?)'))
                trib_cause[team][k]+=1
                if k=='no hit, no move (?)' and len(trib_cause[team])<99 and trib_cause[team][k]<=3: print(f'   sample unexplained: {rec["match"][:8]} {g["map"]} {team} {c["ty"]} r0={r0} gems={t["gems"]} pos={t["pos"]} gems_end? next events:',[ (e['r'],e['k'],e['ph']) for r in range(r0,r0+dur+2) for e in Gm.ev.get(r,[]) if e.get('a')==i][:12])
    # rows detours: sample biggest legs for us
    if g['map']=='rows':
        for c in g['champs']:
            if c['team']!='us': continue
            for s,d in c['segs']:
                if s-d>=12: rows_legs.append((s-d,rec['match'][:8],c['ty'],s,d))
print('### Recall classification (arrived recalls), us vs opp\n')
for team in ('us','opp'):
    tot=sum(cls[team].values()); print(f'- {team}: '+', '.join(f'{k} {v} ({100*v/tot:.0f}%)' for k,v in cls[team].most_common())+f'; gold at arrival med {med(goldarr[team]):.0f} (share >=90: {100*sum(x>=90 for x in goldarr[team])/len(goldarr[team]):.0f}%, >=150: {100*sum(x>=150 for x in goldarr[team])/len(goldarr[team]):.0f}%); hp at start med {med(hpstart[team]):.2f}')
print()
print('### Rounds lost on recalls after a capture where walking to the altar was shorter than 5 + spawn->altar\n')
for team in ('us','opp'): print(f'- {team}: {costn[team]} such recalls, {cost[team]:.0f} champion-rounds lost in total = {cost[team]/150:.0f} per game ({cost[team]/max(1,costn[team]):.1f} per recall)')
print()
print('### Why tribute starts do not complete\n')
for team in ('us','opp'): print(f'- {team}: {dict(trib_cause[team])}')
print()
rows_legs.sort(reverse=True); print('### Rows: largest detour legs for us (extra moves, match, type, moves, shortest):', rows_legs[:12]); print(f'legs with >=12 extra moves: {len(rows_legs)}')

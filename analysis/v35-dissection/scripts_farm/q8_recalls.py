import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
from common import Game, SEL
print('## Q8 Recall classes (corrected gold at arrival = snapshot gold + purchases that round)\n')
cls=collections.defaultdict(collections.Counter); goldarr=collections.defaultdict(list); permap=collections.defaultdict(collections.Counter)
cost=collections.defaultdict(collections.Counter); costn=collections.defaultdict(collections.Counter); stay=collections.defaultdict(list)
byid={g['match']:g for g in G}
for rec in SEL:
    g=byid[rec['match']]; Gm=Game(rec); R=Gm.R
    for c in g['champs']:
        i=c['i']; team=c['team']; tm=Gm.teamof[i]; sa=g['spawn_alt'][str(tm)]
        tribs=sorted([t['done'] for t in c['tributes'] if t.get('done')])
        caps=sorted(c['captures'],key=lambda x:x['r'])
        for rc in c['recalls']:
            if rc.get('done') is None: rc['cls']='interrupted'; continue
            d=rc['done']; snap=R[d]
            ga=next((cc[8] for cc in snap['champs'] if cc[0]==i),0)+sum(b['gold'] for b in c['buys'] if b['r']==d)
            gems=next((cc[7] for cc in snap['champs'] if cc[0]==i),0)
            buy=any(d<=b['r']<=d+3 for b in c['buys']); trib_after=any(d<t<=d+sa+12 for t in tribs)
            if rc['hp']<0.5*rc['mhp']: k='heal (hp<50% at start)'
            elif buy and ga>=90: k='shop (>=90 gold, buys)'
            elif gems>=10 and trib_after: k='teleport (gems, tribute after)'
            elif buy: k='shop small (<90 gold)'
            else: k='no reason visible'
            rc['cls']=k; cls[team][k]+=1; goldarr[team].append(ga); permap[(g['map'],team)][k]+=1
            # rounds on spawn after arrival: first move away
            # (approx) next capture/tribute leg start not available; skip
        for cp in caps:
            if not cp['recall'] or cp['dAlt'] is None: continue
            rc=next((rc for rc in c['recalls'] if cp['r']-5<=rc['r0']<=cp['r']+3),None)
            if rc is None: continue
            k=rc.get('cls','?'); extra=(5+cp['spawnAlt'])-cp['dAlt']
            if extra>0: cost[team][k]+=extra; costn[team][k]+=1
for team in ('us','opp'):
    tot=sum(cls[team].values()); print(f'- {team}: '+', '.join(f'{k} {v} ({100*v/tot:.0f}%)' for k,v in cls[team].most_common())+f'; gold at arrival med {med(goldarr[team]):.0f}, >=90: {100*sum(x>=90 for x in goldarr[team])/len(goldarr[team]):.0f}%, >=150: {100*sum(x>=150 for x in goldarr[team])/len(goldarr[team]):.0f}%')
print('\n### Per map recall classes (us / opp counts)\n')
ks=['heal (hp<50% at start)','shop (>=90 gold, buys)','teleport (gems, tribute after)','shop small (<90 gold)','no reason visible']
rows=[]
for m in MAPS:
    rows.append([m]+[f"{permap[(m,'us')][k]} / {permap[(m,'opp')][k]}" for k in ks])
tbl(['map']+ks,rows)
print('### Rounds lost on recalls after a capture where walking was shorter, by recall class (champion-rounds, total over 150 games; per game)\n')
rows=[]
for team in ('us','opp'):
    for k in ks: rows.append([team,k,costn[team][k],f(cost[team][k],0),f(cost[team][k]/150,1)])
tbl(['team','recall class','recalls','rounds lost','per game'],rows)

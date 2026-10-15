import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
from common import Game, SEL
print('## Q10 Camp utilization: for the own-side gem groups each team farms (>=50% of games), share of rounds the group is respawning / up and untouched / under attack\n')
byid={g['match']:g for g in G}
# farmed sets per map from q3 logic
farmed={}
for m in MAPS:
    gs=[g for g in G if g['map']==m]
    for team in ('us','opp'):
        cnt=collections.Counter()
        for g in gs:
            s=set()
            for ch in champs(g,team):
                for cp in ch['captures']:
                    terr=cp['terr'] if team=='us' else {'own':'enemy','enemy':'own','mid':'mid'}[cp['terr']]
                    if terr=='own': s.add(cp['jg'])
            for k in s: cnt[k]+=1
        farmed[(m,team)]={k for k,v in cnt.items() if v>=0.5*len(gs)}
acc=collections.defaultdict(collections.Counter); idle_gaps=collections.defaultdict(list)
for rec in SEL:
    g=byid[rec['match']]; Gm=Game(rec); R=Gm.R; t=Gm.t
    attacked=collections.defaultdict(set)  # (group) -> rounds under attack by anyone
    for r,evs in Gm.ev.items():
        for e in evs:
            if e['ak']==1 and e['k'] in (5,6):
                for kf in e.get('keff',[]):
                    if kf.get('hp',0)<0 and kf['i'] in Gm.camp_group: attacked[Gm.camp_group[kf['i']]].add(r)
    for team in ('us','opp'):
        tm=t if team=='us' else 1-t
        for gi,inf in Gm.groups.items():
            terr=inf['terr'] if team=='us' else {'own':'enemy','enemy':'own','mid':'mid'}[inf['terr']]
            if terr!='own' or inf['jg'] not in farmed[(rec['map'],team)]: continue
            cs=[c for c in Gm.camp_group if Gm.camp_group[c]==gi]
            up_run=0
            for r in Gm.order:
                alive=any(c[5] for c in R[r]['camps'] if c[0] in cs)
                if not alive: acc[(rec['map'],team)]['respawning']+=1; up_run=0
                elif r in attacked[gi]: acc[(rec['map'],team)]['attacked']+=1; up_run=0
                else: acc[(rec['map'],team)]['untouched']+=1
rows=[]
for m in MAPS:
    r=[m]
    for team in ('us','opp'):
        a=acc[(m,team)]; tot=sum(a.values()) or 1
        r+=[len(farmed[(m,team)]),f'{100*a["respawning"]/tot:.0f}%',f'{100*a["untouched"]/tot:.0f}%',f'{100*a["attacked"]/tot:.0f}%']
    rows.append(r)
tbl(['map','us farmed own groups','respawning','up & untouched','under attack','opp farmed own groups','respawning','up & untouched','under attack'],rows)

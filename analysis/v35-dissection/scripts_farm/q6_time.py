import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
print('## Q6 Lost time\n')
STATES=['walk','camp','fight','tribute','recall','shop','idle','cast_other','dead']
print('### Share of champion-rounds by state (all rounds incl. dead), us vs opp\n')
rows=[]
for name,gs in splits():
    for team in ('us','opp'):
        c=collections.Counter()
        for g in gs:
            for ch in champs(g,team): c.update(ch['states'])
        tot=sum(c.values()); rows.append([name,team,tot]+[f'{100*c[s]/tot:.1f}%' for s in STATES])
tbl(['split','team','champ-rounds']+STATES,rows)
print('### Walking efficiency (moves between purpose points vs shortest path; Mite 0.75, 4.0 extra/leg; study25 0.80)\n')
rows=[]
for name,gs in splits():
    for team in ('us','opp'):
        steps=bfs=n=0
        for g in gs:
            for ch in champs(g,team):
                for s,d in ch['segs']: steps+=s; bfs+=d; n+=1
        rows.append([name,team,n,steps,bfs,f(bfs/max(1,steps),2),f((steps-bfs)/max(1,n),1)])
tbl(['split','team','legs','moves','shortest path','efficiency','extra moves/leg'],rows)
print('### Deaths and respawn cost per map (death = 60 rounds dead)\n')
rows=[]
for name,gs in splits():
    for team in ('us','opp'):
        deaths=sum(len(ch['deaths']) for g in gs for ch in champs(g,team)); dead=sum(ch['states'].get('dead',0) for g in gs for ch in champs(g,team)); tot=sum(sum(ch['states'].values()) for g in gs for ch in champs(g,team))
        cr=sum(alive_rounds(ch) for g in gs for ch in champs(g,team)); cg=sum(x['gems'] for g in gs for ch in champs(g,team) for x in ch['captures'])
        gl=sum(x['gems'] for g in gs for ch in champs(g,team) for x in ch['deaths'])
        rows.append([name,team,len(gs),deaths,f(deaths/len(gs),1),dead,f'{100*dead/max(1,tot):.1f}%',f(dead*cg/max(1,cr),0),gl,f(gl/len(gs),0)])
tbl(['split','team','n','deaths','deaths/game','rounds dead','% of champ-rounds','gems not farmed while dead (dead rounds x gems/alive round)','gems dropped at death','per game'],rows)
print('### Idle rounds: by type (share of alive rounds with no action), us\n')
rows=[]
for team in ('us','opp'):
    c=collections.defaultdict(collections.Counter)
    for g in G:
        for ch in champs(g,team): c[ch['ty']].update(ch['states'])
    for ty,cc in sorted(c.items(),key=lambda x:-sum(x[1].values())):
        al=sum(v for k,v in cc.items() if k!='dead'); rows.append([team,ty,al]+[f'{100*cc[s]/al:.1f}%' for s in STATES[:-1]])
tbl(['team','type','alive rounds']+STATES[:-1],rows)

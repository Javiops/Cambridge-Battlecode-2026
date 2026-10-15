import sys, json, collections
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
c=collections.defaultdict(collections.Counter)
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    for r in g.order:
        for e in g.evs.get(r,[]):
            if e['ak']==1 and g.teamof[e['a']]==t and e['k'] in (12,18,20,11,26):
                c[rec['team']]['k%d'%e['k']]+=1
            if e['ak']==1 and g.teamof[e['a']]==t and e['k']==13:
                for x in e['eff']:
                    if x.get('gold',0)==-10: c[rec['team']]['buy10']+=1
    # tribute starts not completed: k12 by champ i without k18 within 12 rounds
    starts=[(r,e['a']) for r in g.order for e in g.evs.get(r,[]) if e['ak']==1 and e['k']==12 and g.teamof[e['a']]==t]
    dones=[(r,e['a']) for r in g.order for e in g.evs.get(r,[]) if e['ak']==1 and e['k']==18 and g.teamof[e['a']]==t]
    for r,a in starts:
        if not any(a==b and r<=rr<=r+15 for rr,b in dones): c[rec['team']]['start_without_done']+=1
for k,v in c.items(): print(k, dict(v))

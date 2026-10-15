import sys, json, collections, statistics
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
FIGHT={'corners','interlock','elkring','packs','collision'}
st=collections.defaultdict(collections.Counter)
endg=collections.defaultdict(collections.Counter)
tribs=collections.defaultdict(list)
rounds_dist=[]
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    mt='fight' if rec['map'] in FIGHT else 'farm'
    rounds_dist.append((rec['team'],rec['map'],g.last,rec['res'],rec['score'],rec['oscore']))
    for r in g.order:
        sn=g.rounds[r]; diff=g.sub[r][t]-g.sub[r][1-t]
        state='ahead' if diff>=50 else ('behind' if diff<=-50 else 'even')
        late = 'late' if r>=g.last-100 else 'early'
        for key in ((rec['team'],mt,state),(rec['team'],mt,late)):
            S_=st[key]
            for c in sn.values():
                if c['team']==t and c['alive']:
                    S_['cr']+=1; tr=terr(mp,c['x'],c['y'],t); S_[tr]+=1; S_['gems']+=c['gems']
            for e in g.evs.get(r,[]):
                if e['ak']==1 and g.teamof[e['a']]==t:
                    for x in e['eff']:
                        if x.get('hp',0)<0 and g.teamof[x['i']]!=t: S_['dmg']+=-x['hp']
                        if x.get('alive')==0 and g.teamof[x['i']]!=t: S_['kills']+=1
                    if e['k']==18:
                        for x in e['eff']:
                            if x.get('gems',0)<0: S_['trib']+=1; S_['tribgems']+=-x['gems']
                    if e['k']==11: S_['recall']+=1
                if e['ak']==1 and g.teamof[e['a']]!=t:
                    for x in e['eff']:
                        if x.get('alive')==0 and g.teamof[x['i']]==t: S_['deaths']+=1
                if e['ak']==0 and e['ph']==7:
                    for x in e['eff']:
                        if x.get('gems',0)>0 and g.teamof[x['i']]==t: S_['caps']+=1; break
            S_['rounds']+=1
    # tributes by time-to-end
    for r in g.order:
        for e in g.evs.get(r,[]):
            if e['ak']==1 and e['k']==18 and g.teamof[e['a']]==t:
                for x in e['eff']:
                    if x.get('gems',0)<0: tribs[(rec['team'],mt)].append((g.last-r,-x['gems']))
print('## Q5 behaviour by score state (diff = own tributed - enemy tributed; ahead >= +50, behind <= -50)')
print('| team | maps | state | champ-rounds | % in mid+enemy half | dmg to champs per 100 champ-rounds | kills/100 cr | deaths/100 cr | captures/100 cr | tributes/100 cr | mean bag tributed | recalls/100 cr | mean gems carried |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for team in ('mite','uni'):
    for mt in ('fight','farm'):
        for state in ('behind','even','ahead','early','late'):
            S_=st[(team,mt,state)]; cr=S_['cr'] or 1
            print('| %s | %s | %s | %d | %d%% | %.0f | %.2f | %.2f | %.2f | %.2f | %.0f | %.2f | %.0f |'%(team,mt,state,S_['cr'],100*(S_['mid']+S_['enemy'])/cr,100*S_['dmg']/cr,100*S_['kills']/cr,100*S_['deaths']/cr,100*S_['caps']/cr,100*S_['trib']/cr,S_['tribgems']/max(1,S_['trib']),100*S_['recall']/cr,S_['gems']/cr))
print()
print('## tribute bag size vs rounds before game end')
for k,L in sorted(tribs.items()):
    for lo,hi in ((0,25),(25,50),(50,100),(100,300),(300,5000)):
        b=[g for d,g in L if lo<=d<hi]
        if b: print(k,'%d-%d rounds before end: n=%d mean bag %.0f median %d, bags<=10: %d%%'%(lo,hi,len(b),statistics.mean(b),statistics.median(b),100*sum(x<=10 for x in b)/len(b)))
print()
print('## game lengths (team,map,last round,res,score,oscore)')
c=collections.Counter()
for x in rounds_dist:
    c[(x[0],'1000' if max(x[4],x[5])>=1000 else 'timeout')]+=1
print(c)
for x in sorted(rounds_dist,key=lambda z:-z[2])[:8]: print(x)

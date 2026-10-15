import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
print('## Q9 Capture credit, shop trips, rows per type\n')
print('### Attackers that helped kill a group but were not on the capture tiles (no gems/gold), per type; and credited captures per champion-game\n')
rows=[]
for team in ('us','opp'):
    part=collections.Counter(); uncred=collections.Counter(); cred=collections.Counter(); n=collections.Counter(); gold=collections.Counter()
    for g in G:
        kills=collections.defaultdict(lambda:dict(att=set(),cr=set()))
        for ch in champs(g,team):
            n[ch['ty']]+=1; gold[ch['ty']]+=ch.get('earnedGold',0)
            for cp in ch['captures']:
                k=(cp['g'],cp['r']); kills[k]['att']|=set(cp['att']); kills[k]['cr'].add(ch['ty']); cred[ch['ty']]+=1
        for k,v in kills.items():
            for ty in v['att']:
                part[ty]+=1
                if ty not in v['cr']: uncred[ty]+=1
    for ty,_ in n.most_common():
        rows.append([team,ty,n[ty],f(cred[ty]/n[ty],1),part[ty],uncred[ty],f'{100*uncred[ty]/max(1,part[ty]):.0f}%',f(gold[ty]/n[ty],0)])
tbl(['team','type','champion-games','credited captures/g','group kills helped','..not credited','% not credited','gold earned/g'],rows)
print('### Cassi per map: credited captures/g, gold earned/g, buys/g (us vs opp)\n'); rows=[]
for m in MAPS:
    gs=[g for g in G if g['map']==m]; r=[m,len(gs)]
    for team in ('us','opp'):
        cs=[c for g in gs for c in champs(g,team) if c['ty']=='Cassi']
        if not cs: r+=['-','-','-']; continue
        r+=[f(mean([len(c['captures']) for c in cs]),1),f(mean([c.get('earnedGold',0) for c in cs]),0),f(mean([len(c['buys']) for c in cs]),1)]
    rows.append(r)
tbl(['map','n','us Cassi captures/g','gold/g','buys/g','opp Cassi captures/g','gold/g','buys/g'],rows)
print('### Shopping trips (recall at hp>=50% followed by a purchase within 3 rounds of arrival): count per game and rounds from recall start to the next capture or tribute\n'); rows=[]
for name,gs in splits():
    for team in ('us','opp'):
        durs=[]; nrec=0
        for g in gs:
            for ch in champs(g,team):
                pts=sorted([cp['r'] for cp in ch['captures']]+[t['done'] for t in ch['tributes'] if t.get('done')])
                for rc in ch['recalls']:
                    if rc.get('done') is None or rc['hp']<0.5*rc['mhp']: continue
                    if not any(rc['done']<=b['r']<=rc['done']+3 for b in ch['buys']): continue
                    nrec+=1; nxt=next((p for p in pts if p>rc['done']),None)
                    if nxt is not None: durs.append(nxt-rc['r0'])
        rows.append([name,team,nrec,f(nrec/len(gs),1),f(med(durs),0),f(mean(durs),1),f(sum(durs)/len(gs),0)])
tbl(['split','team','shop trips','per game','rounds to next capture/tribute med','mean','champion-rounds per game'],rows)
print('### Gold at the start of a shopping trip is not observable (recall starts before the capture pays); gold spent on the trip instead\n'); rows=[]
for team in ('us','opp'):
    sp=[]
    for g in G:
        for ch in champs(g,team):
            for rc in ch['recalls']:
                if rc.get('done') is None or rc['hp']<0.5*rc['mhp']: continue
                s=sum(b['gold'] for b in ch['buys'] if rc['done']<=b['r']<=rc['done']+3)
                if s>0: sp.append(s)
    bins=[(10,89),(90,149),(150,239),(240,329),(330,10**6)]
    rows.append([team,len(sp),f(med(sp),0)]+[f'{100*sum(lo<=x<=hi for x in sp)/len(sp):.0f}%' for lo,hi in bins])
tbl(['team','shop trips','gold spent med','<90','90-149','150-239','240-329','>=330'],rows)
print('### Rows: per champion type, states and credited captures (us vs opp)\n'); rows=[]
gs=[g for g in G if g['map']=='rows']
for team in ('us','opp'):
    by=collections.defaultdict(list)
    for g in gs:
        for ch in champs(g,team): by[ch['ty']].append(ch)
    for ty,lst in sorted(by.items(),key=lambda x:-len(x[1])):
        c=collections.Counter()
        for ch in lst: c.update(ch['states'])
        tot=sum(c.values()); rows.append([team,ty,len(lst),f(mean([len(ch['captures']) for ch in lst]),1),f(mean([sum(x['gems'] for x in ch['captures']) for ch in lst]),0),f(mean([len(ch['tributes']) for ch in lst]),1),f(mean([len(ch['recalls']) for ch in lst]),1)]+[f'{100*c[s]/tot:.0f}%' for s in ['walk','camp','tribute','recall','idle']])
tbl(['team','type','n','captures/g','gems/g','tributes/g','recalls/g','walk','camp','tribute','recall','idle'],rows)
print('### Rows: team captures by round bins (per game), us vs opp; and gems in hand at game end\n'); rows=[]
for team in ('us','opp'):
    c=collections.Counter()
    for g in gs:
        for ch in champs(g,team):
            for cp in ch['captures']: c[min(cp['r']//50,8)]+=1
    endg=mean([sum(ch['gems_end'] for ch in champs(g,team)) for g in gs])
    rows.append([team]+[f(c[b]/len(gs),2) for b in range(9)]+[f(endg,0)])
tbl(['team']+[f'r{50*b}-{50*b+49}' for b in range(8)]+['r400+','gems in hand at end'],rows)

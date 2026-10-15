import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
print('## Q5 Bags and tributes\n')
def tribrows(gs,team):
    bags=[]; started=[]; oldest=[]; newest=[]; ncap=[]; interrupted=0; died=0; cancel=0; starts=0; passes=0; cr=0; done=0
    for g in gs:
        for ch in champs(g,team):
            passes+=ch['passes']; cr+=alive_rounds(ch)
            for tb in ch['tributes']:
                if tb.get('r0') is not None:
                    starts+=1; started.append(tb['gems'])
                    if tb.get('done') is None:
                        if tb.get('died'): died+=1
                        elif tb.get('cancel'): cancel+=1
                        else: interrupted+=1
                if tb.get('done') is not None:
                    done+=1; bags.append(tb['bag'])
                    if tb.get('oldest') is not None: oldest.append(tb['oldest']); newest.append(tb['newest']); ncap.append(tb.get('ncap',1))
    n=len(gs)
    return [n,starts,done,f(done/n,1),f(100*done/max(cr,1),2),f(med(bags),0),f(mean(bags),0),f(p(bags,0.9),0),f(100*sum(b<=10 for b in bags)/max(1,len(bags)),0)+'%',f(100*sum(b>=100 for b in bags)/max(1,len(bags)),0)+'%',f(mean(ncap),2),f(med(oldest),0),f(med(newest),0),f'{starts-done} ({100*(starts-done)/max(1,starts):.0f}%)',died,cancel,interrupted,passes,f(passes/n,2)]
hdr=['split','team','n','tribute starts','completed','completed/game','per 100 champ-rounds','bag med','mean','p90','bags<=10','bags>=100','captures per bag','oldest gems age med','newest age med','not completed','..died','..cancelled','..other','altar passes with >=10 gems','passes/game']
rows=[]
for name,gs in splits():
    for team in ('us','opp'): rows.append([name,team]+tribrows(gs,team))
tbl(hdr,rows)
print('### Bag distribution at tribute completion (count), us vs opp\n')
rows=[]
for team in ('us','opp'):
    bags=[tb['bag'] for g in G for ch in champs(g,team) for tb in ch['tributes'] if tb.get('done') is not None]
    bins=[(0,10),(11,22),(23,44),(45,66),(67,100),(101,10**9)]
    rows.append([team,len(bags)]+[sum(1 for b in bags if lo<=b<=hi) for lo,hi in bins])
tbl(['team','tributes','<=10','11-22','23-44','45-66','67-100','>100'],rows)
print('### Recall as a teleport: captures followed by a recall start within [-5,+3] rounds; cost comparison walk-to-altar vs 5+spawn-to-altar\n')
rows=[]
for name,gs in splits():
    for team in ('us','opp'):
        caps=[cp for g in gs for ch in champs(g,team) for cp in ch['captures'] if cp['dAlt'] is not None]
        rc=[cp for cp in caps if cp['recall']]
        tele_better=[cp for cp in caps if 5+cp['spawnAlt']<cp['dAlt']]
        tb_rc=[cp for cp in tele_better if cp['recall']]
        walk_better=[cp for cp in caps if 5+cp['spawnAlt']>=cp['dAlt']]; wb_rc=[cp for cp in walk_better if cp['recall']]
        rows.append([name,team,len(caps),len(rc),f(100*len(rc)/max(1,len(caps)),0)+'%',f(med([cp['dAlt'] for cp in caps]),0),f(med([5+cp['spawnAlt'] for cp in caps]),0),len(tele_better),f'{len(tb_rc)} ({100*len(tb_rc)/max(1,len(tele_better)):.0f}%)',len(walk_better),f'{len(wb_rc)} ({100*len(wb_rc)/max(1,len(walk_better)):.0f}%)',f(med([cp['gems_before']+cp['gems'] for cp in rc]),0)])
tbl(['split','team','captures','followed by recall','%','walk camp->altar med','5+spawn->altar med','captures where recall is shorter','..of which recalled','captures where walking is shorter','..of which recalled','gems carried on recalled captures med'],rows)
print('### Recalls: per game, hp at start, gems carried, interrupted/died, and what happened after arrival (purchase within 2 rounds)\n')
rows=[]
for name,gs in splits():
    for team in ('us','opp'):
        recs=[(ch,rc) for g in gs for ch in champs(g,team) for rc in ch['recalls']]
        n=len(gs); done=[(ch,rc) for ch,rc in recs if rc.get('done') is not None]
        hi=[rc for ch,rc in done if rc['hp']>=0.7*rc['mhp']]
        buy=sum(1 for ch,rc in recs if rc.get('done') is not None and any(rc['done']<=b['r']<=rc['done']+2 for b in ch['buys']))
        gems=[rc['gems'] for ch,rc in recs]
        rows.append([name,team,len(recs),f(len(recs)/n,1),len(done),len(recs)-len(done),f(100*len(hi)/max(1,len(done)),0)+'%',f(med([rc['hp']/rc['mhp'] for ch,rc in recs]),2),f(med(gems),0),f(100*sum(g_>0 for g_ in gems)/max(1,len(gems)),0)+'%',f(med([rc['gold'] for ch,rc in recs]),0),f(100*buy/max(1,len(done)),0)+'%'])
tbl(['split','team','recall starts','per game','arrived','interrupted/died','arrivals with hp>=70%','hp frac med','gems carried med','% carrying gems','gold carried med','arrival followed by purchase'],rows)

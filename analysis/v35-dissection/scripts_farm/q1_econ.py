import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
print('## Q1 Economy\n'); print(f'games {len(G)}, W-L {sum(g["res"]=="win" for g in G)}-{sum(g["res"]=="loss" for g in G)}; by map:',{m:f"{sum(1 for g in G if g['map']==m and g['res']=='win')}-{sum(1 for g in G if g['map']==m and g['res']=='loss')}" for m in MAPS})
print('by opp tier:',{t:f"{sum(1 for g in G if g['tier']==t and g['res']=='win')}-{sum(1 for g in G if g['tier']==t and g['res']=='loss')}" for t in TIERS}); print()
# curve
print('### Tributed gems at round marks (mean over games of the map; us / opp); games still running at that mark in brackets\n')
marks=[50,100,150,200,250,300,400,500,700]
rows=[]
for m in MAPS:
    gs=[g for g in G if g['map']==m]; row=[m,len(gs),f(mean([g['rounds'] for g in gs]),0)]
    for mk in marks:
        us=[];op=[]
        for g in gs:
            sub=g['sub']; r=min(mk,len(sub)-1); t=g['t']; us.append(sub[r][t]); op.append(sub[r][1-t])
        n=sum(1 for g in gs if g['rounds']>=mk)
        row.append(f'{mean(us):.0f}/{mean(op):.0f} [{n}]')
    rows.append(row)
tbl(['map','n','mean rounds']+[f'r{mk}' for mk in marks],rows)
# decided round
print('### Round the game is decided (last round at which the eventual winner was not ahead, +1) and lead changes\n')
rows=[]; allrel=[]
def decided(g):
    sub=g['sub']; t=g['t']; w=t if g['res']=='win' else 1-t
    last=0; changes=0; prev=0
    for r,s in enumerate(sub):
        lead=s[w]-s[1-w]
        if lead<=0: last=r
        sg=(lead>0)-(lead<0)
        if sg and prev and sg!=prev: changes+=1
        if sg: prev=sg
    return last+1,changes
for name,gs in splits():
    d=[decided(g) for g in gs]; rel=[x[0]/g['rounds'] for x,g in zip(d,gs)]
    rows.append([name,len(gs),f(med([x[0] for x in d]),0),f(mean([x[0] for x in d]),0),f(100*med(rel),0)+'%',f(mean([x[1] for x in d]),2),sum(1 for x in d if x[0]<=100),sum(1 for x,g_ in zip(d,gs) if x[0]>=g_['rounds']*0.8)])
tbl(['split','n','decided round med','mean','med % of game','lead changes/game','decided by r100','decided in last 20%'],rows)
# rates
print('### Farm rates per team (us vs opponent in the same games)\n')
def rates(gs,team):
    cr=0; caps=0; cg=0; kg=0; trib=0; tg=0; dl=0; endg=0; deaths=0; rounds=0
    for g in gs:
        rounds+=g['rounds']
        for c in champs(g,team):
            cr+=alive_rounds(c); caps+=len(c['captures']); cg+=sum(x['gems'] for x in c['captures']); kg+=sum(x['gems'] for x in c['killgains'])
            trib+=len(c['tributes']); tg+=sum(x['bag'] for x in c['tributes']); dl+=sum(x['gems'] for x in c['deaths']); endg+=c['gems_end']; deaths+=len(c['deaths'])
    n=len(gs); tot=cg+kg
    return [f(caps/n,1),f(100*caps/max(cr,1),2),f(cg/max(caps,1),1),f(100*cg/max(cr,1),1),f(100*tg/max(cr,1),1),f(tg/n,0),f(100*tg/max(tot,1),0)+'%',f(100*dl/max(tot,1),0)+'%',f(100*endg/max(tot,1),0)+'%',f(100*kg/max(tot,1),0)+'%',f(deaths/n,1)]
hdr=['split','team','n','captures/game','captures/100 champ-rounds alive','gems/capture','captured gems/100cr','tributed gems/100cr','tributed/game','% tributed','% lost at death','% carried at end','% of gems from kills','deaths/game']
rows=[]
for name,gs in splits():
    rows.append([name,'us',len(gs)]+rates(gs,'us')); rows.append([name,'opp',len(gs)]+rates(gs,'opp'))
tbl(hdr,rows)
# per map per champion type gems share
print('### Who farms: share of our captured gems by champion type (all games)\n')
c=collections.Counter(); n=collections.Counter()
for g in G:
    for ch in champs(g,'us'): c[ch['ty']]+=sum(x['gems'] for x in ch['captures']); n[ch['ty']]+=1
tot=sum(c.values()); tbl(['type','champion-games','captured gems','share','gems/champion-game'],[[k,n[k],v,f(100*v/tot,0)+'%',f(v/n[k],0)] for k,v in c.most_common()])

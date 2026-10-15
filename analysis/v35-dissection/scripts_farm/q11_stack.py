# Stacking check: squad on the camp during the attack window, by group hp; stack lag; deaths near camps; idle near camps. Both teams.
import sys, os; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
from common import Game, SEL, cheb
print('## Q11 Stacking (squad on the camp during the attack window)\n')
def bucket(v): return '<800' if v<800 else ('800-1500' if v<1500 else ('1500-3000' if v<3000 else '>=3000'))
BK=['<800','800-1500','1500-3000','>=3000']
byid={g['match']:g for g in G}
win=collections.defaultdict(list)        # (team,bucket) -> list of dicts per capture
lag=collections.defaultdict(list)        # (team,bucket) -> rounds between 1st hitter and 2nd/3rd hitter first hit
deaths=collections.defaultdict(collections.Counter)
idle=collections.defaultdict(collections.Counter)
permap=collections.defaultdict(list)     # (team,map) for >=3000
small=collections.defaultdict(list)
for rec in SEL:
    if rec['match'] not in byid: continue
    g=byid[rec['match']]; Gm=Game(rec); R=Gm.R; t=Gm.t; mp=Gm.map
    ch={c['i']:c for c in g['champs']}
    gtiles={gi:[tuple(p) for p in inf['tiles']] for gi,inf in g['groups'].items()}
    # per round alive camp tiles, actions, last damage source
    acted=collections.defaultdict(set); lastsrc={}; firsthit=collections.defaultdict(dict)  # (g,epoch)->{champ:r}
    epoch=collections.Counter(); hitter_rounds=collections.defaultdict(set)
    deadcamp_r=collections.defaultdict(list)
    for r in Gm.order:
        for e in Gm.ev.get(r,[]):
            if e['ak']==1: acted[r].add(e['a'])
            for x in e.get('eff',[]):
                if x.get('hp',0)<0 and x['i'] in ch: lastsrc[(x['i'],r)]=('monster' if e['ak']==2 else ('champion' if e['ak']==1 else 'other'))
            if e['ak']==1 and e['k'] in (5,6):
                for kf in e.get('keff',[]):
                    if kf.get('hp',0)<0 and kf['i'] in Gm.camp_group:
                        gi=Gm.camp_group[kf['i']]; key=(gi,epoch[gi]); firsthit[key].setdefault(e['a'],r)
            if e['ak']==0 and e['ph']==7:
                for kf in e.get('keff',[]):
                    if kf.get('alive')==0 and kf['i'] in Gm.camp_group: pass
        # epoch increments when group dies this round
    # own-team hits on each group per round: (gi) -> {r: set(champ)}
    hits=collections.defaultdict(lambda:collections.defaultdict(set))
    for r in Gm.order:
        for e in Gm.ev.get(r,[]):
            if e['ak']==1 and e['k'] in (5,6):
                for kf in e.get('keff',[]):
                    if kf.get('hp',0)<0 and kf['i'] in Gm.camp_group: hits[Gm.camp_group[kf['i']]][r].add(e['a'])
    for c in g['champs']:
        team=c['team']; tm=Gm.teamof[c['i']]
        for cp in c['captures']:
            if cp['dur'] is None or cp['natt']==0: continue
            gi=cp['g']; tiles=gtiles[str(gi)]; r1=cp['r']; r0=max(0,r1-cp['dur'])
            near=[]
            for r in range(r0,r1+1):
                if r not in R: continue
                near.append(sum(1 for cc in R[r]['champs'] if cc[1]==tm and cc[9] and min(cheb((cc[3],cc[4]),q) for q in tiles)<=3))
            d=dict(natt=cp['natt'],dur=cp['dur'],maxn=max(near) if near else 0,meann=mean(near) if near else 0,hp=cp['hp'],gems=cp['gems'],r=r1,map=g['map'])
            b=bucket(cp['hp']); win[(team,b)].append(d)
            if b=='>=3000': permap[(team,g['map'])].append(d)
            fh={}
            for r in range(r0,r1+1):
                for a in hits[gi].get(r,()):
                    if Gm.teamof[a]==tm: fh.setdefault(a,r)
            rs=sorted(fh.values())
            if len(rs)>=2: lag[(team,b)].append(dict(l2=rs[1]-rs[0],l3=(rs[2]-rs[0]) if len(rs)>=3 else None,n=len(rs)))
        for d in c['deaths']:
            r=d['r']; p=tuple(d['pos'])
            src=next((lastsrc[(c['i'],rr)] for rr in range(r,max(-1,r-4),-1) if (c['i'],rr) in lastsrc),'unknown')
            # distance to nearest alive camp tile at round r
            snap=R.get(r) or R[max(x for x in Gm.order if x<=r)]
            dc=min([cheb(p,(cc[2],cc[3])) for cc in snap['camps'] if cc[5] and cc[1]!='monolith'] or [99])
            k=('monster' if src=='monster' else ('champion@camp' if dc<=4 else 'champion away')) if src!='unknown' else 'unknown'
            deaths[team][k]+=1
    # idle near camps
    for r in Gm.order:
        snap=R[r]; alive_t=[(cc[2],cc[3]) for cc in snap['camps'] if cc[5] and cc[1]!='monolith']
        for cc in snap['champs']:
            if not cc[9]: continue
            team='us' if cc[1]==t else 'opp'
            if cc[0] in acted[r]: continue
            idle[team]['idle']+=1
            if alive_t and min(cheb((cc[3],cc[4]),q) for q in alive_t)<=3: idle[team]['idle_near_camp']+=1
print('### Champions on the camp (within 3 tiles of the group) during the attack window, by group hp; attackers = dealt damage\n')
rows=[]
for team in ('us','opp'):
    for b in BK:
        xs=win[(team,b)]
        if not xs: continue
        cnt=collections.Counter(min(x['maxn'],5) for x in xs); cna=collections.Counter(min(x['natt'],5) for x in xs)
        rows.append([team,b,len(xs),f(mean([x['natt'] for x in xs]),2),f(mean([x['maxn'] for x in xs]),2),f(mean([x['meann'] for x in xs]),2),f(med([x['dur'] for x in xs]),0),f(mean([x['dur'] for x in xs]),1),
                     ' / '.join(str(cna[n]) for n in (1,2,3,4,5)),' / '.join(str(cnt[n]) for n in (1,2,3,4,5)),f(100*sum(1 for x in xs if x['maxn']>=3)/len(xs),0)+'%',f(100*sum(1 for x in xs if x['maxn']>=4)/len(xs),0)+'%'])
tbl(['team','hp bucket','captures','attackers mean','max on camp mean','mean on camp over window','hit->capture med','mean','attackers 1/2/3/4/5+','max on camp 1/2/3/4/5+','>=3 on camp','>=4 on camp'],rows)
print('### >= 3000 hp groups per map (us vs opp): captures, attackers, max on camp, hit->capture\n')
rows=[]
for m in MAPS:
    for team in ('us','opp'):
        xs=permap[(team,m)]
        if not xs: continue
        cna=collections.Counter(min(x['natt'],5) for x in xs)
        rows.append([m,team,len(xs),f(len(xs)/sum(1 for g in G if g['map']==m),2),f(mean([x['natt'] for x in xs]),2),' / '.join(str(cna[n]) for n in (1,2,3,4,5)),f(mean([x['maxn'] for x in xs]),2),f(med([x['dur'] for x in xs]),0),f(mean([x['dur'] for x in xs]),1),f(mean([x['hp'] for x in xs]),0)])
tbl(['map','team','captures','per game','attackers mean','attackers 1/2/3/4/5+','max on camp mean','hit->capture med','mean','mean hp'],rows)
print('### Stack lag: rounds from the first hit on the group to the 2nd / 3rd attacker\'s first hit (captures with >=2 attackers)\n')
rows=[]
for team in ('us','opp'):
    for b in BK:
        xs=lag[(team,b)]
        if not xs: continue
        l3=[x['l3'] for x in xs if x['l3'] is not None]
        rows.append([team,b,len(xs),f(med([x['l2'] for x in xs]),0),f(mean([x['l2'] for x in xs]),1),f(100*sum(1 for x in xs if x['l2']<=2)/len(xs),0)+'%',len(l3),f(med(l3),0),f(mean(l3),1)])
tbl(['team','hp bucket','captures (>=2 hitters)','2nd hitter lag med','mean','2nd within 2 rounds','with 3rd','3rd lag med','mean'],rows)
print('### Deaths by cause (last damage source within 3 rounds; champion kills split by distance to the nearest live camp <=4)\n')
rows=[]
for team in ('us','opp'):
    d=deaths[team]; tot=sum(d.values()) or 1
    rows.append([team,tot,f(tot/len(G),2)]+[f'{d[k]} ({100*d[k]/tot:.0f}%)' for k in ('monster','champion@camp','champion away','unknown')])
tbl(['team','deaths','per game','by monsters','by champions near a camp','by champions away','unknown'],rows)
print('### Idle rounds (alive, no action) and idle within 3 tiles of a live camp\n')
rows=[]
for team in ('us','opp'):
    d=idle[team]; rows.append([team,d['idle'],f(d['idle']/len(G),1),d['idle_near_camp'],f(d['idle_near_camp']/len(G),1),f(100*d['idle_near_camp']/max(1,d['idle']),0)+'%'])
tbl(['team','idle rounds','per game','idle near a camp','per game','share of idle'],rows)

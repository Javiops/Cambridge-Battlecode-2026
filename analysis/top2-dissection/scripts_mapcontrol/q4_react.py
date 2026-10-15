import sys, json, collections, statistics
sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_mapcontrol')
from common import *
FIGHT={'corners','interlock','elkring','packs','collision'}
enc=[]; grp=[]; deaths=[]
for rec in SEL:
    mid=rec['match']; mp=load_map(rec['map']); g=Game(mid); t=0 if rec['side']=='a' else 1
    key=(rec['team'],'fight' if rec['map'] in FIGHT else 'farm')
    def near(sn,i,team,R=8):
        c=sn[i]
        return [e for e in sn.values() if e['alive'] and e['team']==team and e['i']!=i and cheb((c['x'],c['y']),(e['x'],e['y']))<=R]
    def acts(i,r0,r1):
        hitE=hitC=rec_=0; dead=False
        for rr in range(r0,r1+1):
            for e in g.evs.get(rr,[]):
                if e['ak']==1 and e['a']==i:
                    if any(x.get('hp',0)<0 and g.teamof[x['i']]!=t for x in e['eff']): hitE+=1
                    if any(x.get('hp',0)<0 for x in e['keff']): hitC+=1
                    if e['k']==11: rec_+=1
        return hitE,hitC,rec_
    # encounters
    for r in g.order:
        if r<1 or r+5>g.last: continue
        sn=g.rounds[r]
        for c in sn.values():
            if c['team']!=t or not c['alive']: continue
            ens=near(sn,c['i'],1-t)
            if not ens: continue
            # new: no enemy within 8 in r-5..r-1
            new=True
            for rr in range(max(0,r-5),r):
                s2=g.rounds.get(rr)
                if s2 and s2[c['i']]['alive'] and near(s2,c['i'],1-t): new=False;break
            if not new: continue
            e=min(ens,key=lambda e:cheb((c['x'],c['y']),(e['x'],e['y'])))
            s5=g.rounds.get(r+5)
            if not s5: continue
            c5=s5[c['i']]; e5=s5[e['i']]
            d0=cheb((c['x'],c['y']),(e['x'],e['y']))
            al=near(sn,c['i'],t); 
            # was farming: camp hit in r-3..r
            hE0,hC0,_=acts(c['i'],max(0,r-3),r)
            hE,hC,rc=acts(c['i'],r+1,r+5)
            # allies converge: mean dist of other alive allies (any distance) at r vs r+5
            oth=[a for a in sn.values() if a['team']==t and a['alive'] and a['i']!=c['i']]
            conv=None
            if oth:
                d_now=statistics.mean(cheb((c['x'],c['y']),(a['x'],a['y'])) for a in oth)
                oth5=[s5[a['i']] for a in oth if s5[a['i']]['alive']]
                if oth5 and c5['alive']:
                    d_5=statistics.mean(cheb((c5['x'],c5['y']),(a['x'],a['y'])) for a in oth5); conv=d_now-d_5
            if c5['alive']:
                d5=cheb((c5['x'],c5['y']),(e5['x'],e5['y'])) if e5['alive'] else None
                mv='dead'
                if d5 is None: mv='enemy_died'
                elif d5<=d0-2: mv='approach'
                elif d5>=d0+2: mv='retreat'
                else: mv='hold'
                sp=spawn_dist(mp,c5['x'],c5['y'],t)-spawn_dist(mp,c['x'],c['y'],t)
            else: mv='dead'; sp=0
            enc.append(dict(key=key,team=rec['team'],map=rec['map'],mid=mid[:8],r=r,ty=c['ty'],nal=len(al)+1,nen=len(ens),hp=c['hp']/c['mhp'],gems=c['gems'],terr=terr(mp,c['x'],c['y'],t),
                            farming=hC0>0,mv=mv,hitE=hE>0,hitC=hC>0,recall=rc>0,conv=conv,toSpawn=sp,d0=d0,ehp=e['hp']/e['mhp']))
    # enemy group (>=2) entering our own half
    inside=False
    for r in g.order:
        if r+10>g.last: continue
        sn=g.rounds[r]
        ens=[e for e in sn.values() if e['team']!=t and e['alive'] and terr(mp,e['x'],e['y'],t)=='enemy']  # enemy's own==our... careful
        ens=[e for e in sn.values() if e['team']!=t and e['alive'] and terr(mp,e['x'],e['y'],1-t)=='enemy']  # in OUR half from their view
        if len(ens)>=2 and not inside:
            inside=True
            cx=statistics.mean(e['x'] for e in ens); cy=statistics.mean(e['y'] for e in ens)
            mine=[c for c in sn.values() if c['team']==t and c['alive']]
            s10=g.rounds[r+10]
            n0=sum(cheb((c['x'],c['y']),(cx,cy))<=10 for c in mine)
            toward=away=0; farm=0; rc=0
            for c in mine:
                c10=s10[c['i']]
                if not c10['alive']: continue
                d0=cheb((c['x'],c['y']),(cx,cy)); d1=cheb((c10['x'],c10['y']),(cx,cy))
                if d0>10:
                    if d1<=d0-4: toward+=1
                    elif d1>=d0+4: away+=1
                hE,hC,r_=acts(c['i'],r+1,r+10); farm+=hC>0; rc+=r_>0
            n10=sum(s10[c['i']]['alive'] and cheb((s10[c['i']]['x'],s10[c['i']]['y']),(cx,cy))<=10 for c in mine)
            grp.append(dict(key=key,team=rec['team'],map=rec['map'],mid=mid[:8],r=r,nen=len(ens),nmine=len(mine),n0=n0,n10=n10,toward=toward,away=away,farm=farm,recall=rc,diff=g.sub[r][t]-g.sub[r][1-t]))
        if len(ens)==0: inside=False
    # death reaction
    prev=None
    for r in g.order:
        sn=g.rounds[r]
        if prev is not None:
            for c in sn.values():
                p=prev.get(c['i'])
                if c['team']==t and p and p['alive'] and not c['alive'] and r+8<=g.last:
                    s8=g.rounds[r+8]
                    for a in sn.values():
                        if a['team']==t and a['alive'] and a['i']!=c['i'] and cheb((a['x'],a['y']),(p['x'],p['y']))<=12:
                            a8=s8[a['i']]
                            hE,hC,rc=acts(a['i'],r+1,r+8)
                            sp=(spawn_dist(mp,a8['x'],a8['y'],t)-spawn_dist(mp,a['x'],a['y'],t)) if a8['alive'] else None
                            ens=[e for e in sn.values() if e['team']!=t and e['alive'] and cheb((a['x'],a['y']),(e['x'],e['y']))<=8]
                            deaths.append(dict(key=key,team=rec['team'],map=rec['map'],mid=mid[:8],r=r,ty=a['ty'],hp=a['hp']/a['mhp'],nen=len(ens),dead=not a8['alive'],retreat=(sp is not None and sp<=-3),recall=rc>0,hitE=hE>0,hitC=hC>0,sp=sp))
        prev=sn
def tab(L,label):
    n=len(L)
    if n==0: return '| %s | 0 | | | | | | | | |'%label
    cv=[x['conv'] for x in L if x['conv'] is not None]
    return '| %s | %d | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% |'%(label,n,100*sum(x['mv']=='approach' for x in L)/n,100*sum(x['mv']=='hold' for x in L)/n,100*sum(x['mv']=='retreat' for x in L)/n,100*sum(x['mv']=='dead' for x in L)/n,
        100*sum(x['hitE'] for x in L)/n,100*sum(x['hitC'] for x in L)/n,100*sum(x['recall'] for x in L)/n,100*sum(c>=2 for c in cv)/max(1,len(cv)),100*sum(x['toSpawn']<=-3 for x in L)/n)
hdr='| situation | n | approach | hold | retreat | dies | hits enemy | hits camp | recalls | allies converge(>=2) | moves >=3 toward own spawn |\n|---|---|---|---|---|---|---|---|---|---|---|'
print('## Q4a new enemy within 8 tiles: what the champion does in the next 5 rounds')
for team in ('mite','uni'):
    for mt in ('fight','farm'):
        L=[x for x in enc if x['key']==(team,mt)]
        print('\n### %s on %s maps (n=%d)'%(team,mt,len(L))); print(hdr)
        print(tab(L,'all'))
        print(tab([x for x in L if x['nal']>x['nen']],'numbers advantage'))
        print(tab([x for x in L if x['nal']==x['nen']],'equal numbers'))
        print(tab([x for x in L if x['nal']<x['nen']],'outnumbered'))
        print(tab([x for x in L if x['hp']<0.5],'own hp<50%'))
        print(tab([x for x in L if x['hp']>=0.5],'own hp>=50%'))
        print(tab([x for x in L if x['gems']>0],'carrying gems'))
        print(tab([x for x in L if x['gems']>=50],'carrying >=50 gems'))
        print(tab([x for x in L if x['gems']==0],'no gems'))
        print(tab([x for x in L if x['farming']],'was hitting a camp'))
        print(tab([x for x in L if x['terr']=='own'],'in own half'))
        print(tab([x for x in L if x['terr']=='mid'],'in middle'))
        print(tab([x for x in L if x['terr']=='enemy'],'in enemy half'))
        print(tab([x for x in L if x['ehp']<0.5],'enemy hp<50%'))
        print(tab([x for x in L if x['nal']==1 and x['nen']>=2],'alone vs 2+'))
print('\n## Q4b enemy group (>=2) enters our half: response within 10 rounds')
print('| team | maps | episodes | our champs within 10 at entry -> at +10 (mean) | far champs moving toward (>=4) | moving away | champs still hitting camps | champs recalling | mean enemies in group |')
print('|---|---|---|---|---|---|---|---|---|')
for team in ('mite','uni'):
    for mt in ('fight','farm'):
        L=[x for x in grp if x['key']==(team,mt)]
        if not L: continue
        n=len(L)
        print('| %s | %s | %d | %.1f -> %.1f | %.2f/game-episode | %.2f | %.1f of %.1f | %.2f | %.1f |'%(team,mt,n,statistics.mean(x['n0'] for x in L),statistics.mean(x['n10'] for x in L),statistics.mean(x['toward'] for x in L),statistics.mean(x['away'] for x in L),statistics.mean(x['farm'] for x in L),statistics.mean(x['nmine'] for x in L),statistics.mean(x['recall'] for x in L),statistics.mean(x['nen'] for x in L)))
print('\n## Q4c after an ally dies within 12 tiles: next 8 rounds of each nearby ally')
print('| team | maps | n allies | retreats >=3 toward spawn | recalls | keeps hitting enemies | hits camp | also dies | hp<50% share |')
print('|---|---|---|---|---|---|---|---|---|')
for team in ('mite','uni'):
    for mt in ('fight','farm'):
        L=[x for x in deaths if x['key']==(team,mt)]
        if not L: continue
        n=len(L)
        print('| %s | %s | %d | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% |'%(team,mt,n,100*sum(x['retreat'] for x in L)/n,100*sum(x['recall'] for x in L)/n,100*sum(x['hitE'] for x in L)/n,100*sum(x['hitC'] for x in L)/n,100*sum(x['dead'] for x in L)/n,100*sum(x['hp']<0.5 for x in L)/n))
        for sub,lab in ((lambda x:x['nen']>=2,'enemies>=2 near'),(lambda x:x['nen']==0,'no enemy near'),(lambda x:x['hp']<0.5,'own hp<50%')):
            L2=[x for x in L if sub(x)]; n2=len(L2) or 1
            print('| %s | %s: %s | %d | %d%% | %d%% | %d%% | %d%% | %d%% | |'%(team,mt,lab,len(L2),100*sum(x['retreat'] for x in L2)/n2,100*sum(x['recall'] for x in L2)/n2,100*sum(x['hitE'] for x in L2)/n2,100*sum(x['hitC'] for x in L2)/n2,100*sum(x['dead'] for x in L2)/n2))
import pickle
pickle.dump(dict(enc=enc,grp=grp,deaths=deaths),open(S+'/reports/scripts_mapcontrol/q4.pkl','wb'))

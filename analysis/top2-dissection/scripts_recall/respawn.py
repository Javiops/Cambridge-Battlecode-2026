import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
import collections, statistics as st, json
sel=load_sel()
def med(xs): return st.median(xs) if xs else None
R=[]; H=[]; IDLE=collections.defaultdict(collections.Counter)
for g in sel:
    m=load_map(g['map']); side=0 if g['side']=='a' else 1; al=altars(m)
    rounds,order,events,types,camps=load_game(g['match'])
    sa=m['spawnA']; sp0=set((x,y) for x in range(sa[0],sa[2]+1) for y in range(sa[1],sa[3]+1)); sp={0:sp0,1:set(mirror(m,x,y) for x,y in sp0)}
    byc=collections.defaultdict(list)
    for r in order:
        for e in events[r]:
            if e['ak']==1 and types[e['a']][0]==side: byc[e['a']].append((r,e))
            elif e['ak']==0 and e['ph']==7:
                for x in e['eff']:
                    if types[x['i']][0]==side: byc[x['i']].append((r,dict(e,k='cap',a=x['i'])))
    for i,(t,ty) in types.items():
        if t!=side: continue
        evs=byc[i]
        # positive hp events: source
        for r,e in evs:
            for x in e['eff']:
                if x['i']==i and x.get('hp',0)>0:
                    on=(tuple(e['apos']) in sp[side]) if e['apos'] else None
                    H.append((g['team'],'spawn_regen' if (e['ph']==13 and e['k']==3) else ('buy_k13' if e['k']==13 else 'k%d_ph%d'%(e['k'],e['ph'])),on))
        # idle turns (no action at ph10) off spawn and hp<60%: count
        acted=collections.defaultdict(set)
        for r,e in evs:
            if e['ph']==10: acted[r].add(e['k'])
        for r in order:
            c=rounds[r][i]
            if not c['alive'] or r==0: continue
            on=(c['x'],c['y']) in sp[side]
            key=('spawn' if on else 'field', 'low' if c['hp']<0.6*c['mhp'] else 'ok')
            IDLE[g['team']][key+('idle' if not acted[r] else 'act',)]+=1
        # respawns
        dead_buys=[]
        for r,e in evs:
            if e['k']==13 and e['apos']==[-1,-1]: dead_buys.append(r)
            if e['ph']==14 and e['k']==1:
                ra=r
                stay=0; rr=ra
                while rr in rounds and rounds[rr][i]['alive'] and (rounds[rr][i]['x'],rounds[rr][i]['y']) in sp[side]: stay+=1; rr+=1
                buys=[(r2,e2) for r2,e2 in evs if ra<=r2<=ra+stay and e2['k']==13]
                nxt=None
                for r2,e2 in evs:
                    if r2<=ra+stay: continue
                    if r2>ra+100: break
                    k=e2['k']
                    if k==12: nxt=('tribute',r2-ra); break
                    if k=='cap': nxt=('capture',r2-ra); break
                    if k in(5,6) and any(x['i']!=i and x.get('hp',0)<0 and types[x['i']][0]!=side for x in e2['eff']): nxt=('fight_foe',r2-ra); break
                    if k==11: nxt=('recall',r2-ra); break
                    if k in(5,6) and e2['keff']: nxt=('attack_camp',r2-ra); break
                if nxt is None: nxt=('none',None)
                gold=rounds[ra-1][i]['gold'] if ra-1 in rounds else None
                R.append(dict(team=g['team'],map=g['map'],match=g['match'],ty=ty,r=ra,stay=stay,buys=len(buys),dead_buys=sum(1 for b in dead_buys if ra-61<=b<ra),gold=gold,next=nxt[0],dt=nxt[1]))
for team in ('mite','uni'):
    X=[x for x in R if x['team']==team]
    print('='*10,team,'respawns',len(X))
    print(' bought while dead (per respawn):',collections.Counter(x['dead_buys'] for x in X),' bought on spawn after respawn:',collections.Counter(x['buys'] for x in X),' gold at respawn med',med([x['gold'] for x in X if x['gold'] is not None]))
    print(' stay on spawn after respawn:',sorted(collections.Counter(min(x['stay'],8) for x in X).items()))
    print(' next:',collections.Counter(x['next'] for x in X),' dt med',med([x['dt'] for x in X if x['dt']]))
    print(' by map next:',{mp:dict(collections.Counter(x['next'] for x in X if x['map']==mp)) for mp in sorted(set(x['map'] for x in X))})
    hh=collections.Counter((k,on) for t,k,on in H if t==team); print(' positive hp events by source/onspawn:',dict(hh))
    I=IDLE[team]; print(' champion-turns: ',{k:v for k,v in sorted(I.items())})

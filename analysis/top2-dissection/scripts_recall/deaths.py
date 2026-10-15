import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
import collections, statistics as st, json
sel=load_sel()
def med(xs): return st.median(xs) if xs else None
def pct(xs,p):
    if not xs: return None
    xs=sorted(xs); return xs[min(len(xs)-1,int(p*len(xs)))]
D=[]
for g in sel:
    m=load_map(g['map']); side=0 if g['side']=='a' else 1
    rounds,order,events,types,camps=load_game(g['match'])
    sa=m['spawnA']; sp0=set((x,y) for x in range(sa[0],sa[2]+1) for y in range(sa[1],sa[3]+1)); sp={0:sp0,1:set(mirror(m,x,y) for x,y in sp0)}
    dsp={t:bfs(m,sp[t]) for t in (0,1)}
    for k in range(1,len(order)):
        r=order[k]; pr=order[k-1]
        for i,(t,ty) in types.items():
            if t!=side: continue
            if not (rounds[pr][i]['alive'] and not rounds[r][i]['alive']): continue
            # death event
            killer=None; kkind=None; gems=0; dmg_src=collections.Counter(); dmg_last10=collections.Counter()
            traj=[]
            for rr in range(max(0,r-10),r):
                if rr in rounds: traj.append(round(100*rounds[rr][i]['hp']/rounds[rr][i]['mhp']))
            # damage sources in last 10 rounds and death blow
            acts=collections.Counter(); moved_away=0; recall_try=0; attacked=0; moved=0; first_hit=None
            for rr in range(max(1,r-10),r+1):
                for e in events.get(rr,[]):
                    for x in e['eff']:
                        if x['i']==i and x.get('hp',0)<0:
                            if e['ak']==2: src='camp'
                            elif e['ak']==1: src=types[e['a']][1]+('_spell' if e['k']==6 else '_atk')
                            else: src='other'
                            dmg_last10[src]+=-x['hp']
                            if first_hit is None: first_hit=rr
                            if x.get('alive')==0:
                                killer=src; kkind='camp' if e['ak']==2 else ('spell' if e['k']==6 else 'attack'); gems=-x.get('gems',0)
                    if e['ak']==1 and e['a']==i and e['ph']==10:
                        if e['k']==11: recall_try+=1
                        elif e['k']==4: moved+=1
                        elif e['k'] in (5,6) and (e['eff'] or e['keff']): attacked+=1
            # escape check at r-5 (or at first hit): distance to spawn, number of foes within 8, hp%
            r5=max(0,r-5); c5=rounds[r5][i]; p5=(c5['x'],c5['y'])
            foes5=[f for f in rounds[r5].values() if f['team']!=side and f['alive']]
            nfoe8=sum(1 for f in foes5 if cheb(p5,(f['x'],f['y']))<=8); nfoe3=sum(1 for f in foes5 if cheb(p5,(f['x'],f['y']))<=3)
            allies8=sum(1 for f in rounds[r5].values() if f['team']==side and f['alive'] and f['i']!=i and cheb(p5,(f['x'],f['y']))<=8)
            dfoe5=min((cheb(p5,(f['x'],f['y'])) for f in foes5),default=99)
            # movement toward/away from nearest foe during last 5 rounds
            pd=(rounds[pr][i]['x'],rounds[pr][i]['y'])
            foesd=[f for f in rounds[pr].values() if f['team']!=side and f['alive']]
            dfoed=min((cheb(pd,(f['x'],f['y'])) for f in foesd),default=99)
            dsp5=dsp[side].get(p5,99); dspd=dsp[side].get(pd,99)
            hp5=round(100*c5['hp']/c5['mhp'])
            # damage per round in last 5 rounds
            dmg5=sum(v for v in dmg_last10.values())  # approx (10 rounds)
            kind='camp' if kkind=='camp' else ('foe' if killer else 'unknown')
            # avoidable criteria: at r-5 hp>=35% and (dfoe>=3 or killed by camp) -> could have walked/recalled; or killed by camp (never necessary)
            avoid = kind=='camp' or (hp5>=35 and nfoe3==0) or (hp5>=50)
            D.append(dict(team=g['team'],map=g['map'],match=g['match'],ty=ty,r=r,killer=killer,kind=kind,kkind=kkind,gems=gems,traj=traj,hp5=hp5,dfoe5=dfoe5,nfoe8=nfoe8,nfoe3=nfoe3,allies8=allies8,dsp5=dsp5,dspd=dspd,dfoed=dfoed,
                          recall_try=recall_try,moved=moved,attacked=attacked,fled=(dfoed>dfoe5),avoid=avoid,dmg=dict(dmg_last10),since_first_hit=(r-first_hit) if first_hit else None,
                          near_spawn=dspd<=6,nrounds=g['rounds']))
json.dump(D,open('death_rows.json','w'))
for team in ('mite','uni'):
    X=[d for d in D if d['team']==team]; ng=len([g for g in sel if g['team']==team])
    print('='*10,team,'deaths',len(X),'per game %.1f'%(len(X)/ng),'kind',collections.Counter(d['kind'] for d in X),'blow',collections.Counter(d['kkind'] for d in X))
    print(' killer:',collections.Counter(d['killer'] for d in X).most_common(12))
    print(' spell vs attack damage share in last 10 r: ', end='')
    tot=collections.Counter()
    for d in X:
        for k,v in d['dmg'].items(): tot['camp' if k=='camp' else k.split('_')[1]]+=v
    s=sum(tot.values()); print({k:'%.0f%%'%(100*v/s) for k,v in tot.items()})
    print(' hp%% at r-5: med %s; hist %s'%(med([d['hp5'] for d in X]),sorted(collections.Counter(min(d['hp5']//20*20,100) for d in X).items())))
    print(' rounds from first damage (in 10r window) to death: ',sorted(collections.Counter(d['since_first_hit'] for d in X).items()))
    print(' dfoe at r-5 hist:',sorted(collections.Counter(min(d['dfoe5'],9) for d in X).items()),' nfoe8 ',collections.Counter(d['nfoe8'] for d in X),' allies8',collections.Counter(d['allies8'] for d in X))
    print(' dspawn at death: med %s, <=6: %d'%(med([d['dspd'] for d in X]),sum(d['near_spawn'] for d in X)))
    print(' tried: recall_try>0: %d, moved>0: %d, fled (dist to foe grew): %d, attacked>0: %d, did nothing: %d'%(sum(d['recall_try']>0 for d in X),sum(d['moved']>0 for d in X),sum(d['fled'] for d in X),sum(d['attacked']>0 for d in X),sum(1 for d in X if not d['moved'] and not d['attacked'] and not d['recall_try'])))
    print(' avoidable (my criteria): %d/%d = %.0f%%'%(sum(d['avoid'] for d in X),len(X),100*sum(d['avoid'] for d in X)/len(X)))
    print(' camp deaths: %d; with foe within 8: %d; hp5 med %s; gems lost %d'%(sum(d['kind']=='camp' for d in X),sum(1 for d in X if d['kind']=='camp' and d['nfoe8']>0),med([d['hp5'] for d in X if d['kind']=='camp']),sum(d['gems'] for d in X if d['kind']=='camp')))
    print(' deaths with gems: %d, gems lost %d'%(sum(d['gems']>0 for d in X),sum(d['gems'] for d in X)))
    print(' by map:')
    for mp in sorted(set(d['map'] for d in X)):
        Y=[d for d in X if d['map']==mp]; print('   %-10s deaths %2d (%.1f/game) camp %d foe %d avoid %d hp5 med %s traj-example %s'%(mp,len(Y),len(Y)/6,sum(d['kind']=='camp' for d in Y),sum(d['kind']=='foe' for d in Y),sum(d['avoid'] for d in Y),med([d['hp5'] for d in Y]),Y[0]['traj'] if Y else ''))
    print(' by type:',{ty:(len([d for d in X if d['ty']==ty]),sum(d['kind']=='camp' for d in X if d['ty']==ty)) for ty in sorted(set(d['ty'] for d in X))})
    print(' examples:')
    for d in X[:3]+[d for d in X if d['kind']=='camp'][:3]+[d for d in X if d['avoid'] and d['kind']=='foe'][:3]:
        print('   ',d['match'][:8],d['map'],d['ty'],'r',d['r'],'killer',d['killer'],'gems',d['gems'],'traj',d['traj'],'dfoe5',d['dfoe5'],'nfoe8',d['nfoe8'],'allies8',d['allies8'],'dspawn',d['dsp5'],'recall_try',d['recall_try'],'moved',d['moved'],'attacked',d['attacked'],'fled',d['fled'],'dmg',d['dmg'])

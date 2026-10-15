import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
import collections, statistics as st, json
sel=load_sel()
def med(xs): return st.median(xs) if xs else None
def pct(xs,p):
    if not xs: return None
    xs=sorted(xs); return xs[min(len(xs)-1,int(p*len(xs)))]
rows=[]; passes=[]; bagsamples=[]; lost=[]; pergame=[]
for g in sel:
    m=load_map(g['map']); al=altars(m); side=0 if g['side']=='a' else 1
    rounds,order,events,types,camps=load_game(g['match'])
    byc=collections.defaultdict(list)
    for r in order:
        for e in events[r]:
            if e['ak']==1 and types[e['a']][0]==side: byc[e['a']].append((r,e))
    mine=[i for i,(t,_) in types.items() if t==side]
    glost=0; gtrib=0
    for i in mine:
        evs=byc[i]
        # tribute starts
        starts=[(r,e) for r,e in evs if e['k']==12]
        comps=[(r,e) for r,e in evs if e['k']==18]
        # pair starts to completions: a completion at r, start is last k12 before r
        used=set()
        for r,e in comps:
            s=[(rs,es) for rs,es in starts if rs<r and rs not in used]
            rs=s[-1][0] if s else None
            if rs is not None: used.add(rs)
            bag=-e['eff'][0]['gems']; gtrib+=bag
            c=rounds[rs-1][i] if rs and rs-1 in rounds else None
            fs=[f for f in rounds[r-1].values() if f['team']!=side and f['alive']]
            p=tuple(e['apos'])
            dfoe=min((cheb(p,(f['x'],f['y'])) for f in fs),default=99)
            rows.append(dict(team=g['team'],map=g['map'],match=g['match'],ty=types[i][1],r=r,bag=bag,start=rs,dur=(r-rs) if rs else None,hpp=round(100*c['hp']/c['mhp']) if c else None,dfoe=dfoe,ticks=max(1,-(-bag//10))))
        # tribute starts that didn't complete (cancelled)
        ncancel=len(starts)-len(used)
        # passes by altar with gems and no tribute: rounds where champion is within cheb 1 of an altar with gems>0
        prev_in=False; cur=None
        for r in order:
            c=rounds[r][i]
            if not c['alive']: prev_in=False; continue
            p=(c['x'],c['y']); inA=any(cheb(p,a)<=1 for a in al) and c['gems']>0
            if inA and not prev_in: cur=dict(team=g['team'],map=g['map'],match=g['match'],ty=types[i][1],r=r,gems=c['gems'],trib=False,rounds=0)
            if inA: cur['rounds']+=1
            if not inA and prev_in: passes.append(cur)
            prev_in=inA
        for r,e in starts:
            # mark the pass containing r
            for ps in passes:
                if ps['match']==g['match'] and ps['ty']==types[i][1] and ps['r']<=r<ps['r']+ps['rounds']+2 and ps['team']==g['team']: ps['trib']=True
        # bag size over time (sample every 10 rounds alive) + deaths with gems
        for r in order:
            if r%10==0 and rounds[r][i]['alive']: bagsamples.append((g['team'],g['map'],types[i][1],rounds[r][i]['gems']))
        for k in range(1,len(order)):
            r=order[k]; pr=order[k-1]
            if rounds[pr][i]['alive'] and not rounds[r][i]['alive']:
                gl=rounds[pr][i]['gems']
                # note: gems at pr end; capture in round r before death could add; use death event eff gems
                for e in events[r]:
                    for x in e['eff']:
                        if x['i']==i and x.get('alive')==0 and 'gems' in x: gl=-x['gems']
                lost.append(dict(team=g['team'],map=g['map'],match=g['match'],ty=types[i][1],r=r,gems=gl)); glost+=gl
    pergame.append(dict(team=g['team'],map=g['map'],match=g['match'],lost=glost,trib=gtrib,score=g['score']))
json.dump(dict(rows=rows,passes=passes,lost=lost,pergame=pergame),open('tribute_rows.json','w'))
for team in ('mite','uni'):
    R=[x for x in rows if x['team']==team]; P=[x for x in passes if x['team']==team]; L=[x for x in lost if x['team']==team]; PG=[x for x in pergame if x['team']==team]
    print('='*10,team,'tributes',len(R),'bag med',med([x['bag'] for x in R]),'p90',pct([x['bag'] for x in R],.9),'max',max(x['bag'] for x in R))
    print(' bag hist:',sorted(collections.Counter(min(x['bag']//10*10,150) for x in R).items()))
    print(' ticks hist:',sorted(collections.Counter(x['ticks'] for x in R).items()),' dur hist',sorted(collections.Counter(x['dur'] for x in R).items()))
    print(' hpp at tribute start med',med([x['hpp'] for x in R if x['hpp'] is not None]),'dfoe med',med([x['dfoe'] for x in R]),'dfoe<=3:',sum(1 for x in R if x['dfoe']<=3))
    print(' passes by altar w/ gems:',len(P),'tributed',sum(x['trib'] for x in P),'not:',sum(1 for x in P if not x['trib']),'gems at untributed passes med',med([x['gems'] for x in P if not x['trib']]),'rounds-in-altar-zone med (trib)',med([x['rounds'] for x in P if x['trib']]),'(no trib)',med([x['rounds'] for x in P if not x['trib']]))
    print('   untributed passes by map:',collections.Counter(x['map'] for x in P if not x['trib']))
    print('   untributed examples:',[(x['match'][:8],x['map'],x['ty'],x['r'],x['gems'],x['rounds']) for x in P if not x['trib']][:6])
    B=[b for t,mp,ty,b in bagsamples if t==team]
    print(' carried bag (sample every 10 r): mean %.1f med %s p90 %s p99 %s >=50: %.1f%% >=100: %.1f%%'%(sum(B)/len(B),med(B),pct(B,.9),pct(B,.99),100*sum(b>=50 for b in B)/len(B),100*sum(b>=100 for b in B)/len(B)))
    print(' deaths',len(L),'with gems>0',sum(1 for x in L if x['gems']>0),'gems lost total',sum(x['gems'] for x in L),'per game med',med([x['lost'] for x in PG]),'mean %.1f'%(sum(x['lost'] for x in PG)/len(PG)),'lost/tributed = %.1f%%'%(100*sum(x['lost'] for x in PG)/sum(x['trib'] for x in PG)))
    print('   gems lost hist:',sorted(collections.Counter(min(x['gems']//20*20,200) for x in L).items()),'big losses:',sorted([(x['gems'],x['match'][:8],x['map'],x['ty'],x['r']) for x in L],reverse=True)[:6])
    print(' by map: ')
    for mp in sorted(set(x['map'] for x in R)):
        X=[x for x in R if x['map']==mp]; LL=[x for x in L if x['map']==mp]; PP=[x for x in P if x['map']==mp]
        print('   %-10s tributes %d bag med %s p90 %s | lost gems %d in %d deaths | passes untributed %d/%d'%(mp,len(X),med([x['bag'] for x in X]),pct([x['bag'] for x in X],.9),sum(x['gems'] for x in LL),len(LL),sum(1 for x in PP if not x['trib']),len(PP)))
    print(' by type:',{ty:(len([x for x in R if x['ty']==ty]),med([x['bag'] for x in R if x['ty']==ty])) for ty in sorted(set(x['ty'] for x in R))})

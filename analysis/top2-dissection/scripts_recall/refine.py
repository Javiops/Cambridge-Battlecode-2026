import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
import collections, statistics as st, json
sel=load_sel()
def med(xs): return st.median(xs) if xs else None
def pct(xs,p):
    if not xs: return None
    xs=sorted(xs); return xs[min(len(xs)-1,int(p*len(xs)))]
rows=json.load(open('recall_rows.json')); D=json.load(open('death_rows.json'))
# 1. heal thresholds per type (heal-only recalls) ; 2. retry streaks; 3. uni 'moved' cancels context
for team in ('mite','uni'):
    print('=====',team)
    A=[x for x in rows if x['team']==team and x['result']=='arrived']
    H=[x for x in A if 'heal' in x['flags'] and 'escape' not in x['flags']]
    print(' heal recall hp%% by type (med/p75/p90/max, n):',{ty:(med([x['hpp'] for x in H if x['ty']==ty]),pct([x['hpp'] for x in H if x['ty']==ty],.75),pct([x['hpp'] for x in H if x['ty']==ty],.9),max([x['hpp'] for x in H if x['ty']==ty]),len([x for x in H if x['ty']==ty])) for ty in sorted(set(x['ty'] for x in H))})
    # non-heal recalls (hp>=50) hp distribution: is there a 'hp<X and not fighting' rule at 50-70?
    NH=[x for x in A if x['hpp']>=50]
    print(' recalls with hp>=50: n=%d, of which shop %d bank %d reposition %d; hp hist %s'%(len(NH),sum('shop' in x['flags'] for x in NH),sum('bank' in x['flags'] for x in NH),sum(x['reason']=='reposition' for x in NH),sorted(collections.Counter(min(x['hpp']//10*10,100) for x in NH).items())))
    # streaks of interrupted starts
    S=sorted([x for x in rows if x['team']==team],key=lambda x:(x['match'],x['idx'],x['r']))
    streaks=[]; cur=None
    for x in S:
        if x['result']=='arrived' or x['result']=='game_end':
            if cur: streaks.append(cur); cur=None
            continue
        if cur and cur['match']==x['match'] and cur['idx']==x['idx'] and x['r']-cur['last']<=2: cur['n']+=1; cur['last']=x['r']; cur['res'].append(x['result'])
        else:
            if cur: streaks.append(cur)
            cur=dict(match=x['match'],idx=x['idx'],ty=x['ty'],map=x['map'],r0=x['r'],last=x['r'],n=1,res=[x['result']],hpp=x['hpp'],dfoe=x['dfoe'])
    if cur: streaks.append(cur)
    print(' interrupted-recall streaks: n streaks %d, length hist %s, rounds wasted in streaks>=3: %d'%(len(streaks),sorted(collections.Counter(min(s['n'],6) for s in streaks).items()),sum(s['last']-s['r0']+1 for s in streaks if s['n']>=3)))
    print('   long streaks:',[(s['match'][:8],s['map'],s['ty'],s['r0'],s['n'],collections.Counter(s['res']).most_common(2),s['hpp'],s['dfoe']) for s in sorted(streaks,key=lambda s:-s['n'])[:6]])
    # uni moved-cancels: dfoe at cancel round, what they do next
    M=[x for x in rows if x['team']==team and x['result']=='moved']
    print(' moved-cancels: n=%d, delay hist %s, hpp med %s, dfoe at start med %s, after %s'%(len(M),collections.Counter(x['end']-x['r'] for x in M),med([x['hpp'] for x in M]),med([x['dfoe'] for x in M]),collections.Counter(x['after'] for x in M)))
    # deaths refinement
    X=[d for d in D if d['team']==team]
    burst=[d for d in X if d['traj'] and len(d['traj'])>=3 and d['traj'][-2]>=50]
    print(' deaths: hp%% at r-2 >=50 (burst): %d/%d; hp at r-2 hist %s'%(len(burst),len(X),sorted(collections.Counter(min(d['traj'][-2]//20*20,100) for d in X if len(d['traj'])>=2).items())))
    print('   deaths with recall attempt in last 10r: %d; of those hp5 med %s'%(sum(d['recall_try']>0 for d in X),med([d['hp5'] for d in X if d['recall_try']>0])))
    print('   deaths where at r-5 hp<50 and nfoe3==0 (could have walked/recalled): %d'%sum(1 for d in X if d['hp5']<50 and d['nfoe3']==0))
    print('   deaths with allies8==0 (alone): %d; outnumbered (nfoe8>allies8+1): %d'%(sum(d['allies8']==0 for d in X),sum(d['nfoe8']>d['allies8']+1 for d in X)))
    print('   killer type share of damage:',collections.Counter(d['killer'].split('_')[0] for d in X if d['killer']).most_common(6))
# tribute wait: delay between entering altar zone with gems and k12 start
W=collections.defaultdict(list); STAYS=collections.defaultdict(list)
for g in sel:
    m=load_map(g['map']); side=0 if g['side']=='a' else 1; al=altars(m)
    rounds,order,events,types,camps=load_game(g['match'])
    sa=m['spawnA']; sp0=set((x,y) for x in range(sa[0],sa[2]+1) for y in range(sa[1],sa[3]+1)); sp={0:sp0,1:set(mirror(m,x,y) for x,y in sp0)}
    k12=collections.defaultdict(list); arr=collections.defaultdict(list)
    for r in order:
        for e in events[r]:
            if e['ak']==1 and types[e['a']][0]==side:
                if e['k']==12: k12[e['a']].append(r)
                if e['ph']==14 and e['k'] in (1,4) and (e['k']==1 or cheb(tuple(e['eff'][0]['pos'][:2]),tuple(e['eff'][0]['pos'][2:]))>1): arr[e['a']].append((r,e['k']))
    for i,(t,ty) in types.items():
        if t!=side: continue
        prev=False; enter=None
        for r in order:
            c=rounds[r][i]
            if not c['alive']: prev=False; continue
            inA=any(cheb((c['x'],c['y']),a)<=1 for a in al) and c['gems']>0
            if inA and not prev: enter=r
            if not inA and prev and enter is not None:
                ks=[k for k in k12[i] if enter<=k<=r+1]
                if ks: W[g['team']].append(ks[0]-enter)
            prev=inA
        # spawn stays after arrival/respawn: allies on spawn when leaving
        for ra,k in arr[i]:
            stay=0; rr=ra
            while rr in rounds and rounds[rr][i]['alive'] and (rounds[rr][i]['x'],rounds[rr][i]['y']) in sp[side]: stay+=1; rr+=1
            leave=ra+stay-1
            if leave not in rounds: continue
            allies_on=sum(1 for f in rounds[leave].values() if f['team']==side and f['i']!=i and f['alive'] and (f['x'],f['y']) in sp[side])
            allies_leave=sum(1 for f in rounds[leave].values() if f['team']==side and f['i']!=i and f['alive'] and (f['x'],f['y']) in sp[side] and (leave+1 in rounds) and (rounds[leave+1][f['i']]['x'],rounds[leave+1][f['i']]['y']) not in sp[side])
            # idle turns during stay (no ph10 action)
            acts=set(r2 for r2 in range(ra,ra+stay) for e in events.get(r2,[]) if e['ak']==1 and e['a']==i and e['ph']==10)
            STAYS[g['team']].append(dict(k=k,stay=stay,allies_on=allies_on,allies_leave=allies_leave,idle=stay-len(acts),map=g['map'],r=ra,ty=ty,match=g['match']))
for team in ('mite','uni'):
    print('=====',team,'tribute start delay after entering altar zone w/ gems: hist',sorted(collections.Counter(min(w,6) for w in W[team]).items()))
    Sx=STAYS[team]
    for kk,name in ((4,'recall-arrival'),(1,'respawn')):
        Y=[s for s in Sx if s['k']==kk]
        print('  %s stays: n=%d; stay>=4: %d, of which allies also on spawn at leave: %d, ally leaves same round: %d; idle turns during stay med %s; stay>=4 by map %s'%(name,len(Y),sum(s['stay']>=4 for s in Y),sum(1 for s in Y if s['stay']>=4 and s['allies_on']>0),sum(1 for s in Y if s['stay']>=4 and s['allies_leave']>0),med([s['idle'] for s in Y]),dict(collections.Counter(s['map'] for s in Y if s['stay']>=4))))
        print('     stay<=1: allies on spawn at leave: %d/%d'%(sum(1 for s in Y if s['stay']<=1 and s['allies_on']>0),sum(s['stay']<=1 for s in Y)))

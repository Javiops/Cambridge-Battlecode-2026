import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
from recalls import analyze, sel
import collections, statistics as st, json
def med(xs): return st.median(xs) if xs else None
def pct(xs,p): 
    if not xs: return None
    xs=sorted(xs); return xs[min(len(xs)-1,int(p*len(xs)))]
rows=[]
per_game=collections.defaultdict(list)
for g in sel:
    out,rounds,order,events,types,dsp,dal,sp=analyze(g)
    side=0 if g['side']=='a' else 1
    m=load_map(g['map']); al=altars(m)
    # index events by champion
    byc=collections.defaultdict(list)
    for r in order:
        for e in events[r]:
            if e['ak']==1: byc[e['a']].append((r,e))
            elif e['ak']==0 and e['ph']==7:
                for x in e['eff']: byc[x['i']].append((r,dict(e,k='cap',a=x['i'])))
    nrounds=g['rounds']
    for rc in out:
        a=rc['idx']; t=side
        rc['nrounds']=nrounds
        if rc['result']!='arrived':
            if rc['end'] is None: rc['end']=nrounds
            # what after interruption within 8 rounds
            r0=rc['end']; acts=[]
            if rc['result']=='game_end': rc['after']='game_end'; rc['retry_delay']=None; rows.append(rc); continue
            for r,e in byc[a]:
                if r0<r<=r0+8 and e['ph']==10: acts.append(e['k'])
            retry=next((r-r0 for r,e in byc[a] if r0<r<=r0+12 and e['k']==11),None)
            died=any(not rounds[r][a]['alive'] for r in order if r0<=r<=r0+8 and r in rounds)
            rc['after']='retry' if retry is not None else ('died' if died else ('fight' if any(k in(5,6) for k in acts) else ('walk' if 4 in acts else 'idle')))
            rc['retry_delay']=retry
            rows.append(rc); continue
        ra=rc['end']
        # stay on spawn: rounds from ra while position in spawn set
        stay=0; r=ra
        while r in rounds and rounds[r][a]['alive'] and (rounds[r][a]['x'],rounds[r][a]['y']) in sp[t]: stay+=1; r+=1
        rc['stay']=stay
        buys=[(r,e) for r,e in byc[a] if ra<=r<ra+max(stay,1)+1 and e['k']==13]
        rc['bought']=len(buys); rc['gold_spent']=-sum(x.get('gold',0) for _,e in buys for x in e['eff'])
        rc['healed']=any(e['ph']==13 and e['k']==3 for r,e in byc[a] if ra<=r<=ra+stay)
        hp_after=rounds[ra][a]['hp']/rounds[ra][a]['mhp'] if ra in rounds else None
        rc['hpp_after']=round(100*hp_after) if hp_after is not None else None
        # next thing: tribute start, capture, foe damage dealt, death, recall, within 60 rounds after leaving
        nxt=None
        for r,e in byc[a]:
            if r<=ra+stay: continue
            if r>ra+stay+80: break
            k=e['k']
            if k==12: nxt=('tribute',r-ra); break
            if k=='cap': nxt=('capture',r-ra); break
            if k in(5,6) and any(x['i']!=a and x.get('hp',0)<0 and types[x['i']][0]!=t for x in e['eff']): nxt=('fight_foe',r-ra); break
            if k==11: nxt=('recall',r-ra); break
            if k in(5,6) and e['keff']: nxt=('attack_camp',r-ra); break
        if nxt is None:
            died=any(not rounds[r][a]['alive'] for r in order if ra<r<=ra+60 and r in rounds)
            nxt=('died',None) if died else ('none/end',None)
        rc['next']=nxt[0]; rc['next_dt']=nxt[1]
        # reasons
        flags=[]
        if rc['dfoe']<=5 and rc['last_hit']<=3: flags.append('escape')
        if rc['hpp']<50: flags.append('heal')
        if rc['gems']>0 and nxt[0]=='tribute': flags.append('bank')
        if rc['gold']>=30 and rc['bought']>0: flags.append('shop')
        if not flags: flags.append('reposition')
        rc['flags']=flags; rc['reason']=flags[0]
        rows.append(rc)
json.dump(rows,open('recall_rows.json','w'))
for team in ('mite','uni'):
    R=[x for x in rows if x['team']==team]
    A=[x for x in R if x['result']=='arrived']
    print('='*20,team,'starts',len(R),'arrived',len(A))
    print('reasons:',collections.Counter(x['reason'] for x in A))
    print('flag combos:',collections.Counter('+'.join(x['flags']) for x in A).most_common(12))
    for reason in ('escape','heal','bank','shop','reposition'):
        X=[x for x in A if x['reason']==reason]
        if not X: continue
        print(' %-10s n=%d hpp med %s p10 %s p90 %s | gems med %s p90 %s | gold med %s | dfoe med %s p10 %s | dspawn med %s | dalt med %s | stay med %s | bought %.0f%% | next %s'%(
            reason,len(X),med([x['hpp'] for x in X]),pct([x['hpp'] for x in X],.1),pct([x['hpp'] for x in X],.9),med([x['gems'] for x in X]),pct([x['gems'] for x in X],.9),med([x['gold'] for x in X]),
            med([x['dfoe'] for x in X]),pct([x['dfoe'] for x in X],.1),med([x['dspawn'] for x in X]),med([x['dalt'] for x in X]),med([x['stay'] for x in X]),100*sum(x['bought']>0 for x in X)/len(X),
            collections.Counter(x['next'] for x in X).most_common(4)))
    print(' hpp hist (arrived):',sorted(collections.Counter(min(x['hpp']//10*10,100) for x in A).items()))
    print(' gems hist:',sorted(collections.Counter(min(x['gems']//20*20,200) for x in A).items()))
    print(' gold hist:',sorted(collections.Counter(min(x['gold']//30*30,300) for x in A).items()))
    print(' dfoe hist at start:',sorted(collections.Counter(min(x['dfoe'],12) for x in A).items()))
    print(' dspawn hist:',sorted(collections.Counter(min(x['dspawn']//10*10,80) for x in A).items()))
    print(' stay hist:',sorted(collections.Counter(min(x['stay'],10) for x in A).items()))
    print(' bought at spawn:',collections.Counter(x['bought'] for x in A),'gold_spent med',med([x['gold_spent'] for x in A if x['bought']]))
    print(' healed on spawn:',sum(x['healed'] for x in A),'/',len(A),' hpp_after<100:',sum(1 for x in A if x['hpp_after'] and x['hpp_after']<100))
    print(' next:',collections.Counter(x['next'] for x in A),'next_dt med',med([x['next_dt'] for x in A if x['next_dt']]))
    print(' by map:')
    for mp in sorted(set(x['map'] for x in R)):
        X=[x for x in A if x['map']==mp]; games=len(set(x['match'] for x in R if x['map']==mp))
        print('   %-10s games %d arrived/game %.1f  reasons %s hpp med %s dfoe med %s stay med %s'%(mp,games,len(X)/max(games,1),dict(collections.Counter(x['reason'] for x in X)),med([x['hpp'] for x in X]),med([x['dfoe'] for x in X]),med([x['stay'] for x in X])))
    print(' by type:')
    for ty in sorted(set(x['ty'] for x in R)):
        X=[x for x in A if x['ty']==ty]
        print('   %-8s n=%d reasons %s hpp med %s gems med %s'%(ty,len(X),dict(collections.Counter(x['reason'] for x in X)),med([x['hpp'] for x in X]),med([x['gems'] for x in X])))
    # interrupted
    I=[x for x in R if x['result']!='arrived']
    print(' INTERRUPTED',len(I),collections.Counter(x['result'] for x in I))
    print('   dfoe at start of interrupted:',sorted(collections.Counter(min(x['dfoe'],12) for x in I).items()),' hpp med',med([x['hpp'] for x in I]))
    print('   after:',collections.Counter(x['after'] for x in I),' retry delay',collections.Counter(x['retry_delay'] for x in I if x['retry_delay']))
    print('   hit_by:',collections.Counter(x.get('hit_by') for x in I if x['result'].startswith('hit')))
    print('   by result -> after:',{k:dict(collections.Counter(x['after'] for x in I if x['result']==k)) for k in set(x['result'] for x in I)})
    # per game
    pg=collections.defaultdict(lambda:[0,0,0])
    for x in R:
        pg[x['match']][0]+=1
        if x['result']=='arrived': pg[x['match']][1]+=1; pg[x['match']][2]+=5+x['stay']
        else: pg[x['match']][2]+=(x['end']-x['r'])
    v=list(pg.values()); ng=len(set(x['match'] for x in sel if x['team']==team))
    print(' per game: starts med %s arrived med %s champ-rounds lost med %s (games %d) ; per champ per 100 rounds: %.2f'%(med([a for a,_,_ in v]),med([b for _,b,_ in v]),med([c for _,_,c in v]),ng, sum(b for _,b,_ in v)/sum(load_map(g['map'])['nch']*g['rounds']/100 for g in sel if g['team']==team)))
    # examples
    print(' examples:')
    for reason in ('escape','heal','bank','shop','reposition'):
        X=[x for x in A if x['reason']==reason][:2]
        for x in X: print('   ',reason,x['match'][:8],x['map'],x['ty'],'r',x['r'],'pos',x['pos'],'hp%',x['hpp'],'gems',x['gems'],'gold',x['gold'],'dfoe',x['dfoe'],'dspawn',x['dspawn'],'stay',x['stay'],'next',x['next'],x['next_dt'])
    for x in [x for x in I][:4]: print('    interrupted',x['match'][:8],x['map'],x['ty'],'r',x['r'],'res',x['result'],'end',x['end'],'hp%',x['hpp'],'dfoe',x['dfoe'],'after',x['after'])

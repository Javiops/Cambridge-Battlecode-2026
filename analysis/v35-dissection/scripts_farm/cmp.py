# usage: FARM_OUT=<out27> python3 -I cmp.py <out26>   -> headline tables, study27 (A) vs study26 (B), with opponents of the study27 games
import sys, os; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_farm')
from lib import *
A=G; B=[json.load(open(f)) for f in sorted(glob.glob(sys.argv[1]+'/*.json'))]
def wl(gs): return f"{sum(g['res']=='win' for g in gs)}-{sum(g['res']=='loss' for g in gs)}"
def bymap(gs,m): return [g for g in gs if g['map']==m]
def flip(t): return {'own':'enemy','enemy':'own','mid':'mid'}[t]
print('## C0 Record\n')
rows=[['all',len(A),wl(A),len(B),wl(B)]]+[[m,len(bymap(A,m)),wl(bymap(A,m)),len(bymap(B,m)),wl(bymap(B,m))] for m in MAPS]
rows+=[['opp '+t,sum(g['tier']==t for g in A),wl([g for g in A if g['tier']==t]),sum(g['tier']==t for g in B),wl([g for g in B if g['tier']==t])] for t in TIERS]
rows+=[['side a / b',f"{sum(g['t']==0 for g in A)} / {sum(g['t']==1 for g in A)}",'',f"{sum(g['t']==0 for g in B)} / {sum(g['t']==1 for g in B)}",'']]
tbl(['split','27 n','27 W-L','26 n','26 W-L'],rows)
opps=collections.Counter(g['opp'] for g in A); oppsB=collections.Counter(g['opp'] for g in B)
print('opponents 27 (games, rank):',', '.join(f"{o}({n},#{next(g['orank'] for g in A if g['opp']==o)})" for o,n in opps.most_common()))
print('opponents 26:',', '.join(f"{o}({n})" for o,n in oppsB.most_common()),'\n')
print('## C1 Economy curve: tributed gems at round marks, us/opp (27) vs us/opp (26); mean over the games of the map\n')
marks=[100,200,300,400]
def curve(gs,mk):
    us=[];op=[]
    for g in gs:
        sub=g['sub']; r=min(mk,len(sub)-1); t=g['t']; us.append(sub[r][t]); op.append(sub[r][1-t])
    return f'{mean(us):.0f}/{mean(op):.0f}'
def decided(g):
    sub=g['sub']; t=g['t']; w=t if g['res']=='win' else 1-t; last=0
    for r,s in enumerate(sub):
        if s[w]-s[1-w]<=0: last=r
    return last+1
rows=[]
for m in MAPS:
    a=bymap(A,m); b=bymap(B,m)
    rows.append([m,f'{len(a)}/{len(b)}']+[f'{curve(a,mk)} ; {curve(b,mk)}' for mk in marks]+[f"{med([decided(g) for g in a]):.0f} ; {med([decided(g) for g in b]):.0f}",f"{mean([g['rounds'] for g in a]):.0f} ; {mean([g['rounds'] for g in b]):.0f}"])
tbl(['map','n 27/26']+[f'r{mk} 27 ; 26' for mk in marks]+['decided round med 27 ; 26','mean rounds 27 ; 26'],rows)
print('## C2 Farm rates (per split: us27 / opp27 / us26 / opp26)\n')
def rates(gs,team):
    cr=caps=cg=kg=tg=dl=endg=deaths=0
    for g in gs:
        for c in champs(g,team):
            cr+=alive_rounds(c); caps+=len(c['captures']); cg+=sum(x['gems'] for x in c['captures']); kg+=sum(x['gems'] for x in c['killgains'])
            tg+=sum(x['bag'] for x in c['tributes']); dl+=sum(x['gems'] for x in c['deaths']); endg+=c['gems_end']; deaths+=len(c['deaths'])
    n=max(1,len(gs)); tot=max(1,cg+kg)
    return dict(capg=caps/n,cap100=100*caps/max(cr,1),gems100=100*cg/max(cr,1),trib100=100*tg/max(cr,1),tribg=tg/n,lost=100*dl/tot,end=100*endg/tot,deaths=deaths/n,gpc=cg/max(1,caps))
rows=[]
for name,ga,gb in [('all',A,B)]+[('map '+m,bymap(A,m),bymap(B,m)) for m in MAPS]+[('win',[g for g in A if g['res']=='win'],[g for g in B if g['res']=='win']),('loss',[g for g in A if g['res']=='loss'],[g for g in B if g['res']=='loss'])]+[('opp '+t,[g for g in A if g['tier']==t],[g for g in B if g['tier']==t]) for t in TIERS[:3]]:
    rs=[rates(ga,'us'),rates(ga,'opp'),rates(gb,'us'),rates(gb,'opp')]
    def col(k,d=1): return ' / '.join(f(r[k],d) for r in rs)
    rows.append([name,f'{len(ga)}/{len(gb)}',col('capg'),col('cap100',2),col('gpc'),col('gems100'),col('tribg',0),col('deaths'),col('lost',0),col('end',0)])
tbl(['split','n 27/26','captures/game','captures/100cr','gems/capture','captured gems/100cr','tributed/game','deaths/game','% lost at death','% carried at end'],rows)
print('## C3 Squad size by group hp (us27 / us26 / opp27 / opp26)\n')
def bucket(v): return '<800' if v<800 else ('800-1500' if v<1500 else ('1500-3000' if v<3000 else '>=3000'))
BK=['<800','800-1500','1500-3000','>=3000']
def sq(gs,team):
    b=collections.defaultdict(list)
    for g in gs:
        for ch in champs(g,team):
            for cp in ch['captures']:
                if cp['dur'] is None or cp['natt']==0: continue
                b[bucket(cp['hp'])].append(cp)
    return b
sets=[sq(A,'us'),sq(A,'opp'),sq(B,'us'),sq(B,'opp')]
rows=[]
for k in BK:
    def col(fn): return ' / '.join(fn(s[k]) for s in sets)
    rows.append([k,col(lambda xs:str(len(xs))),col(lambda xs:f(mean([x['natt'] for x in xs]),2)),col(lambda xs:f(med([x['dur'] for x in xs]),0)),col(lambda xs:f(mean([x['dur'] for x in xs]),1)),
                 col(lambda xs:f(100*sum(x['natt']==1 for x in xs)/max(1,len(xs)),0)+'%'),col(lambda xs:f(100*sum(x['natt']>=3 for x in xs)/max(1,len(xs)),0)+'%'),col(lambda xs:f(100*sum(x['natt']>=4 for x in xs)/max(1,len(xs)),0)+'%'),col(lambda xs:f(med([x['dmg']/x['natt']/max(1,x['dur']) for x in xs]),0))])
tbl(['hp bucket','captures','attackers mean','hit->capture med','mean','single attacker','>=3 attackers','>=4 attackers','dmg/attacker/round med'],rows)
print('### Attackers distribution on >=3000 hp groups (count by 1/2/3/4/5+)\n')
rows=[]
for lab,s in zip(['us27','opp27','us26','opp26'],sets):
    c=collections.Counter(min(x['natt'],5) for x in s['>=3000']); rows.append([lab,len(s['>=3000'])]+[c[n] for n in (1,2,3,4,5)])
tbl(['team','captures','1','2','3','4','5+'],rows)
print('## C4 First camp per map (attackers on the first capture, first capture round, hit->capture): us27 / us26 / opp27\n')
rows=[]
for m in MAPS:
    r=[m]
    for gs,team in ((bymap(A,m),'us'),(bymap(B,m),'us'),(bymap(A,m),'opp')):
        fs=[]
        for g in gs:
            caps=sorted([cp for ch in champs(g,team) for cp in ch['captures'] if cp['dur'] is not None],key=lambda x:x['r'])
            if caps: fs.append(caps[0])
        r.append(f"{mean([x['natt'] for x in fs]):.2f} / r{med([x['r'] for x in fs]):.0f} / {med([x['dur'] for x in fs]):.0f}")
    rows.append(r)
tbl(['map','us27 attackers / 1st capture / hit->cap','us26','opp27'],rows)
print('## C5 Rows cycle (us27 / us26 / opp27 / opp26)\n')
ra=bymap(A,'rows'); rb=bymap(B,'rows'); RS=[(ra,'us'),(rb,'us'),(ra,'opp'),(rb,'opp')]
rows=[]
for gs,team in RS:
    c=collections.Counter()
    for g in gs:
        for ch in champs(g,team):
            for cp in ch['captures']: c[min(cp['r']//50,8)]+=1
    endg=mean([sum(ch['gems_end'] for ch in champs(g,team)) for g in gs]); trib=mean([sum(x['bag'] for ch in champs(g,team) for x in ch['tributes']) for g in gs])
    rows.append([f"{team}{'27' if gs is ra else '26'}",len(gs)]+[f(c[b]/max(1,len(gs)),2) for b in range(9)]+[f(sum(c.values())/max(1,len(gs)),1),f(endg,0),f(trib,0)])
tbl(['team','n']+[f'r{50*b}-{50*b+49}' for b in range(8)]+['r400+','captures/game','gems in hand at end','tributed/game'],rows)
def revisit(gs,team,m=None):
    gaps=[cp['since_up'] for g in gs if m is None or g['map']==m for ch in champs(g,team) for cp in ch['captures'] if cp['since_up']<cp['r']]
    return gaps
rows=[]
for lab,gs,team in (('us27',A,'us'),('us26',B,'us'),('opp27',A,'opp'),('opp26',B,'opp')):
    ga=revisit(gs,team); gr=revisit(gs,team,'rows')
    ranks=[cp for g in gs for ch in champs(g,team) for cp in ch['captures'] if cp['rank'] is not None]
    rows.append([lab,len(ga),f(med(ga),0),f(mean(ga),0),len(gr),f(med(gr),0),f(mean(gr),0),f(100*sum(cp['rank']==0 for cp in ranks)/max(1,len(ranks)),0)+'%',f(mean([cp['dsel']-cp['dnear'] for cp in ranks]),1)])
tbl(['team','revisits (all maps)','gap after respawn med','mean','revisits rows','gap med','mean','nearest-up chosen (all)','extra tiles mean'],rows)
print('### Rows: first-capture round and attackers per game (27 vs 26), from the first 4 team captures\n')
for lab,gs in (('27',ra),('26',rb)):
    c=collections.Counter()
    for g in gs:
        caps=sorted([cp for ch in champs(g,'us') for cp in ch['captures']],key=lambda x:x['r'])
        c[' '.join(f"r{cp['r']}x{cp['natt']}" for cp in caps[:4])]+=1
    print(f'- {lab}: '+'; '.join(f'{k} x{v}' for k,v in c.most_common(4)))
print()
print('## C6 Time: share of champion-rounds by state (us27 / us26 / opp27 / opp26)\n')
STATES=['walk','camp','fight','tribute','recall','shop','idle','dead']
rows=[]
for lab,gs,team in (('us27',A,'us'),('us26',B,'us'),('opp27',A,'opp'),('opp26',B,'opp')):
    c=collections.Counter()
    for g in gs:
        for ch in champs(g,team): c.update(ch['states'])
    tot=sum(c.values()); rows.append([lab,tot]+[f'{100*c[s]/tot:.1f}%' for s in STATES])
tbl(['team','champ-rounds']+STATES,rows)
print('### Dead share per map (us27 / us26 / opp27)\n')
rows=[]
for m in MAPS:
    r=[m]
    for gs,team in ((bymap(A,m),'us'),(bymap(B,m),'us'),(bymap(A,m),'opp')):
        dead=sum(ch['states'].get('dead',0) for g in gs for ch in champs(g,team)); tot=sum(sum(ch['states'].values()) for g in gs for ch in champs(g,team)); d=sum(len(ch['deaths']) for g in gs for ch in champs(g,team))
        r.append(f'{100*dead/max(1,tot):.1f}% ({d/max(1,len(gs)):.1f}/g)')
    rows.append(r)
tbl(['map','us27 dead (deaths/game)','us26','opp27'],rows)
print('## C7 Shop recalls before tributing (us27 / us26 / opp27 / opp26)\n')
rows=[]
for lab,gs,team in (('us27',A,'us'),('us26',B,'us'),('opp27',A,'opp'),('opp26',B,'opp')):
    caps=[cp for g in gs for ch in champs(g,team) for cp in ch['captures'] if cp['dAlt'] is not None]
    rc=[cp for cp in caps if cp['recall']]; wb=[cp for cp in caps if 5+cp['spawnAlt']>=cp['dAlt']]; wbr=[cp for cp in wb if cp['recall']]
    recs=[(ch,r_) for g in gs for ch in champs(g,team) for r_ in ch['recalls']]; n=len(gs)
    trips=0; durs=[]
    for g in gs:
        for ch in champs(g,team):
            pts=sorted([cp['r'] for cp in ch['captures']]+[t['done'] for t in ch['tributes'] if t.get('done')])
            for r_ in ch['recalls']:
                if r_.get('done') is None or r_['hp']<0.5*r_['mhp']: continue
                if not any(r_['done']<=b['r']<=r_['done']+3 for b in ch['buys']): continue
                trips+=1; nxt=next((p_ for p_ in pts if p_>r_['done']),None)
                if nxt is not None: durs.append(nxt-r_['r0'])
    heal=sum(1 for ch,r_ in recs if r_['hp']<0.5*r_['mhp'])
    rows.append([lab,len(caps),f'{len(rc)} ({100*len(rc)/max(1,len(caps)):.0f}%)',f'{len(wbr)} of {len(wb)} ({100*len(wbr)/max(1,len(wb)):.0f}%)',f(len(recs)/n,1),f'{100*heal/max(1,len(recs)):.0f}%',f(trips/n,1),f(med(durs),0),f(sum(durs)/n,0)])
tbl(['team','captures','followed by recall','recall where walking to the altar is shorter','recall starts/game','hp<50% at start','shop trips/game','rounds to next capture/tribute med','shop-trip champion-rounds/game'],rows)
print('## C8 Camps left to the opponent (own-view jg/side; captures/game us vs opp): groups with us <0.2 and opp >=0.5, 27 vs 26\n')
for m in MAPS:
    out=[]
    for lab,gs in (('27',bymap(A,m)),('26',bymap(B,m))):
        n=max(1,len(gs)); cu=collections.Counter(); co=collections.Counter(); info={}
        for g in gs:
            for gi,inf in g['groups'].items(): info[(inf['jg'],inf['terr'])]=inf
            for ch in g['champs']:
                for cp in ch['captures']:
                    terr=cp['terr'] if ch['team']=='us' else flip(cp['terr']); (cu if ch['team']=='us' else co)[(cp['jg'],terr)]+=1
        a=[f"{k[0]}{k[1][0]}({info[k]['gems']}g,{info[k]['hp']}hp: {cu[k]/n:.2f} vs {co[k]/n:.2f})" for k in sorted(info) if cu[k]/n<0.2 and co[k]/n>=0.5]
        out.append(f"{lab}: {', '.join(a) or '-'}")
    print(f'- {m}: '+'  ;;  '.join(out))
print()
print('### Captures per game by territory own/mid/enemy (us27 / us26 / opp27)\n')
rows=[]
for m in ['all']+MAPS:
    r=[m]
    for gs,team in ((A if m=='all' else bymap(A,m),'us'),(B if m=='all' else bymap(B,m),'us'),(A if m=='all' else bymap(A,m),'opp')):
        c=collections.Counter(); n=max(1,len(gs))
        for g in gs:
            for ch in champs(g,team):
                for cp in ch['captures']: c[cp['terr'] if team=='us' else flip(cp['terr'])]+=1
        r.append(f'{c["own"]/n:.1f} / {c["mid"]/n:.1f} / {c["enemy"]/n:.1f}')
    rows.append(r)
tbl(['map','us27','us26','opp27'],rows)
print('## C9 Bags and tributes (us27 / us26 / opp27 / opp26)\n')
rows=[]
for lab,gs,team in (('us27',A,'us'),('us26',B,'us'),('opp27',A,'opp'),('opp26',B,'opp')):
    bags=[];ncap=[];starts=done=passes=cr=0;inter=collections.Counter()
    for g in gs:
        for ch in champs(g,team):
            passes+=ch['passes']; cr+=alive_rounds(ch)
            for tb in ch['tributes']:
                if tb.get('r0') is not None:
                    starts+=1
                    if tb.get('done') is None: inter['died' if tb.get('died') else ('cancel' if tb.get('cancel') else 'other')]+=1
                if tb.get('done') is not None:
                    done+=1; bags.append(tb['bag'])
                    if tb.get('ncap'): ncap.append(tb['ncap'])
    n=len(gs)
    rows.append([lab,starts,done,f(done/n,1),f(100*done/max(1,cr),2),f(med(bags),0),f(mean(bags),0),f(100*sum(b>66 for b in bags)/max(1,len(bags)),0)+'%',f(mean(ncap),2),f'{starts-done} ({100*(starts-done)/max(1,starts):.0f}%)',f(passes/n,2)])
tbl(['team','tribute starts','completed','per game','per 100cr','bag med','mean','bags >66','captures per bag','not completed','altar passes/game'],rows)
print('## C10 Draft per map 27 vs 26\n')
for m in MAPS:
    da=collections.Counter(' > '.join(g['draft']) for g in bymap(A,m)); db=collections.Counter(' > '.join(g['draft']) for g in bymap(B,m))
    print(f'- {m}: 27 {dict(da)} | 26 {dict(db)}')

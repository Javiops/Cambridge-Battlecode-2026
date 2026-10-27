# t5b_arrive.py SET : farming episodes in (LO,HI]: a champion arrives within 2 of a live group (was not within 2 the round before).
# At arrival: allies within 6, nearest ally, enemies within 10 (visible), side, group value. Outcome: death within 15 rounds.
import sys,glob,pickle,os,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import cheb
from cmpwin2 import ok
pref=sys.argv[1]; LO=int(os.environ.get("LO","150")); HI=int(os.environ.get("HI","300"))
files=glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl')
STR={'elk':60,'wolf':20,'monolith':200,'golem':120}
OUT={'us':[], 't5':[]}; n=0
for f in files:
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; n+=1
    r0=rows[0]; groups=collections.defaultdict(list)
    for c in r0['camps']: groups[c['group']].append(c)
    G={g:{'cen':(st.mean(c['spawnX'] for c in cs), st.mean(c['spawnY'] for c in cs)),'gold':sum(c['rewardGold'] for c in cs),'gems':sum(c['rewardGems'] for c in cs),'str':sum(STR.get(c['typeName'],0) for c in cs)} for g,cs in groups.items()}
    sp={t:[(c['x'],c['y']) for c in r0['champions'] if c['team']==t] for t in (0,1)}
    spc={t:(st.mean(p[0] for p in sp[t]), st.mean(p[1] for p in sp[t])) for t in (0,1)}
    inside={}  # (team,index) -> group currently within 2 of
    for ri,r in enumerate(rows):
        if r['round']>HI: break
        live={c['group']:(c['captureTeam'] not in (0,1)) for c in r['camps']}
        for ch in r['champions']:
            k=(ch['team'],ch['index'])
            if not ch['alive']: inside[k]=None; continue
            pos=(ch['x'],ch['y']); g=next((g for g in G if live.get(g,True) and cheb(pos,G[g]['cen'])<=2),None)
            if g is not None and inside.get(k)!=g and LO<r['round']<=HI:
                t=ch['team']; who='us' if t==us else 't5'
                al=[cheb((c['x'],c['y']),pos) for c in r['champions'] if c['team']==t and c['alive'] and c['index']!=ch['index']]
                en=[cheb((c['x'],c['y']),pos) for c in r['champions'] if c['team']!=t and c['alive']]
                du=cheb(G[g]['cen'],spc[t]); dt=cheb(G[g]['cen'],spc[1-t]); side='own' if du<dt-2 else ('their' if dt<du-2 else 'mid')
                died=False
                for rr in rows[ri+1:ri+16]:
                    c2=next((c for c in rr['champions'] if (c['team'],c['index'])==k),None)
                    if c2 and not c2['alive']: died=True; break
                OUT[who].append({'al6':sum(1 for d in al if d<=6),'dal':min(al) if al else 99,'en10':sum(1 for d in en if d<=10),'side':side,'gold':G[g]['gold'],'gems':G[g]['gems'],'str':G[g]['str'],'died':died,'type':ch['typeName']})
            inside[k]=g
print(pref,'clean',n,f'arrivals r{LO}-{HI}')
for who in ('us','t5'):
    L=OUT[who]; m=len(L)
    def pc(f,S=L): S=list(S); return f"{100*sum(1 for d in S if f(d))/max(1,len(S)):.0f}%"
    def dr(S): S=list(S); return f"{100*sum(1 for d in S if d['died'])/max(1,len(S)):.0f}% of {len(S)}"
    print(f"=== {who}: {m/n:.1f} arrivals/game; died within 15 rounds: {dr(L)}")
    print(f"  allies within 6 at arrival 0/1/2+: {pc(lambda d:d['al6']==0)}/{pc(lambda d:d['al6']==1)}/{pc(lambda d:d['al6']>=2)}; death rate by that: {dr(d for d in L if d['al6']==0)} / {dr(d for d in L if d['al6']==1)} / {dr(d for d in L if d['al6']>=2)}")
    print(f"  enemies within 10 at arrival 0/1/2+: {pc(lambda d:d['en10']==0)}/{pc(lambda d:d['en10']==1)}/{pc(lambda d:d['en10']>=2)}; death rate: {dr(d for d in L if d['en10']==0)} / {dr(d for d in L if d['en10']==1)} / {dr(d for d in L if d['en10']>=2)}")
    print(f"  alone (0 allies within 6) AND enemy visible: {pc(lambda d:d['al6']==0 and d['en10']>0)} death rate {dr(d for d in L if d['al6']==0 and d['en10']>0)}; alone, none visible: death rate {dr(d for d in L if d['al6']==0 and d['en10']==0)}")
    print(f"  side own/mid/their: {pc(lambda d:d['side']=='own')}/{pc(lambda d:d['side']=='mid')}/{pc(lambda d:d['side']=='their')}; death rate: {dr(d for d in L if d['side']=='own')} / {dr(d for d in L if d['side']=='mid')} / {dr(d for d in L if d['side']=='their')}")
    print(f"  group gold>=300: {pc(lambda d:d['gold']>=300)} (death {dr(d for d in L if d['gold']>=300)}); str>=60: {pc(lambda d:d['str']>=60)} (death {dr(d for d in L if d['str']>=60)}); alone at str>=60: {pc(lambda d:d['str']>=60 and d['al6']==0)}")
print('--- cross: death rate by enemies within 10 (rows) x allies within 6 (cols 0/1/2+) and by local balance (enemies - (allies+1))')
for who in ('us','t5'):
    L=OUT[who]
    def dr(S): S=list(S); return f"{100*sum(1 for d in S if d['died'])/max(1,len(S)):.0f}%({len(S)})"
    for e in (1,2,3):
        S=[d for d in L if (d['en10']==e if e<3 else d['en10']>=3)]
        print(f"  {who} en10={'3+' if e==3 else e}: " + ' / '.join(dr(d for d in S if (d['al6']==a if a<2 else d['al6']>=2)) for a in (0,1,2)))
    bal=collections.defaultdict(list)
    for d in L:
        if d['en10']>0: bal[max(-2,min(3,d['en10']-(d['al6']+1)))].append(d)
    print(f"  {who} balance (en - ours) -2..3: " + ' / '.join(f"{k}:{dr(bal[k])}" for k in sorted(bal)))
    S=[d for d in L if d['en10']>=2 and d['side']=='own']; print(f"  {who} en10>=2 on own side: {len(S)/n:.1f}/game death {dr(S)}; their side {dr(d for d in L if d['en10']>=2 and d['side']=='their')}")

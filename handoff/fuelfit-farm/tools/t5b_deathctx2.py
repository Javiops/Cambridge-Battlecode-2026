# t5b_deathctx2.py SET : for each death in (LO,HI], look back 20 rounds: when was an enemy first within 10 (visible), how many, what did the victim do
# between first sight and death (approach / stay / retreat), did an ally come, how far was the nearest ally, and was the victim still at a camp when seen
import sys,glob,pickle,os,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import cheb
from cmpwin2 import ok
pref=sys.argv[1]; LO=int(os.environ.get("LO","150")); HI=int(os.environ.get("HI","300")); V=int(os.environ.get("VIS","10"))
files=glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl')
OUT={'us':[], 't5':[]}; n=0
def pos(rr,k):
    c=next((c for c in rr['champions'] if (c['team'],c['index'])==k),None); return c if c and c['alive'] else None
for f in files:
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; n+=1
    r0=rows[0]; groups=collections.defaultdict(list)
    for c in r0['camps']: groups[c['group']].append(c)
    G={g:(st.mean(c['spawnX'] for c in cs), st.mean(c['spawnY'] for c in cs)) for g,cs in groups.items()}
    prev={}
    for ri,r in enumerate(rows):
        if r['round']>HI: break
        for ch in r['champions']:
            k=(ch['team'],ch['index']); p=prev.get(k)
            if p and p['alive'] and not ch['alive'] and LO<r['round']<=HI:
                t=ch['team']; who='us' if t==us else 't5'
                first=None; info=None
                for j in range(max(0,ri-20),ri):
                    rr=rows[j]; me=pos(rr,k)
                    if not me: continue
                    ens=[c for c in rr['champions'] if c['team']!=t and c['alive'] and cheb((c['x'],c['y']),(me['x'],me['y']))<=V]
                    if ens and first is None:
                        first=j; nearest_e=min(cheb((c['x'],c['y']),(me['x'],me['y'])) for c in ens)
                        al=[cheb((c['x'],c['y']),(me['x'],me['y'])) for c in rr['champions'] if c['team']==t and c['alive'] and c['index']!=ch['index']]
                        lv={c['group']:(c['captureTeam'] not in (0,1)) for c in rr['camps']}
                        atc=any(lv.get(g,True) and cheb((me['x'],me['y']),G[g])<=2 for g in G)
                        info={'lead':ri-j,'n_en':len(ens),'d_en':nearest_e,'d_al':min(al) if al else 99,'alive_al':len(al),'hp':me['health'],'atcamp':atc,'p0':(me['x'],me['y'])}
                if info:
                    # what happened between first sight and death: our displacement relative to the enemy centroid at first sight, ally approach
                    rr=rows[first]; me0=info['p0']
                    ens0=[c for c in rr['champions'] if c['team']!=t and c['alive'] and cheb((c['x'],c['y']),me0)<=V]
                    ec=(st.mean(c['x'] for c in ens0), st.mean(c['y'] for c in ens0))
                    pd=(p['x'],p['y']); d0=cheb(me0,ec); d1=cheb(pd,ec)
                    info['move']='approach' if d1<d0-1 else ('retreat' if d1>d0+1 else 'stay')
                    al1=[cheb((c['x'],c['y']),pd) for c in r['champions'] if c['team']==t and c['alive'] and c['index']!=ch['index']]
                    info['d_al1']=min(al1) if al1 else 99
                    info['n_en_end']=sum(1 for c in r['champions'] if c['team']!=t and c['alive'] and cheb((c['x'],c['y']),pd)<=8)
                    # did the victim keep farming (within 2 of a live camp) for >=3 rounds after first sight?
                    stay=0
                    for j in range(first,ri):
                        me=pos(rows[j],k)
                        if me:
                            lv={c['group']:(c['captureTeam'] not in (0,1)) for c in rows[j]['camps']}
                            if any(lv.get(g,True) and cheb((me['x'],me['y']),G[g])<=2 for g in G): stay+=1
                    info['farm_after']=stay
                OUT[who].append(info or {'lead':0})
            prev[k]=ch
print(pref,'clean',n,f'deaths r{LO}-{HI} vision {V}')
for who in ('us','t5'):
    L=OUT[who]; m=len(L); S=[d for d in L if d['lead']>0]
    print(f"=== {who}: {m} deaths; no enemy within {V} in the 20 rounds before death: {100*(m-len(S))/m:.0f}%")
    def pc(f): return f"{100*sum(1 for d in S if f(d))/len(S):.0f}%"
    print(f"  rounds from first sight to death: median {st.median(d['lead'] for d in S):.0f}; <=3: {pc(lambda d:d['lead']<=3)} 4-8: {pc(lambda d:4<=d['lead']<=8)} 9+: {pc(lambda d:d['lead']>=9)}")
    print(f"  enemies seen at first sight 1/2/3+: {pc(lambda d:d['n_en']==1)}/{pc(lambda d:d['n_en']==2)}/{pc(lambda d:d['n_en']>=3)}; enemies within 8 at death 1/2/3+: {pc(lambda d:d['n_en_end']<=1)}/{pc(lambda d:d['n_en_end']==2)}/{pc(lambda d:d['n_en_end']>=3)}")
    print(f"  victim at first sight: at a camp {pc(lambda d:d['atcamp'])}; nearest ally <=3 {pc(lambda d:d['d_al']<=3)}, 4-6 {pc(lambda d:4<=d['d_al']<=6)}, 7+ {pc(lambda d:d['d_al']>=7)}; health median {st.median(d['hp'] for d in S):.0f}")
    print(f"  victim moved vs enemy centroid: approach {pc(lambda d:d['move']=='approach')} stay {pc(lambda d:d['move']=='stay')} retreat {pc(lambda d:d['move']=='retreat')}; kept farming >=3 rounds after sight {pc(lambda d:d['farm_after']>=3)}")
    print(f"  nearest ally at death <=3 {pc(lambda d:d['d_al1']<=3)}, 7+ {pc(lambda d:d['d_al1']>=7)}; ally came closer (>=2) {pc(lambda d:d['d_al1']<=d['d_al']-2)}, ally went away {pc(lambda d:d['d_al1']>=d['d_al']+2)}")

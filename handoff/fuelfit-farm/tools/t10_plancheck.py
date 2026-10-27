# t10_plancheck.py : checks handoff4/t10plan/src/plan_t10.h (share of camp-HIT champion-rounds per group, per side and 50-round bin,
# winners x2) against my cache (599 top-10 games to r300): capture share per group (winners only) and presence share (alive champion-
# rounds within 2 of a camp of the group while the group is alive). Reports per-bin agreement and the systematic bias by group kind.
import re,glob,pickle,os,json,collections,statistics as st,math
H=open('/tmp/claude-0/ff/t10plan/src/plan_t10.h').read()
arr={m.group(1):[int(v) for v in m.group(2).split(',') if v.strip()] for m in re.finditer(r'inline const unsigned char (\w+)\[\]=\{([^}]*)\};',H)}
MAPS={}
for m in re.finditer(r'\{"([^"]+)", (\d+), (\d+), (\w+)_gx, \w+_gy, \{(\d+),(\d+)\}, \{(\d+),(\d+)\}, \w+_sh\}',H):
    name,ng,games,idn,sx0,sx1,sy0,sy1=m.groups(); ng=int(ng)
    MAPS[name]={'ng':ng,'games':int(games),'gx':arr[idn+'_gx'],'gy':arr[idn+'_gy'],'sp':{0:(int(sx0),int(sy0)),1:(int(sx1),int(sy1))},'sh':arr[idn+'_sh']}
NB=14
def share(mp,t,b): return [mp['sh'][(t*NB+b)*mp['ng']+i]/255 for i in range(mp['ng'])]
STR={'wolf':20,'elk':60,'gem_cluster':0,'gold_cluster':0,'monolith':200,'golem':120}
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
idx={g['file'].split('/')[-1]:g for g in json.load(open('/tmp/claude-0/ff/t10/index.json'))}
CAP=collections.defaultdict(lambda: collections.Counter()); PRES=collections.defaultdict(lambda: collections.Counter()); KIND={}; NGAMES=collections.Counter(); unmatched=collections.Counter()
for f in glob.glob('/tmp/claude-0/ff/gem/cache/t10__A_A_*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or rows[-1]['round']<300: continue
    g=idx.get(os.path.basename(f).replace('t10__A_A_','').replace('.r300h.pkl',''))
    if not g or g['map'] not in MAPS: continue
    mp=MAPS[g['map']]
    grp=collections.defaultdict(lambda:{'xs':[],'ys':[],'kinds':set(),'str':0,'camps':[]})
    for c in rows[0]['camps']:
        d=grp[c['group']]; d['xs'].append(c['spawnX']); d['ys'].append(c['spawnY']); d['kinds'].add(c['typeName']); d['str']+=STR.get(c['typeName'],0); d['camps'].append((c['spawnX'],c['spawnY']))
    # match my groups to their index by centre
    g2i={}
    for gi,d in grp.items():
        c=(st.mean(d['xs']),st.mean(d['ys'])); best=min(range(mp['ng']), key=lambda i: cheb(c,(mp['gx'][i],mp['gy'][i])))
        if cheb(c,(mp['gx'][best],mp['gy'][best]))<=2: g2i[gi]=best; KIND[(g['map'],best)]='mono' if 'monolith' in d['kinds'] else ('strong' if d['str']>=120 else ('camp' if d['str']>0 else 'cluster'))
        else: unmatched[g['map']]+=1
    # side check: spawn centre
    for t in (0,1):
        P0=[(ch['x'],ch['y']) for ch in rows[0]['champions'] if ch['team']==t]; sc=(st.mean(p[0] for p in P0),st.mean(p[1] for p in P0))
        if cheb(sc,mp['sp'][t])>3: unmatched[g['map']+'_spawn']+=1
    res={0:g['a_result'],1:g['b_result']}
    for t in (0,1):
        if res[t]!='win': continue
        NGAMES[(g['map'],t)]+=1
    prev={}
    for r in rows:
        rd=r['round']; b=min(NB-1,rd//50)
        alive_g={c['group']:(c['captureTeam'] not in (0,1)) for c in r['camps']}
        for t in (0,1):
            if res[t]!='win': continue
            for ch in r['champions']:
                if ch['team']!=t or not ch['alive']: continue
                for gi,d in grp.items():
                    if gi in g2i and alive_g.get(gi,True) and any(cheb((ch['x'],ch['y']),cp)<=2 for cp in d['camps']): PRES[(g['map'],t,b)][g2i[gi]]+=1
        for c in r['camps']:
            gi=c['group']; ct=c['captureTeam']
            if prev.get(gi,2) not in (0,1) and ct in (0,1) and res[ct]=='win' and gi in g2i: CAP[(g['map'],ct,b)][g2i[gi]]+=1
            prev[gi]=ct
def corr(a,b):
    n=len(a); ma=sum(a)/n; mb=sum(b)/n; sa=math.sqrt(sum((x-ma)**2 for x in a)); sb=math.sqrt(sum((x-mb)**2 for x in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(sa*sb) if sa>0 and sb>0 else float('nan')
print(f"plan_t10.h maps {len(MAPS)}; my winners games per map/side: {sum(NGAMES.values())}; unmatched groups/spawns: {dict(unmatched)}")
cc=[];cp=[]; bias=collections.defaultdict(lambda:[0.0,0.0,0.0,0]); topmatch=collections.Counter(); rows_out=[]
for (m,t,b),caps in sorted(CAP.items()):
    if b>5 or sum(caps.values())<5: continue
    mp=MAPS[m]; th=share(mp,t,b); tot=sum(caps.values()); mine=[caps[i]/tot for i in range(mp['ng'])]
    pres=PRES[(m,t,b)]; ptot=sum(pres.values()) or 1; pr=[pres[i]/ptot for i in range(mp['ng'])]
    c1=corr(th,mine); c2=corr(th,pr); cc.append(c1); cp.append(c2)
    topmatch['n']+=1; topmatch['top1_cap']+= max(range(mp['ng']),key=lambda i:th[i])==max(range(mp['ng']),key=lambda i:mine[i]); topmatch['top1_pres']+= max(range(mp['ng']),key=lambda i:th[i])==max(range(mp['ng']),key=lambda i:pr[i])
    for i in range(mp['ng']):
        k=KIND.get((m,i),'?'); bias[k][0]+=th[i]; bias[k][1]+=mine[i]; bias[k][2]+=pr[i]; bias[k][3]+=1
    rows_out.append((m,t,b,c1,c2,tot))
print(f"map/side/bin cells (r0-299, >=5 winner captures): {len(cc)}; correlation plan vs CAPTURE share: median {st.median(x for x in cc if x==x):.2f}, mean {st.mean(x for x in cc if x==x):.2f}; plan vs PRESENCE share: median {st.median(x for x in cp if x==x):.2f}, mean {st.mean(x for x in cp if x==x):.2f}")
print(f"plan's top group = my most-captured group in {100*topmatch['top1_cap']/topmatch['n']:.0f}% of cells, = my most-present group in {100*topmatch['top1_pres']/topmatch['n']:.0f}%")
print("share by group kind, summed over cells (plan hit-share / my capture share / my presence share):")
for k,(a,bm,c,n) in bias.items(): print(f"   {k:8s} groups {n:5d}: plan {a:7.1f}  captures {bm:7.1f}  presence {c:7.1f}   -> plan/captures {a/max(bm,0.01):.2f}")
bad=sorted([r for r in rows_out if r[3]==r[3]], key=lambda r:r[3])[:12]
print("worst cells (map side bin corr_cap corr_pres winner captures):"); [print("   ",r[0],r[1],f"r{50*r[2]}-{50*r[2]+49}",f"{r[3]:.2f}",f"{r[4]:.2f}",r[5]) for r in bad]

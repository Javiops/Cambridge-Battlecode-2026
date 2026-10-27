# c34_lossdeep.py SET : WIN vs LOSS games, r151-300: where the rival captures (our half / mid / their half) and what; where our champions
# are (fraction of champion-rounds on our half / mid / their half) and dead; our deaths context (3+ enemies, no ally, side); our arrivals
# contested and death rate; rival champion-rounds on our half (invasion); elk groups on our half taken by us / them / none.
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import cheb
from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]; LO,HI=150,300
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
STR={'elk':60,'wolf':20,'monolith':200,'golem':120}
A={'win':collections.Counter(),'loss':collections.Counter()}; N={'win':0,'loss':0}
def side_of(p,spc,t):
    du=cheb(p,spc[t]); dt=cheb(p,spc[1-t]); return 'own' if du<dt-2 else ('their' if dt<du-2 else 'mid')
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    res='win' if g['result']=='win' else 'loss'; N[res]+=1; C=A[res]
    r0=rows[0]; groups=collections.defaultdict(list)
    for c in r0['camps']: groups[c['group']].append(c)
    G={gi:{'cen':(st.mean(c['spawnX'] for c in cs), st.mean(c['spawnY'] for c in cs)),'gems':max(c['rewardGems'] for c in cs),'gold':max(c['rewardGold'] for c in cs),'str':sum(STR.get(c['typeName'],0) for c in cs),'elk':any(c['typeName']=='elk' for c in cs)} for gi,cs in groups.items()}
    sp={t:[(c['x'],c['y']) for c in r0['champions'] if c['team']==t] for t in (0,1)}
    spc={t:(st.mean(p[0] for p in sp[t]), st.mean(p[1] for p in sp[t])) for t in (0,1)}
    prev={}; pv={}; inside={}
    for ri,r in enumerate(rows):
        rd=r['round']
        if rd>HI: break
        live={c['group']:(c['captureTeam'] not in (0,1)) for c in r['camps']}
        if LO<rd<=HI:
            seen=set()
            for c in r['camps']:
                gi=c['group']
                if gi in seen: continue
                seen.add(gi); ct=c['captureTeam']
                if prev.get(gi,2) not in (0,1) and ct in (0,1):
                    who='us' if ct==us else 'riv'; s=side_of(G[gi]['cen'],spc,us)
                    C[(who,'cap',s)]+=1; C[(who,'gems',s)]+=G[gi]['gems']; C[(who,'gold',s)]+=G[gi]['gold']
                    if G[gi]['elk']: C[(who,'elk',s)]+=1
                prev[gi]=ct
            for ch in r['champions']:
                t=ch['team']; who='us' if t==us else 'riv'
                if not ch['alive']: C[(who,'dead_rounds')]+=1; continue
                C[(who,'pos',side_of((ch['x'],ch['y']),spc,us))]+=1
                k=(t,ch['index']); pos=(ch['x'],ch['y'])
                gi=next((gi for gi in G if live.get(gi,True) and cheb(pos,G[gi]['cen'])<=2),None)
                if gi is not None and inside.get(k)!=gi and who=='us':
                    al=sum(1 for c in r['champions'] if c['team']==t and c['alive'] and c['index']!=ch['index'] and cheb((c['x'],c['y']),pos)<=6)
                    en=sum(1 for c in r['champions'] if c['team']!=t and c['alive'] and cheb((c['x'],c['y']),pos)<=10)
                    died=any((c2:=next((c for c in rr['champions'] if (c['team'],c['index'])==k),None)) and not c2['alive'] for rr in rows[ri+1:ri+16])
                    C[('arr','all')]+=1; C[('arr','en2+')]+=en>=2; C[('arr','out')]+=en>al+1
                    if en>=2: C[('arr','en2+_died')]+=died
                    if en>al+1: C[('arr','out_died')]+=died
                    if died: C[('arr','died')]+=1
                inside[k]=gi
        else:
            for c in r['camps']: prev[c['group']]=c['captureTeam']
        for ch in r['champions']:
            k=(ch['team'],ch['index']); p=pv.get(k)
            if p and p['alive'] and not ch['alive'] and LO<rd<=HI:
                t=ch['team']; who='us' if t==us else 'riv'; pos=(p['x'],p['y'])
                en=max(sum(1 for c in rr['champions'] if c['team']!=t and c['alive'] and cheb((c['x'],c['y']),pos)<=8) for rr in rows[max(0,ri-5):ri+1])
                al=sum(1 for c in r['champions'] if c['team']==t and c['alive'] and c['index']!=ch['index'] and cheb((c['x'],c['y']),pos)<=6)
                C[(who,'death')]+=1; C[(who,'death_3+')]+=en>=3; C[(who,'death_0en')]+=en==0; C[(who,'death_alone')]+=al==0; C[(who,'death_'+side_of(pos,spc,us))]+=1
            pv[k]=ch
    # elk groups on our half by r300
    for gi,gg in G.items():
        if not gg['elk'] or side_of(gg['cen'],spc,us)!='own': continue
        first=None; pr=None
        for r in rows:
            if r['round']>HI: break
            ct=next((c['captureTeam'] for c in r['camps'] if c['group']==gi),None)
            if first is None and pr is not None and pr not in (0,1) and ct in (0,1): first='us' if ct==us else 'riv'
            pr=ct
        C[('ownelk',first or 'none')]+=1
for res in ('win','loss'):
    C=A[res]; n=N[res]; print(f"=== {pref} {res.upper()} {n} games, r151-300 (per game)")
    for who in ('us','riv'):
        print(f"  {who}: captures own/mid/their {C[(who,'cap','own')]/n:.2f}/{C[(who,'cap','mid')]/n:.2f}/{C[(who,'cap','their')]/n:.2f}; gems own/mid/their {C[(who,'gems','own')]/n:.0f}/{C[(who,'gems','mid')]/n:.0f}/{C[(who,'gems','their')]/n:.0f}; elk own/mid/their {C[(who,'elk','own')]/n:.2f}/{C[(who,'elk','mid')]/n:.2f}/{C[(who,'elk','their')]/n:.2f}  [sides are OUR own/mid/their]")
        tot=C[(who,'pos','own')]+C[(who,'pos','mid')]+C[(who,'pos','their')]+C[(who,'dead_rounds')]
        print(f"      champion-rounds on our half/mid/their half/dead: {100*C[(who,'pos','own')]/tot:.0f}/{100*C[(who,'pos','mid')]/tot:.0f}/{100*C[(who,'pos','their')]/tot:.0f}/{100*C[(who,'dead_rounds')]/tot:.0f}% | deaths {C[(who,'death')]/n:.2f}: 3+ enemies {100*C[(who,'death_3+')]/max(1,C[(who,'death')]):.0f}%, monsters only {100*C[(who,'death_0en')]/max(1,C[(who,'death')]):.0f}%, alone {100*C[(who,'death_alone')]/max(1,C[(who,'death')]):.0f}%, on our half {100*C[(who,'death_own')]/max(1,C[(who,'death')]):.0f}%")
    a=C[('arr','all')]; print(f"  our arrivals {a/n:.1f}/game: with 2+ enemies within 10 {100*C[('arr','en2+')]/max(1,a):.0f}% (died {100*C[('arr','en2+_died')]/max(1,C[('arr','en2+')]):.0f}%), outnumbered {100*C[('arr','out')]/max(1,a):.0f}% (died {100*C[('arr','out_died')]/max(1,C[('arr','out')]):.0f}%), died after any arrival {100*C[('arr','died')]/max(1,a):.1f}%")
    e=C[('ownelk','us')]+C[('ownelk','riv')]+C[('ownelk','none')]; print(f"  our-half elk groups {e/n:.2f}/game: taken by us {C[('ownelk','us')]/n:.2f}, by rival {C[('ownelk','riv')]/n:.2f}, untouched {C[('ownelk','none')]/n:.2f}")

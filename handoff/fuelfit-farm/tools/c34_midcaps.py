# c34_midcaps.py SET : mid-map captures in r151-300 (both teams), by result: group gems/str, round, capturing champions within 3, our alive champions,
# nearest of ours, and whether the group is the map's biggest gem group
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import cheb
from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]; LO,HI=150,300
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
STR={'elk':60,'wolf':20,'monolith':200,'golem':120}
L=[]
def side_of(p,spc,t):
    du=cheb(p,spc[t]); dt=cheb(p,spc[1-t]); return 'own' if du<dt-2 else ('their' if dt<du-2 else 'mid')
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    res='win' if g['result']=='win' else 'loss'
    r0=rows[0]; groups=collections.defaultdict(list)
    for c in r0['camps']: groups[c['group']].append(c)
    G={gi:{'cen':(st.mean(c['spawnX'] for c in cs), st.mean(c['spawnY'] for c in cs)),'gems':max(c['rewardGems'] for c in cs),'gold':max(c['rewardGold'] for c in cs),'str':sum(STR.get(c['typeName'],0) for c in cs),'kinds':'+'.join(sorted(set(c['typeName'] for c in cs)))} for gi,cs in groups.items()}
    maxg=max(G.values(), key=lambda x:x['gems'])['gems']; totg=sum(x['gems'] for x in G.values())
    sp={t:[(c['x'],c['y']) for c in r0['champions'] if c['team']==t] for t in (0,1)}
    spc={t:(st.mean(p[0] for p in sp[t]), st.mean(p[1] for p in sp[t])) for t in (0,1)}
    prev={}
    for ri,r in enumerate(rows):
        rd=r['round']
        if rd>HI: break
        seen=set()
        for c in r['camps']:
            gi=c['group']
            if gi in seen: continue
            seen.add(gi); ct=c['captureTeam']
            if prev.get(gi,2) not in (0,1) and ct in (0,1) and LO<rd<=HI and side_of(G[gi]['cen'],spc,us)=='mid':
                who='us' if ct==us else 'riv'; cen=G[gi]['cen']
                nin=max(sum(1 for cc in rr['champions'] if cc['team']==ct and cc['alive'] and cheb((cc['x'],cc['y']),cen)<=3) for rr in rows[max(0,ri-5):ri+1])
                ours=[cheb((cc['x'],cc['y']),cen) for cc in r['champions'] if cc['team']==us and cc['alive']]
                L.append({'res':res,'who':who,'gems':G[gi]['gems'],'gold':G[gi]['gold'],'str':G[gi]['str'],'kinds':G[gi]['kinds'],'r':rd,'nin':nin,'ours_alive':len(ours),'ours_near':min(ours) if ours else 99,'big':G[gi]['gems']==maxg,'share':G[gi]['gems']/max(1,totg),'map':g['map']})
            prev[gi]=ct
for res in ('win','loss'):
    for who in ('us','riv'):
        S=[d for d in L if d['res']==res and d['who']==who]
        if not S: print(res,who,'none'); continue
        big=[d for d in S if d['gems']>=150]
        print(f"=== {res} {who}: {len(S)} mid captures; gems median {st.median(d['gems'] for d in S):.0f}, >=150 gems: {len(big)} (sum gems {sum(d['gems'] for d in big)}), biggest group of the map: {sum(1 for d in S if d['big'])}")
        if big: print(f"    big ones: round median {st.median(d['r'] for d in big):.0f}; capturing champions within 3 median {st.median(d['nin'] for d in big)}; str median {st.median(d['str'] for d in big)}; kinds {dict(collections.Counter(d['kinds'] for d in big).most_common(3))}; our alive median {st.median(d['ours_alive'] for d in big)}; our nearest champion median {st.median(d['ours_near'] for d in big)}; share of map gems median {st.median(d['share'] for d in big):.2f}; maps {dict(collections.Counter(d['map'] for d in big).most_common(6))}")

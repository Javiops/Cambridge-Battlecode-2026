# t5b_elkleft.py SET : elk groups on OUR half (closer to our spawn centre by 2+): by r300, first taken by us / by them / untouched;
# properties: group strength (elk 60, wolf 20...), gems, gold, distance from our spawn centre, whether we ever came within 6 / 3,
# rounds with an enemy within 8 of it before r300 (contested), round of our first arrival within 3.  Also our-half elks we took, by the same properties.
import sys,glob,pickle,os,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import cheb
from cmpwin2 import ok
pref=sys.argv[1]; HI=int(os.environ.get("HI","300"))
files=glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl')
STR={'elk':60,'wolf':20,'monolith':200,'golem':120}
L=[]; n=0
for f in files:
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; n+=1
    r0=rows[0]; groups=collections.defaultdict(list)
    for c in r0['camps']: groups[c['group']].append(c)
    sp={t:[(c['x'],c['y']) for c in r0['champions'] if c['team']==t] for t in (0,1)}
    spc={t:(st.mean(p[0] for p in sp[t]), st.mean(p[1] for p in sp[t])) for t in (0,1)}
    for g,cs in groups.items():
        kinds=[c['typeName'] for c in cs]
        if 'elk' not in kinds: continue
        cen=(st.mean(c['spawnX'] for c in cs), st.mean(c['spawnY'] for c in cs))
        du=cheb(cen,spc[us]); dt=cheb(cen,spc[1-us])
        if not du<dt-2: continue
        d={'str':sum(STR.get(k,0) for k in kinds),'gems':sum(c['rewardGems'] for c in cs),'gold':sum(c['rewardGold'] for c in cs),'dist':du,'n':len(cs),'first':None,'first_r':None,'min_us':99,'arr_r':None,'contested':0,'alive':0}
        prev=None
        for r in rows:
            if r['round']>HI: break
            ct=next((c['captureTeam'] for c in r['camps'] if c['group']==g),None)
            live=ct not in (0,1)
            if live: d['alive']+=1
            if d['first'] is None and prev is not None and prev not in (0,1) and ct in (0,1): d['first']='us' if ct==us else 't5'; d['first_r']=r['round']
            prev=ct
            ours=[cheb((c['x'],c['y']),cen) for c in r['champions'] if c['team']==us and c['alive']]
            if ours:
                m=min(ours); d['min_us']=min(d['min_us'],m)
                if d['arr_r'] is None and m<=3: d['arr_r']=r['round']
            if live and any(c['team']!=us and c['alive'] and cheb((c['x'],c['y']),cen)<=8 for c in r['champions']): d['contested']+=1
        L.append(d)
print(pref,'clean',n,'our-half elk groups',len(L),f'({len(L)/n:.2f}/game)')
by=collections.defaultdict(list)
for d in L: by[d['first'] or 'none'].append(d)
for k in ('us','t5','none'):
    S=by[k]; m=len(S)
    if not m: continue
    print(f"=== first taken by {k}: {m} ({m/len(L)*100:.0f}%), {m/n:.2f}/game; first round median {st.median(d['first_r'] for d in S) if k!='none' else '-'}")
    print(f"  str: 60 {sum(1 for d in S if d['str']==60)/m*100:.0f}% 80-100 {sum(1 for d in S if 80<=d['str']<=100)/m*100:.0f}% 120 {sum(1 for d in S if d['str']==120)/m*100:.0f}% 140+ {sum(1 for d in S if d['str']>=140)/m*100:.0f}% | gems median {st.median(d['gems'] for d in S)} gold median {st.median(d['gold'] for d in S)} | dist from our spawn median {st.median(d['dist'] for d in S)}, >=15: {sum(1 for d in S if d['dist']>=15)/m*100:.0f}%")
    print(f"  we came within 3 ever: {sum(1 for d in S if d['min_us']<=3)/m*100:.0f}%, within 6: {sum(1 for d in S if d['min_us']<=6)/m*100:.0f}%, never within 10: {sum(1 for d in S if d['min_us']>10)/m*100:.0f}% | contested rounds (enemy within 8 while alive) median {st.median(d['contested'] for d in S)}, >=30: {sum(1 for d in S if d['contested']>=30)/m*100:.0f}% | alive rounds median {st.median(d['alive'] for d in S)}")
# untouched by strength x distance
S=by['none']
print('untouched by str:', dict(sorted(collections.Counter(d['str'] for d in S).items())))
print('untouched by dist bucket (<8, 8-14, 15-21, 22+):', [sum(1 for d in S if lo<=d['dist']<=hi) for lo,hi in ((0,7),(8,14),(15,21),(22,99))])
print('ALL our-half elk by str (taken by us / t5 / none):', {s:(sum(1 for d in L if d['str']==s and d['first']=='us'),sum(1 for d in L if d['str']==s and d['first']=='t5'),sum(1 for d in L if d['str']==s and d['first'] is None)) for s in sorted(set(d['str'] for d in L))})

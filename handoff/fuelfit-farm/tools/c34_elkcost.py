# c34_elkcost.py SET : real cost of clearing strong groups (str >= STR, i.e. 2+ elks or equivalent) in r1-300, both sides, c34 games:
# champions within 4 of the group centre at capture, clear duration (first round a capturer is within 4 and the group is alive, until capture),
# health lost by the capturers over that duration (sum of per-round decreases, so heals do not hide damage), deaths of capturers in the window,
# and the bot's model: incoming = str * t_clear * 0.5 with t_clear = hp/(dps*n) at dps 60.
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]; STRMIN=int(os.environ.get('STR','120')); HI=300
STR={'wolf':20,'elk':60,'gem_cluster':0,'gold_cluster':0,'monolith':200,'golem':120}; HP={'wolf':1350,'elk':2400,'gem_cluster':120,'gold_cluster':120,'monolith':20000,'golem':5000}
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
R=collections.defaultdict(list)
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    grp={}
    for c in rows[0]['camps']:
        d=grp.setdefault(c['group'],{'gems':c['rewardGems'],'xs':[],'ys':[],'str':0,'hp':0,'kinds':set()})
        d['xs'].append(c['spawnX']); d['ys'].append(c['spawnY']); d['str']+=STR.get(c['typeName'],0); d['hp']+=HP.get(c['typeName'],0); d['kinds'].add(c['typeName'])
    for d in grp.values(): d['c']=(st.mean(d['xs']),st.mean(d['ys']))
    prev={}
    for ri,r in enumerate(rows):
        if r['round']>HI: break
        seen=set()
        for c in r['camps']:
            gi=c['group']
            if gi in seen: continue
            seen.add(gi); ct=c['captureTeam']
            if prev.get(gi,2) not in (0,1) and ct in (0,1) and grp[gi]['str']>=STRMIN and r['round']>0:
                d=grp[gi]
                caps=[ch for ch in r['champions'] if ch['team']==ct and ch['alive'] and cheb((ch['x'],ch['y']),d['c'])<=4]
                if not caps: prev[gi]=ct; continue
                keys={(ch['team'],ch['index']) for ch in caps}
                # walk back: first round (after the previous capture of this group) a capturer is within 4
                start=ri; j=ri-1
                while j>=0:
                    rj=rows[j]; capt=[c2 for c2 in rj['camps'] if c2['group']==gi]
                    if capt and capt[0]['captureTeam'] in (0,1): break   # group was still captured (respawning) then
                    near=any((ch['team'],ch['index']) in keys and ch['alive'] and cheb((ch['x'],ch['y']),d['c'])<=4 for ch in rj['champions'])
                    if near: start=j
                    elif ri-j>12 and start<ri: break
                    j-=1
                lost=0; deaths=0; pv={}
                for k in range(start, ri+1):
                    for ch in rows[k]['champions']:
                        kk=(ch['team'],ch['index'])
                        if kk not in keys: continue
                        p=pv.get(kk)
                        if p is not None:
                            if p['alive'] and ch['health']<p['health']: lost+=p['health']-ch['health']
                            if p['alive'] and not ch['alive']: deaths+=1
                        pv[kk]=ch
                n=len(caps); dur=rows[ri]['round']-rows[start]['round']
                model=d['str']*(d['hp']/(60.0*n))*0.5
                R[('us' if ct==us else 'riv', g['result'])].append({'n':n,'dur':dur,'lost':lost,'deaths':deaths,'str':d['str'],'hp':d['hp'],'gems':d['gems'],'model':model,'r':r['round'],'kinds':'+'.join(sorted(d['kinds']))})
            prev[gi]=ct
for key in sorted(R):
    L=R[key]
    print(f"=== {pref} {key[0]} {key[1]}: {len(L)} captures of str>={STRMIN} groups in r1-300; str median {st.median(x['str'] for x in L):.0f}, gems median {st.median(x['gems'] for x in L):.0f}; capturers within 4: {dict(collections.Counter(x['n'] for x in L))}; duration median {st.median(x['dur'] for x in L):.0f} (mean {st.mean(x['dur'] for x in L):.0f}); health lost by capturers median {st.median(x['lost'] for x in L):.0f} mean {st.mean(x['lost'] for x in L):.0f}; model incoming median {st.median(x['model'] for x in L):.0f}; capturer deaths {sum(x['deaths'] for x in L)}; round median {st.median(x['r'] for x in L):.0f}")
    for n in (1,2,3):
        S=[x for x in L if x['n']==n]
        if len(S)>=3: print(f"      n={n}: {len(S)} caps, duration median {st.median(x['dur'] for x in S):.0f}, lost median {st.median(x['lost'] for x in S):.0f} mean {st.mean(x['lost'] for x in S):.0f}, per capturer {st.mean(x['lost'] for x in S)/n:.0f}, deaths {sum(x['deaths'] for x in S)}, kinds {dict(collections.Counter(x['kinds'] for x in S).most_common(3))}")

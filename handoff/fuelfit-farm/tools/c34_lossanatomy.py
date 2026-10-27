# c34_lossanatomy.py SET : wins vs losses: gem capture and deaths by window (0-150, 151-300) for us and the rival; per-rival record
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
G=[]
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    r0=rows[0]; ggems={}
    for c in r0['camps']: ggems[c['group']]=c['rewardGems']  # per-capture group reward (an earlier version summed it over the group's camps, x members)
    d={'res':g['result'],'rival':g['rival'],'map':g['map']}
    for w,(lo,hi) in (('a',(0,150)),('b',(150,300))):
        gems={0:0,1:0}; prev={}; deaths={0:0,1:0}; pv={}
        for r in rows:
            seen=set()
            for c in r['camps']:
                gi=c['group']
                if gi in seen: continue
                seen.add(gi); ct=c['captureTeam']
                if prev.get(gi,2) not in (0,1) and ct in (0,1) and lo<r['round']<=hi: gems[ct]+=ggems[gi]
                prev[gi]=ct
            for ch in r['champions']:
                k=(ch['team'],ch['index']); p=pv.get(k)
                if p and p['alive'] and not ch['alive'] and lo<r['round']<=hi: deaths[ch['team']]+=1
                pv[k]=ch
        d['g'+w]=gems[us]; d['tg'+w]=gems[1-us]; d['d'+w]=deaths[us]; d['td'+w]=deaths[1-us]
    # first-blood: round of our first death and theirs
    G.append(d)
for name,S in (('WIN',[d for d in G if d['res']=='win']),('LOSS',[d for d in G if d['res']!='win'])):
    m=len(S)
    print(f"{pref} {name} {m}: r0-150 gems us {st.mean(d['ga'] for d in S):.0f} them {st.mean(d['tga'] for d in S):.0f}, deaths us {st.mean(d['da'] for d in S):.2f} them {st.mean(d['tda'] for d in S):.2f} | r151-300 gems us {st.mean(d['gb'] for d in S):.0f} them {st.mean(d['tgb'] for d in S):.0f}, deaths us {st.mean(d['db'] for d in S):.2f} them {st.mean(d['tdb'] for d in S):.2f}")
    print(f"   games where they lead gems already at r150: {sum(1 for d in S if d['tga']>d['ga'])}/{m}; where we die more in r0-150: {sum(1 for d in S if d['da']>d['tda'])}/{m}")
rec=collections.defaultdict(lambda:[0,0])
for d in G: rec[d['rival'][:16]][0 if d['res']=='win' else 1]+=1
print('  per rival (W-L):', ', '.join(f"{k} {v[0]}-{v[1]}" for k,v in sorted(rec.items(), key=lambda x:-x[1][1])))

# c34_farmanat.py SET : farm anatomy with per-capture group rewards. Wins vs losses, windows r1-150 / r151-300, us vs rival:
# alive champion-rounds, captures, gems, gems per 100 alive champion-rounds, captures by kind, and where (our half / mid / their half by
# distance to each team's r0 centroid). Separates "dead" (time) from "choice" (yield per alive champion-round).
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
G=[]
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    r0=rows[0]; grp={}
    for c in r0['camps']:
        d=grp.setdefault(c['group'],{'gems':c['rewardGems'],'gold':c['rewardGold'],'xs':[],'ys':[],'kinds':set()})
        d['xs'].append(c['spawnX']); d['ys'].append(c['spawnY']); d['kinds'].add(c['typeName'])
    cen={t:(st.mean(ch['x'] for ch in r0['champions'] if ch['team']==t), st.mean(ch['y'] for ch in r0['champions'] if ch['team']==t)) for t in (0,1)}
    for gi,d in grp.items():
        c=(st.mean(d['xs']),st.mean(d['ys'])); d0,d1=cheb(c,cen[0]),cheb(c,cen[1])
        d['where']={t:('mid' if abs(d0-d1)<=6 else ('own' if (d0<d1)==(t==0) else 'their')) for t in (0,1)}
        d['kind']='mono' if 'monolith' in d['kinds'] else ('elk' if 'elk' in d['kinds'] else ('wolf' if 'wolf' in d['kinds'] else ('golem' if 'golem' in d['kinds'] else ('gem' if 'gem_cluster' in d['kinds'] else 'gold'))))
    rec={'res':g['result'],'rival':g['rival'],'map':g['map']}
    for w,(lo,hi) in (('a',(0,150)),('b',(150,300))):
        alive={0:0,1:0}; caps={0:collections.Counter(),1:collections.Counter()}; gems={0:0,1:0}; where={0:collections.Counter(),1:collections.Counter()}; ncap={0:0,1:0}; prev={}
        for r in rows:
            if not (lo<r['round']<=hi): 
                for c in r['camps']: prev[c['group']]=c['captureTeam']
                continue
            seen=set()
            for c in r['camps']:
                gi=c['group']
                if gi in seen: continue
                seen.add(gi); ct=c['captureTeam']
                if prev.get(gi,2) not in (0,1) and ct in (0,1):
                    d=grp[gi]; gems[ct]+=d['gems']; ncap[ct]+=1; caps[ct][d['kind']]+=1; where[ct][d['where'][ct]]+=1
                prev[gi]=ct
            for ch in r['champions']:
                if ch['alive']: alive[ch['team']]+=1
        for who,t in (('u',us),('t',1-us)):
            rec[who+'alive'+w]=alive[t]; rec[who+'gems'+w]=gems[t]; rec[who+'ncap'+w]=ncap[t]; rec[who+'caps'+w]=caps[t]; rec[who+'where'+w]=where[t]
    G.append(rec)
def M(S,k): return st.mean(d[k] for d in S)
for res in ('win','loss'):
    S=[d for d in G if d['res']==res]
    if not S: continue
    print(f"=== {pref} {res} {len(S)} games")
    for w,lab in (('a','r1-150'),('b','r151-300')):
        for who,nm in (('u','us '),('t','riv')):
            al=M(S,who+'alive'+w); gm=M(S,who+'gems'+w); nc=M(S,who+'ncap'+w)
            kinds=collections.Counter(); wh=collections.Counter()
            for d in S: kinds.update(d[who+'caps'+w]); wh.update(d[who+'where'+w])
            n=len(S)
            print(f"  {lab:9s} {nm}: alive champ-rounds {al:5.0f} ({al/150:.2f} alive avg), captures {nc:5.2f}, gems {gm:5.1f}, gems/100 alive-rounds {100*gm/max(al,1):.1f}, caps/100 alive-rounds {100*nc/max(al,1):.2f} | kinds "+", ".join(f"{k} {v/n:.2f}" for k,v in kinds.most_common())+" | where "+", ".join(f"{k} {v/n:.2f}" for k,v in wh.most_common()))

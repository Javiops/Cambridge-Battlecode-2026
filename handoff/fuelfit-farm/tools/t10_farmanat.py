# t10_farmanat.py : farm anatomy of the top 10 vs top 10 (pcassets/replays_t10, engine 2.0.0), both sides, by result and window
# (r1-150, r151-300): alive champion-rounds, captures, gems (per-capture group reward), gems per 100 alive champion-rounds, kinds,
# champions within 4 of the camp at capture, strong-group (str >= 120) captures, pack share (alive champion-rounds with >= 2 allies
# within 10). Compare with our c34 numbers (c34_farmanat.py, c34_pack.py, c34_elkcost.py).
import sys,glob,pickle,os,json,re,collections,statistics as st
idx={g['file'].split('/')[-1]:g for g in json.load(open('/tmp/claude-0/ff/t10/index.json'))}
STR={'wolf':20,'elk':60,'gem_cluster':0,'gold_cluster':0,'monolith':200,'golem':120}
MINR=int(os.environ.get('MINR','300'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
A=collections.defaultdict(list); PACK=collections.defaultdict(collections.Counter); NG=collections.Counter(); TEAM=collections.defaultdict(collections.Counter)
for f in glob.glob('/tmp/claude-0/ff/gem/cache/t10__A_A_*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or rows[-1]['round']<MINR: continue
    name=os.path.basename(f).replace('t10__A_A_','').replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    grp={}
    for c in rows[0]['camps']:
        d=grp.setdefault(c['group'],{'gems':c['rewardGems'],'xs':[],'ys':[],'str':0,'kinds':set()}); d['xs'].append(c['spawnX']); d['ys'].append(c['spawnY']); d['str']+=STR.get(c['typeName'],0); d['kinds'].add(c['typeName'])
    for d in grp.values():
        d['c']=(st.mean(d['xs']),st.mean(d['ys'])); d['kind']='mono' if 'monolith' in d['kinds'] else ('elk' if 'elk' in d['kinds'] else ('wolf' if 'wolf' in d['kinds'] else ('golem' if 'golem' in d['kinds'] else ('gem' if 'gem_cluster' in d['kinds'] else 'gold'))))
    res={0:g['a_result'],1:g['b_result']}; tname={0:g['a'],1:g['b']}
    for t in (0,1): NG[res[t]]+=1
    W={(t,w):{'alive':0,'ncap':0,'gems':0,'kinds':collections.Counter(),'n':collections.Counter(),'strong':[],'poor':0} for t in (0,1) for w in ('a','b')}
    prev={}
    for r in rows:
        if r['round']<1 or r['round']>300: 
            for c in r['camps']: prev[c['group']]=c['captureTeam']
            continue
        w='a' if r['round']<=150 else 'b'
        chs={t:[ch for ch in r['champions'] if ch['team']==t and ch['alive']] for t in (0,1)}
        for t in (0,1):
            W[(t,w)]['alive']+=len(chs[t])
            for ch in chs[t]:
                n10=sum(1 for o in chs[t] if o is not ch and cheb((o['x'],o['y']),(ch['x'],ch['y']))<=10)
                p=PACK[res[t]]; p['n']+=1; p['a2']+=n10>=2; p['a1']+=n10>=1; p['a3']+=n10>=3
        for c in r['camps']:
            gi=c['group']; ct=c['captureTeam']
            if prev.get(gi,2) not in (0,1) and ct in (0,1):
                d=grp[gi]; x=W[(ct,w)]; x['ncap']+=1; x['gems']+=d['gems']; x['kinds'][d['kind']]+=1
                n=sum(1 for ch in chs[ct] if cheb((ch['x'],ch['y']),d['c'])<=4); x['n'][min(n,4)]+=1
                if d['gems']<20: x['poor']+=1
                if d['str']>=120: x['strong'].append((d['gems'],n,r['round']))
            prev[gi]=ct
    for t in (0,1):
        for w in ('a','b'): A[(res[t],w)].append(W[(t,w)])
        TEAM[tname[t]]['games']+=1; TEAM[tname[t]]['wins']+=res[t]=='win'; TEAM[tname[t]]['gems_b']+=W[(t,'b')]['gems']; TEAM[tname[t]]['alive_b']+=W[(t,'b')]['alive']; TEAM[tname[t]]['strong']+=len(W[(t,'b')]['strong'])+len(W[(t,'a')]['strong'])
print(f"top10 vs top10 games used: {NG['win']} (team-sides: {dict(NG)})")
for res in ('win','loss'):
    for w,lab in (('a','r1-150'),('b','r151-300')):
        S=A[(res,w)]; n=len(S)
        if not n: continue
        al=st.mean(x['alive'] for x in S); gm=st.mean(x['gems'] for x in S); nc=st.mean(x['ncap'] for x in S)
        kinds=collections.Counter(); nn=collections.Counter(); strong=[]
        for x in S: kinds.update(x['kinds']); nn.update(x['n']); strong+=x['strong']
        tot=sum(nn.values())
        print(f"  {res:4s} {lab:9s}: alive champ-rounds {al:5.0f} ({al/150:.2f}), captures {nc:5.2f}, gems {gm:5.1f}, gems/100 alive-rounds {100*gm/al:.1f}, gems/capture {gm/max(nc,0.01):.1f}, poor share {100*sum(x['poor'] for x in S)/max(1,sum(x['ncap'] for x in S)):.0f}% | kinds "+", ".join(f"{k} {v/n:.2f}" for k,v in kinds.most_common())+f" | champions within 4 at capture: "+", ".join(f"{k}:{100*v/tot:.0f}%" for k,v in sorted(nn.items()))+f" | strong (str>=120) caps/game {len(strong)/n:.2f}, gems median {st.median(s[0] for s in strong) if strong else 0:.0f}, capturers {dict(collections.Counter(min(s[1],4) for s in strong))}")
    p=PACK[res]; print(f"  {res:4s} pack r1-300: allies within 10 >=1 {100*p['a1']/p['n']:.0f}%, >=2 {100*p['a2']/p['n']:.0f}%, >=3 {100*p['a3']/p['n']:.0f}%")
print("per team (r151-300): "+"; ".join(f"{k} {v['wins']}/{v['games']} gems {v['gems_b']/v['games']:.0f} alive {v['alive_b']/v['games']/150:.2f} strong/game {v['strong']/v['games']:.2f}" for k,v in sorted(TEAM.items(), key=lambda kv:-kv[1]['wins']/max(1,kv[1]['games']))))

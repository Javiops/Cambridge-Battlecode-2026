# c34_winlose.py SET : per game, result (from index) vs r300 metrics: gems collected (sum of captured group gems by us/them), deaths <=300, gold captured
import sys,glob,pickle,os,json,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import cheb
from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
rows_by=[]
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1
    import re; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: print('no index for',name); continue
    r0=rows[0]; ggems={}; ggold={}
    for c in r0['camps']: ggems[c['group']]=ggems.get(c['group'],0)+c['rewardGems']; ggold[c['group']]=ggold.get(c['group'],0)+c['rewardGold']
    gems={0:0,1:0}; gold={0:0,1:0}; prev={}
    for r in rows:
        seen=set()
        for c in r['camps']:
            gi=c['group']
            if gi in seen: continue
            seen.add(gi); ct=c['captureTeam']
            if prev.get(gi,2) not in (0,1) and ct in (0,1): gems[ct]+=ggems[gi]; gold[ct]+=ggold[gi]
            prev[gi]=ct
    deaths={0:0,1:0}; pv={}
    for r in rows:
        for ch in r['champions']:
            k=(ch['team'],ch['index']); p=pv.get(k)
            if p and p['alive'] and not ch['alive']: deaths[ch['team']]+=1
            pv[k]=ch
    rows_by.append({'res':g['result'],'map':g['map'],'rival':g['rival'],'dg':gems[us]-gems[1-us],'dgold':gold[us]-gold[1-us],'dd':deaths[us]-deaths[1-us],'gems':gems[us],'tgems':gems[1-us]})
W=[d for d in rows_by if d['res']=='win']; L=[d for d in rows_by if d['res']!='win']
print(pref,'games',len(rows_by),'wins',len(W),'losses',len(L))
for name,S in (('WIN',W),('LOSS',L)):
    print(f"  {name}: gems r300 us {st.mean(d['gems'] for d in S):.0f} them {st.mean(d['tgems'] for d in S):.0f}; gem lead median {st.median(d['dg'] for d in S):+.0f}; gold lead median {st.median(d['dgold'] for d in S):+.0f}; death diff (us-them) mean {st.mean(d['dd'] for d in S):+.2f}")
ahead=[d for d in rows_by if d['dg']>0]; behind=[d for d in rows_by if d['dg']<0]
print(f"  gem lead at r300 > 0: {len(ahead)} games, won {sum(1 for d in ahead if d['res']=='win')}; lead < 0: {len(behind)}, won {sum(1 for d in behind if d['res']=='win')}")
big=[d for d in rows_by if d['dg']>=40]; print(f"  lead >= 40 gems at r300: {len(big)}, won {sum(1 for d in big if d['res']=='win')}; lead <= -40: {sum(1 for d in rows_by if d['dg']<=-40)}, won {sum(1 for d in rows_by if d['dg']<=-40 and d['res']=='win')}")
print('  by rival:', dict(collections.Counter((d['rival'][:14],d['res']) for d in rows_by).most_common(12)))

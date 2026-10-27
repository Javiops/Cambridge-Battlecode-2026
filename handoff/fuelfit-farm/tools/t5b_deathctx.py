# t5b_deathctx.py SET LO HI : context of each death in (LO,HI] for both sides: nearest live camp group (kind, gold, str), allies within 6,
# enemies within 8 in the 5 rounds before, gems carried, side of the map, what the dying champion had been doing (at camp / moving)
import sys,glob,pickle,os,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import analyse, cheb
from cmpwin2 import ok
pref=sys.argv[1]; LO=int(os.environ.get("LO","150")); HI=int(os.environ.get("HI","300")); files=glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl')
STR={'elk':60,'wolf':20,'monolith':200,'golem':120}
OUT={'us':[], 't5':[]}; n=0
for f in files:
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; n+=1
    r0=rows[0]; groups=collections.defaultdict(list)
    for c in r0['camps']: groups[c['group']].append(c)
    G={g:{'cen':(st.mean(c['spawnX'] for c in cs), st.mean(c['spawnY'] for c in cs)),'gold':sum(c['rewardGold'] for c in cs),'gems':sum(c['rewardGems'] for c in cs),'str':sum(STR.get(c['typeName'],0) for c in cs),'kind':'+'.join(sorted(set(c['typeName'] for c in cs)))} for g,cs in groups.items()}
    sp={t:[(c['x'],c['y']) for c in r0['champions'] if c['team']==t] for t in (0,1)}
    spc={t:(st.mean(p[0] for p in sp[t]), st.mean(p[1] for p in sp[t])) for t in (0,1)}
    byr={r['round']:r for r in rows}; rounds=sorted(byr)
    # live state per round: group captured (captureTeam in 0/1) means cleared recently -> not live; approximate live = captureTeam==2
    prev={}
    for ri,r in enumerate(rows):
        if r['round']>HI: break
        live={c['group']:(c['captureTeam'] not in (0,1)) for c in r['camps']}
        for ch in r['champions']:
            k=(ch['team'],ch['index']); p=prev.get(k)
            if p and p['alive'] and not ch['alive'] and LO<r['round']<=HI:
                t=ch['team']; who='us' if t==us else 't5'; pos=(p['x'],p['y'])
                # nearest live group within 5
                near=[(cheb(pos,G[g]['cen']),g) for g in G if live.get(g,True) and cheb(pos,G[g]['cen'])<=5]
                near.sort(); ng=G[near[0][1]] if near else None
                allies=sum(1 for c in r['champions'] if c['team']==t and c['alive'] and c['index']!=ch['index'] and cheb((c['x'],c['y']),pos)<=6)
                ens=0; enseen=0
                for rr in rows[max(0,ri-5):ri+1]:
                    e=sum(1 for c in rr['champions'] if c['team']!=t and c['alive'] and cheb((c['x'],c['y']),pos)<=8); ens=max(ens,e)
                    enseen=max(enseen, sum(1 for c in rr['champions'] if c['team']!=t and c['alive'] and cheb((c['x'],c['y']),pos)<=12))
                du=cheb(pos,spc[t]); dt=cheb(pos,spc[1-t]); side='own' if du<dt-2 else ('their' if dt<du-2 else 'mid')
                # activity in the 10 rounds before: fraction of rounds within 2 of a live group centre
                atcamp=0; tot=0
                for rr in rows[max(0,ri-10):ri]:
                    c2=next((c for c in rr['champions'] if (c['team'],c['index'])==k),None)
                    if c2 and c2['alive']:
                        tot+=1; lv={c['group']:(c['captureTeam'] not in (0,1)) for c in rr['camps']}
                        if any(lv.get(g,True) and cheb((c2['x'],c2['y']),G[g]['cen'])<=2 for g in G): atcamp+=1
                OUT[who].append({'r':r['round'],'type':ch['typeName'],'gems':p['gems'],'side':side,'allies':allies,'en8':ens,'en12':enseen,'atcamp':atcamp/max(1,tot),'grp':ng})
            prev[k]=ch
print(pref,'clean',n, f'deaths r{LO}-{HI}')
for who in ('us','t5'):
    L=OUT[who]; m=len(L)
    print(f"=== {who}: {m/n:.2f} deaths/game")
    print(f"  side own/mid/their {sum(1 for d in L if d['side']=='own')/m*100:.0f}/{sum(1 for d in L if d['side']=='mid')/m*100:.0f}/{sum(1 for d in L if d['side']=='their')/m*100:.0f}% | no ally within 6: {sum(1 for d in L if d['allies']==0)/m*100:.0f}% | enemies within 8 in the last 5 rounds: 0:{sum(1 for d in L if d['en8']==0)/m*100:.0f}% 1:{sum(1 for d in L if d['en8']==1)/m*100:.0f}% 2:{sum(1 for d in L if d['en8']==2)/m*100:.0f}% 3+:{sum(1 for d in L if d['en8']>=3)/m*100:.0f}% | gems carried mean {st.mean(d['gems'] for d in L):.0f}")
    print(f"  was at a live camp (>=50% of the last 10 rounds within 2): {sum(1 for d in L if d['atcamp']>=0.5)/m*100:.0f}% | nearest live group within 5 at death: none {sum(1 for d in L if d['grp'] is None)/m*100:.0f}%, " + ', '.join(f"{k} {v/m*100:.0f}%" for k,v in collections.Counter(d['grp']['kind'] for d in L if d['grp']).most_common(6)))
    big=[d for d in L if d['grp'] and d['grp']['gold']>=300]; print(f"  at a big gold group (>=300): {len(big)/m*100:.0f}%; at a group with str>=60: {sum(1 for d in L if d['grp'] and d['grp']['str']>=60)/m*100:.0f}% | enemies 0 within 8 AND at camp (monsters killed us): {sum(1 for d in L if d['en8']==0 and d['atcamp']>=0.5)/m*100:.0f}%")
    print('  by champion:', dict(collections.Counter(d['type'] for d in L).most_common()))

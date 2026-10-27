# t10_plan.py [OUT.md] : game plan by map and 50-round window, top 10 vs top 10 (both sides, 599 games) against ours (e1foco in c34,
# our side only), on the maps both samples share. Per window: captures per team-game by kind and position (own half / mid / their half,
# by distance to each team's r0 centroid), gems, champions within 4 of the camp at capture, home trips per team (a champion back within
# 3 of its spawn centroid after being 8+ away; gems carried on return) and the alive count. Group reward = per-capture engine value.
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from cmpwin2 import ok
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/claude-0/ff/t10/t10_plan.md'
STR={'wolf':20,'elk':60,'gem_cluster':0,'gold_cluster':0,'monolith':200,'golem':120}
WIN=[(1,50),(51,100),(101,150),(151,200),(201,250),(251,300)]
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def kind(d):
    k=d['kinds']
    if 'monolith' in k: return 'mono'
    if d['str']>=120: return 'strong'
    if 'elk' in k: return 'elk'
    if 'golem' in k: return 'golem'
    if 'wolf' in k: return 'wolf'
    return 'gem' if 'gem_cluster' in k else 'gold'
def analyse(rows, teams, label):
    """teams: list of team ids to analyse; returns list of per-team dicts {w: stats}"""
    grp={}
    for c in rows[0]['camps']:
        d=grp.setdefault(c['group'],{'gems':c['rewardGems'],'xs':[],'ys':[],'str':0,'kinds':set()}); d['xs'].append(c['spawnX']); d['ys'].append(c['spawnY']); d['str']+=STR.get(c['typeName'],0); d['kinds'].add(c['typeName'])
    cen={t:(st.mean(ch['x'] for ch in rows[0]['champions'] if ch['team']==t), st.mean(ch['y'] for ch in rows[0]['champions'] if ch['team']==t)) for t in (0,1)}
    for d in grp.values():
        d['c']=(st.mean(d['xs']),st.mean(d['ys'])); d0,d1=cheb(d['c'],cen[0]),cheb(d['c'],cen[1])
        d['side']={t:('mid' if abs(d0-d1)<=6 else ('own' if (d0<d1)==(t==0) else 'their')) for t in (0,1)}; d['kind']=kind(d)
    res={t:{w:{'caps':collections.Counter(),'gems':0,'n':[],'home':0,'homegems':[],'alive':0,'ncap':0} for w in WIN} for t in teams}
    prev={}; far={}; lastg={}
    for r in rows:
        rd=r['round']
        if rd<1 or rd>300:
            for c in r['camps']: prev[c['group']]=c['captureTeam']
            continue
        w=next(x for x in WIN if x[0]<=rd<=x[1])
        chs={t:[ch for ch in r['champions'] if ch['team']==t and ch['alive']] for t in (0,1)}
        for t in teams:
            res[t][w]['alive']+=len(chs[t])
            for ch in chs[t]:
                k=(t,ch['index']); dd=cheb((ch['x'],ch['y']),cen[t])
                if dd>=8: far[k]=True
                elif dd<=3 and far.get(k):
                    far[k]=False; res[t][w]['home']+=1; res[t][w]['homegems'].append(lastg.get(k,0))
                lastg[k]=ch.get('gems') or 0
        for c in r['camps']:
            gi=c['group']; ct=c['captureTeam']
            if prev.get(gi,2) not in (0,1) and ct in (0,1) and ct in teams:
                d=grp[gi]; x=res[ct][w]; x['caps'][(d['kind'],d['side'][ct])]+=1; x['gems']+=d['gems']; x['ncap']+=1
                x['n'].append(sum(1 for ch in chs[ct] if cheb((ch['x'],ch['y']),d['c'])<=4))
            prev[gi]=ct
    return [res[t] for t in teams]
# top 10
idx={g['file'].split('/')[-1]:g for g in json.load(open('/tmp/claude-0/ff/t10/index.json'))}
T10=collections.defaultdict(list)
for f in glob.glob('/tmp/claude-0/ff/gem/cache/t10__A_A_*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or rows[-1]['round']<300: continue
    g=idx.get(os.path.basename(f).replace('t10__A_A_','').replace('.r300h.pkl',''))
    if not g: continue
    for r_ in analyse(rows,[0,1],'t10'): T10[g['map']].append(r_)
# ours (e1foco, c34)
cidx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']=='e1foco'}
US=collections.defaultdict(list); RIV=collections.defaultdict(list)
for f in glob.glob('/tmp/claude-0/ff/gem/cache/c34_e1foco__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(r'^c34_e1foco__c34_e1foco_[AB]_','',b).replace('.r300h.pkl','')
    g=cidx.get(name)
    if not g: continue
    a,b2=analyse(rows,[us,1-us],'c34'); US[g['map']].append(a); RIV[g['map']].append(b2)
def agg(L,w):
    n=len(L)
    if not n: return None
    caps=collections.Counter(); gems=0; ns=[]; home=0; hg=[]; alive=0
    for x in L: caps.update(x[w]['caps']); gems+=x[w]['gems']; ns+=x[w]['n']; home+=x[w]['home']; hg+=x[w]['homegems']; alive+=x[w]['alive']
    return {'n':n,'caps':caps,'gems':gems/n,'ncap':sum(caps.values())/n,'n4':collections.Counter(min(v,4) for v in ns),'home':home/n,'homegems':st.median(hg) if hg else 0,'alive':alive/n/50}
def fmt(a):
    if not a: return 'no games'
    order=sorted(a['caps'].items(), key=lambda kv:-kv[1])
    tot=sum(a['n4'].values()) or 1
    return (f"caps {a['ncap']:.1f}/g gems {a['gems']:.0f} alive {a['alive']:.2f} | " + ", ".join(f"{k}-{s} {v/a['n']:.1f}" for (k,s),v in order[:6]) +
            f" | with 1:{100*a['n4'][1]/tot:.0f}% 2:{100*a['n4'][2]/tot:.0f}% 3+:{100*(a['n4'][3]+a['n4'][4])/tot:.0f}% | home {a['home']:.1f}/team, gems carried {a['homegems']:.0f}")
lines=[f"# Game plan by map and 50-round window: top 10 vs top 10 (599 games of 10-27, both sides) vs ours (e1foco in c34 vs ranks 56-70) and the c34 rivals",
"Per window: captures per team-game, kind-side (own = our half, mid = within 6 of equidistant, their = their half), champions within 4 of the camp at capture, home trips per team (back within 3 of spawn after 8+ away) with the median gems carried, alive champions.",
"kind: strong = str >= 120 (two elks or more); elk / wolf = groups with that monster; gem / gold = clusters only; mono = monolith group.", ""]
lines.append("## ALL MAPS")
for w in WIN:
    lines.append(f"### r{w[0]}-{w[1]}")
    lines.append(f"- top10 : {fmt(agg([x for L in T10.values() for x in L],w))}")
    lines.append(f"- ours  : {fmt(agg([x for L in US.values() for x in L],w))}")
    lines.append(f"- c34riv: {fmt(agg([x for L in RIV.values() for x in L],w))}")
shared=sorted(set(T10)&set(US), key=lambda m:-len(US[m]))
lines.append(f"\n## SHARED MAPS ({len(shared)}): "+", ".join(f"{m} (t10 {len(T10[m])//2}, ours {len(US[m])})" for m in shared))
for m in shared:
    lines.append(f"\n## {m}  (top10 games {len(T10[m])//2}, ours {len(US[m])})")
    for w in WIN:
        lines.append(f"### r{w[0]}-{w[1]}")
        lines.append(f"- top10 : {fmt(agg(T10[m],w))}")
        lines.append(f"- ours  : {fmt(agg(US[m],w))}")
        lines.append(f"- c34riv: {fmt(agg(RIV[m],w))}")
t10only=sorted(set(T10)-set(US), key=lambda m:-len(T10[m]))
lines.append(f"\n## TOP-10 MAPS NOT IN OUR c34 SAMPLE ({len(t10only)})")
for m in t10only:
    lines.append(f"\n## {m}  (top10 games {len(T10[m])//2})")
    for w in WIN: lines.append(f"- r{w[0]}-{w[1]} top10: {fmt(agg(T10[m],w))}")
open(OUT,'w').write("\n".join(lines)+"\n"); print(OUT, len(lines),'lines; shared maps',len(shared))

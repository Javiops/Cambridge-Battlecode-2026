# c34_choice.py SET : the choice test. For every capture by us (and by the rival) in r151-300, by result: the group's gems, and whether a
# richer uncaptured group (>= RICH gems, respawned, not held by anybody) was available within D tiles of the capturing champion on our
# half or mid. Also the richest available group's gems/str and distance. Group reward is per capture (engine value).
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]; RICH=int(os.environ.get('RICH','20')); D=int(os.environ.get('D','15')); LO,HI=150,300
STR={'wolf':20,'elk':60,'gem_cluster':0,'gold_cluster':0,'monolith':200,'golem':120}
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
R=collections.defaultdict(list)
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    r0=rows[0]; grp={}
    for c in r0['camps']:
        d=grp.setdefault(c['group'],{'gems':c['rewardGems'],'gold':c['rewardGold'],'xs':[],'ys':[],'kinds':set(),'str':0})
        d['xs'].append(c['spawnX']); d['ys'].append(c['spawnY']); d['kinds'].add(c['typeName']); d['str']+=STR.get(c['typeName'],0)
    cen={t:(st.mean(ch['x'] for ch in r0['champions'] if ch['team']==t), st.mean(ch['y'] for ch in r0['champions'] if ch['team']==t)) for t in (0,1)}
    for gi,d in grp.items():
        d['c']=(st.mean(d['xs']),st.mean(d['ys'])); d0,d1=cheb(d['c'],cen[0]),cheb(d['c'],cen[1])
        d['side']={t:('mid' if abs(d0-d1)<=6 else ('own' if (d0<d1)==(t==0) else 'their')) for t in (0,1)}
    prev={}; state={}  # state[gi] = captureTeam seen last (2 = alive/uncaptured)
    for r in rows:
        seen=set(); caps=[]
        for c in r['camps']:
            gi=c['group']
            if gi in seen: continue
            seen.add(gi); ct=c['captureTeam']
            if prev.get(gi,2) not in (0,1) and ct in (0,1) and LO<r['round']<=HI: caps.append((gi,ct))
            prev[gi]=ct
        for gi,ct in caps:
            d=grp[gi]; who='us' if ct==us else 'riv'
            # capturing champion: the alive champion of team ct nearest the group centre
            chs=[ch for ch in r['champions'] if ch['team']==ct and ch['alive']]
            if not chs: continue
            cap=min(chs, key=lambda ch: cheb((ch['x'],ch['y']),d['c']))
            # available richer groups: uncaptured (prev==2 and not just captured), gems >= RICH, on ct's own half or mid, within D of the capturer
            avail=[]
            for gj,e in grp.items():
                if gj==gi or prev.get(gj,2) in (0,1) or e['gems']<RICH or e['side'][ct]=='their': continue
                dd=cheb((cap['x'],cap['y']),e['c'])
                if dd<=D: avail.append((e['gems'],e['str'],dd))
            n_en=sum(1 for ch in r['champions'] if ch['team']!=ct and ch['alive'] and cheb((ch['x'],ch['y']),(cap['x'],cap['y']))<=8)
            n_al=sum(1 for ch in chs if ch is not cap and cheb((ch['x'],ch['y']),(cap['x'],cap['y']))<=6)
            R[(g['result'],who)].append({'gems':d['gems'],'gold':d['gold'],'str':d['str'],'side':d['side'][ct],'poor':d['gems']<RICH,'avail':avail,'best':max(avail) if avail else None,'r':r['round'],'en':n_en,'al':n_al,'map':g['map']})
n_games={res:sum(1 for x in idx.values() if x['result']==res) for res in ('win','loss')}
for res in ('win','loss'):
    for who in ('us','riv'):
        L=R[(res,who)]
        if not L: continue
        poor=[x for x in L if x['poor']]; pa=[x for x in poor if x['avail']]
        print(f"=== {pref} {res} {who}: {len(L)} captures r151-300; gems/capture {st.mean(x['gems'] for x in L):.1f}; poor (<{RICH} gems) {len(poor)} ({100*len(poor)//len(L)}%), of which a rich group was free within {D}: {len(pa)} ({100*len(pa)//max(1,len(poor))}%)")
        if pa: print(f"    when free: richest free group gems median {st.median(x['best'][0] for x in pa):.0f}, str median {st.median(x['best'][1] for x in pa):.0f}, distance median {st.median(x['best'][2] for x in pa):.0f}; capturer allies within 6 median {st.median(x['al'] for x in pa)}, enemies within 8 median {st.median(x['en'] for x in pa)}; free group str dist {dict(collections.Counter(min(x['best'][1],180) for x in pa).most_common(6))}")
        rich=[x for x in L if not x['poor']]
        if rich: print(f"    rich captures {len(rich)}: gems median {st.median(x['gems'] for x in rich):.0f}, str median {st.median(x['str'] for x in rich):.0f}, side {dict(collections.Counter(x['side'] for x in rich))}, allies within 6 median {st.median(x['al'] for x in rich)}")
        print(f"    side of all captures {dict(collections.Counter(x['side'] for x in L))}; poor kinds: gold-only {sum(1 for x in poor if x['gems']==0)}, tiny gem {sum(1 for x in poor if 0<x['gems']<RICH)}")

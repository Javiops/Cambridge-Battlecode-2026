import json,collections,sys,statistics as st
NEAR=set("collision eight contest corners corridors elk_arena elkring gem_fields gemfight gold_rush hooks lost_world monolith quadrants reverse_spiral rushbait_v2 stampede starfish swirl the_farm yellow_brick_road boss_battle broken_curve fragment interlock packs".split())
idx,dec=sys.argv[1],sys.argv[2]; onlynear=len(sys.argv)>3 and sys.argv[3]=='near'
d=json.load(open(idx))['pairs']
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
out=collections.defaultdict(list); res=collections.Counter(); sep=collections.defaultdict(list)
for it in d:
    team=0 if it['side']=='a' else 1; mp=it['map'][2:]
    if onlynear and mp not in NEAR: continue
    for t in ('base','cand'):
        res[t,it[t]['result']]+=1
        rows=[json.loads(l) for l in open(f'{dec}/{it[t]["match"]}.jsonl')]; rows=[r for r in rows if 'round' in r]
        prev={}
        for i,r in enumerate(rows):
            rd=r['round']
            ours=[c for c in r['champions'] if c['team']==team]; theirs=[c for c in r['champions'] if c['team']!=team and c['alive']]
            # separation: for alive ours, dist to nearest alive ally, r50-300
            if 50<=rd<=300:
                al=[c for c in ours if c['alive']]
                for c in al:
                    o=[cheb((c['x'],c['y']),(a['x'],a['y'])) for a in al if a['index']!=c['index']]
                    if o: sep[t].append(min(o))
            for c in ours:
                k=c['index']
                if k in prev and prev[k]['alive'] and not c['alive'] and rd<=400:
                    p=(prev[k]['x'],prev[k]['y'])
                    foes4=sum(1 for e in theirs if cheb((e['x'],e['y']),p)<=4)
                    allies5=sum(1 for a in ours if a['index']!=k and a['alive'] and cheb((a['x'],a['y']),p)<=5)
                    # nearest ally distance 10 rounds before death
                    sep10=None
                    if i>=10:
                        pr=[x for x in rows[i-10]['champions'] if x['team']==team and x['alive']]
                        me=[x for x in pr if x['index']==k]
                        if me:
                            o=[cheb((me[0]['x'],me[0]['y']),(a['x'],a['y'])) for a in pr if a['index']!=k]
                            sep10=min(o) if o else None
                    out[t].append(dict(map=mp,r=rd,who=c['typeName'],foes4=foes4,allies5=allies5,sep10=sep10,gems=prev[k]['gems']))
                prev[k]=c
print('results',dict(res))
for t in ('base','cand'):
    L=out[t]; L100=[x for x in L if 100<x['r']<=300]; L0=[x for x in L if x['r']<=100]
    print(t,'deaths<=400',len(L),' <=100',len(L0),' r100-300',len(L100),' gems lost(r100-300)',sum(x['gems'] for x in L100))
    if L100:
        print('   alone(allies5=0)',sum(1 for x in L100 if x['allies5']==0),'outnumbered',sum(1 for x in L100 if x['foes4']>x['allies5']+1),'no foe',sum(1 for x in L100 if x['foes4']==0),
              'sep10>=6',sum(1 for x in L100 if x['sep10'] is not None and x['sep10']>=6),'sep10 median',st.median([x['sep10'] for x in L100 if x['sep10'] is not None]))
        print('   by champ',collections.Counter(x['who'] for x in L100).most_common())
    if sep[t]: print('   alive nearest-ally dist r50-300: mean',round(st.mean(sep[t]),2),'frac>=6',round(sum(1 for s in sep[t] if s>=6)/len(sep[t]),3))

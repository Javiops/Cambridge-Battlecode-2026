import json,collections,sys,statistics as st
NEAR=set("collision eight contest corners corridors elk_arena elkring gem_fields gemfight gold_rush hooks lost_world monolith quadrants reverse_spiral rushbait_v2 stampede starfish swirl the_farm yellow_brick_road boss_battle broken_curve fragment interlock packs".split())
idx,dec=sys.argv[1],sys.argv[2]; onlynear=len(sys.argv)>3
d=json.load(open(idx))['pairs']
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def clusters(pts,th=6):
    n=len(pts); seen=[False]*n; k=0
    for i in range(n):
        if seen[i]: continue
        k+=1; stack=[i]; seen[i]=True
        while stack:
            a=stack.pop()
            for b in range(n):
                if not seen[b] and cheb(pts[a],pts[b])<=th: seen[b]=True; stack.append(b)
    return k
agg=collections.defaultdict(lambda: collections.defaultdict(list))
for it in d:
    team=0 if it['side']=='a' else 1; mp=it['map'][2:]
    if onlynear and mp not in NEAR: continue
    for t in ('base','cand'):
        rows=[json.loads(l) for l in open(f'{dec}/{it[t]["match"]}.jsonl')]; rows=[r for r in rows if 'round' in r]
        A=agg[t]; sub_prev=0; subs=[]
        for r in rows:
            rd=r['round']
            if rd>300: break
            ours=[c for c in r['champions'] if c['team']==team and c['alive']]
            sg=r.get('submittedGems',[0,0])[team]
            if sg>sub_prev: subs.append(rd); sub_prev=sg
            if 50<=rd<=300 and ours:
                A['carried'].append(sum(c['gems'] for c in ours)/len(ours))
                A['maxcarried'].append(max(c['gems'] for c in ours))
                A['clusters'].append(clusters([(c['x'],c['y']) for c in ours]))
                A['split'].append(1 if clusters([(c['x'],c['y']) for c in ours])>=2 else 0)
        A['sub150'].append(sum(1 for s in subs if s<=150)); A['sub300'].append(len(subs))
        A['gems300'].append(sub_prev)
for t in ('base','cand'):
    A=agg[t]
    print(t,'carried/champ r50-300 mean',round(st.mean(A['carried']),2),'max-carrier mean',round(st.mean(A['maxcarried']),2),
          'clusters mean',round(st.mean(A['clusters']),2),'frac split',round(st.mean(A['split']),3),
          'subs<=150/game',round(st.mean(A['sub150']),2),'subs<=300',round(st.mean(A['sub300']),2),'gems submitted by r300/game',round(st.mean(A['gems300']),1))

import json,collections,sys,statistics as st
NEAR=set("collision eight contest corners corridors elk_arena elkring gem_fields gemfight gold_rush hooks lost_world monolith quadrants reverse_spiral rushbait_v2 stampede starfish swirl the_farm yellow_brick_road boss_battle broken_curve fragment interlock packs".split())
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for idx,dec,tag in [('/mnt/project-files/online/data/c20_b32_changed27/index.json','/tmp/c20/dec','c20'),('/mnt/project-files/online/data/c19_b27_changed37/index.json','/tmp/c19/dec','c19')]:
    d=json.load(open(idx))['pairs']
    for t in ('base','cand'):
        H=collections.Counter(); first=[]; kind=collections.Counter()
        for it in d:
            team=0 if it['side']=='a' else 1; mp=it['map'][2:]
            if mp not in NEAR: continue
            rows=[json.loads(l) for l in open(f'{dec}/{it[t]["match"]}.jsonl')]; rows=[r for r in rows if 'round' in r]
            prev={}; fd=None
            for i,r in enumerate(rows):
                rd=r['round']
                if rd>300: break
                for c in r['champions']:
                    if c['team']!=team: continue
                    k=c['index']
                    if k in prev and prev[k]['alive'] and not c['alive']:
                        H[rd//50*50]+=1
                        if fd is None:
                            fd=rd; f6=0
                            if i>=6:
                                pc=[x for x in rows[i-6]['champions'] if x['team']==team and x['index']==k][0]; p6=(pc['x'],pc['y'])
                                f6=sum(1 for e in rows[i-6]['champions'] if e['team']!=team and e['alive'] and cheb((e['x'],e['y']),p6)<=6)
                            kind['enemy' if f6 else 'camp/alone']+=1
                            first.append((mp,rd,c['typeName'],'E' if f6 else 'C'))
                    prev[k]=c
        print(tag,t,'hist',[H[b] for b in range(0,300,50)],'first death kind',dict(kind))
        print('   ',sorted(first,key=lambda x:x[1])[:14])

import json,collections,sys,statistics as st
NEAR=set("collision eight contest corners corridors elk_arena elkring gem_fields gemfight gold_rush hooks lost_world monolith quadrants reverse_spiral rushbait_v2 stampede starfish swirl the_farm yellow_brick_road boss_battle broken_curve fragment interlock packs".split())
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for idx,dec,tag in [('/mnt/project-files/online/data/c20_b32_changed27/index.json','/tmp/c20/dec','c20'),('/mnt/project-files/online/data/c19_b27_changed37/index.json','/tmp/c19/dec','c19')]:
    d=json.load(open(idx))['pairs']
    for t in ('base','cand'):
        A=collections.defaultdict(list)
        for it in d:
            team=0 if it['side']=='a' else 1; mp=it['map'][2:]
            if mp not in NEAR: continue
            rows=[json.loads(l) for l in open(f'{dec}/{it[t]["match"]}.jsonl')]; rows=[r for r in rows if 'round' in r]
            sp=None; esp=None; contact=0; n=0; dsp=[]; desp=[]; fightrounds=0; adv=[]
            for r in rows:
                rd=r['round']
                if rd>300: break
                ours=[c for c in r['champions'] if c['team']==team]; theirs=[c for c in r['champions'] if c['team']!=team]
                if sp is None:
                    sp=(st.mean(c['x'] for c in ours),st.mean(c['y'] for c in ours)); esp=(st.mean(c['x'] for c in theirs),st.mean(c['y'] for c in theirs))
                if rd<20: continue
                oa=[c for c in ours if c['alive']]; ta=[c for c in theirs if c['alive']]
                for c in oa:
                    n+=1; p=(c['x'],c['y'])
                    dsp.append(cheb(p,sp)); desp.append(cheb(p,esp))
                    near=[e for e in ta if cheb((e['x'],e['y']),p)<=6]
                    if near:
                        contact+=1
                        al=sum(1 for a in oa if a['index']!=c['index'] and cheb((a['x'],a['y']),p)<=5)
                        adv.append(al+1-len(near))
                # team-level fight round: any contact
                if any(cheb((c['x'],c['y']),(e['x'],e['y']))<=6 for c in oa for e in ta): fightrounds+=1
            A['contact'].append(contact/max(1,n)); A['dsp'].append(st.mean(dsp)); A['desp'].append(st.mean(desp)); A['fr'].append(fightrounds)
            A['adv'].extend(adv)
        print(tag,t,'contact frac',round(st.mean(A['contact']),3),'fight rounds<=300/game',round(st.mean(A['fr']),1),'mean dist to own spawn',round(st.mean(A['dsp']),1),'to enemy spawn',round(st.mean(A['desp']),1),
              'local advantage in contact: mean',round(st.mean(A['adv']),2),'frac outnumbered',round(sum(1 for a in A['adv'] if a<0)/len(A['adv']),3),'frac superior',round(sum(1 for a in A['adv'] if a>0)/len(A['adv']),3))

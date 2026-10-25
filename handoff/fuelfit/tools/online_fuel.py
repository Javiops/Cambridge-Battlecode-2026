import json,zipfile,struct,re,collections,sys,statistics as st
NEAR=set("collision eight contest corners corridors elk_arena elkring gem_fields gemfight gold_rush hooks lost_world monolith quadrants reverse_spiral rushbait_v2 stampede starfish swirl the_farm yellow_brick_road boss_battle broken_curve fragment interlock packs".split())
for idx,dec,tag in [('/mnt/project-files/online/data/c20_b32_changed27/index.json','/tmp/c20/dec','c20'),('/mnt/project-files/online/data/c19_b27_changed37/index.json','/tmp/c19/dec','c19')]:
    d=json.load(open(idx))['pairs']
    for t in ('base','cand'):
        caps1=0; capsl=0; games=0; deaths=0; deaths_cap3=0; capr=collections.Counter(); mx=[]
        for it in d:
            team=0 if it['side']=='a' else 1; mp=it['map'][2:]
            if mp not in NEAR: continue
            z=zipfile.ZipFile(it[t]['replay'])
            names=[n for n in z.namelist() if n.endswith('.fuel')]
            if not names: continue
            b=z.read(names[0]); out=z.read(names[0].replace('.fuel','.stdout')).decode('utf8','replace')
            m=re.search(r'\[mapplan\] ts=(\d+)',out); ts=int(m.group(1)) if m else 4
            vals=struct.unpack_from('<%dQ'%((len(b)-13)//8), b, 13); body=vals[8:]; turns=body[ts:]
            games+=1
            t1=turns[:ts]; caps1+=sum(1 for v in t1 if v>=200000)
            R=min(400,len(turns)//ts)
            capset=set()
            for r in range(1,R):
                for i in range(ts):
                    v=turns[ts*r+i]
                    if v>=100000: capsl+=1; capset.add((r+1,i)); capr[(r+1)//50*50]+=1
            later=[turns[ts*r+i] for r in range(1,R) for i in range(ts) if turns[ts*r+i]<100000]
            if later: mx.append(st.quantiles(later,n=100)[94])
            # deaths r20-300 preceded by a capped turn of that champion within 3 rounds
            rows=[json.loads(l) for l in open(f'{dec}/{it[t]["match"]}.jsonl')]; rows=[r for r in rows if 'round' in r]
            prev={}
            for r in rows:
                rd=r['round']
                if rd>300: break
                for c in r['champions']:
                    if c['team']!=team: continue
                    k=c['index']
                    if k in prev and prev[k]['alive'] and not c['alive'] and rd>20:
                        deaths+=1
                        if any((rr,k) in capset for rr in range(rd-3,rd+1)): deaths_cap3+=1
                    prev[k]=c
        print(tag,t,'games',games,'t1 capped champs',caps1,'later capped turns',capsl,'per game',round(capsl/max(1,games),2),'by round',dict(sorted(capr.items())),'p95 later turn',round(st.median(mx)) if mx else None,'| deaths r20-300',deaths,'with a capped turn in the 3 rounds before',deaths_cap3)

# dagg.py LIST.json : from dmg/<match>.json (dmg.py), the studied team's champion damage to champions r30-300
import json,sys,collections,os
S=os.path.dirname(os.path.abspath(__file__))
L=json.load(open(sys.argv[1])); T=collections.Counter(); TY=collections.defaultdict(lambda:[0,0,0]); n=0
for fn,us in L:
    m=os.path.basename(fn).split('.')[0]; f=f'{S}/dmg/{m}.json'
    if not os.path.exists(f): continue
    d=json.load(open(f)); info={int(k):v for k,v in d['info'].items()}; n+=1
    fr=collections.Counter()
    for r,ids in d['fight'].items():
        if 30<=int(r)<=300:
            for i in ids:
                if info[i][0]==us: fr[i]+=1; T['fr']+=1
                else: T['fr_them']+=1
    for i,c in fr.items(): TY[info[i][1]][1]+=c
    for r,v in d['dmg'].items():
        if not 30<=int(r)<=300: continue
        hitters=collections.defaultdict(set)
        for k,x in v.items():
            a,b=map(int,k.split('>'))
            if info[a][0]==us:
                T['dealt']+=x; hitters[a].add(b); TY[info[a][1]][0]+=x; TY[info[a][1]][2]+=1
            else: T['taken']+=x
        if len(hitters)>=2:
            T['multi']+=1; allt=set().union(*hitters.values()); T['focus']+=len(allt)==1
        if hitters: T['hitrounds']+=len(hitters)
print(f"{sys.argv[1]:16s} g {n} dealt/game {T['dealt']/n:.0f} taken/game {T['taken']/n:.0f} ratio {T['dealt']/max(1,T['taken']):.2f} | dealt per own fight-round {T['dealt']/max(1,T['fr']):.0f} | hitting share of fight rounds {T['hitrounds']/max(1,T['fr']):.0%} | dmg per hit-round {T['dealt']/max(1,T['hitrounds']):.0f} | focus {T['focus']/max(1,T['multi']):.0%} of {T['multi']/n:.0f}/game multi-hitter rounds")
print('   by type (dmg per fight-round, per hit-round):',' '.join(f"{t} {v[0]/max(1,v[1]):.0f}/{v[0]/max(1,v[2]):.0f}" for t,v in sorted(TY.items(),key=lambda x:-x[1][1]) if v[1]>200))

import json,collections,re,statistics as st
names=[l for l in json.load(open('items.json'))]
G=json.load(open('prism_t5b.json'))
print('games',len(G),'rivals',collections.Counter(g['rival'] for g in G).most_common())
IB=collections.Counter(); K=collections.Counter(); n=0
row=collections.defaultdict(list)
for g in G:
    S=g['stats']; th=g['th']
    for c in S['champions']:
        if c['team']!=th: continue
        t=c['typeName']
        for m in ('kills','deaths','collectedGems','earnedGold','championDamageDone','monsterDamageDone','championDamageTaken'): row[(t,m)].append(c[m])
        if t=='Prism':
            for i,q in enumerate(c['itemsBought']): IB[names[i]]+=q
    for c in S['champions']:
        if c['team']==th: continue
        t='us_'+c['typeName']
        for m in ('kills','deaths','collectedGems','earnedGold','championDamageDone','monsterDamageDone'): row[(t,m)].append(c[m])
ts=sorted(set(t for t,m in row))
for t in ts: print(f"{t:16s} n={len(row[(t,'kills')]):3d} "+' '.join(f"{m}={st.mean(row[(t,m)]):.0f}" if m.endswith('Done') or m.endswith('Gold') or m.endswith('Taken') else f"{m}={st.mean(row[(t,m)]):.2f}" for m in ('kills','deaths','collectedGems','earnedGold','championDamageDone','monsterDamageDone')))
print('Prism items bought per game:',[(k,round(v/len(G),1)) for k,v in IB.most_common(14)])
# behaviour
alive=0; cast=collections.Counter(); ctx=collections.Counter(); al=[]; en=[]; gems=[]; al2=0; al4=0; casts_r=collections.Counter(); hpcast=[]
for g in G:
    for p in g['per']:
        if p[1]==0: continue
        r,_,x,y,hp,mhp,gm,gd,da,na,de,ne,cs,cd=p
        alive+=1; al.append(da); gems.append(gm); al2+=da<=2; al4+=da<=4
        for k in cs:
            cast[k]+=1; ctx[(k,'enemy<=5' if de<=5 else 'no enemy')]+=1; casts_r[(k,min(r//150,6))]+=1
print('alive rounds',alive,'casts per game',{k:round(v/len(G),1) for k,v in cast.items()})
print('cast context per game',{k:round(v/len(G),1) for k,v in sorted(ctx.items())})
print('casts by r//150',sorted((k,round(v/len(G),1)) for k,v in casts_r.items()))
print('ally dist median',st.median(al),'ally<=2',round(al2/alive,2),'ally<=4',round(al4/alive,2),'gems carried mean',round(st.mean(gems),1),'p90',sorted(gems)[int(.9*len(gems))])

# member.py TAG: per gold capture (our side), per alive champion of ours: rounds of the hitting phase spent <=4 of a live camp,
# rounds hitting, split by champion type; and among the near-not-hitting rounds whether the champion moved.
import json,gzip,glob,collections,sys
W='/home/user/ws'; T=sys.argv[1]
near=collections.Counter(); hit=collections.Counter(); mv=collections.Counter(); still=collections.Counter(); far=collections.Counter()
everhit=collections.Counter(); everin=collections.Counter(); ph=collections.Counter()
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    us=0 if f.endswith('_a.json.gz') else 1; D=json.load(gzip.open(f))
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    typ={c['index']+(0 if c['team']==0 else 0):c['typeName'] for c in D['meta']['stats']['champions']}
    grp={k[0]:k[2] for k in D['camps']}; cpos={k[0]:(k[3],k[4]) for k in D['camps']}; gg={}
    for k in D['camps']: gg[k[2]]=max(gg.get(k[2],0),k[6] or 0)
    big={g for g,v in gg.items() if v>=20}
    hits=collections.defaultdict(lambda: collections.defaultdict(set))
    for r,dd in D['ck'].items():
        r=int(r)
        for k,v in dd.items():
            a,ci=map(int,k.split('>')); g=grp.get(ci)
            if g in big and team.get(a)==us: hits[g][r].add(a)
    R={row['r']:row for row in D['rounds']}
    caps={g:r for g,t,r in D['caps'] if t==us and g in big and r<=600}
    for g,r0 in caps.items():
        rs=sorted(r for r in hits[g] if r<=r0)
        if not rs: continue
        ep=[rs[-1]]
        for r in reversed(rs[:-1]):
            if ep[-1]-r<=15: ep.append(r)
            else: break
        first=min(ep); last=max(ep); dead=None
        for r in range(first,r0+1):
            if r in R and R[r].get('gs',{}).get(str(g))==2: dead=r; break
        if dead is None: dead=last+1
        seen=set(); hitset=set()
        for r in range(first,dead):
            if r not in R: continue
            live=[cpos[ci] for ci in R[r]['ka'] if grp.get(ci)==g]
            if not live: continue
            P={c[0]:c for c in R[r]['c']}
            for c in R[r]['c']:
                if c[1]!=us or not c[9]: continue
                t=typ.get(c[0],'?'); d=min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in live)
                if c[0] in hits[g].get(r,()): hit[t]+=1; hitset.add(c[0])
                elif d<=4:
                    near[t]+=1
                    n=R.get(r+1); 
                    if n:
                        q={x[0]:x for x in n['c']}.get(c[0])
                        if q and (q[3],q[4])!=(c[3],c[4]): mv[t]+=1
                        else: still[t]+=1
                else: far[t]+=1
                if d<=4: seen.add(c[0])
        for a in seen: everin[typ.get(a,'?')]+=1
        for a in hitset: everhit[typ.get(a,'?')]+=1
print(T)
for t in sorted(set(list(hit)+list(near))):
    print('  %-14s hitting %5d  near-not-hitting %5d (moved %4d still %4d)  far %5d   captures where <=4: %4d, hit: %4d'%(t,hit[t],near[t],mv[t],still[t],far[t],everin[t],everhit[t]))

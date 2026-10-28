import json,gzip,glob,collections,sys
W='/tmp/claude-0/w'; T=sys.argv[1]
H=collections.Counter(); idle=0; tot=0; durs=[]; split=0; dmg=0; dpsum=0
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    us=0 if f.endswith('_a.json.gz') else 1; D=json.load(gzip.open(f))
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    grp={k[0]:k[2] for k in D['camps']}; gg={}
    for k in D['camps']: gg[k[2]]=max(gg.get(k[2],0),k[6] or 0)
    big={g for g,v in gg.items() if v>=20}
    hits=collections.defaultdict(lambda: collections.defaultdict(dict))
    for r,dd in D['ck'].items():
        r=int(r)
        for k,v in dd.items():
            a,ci=map(int,k.split('>')); g=grp.get(ci)
            if g in big and team.get(a)==us: hits[g][r][(a,ci)]=v
    caps={g:r for g,t,r in D['caps'] if t==us and g in big and r<=600}
    pos={row['r']:{c[0]:c for c in row['c']} for row in D['rounds']}
    for g,r0 in caps.items():
        rs=sorted(r for r in hits[g] if r<=r0)
        if not rs: continue
        ep=[rs[-1]]
        for r in reversed(rs[:-1]):
            if ep[-1]-r<=15: ep.append(r)
            else: break
        first=min(ep); durs.append(r0-first)
        for r in range(first,r0+1):
            h=hits[g].get(r,{}); tot+=1
            n=len({a for a,ci in h}); H[min(n,4)]+=1
            if len({ci for a,ci in h})>1: split+=1
            # block members within 6 of any hitter but not hitting
            P=pos.get(r,{})
            hp={a for a,ci in h}
            for a in hp:
                for c in P.values():
                    if c[1]==us and c[9] and c[0] not in hp and max(abs(c[3]-P[a][3]),abs(c[4]-P[a][4]))<=6: idle+=1; break
print(T,'caps20+',len(durs),'mean dur',sum(durs)/len(durs),'median',sorted(durs)[len(durs)//2],'rounds',tot,'hitters dist',dict(H),'split-camp rounds',split,'rounds with idle member<=6 of hitter',idle)

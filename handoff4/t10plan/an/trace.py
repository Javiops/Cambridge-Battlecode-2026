import json,gzip,sys,collections
W='/tmp/claude-0/w'; T,b,r1,r2=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
us=0 if b.endswith('_a') else 1; D=json.load(gzip.open(f'{W}/dec/{T}/{b}.json.gz'))
grp={k[0]:k[2] for k in D['camps']}; gc={}
for k in D['camps']: gc.setdefault(k[2],[]).append((k[3],k[4],k[6]))
print('groups:',{g:(v[0][0],v[0][1],sum(x[2] for x in v)) for g,v in gc.items()})
caps=[(g,r) for g,t,r in D['caps'] if t==us and r<=r2]; print('our caps',caps, 'theirs',[(g,r) for g,t,r in D['caps'] if t!=us and r<=r2])
for row in D['rounds']:
    r=row['r']
    if r<r1 or r>r2 or r%5: continue
    ours=[f"{c[0]}@{c[3]},{c[4]}h{int(100*c[5]/max(1,c[6]))}{'' if c[9] else 'X'}" for c in row['c'] if c[1]==us]
    th=[f"{c[3]},{c[4]}" for c in row['c'] if c[1]!=us and c[9]]
    h=D['ck'].get(str(r),{}); hh=[(a,grp.get(ci)) for a,ci in (map(int,k.split('>')) for k in h)]
    print(r,' '.join(ours),'| foes',' '.join(th),'| hits',hh)

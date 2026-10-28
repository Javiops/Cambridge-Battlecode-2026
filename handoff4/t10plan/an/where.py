# where.py TAG: during the hitting phase of our gold captures, where are our alive champions each round:
# hitting / <=4 of a live camp of the group not hitting / 5-10 / 11-20 / >20 (incl. spawn). Also at the block's first hit.
import json,gzip,glob,collections,sys
W='/home/user/ws'; T=sys.argv[1]
C=collections.Counter(); F=collections.Counter(); tot=0; ftot=0
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    us=0 if f.endswith('_a.json.gz') else 1; D=json.load(gzip.open(f))
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
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
    def cls(d):
        return 'near<=4' if d<=4 else '5-10' if d<=10 else '11-20' if d<=20 else '>20'
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
        for r in range(first,dead):
            if r not in R: continue
            live=[cpos[ci] for ci in R[r]['ka'] if grp.get(ci)==g]
            if not live: continue
            for c in R[r]['c']:
                if c[1]!=us: continue
                tot+=1
                if not c[9]: k='dead'
                elif c[0] in hits[g].get(r,()): k='hitting'
                else:
                    d=min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in live); k=cls(d)
                C[k]+=1
                if r==first: ftot+=1; F[k]+=1
print(T,'champion-rounds in hitting phases',tot)
for k in ['hitting','near<=4','5-10','11-20','>20','dead']: print('  %-8s %5.1f%%   at first hit %5.1f%%'%(k,100*C[k]/max(1,tot),100*F[k]/max(1,ftot)))

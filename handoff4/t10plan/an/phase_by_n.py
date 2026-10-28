# phase_by_n.py TAG: hitting phase length of gold captures by the number of our members that hit during it, and by the
# number of camps of the group; plus hitter-rounds (sum of hitters over the phase) per capture.
import json,gzip,glob,collections,sys
W='/home/user/ws'; T=sys.argv[1]
ph=collections.defaultdict(list); hr=collections.defaultdict(list); byc=collections.defaultdict(list)
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    us=0 if f.endswith('_a.json.gz') else 1; D=json.load(gzip.open(f))
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    grp={k[0]:k[2] for k in D['camps']}; gg={}; nc=collections.Counter()
    for k in D['camps']: gg[k[2]]=max(gg.get(k[2],0),k[6] or 0); nc[k[2]]+=1
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
        mem=set(); hsum=0
        for r in range(first,dead): mem|=hits[g].get(r,set()); hsum+=len(hits[g].get(r,()))
        n=min(len(mem),4); ph[n].append(dead-first); hr[n].append(hsum); byc[min(nc[g],4)].append(dead-first)
print(T)
for n in sorted(ph): x=sorted(ph[n]); print('  members hitting=%d: captures %4d  phase mean %.1f median %d  hitter-rounds mean %.1f'%(n,len(x),sum(x)/len(x),x[len(x)//2],sum(hr[n])/len(x)))
for n in sorted(byc): x=sorted(byc[n]); print('  camps in group=%d: captures %4d phase mean %.1f median %d'%(n,len(x),sum(x)/len(x),x[len(x)//2]))

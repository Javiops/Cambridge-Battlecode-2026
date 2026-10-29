import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
bot=os.path.basename(d.rstrip('/')); A=collections.Counter(); n=0; T=collections.Counter(); NB=collections.Counter()
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if key not in side: continue
    us=side[key]; D=json.load(gzip.open(os.path.join(d,fn))); n+=1
    R={rr['r']:rr for rr in D['rounds']}
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    sp={}
    for t in (0,1):
        ps=[(c[3],c[4]) for c in R[1]['c'] if c[1]==t and c[9]]
        sp[t]=(sum(p[0] for p in ps)/len(ps),sum(p[1] for p in ps)/len(ps))
    gg={};pos=collections.defaultdict(list);k2g={}
    for k in D['camps']: gg[k[2]]=k[5] or 0; pos[k[2]].append((k[3],k[4])); k2g[k[0]]=k[2]
    hits=collections.defaultdict(list)
    for r,a,k,dm,kind in D['ck']: hits[k2g[k]].append((r,team.get(a),a,dm))
    for g,t,r in D['caps']:
        if r>300 or gg[g]<40: continue
        c=(sum(p[0] for p in pos[g])/len(pos[g]),sum(p[1] for p in pos[g])/len(pos[g]))
        dus=cheb(c,sp[us]); dth=cheb(c,sp[1-us])
        if abs(dus-dth)>3: continue
        who='us' if t==us else 'them'
        h=[x for x in hits[g] if r-40<=x[0]<=r]
        ours=sum(x[3] for x in h if x[1]==us); theirs=sum(x[3] for x in h if x[1]!=us)
        nh_them=len({x[2] for x in h if x[1]!=us}); nh_us=len({x[2] for x in h if x[1]==us})
        A[(who,'contested' if ours and theirs else 'solo')]+=1
        T[(who,r//100*100)]+=1
        NB[(who,'hitters_us',nh_us)]+=1; NB[(who,'hitters_them',nh_them)]+=1
        # our champions within 8 at capture time -40..r
        if who=='them':
            near=max(sum(1 for cc in R[q]['c'] if cc[1]==us and cc[9] and cheb((cc[3],cc[4]),c)<=8) for q in range(max(1,r-40),r) if q in R)
            NB[('them','our_max_within8',near)]+=1
for D_ in (A,T,NB):
    for k in sorted(D_): print(k, round(D_[k]/n,2))

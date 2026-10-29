import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
bot=os.path.basename(d.rstrip('/')); n=0; B=collections.Counter(); ex=[]
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
    hitr=collections.defaultdict(dict)
    for r,a,k,dm,kind in D['ck']: hitr[a][r]=k2g[k]
    for g,t,r in D['caps']:
        if r>300 or gg[g]<40 or t==us: continue
        c=(sum(p[0] for p in pos[g])/len(pos[g]),sum(p[1] for p in pos[g])/len(pos[g]))
        if abs(cheb(c,sp[us])-cheb(c,sp[1-us]))>3: continue
        # rival first hit on g in last 40
        for q in range(r-40,r):
            if q not in R: continue
            for cc in R[q]['c']:
                if cc[1]!=us or not cc[9] or cheb((cc[3],cc[4]),c)>8: continue
                h=hitr[cc[0]].get(q)
                fo=sum(1 for x in R[q]['c'] if x[1]!=us and x[9] and cheb((x[3],x[4]),(cc[3],cc[4]))<=6)
                B['hit-this' if h==g else 'hit-other' if h is not None else ('foe6' if fo else 'nofoe')]+=1
print({k:round(v/n,1) for k,v in B.items()}, 'champion-rounds/game within 8 of a centre 40+ group in the 40 rounds before a rival captures it')

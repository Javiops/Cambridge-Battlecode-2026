import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
bot=os.path.basename(d.rstrip('/')); A=collections.Counter(); n=0
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if key not in side: continue
    us=side[key]; D=json.load(gzip.open(os.path.join(d,fn))); n+=1
    R={rr['r']:rr for rr in D['rounds']}
    sp={}
    for t in (0,1):
        ps=[(c[3],c[4]) for c in R[1]['c'] if c[1]==t and c[9]]
        sp[t]=(sum(p[0] for p in ps)/len(ps),sum(p[1] for p in ps)/len(ps))
    gg={};pos=collections.defaultdict(list)
    for k in D['camps']: gg[k[2]]=k[5] or 0; pos[k[2]].append((k[3],k[4]))
    for g,t,r in D['caps']:
        if r>300: continue
        b='0' if gg[g]==0 else '1-39' if gg[g]<40 else '40+'
        cx=sum(p[0] for p in pos[g])/len(pos[g]); cy=sum(p[1] for p in pos[g])/len(pos[g])
        dus=max(abs(cx-sp[us][0]),abs(cy-sp[us][1])); dth=max(abs(cx-sp[1-us][0]),abs(cy-sp[1-us][1]))
        z='ourhalf' if dus<dth-3 else 'theirhalf' if dus>dth+3 else 'centre'
        A[('us' if t==us else 'them',b,z)]+=1
for k in sorted(A): print(k, round(A[k]/n,2))

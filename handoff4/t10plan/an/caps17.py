import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
bot=os.path.basename(d.rstrip('/')); A=collections.Counter(); n=0
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if key not in side: continue
    us=side[key]; D=json.load(gzip.open(os.path.join(d,fn))); n+=1
    gg=collections.Counter(); gd=collections.Counter()
    for k in D['camps']: gg[k[2]]+=k[5] or 0; gd[k[2]]+=k[6] or 0
    for g,t,r in D['caps']:
        w='a0-150' if r<=150 else 'b151-300'
        who='us' if t==us else 'them'
        A[(w,who,'n')]+=1; A[(w,who,'gems')]+=gg[g]; A[(w,who,'gold')]+=gd[g]
    R=D['rounds']; last=R[-1]
    A[('gems300','us','')]+=sum(c[7] for c in last['c'] if c[1]==us); A[('gems300','them','')]+=sum(c[7] for c in last['c'] if c[1]!=us)
for k in sorted(A): print(k, round(A[k]/n,1))

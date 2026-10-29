import sys,json,gzip,os,collections
T=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open('pcassets/replays_c37/index.json'))}
TY=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
A=collections.Counter()
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for fn in os.listdir('dec/'+T):
    us=side.get(T+'/'+fn.replace('.json.gz','.repl26a'))
    if us is None: continue
    D=json.load(gzip.open('dec/'+T+'/'+fn))
    for rr in D['rounds']:
        r=rr['r']
        if r<30 or r>600: continue
        kk=D['kinds'].get(str(r),{})
        C=rr['c']
        for c in C:
            if not c[9]: continue
            fo=min([cheb(c[3:5],x[3:5]) for x in C if x[1]!=c[1] and x[9]] or [99])
            ctx='fight' if fo<=4 else 'other'
            ks=kk.get(str(c[0]),[])
            w='us' if c[1]==us else 'them'
            k=(TY[c[2]],w,ctx)
            A[k+('t',)]+=1; A[k+('ab',)]+=ks.count(6); A[k+('at',)]+=ks.count(5)
for t in TY:
    for ctx in ('fight','other'):
        row=[]
        for w in ('us','them'):
            n=A[(t,w,ctx,'t')]
            if n<500: row.append(f'{w}: -'); continue
            row.append(f"{w}: turns/g? {n} ab {100*A[(t,w,ctx,'ab')]/n:.1f} at {100*A[(t,w,ctx,'at')]/n:.1f}")
        if any('ab' in x for x in row): print(t,ctx,' | '.join(row))

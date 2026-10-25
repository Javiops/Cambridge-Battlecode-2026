import zipfile,glob,sys
H={k:[0]*100 for k in (0,8,9,12)}
for f in glob.glob(sys.argv[1]+'/*/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    for l in [l for l in t if '[ufh]' in l][-16:]:
        p=l[l.index('[ufh]'):].split(); k=int(p[1])
        for b,v in enumerate(p[2:]): H[k][b]+=int(v)
for k,h in H.items():
    n=sum(h); out=[]
    for q in (.99,.995,.999,.9995,.9999):
        c=0
        for b,v in enumerate(h):
            c+=v
            if c>=q*n: out.append(f'p{q*100:g}={b+1}k'); break
    mx=max(b for b,v in enumerate(h) if v)+1
    print({0:'pre',8:'decide',9:'fight',12:'post'}[k], ' '.join(out), 'max',mx,'k', '>25k',sum(h[25:]), 'of', n)

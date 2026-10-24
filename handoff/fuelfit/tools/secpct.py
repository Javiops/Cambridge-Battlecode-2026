import zipfile,glob,sys
H=[[0]*40 for _ in range(14)]; T=[[0.0]*14 for _ in range(3)]; NT=0
for f in glob.glob(sys.argv[1]+'/*/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    for l in [l for l in t if '[ush]' in l][-56:]:
        p=l[l.index('[ush]'):].split(); k=int(p[1])
        for b,v in enumerate(p[2:]): H[k][b]+=int(v)
    for l in [l for l in t if '[ut1]' in l][-12:]:
        p=l[l.index('[ut1]'):].split(); tt=int(p[1])-1; NT+=1
        for k,v in enumerate(p[2:]): T[tt][k]+=float(v)
names='pre init shop vis groups foes camps support decide fight recall farm post log'.split()
def pct(h,q):
    n=sum(h); c=0
    for b,v in enumerate(h):
        c+=v
        if c>=q*n: return (b+1)*2.5
print('section   p50   p90   p99  p99.9  max-bucket (k)')
for k in range(14):
    h=H[k]; mb=max(b for b,v in enumerate(h) if v)
    print(f'{names[k]:8s} {pct(h,.5):5.1f} {pct(h,.9):5.1f} {pct(h,.99):5.1f} {pct(h,.999):6.1f}  {(mb+1)*2.5:5.1f}{"+" if mb==39 else ""}')
n=NT/3
for tt in range(3): print('turn',tt+1,'mean per section',[round(x/n) for x in T[tt]],'total',round(sum(T[tt])/n))

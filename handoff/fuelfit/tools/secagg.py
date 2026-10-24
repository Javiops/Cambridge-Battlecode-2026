import zipfile,glob,re,sys
S=[0.0]*14; B=[0.0]*14; M=[0.0]*14; NT=NB=0; H=[0]*40
for f in glob.glob(sys.argv[1]+'/*/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    for l in [l for l in t if '[usec]' in l][-4:]:
        p=l[l.index('[usec]'):].split(); NT+=int(p[2]); NB+=int(p[3])
        for k,x in enumerate(p[4:18]):
            a,b,m=map(float,x.split(':')); S[k]+=a; B[k]+=b; M[k]=max(M[k],m)
    for l in [l for l in t if '[ugh]' in l][-4:]:
        for i,v in enumerate(l[l.index('[ugh]'):].split()[2:]): H[i]+=int(v)
names='pre init shop vis groups foes camps support decide fight recall farm post log'.split()
print('turns',NT,'big(>92k)',NB, 'mean/turn',round(sum(S)/NT),'mean/big',round(sum(B)/max(1,NB)))
for k in range(14): print(f'{names[k]:8s} all {S[k]/NT:7.0f} big {B[k]/max(1,NB):7.0f} max {M[k]:7.0f}')
N=sum(H); c=0
for i,v in enumerate(H):
    c+=v
    if i>=16 and v: print(f'{i*5}-{i*5+5}k: {v} cum {c/N:.4f}')

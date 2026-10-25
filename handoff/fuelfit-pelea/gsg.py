import zipfile,glob,collections,sys
R=sys.argv[1]; names={int(x.split('=')[0]):x.split('=')[1] for x in sys.argv[2].split(',')} if len(sys.argv)>2 else {}
A=collections.Counter();B=collections.Counter();N=NB=0
for f in glob.glob(R+'/*/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    for l in [l[l.index('[gsg]'):] for l in t if '[gsg]' in l][-5:]:
        p=l.split(); N+=int(p[2]); NB+=int(p[3])
        for x in p[4:]:
            k,a,b=x.split(':'); A[int(k)]+=float(a); B[int(k)]+=float(b)
print('turns',N,'big',NB,'mean big',round(sum(B.values())/max(1,NB)))
for k,v in sorted(B.items(),key=lambda x:-x[1]): print(f'{k:3d} {names.get(k,"")!s:22s} all {A[k]/N:7.0f} big {v/max(1,NB):7.0f}')

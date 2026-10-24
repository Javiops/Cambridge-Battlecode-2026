import zipfile,glob,collections,sys
R=sys.argv[1]
A=collections.Counter();B=collections.Counter();N=NB=0
for f in glob.glob(R+'/*/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    rows=[l[l.index('[fsg]'):] for l in t if '[fsg]' in l][-5:]
    for l in rows:
        p=l.split(); N+=int(p[2]); NB+=int(p[3])
        for x in p[4:]:
            k,a,b=x.split(':'); A[int(k)]+=float(a); B[int(k)]+=float(b)
names={1:'start->chase',11:'chase test/pick',12:'chase act',2:'bcf feat',13:'bcf decide->engage',14:'bcf engage',15:'after bcf fail',3:'ally duty',4:'verdict',5:'kite',6:'pre-favourable',7:'fav->lowhp',16:'lowhp avoid',17:'outnum',18:'avoid+front?',8:'front_line',9:'pre-engage',10:'final engage'}
print('turns',N,'big',NB, 'sum big', round(sum(B.values())/max(1,NB)))
for k,v in sorted(B.items(),key=lambda x:-x[1]): print(f'{k:3d} {names.get(k,k)!s:24s} all {A[k]/N:7.0f} big {v/max(1,NB):7.0f}')

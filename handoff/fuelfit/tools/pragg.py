import zipfile,glob,re,sys,collections,json
names=json.load(open(sys.argv[2])); A=collections.Counter(); B=collections.Counter(); XA=collections.Counter(); XB=collections.Counter(); NA=NB=0
for f in glob.glob(sys.argv[1]+'/*/*.repl26a'):
    side='a' if '/A_' in f else 'b'
    t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
    for l in [l for l in t if '[prf]' in l][-4:]:
        l=l[l.index('[prf]'):]; p=l.split(); NA+=int(p[2]); NB+=int(p[3])
        for k,a,b,xa,xb in re.findall(r' (\d+):([-0-9.e+]+):([-0-9.e+]+):([-0-9.e+]+):([-0-9.e+]+)',l): A[int(k)]+=float(a); B[int(k)]+=float(b); XA[int(k)]+=float(xa); XB[int(k)]+=float(xb)
print('turns',NA,'big(>92k)',NB)
print(f'{"function":36s} {"incl/turn":>9s} {"incl/big":>9s} {"excl/turn":>9s} {"excl/big":>9s}')
for k,v in sorted(XB.items(),key=lambda x:-x[1])[:int(sys.argv[3]) if len(sys.argv)>3 else 30]:
    print(f'{names[k]:36s} {A[k]/NA:9.0f} {B[k]/NB:9.0f} {XA[k]/NA:9.0f} {v/NB:9.0f}')

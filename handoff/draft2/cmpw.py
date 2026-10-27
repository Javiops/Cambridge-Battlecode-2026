import json,sys,os,glob,math
def res(d):
    o={}
    for f in glob.glob(d+'/*/*.json'):
        try: m=json.load(open(f))['match']['outcome']
        except Exception: continue
        k=os.path.relpath(f,d); side=os.path.basename(f)[0]
        o[k]=(m=='teamA')==(side=='A')
    return o
b=res(sys.argv[1]); v=res(sys.argv[2]); ks=set(b)&set(v)
p=sum(1 for k in ks if v[k] and not b[k]); m=sum(1 for k in ks if b[k] and not v[k])
print(f'n={len(ks)} base {sum(b[k] for k in ks)} var {sum(v[k] for k in ks)} +{p} -{m} bar {2*math.sqrt(p+m):.1f}')

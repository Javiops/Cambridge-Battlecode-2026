import json,glob,os,sys
sys.path.insert(0,'.')
def seq(runs):
    t=0;o=[]
    for x in runs: o.append((t,x['value'])); t+=x['duration']
    return o
B,C=sys.argv[1:3]; out=[]
for f in glob.glob(B+'/*/*.json'):
    g=C+f[len(B):]
    if not os.path.exists(g): continue
    a=json.load(open(f)); b=json.load(open(g))
    A={(T['metric'],T['owner']['team'],T['owner'].get('name')):seq(T['runs']) for T in a['championTimelines']}
    Bb={(T['metric'],T['owner']['team'],T['owner'].get('name')):seq(T['runs']) for T in b['championTimelines']}
    best=None
    for k in A:
        if k not in Bb: continue
        for x,y in zip(A[k],Bb[k]):
            if x!=y:
                r=min(x[0],y[0])
                if best is None or r<best[0]: best=(r,k)
                break
    if best: out.append((best[0],best[1],f[len(B)+1:]))
out.sort()
for o in out[:25]: print(o)

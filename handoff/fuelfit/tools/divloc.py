# divloc.py BASE CAND : changed games + first round any timeline differs
import json,glob,os,collections
import sys
def seq(runs):
    t=0;o=[]
    for x in runs: o.append((t,x['value'])); t+=x['duration']
    return o
def tlines(J):
    D={}
    for T in J['championTimelines']: D[(T['metric'],T['owner']['team'],T['owner']['id'])]=seq(T['runs'])
    return D
def firstdiff(a,b):
    best=None
    for k in a:
        if k not in b: continue
        A=a[k];B=b[k]
        for (ta,va),(tb,vb) in zip(A,B):
            if (ta,va)!=(tb,vb): r=min(ta,tb); best=r if best is None else min(best,r); break
    return best
B,C=sys.argv[1:3]; rs=[]; ch=0; n=0; res=0
for f in glob.glob(B+'/*/*.json'):
    g=C+f[len(B):]
    if not os.path.exists(g): continue
    a=json.load(open(f)); b=json.load(open(g)); n+=1
    if a['match']['outcome']!=b['match']['outcome']: res+=1
    d=firstdiff(tlines(a),tlines(b))
    if d is not None: ch+=1; rs.append(d)
rs.sort()
print(f'{C}: games {n} any-diff {ch} result-changed {res}', 'div<150', sum(r<150 for r in rs), 'div<300', sum(r<300 for r in rs), 'div median', rs[len(rs)//2] if rs else None, 'p10',rs[len(rs)//10] if rs else None)

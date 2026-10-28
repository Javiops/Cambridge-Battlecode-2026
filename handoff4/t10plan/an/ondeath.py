# ondeath.py: online c34 v4b vs e1foco on near maps (spawn path < 35): per game result, deaths r1-150 with context, gold-only/other captures r<600
import json,gzip,os,collections
W='/tmp/claude-0/w'
near=set(open('/tmp/claude-0/-home-user-cambridge-battlecode-2026/3dc070b2-a00b-5e31-ba97-59618d5276fa/scratchpad/near.txt').read().split())
T=json.load(open(f'{W}/c34index.json'))
I={(x['bot'],os.path.basename(x['file'])):x for x in T}
N={1:'Ves',7:'Mar',12:'HoR',0:'Ryt',2:'Ven'}
def an(d,x):
    D=json.load(gzip.open(f'{W}/dec/{d}/'+os.path.basename(x['file']).replace('.repl26a','.json.gz'))); us=0 if x['side']=='a' else 1
    gty=collections.defaultdict(set); gv={}
    for k in D['camps']: gty[k[2]].add(k[1]); gv[k[2]]=k[5]
    gold=sum(1 for g,t,r in D['caps'] if t==us and r<600 and gv[g]<=0 and not gty[g]&{0,1,4,5}); allc=sum(1 for g,t,r in D['caps'] if t==us and r<600)
    prev={}; out=[]; sp=None
    for row in D['rounds']:
        r=row['r']
        if r>150: break
        cs=[c for c in row['c'] if c[1]==us]; en=[c for c in row['c'] if c[1]!=us and c[9]]
        if sp is None: sp=[(c[3],c[4]) for c in cs]
        for c in cs:
            p=prev.get(c[0])
            if p and p[9] and not c[9]:
                al=[a for a in cs if a is not c and prev.get(a[0],a)[9] and max(abs(a[3]-p[3]),abs(a[4]-p[4]))<=4]
                ne=[e for e in en if max(abs(e[3]-p[3]),abs(e[4]-p[4]))<=5]
                hs=min(max(abs(p[3]-x),abs(p[4]-y)) for x,y in sp)
                out.append(f'r{r} {N.get(c[2])} allies<=4 {len(al)} foes<=5 {len(ne)} from-spawn {hs}')
            prev[c[0]]=c
    return x['result'],allc,gold,out
rows=[]
for x in T:
    if x['bot']!='t10plan4b' or x['map'] not in near: continue
    b=os.path.basename(x['file']); y=I.get(('e1foco',b))
    if not y: continue
    rv,av,gvv,dv=an('on4b',x); re_,ae,ge,de=an('e1foco',y)
    print(f"## {x['map']} {x['rival']} side {x['side']}: v4b {rv} caps r<600 {av} (gold-only {gvv}) | e1foco {re_} caps {ae} (gold-only {ge})")
    print('   v4b deaths r1-150: '+('; '.join(dv) or '-'))
    print('   e1f deaths r1-150: '+('; '.join(de) or '-'))

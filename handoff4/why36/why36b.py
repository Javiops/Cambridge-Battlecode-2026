# why36b.py: gem income decomposition by phase (captures by group size, kill transfers), team gems over time, for c34 losses
import json,gzip,os,collections
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
PH=[(0,150),(151,300),(301,450),(451,700)]
def ph(r): return next(i for i,(a,b) in enumerate(PH) if a<=r<=b) if r<=700 else 3
for bot in DIR:
  for res in ('loss','win'):
    n=0; A=[collections.Counter(),collections.Counter()]
    for x in T:
        if x['bot']!=bot or x['result']!=res: continue
        f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
        if not os.path.exists(f): continue
        D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; n+=1
        gv={}
        for k in D['camps']: gv[k[2]]=max(gv.get(k[2],0),k[5] or 0)
        for g,t,r in D['caps']:
            if t not in (0,1): continue
            i=0 if t==us else 1; v=gv.get(g,0); p=ph(r)
            A[i][f'capg{p}']+=v
            A[i][f'n{"big" if v>=40 else ("mid" if v>=15 else ("small" if v>0 else "gold"))}{p}']+=1
        prev={}
        for row in D['rounds']:
            r=row['r']
            for c in row['c']:
                q=prev.get(c[0])
                if q and q[9] and not c[9]:
                    i=0 if c[1]==us else 1
                    A[1-i][f'tr{ph(r)}']+=q[7]
                prev[c[0]]=c
            if r in (150,300,450,600):
                for t in (0,1):
                    i=0 if t==us else 1
                    A[i][f'tot{r}']+=row['sg'][t]+sum(c[7] for c in row['c'] if c[1]==t and c[9])
    print(f'## {bot} {res} n={n}   us / rival per game')
    for p in range(4):
        print(f'  r{PH[p][0]}-{PH[p][1]}: capture gems {A[0][f"capg{p}"]/n:.0f}/{A[1][f"capg{p}"]/n:.0f}  kill transfer {A[0][f"tr{p}"]/n:.0f}/{A[1][f"tr{p}"]/n:.0f}  caps big>=40 {A[0][f"nbig{p}"]/n:.2f}/{A[1][f"nbig{p}"]/n:.2f} mid {A[0][f"nmid{p}"]/n:.2f}/{A[1][f"nmid{p}"]/n:.2f} small {A[0][f"nsmall{p}"]/n:.2f}/{A[1][f"nsmall{p}"]/n:.2f} gold {A[0][f"ngold{p}"]/n:.2f}/{A[1][f"ngold{p}"]/n:.2f}')
    print('  gems held+banked at r150/300/450/600:',' '.join(f'{A[0][f"tot{r}"]/n:.0f}/{A[1][f"tot{r}"]/n:.0f}' for r in (150,300,450,600)))

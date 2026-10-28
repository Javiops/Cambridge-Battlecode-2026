# carryanal.py GLOB [WIN=1]: carries (Vesper, Marcella) r0-400: round use, banks, captures by group class with gems/gold and spawn distance
import json,gzip,glob,sys,os,collections
WIN=os.environ.get('WIN')
U=collections.Counter(); BK=[]; CP=collections.defaultdict(list); NG=0; NC=0
for f in glob.glob(sys.argv[1]):
    D=json.load(gzip.open(f)); us=(0 if f.endswith('_a.json.gz') else 1) if not WIN else D['meta']['outcome']-1
    if us not in (0,1): continue
    NG+=1
    gt=collections.defaultdict(list); gty=collections.defaultdict(set); gv={}
    for k in D['camps']: gt[k[2]].append((k[3],k[4])); gty[k[2]].add(k[1]); gv[k[2]]=(k[5],k[6])
    def cls(g):
        t=gty[g]
        return 'mono' if 4 in t else 'boss' if 5 in t else 'elk' if 1 in t else 'wolf' if 0 in t else ('cluster' if gv[g][0]>0 else 'gold')
    tiles=[t for v in gt.values() for t in v]
    R={row['r']:row for row in D['rounds']}; sp=None; prev={}
    for row in D['rounds']:
        r=row['r']
        if r>=400: break
        cs=[c for c in row['c'] if c[1]==us]; en=[c for c in row['c'] if c[1]!=us and c[9]]
        if sp is None: sp=[(c[3],c[4]) for c in cs]; NC+=sum(1 for c in cs if c[2] in (1,7))
        for c in cs:
            if c[2] not in (1,7): continue
            p=prev.get(c[0])
            if p and p[9] and c[9] and c[8]<p[8]: BK.append(p[8]-c[8])
            prev[c[0]]=c
            if not c[9]: U['dead']+=1
            elif min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in sp)<=3: U['spawn']+=1
            elif any(max(abs(c[3]-e[3]),abs(c[4]-e[4]))<=4 for e in en): U['fight']+=1
            elif any(max(abs(c[3]-x),abs(c[4]-y))<=2 for x,y in tiles): U['camp']+=1
            else: U['walk']+=1
    for g,t,r in D['caps']:
        if t!=us or r>=400 or r not in R: continue
        if any(c[2] in (1,7) and c[9] and min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in gt[g])<=1 for c in R[r]['c'] if c[1]==us):
            cx=sum(x for x,_ in gt[g])/len(gt[g]); cy=sum(y for _,y in gt[g])/len(gt[g])
            CP[cls(g)].append((gv[g][0],gv[g][1],min(max(abs(cx-x),abs(cy-y)) for x,y in sp)))
n=sum(U.values()); nc=max(NC,1)
print(f'games {NG}; per carry r0-400: '+' '.join(f'{k} {U[k]/n:.0%}' for k in ('camp','walk','fight','spawn','dead')))
print(f'banks per carry {len(BK)/nc:.1f}, gems per bank {sum(BK)/max(len(BK),1):.0f}, gems banked per carry {sum(BK)/nc:.0f}')
for k in ('gold','cluster','wolf','elk','boss','mono'):
    v=CP.get(k,[])
    if v: print(f'  {k}: caps/game {len(v)/NG:.2f}, gems {sum(a for a,_,_ in v)/len(v):.0f} gold {sum(b for _,b,_ in v)/len(v):.0f} per cap, spawn dist {sum(d for *_,d in v)/len(v):.0f}')

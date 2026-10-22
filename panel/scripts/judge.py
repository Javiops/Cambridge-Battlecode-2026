import sys, math, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ab
MAPS=set(os.environ['MAPS'].split(',')) if os.environ.get('MAPS') else None
EXCL=os.environ.get('EXCL')=='1'
keep=lambda g: MAPS is None or ((g[2:] in MAPS) != EXCL)
base=sys.argv[1]; PAN=os.environ.get('PAN','pA,pB,pC,pInv,pD,pF,pE,pG,pM').split(',')
for c in sys.argv[2:]:
    F=A=0; row=[]; gc=gb=dc=db=m=0
    for p in PAN:
        B=ab.load(f'cal_{base}_{p}'); C={g:v for g,v in ab.load(f'cal_{c}_{p}').items() if keep(g)}
        f=sum(1 for g in C if g in B and C[g][0]>B[g][0]); a=sum(1 for g in C if g in B and C[g][0]<B[g][0]); F+=f; A+=a
        row.append(f'{p} {f-a:+d} ({f}/{a})')
        for g in C:
            if g in B: gc+=C[g][1]['cand'].get('gems',0); gb+=B[g][1]['cand'].get('gems',0); dc+=C[g][1]['cand'].get('deaths',0); db+=B[g][1]['cand'].get('deaths',0); m+=1
    print(f"{c} vs {base}: panel net {F-A:+d} ({F}/{A}, bar {2*math.sqrt(max(1,F+A)):.1f}); gems {gc/m:.0f} vs {gb/m:.0f}; deaths {dc/m:.1f} vs {db/m:.1f}; games {m} | "+'  '.join(row))

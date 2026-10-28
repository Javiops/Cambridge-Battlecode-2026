# carrytime.py GLOB: carry (vesper, marcella) rounds r0-400: dead / on spawn / within 1 of a camp tile / elsewhere
import json,gzip,glob,sys,collections
C=collections.Counter()
for f in glob.glob(sys.argv[1]):
    us=0 if f.endswith('_a.json.gz') else 1; D=json.load(gzip.open(f))
    tiles=set((k[3],k[4]) for k in D['camps']); sp=None
    for row in D['rounds']:
        if row['r']>=400: break
        cs=[c for c in row['c'] if c[1]==us]
        if sp is None: sp=[(c[3],c[4]) for c in cs]
        for c in cs:
            if c[2] not in (1,7): continue
            if not c[9]: C['dead']+=1
            elif min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in sp)<=3: C['spawn']+=1
            elif any(max(abs(c[3]-x),abs(c[4]-y))<=2 for x,y in tiles): C['camp']+=1
            else: C['walk']+=1
n=sum(C.values()); print(' '.join(f'{k} {C[k]/n:.0%}' for k in ('camp','walk','spawn','dead')))

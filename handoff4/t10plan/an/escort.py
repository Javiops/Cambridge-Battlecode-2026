# escort.py PREFIX: per 50-round bin, where each escort is relative to its carry (replay positions, our side)
# escort HoR(12)->Vesper(1), Ryth(0)->Marcella(7), others -> nearest live carry. Categories per escort-round (r50-600):
# near (<=4) | esc dead | esc on spawn | carry dead | carry on spawn | apart (both alive off spawn, >4)
import json,gzip,glob,os,sys,collections
cat=['near','esc_dead','esc_spawn','car_dead','car_spawn','apart']
B=collections.defaultdict(collections.Counter); G=collections.Counter()
pat=sys.argv[1] if '/' in sys.argv[1] else f'/tmp/claude-0/w/tl/{sys.argv[1]}_*.json.gz'
CAP=[0,0]
for f in sorted(glob.glob(pat)):
    us=0 if f.endswith('_a.json.gz') else 1
    D=json.load(gzip.open(f)); sp=None
    CAP[0]+=sum(1 for g,t,r in D['caps'] if t==us and r<400); CAP[1]+=1
    for row in D['rounds']:
        C={c[2]:c for c in row['c'] if c[1]==us}
        if sp is None: sp=[(c[3],c[4]) for c in C.values()]
        r=row['r']
        if r<50 or r>=600: continue
        ons=lambda c: min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in sp)<=4
        d=lambda a,b: max(abs(a[3]-b[3]),abs(a[4]-b[4]))
        carries=[C[t] for t in (1,7) if t in C]
        for t,e in C.items():
            if t in (1,7): continue
            k=1 if t==12 and 1 in C else 7 if t==0 and 7 in C else None
            if k is None:
                live=[c for c in carries if c[9]]
                if not live or not e[9]: k=carries[0][2] if carries else None
                else: k=min(live,key=lambda c:d(c,e))[2]
            if k is None: continue
            c=C[k]
            if not e[9]: x='esc_dead'
            elif not c[9]: x='car_dead'
            elif d(e,c)<=4: x='near'
            elif ons(e): x='esc_spawn'
            elif ons(c): x='car_spawn'
            else: x='apart'
            B[r//50*50][x]+=1; G[x]+=1
print('| r | '+' | '.join(cat)+' |'); print('|---'*(len(cat)+1)+'|')
for b in sorted(B):
    n=sum(B[b].values()); print(f'| {b}-{b+49} | '+' | '.join(f'{B[b][x]/n:.0%}' for x in cat)+' |')
n=sum(G.values()); print(f'| all | '+' | '.join(f'{G[x]/n:.0%}' for x in cat)+' |')
print(f'captures r<400 per game {CAP[0]/CAP[1]:.1f} ({CAP[1]} games)')

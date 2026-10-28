# fargate.py TAG...: far maps (spawn path >= 35) local vs kvvl: ally<=4 off spawn (all / with a rival within 8), captures r<400, deaths r150-600, wins
import json,gzip,glob,os,sys,re,collections
near=set(open('/tmp/claude-0/-home-user-cambridge-battlecode-2026/3dc070b2-a00b-5e31-ba97-59618d5276fa/scratchpad/near.txt').read().split())
ch=lambda a,b:max(abs(a[3]-b[3]),abs(a[4]-b[4]))
for d in sys.argv[1:]:
    a=n=af=nf=cap=dth=g=0
    for f in glob.glob(f'/tmp/claude-0/w/dec/{d}/*.json.gz'):
        b=os.path.basename(f)[:-8]; m=b[:-2]
        if m in near: continue
        us=0 if b.endswith('_a') else 1; D=json.load(gzip.open(f)); g+=1; sp=None; prev={}
        cap+=sum(1 for gg,t,r in D['caps'] if t==us and r<400)
        for row in D['rounds']:
            r=row['r']
            if r>=600: break
            cs=[c for c in row['c'] if c[1]==us]; en=[c for c in row['c'] if c[1]!=us and c[9]]
            if sp is None: sp=[(c[3],c[4]) for c in cs]
            for c in cs:
                if prev.get(c[0],1) and not c[9] and r>=150: dth+=1
                prev[c[0]]=c[9]
            if r<50: continue
            A=[c for c in cs if c[9]]
            for c in A:
                if min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in sp)<=4: continue
                k=any(e is not c and ch(c,e)<=4 for e in A); n+=1; a+=k
                if any(ch(c,e)<=8 for e in en): nf+=1; af+=k
    print(f'{d}: far games {g}, ally<=4 {a/n:.0%}, with rival within 8 {af/max(nf,1):.0%}, captures r<400 {cap/g:.1f}, deaths r150-600 {dth/g:.2f}')

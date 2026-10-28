import json,gzip,glob,os,sys
def frac(d, r0=50, r1=600):
    a=n=0; dd=0; g=0
    for f in glob.glob(f'/tmp/claude-0/w/dec/{d}/*.json.gz'):
        D=json.load(gzip.open(f)); us=0 if os.path.basename(f).split('.')[0].endswith('_a') else 1
        c0=D['rounds'][0]['c']; sp=[(c[3],c[4]) for c in c0 if c[1]==us]; g+=1; prev={}
        for row in D['rounds']:
            if row['r']<r0 or row['r']>=r1: continue
            A=[c for c in row['c'] if c[1]==us and c[9]]
            for c in row['c']:
                if c[1]==us:
                    if prev.get(c[0],1) and not c[9]: dd+=1
                    prev[c[0]]=c[9]
            for c in A:
                if min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in sp)<=4: continue
                n+=1; a+= any(e is not c and max(abs(c[3]-e[3]),abs(c[4]-e[4]))<=4 for e in A)
    return a/n, dd/g
for d in sys.argv[1:]: print(d, 'ally<=4 off spawn r50-600 %.2f, deaths r50-600 per game %.1f'%frac(d))

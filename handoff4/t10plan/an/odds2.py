# like odds.py on ext.py decodes (whole game), windows of 150 rounds
import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
bot=os.path.basename(d.rstrip('/')); C=collections.Counter(); n=0; G=collections.Counter()
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if key not in side: continue
    us=side[key]; D=json.load(gzip.open(os.path.join(d,fn))); n+=1
    R={rr['r']:{c[0]:c for c in rr['c']} for rr in D['rounds']}
    cc=collections.defaultdict(float)
    for r,m in D['cc'].items():
        for k,v in m.items(): a,t=k.split('>'); cc[(int(t),int(r))]+=abs(v)
    last=max(R)
    for r in range(30,last+1):
        if r not in R or r-1 not in R or r-5 not in R or r-10 not in R: continue
        for i,c in R[r].items():
            if i not in R[r-1] or not (R[r-1][i][9] and not c[9]): continue
            me=R[r-5][i]
            if not me[9]: continue
            champ=sum(cc[(i,q)] for q in range(r-10,r+1)) >= 0.5*max(1,R[r-10][i][5])
            al=sum(1 for x in R[r-5].values() if x[1]==me[1] and x[0]!=i and x[9] and cheb(x[3:5],me[3:5])<=6)
            fo=sum(1 for x in R[r-5].values() if x[1]!=me[1] and x[9] and cheb(x[3:5],me[3:5])<=6)
            who='us' if me[1]==us else 'them'
            k='camp' if not champ else 'outnumbered' if fo>al+1 else 'even' if fo==al+1 else 'ahead'
            w=min(r//150*150,900)
            C[(who,w,k)]+=1
for who in ('us','them'):
    for w in range(0,1050,150):
        row={k:round(C[(who,w,k)]/n,2) for k in ('outnumbered','even','ahead','camp')}
        print(who,w,row,'sum',round(sum(row.values()),2))

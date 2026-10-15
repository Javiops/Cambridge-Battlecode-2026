import re,sys,glob,collections,math
def binp(k,n):
    # two-sided sign test
    if n==0: return 1
    p=sum(math.comb(n,i) for i in range(0,n+1) if abs(i-n/2)>=abs(k-n/2))/2**n
    return min(1,p)
for f in sorted(glob.glob(sys.argv[1])):
    rows=collections.defaultdict(dict)
    for l in open(f):
        m=re.match(r'(\S+)\s+side=(A|B) (WIN|LOSS|DRAW)',l)
        if m: rows[m[1]][m[2]]=m[3]
    w=l_=0; gw=0
    for mp,d in rows.items():
        if len(d)<2: continue
        if d['A']==d['B']=='WIN': w+=1
        elif d['A']==d['B']=='LOSS': l_+=1
    tot=sum(1 for d in rows.values() for v in d.values() if v=='WIN')
    games=sum(len(d) for d in rows.values())
    print(f"{f.split('/')[-1]:28s} games {tot}-{games-tot}  maps won both sides {w}, lost both {l_}, sign-test p={binp(w,w+l_):.2f}")

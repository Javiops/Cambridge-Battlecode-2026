# champion-killed deaths r30-300: allies vs foes within 6 of the victim 5 rounds before death, for us and for the rival
import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
bot=os.path.basename(d.rstrip('/')); C={'us':collections.Counter(),'them':collections.Counter()}; n=0
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if key not in side: continue
    us=side[key]; D=json.load(gzip.open(os.path.join(d,fn))); n+=1
    R={rr['r']:{c[0]:c for c in rr['c']} for rr in D['rounds']}
    cc=collections.defaultdict(float)
    for r,a,t,dm in D['cc']: cc[(t,r)]+=dm
    for r in range(30,301):
        if r not in R or r-1 not in R or r-5 not in R: continue
        for i,c in R[r].items():
            if not (R[r-1][i][9] and not c[9]): continue
            if sum(cc[(i,q)] for q in range(r-10,r+1)) < 0.5*R[r-10][i][5] if r-10 in R else True: continue
            me=R[r-5][i]
            if not me[9]: continue
            al=sum(1 for x in R[r-5].values() if x[1]==me[1] and x[0]!=i and x[9] and cheb(x[3:5],me[3:5])<=6)
            fo=sum(1 for x in R[r-5].values() if x[1]!=me[1] and x[9] and cheb(x[3:5],me[3:5])<=6)
            who='us' if me[1]==us else 'them'
            k='outnumbered' if fo>al+1 else 'even' if fo==al+1 else 'ahead'
            C[who][k]+=1
for w in C: print(w,{k:round(v/n,2) for k,v in C[w].items()}, 'total',round(sum(C[w].values())/n,2))

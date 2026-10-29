# our champion-killed deaths while ahead (allies+1 > foes within 6 at r-5): did the allies within 6 deal champion damage in the last 10 rounds?
import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
bot=os.path.basename(d.rstrip('/')); C=collections.Counter(); n=0
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if key not in side: continue
    us=side[key]; D=json.load(gzip.open(os.path.join(d,fn))); n+=1
    R={rr['r']:{c[0]:c for c in rr['c']} for rr in D['rounds']}
    cc=collections.defaultdict(float); dealt=collections.defaultdict(float)
    for r,m in D['cc'].items():
        for k,v in m.items(): a,t=map(int,k.split('>')); cc[(t,int(r))]+=abs(v); dealt[(a,int(r))]+=abs(v)
    for r in range(30,max(R)+1):
        if r not in R or r-1 not in R or r-10 not in R: continue
        for i,c in R[r].items():
            if c[1]!=us or i not in R[r-1] or not (R[r-1][i][9] and not c[9]): continue
            me=R[r-5].get(i) if r-5 in R else None
            if not me or not me[9]: continue
            if sum(cc[(i,q)] for q in range(r-10,r+1)) < 0.5*max(1,R[r-10][i][5]): continue
            al=[x for x in R[r-5].values() if x[1]==us and x[0]!=i and x[9] and cheb(x[3:5],me[3:5])<=6]
            fo=[x for x in R[r-5].values() if x[1]!=us and x[9] and cheb(x[3:5],me[3:5])<=6]
            if not (len(al)+1>len(fo)): continue
            C['n']+=1
            for a in al:
                C['allies']+=1
                dd=sum(dealt[(a[0],q)] for q in range(r-10,r+1))
                C['ally_dealt']+=dd; C['ally_zero']+= dd==0
                C['ally_hp_frac']+=a[5]/a[6]
            C['me_dealt']+=sum(dealt[(i,q)] for q in range(r-10,r+1)); C['foes']+=len(fo)
            C['foe_hp_frac']+=sum(x[5]/x[6] for x in fo)
print(n,'games; ahead deaths',C['n'],'per game',round(C['n']/n,2))
print('allies/death',round(C['allies']/C['n'],2),'foes/death',round(C['foes']/C['n'],2),'ally dealt 10r',round(C['ally_dealt']/C['allies']),'ally dealt 0 share',round(C['ally_zero']/C['allies'],2),'ally hp frac',round(C['ally_hp_frac']/C['allies'],2),'me dealt',round(C['me_dealt']/C['n']),'foe hp frac',round(C['foe_hp_frac']/max(1,C['foes']),2))

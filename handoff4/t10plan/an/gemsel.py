import sys,os,json,gzip,collections
d=sys.argv[1]; side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(sys.argv[2]))}
R1=int(sys.argv[3]) if len(sys.argv)>3 else 150
bot=os.path.basename(d.rstrip('/')); A=collections.Counter(); n=0
def b(g): return '0' if g==0 else '1-39' if g<40 else '40-99' if g<100 else '100+'
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if key not in side: continue
    us=side[key]; D=json.load(gzip.open(os.path.join(d,fn))); n+=1
    gg={};gh=collections.Counter();cnt=collections.Counter()
    for k in D['camps']: gg[k[2]]=k[5] or 0; gh[k[2]]+=k[7]; cnt[k[2]]+=1
    for g,t,r in D['caps']:
        if r>R1: continue
        who='us' if t==us else 'them'
        A[(who,b(gg[g]),'n')]+=1; A[(who,b(gg[g]),'gems')]+=gg[g]; A[(who,b(gg[g]),'hp')]+=gh[g]
for who in ['us','them']:
    for bb in ['0','1-39','40-99','100+']:
        k=A[(who,bb,'n')]
        if k: print(who,bb,'caps/g',round(k/n,2),'gems/g',round(A[(who,bb,'gems')]/n),'avg hp',round(A[(who,bb,'hp')]/k))

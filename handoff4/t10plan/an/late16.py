import sys,json,gzip,collections
# per game: champion kills by side per 50-round window, gems at r300/r400/end, camp captures by side per window
for f in sys.argv[1:]:
    side=0 if f.split(':')[1]=='a' else 1; fn=f.split(':')[0]
    D=json.load(gzip.open(fn)); R=D['rounds']
    us=side
    def gems(r):
        rr=[x for x in R if x['r']<=r][-1]; t=[0,0]
        for c in rr['c']: t[c[1]]+=c[7]
        return t[us],t[1-us],rr['r']
    deaths=collections.Counter()
    prev={}
    for rr in R:
        for c in rr['c']:
            if prev.get(c[0]) and not c[9]: deaths[(c[1]==us,rr['r']//100)]+=1
            prev[c[0]]=c[9]
    caps=collections.Counter((g[1]==us,g[2]//100) for g in D.get('caps',[]))
    last=R[-1]['r']
    print(fn.split('/')[-2],fn.split('/')[-1][:30],'end',last,'gems r200/300/400/end',gems(200),gems(300),gems(400),gems(9999))
    print('  deaths us/them per 100r:',[(deaths[(True,b)],deaths[(False,b)]) for b in range(last//100+1)],' caps us/them:',[(caps[(True,b)],caps[(False,b)]) for b in range(last//100+1)])

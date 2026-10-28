import json,gzip,glob,collections,sys
W='/tmp/claude-0/w'; T=sys.argv[1]; only=sys.argv[2] if len(sys.argv)>2 else None
L=collections.Counter(); eps=[]
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    b=f.split('/')[-1][:-8]
    if only and b!=only: continue
    us=0 if b.endswith('_a') else 1; D=json.load(gzip.open(f))
    tiles=collections.defaultdict(list)
    for k in D['camps']: tiles[k[2]].append((k[3],k[4]))
    cen={g:t[0] for g,t in tiles.items()}
    val={}
    for k in D['camps']: val[k[2]]=max(val.get(k[2],0),(k[5] or 0)+(k[6] or 0))
    ctc=collections.defaultdict(list)
    for g,t,r in D['ctc']: ctc[r].append((g,t))
    cur={}; run={}
    for row in D['rounds']:
        r=row['r']
        for g,t in ctc.get(r,[]): cur[g]=t
        if r>600: break
        act=set()
        for g,s in row['gs'].items():
            g=int(g)
            if s!=2 or val.get(g,0)<20: continue
            ours=[c for c in row['c'] if c[1]==us and c[9]]
            near=[c for c in ours if max(abs(c[3]-cen[g][0]),abs(c[4]-cen[g][1]))<=6]
            on=[c for c in near if (c[3],c[4]) in tiles[g]]
            if near and cur.get(g,2)==2 and not on:
                act.add(g)
                if g not in run: run[g]=[r,r,[]]
                run[g][1]=r; run[g][2].append([(c[0],c[3],c[4],int(c[5])) for c in near])
        for g in list(run):
            if g not in act:
                r0,r1,nn=run.pop(g); n=r1-r0+1; L[min(n,20)]+=1
                if n>=4: eps.append((b,g,r0,r1,val[g],cen[g],nn[0],nn[-1]))
print('episode length dist',sorted(L.items()))
print('episodes>=4:',len(eps),'rounds in them',sum(e[3]-e[2]+1 for e in eps))
for e in eps[:60]: print(e)

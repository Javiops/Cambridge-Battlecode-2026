# missing.py TAG: at every [v12-sync] line fired by the cap (arr<want) on a gold group (gold>=20, r<=600), where are our
# alive members farther than 5 from every live camp of that group: distance bucket, hitting another camp, at home spawn (<=2 of a spawn tile of ours).
import json,gzip,glob,collections,sys,zipfile,re
W='/home/user/ws'; T=sys.argv[1]
C=collections.Counter(); n=0
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    b=f.split('/')[-1][:-8]; side=b[-1]; us=0 if side=='a' else 1; D=json.load(gzip.open(f))
    out=zipfile.ZipFile(f'{W}/rep/{T}/{b}.repl26a').read(f'team-{side}.stdout').decode(errors='replace')
    grp={k[0]:k[2] for k in D['camps']}; cpos={k[0]:(k[3],k[4]) for k in D['camps']}; gg={}
    for k in D['camps']: gg[k[2]]=max(gg.get(k[2],0),k[6] or 0)
    R={row['r']:row for row in D['rounds']}
    hitters={}
    for r,dd in D['ck'].items():
        for k in dd: a,ci=map(int,k.split('>')); hitters[(int(r),a)]=grp.get(ci)
    spawn=[(c[3],c[4]) for c in D['rounds'][0]['c'] if c[1]==us]
    done=set()
    for m in re.finditer(r'\[v12-sync\] r=(\d+) ch=(\w+) grp=(\d+) wait=(\d+) n=(\d+)/(\d+)',out):
        r,g,a,w=int(m.group(1)),int(m.group(3)),int(m.group(5)),int(m.group(6))
        if r>600 or a>=w or gg.get(g,0)<20 or (r,g) in done or r not in R: continue
        done.add((r,g)); n+=1
        live=[cpos[ci] for ci in R[r]['ka'] if grp.get(ci)==g]
        if not live: continue
        for c in R[r]['c']:
            if c[1]!=us or not c[9]: continue
            d=min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in live)
            if d<=5: continue
            k='d6-10' if d<=10 else 'd11-20' if d<=20 else 'd>20'
            if (r,c[0]) in hitters: k+='/hitting-other'
            elif min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in spawn)<=2: k+='/at-spawn'
            C[k]+=1
print(T,'capped sync events on gold groups',n); tot=sum(C.values())
for k,v in sorted(C.items()): print('  %-24s %5d %5.1f%%'%(k,v,100*v/max(1,tot)))

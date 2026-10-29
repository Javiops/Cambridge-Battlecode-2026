# camp17.py DECDIR --index I : detail of camp deaths r30-150 (death15 'camp' class)
import sys, os, json, gzip, collections
TYPES = ['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
d = sys.argv[1]; side = {x["file"]: (0 if x["side"]=="a" else 1) for x in json.load(open(sys.argv[3]))} if len(sys.argv)>3 else None
bot = os.path.basename(d.rstrip('/'))
def cheb(p,q): return max(abs(p[0]-q[0]),abs(p[1]-q[1]))
S = collections.Counter(); rows=[]
for fn in sorted(os.listdir(d)):
    key=f"{bot}/{fn.replace('.json.gz','.repl26a')}"
    if side is not None and key not in side: continue
    us=side[key] if side else 0; D=json.load(gzip.open(os.path.join(d,fn))); R=D['rounds']
    if not R: continue
    byr={rr['r']:{c[0]:c for c in rr['c']} for rr in R}
    camps={k[0]:k for k in D['camps']}
    cc=collections.defaultdict(list)
    for r,at,t,dm in D['cc']: cc[t].append((r,at,dm))
    ckby=collections.defaultdict(list)
    for r,a,k,dm,kind in D['ck']: ckby[a].append((r,k,dm))
    for idx in [c[0] for c in R[0]['c'] if c[1]==us]:
        for r in range(30,151):
            if r not in byr or r-1 not in byr: continue
            if not (byr[r-1][idx][9] and not byr[r][idx][9]): continue
            hp10=byr[r-10][idx][5] if r-10 in byr and byr[r-10][idx][9] else byr[r-1][idx][5]
            cd=sum(dm for q,at,dm in cc[idx] if r-10<=q<=r)
            if cd>=0.5*max(hp10,1): continue
            me=byr[r-1][idx]
            hits=[(q,k,dm) for q,k,dm in ckby[idx] if r-15<=q<r]
            grp=collections.Counter(camps[k][2] for q,k,dm in hits)
            g=grp.most_common(1)[0][0] if grp else None
            # first hit on this group in this engagement
            first=None
            if g is not None:
                q=r-1
                hs=sorted(q for q,k,dm in ckby[idx] if camps[k][2]==g and q<r)
                first=hs[-1]
                for x in reversed(hs):
                    if first-x<=6: first=x
                    else: break
            hp0=byr[first][idx][5]/byr[first][idx][6] if first and first in byr else None
            gmax=sum(k[7] for k in D['camps'] if k[2]==g) if g is not None else 0
            # allies hitting same group in last 15
            co=set(a for a in ckby for q,k,dm in ckby[a] if r-15<=q<r and camps[k][2]==g and a!=idx and byr[r-1].get(a,[0,us])[1]==us) if g is not None else set()
            foes=[c for c in byr[r-1].values() if c[1]!=us and c[9] and cheb(c[3:5],me[3:5])<=6]
            ctype=collections.Counter(camps[k][1] for q,k,dm in hits)
            row=(fn[:28],r,TYPES[me[2]],f"hp0={hp0 and round(hp0,2)}",f"start={first}",f"dur={first and r-first}",f"grpHP={gmax}",f"co={len(co)}",f"foes6={len(foes)}",f"cdmg={int(cd)}/{int(hp10)}",f"ctypes={dict(ctype)}")
            rows.append(row); S[TYPES[me[2]]]+=1
for x in rows: print(*x)
print(S)

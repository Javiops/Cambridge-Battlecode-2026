# why36f.py: outnumbered deaths (3+ foes within 6) r151-600: warning time, what the victim did, allies near, victim fought back?
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
RES=sys.argv[1]
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
S=[collections.Counter(),collections.Counter()]; n=0; warnh=[collections.Counter(),collections.Counter()]
for x in T:
    if x['bot'] not in DIR or x['result']!=RES: continue
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; n+=1
    R={row['r']:{c[0]:c for c in row['c']} for row in D['rounds']}
    grp={k[0]:k[2] for k in D['camps']}
    for r in sorted(R):
        if r<=151 or r>600 or r-1 not in R: continue
        for cid,c in R[r].items():
            p=R[r-1][cid]
            if not (p[9] and not c[9]): continue
            i=0 if c[1]==us else 1
            fo=[a for a in R[r-1].values() if a[1]!=c[1] and a[9] and ch(a,p)<=6]
            if len(fo)<3: continue
            S[i]['n']+=1
            # warning: earliest round in last 25 from which every round had >=3 foes within 8
            tw=r-1
            for rr in range(r-1,r-26,-1):
                if rr not in R or not R[rr][cid][9]: break
                v=R[rr][cid]
                if sum(1 for a in R[rr].values() if a[1]!=c[1] and a[9] and ch(a,v)<=8)>=3: tw=rr
                else: break
            w=r-tw; warnh[i][min(w,10)//2*2]+=1; S[i]['warn']+=w
            v=R[tw][cid]
            S[i]['hpw']+=v[5]/v[6]
            S[i]['allies6']+=sum(1 for a in R[tw].values() if a[1]==c[1] and a[0]!=cid and a[9] and ch(a,v)<=6)
            S[i]['allies12']+=sum(1 for a in R[tw].values() if a[1]==c[1] and a[0]!=cid and a[9] and ch(a,v)<=12)
            # victim at a camp in window? (damage to camps)
            camp=any(k.startswith(f'{cid}>') for rr in range(tw-3,r) for k in D['ck'].get(str(rr),{}))
            S[i]['camp']+=camp
            dealt=sum(vv for rr in range(tw,r+1) for k,vv in D['cc'].get(str(rr),{}).items() if k.startswith(f'{cid}>'))
            S[i]['dealt']+=dealt
            # did victim move away from foes centroid over the window? distance to nearest foe at tw vs r-1
            d0=min(ch(a,v) for a in R[tw].values() if a[1]!=c[1] and a[9]); d1=min(ch(a,p) for a in fo)
            S[i]['closer']+= d1<d0; S[i]['farther']+= d1>d0
            S[i]['gemscarried']+=p[7]
print(f'{RES} n={n}: deaths r151-600 with 3+ foes within 6 (us / rival)')
print(f"  count/game {S[0]['n']/n:.2f} / {S[1]['n']/n:.2f}")
for k in ['warn','hpw','allies6','allies12','camp','dealt','closer','farther','gemscarried']:
    print(f"  per death {k:10s} {S[0][k]/max(1,S[0]['n']):7.2f} / {S[1][k]/max(1,S[1]['n']):7.2f}")
print('  warning rounds histogram (us):',sorted(warnh[0].items()))

# why36g.py: for deaths r151-600 with 3+ foes within 6: the engagement's first contact (nearest foe <=6, gaps <=4 rounds):
# foes/allies within 6 at first contact, rounds from first contact to death, and the round the 3rd foe arrived
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
RES=sys.argv[1]
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
S=[collections.Counter(),collections.Counter()]; H=[collections.Counter(),collections.Counter()]
for x in T:
    if x['bot'] not in DIR or x['result']!=RES: continue
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1
    R={row['r']:{c[0]:c for c in row['c']} for row in D['rounds']}
    for r in sorted(R):
        if r<=151 or r>600 or r-1 not in R: continue
        for cid,c in R[r].items():
            p=R[r-1][cid]
            if not (p[9] and not c[9]): continue
            i=0 if c[1]==us else 1
            F=lambda rr,d: [a for a in R[rr].values() if a[1]!=c[1] and a[9] and ch(a,R[rr][cid])<=d]
            A=lambda rr,d: [a for a in R[rr].values() if a[1]==c[1] and a[0]!=cid and a[9] and ch(a,R[rr][cid])<=d]
            if len(F(r-1,6))<3: continue
            # walk back: engagement start = earliest round with foe<=6 such that no gap > 4 rounds
            fc=r-1; gap=0; rr=r-1
            while rr-1 in R and R[rr-1][cid][9] and rr>r-80:
                rr-=1
                if F(rr,6): fc=rr; gap=0
                else:
                    gap+=1
                    if gap>4: break
            n0=len(F(fc,6)); a0=len(A(fc,6))
            third=next((q for q in range(fc,r) if len(F(q,6))>=3),r-1)
            S[i]['n']+=1; S[i]['dur']+=r-fc; S[i]['f0']+=n0; S[i]['a0']+=a0; S[i]['third']+=third-fc
            S[i]['start_le2']+= n0<=2 and a0+1>=n0
            S[i]['third_late']+= third-fc>=3
            H[i][(min(n0,3),min(a0+1,3))]+=1
for i,who in enumerate(('us','rival')):
    n=max(1,S[i]['n'])
    print(f"{RES} {who}: n={S[i]['n']} contact->death {S[i]['dur']/n:.1f} r, foes<=6 at first contact {S[i]['f0']/n:.2f}, our bodies {1+S[i]['a0']/n:.2f}, 3rd foe arrives after {S[i]['third']/n:.1f} r; started even-or-better {S[i]['start_le2']/n:.0%}, 3rd foe came 3+ rounds later {S[i]['third_late']/n:.0%}")
    print('   (foes, our bodies) at first contact:',sorted(H[i].items(),key=lambda z:-z[1])[:8])

# why36h.py: "turned" episodes: a champion in contact (foe<=6) that becomes outnumbered (foes<=6 >= own bodies<=6 + 2, 3+ foes).
# What happens in the next 12 rounds: dies / leaves (no foe within 6 for 2 rounds, alive) / stays. Per team, losses and wins.
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
for RES in ('loss','win'):
    S=[collections.Counter(),collections.Counter()]; n=0
    for x in T:
        if x['bot'] not in DIR or x['result']!=RES: continue
        f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
        if not os.path.exists(f): continue
        D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; n+=1
        R={row['r']:{c[0]:c for c in row['c']} for row in D['rounds']}
        busy={}
        for r in sorted(R):
            if r<151 or r>588: continue
            for cid,c in R[r].items():
                if not c[9] or busy.get(cid,-1)>=r: continue
                fo=[a for a in R[r].values() if a[1]!=c[1] and a[9] and ch(a,c)<=6]
                al=[a for a in R[r].values() if a[1]==c[1] and a[0]!=cid and a[9] and ch(a,c)<=6]
                if len(fo)>=3 and len(fo)>=len(al)+3:
                    i=0 if c[1]==us else 1
                    out='stay'; d0=min(ch(a,c) for a in fo)
                    first_move=None
                    for q in range(r+1,r+13):
                        if q not in R or q+1 not in R: break
                        v=R[q][cid]
                        if not v[9]: out='die'; break
                        f2=[a for a in R[q].values() if a[1]!=c[1] and a[9] and ch(a,v)<=6]
                        if first_move is None and (v[3],v[4])!=(c[3],c[4]):
                            first_move= min([ch(a,v) for a in R[q].values() if a[1]!=c[1] and a[9]] or [99]) - d0
                        if not f2:
                            if q+1 in R and R[q+1][cid][9] and not [a for a in R[q+1].values() if a[1]!=c[1] and a[9] and ch(a,R[q+1][cid])<=6]:
                                out='leave'; break
                    S[i][out]+=1; S[i]['n']+=1
                    if first_move is not None: S[i]['away' if first_move>0 else ('toward' if first_move<0 else 'same')]+=1
                    busy[cid]=r+12
    print(f'{RES} n={n} games: champion outnumbered by 3+ (3+ foes within 6), next 12 rounds')
    for i,w in enumerate(('us','rival')):
        m=max(1,S[i]['n'])
        print(f"  {w:5s} episodes/game {S[i]['n']/n:.2f}: die {S[i]['die']/m:.0%} leave {S[i]['leave']/m:.0%} stay {S[i]['stay']/m:.0%}; first step away {S[i]['away']/m:.0%} toward {S[i]['toward']/m:.0%} same {S[i]['same']/m:.0%}")

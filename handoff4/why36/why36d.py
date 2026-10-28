# why36d.py: champion-round allocation r1-600: dead / fighting champions / at big group / at other camp / at altar-walk / idle-walk
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
RES=sys.argv[1]
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
S=[collections.Counter(),collections.Counter()]; n=0
for x in T:
    if x['bot'] not in DIR or x['result']!=RES: continue
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; n+=1
    grp={}; gv={}
    for k in D['camps']: grp[k[0]]=k[2]; gv[k[2]]=max(gv.get(k[2],0),k[5] or 0)
    kpos={k[0]:(k[3],k[4]) for k in D['camps']}
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    for row in D['rounds']:
        r=row['r']
        if r<1 or r>600: continue
        cc=D['cc'].get(str(r),{}); ck=D['ck'].get(str(r),{})
        fight=set()
        for k in cc: a,b=map(int,k.split('>')); fight.add(a); fight.add(b)
        hit={}
        for k in ck: a,ci=map(int,k.split('>')); hit[a]=ci
        alive=[kpos[i] for i in row['ka']] if row.get('ka') else []
        akb=[kpos[i] for i in row['ka'] if gv.get(grp[i],0)>=40]
        ph='a' if r<=150 else ('b' if r<=300 else 'c')
        for c in row['c']:
            i=0 if c[1]==us else 1
            if not c[9]: k='dead'
            elif c[0] in fight: k='fight'
            elif c[0] in hit: k='bigcamp' if gv.get(grp[hit[c[0]]],0)>=40 else 'camp'
            elif akb and min(ch((c[3],c[4]),p) for p in akb)<=3: k='bigcamp'
            elif alive and min(ch((c[3],c[4]),p) for p in alive)<=2: k='camp'
            else: k='move'
            S[i][k+ph]+=1; S[i][k]+=1
print(f'{RES} n={n}: champion-rounds per game r1-600, us / rival  [r1-150 | r151-300 | r301-600]')
for k in ['dead','fight','bigcamp','camp','move']:
    print(f"  {k:8s} {S[0][k]/n:6.0f} / {S[1][k]/n:6.0f}   [" + ' | '.join(f"{S[0][k+p]/n:.0f}/{S[1][k+p]/n:.0f}" for p in 'abc')+']')

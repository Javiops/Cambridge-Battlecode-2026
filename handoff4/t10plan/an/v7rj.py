# v7rj.py: our deaths r151-600 with 3+ foes within 6 in v7 local games: was there a rejudge by that champion in the 25 rounds before? what mode/positions after
import json,gzip,os,zipfile,re,collections,sys
W='/tmp/claude-0/w'; A=sys.argv[1]
TN={0:'ryth',1:'vesper',2:'vendetta',7:'marcella',12:'heartofruin'}
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
S=collections.Counter(); ex=[]
for fn in sorted(os.listdir(f'{W}/ws/rep/{A}')):
    if not fn.endswith('.repl26a'): continue
    b=fn[:-8]; side=b[-1]; us=0 if side=='a' else 1
    out=zipfile.ZipFile(f'{W}/ws/rep/{A}/{fn}').read(f'team-{side}.stdout').decode(errors='replace')
    rj=[(int(m.group(1)),m.group(2)) for m in re.finditer(r'\[v7-rejudge\] r=(\d+) who=(\S+)',out)]
    D=json.load(gzip.open(f'{W}/dec/{A}/{b}.json.gz'))
    R={row['r']:{c[0]:c for c in row['c']} for row in D['rounds']}
    # outcome of each rejudge: survive 15 rounds? nearest foe distance change after 3 rounds
    for r,who in rj:
        cs=[c for c in R.get(r,{}).values() if c[1]==us and who.startswith(TN.get(c[2],'?'))]
        if not cs or r+15 not in R: continue
        c=cs[0]; S['rj']+=1
        died=any(not R[q][c[0]][9] for q in range(r,r+16) if q in R)
        S['rjdied']+=died
        f0=min([ch(a,c) for a in R[r].values() if a[1]!=us and a[9]] or [99]); v=R[r+3][c[0]]
        f3=min([ch(a,v) for a in R[r+3].values() if a[1]!=us and a[9]] or [99]) if v[9] else -1
        S['away']+= f3>f0; S['closer']+= 0<=f3<f0
    prev={}
    for row in D['rounds']:
        r=row['r']
        for c in row['c']:
            p=prev.get(c[0])
            if p and p[9] and not c[9] and c[1]==us and 150<r<=600 and sum(1 for a in prev.values() if a[1]!=us and a[9] and ch(a,p)<=6)>=3:
                S['d3']+=1
                had=[q for q,w in rj if w.startswith(TN.get(c[2],'?')) and r-25<=q<=r]
                S['d3rj']+=bool(had)
                if len(ex)<12: ex.append((b,r,TN.get(c[2]),had))
        prev={c[0]:c for c in row['c']}
print(dict(S)); print(*ex,sep='\n')

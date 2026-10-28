# why36e.py: fight exchange (champion damage dealt/taken, heal), max hp growth, gold spent, deaths with 3+ foes near, rival pack origin
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
RES=sys.argv[1]
def ch(a,b): return max(abs(a[3]-b[3]),abs(a[4]-b[4]))
S=[collections.Counter(),collections.Counter()]; n=0
for x in T:
    if x['bot'] not in DIR or x['result']!=RES: continue
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; n+=1
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    I=lambda t:0 if t==us else 1
    for r,dd in D['cc'].items():
        if int(r)>600: continue
        for k,v in dd.items(): a,b=map(int,k.split('>')); S[I(team[a])]['ccdealt']+=v
    for r,dd in D['heal'].items():
        if int(r)>600: continue
        for k,v in dd.items(): a,b=map(int,k.split('>')); S[I(team[a])]['heal']+=v
    for r,dd in D['kc'].items():
        if int(r)>600: continue
        for k,v in dd.items(): a,b=k.split('>'); S[I(team[int(b)])]['camptaken']+=v
    prev={}
    for row in D['rounds']:
        r=row['r']
        if r in (150,300,450):
            for c in row['c']:
                S[I(c[1])][f'mhp{r}']+=c[6]; S[I(c[1])][f'gold{r}']+=c[8]
        for c in row['c']:
            p=prev.get(c[0])
            if p and p[9] and not c[9] and 150<r<=600:
                fo=sum(1 for a in prev.values() if a[1]!=c[1] and a[9] and ch(a,p)<=6)
                S[I(c[1])]['d']+=1; S[I(c[1])]['d3']+= fo>=3
        prev={c[0]:c for c in row['c']}
print(f'{RES} n={n}, us / rival per game (r1-600)')
for k in ['ccdealt','heal','camptaken']: print(f'  {k:10s} {S[0][k]/n:8.0f} / {S[1][k]/n:8.0f}')
for r in (150,300,450): print(f'  r{r}: team max hp {S[0][f"mhp{r}"]/n:.0f} / {S[1][f"mhp{r}"]/n:.0f}; gold held {S[0][f"gold{r}"]/n:.0f} / {S[1][f"gold{r}"]/n:.0f}')
print(f'  deaths r151-600 {S[0]["d"]/n:.2f} / {S[1]["d"]/n:.2f}; with 3+ foes within 6: {S[0]["d3"]/n:.2f} / {S[1]["d3"]/n:.2f}')

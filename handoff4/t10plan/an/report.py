import sys, pickle
from collections import defaultdict
sys.path.insert(0,'/tmp/claude-0/w/an'); from agg import team_bin, KINDS
R=pickle.load(open('/tmp/claude-0/w/rows.pkl','rb'))
ours_maps=set(r['map'] for r in R if r['src']=='ours')
K=['alive','deaths','fr','own','home','al4','big','ncl','contact','outn','hitr','h_mates']+['h_'+k for k in KINDS]+['caps','capgems']
def avg(rows,b):
    s=defaultdict(float); n=0
    for r in rows:
        o=team_bin(r,b)
        if o is None: continue
        n+=1
        for k in K: s[k]+=o.get(k,0)
    return {k:s[k]/n for k in K} if n else None, n
def table(sel, title, bins=range(0,12)):
    print('##',title)
    print('bin   ', ' '.join(f'{k[:7]:>7}' for k in K))
    for b in bins:
        for lab,rows in sel:
            a,n=avg(rows,b)
            if a: print(f'{b*50:>3} {lab:5}', ' '.join(f'{a[k]:7.2f}' for k in K), n)
if __name__=='__main__':
    t10=[r for r in R if r['src']=='t10' and r['map'] in ours_maps]
    sel=[('T10W',[r for r in t10 if r['win']]),('T10L',[r for r in t10 if not r['win']]),('OURS',[r for r in R if r['src']=='ours']),('RIV',[r for r in R if r['src']=='riv'])]
    table(sel,'all shared maps')

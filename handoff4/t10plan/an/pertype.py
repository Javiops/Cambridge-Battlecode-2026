import pickle, sys
from collections import defaultdict
sys.path.insert(0,'/tmp/claude-0/w/an')
R=pickle.load(open('/tmp/claude-0/w/rows.pkl','rb'))
TN={0:'Ryth',1:'Vesper',2:'Vendetta',7:'Marcella',12:'HoR',11:'Tavi',3:'Cassi',4:'Issac',5:'Stellar',6:'Prism',8:'Willow',9:'Ren',10:'Varg'}
om=set(r['map'] for r in R if r['src']=='ours')
PH=[(0,0),(1,2),(3,5),(6,11)]
def agg(rows):
    S=defaultdict(lambda: defaultdict(float))
    for r in rows:
        F=r['F']; t=r['team']
        for (i,b),f in F['F'].items():
            if F['team'][i]!=t: continue
            ph=[k for k,(a,z) in enumerate(PH) if a<=b<=z]
            if not ph: continue
            key=(TN.get(F['typ'][i],'?'),ph[0]); s=S[key]
            for k in ('n','alive','fr','own','al4','contact','outn','death','gems'): s[k]+=f.get(k,0)
    return S
sets={'W':[r for r in R if r['src']=='t10' and r['map'] in om and r['win']],'L':[r for r in R if r['src']=='t10' and r['map'] in om and not r['win']],'O':[r for r in R if r['src']=='ours']}
A={k:agg(v) for k,v in sets.items()}
print('type      ph | W: alive fr own al4 outn/c death/g gems | L ... | O ...')
for ty in ('HoR','Vesper','Marcella','Vendetta','Ryth'):
    for ph in range(4):
        line=f'{ty:9} {PH[ph][0]*50:3}-{PH[ph][1]*50+50:3}'
        for k in 'WLO':
            s=A[k].get((ty,ph))
            if not s or not s['alive']: line+=' |   -'; continue
            a=s['alive']; ng=s['n']/((PH[ph][1]-PH[ph][0]+1)*50)
            line+=f" | {a/s['n']:.2f} {s['fr']/a:.2f} {s['own']/a:.2f} {s['al4']/a:.2f} {s['outn']/max(1,s['contact']):.2f} {s['death']/ng:.2f} {s['gems']/a:4.1f} n{ng:.0f}"
        print(line)

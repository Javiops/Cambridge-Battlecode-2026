import json,glob,sys,os,collections
sys.path.insert(0,os.path.dirname(__file__)); 
def at(runs,r):
    t=0;v=0
    for x in runs:
        if t>r: break
        v=float(x['value']); t+=x['duration']
    return v
exec(open(os.path.dirname(os.path.abspath(__file__))+'/mbuy.py').read().split('J=jobs')[0])
J=jobs(sys.argv[1]); A=collections.defaultdict(float); n=0
for summ,tn in J:
    s=json.load(open(summ)); tl={t['metric']:t for t in s['championTimelines'] if t['owner']['team']==tn and t['owner']['name']=='Marcella'}
    if 'earnedGold' not in tl: continue
    n+=1
    for R in (150,250,400):
        for m in ('earnedGold','gold','spentGold','deaths','submittedGems','collectedGems'): A[m,R]+=at(tl[m]['runs'],R)
print(sys.argv[1],n)
for R in (150,250,400): print(R,' '.join(f"{m} {A[m,R]/n:.0f}" for m in ('earnedGold','gold','spentGold','deaths','collectedGems','submittedGems')))

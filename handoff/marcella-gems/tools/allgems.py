import json,glob,sys,os,collections
def at(runs,r):
    t=0;v=0
    for x in runs:
        if t>r: break
        v=float(x['value']); t+=x['duration']
    return v
w=sys.argv[1]
if w=='t10':
    L=json.load(open('/mnt/project-files/online/data/t10_vs_band_1024/index.json'))['games']
    J=[(g['summary'],'teamA' if g['side']=='a' else 'teamB') for g in L if not g.get('far') and g.get('summary') and '6' in g['draft']]
else: J=[(f,'teamA' if os.path.basename(f).startswith('A_') else 'teamB') for f in glob.glob(w+'/*/*.json')]
A=collections.defaultdict(float); N=collections.Counter()
for summ,tn in J:
    s=json.load(open(summ))
    for t in s['championTimelines']:
        if t['owner']['team']!=tn or t['metric'] not in ('collectedGems','submittedGems','earnedGold','monsterDamageDone'): continue
        nm=t['owner']['name']
        for R in (150,400): A[nm,t['metric'],R]+=at(t['runs'],R)
        if t['metric']=='earnedGold': N[nm]+=1
print(w)
for nm in N:
    n=N[nm]; print(f"{nm:14s} n{n:3d} "+' | '.join(f"r{R} gems {A[nm,'collectedGems',R]/n:5.1f} sub {A[nm,'submittedGems',R]/n:5.1f} gold {A[nm,'earnedGold',R]/n:4.0f} mob {A[nm,'monsterDamageDone',R]/n:5.0f}" for R in (150,400)))

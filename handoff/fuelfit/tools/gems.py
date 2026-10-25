import json,sys
# gems.py FILE... : submittedGems us/them at r100..r600
def at(runs,r):
    t=0;v=0
    for x in runs:
        if t+x['duration']>r: return int(x['value'])
        t+=x['duration']; v=int(x['value'])
    return v
for f in sys.argv[1:]:
    d=json.load(open(f)); us='teamA' if '/A_' in f else 'teamB'
    g={}
    for t in d['teamTimelines']:
        if t['metric']=='submittedGems': g[t['owner']]=t['runs']
    them=[k for k in g if k!=us][0]
    row=[f"r{r}:{at(g[us],r)}/{at(g[them],r)}" for r in (100,200,300,400,600)]
    print(f.split('res/')[-1].ljust(40),'WIN ' if d['match']['outcome']==us else 'loss',*row)

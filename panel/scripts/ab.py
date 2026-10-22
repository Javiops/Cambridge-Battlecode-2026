"""Summarise local A/B dirs res/TAG/{A,B}_map.json (cand=teamA in A_, teamB in B_). Also per-game outcome vector for flip counts."""
import json, glob, sys, os
def load(tag):
    R={}
    for f in sorted(glob.glob(f'res/{tag}/[AB]_*.json')):
        d=json.load(open(f)); b=os.path.basename(f)[:-5]; cand='teamA' if b.startswith('A_') else 'teamB'
        o=d['match']['outcome']; r = 1 if o==cand else (0.5 if o in ('draw',None) else 0)
        st={'cand':{}, 'base':{}}
        for c in d['champions']:
            k='cand' if c['team']==cand else 'base'; m=c['metrics']; s=st[k]
            if c['name']!='Issac': s['deaths']=s.get('deaths',0)+int(m['deaths'])
            s['kills']=s.get('kills',0)+int(m['kills']); s['gems']=s.get('gems',0)+int(m['submittedGems'])
        R[b]=(r,st)
    return R
if __name__=='__main__':
    tags=sys.argv[1:]; base=load('self') if os.path.isdir('res/self') else {}
    for t in tags:
        R=load(t); n=len(R); w=sum(v[0] for v in R.values())
        agg=lambda k,f: sum(v[1][k].get(f,0) for v in R.values())/max(1,n)
        flips = sum(1 for g in R if g in base and R[g][0]!=base[g][0])
        print(f"{t:18s} n={n:3d} cand {w:5.1f}-{n-w:5.1f}  deaths c/b {agg('cand','deaths'):.1f}/{agg('base','deaths'):.1f} kills {agg('cand','kills'):.1f}/{agg('base','kills'):.1f} gems {agg('cand','gems'):.0f}/{agg('base','gems'):.0f}  outcome differs from self-play game: {flips}")

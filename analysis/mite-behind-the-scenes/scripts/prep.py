# Is Mite's play a fixed per-map plan? Compare its champion trajectories across games on the same map (different opponents),
# normalised to side A by the map symmetry. Also: squad size per camp vs camp group, and kill speed.
import json, glob, collections, sys, itertools
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws'
sel=json.load(open(S+'/selected.json')); maps={m.split('/')[-1][:-5]:json.load(open(m)) for m in glob.glob(S+'/mapsj/*.json')}
def mirror(m,x,y):
    w,h,s=m['w'],m['h'],m['sym']
    return {'V':(w-1-x,y),'H':(x,h-1-y),'R180':(w-1-x,h-1-y)}[s]
def load(match):
    rounds={}
    for line in open(f'{S}/steps/{match}.c.jsonl'):
        d=json.loads(line)
        if d['t']=='round': rounds[d['r']]=d
    return rounds
team=sys.argv[1] if len(sys.argv)>1 else 'mite'
games=[g for g in sel if g['team']==team]
bymap=collections.defaultdict(list)
for g in games: bymap[g['map']].append(g)
print(f'== {team}: trajectory similarity between games on the same map (positions of own champions by type, side-normalised)')
for mp,gs in sorted(bymap.items()):
    m=maps[mp]; trajs=[]
    for g in gs:
        R=load(g['match']); t=0 if g['side']=='a' else 1; tr={}
        for r,d in R.items():
            pos=[]
            for c in d['champs']:
                if c[1]!=t or not c[9]: continue
                x,y=c[3],c[4]
                if t==1: x,y=mirror(m,x,y)
                pos.append((c[2],x,y))
            tr[r]=tuple(sorted(pos))
        trajs.append((g,tr))
    # pairwise: identical rounds among first 30 / 100, first divergence round
    res=[]
    for (g1,t1),(g2,t2) in itertools.combinations(trajs,2):
        same30=sum(1 for r in range(1,31) if t1.get(r)==t2.get(r)); same100=sum(1 for r in range(1,101) if t1.get(r)==t2.get(r))
        div=next((r for r in range(1,400) if t1.get(r)!=t2.get(r)),400)
        res.append((same30,same100,div))
    import statistics as st
    print(f'{mp:10s} games {len(gs)} drafts {sorted(set(tuple(g["draft"]) for g in gs))} identical rounds in first 30: mean {st.mean(r[0] for r in res):.1f}  in first 100: {st.mean(r[1] for r in res):.1f}  first divergence: median r{st.median(r[2] for r in res):.0f} (min {min(r[2] for r in res)}, max {max(r[2] for r in res)})')

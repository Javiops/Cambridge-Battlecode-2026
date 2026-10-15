# For each camp group Mite captures: how many champions attacked it, time from first hit to capture, vs group hp / gems / distance.
import json, glob, collections, sys, statistics as st
from collections import deque
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws'
import os; sel=json.load(open(os.environ.get('SEL',S+'/selected.json'))); maps={m.split('/')[-1][:-5]:json.load(open(m)) for m in glob.glob(S+'/mapsj/*.json')}
def bfs(m,src):
    g=m['grid']; w,h=m['w'],m['h']; D=[[-1]*w for _ in range(h)]; q=deque()
    for (x,y) in src: D[y][x]=0; q.append((x,y))
    while q:
        x,y=q.popleft()
        for dx in(-1,0,1):
            for dy in(-1,0,1):
                nx,ny=x+dx,y+dy
                if 0<=nx<w and 0<=ny<h and D[ny][nx]<0 and g[ny][nx] not in '#o': D[ny][nx]=D[y][x]+1; q.append((nx,ny))
    return D
team=sys.argv[1] if len(sys.argv)>1 else 'mite'
rows=[]; idle=collections.Counter()
for g in sel:
    if g['team']!=team: continue
    m=maps[g['map']]; t=0 if g['side']=='a' else 1
    R={}; ev=collections.defaultdict(list)
    for line in open(f"{os.environ.get('STEPS',S+'/steps')}/{g['match']}.c.jsonl"):
        d=json.loads(line)
        if d['t']=='round': R[d['r']]=d
        elif d['t']=='ev': ev[d['r']].append(d)
    camps0={c[0]:c for c in R[0]['camps']}; grp={c[0]:c[7] for c in R[0]['camps']}
    ghp=collections.Counter(); gpos={}
    for c in R[0]['camps']: ghp[c[7]]+=c[4]; gpos.setdefault(c[7],(c[2],c[3]))
    own=[c[0] for c in R[0]['champs'] if c[1]==t]; nch=len(own)
    sp=[(c[3],c[4]) for c in R[0]['champs'] if c[1]==t]; D=bfs(m,sp)
    # per group: first hit round, attackers, capture round
    first={}; att=collections.defaultdict(set); respawn_r={}
    order=sorted(R)
    for r in order:
        for e in ev[r]:
            if e['ak']==1 and e['a'] in own and e['k'] in (5,6):
                for k in e.get('keff',[]):
                    if k.get('hp',0)<0 and k['i'] in grp:
                        gi=grp[k['i']]; key=(gi,respawn_r.get(gi,0))
                        first.setdefault(key,r); att[key].add(e['a'])
            if e['ak']==0 and e['ph']==7:
                for x in e.get('eff',[]):
                    if x['i'] in own and x.get('gems',0)>0:
                        # which group? the awake/alive->dead group nearest to the champion
                        c=R[r]['champs'][x['i']] if False else None
                        pos=next((cc[3],cc[4]) for cc in R[min(r,max(R))]['champs'] if cc[0]==x['i'])
                        gi=min(gpos,key=lambda q:max(abs(gpos[q][0]-pos[0]),abs(gpos[q][1]-pos[1])))
                        key=(gi,respawn_r.get(gi,0))
                        if key in first:
                            near=sum(1 for cc in R[r]['champs'] if cc[1]==t and cc[9] and max(abs(cc[3]-pos[0]),abs(cc[4]-pos[1]))<=4)
                            rows.append(dict(map=g['map'],nch=nch,r=r,gems=x['gems'],hp=ghp[gi],dist=D[gpos[gi][1]][gpos[gi][0]],n=len(att[key]),near=near,dur=r-first[key]))
                            respawn_r[gi]=r+1; first.pop(key,None); att.pop(key,None)
        # idle: alive own champions with no event this round
        acted={e['a'] for e in ev[r] if e['ak']==1}
        for cc in R[r]['champs']:
            if cc[1]==t and cc[9]: idle['alive']+=1; idle['noact']+= (cc[0] not in acted)
print(f'== {team}: {len(rows)} captures; champion-rounds alive {idle["alive"]}, with no action at all {idle["noact"]} ({100*idle["noact"]/idle["alive"]:.0f}%)')
def bucket(v,edges): return next((f'<{e}' for e in edges if v<e),f'>={edges[-1]}')
for name,key,edges in [('group hp','hp',[400,800,1500,3000]),('gems','gems',[30,60,100]),('dist from spawn','dist',[8,15,25,40]),('round','r',[50,150,300]),('team size','nch',[4,5])]:
    b=collections.defaultdict(list)
    for x in rows: b[bucket(x[key],edges)].append(x)
    print(f'-- by {name}:')
    for k in sorted(b,key=lambda s:(s[0]!='<',s)):
        xs=b[k]; print(f'   {k:6s} n={len(xs):3d} attackers mean {st.mean(x["n"] for x in xs):.2f} (within 4 at capture {st.mean(x["near"] for x in xs):.2f})  hit->capture {st.median(x["dur"] for x in xs):.0f} rounds  hp/attacker/round {st.median(x["hp"]/max(1,x["n"])/max(1,x["dur"]) for x in xs):.0f}')
# attackers vs hp per team size
print('-- attackers by (team size, hp bucket):')
b=collections.defaultdict(list)
for x in rows: b[(x['nch'],bucket(x['hp'],[400,800,1500,3000]))].append(x['n'])
for k in sorted(b): print('   ',k,'n=%d'%len(b[k]),'mean %.2f'%st.mean(b[k]),'dist',collections.Counter(b[k]).most_common(4))
json.dump(rows,open(f'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/behind/captures_{team}.json','w'))

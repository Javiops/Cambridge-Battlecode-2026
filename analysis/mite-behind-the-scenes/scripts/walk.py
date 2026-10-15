# Walking efficiency: between consecutive "purpose points" (capture, tribute done, recall/respawn arrival) how many
# single-tile moves did a champion make vs the BFS distance between the two points?
import json, glob, collections, sys, os, statistics as st
from collections import deque
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws'
sel=json.load(open(os.environ.get('SEL',S+'/selected.json'))); STEPS=os.environ.get('STEPS',S+'/steps')
maps={m.split('/')[-1][:-5]:json.load(open(m)) for m in glob.glob(S+'/mapsj/*.json')}
def bfs(m,src):
    g=m['grid']; w,h=m['w'],m['h']; D=[[-1]*w for _ in range(h)]; q=deque([src]); D[src[1]][src[0]]=0
    while q:
        x,y=q.popleft()
        for dx in(-1,0,1):
            for dy in(-1,0,1):
                nx,ny=x+dx,y+dy
                if 0<=nx<w and 0<=ny<h and D[ny][nx]<0 and g[ny][nx] not in '#o': D[ny][nx]=D[y][x]+1; q.append((nx,ny))
    return D
team=sys.argv[1]; tot=collections.Counter(); permap=collections.defaultdict(collections.Counter); cache={}
for g in sel:
    if g['team']!=team: continue
    m=maps[g['map']]; t=0 if g['side']=='a' else 1
    R={}; ev=collections.defaultdict(list)
    for line in open(f"{STEPS}/{g['match']}.c.jsonl"):
        d=json.loads(line)
        if d['t']=='round': R[d['r']]=d
        elif d['t']=='ev': ev[d['r']].append(d)
    own={c[0] for c in R[0]['champs'] if c[1]==t}
    seg={i:dict(start=(c[3],c[4]),steps=0,r0=0) for c in R[0]['champs'] if c[1]==t for i in [c[0]]}
    for r in sorted(R):
        if r==0: continue
        for e in ev[r]:
            if e['ak']==1 and e['a'] in own and e['k']==4:
                for x in e['eff']:
                    if x['i']==e['a'] and 'pos' in x:
                        x0,y0,x1,y1=x['pos']
                        if max(abs(x1-x0),abs(y1-y0))<=1: seg[e['a']]['steps']+=1
                        else: seg[e['a']]=dict(start=(x1,y1),steps=0,r0=r)   # recall / respawn arrival: new segment
            ends=[]
            if e['ak']==0 and e['ph']==7: ends=[x['i'] for x in e.get('eff',[]) if x['i'] in own and x.get('gems',0)>0]
            if e['ph'] in (13,14): ends+=[x['i'] for x in e.get('eff',[]) if x['i'] in own and x.get('gems',0)<0 and x.get('hp') is None]
            for i in ends:
                pos=next(((cc[3],cc[4]) for cc in R[r]['champs'] if cc[0]==i),None)
                if pos is None or pos[0]<0: continue
                s=seg[i]; key=(g['map'],s['start'])
                if key not in cache: cache[key]=bfs(m,s['start'])
                d=cache[key][pos[1]][pos[0]]
                if d>=0 and (s['steps']>0 or d>0):
                    tot['bfs']+=d; tot['steps']+=s['steps']; tot['n']+=1; permap[g['map']]['bfs']+=d; permap[g['map']]['steps']+=s['steps']; permap[g['map']]['n']+=1
                seg[i]=dict(start=pos,steps=0,r0=r)
print(f"== {team}: {tot['n']} segments, moves {tot['steps']}, shortest-path distance {tot['bfs']}, efficiency {tot['bfs']/max(1,tot['steps']):.2f} (1.0 = straight line), extra moves per segment {(tot['steps']-tot['bfs'])/max(1,tot['n']):.1f}")
for mp in sorted(permap): p=permap[mp]; print(f"   {mp:10s} n={p['n']:4d} eff {p['bfs']/max(1,p['steps']):.2f} extra/seg {(p['steps']-p['bfs'])/max(1,p['n']):.1f}")

import json, collections, os
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def load_sel():
    return json.load(open(S+'/ws/selected.json'))
MAPS={}
def load_map(name):
    if name not in MAPS:
        m=json.load(open(S+'/ws/mapsj/%s.json'%name))
        MAPS[name]=m
    return MAPS[name]
def mirror(m,x,y):
    w,h=m['w'],m['h']; s=m['sym']
    if s=='R180': return (w-1-x,h-1-y)
    if s in('H','HORIZ','horizontal'): return (w-1-x,y)
    if s in('V','VERT','vertical'): return (x,h-1-y)
    if s in('D','DIAG','diag'): return (y,x)
    return (w-1-x,h-1-y)
def bfs(m,src):
    """src: iterable of (x,y). returns dict dist"""
    g=m['grid']; w,h=m['w'],m['h']
    dist={}
    q=collections.deque()
    for s in src:
        dist[s]=0; q.append(s)
    while q:
        x,y=q.popleft(); d=dist[(x,y)]
        for dx in(-1,0,1):
            for dy in(-1,0,1):
                if dx==0 and dy==0: continue
                nx,ny=x+dx,y+dy
                if 0<=nx<w and 0<=ny<h and (nx,ny) not in dist and g[ny][nx] not in '#o':
                    dist[(nx,ny)]=d+1; q.append((nx,ny))
    return dist
def altars(m):
    return [(x,y) for y,row in enumerate(m['grid']) for x,c in enumerate(row) if c=='A']
def load_game(match):
    rounds={}; order=[]; events=collections.defaultdict(list); types={}; camps={}
    for line in open(S+'/ws/steps/%s.c.jsonl'%match):
        d=json.loads(line)
        if d['t']=='round':
            rounds[d['r']]={c[0]:dict(i=c[0],team=c[1],ty=c[2],x=c[3],y=c[4],hp=c[5],mhp=c[6],gems=c[7],gold=c[8],alive=c[9]) for c in d['champs']}
            camps[d['r']]=d['camps']
            order.append(d['r'])
            for c in d['champs']: types[c[0]]=(c[1],c[2])
        elif d['t']=='ev': events[d['r']].append(d)
    return rounds,order,events,types,camps

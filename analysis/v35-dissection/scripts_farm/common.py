import json, collections, math, os
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
WS=os.environ.get('FARM_WS',S+'/ws2')   # data dir: selected.json, steps/, mapsj/
SEL=json.load(open(WS+'/selected.json'))
ITEMS=[l.strip() for l in open('/mnt/project-files/analysis/data/items.txt') if l.strip()]
MAPS={}
TERR_T=3
def tier(orank): return 'top10' if orank<=10 else ('11-20' if orank<=20 else ('21-30' if orank<=30 else 'other'))
def mirror(mp,x,y):
    s=mp['sym']; w,h=mp['w'],mp['h']
    if s=='H': return (w-1-x,y)
    if s=='V': return (x,h-1-y)
    return (w-1-x,h-1-y)
def bfs(mp,srcs):
    w,h=mp['w'],mp['h']; g=mp['grid']; INF=10**6; d=[[INF]*w for _ in range(h)]; q=collections.deque()
    for (x,y) in srcs:
        if 0<=x<w and 0<=y<h and g[y][x] not in '#o' and d[y][x]==INF: d[y][x]=0; q.append((x,y))
    while q:
        x,y=q.popleft()
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                nx,ny=x+dx,y+dy
                if 0<=nx<w and 0<=ny<h and g[ny][nx] not in '#o' and d[ny][nx]==INF: d[ny][nx]=d[y][x]+1; q.append((nx,ny))
    return d
def near_d(mp,d,x,y):
    best=10**6
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nx,ny=x+dx,y+dy
            if 0<=nx<mp['w'] and 0<=ny<mp['h']: best=min(best,d[ny][nx])
    return best
def load_map(name):
    if name in MAPS: return MAPS[name]
    mp=json.load(open(WS+'/mapsj/%s.json'%name))
    x0,y0,x1,y1=mp['spawnA']
    sa=[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]; sb=[mirror(mp,x,y) for x,y in sa]
    mp['sp']=[set(sa),set(sb)]
    mp['dS']=[bfs(mp,sa),bfs(mp,sb)]
    mp['altars']=[(x,y) for y,row in enumerate(mp['grid']) for x,c in enumerate(row) if c=='A']
    mp['dAlt']=bfs(mp,[(x+dx,y+dy) for x,y in mp['altars'] for dx in (-1,0,1) for dy in (-1,0,1)])  # distance to a tile adjacent to any altar
    mp['dAltEach']=[bfs(mp,[(x+dx,y+dy) for dx in (-1,0,1) for dy in (-1,0,1)]) for x,y in mp['altars']]
    mp['jpos']={}
    for gi,g in enumerate(mp['groups']):
        for ci in g['camps']: mp['jpos'][(mp['camps'][ci]['x'],mp['camps'][ci]['y'])]=gi
    MAPS[name]=mp; return mp
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
class Game:
    def __init__(self,rec):
        self.rec=rec; mid=rec['match']; self.map=load_map(rec['map']); self.t=0 if rec['side']=='a' else 1
        self.R={}; self.ev=collections.defaultdict(list); self.order=[]; self.summary=None
        for line in open(WS+'/steps/%s.c.jsonl'%mid):
            d=json.loads(line)
            if d['t']=='round': self.R[d['r']]=d; self.order.append(d['r'])
            elif d['t']=='ev': self.ev[d['r']].append(d)
            elif d['t']=='summary': self.summary=d
        r0=self.R[self.order[0]]
        self.teamof={c[0]:c[1] for c in r0['champs']}; self.typeof={c[0]:c[2] for c in r0['champs']}
        self.own=[c[0] for c in r0['champs'] if c[1]==self.t]; self.opp=[c[0] for c in r0['champs'] if c[1]!=self.t]
        self.camp_group={c[0]:c[7] for c in r0['camps']}
        # groups: replay group index -> info
        mp=self.map; self.groups={}
        gt=collections.defaultdict(set); ghp=collections.Counter(); gtypes=collections.defaultdict(list)
        for c in r0['camps']: gt[c[7]].add((c[2],c[3])); ghp[c[7]]+=c[4]; gtypes[c[7]].append(c[1])
        for g,tiles in gt.items():
            jg=None
            for (x,y) in tiles:
                if (x,y) in mp['jpos']: jg=mp['jpos'][(x,y)]; break
                mx,my=mirror(mp,x,y)
                if (mx,my) in mp['jpos']: jg=mp['jpos'][(mx,my)]; break
            info=mp['groups'][jg] if jg is not None else dict(gems=0,gold=0,respawn=0)
            x,y=next(iter(tiles))
            dA=min(near_d(mp,mp['dS'][0],tx,ty) for tx,ty in tiles); dB=min(near_d(mp,mp['dS'][1],tx,ty) for tx,ty in tiles)
            do,de=(dA,dB) if self.t==0 else (dB,dA)
            terr='mid' if abs(do-de)<=TERR_T else ('own' if do<de else 'enemy')
            dalt=min(near_d(mp,mp['dAlt'],tx,ty) for tx,ty in tiles)
            self.groups[g]=dict(g=g,jg=jg,tiles=tiles,hp=ghp[g],gems=info['gems'],gold=info['gold'],respawn=info['respawn'],types=sorted(set(gtypes[g])),dOwn=do,dEnemy=de,terr=terr,dAlt=dalt,n=len(tiles))
        self.gdist={}   # bfs from group tiles, lazily
    def gd(self,g):
        if g not in self.gdist: self.gdist[g]=bfs(self.map,list(self.groups[g]['tiles']))
        return self.gdist[g]

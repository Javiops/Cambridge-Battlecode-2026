import json, glob, collections
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
SEL=json.load(open(S+'/ws/selected.json'))
MAPS={}
TERR_T=3   # |dOwn-dEnemy| <= T  => middle
def mirror(mp,x,y):
    s=mp['sym']; w,h=mp['w'],mp['h']
    if s=='H': return (w-1-x,y)
    if s=='V': return (x,h-1-y)
    return (w-1-x,h-1-y)
def bfs(mp,srcs):
    w,h=mp['w'],mp['h']; g=mp['grid']
    INF=10**6; d=[[INF]*w for _ in range(h)]
    q=collections.deque()
    for (x,y) in srcs:
        if g[y][x] not in '#o': d[y][x]=0; q.append((x,y))
    while q:
        x,y=q.popleft()
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                nx,ny=x+dx,y+dy
                if 0<=nx<w and 0<=ny<h and g[ny][nx] not in '#o' and d[ny][nx]==INF:
                    d[ny][nx]=d[y][x]+1; q.append((nx,ny))
    return d
def load_map(name):
    if name in MAPS: return MAPS[name]
    mp=json.load(open(S+'/ws/mapsj/%s.json'%name))
    x0,y0,x1,y1=mp['spawnA']
    sa=[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]
    sb=[mirror(mp,x,y) for x,y in sa]
    mp['sa']=sa; mp['sb']=sb
    mp['dA']=bfs(mp,sa); mp['dB']=bfs(mp,sb)
    mp['altars']=[(x,y) for y,row in enumerate(mp['grid']) for x,c in enumerate(row) if c=='A']
    mp['bush']={(x,y) for y,row in enumerate(mp['grid']) for x,c in enumerate(row) if c=='"'}
    # altar tiles are not walkable? treat adjacent walkable tile distance: dA of altar itself may be INF; use min of neighbours
    def near_d(d,x,y):
        best=10**6
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                nx,ny=x+dx,y+dy
                if 0<=nx<mp['w'] and 0<=ny<mp['h']: best=min(best,d[ny][nx])
        return best
    mp['nearD']=near_d
    # camp group spawn tiles
    mp['gtiles']=collections.defaultdict(set)
    for gi,g in enumerate(mp['groups']):
        for ci in g['camps']:
            c=mp['camps'][ci]; mp['gtiles'][gi].add((c['x'],c['y']))
    MAPS[name]=mp; return mp
def terr(mp,x,y,team):
    """territory of tile for team (0 = A): 'own','mid','enemy'"""
    if x<0: return None
    dA=mp['nearD'](mp['dA'],x,y); dB=mp['nearD'](mp['dB'],x,y)
    do,de=(dA,dB) if team==0 else (dB,dA)
    if abs(do-de)<=TERR_T: return 'mid'
    return 'own' if do<de else 'enemy'
def group_terr(mp,gi,team,gt=None):
    xs=list((gt or mp['gtiles'])[gi]); x,y=xs[0]
    return terr(mp,x,y,team)
def spawn_dist(mp,x,y,team):
    d=mp['dA'] if team==0 else mp['dB']
    return mp['nearD'](d,x,y)
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
class Game:
    def __init__(self,mid):
        self.mid=mid
        self.rounds={}; self.evs=collections.defaultdict(list); self.order=[]; self.sub={}; self.camps={}
        for line in open(S+'/ws/steps/%s.c.jsonl'%mid):
            d=json.loads(line)
            if d['t']=='round':
                self.rounds[d['r']]={c[0]:dict(i=c[0],team=c[1],ty=c[2],x=c[3],y=c[4],hp=c[5],mhp=c[6],gems=c[7],gold=c[8],alive=c[9]) for c in d['champs']}
                self.sub[d['r']]=d['sub']; self.order.append(d['r'])
                self.camps[d['r']]={k[0]:dict(i=k[0],ty=k[1],x=k[2],y=k[3],hp=k[4],alive=k[5],awake=k[6],g=k[7]) for k in d['camps']}
            elif d['t']=='ev': self.evs[d['r']].append(d)
        self.teamof={i:c['team'] for i,c in self.rounds[0].items()}
        self.gtiles=collections.defaultdict(set)
        for k in self.camps[0].values(): self.gtiles[k['g']].add((k['x'],k['y']))
        self.last=self.order[-1]
    def snap(self,r):
        # snapshot at end of round r (or nearest earlier)
        while r not in self.rounds and r>0: r-=1
        return self.rounds[r]
def focus_games():
    """yield (rec, Game, mp, team index) for every selected record"""
    for rec in SEL:
        yield rec
def phase(r):
    return 0 if r<100 else (1 if r<300 else 2)
PH=['0-100','100-300','300-end']

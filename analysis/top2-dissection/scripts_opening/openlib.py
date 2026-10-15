"""Loader + per-game opening extraction for the CAMBC 2026 compact replay format.
Usage as module: from openlib import *; g = Game(match_id); g.analyse(team, upto=60)
"""
import json, collections, os
S = '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
SEL = json.load(open(S + '/ws/selected.json'))
BYMATCH = {}
for rec in SEL:
    BYMATCH.setdefault(rec['match'], []).append(rec)

def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

class Map:
    cache = {}
    def __init__(self, name):
        m = json.load(open(S + '/ws/mapsj/%s.json' % name))
        self.name = name; self.w, self.h, self.sym, self.nch = m['w'], m['h'], m['sym'], m['nch']
        self.grid = m['grid']; self.camps = m['camps']; self.groups = m['groups']
        self.spawnA = m['spawnA']
        x0, y0, x1, y1 = self.spawnA
        self.spawn = {0: [(x, y) for x in range(x0, x1+1) for y in range(y0, y1+1)]}
        self.spawn[1] = [self.mirror(p) for p in self.spawn[0]]
        self.altars = [(x, y) for y, row in enumerate(self.grid) for x, ch in enumerate(row) if ch == 'A']
        self.dist = {0: self.bfs(self.spawn[0]), 1: self.bfs(self.spawn[1])}
        self.centre = ((self.w-1)/2, (self.h-1)/2)
        rad = 1
        while True:
            src = [(x, y) for x in range(self.w) for y in range(self.h) if cheb((x, y), self.centre) <= rad and self.passable(x, y)]
            if len(src) >= 4: break
            rad += 1
        self.centre_rad = rad
        self.dcentre = self.bfs(src)
        # camp -> group
        self.c2g = {}
        for gi, g in enumerate(self.groups):
            for ci in g['camps']: self.c2g[ci] = gi
        # group info
        self.ginfo = []
        for gi, g in enumerate(self.groups):
            tiles = [(self.camps[ci]['x'], self.camps[ci]['y']) for ci in g['camps']]
            types = sorted(set(self.camps[ci]['type'] for ci in g['camps']))
            dA = min(self.near(self.dist[0], t) for t in tiles); dB = min(self.near(self.dist[1], t) for t in tiles)
            side = 'mid' if abs(dA-dB) <= 2 else ('A' if dA < dB else 'B')
            self.ginfo.append(dict(g=gi, tiles=tiles, types=types, gems=g['gems'], gold=g['gold'], dA=dA, dB=dB, side=side,
                                   dc=min(self.near(self.dcentre, t) for t in tiles)))
        # altar info
        self.ainfo = []
        for a in self.altars:
            dA = self.near(self.dist[0], a); dB = self.near(self.dist[1], a)
            side = 'mid' if abs(dA-dB) <= 2 else ('A' if dA < dB else 'B')
            self.ainfo.append(dict(pos=a, dA=dA, dB=dB, side=side))
    def mirror(self, p):
        x, y = p
        if self.sym == 'V': return (x, self.h-1-y)
        if self.sym == 'H': return (self.w-1-x, y)
        return (self.w-1-x, self.h-1-y)
    def tile(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h: return self.grid[y][x]
        return '#'
    def passable(self, x, y): return self.tile(x, y) in '."'
    def bfs(self, src):
        INF = 10**6
        d = [[INF]*self.w for _ in range(self.h)]
        q = collections.deque()
        for (x, y) in src:
            if d[y][x] == INF: d[y][x] = 0; q.append((x, y))
        while q:
            x, y = q.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x+dx, y+dy
                    if (dx or dy) and self.passable(nx, ny) and d[ny][nx] == INF:
                        d[ny][nx] = d[y][x]+1; q.append((nx, ny))
        return d
    def near(self, d, t):
        """distance to a tile = min over its 8 neighbours (camps/altars are not walkable)"""
        x, y = t
        best = 10**6
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.w and 0 <= ny < self.h: best = min(best, d[ny][nx])
        return best
    def side_of(self, team, side):
        """translate map side 'A'/'B'/'mid' into own/enemy/mid for a team"""
        if side == 'mid': return 'mid'
        return 'own' if (side == 'A') == (team == 0) else 'enemy'
    @classmethod
    def get(cls, name):
        if name not in cls.cache: cls.cache[name] = cls(name)
        return cls.cache[name]

class Game:
    def __init__(self, match):
        self.match = match
        recs = BYMATCH[match]
        self.rec = recs[0]; self.map = Map.get(self.rec['map'])
        self.teams = {}
        for r in recs: self.teams[0 if r['side'] == 'a' else 1] = r['team']
        self.rounds = {}; self.events = collections.defaultdict(list); self.order = []
        for line in open(S + '/ws/steps/%s.c.jsonl' % match):
            d = json.loads(line)
            if d['t'] == 'round':
                self.rounds[d['r']] = dict(champs={c[0]: dict(i=c[0], team=c[1], ty=c[2], x=c[3], y=c[4], hp=c[5], mhp=c[6], gems=c[7], gold=c[8], alive=c[9]) for c in d['champs']},
                                           camps={c[0]: dict(i=c[0], ty=c[1], x=c[2], y=c[3], hp=c[4], alive=c[5], awake=c[6], g=c[7]) for c in d['camps']},
                                           sub=d['sub'])
                self.order.append(d['r'])
            elif d['t'] == 'ev':
                self.events[d['r']].append(d)
        self.types = {i: (c['team'], c['ty']) for i, c in self.rounds[0]['champs'].items()}
        self.champs = {t: [i for i, (tt, _) in self.types.items() if tt == t] for t in (0, 1)}
        # camp index -> group (from snapshot)
        self.c2g = {i: c['g'] for i, c in self.rounds[0]['camps'].items()}
        self.gtiles = collections.defaultdict(list)
        for i, c in self.rounds[0]['camps'].items(): self.gtiles[c['g']].append((c['x'], c['y']))
        self.gtypes = collections.defaultdict(set)
        for i, c in self.rounds[0]['camps'].items(): self.gtypes[c['g']].add(c['ty'])
        M = self.map
        self.ginfo = {}
        for gi, tiles in self.gtiles.items():
            dA = min(M.near(M.dist[0], t) for t in tiles); dB = min(M.near(M.dist[1], t) for t in tiles)
            side = 'mid' if abs(dA-dB) <= 2 else ('A' if dA < dB else 'B')
            self.ginfo[gi] = dict(g=gi, tiles=tiles, types=sorted(self.gtypes[gi]), dA=dA, dB=dB, side=side,
                                  dc=min(M.near(M.dcentre, t) for t in tiles))

    def name(self, i): return '%s%d' % (self.types[i][1][:4], i)

    def team_of_name(self, teamname):
        for t, n in self.teams.items():
            if n == teamname: return t
        return None

    def pos(self, i, r):
        c = self.rounds[r]['champs'][i]
        return (c['x'], c['y'])

    def analyse(self, team, upto=60):
        """per champion per round activity labels + list of key events"""
        M = self.map
        mine = self.champs[team]; enemy = self.champs[1-team]
        act = {i: {} for i in mine}       # i -> r -> set of labels
        hits_camp = {i: {} for i in mine}  # i -> r -> group
        keys = []                            # (r, kind, dict)
        camp_first_hit = {}                  # group -> (r, i, pos)
        camp_hitters = collections.defaultdict(set)
        camp_hit_rounds = collections.defaultdict(set)
        camp_hit_positions = collections.defaultdict(list)   # group -> [(r,i,pos)]
        recall_start = {}
        for r in sorted(self.events):
            if r > upto + 10: break
            for e in self.events[r]:
                if e['ak'] == 1 and e['a'] in mine:
                    i = e['a']; k = e['k']
                    A = act[i].setdefault(r, set())
                    for x in e['keff']:
                        if x.get('hp', 0) < 0:
                            g = self.c2g[x['i']]
                            A.add('C%d' % g); hits_camp[i][r] = g
                            camp_hitters[g].add(i); camp_hit_rounds[g].add(r)
                            camp_hit_positions[g].append((r, i, tuple(e['apos'])))
                            if g not in camp_first_hit: camp_first_hit[g] = (r, i, tuple(e['apos']))
                    for x in e['eff']:
                        if x['i'] in enemy and x.get('hp', 0) < 0:
                            A.add('F'); keys.append((r, 'hit_enemy', dict(i=i, j=x['i'], dmg=-x['hp'], pos=tuple(e['apos']))))
                    if k == 11: A.add('Rs'); recall_start[i] = r; keys.append((r, 'recall_start', dict(i=i, pos=tuple(e['apos']), gems=self.rounds[r]['champs'][i]['gems'])))
                    if k == 12:
                        bag = self.rounds[r-1]['champs'][i]['gems'] if r-1 in self.rounds else None
                        alt = min(M.ainfo, key=lambda a: cheb(a['pos'], e['apos']))
                        A.add('Ts'); keys.append((r, 'tribute_start', dict(i=i, pos=tuple(e['apos']), bag=bag, altar=alt['pos'], altar_side=M.side_of(team, alt['side']))))
                    if k == 18:
                        A.add('Td'); keys.append((r, 'tribute_done', dict(i=i, pos=tuple(e['apos']), bag=-[x.get('gems', 0) for x in e['eff'] if x['i'] == i][0] if e['eff'] else None)))
                    if k == 13:
                        A.add('B'); keys.append((r, 'buy', dict(i=i, gold=[x.get('gold', 0) for x in e['eff'] if x['i'] == i])))
                    if k == 20: A.add('W'); keys.append((r, 'k20_ward?', dict(i=i, pos=tuple(e['apos']))))
                elif e['ak'] == 1 and e['a'] in enemy:
                    for x in e['eff']:
                        if x['i'] in mine and x.get('hp', 0) < 0:
                            act[x['i']].setdefault(r, set()).add('F'); keys.append((r, 'hit_by_enemy', dict(i=x['i'], j=e['a'], dmg=-x['hp'])))
                elif e['ak'] == 2:
                    for x in e['eff']:
                        if x['i'] in mine and x.get('hp', 0) < 0:
                            act[x['i']].setdefault(r, set()).add('c')
                elif e['ph'] == 7:
                    for x in e['eff']:
                        if x['i'] in mine and x.get('gems', 0) > 0 or (x['i'] in mine and x.get('gold', 0) > 0):
                            act[x['i']].setdefault(r, set()).add('cap')
                            keys.append((r, 'capture', dict(i=x['i'], gems=x.get('gems', 0), gold=x.get('gold', 0), pos=self.pos(x['i'], r) if r in self.rounds else None)))
        # recall arrivals / deaths from snapshots
        prev = None
        for r in self.order:
            if r > upto + 10: break
            if prev is not None:
                for i in mine:
                    c = self.rounds[r]['champs'][i]; p = self.rounds[prev]['champs'][i]
                    if p['alive'] and not c['alive']:
                        keys.append((r, 'death', dict(i=i, pos=(p['x'], p['y']), gems_lost=p['gems'])))
                    if p['alive'] and c['alive'] and cheb((p['x'], p['y']), (c['x'], c['y'])) > 2 and min(cheb((c['x'], c['y']), s) for s in M.spawn[team]) <= 1:
                        keys.append((r, 'recall_arrive', dict(i=i, frm=(p['x'], p['y']))))
                        act[i].setdefault(r, set()).add('Ra')
                    if not p['alive'] and c['alive']:
                        keys.append((r, 'respawn', dict(i=i)))
            prev = r
        # camp deaths (group alive -> all dead)
        camp_death = {}
        prev = None
        for r in self.order:
            if r > upto + 10: break
            if prev is not None:
                for g, tiles in self.gtiles.items():
                    alive_now = any(c['alive'] for c in self.rounds[r]['camps'].values() if c['g'] == g)
                    alive_prev = any(c['alive'] for c in self.rounds[prev]['camps'].values() if c['g'] == g)
                    if alive_prev and not alive_now and g not in camp_death: camp_death[g] = r
            prev = r
        keys.sort(key=lambda k: k[0])
        return dict(act=act, keys=keys, camp_first_hit=camp_first_hit, camp_hitters=camp_hitters, camp_hit_rounds=camp_hit_rounds,
                    camp_hit_positions=camp_hit_positions, camp_death=camp_death, mine=mine, enemy=enemy, team=team)

    def timeline(self, team, upto=60):
        """compact per-champion run-length timeline up to round upto"""
        an = self.analyse(team, upto)
        M = self.map
        out = {}
        for i in an['mine']:
            labels = []
            for r in range(1, upto+1):
                if r not in self.rounds: break
                c = self.rounds[r]['champs'][i]
                A = an['act'][i].get(r, set())
                if not c['alive']: lab = 'dead'
                elif any(a.startswith('C') for a in A): lab = 'camp' + sorted(a for a in A if a.startswith('C'))[0][1:]
                elif 'F' in A: lab = 'fight'
                elif 'Ts' in A or 'Td' in A: lab = 'tribute'
                elif 'cap' in A: lab = 'capture'
                else:
                    p = (c['x'], c['y'])
                    # standing on a group's spawn tiles after kill = capturing
                    on = [g for g, tiles in self.gtiles.items() if p in tiles]
                    if on and not any(cc['alive'] for cc in self.rounds[r]['camps'].values() if cc['g'] == on[0]): lab = 'capture'
                    else:
                        pp = self.pos(i, r-1) if r-1 in self.rounds else p
                        lab = 'idle' if pp == p else 'walk'
                        if lab == 'idle' and min(cheb(p, s) for s in M.spawn[team]) <= 0: lab = 'spawn'
                if 'Ts' in A: lab = 'tribute'
                if 'Rs' in A: lab = 'recall'
                labels.append((r, lab, (c['x'], c['y']), c['gems'], c['hp']))
            # recall in flight: from start to arrival
            rs = [k[0] for k in an['keys'] if k[1] == 'recall_start' and k[2]['i'] == i]
            ra = [k[0] for k in an['keys'] if k[1] == 'recall_arrive' and k[2]['i'] == i and k[0] > 1]
            for r0 in rs:
                r1 = min([x for x in ra if x > r0] or [r0+5])
                for j, (r, lab, p, gems, hp) in enumerate(labels):
                    if r0 <= r < r1 and lab in ('idle', 'walk', 'capture', 'recall', 'spawn'):
                        labels[j] = (r, 'cap+recall' if lab == 'capture' else 'recall', p, gems, hp)
            # run-length with tribute/recall extension
            runs = []
            for r, lab, p, gems, hp in labels:
                if lab in ('walk', 'idle') and runs and runs[-1][1] == 'recall' and r - runs[-1][2] <= 1 and r - runs[-1][0] < 6:
                    lab = 'recall'
                if lab in ('walk', 'idle') and runs and runs[-1][1] == 'tribute' and r - runs[-1][2] <= 1 and r - runs[-1][0] < 12 and p == runs[-1][4]:
                    lab = 'tribute'
                if runs and runs[-1][1] == lab and r - runs[-1][2] <= 1:
                    runs[-1][2] = r; runs[-1][4] = p; runs[-1][5] = gems
                else:
                    runs.append([r, lab, r, p, p, gems])
            out[i] = runs
        return out, an

def fmt_runs(g, i, runs, team):
    M = g.map
    parts = []
    for r0, lab, r1, p0, p1, gems in runs:
        if lab.startswith('camp'):
            gi = int(lab[4:]); info = g.ginfo[gi]
            parts.append('%s[g%d %s %s d%d] r%d-%d' % ('camp', gi, '+'.join(t[:4] for t in info['types']), M.side_of(team, info['side']), info['dA'] if team == 0 else info['dB'], r0, r1))
        elif lab == 'walk': parts.append('walk r%d-%d %s>%s' % (r0, r1, p0, p1))
        else: parts.append('%s r%d-%d%s' % (lab, r0, r1, ' @%s' % (p1,) if lab in ('tribute', 'fight', 'capture', 'idle') else ''))
    return '%s: ' % g.name(i) + ' | '.join(parts)

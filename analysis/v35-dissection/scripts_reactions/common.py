"""Loader for the ws2 compact replays + per-champion-round action/damage tables."""
import json, collections, os
S = '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
W = os.environ.get('WS', S + '/ws2')   # data dir: selected.json, steps/, mapsj/
ROWS = os.environ.get('ROWS', 'rows.json')  # rows file name under scripts_reactions
RP = S + '/ws2/scripts_reactions/' + ROWS
MELEE = {'Varg', 'Ryth', 'Issac', 'Vendetta', 'Marcella', 'Ren'}
CASTER = {'Stellar', 'Prism', 'Cassi', 'Tavi'}
def cls(ty):
    return 'melee' if ty in MELEE else ('caster' if ty in CASTER else 'ranged')
def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
def load_sel(): return json.load(open(W + '/selected.json'))
def tier(orank):
    if orank <= 10: return 'top10'
    if orank <= 20: return '11-20'
    if orank <= 30: return '21-30'
    return 'other'
MAPS = {}
def load_map(name):
    if name not in MAPS: MAPS[name] = json.load(open(W + '/mapsj/%s.json' % name))
    return MAPS[name]
def mirror(m, x, y):
    w, h = m['w'], m['h']; s = m['sym']
    if s == 'R180': return (w-1-x, h-1-y)
    if s in ('H', 'HORIZ', 'horizontal'): return (w-1-x, y)
    if s in ('V', 'VERT', 'vertical'): return (x, h-1-y)
    if s in ('D', 'DIAG', 'diag'): return (y, x)
    return (w-1-x, h-1-y)
def bfs(m, src):
    g = m['grid']; w, h = m['w'], m['h']; dist = {}; q = collections.deque()
    for s in src: dist[s] = 0; q.append(s)
    while q:
        x, y = q.popleft(); d = dist[(x, y)]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in dist and g[ny][nx] not in '#o':
                    dist[(nx, ny)] = d+1; q.append((nx, ny))
    return dist
def altars(m): return [(x, y) for y, row in enumerate(m['grid']) for x, c in enumerate(row) if c == 'A']
GEO = {}
def geo(mapname):
    if mapname in GEO: return GEO[mapname]
    m = load_map(mapname); sa = m['spawnA']
    sp0 = set((x, y) for x in range(sa[0], sa[2]+1) for y in range(sa[1], sa[3]+1))
    sp = {0: sp0, 1: set(mirror(m, x, y) for x, y in sp0)}
    dsp = {t: bfs(m, sp[t]) for t in (0, 1)}
    al = altars(m); dal = bfs(m, al) if al else {}
    GEO[mapname] = dict(m=m, sp=sp, dsp=dsp, dal=dal, altars=al)
    return GEO[mapname]

class Game:
    def __init__(self, rec):
        self.rec = rec; self.side = 0 if rec['side'] == 'a' else 1
        self.g = geo(rec['map'])
        rounds = {}; order = []; events = collections.defaultdict(list); types = {}; camps = {}
        for line in open(W + '/steps/%s.c.jsonl' % rec['match']):
            d = json.loads(line)
            if d['t'] == 'round':
                rounds[d['r']] = {c[0]: dict(i=c[0], team=c[1], ty=c[2], x=c[3], y=c[4], hp=c[5], mhp=c[6], gems=c[7], gold=c[8], alive=c[9]) for c in d['champs']}
                camps[d['r']] = {k[0]: dict(i=k[0], ty=k[1], x=k[2], y=k[3], hp=k[4], alive=k[5], awake=k[6], grp=k[7]) for k in d.get('camps', [])}
                order.append(d['r'])
                for c in d['champs']: types[c[0]] = (c[1], c[2])
            elif d['t'] == 'ev': events[d['r']].append(d)
        self.rounds, self.order, self.events, self.types, self.camps = rounds, order, events, types, camps
        self.idx = {r: k for k, r in enumerate(order)}
        self.build()
    def team(self, i): return self.types[i][0]
    def ty(self, i): return self.types[i][1]
    def build(self):
        """per round r, per champion i: act[r][i] = set of action tags; dmg[r][i] = list of (src_idx or 'camp', amount, kind)"""
        self.act = collections.defaultdict(lambda: collections.defaultdict(set))
        self.dmg = collections.defaultdict(lambda: collections.defaultdict(list))
        self.dealt = collections.defaultdict(lambda: collections.defaultdict(int))
        self.campdmg = collections.defaultdict(lambda: collections.defaultdict(list))  # r -> i -> [camp idx]
        self.recall_start = collections.defaultdict(list)   # i -> [rounds]
        self.recall_arrive = collections.defaultdict(list)
        self.tribute_start = collections.defaultdict(list)
        self.tribute_done = collections.defaultdict(list)
        self.death_round = collections.defaultdict(list)
        self.kill = {}  # (r,victim) -> killer idx or 'camp'
        self.pair_death = set(); self.killkind = {}
        for r in self.order:
            for e in self.events[r]:
                ak = e['ak']
                if ak == 1:
                    a = e['a']; k = e['k']; ph = e['ph']
                    if ph == 14 and k == 4:
                        for x in e['eff']:
                            if x['i'] == a and 'pos' in x and cheb(tuple(x['pos'][:2]), tuple(x['pos'][2:])) > 1:
                                self.recall_arrive[a].append(r); self.act[r][a].add('arrive')
                    elif ph == 14 and k == 18: self.tribute_done[a].append(r)
                    elif ph == 10:
                        if k == 4: self.act[r][a].add('move')
                        elif k == 11: self.recall_start[a].append(r); self.act[r][a].add('recall')
                        elif k == 12: self.tribute_start[a].append(r); self.act[r][a].add('tribute')
                        elif k == 6:
                            if any(x['i'] == a and 'pos' in x for x in e['eff']): self.act[r][a].add('dash')
                            elif any(x['i'] != a and x.get('hp', 0) < 0 and self.team(x['i']) != self.team(a) for x in e['eff']): self.act[r][a].add('spell')
                            elif any(kk.get('hp', 0) < 0 for kk in e['keff']): self.act[r][a].add('spellcamp')
                            else: self.act[r][a].add('abil')
                        elif k == 5:
                            if any(x['i'] != a and x.get('hp', 0) < 0 and self.team(x['i']) != self.team(a) for x in e['eff']): self.act[r][a].add('atk')
                            elif any(kk.get('hp', 0) < 0 for kk in e['keff']): self.act[r][a].add('atkcamp')
                            else: self.act[r][a].add('atkother')
                        elif k == 13: self.act[r][a].add('buy')
                    pairs = set()
                    dead = [x for x in e['eff'] if x.get('alive') == 0 and x['i'] != a]
                    if len(dead) >= 2 and e['apos']:
                        for tm in (0, 1):
                            dd = [x for x in dead if self.team(x['i']) == tm and self.ty(x['i']) in ('Cassi', 'Issac')]
                            if len(dd) == 2:
                                far = max(dd, key=lambda x: cheb(tuple(x['pos'][:2]), tuple(e['apos'])))
                                pairs.add(far['i']); self.pair_death.add((r, far['i']))
                    for x in e['eff']:
                        i = x['i']
                        if x.get('hp', 0) < 0 and i != a and i not in pairs and self.team(i) != self.team(a):
                            self.dmg[r][i].append((a, -x['hp'], 'spell' if k == 6 else 'atk'))
                            self.dealt[r][a] += -x['hp']
                        if x.get('alive') == 0:
                            self.death_round[i].append(r); self.kill[(r, i)] = 'pair' if i in pairs else (a if i != a else 'self'); self.killkind[(r, i)] = 'pair' if i in pairs else ('spell' if k == 6 else 'atk')
                elif ak == 2:
                    for x in e['eff']:
                        i = x['i']
                        if x.get('hp', 0) < 0:
                            self.dmg[r][i].append(('camp', -x['hp'], 'camp')); self.campdmg[r][i].append(e['a'])
                        if x.get('alive') == 0:
                            self.death_round[i].append(r); self.kill[(r, i)] = 'camp'; self.killkind[(r, i)] = 'camp'
                else:
                    for x in e['eff']:
                        if x.get('alive') == 0:
                            self.death_round[x['i']].append(r); self.kill.setdefault((r, x['i']), 'other')
    # helpers
    def pos(self, r, i):
        c = self.rounds[r][i]; return (c['x'], c['y'])
    def alive(self, r, i): return self.rounds[r][i]['alive'] == 1
    def hpp(self, r, i):
        c = self.rounds[r][i]; return 100.0 * c['hp'] / c['mhp']
    def foes(self, r, i):
        t = self.team(i)
        return [c for c in self.rounds[r].values() if c['team'] != t and c['alive']]
    def allies(self, r, i):
        t = self.team(i)
        return [c for c in self.rounds[r].values() if c['team'] == t and c['alive'] and c['i'] != i]
    def nearest_foe(self, r, i, p=None):
        p = p or self.pos(r, i)
        best = None
        for f in self.foes(r, i):
            d = cheb(p, (f['x'], f['y']))
            if best is None or d < best[0]: best = (d, f['i'])
        return best or (99, None)
    def nearest_ally_d(self, r, i, p=None):
        p = p or self.pos(r, i)
        return min((cheb(p, (f['x'], f['y'])) for f in self.allies(r, i)), default=99)
    def dspawn(self, i, p): return self.g['dsp'][self.team(i)].get(p, 99)
    def despawn(self, i, p): return self.g['dsp'][1-self.team(i)].get(p, 99)
    def daltar(self, p): return self.g['dal'].get(p, 99)
    def zone(self, i, p):
        a, b = self.dspawn(i, p), self.despawn(i, p)
        if a < b - 3: return 'own'
        if b < a - 3: return 'enemy'
        return 'middle'
    def champ_dmg(self, r, i):
        return [(s, v, k) for (s, v, k) in self.dmg[r][i] if s != 'camp']
    def recall_active(self, r, i):
        """a recall channel started in r-4..r that neither arrived nor was cancelled (approx: started within 5 rounds and no move/atk/hit since)"""
        for s in self.recall_start[i]:
            if s <= r < s + 5:
                ok = True
                for rr in range(s + 1, r + 1):
                    if self.act[rr][i] & {'move', 'atk', 'spell', 'dash', 'atkcamp'} or self.dmg[rr][i] or rr in self.recall_start[i]: ok = False; break
                if ok and not self.dmg[s][i]: return s
        return None
    def tribute_active(self, r, i):
        for s in self.tribute_start[i]:
            if s <= r and not any(s < d <= r for d in self.tribute_done[i]) and r - s <= 25:
                if not any(self.act[rr][i] & {'move', 'atk', 'spell', 'dash', 'atkcamp'} for rr in range(s + 1, r + 1)): return s
        return None
    def classify(self, r, i):
        """primary action class of champion i in round r (hit response classes)."""
        if r not in self.rounds or not self.alive(r, i): return 'dead'
        a = self.act[r][i]
        pr = r - 1
        moved = bool(a & {'move', 'dash'})
        fight = bool(a & {'atk', 'spell'})
        if moved and pr in self.rounds and self.alive(pr, i):
            p0 = self.pos(pr, i); p1 = self.pos(r, i)
            fs = self.foes(pr, i)
            if fs:
                d0 = min(cheb(p0, (f['x'], f['y'])) for f in fs); d1 = min(cheb(p1, (f['x'], f['y'])) for f in fs)
                mv = 'away' if d1 > d0 else ('closer' if d1 < d0 else 'lateral')
            else: mv = 'lateral'
        else: mv = None
        if fight: return 'fight' + ('+' + mv if mv else '')
        if mv: return mv
        if a & {'atkcamp', 'spellcamp'}: return 'camp'
        if 'recall' in a or self.recall_active(r, i) is not None: return 'recall'
        if 'tribute' in a or self.tribute_active(r, i) is not None: return 'tribute'
        if 'arrive' in a: return 'arrived'
        return 'nothing'

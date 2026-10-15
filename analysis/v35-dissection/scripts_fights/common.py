"""Shared loader for the compact replay format ($S/ws/steps/<match>.c.jsonl) + maps.
Usage: from common import *; g = load_game(rec)  (rec = entry of selected.json)
"""
import json, collections, os, functools
S = '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
MELEE = {'Varg', 'Ryth', 'Issac', 'Vendetta', 'Marcella', 'Ren'}
CASTER = {'Stellar', 'Prism', 'Cassi', 'Tavi'}          # ranged with damage spells (range 4)
RANGED = {'Vesper Vale', 'VesperVale', 'Vesper', 'Willow'}  # ranged, basic-attack oriented
def cls(ty):
    if ty in MELEE: return 'melee'
    if ty in CASTER: return 'caster'
    return 'ranged'
def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

def selected():
    return json.load(open(S + '/ws2/selected.json'))

@functools.lru_cache(None)
def load_map(name):
    m = json.load(open(S + '/ws2/mapsj/%s.json' % name))
    grid = m['grid']; w, h = m['w'], m['h']
    altars = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == 'A']
    m['altars'] = altars
    m['passable'] = lambda x, y: 0 <= x < w and 0 <= y < h and grid[y][x] != '#'
    return m

def bfs(m, srcs):
    """distance field (Chebyshev steps, walls block) from a set of source tiles"""
    w, h = m['w'], m['h']; grid = m['grid']
    INF = 10**6
    d = [[INF]*w for _ in range(h)]
    dq = collections.deque()
    for (x, y) in srcs:
        if 0 <= x < w and 0 <= y < h: d[y][x] = 0; dq.append((x, y))
    while dq:
        x, y = dq.popleft(); nd = d[y][x] + 1
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] != '#' and d[ny][nx] > nd:
                    d[ny][nx] = nd; dq.append((nx, ny))
    return d

class Game:
    pass

def load_game(rec):
    g = Game()
    g.rec = rec; g.match = rec['match']; g.map = rec['map']; g.m = load_map(rec['map'])
    g.us = 0 if rec['side'] == 'a' else 1      # team index of the analysed top team
    g.team = rec['team']
    g.rounds = {}; g.order = []; g.events = collections.defaultdict(list); g.types = {}
    g.camps = {}
    for line in open(S + '/ws2/steps/%s.c.jsonl' % rec['match']):
        d = json.loads(line)
        if d['t'] == 'round':
            g.rounds[d['r']] = {c[0]: dict(i=c[0], team=c[1], ty=c[2], x=c[3], y=c[4], hp=c[5], mhp=c[6], gems=c[7], gold=c[8], alive=c[9]) for c in d['champs']}
            g.camps[d['r']] = {c[0]: dict(i=c[0], ty=c[1], x=c[2], y=c[3], hp=c[4], alive=c[5], awake=c[6], grp=c[7]) for c in d['camps']}
            g.order.append(d['r'])
            for c in d['champs']: g.types[c[0]] = (c[1], c[2])
        elif d['t'] == 'ev':
            g.events[d['r']].append(d)
    g.ridx = {r: k for k, r in enumerate(g.order)}
    g.spawn = {0: set(), 1: set()}
    for i, c in g.rounds[g.order[0]].items(): g.spawn[c['team']].add((c['x'], c['y']))
    g.dspawn = {t: bfs(g.m, g.spawn[t]) for t in (0, 1)}
    g.daltar = bfs(g.m, g.m['altars'])
    # replay events: hits (champion on enemy champion), camp interactions, recalls, per-champion per-round actions
    live = {i: (c['x'], c['y']) for i, c in g.rounds[g.order[0]].items()}
    livehp = {i: c['hp'] for i, c in g.rounds[g.order[0]].items()}
    alive = {i: True for i in live}
    def ctx(a):
        t = g.types[a][0]
        return [(j, cheb(live[a], live[j]), livehp[j]) for j in live if g.types[j][0] != t and alive[j]]
    g.hits = []            # dict(r, seq, a, v, dmg, kind, apos, vpos, dist, kill)
    g.campatk = collections.defaultdict(set)   # champ -> rounds hitting a camp
    g.camphit = collections.defaultdict(set)   # champ -> rounds hit by a camp
    g.recall_start = collections.defaultdict(list)  # champ -> rounds
    g.recall_arrive = collections.defaultdict(list)
    g.tribute_start = collections.defaultdict(list); g.tribute_done = collections.defaultdict(list)
    g.casts = collections.defaultdict(list)   # champ -> rounds with any ability cast (k 6)
    g.livehp = {}
    g.acts = collections.defaultdict(lambda: collections.defaultdict(list))  # champ -> r -> ['move','atk','spell','dash','abil0',...]
    g.dealt = collections.defaultdict(lambda: collections.defaultdict(int))  # champ -> r -> dmg to enemy champs
    g.taken = collections.defaultdict(lambda: collections.defaultdict(int))  # champ -> r -> dmg from enemy champs
    seq = 0
    for r in g.order:
        for e in g.events[r]:
            seq += 1
            a = e['a'] if e['ak'] == 1 else None
            if a is not None:
                k = e['k']
                if k == 11: g.recall_start[a].append(r)
                if k == 12: g.tribute_start[a].append(r)
                if k == 18: g.tribute_done[a].append(r)
                if k == 6: g.casts[a].append(r)
                if k == 4 and e['ph'] == 14:
                    for x in e['eff']:
                        if x['i'] == a and 'pos' in x and cheb(x['pos'][:2], x['pos'][2:]) > 2: g.recall_arrive[a].append(r)
                if k == 4 and e['ph'] == 10: g.acts[a][r].append('move')
                elif k == 5:
                    hit = [x for x in e['eff'] if x['i'] != a and x.get('hp', 0) < 0 and g.types[x['i']][0] != g.types[a][0]]
                    if hit: g.acts[a][r].append('atk')
                    elif any(x.get('hp', 0) < 0 for x in e['keff']): g.acts[a][r].append('atkcamp'); g.campatk[a].add(r)
                    for x in hit:
                        g.hits.append(dict(r=r, seq=seq, a=a, v=x['i'], dmg=-x['hp'], kind='atk', apos=live[a], vpos=live[x['i']], dist=cheb(live[a], live[x['i']]), kill=x.get('alive') == 0, ctx=ctx(a)))
                        g.dealt[a][r] += -x['hp']; g.taken[x['i']][r] += -x['hp']
                elif k == 6:
                    moved = [x for x in e['eff'] if x['i'] == a and 'pos' in x]
                    hit = [x for x in e['eff'] if x['i'] != a and x.get('hp', 0) < 0 and g.types[x['i']][0] != g.types[a][0]]
                    if moved: g.acts[a][r].append('dash')
                    elif hit: g.acts[a][r].append('spell')
                    elif any(x.get('hp', 0) < 0 for x in e['keff']): g.acts[a][r].append('spellcamp'); g.campatk[a].add(r)
                    else: g.acts[a][r].append('abil0')
                    for x in hit:
                        g.hits.append(dict(r=r, seq=seq, a=a, v=x['i'], dmg=-x['hp'], kind='spell', apos=live[a], vpos=live[x['i']], dist=cheb(live[a], live[x['i']]), kill=x.get('alive') == 0, ctx=ctx(a)))
                        g.dealt[a][r] += -x['hp']; g.taken[x['i']][r] += -x['hp']
            elif e['ak'] == 2:
                for x in e['eff']:
                    if x.get('hp', 0) < 0: g.camphit[x['i']].add(r)
            for x in e['eff']:
                if 'pos' in x: live[x['i']] = (x['pos'][2], x['pos'][3])
                if 'hpnow' in x: livehp[x['i']] = x['hpnow']
                if 'alive' in x: alive[x['i']] = bool(x['alive'])
        # resync with snapshot
        for i, c in g.rounds[r].items():
            live[i] = (c['x'], c['y']); livehp[i] = c['hp']; alive[i] = bool(c['alive'])
    # deaths: (r, i, killer or None)
    g.deaths = []
    lasthit = {}
    for h in g.hits: lasthit[(h['v'], h['r'])] = h['a']
    for k, r in enumerate(g.order[1:], 1):
        pr = g.order[k-1]
        for i, c in g.rounds[r].items():
            p = g.rounds[pr].get(i)
            if p and p['alive'] and not c['alive']:
                killer = None
                for h in g.hits:
                    if h['v'] == i and h['kill'] and h['r'] == r: killer = h['a']
                g.deaths.append((r, i, killer))
    return g

def snap(g, r):
    """snapshot at end of round r (or the latest one before)"""
    if r in g.rounds: return g.rounds[r]
    k = max(0, min(len(g.order)-1, (g.ridx.get(r) or 0)))
    rr = max([x for x in g.order if x <= r], default=g.order[0])
    return g.rounds[rr]

def prev_round(g, r):
    k = g.ridx[r]
    return g.order[k-1] if k > 0 else r

def tile(g, x, y):
    if 0 <= x < g.m['w'] and 0 <= y < g.m['h']: return g.m['grid'][y][x]
    return '#'

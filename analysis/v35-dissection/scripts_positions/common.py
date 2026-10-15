"""Loader for a batch directory (default ws2 = study26/v35; WS=ws3 = study27). Data dir = $S/$WS with selected.json, steps/, mapsj/.
Select with env var WS (e.g. WS=ws3 python3 -I q1_territory.py) or by passing the directory name/path as DATA=... . from common import *; for rec,g in games(): ...
g.us = our team index; g.rounds[r][i] champion dicts; g.acts[i][r] = set of action tags for round r;
tags: move, atk (hit enemy champ), atkcamp, spell (hit enemy champ), spellcamp, dash, abil0 (no-effect ability), buy, recall (k11 start),
      recalling (rounds between start and arrival), trib (k12 start), tributing (channel rounds until k18), tribdone(k18), other
"""
import json, collections, os, functools
S = '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
WS = os.environ.get('DATA') or os.environ.get('WS') or 'ws2'
D = WS if WS.startswith('/') else S + '/' + WS
SEL = json.load(open(D + '/selected.json'))
MELEE = {'Varg', 'Ryth', 'Issac', 'Vendetta', 'Marcella', 'Ren'}
CASTER = {'Stellar', 'Prism', 'Cassi', 'Tavi'}
def cls(ty):
    if ty in MELEE: return 'melee'
    if ty in CASTER: return 'caster'
    return 'ranged'
def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
TERR_T = 3
def rbin(r): return min(r // 50, 9)
BINS = ['%d-%d' % (50*k, 50*k+49) for k in range(9)] + ['450+']
def mirror(mp, x, y):
    s = mp['sym']; w, h = mp['w'], mp['h']
    if s == 'H': return (w-1-x, y)
    if s == 'V': return (x, h-1-y)
    return (w-1-x, h-1-y)
def bfs(mp, srcs):
    w, h = mp['w'], mp['h']; g = mp['grid']; INF = 10**6
    d = [[INF]*w for _ in range(h)]; q = collections.deque()
    for (x, y) in srcs:
        if 0 <= x < w and 0 <= y < h and g[y][x] not in '#o': d[y][x] = 0; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h and g[ny][nx] not in '#o' and d[ny][nx] == INF:
                    d[ny][nx] = d[y][x]+1; q.append((nx, ny))
    return d
def near_d(mp, d, x, y):
    best = 10**6
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x+dx, y+dy
            if 0 <= nx < mp['w'] and 0 <= ny < mp['h']: best = min(best, d[ny][nx])
    return best
@functools.lru_cache(None)
def load_map(name):
    mp = json.load(open(D + '/mapsj/%s.json' % name))
    x0, y0, x1, y1 = mp['spawnA']
    sa = [(x, y) for x in range(x0, x1+1) for y in range(y0, y1+1)]
    sb = [mirror(mp, x, y) for x, y in sa]
    mp['sp'] = {0: sa, 1: sb}
    mp['d'] = {0: bfs(mp, sa), 1: bfs(mp, sb)}
    mp['altars'] = [(x, y) for y, row in enumerate(mp['grid']) for x, c in enumerate(row) if c == 'A']
    mp['dalt'] = bfs(mp, mp['altars'])
    return mp
def terr(mp, x, y, team):
    if x < 0: return None
    do = near_d(mp, mp['d'][team], x, y); de = near_d(mp, mp['d'][1-team], x, y)
    if abs(do-de) <= TERR_T: return 'mid'
    return 'own' if do < de else 'enemy'
def spawn_dist(mp, x, y, team): return near_d(mp, mp['d'][team], x, y)
def altar_dist(mp, x, y): return near_d(mp, mp['dalt'], x, y)
class Game: pass
def load_game(rec):
    g = Game(); g.rec = rec; g.match = rec['match']; g.map = rec['map']; g.mp = load_map(rec['map'])
    g.us = 0 if rec['side'] == 'a' else 1; g.them = 1-g.us
    g.rounds = {}; g.order = []; g.events = collections.defaultdict(list); g.types = {}; g.camps = {}; g.sub = {}
    for line in open(D + '/steps/%s.c.jsonl' % rec['match']):
        d = json.loads(line)
        if d['t'] == 'round':
            g.rounds[d['r']] = {c[0]: dict(i=c[0], team=c[1], ty=c[2], x=c[3], y=c[4], hp=c[5], mhp=c[6], gems=c[7], gold=c[8], alive=c[9]) for c in d['champs']}
            g.camps[d['r']] = {c[0]: dict(i=c[0], ty=c[1], x=c[2], y=c[3], hp=c[4], alive=c[5], awake=c[6], grp=c[7]) for c in d['camps']}
            g.sub[d['r']] = d['sub']; g.order.append(d['r'])
            for c in d['champs']: g.types[c[0]] = (c[1], c[2])
        elif d['t'] == 'ev': g.events[d['r']].append(d)
    g.ridx = {r: k for k, r in enumerate(g.order)}
    g.ids = {t: [i for i, (tt, ty) in g.types.items() if tt == t] for t in (0, 1)}
    # camp groups
    g.gtiles = collections.defaultdict(set); g.gterr = {}
    for k in g.camps[0].values(): g.gtiles[k['grp']].add((k['x'], k['y']))
    for gi, ts in g.gtiles.items():
        x, y = next(iter(ts)); g.gterr[gi] = {t: terr(g.mp, x, y, t) for t in (0, 1)}
    g.camptiles = {(k['x'], k['y']): k['grp'] for k in g.camps[0].values()}
    g.acts = collections.defaultdict(lambda: collections.defaultdict(set))
    g.hits = []; g.caps = []   # caps: (r, i, gems)
    g.dealt = collections.defaultdict(lambda: collections.defaultdict(int))
    g.taken = collections.defaultdict(lambda: collections.defaultdict(int))
    g.kinds = collections.Counter()
    live = {i: (c['x'], c['y']) for i, c in g.rounds[0].items()}
    trib_open = {}; recall_open = {}
    for r in g.order:
        for e in g.events[r]:
            if e['ak'] == 1:
                a = e['a']; k = e['k']; g.kinds[k] += 1
                if k == 3: pass
                elif k == 4:
                    if e['ph'] == 10: g.acts[a][r].add('move')
                    else:
                        for x in e['eff']:
                            if x['i'] == a and 'pos' in x and cheb(x['pos'][:2], x['pos'][2:]) > 2:
                                g.acts[a][r].add('arrive')
                                if a in recall_open: del recall_open[a]
                elif k == 5:
                    hit = [x for x in e['eff'] if x['i'] != a and x.get('hp', 0) < 0 and g.types[x['i']][0] != g.types[a][0]]
                    if hit: g.acts[a][r].add('atk')
                    elif any(x.get('hp', 0) < 0 for x in e['keff']): g.acts[a][r].add('atkcamp')
                    else: g.acts[a][r].add('atk0')
                    for x in hit:
                        g.hits.append(dict(r=r, a=a, v=x['i'], dmg=-x['hp'], kind='atk', dist=cheb(live[a], live[x['i']]), kill=x.get('alive') == 0))
                        g.dealt[a][r] += -x['hp']; g.taken[x['i']][r] += -x['hp']
                elif k == 6:
                    moved = [x for x in e['eff'] if x['i'] == a and 'pos' in x]
                    hit = [x for x in e['eff'] if x['i'] != a and x.get('hp', 0) < 0 and g.types[x['i']][0] != g.types[a][0]]
                    if moved: g.acts[a][r].add('dash')
                    elif hit: g.acts[a][r].add('spell')
                    elif any(x.get('hp', 0) < 0 for x in e['keff']): g.acts[a][r].add('spellcamp')
                    else: g.acts[a][r].add('abil0')
                    for x in hit:
                        g.hits.append(dict(r=r, a=a, v=x['i'], dmg=-x['hp'], kind='spell', dist=cheb(live[a], live[x['i']]), kill=x.get('alive') == 0))
                        g.dealt[a][r] += -x['hp']; g.taken[x['i']][r] += -x['hp']
                elif k == 13: g.acts[a][r].add('buy')
                elif k == 11: g.acts[a][r].add('recall'); recall_open[a] = r
                elif k == 12: g.acts[a][r].add('trib'); trib_open[a] = r
                elif k == 18:
                    g.acts[a][r].add('tribdone')
                    if a in trib_open: del trib_open[a]
                else: g.acts[a][r].add('other')
            elif e['ak'] == 0 and e['ph'] == 7:
                for x in e['eff']:
                    if x.get('gems', 0) > 0: g.caps.append((r, x['i'], x['gems']))
            for x in e['eff']:
                if 'pos' in x: live[x['i']] = (x['pos'][2], x['pos'][3])
                if x.get('alive') == 0 and x['i'] in trib_open: del trib_open[x['i']]
                if x.get('alive') == 0 and x['i'] in recall_open: del recall_open[x['i']]
        for a, r0 in list(trib_open.items()):
            if r > r0: g.acts[a][r].add('tributing')
            if r - r0 > 40: del trib_open[a]
        for a, r0 in list(recall_open.items()):
            if r > r0: g.acts[a][r].add('recalling')
            if r - r0 > 8: del recall_open[a]
    # deaths
    g.deaths = []
    for k, r in enumerate(g.order[1:], 1):
        pr = g.order[k-1]
        for i, c in g.rounds[r].items():
            p = g.rounds[pr].get(i)
            if p and p['alive'] and not c['alive']: g.deaths.append((r, i))
    return g
def games(only=None):
    for rec in SEL:
        if only and rec['match'] not in only: continue
        if not os.path.exists(D + '/steps/%s.c.jsonl' % rec['match']): continue
        yield rec, load_game(rec)
def primary(acts):
    """one label per champion-round"""
    for tag, lab in (('tribdone', 'tribute'), ('trib', 'tribute'), ('tributing', 'tribute'), ('recall', 'recall'), ('recalling', 'recall'),
                     ('spell', 'cast@champ'), ('atk', 'attack champ'), ('dash', 'dash'), ('spellcamp', 'cast@camp'), ('atkcamp', 'attack camp'),
                     ('abil0', 'ability(no eff)'), ('atk0', 'attack(miss)'), ('move', 'move'), ('buy', 'buy'), ('arrive', 'arrive')):
        if tag in acts: return lab
    return 'nothing'
def split_keys(rec):
    return ['ALL', 'map:'+rec['map'], 'res:'+rec['res'], 'opp:'+('top10' if rec['orank'] <= 10 else 'r11-30')]

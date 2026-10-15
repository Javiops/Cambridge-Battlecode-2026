import sys, json, collections
# usage: python3 -I draft.py $S  -> draft tables per team/map + map features
S = sys.argv[1]
sel = json.load(open(f'{S}/ws/selected.json'))
CH = ['Ryth','Vesper','Vendetta','Cassi&Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi']
MAPS = 'collision corners elkring expanse interlock lanes monolith packs rows'.split()

def bfs(mp, src, dsts):
    w, h, g = mp['w'], mp['h'], mp['grid']
    dist = {src: 0}; q = collections.deque([src])
    while q:
        x, y = q.popleft()
        if (x, y) in dsts: return dist[(x, y)]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in dist and g[ny][nx] not in '#o':
                    dist[(nx, ny)] = dist[(x, y)] + 1; q.append((nx, ny))
    return None

feat = {}
for m in MAPS:
    mp = json.load(open(f'{S}/ws/mapsj/{m}.json'))
    w, h = mp['w'], mp['h']; x0, y0, x1, y1 = mp['spawnA']
    s = mp['sym']
    def mir(p):
        x, y = p
        if s == 'V': return (x, h - 1 - y)
        if s == 'H': return (w - 1 - x, y)
        return (w - 1 - x, h - 1 - y)
    a = ((x0 + x1) // 2, (y0 + y1) // 2); b = mir(a)
    spB = set(mir((x, y)) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))
    d = bfs(mp, a, spB)
    altars = [(x, y) for y in range(h) for x in range(w) if mp['grid'][y][x] == 'A']
    dalt = min(bfs(mp, a, {al}) or 999 for al in altars) if altars else None
    gems = sum(g['gems'] for g in mp['groups']); gold = sum(g['gold'] for g in mp['groups'])
    walk = sum(1 for y in range(h) for x in range(w) if mp['grid'][y][x] not in '#o')
    feat[m] = dict(nch=mp['nch'], size=f'{w}x{h}', walk=walk, spawn_path=d, altars=len(altars), nearest_altar=dalt, groups=len(mp['groups']), camps=len(mp['camps']), gems=gems, gold=gold, gems_per_ch=round(gems / mp['nch']))
    print(m, feat[m])
json.dump(feat, open(f'{S}/reports/scripts_draft/mapfeat.json', 'w'))

# draft per team per map
print()
for team in ('mite', 'uni'):
    print('==', team)
    for m in MAPS:
        rows = [r for r in sel if r['team'] == team and r['map'] == m]
        drafts = collections.Counter(tuple(r['draft']) for r in rows)
        wins = sum(r['res'] == 'win' for r in rows)
        print(f"{m:10s} nch={feat[m]['nch']} path={feat[m]['spawn_path']:3d} {wins}-{len(rows)-wins} ", ' | '.join(f"{'>'.join(CH[i] for i in d)} x{n}" for d, n in drafts.items()), ' side:', ''.join(r['side'] for r in rows))
        for r in rows:
            print(f"     {r['match'][:8]} side={r['side']} opp={r['opp'][:22]:22s} rank={r['orank']:3d} {r['res']:4s} {r['score']:4d}-{r['oscore']:4d} r{r['rounds']} draft={'>'.join(CH[i] for i in r['draft'])}")
# head-to-head (both teams in one match)
print()
both = collections.defaultdict(list)
for r in sel: both[r['match']].append(r)
for m, rs in both.items():
    if len(rs) == 2:
        print('H2H', m[:8], rs[0]['map'], {r['team']: ('>'.join(CH[i] for i in r['draft']), r['side'], r['res'], r['score']) for r in rs})
# first pick frequencies
print()
for team in ('mite', 'uni'):
    fp = collections.Counter(CH[r['draft'][0]] for r in sel if r['team'] == team)
    use = collections.Counter(CH[i] for r in sel if r['team'] == team for i in r['draft'])
    print(team, 'first pick:', fp.most_common(), '\n   usage:', use.most_common())

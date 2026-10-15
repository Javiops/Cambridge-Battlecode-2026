# Extract Mite's (#1) per-map macro script from decoded replays (top-2 dissection format, see DATA.md).
# Per champion: ordered steps
#   C <first-hit round> <capture round> <camp x> <camp y> <caprecall 0/1> <took the reward 0/1>   attack/capture a camp group
#   R <round> <x> <y>                                                     recall start (not on a capture)
#   T <round> <altar x> <altar y>                                         tribute start
#   D <round>                                                             died (informational)
# Usage: extract.py SELECTED.json STEPS_DIR MAPSJ_DIR OUT.json
import json, sys, collections
sel = json.load(open(sys.argv[1])); STEPS = sys.argv[2]; MAPSJ = sys.argv[3]
NAMES = {0: 'ryth', 1: 'vesper', 2: 'vendetta', 3: 'cassi', 4: 'stellar', 5: 'prism', 6: 'marcella', 7: 'willow', 8: 'ren', 9: 'varg', 10: 'tavi'}

ITEMS = [l.strip() for l in open(__file__.replace('extract.py', 'items.txt'))]
ORDER = ['jungle', 'durability', 'bruiser', 'monster', 'treasure', 'home', 'power']

def shop_plan(champ):
    # Mite's shards by family and stat -> our shop plan "family:stat:emblems,...", power last with want 99
    shards = collections.Counter()
    for i, n in enumerate(champ.get('itemsBought', [])):
        if n and 'shard' in ITEMS[i]:
            fam, stat = ITEMS[i].split('_shard_of_')
            shards[(fam, stat[0])] += n
    plan = []
    for fam in ORDER:
        for (f, st), n in sorted(shards.items(), key=lambda kv: -kv[1]):
            if f != fam: continue
            want = max(1, round(n / 5))
            plan.append([fam[:5] if fam == 'durability' else fam, st, want])
    if plan:  # then keep buying power in the main stat (the game may last longer than Mite's)
        main = max(((st, n) for (f, st), n in shards.items() if st != 'h'), key=lambda t: t[1], default=('s', 0))[0]
        k = next((i for i, p in enumerate(plan) if p[0] == 'power' and p[1] == main), None)
        if k is not None: plan.append(plan.pop(k))
        else: plan.append(['power', main, 99])
        plan[-1][2] = 99
    return ','.join(f'{f}:{st}:{w}' for f, st, w in plan)

SUMMARY = {}
def load(match):
    R = {}; ev = collections.defaultdict(list)
    for line in open(f'{STEPS}/{match}.c.jsonl'):
        d = json.loads(line)
        if d['t'] == 'round': R[d['r']] = d
        elif d['t'] == 'ev': ev[d['r']].append(d)
        elif d['t'] == 'summary': SUMMARY[match] = d['stats']
    return R, ev

def script(g):
    m = json.load(open(f"{MAPSJ}/{g['map']}.json"))
    t = 0 if g['side'] == 'a' else 1
    R, ev = load(g['match'])
    r0 = R[0]
    camps = {c[0]: c for c in r0['camps']}            # index -> [i,type,x,y,hp,alive,awake,group]
    gtiles = collections.defaultdict(set)
    for c in r0['camps']: gtiles[c[7]].add((c[2], c[3]))
    gfirst = {gi: min(ts) for gi, ts in gtiles.items()}
    altars = [(x, y) for y, row in enumerate(m['grid']) for x, ch in enumerate(row) if ch == 'A']
    own = {c[0]: c[2] for c in r0['champs'] if c[1] == t}
    steps = {i: [] for i in own}
    open_c = {i: None for i in own}   # index into steps of the open capture step
    pos = {c[0]: (c[3], c[4]) for c in r0['champs']}
    alive = {c[0]: 1 for c in r0['champs']}
    deaths = 0
    rounds = sorted(R)
    dead_since = {}
    for r in rounds:
        if r == 0: continue
        for e in ev.get(r, []):
            a = e.get('a')
            if e['ak'] == 1 and a in own:
                if e['k'] in (5, 6):
                    hit = [k for k in e.get('keff', []) if k.get('hp', 0) < 0]
                    if hit:
                        gi = camps[hit[0]['i']][7]
                        oc = open_c[a]
                        if oc is None or steps[a][oc][3] != gi:
                            steps[a].append(['C', r, -1, gi, 0, 0]); open_c[a] = len(steps[a]) - 1
                elif e['k'] == 11:
                    steps[a].append(['R', r, e['apos'][0], e['apos'][1]])
                elif e['k'] == 12:
                    ax, ay = e['apos']; al = min(altars, key=lambda p: max(abs(p[0] - ax), abs(p[1] - ay)))
                    steps[a].append(['T', r, al[0], al[1]])
            if e['ak'] == 0 and e['ph'] == 7:
                for x in e.get('eff', []):
                    i = x['i']
                    if i in own and (x.get('gems', 0) > 0 or x.get('gold', 0) > 0):
                        p = pos.get(i)
                        gi = next((gg for gg, ts in gtiles.items() if p in ts), None)
                        if gi is None: continue
                        # the capturer: close its matching open step, or add one (stood on it without hitting)
                        k = next((k for k in range(len(steps[i]) - 1, -1, -1) if steps[i][k][0] == 'C' and steps[i][k][3] == gi and steps[i][k][2] in (-1, r)), None)
                        if k is None: steps[i].append(['C', r, r, gi, 0, 0]); k = len(steps[i]) - 1
                        steps[i][k][2] = r; steps[i][k][5] = 1
                        # a recall started on the group's tiles before the reward = capture-recall
                        for j in range(k + 1, len(steps[i])):
                            if steps[i][j][0] == 'R' and (steps[i][j][2], steps[i][j][3]) in gtiles[gi]:
                                steps[i][k][4] = 1; steps[i][j][0] = 'x'
                        if open_c[i] == k: open_c[i] = None
                        # teammates that attacked this group: their step ends with the capture
                        for o in own:
                            oc = open_c[o]
                            if oc is not None and steps[o][oc][3] == gi:
                                steps[o][oc][2] = r; open_c[o] = None
            for x in e.get('eff', []):
                if 'pos' in x: pos[x['i']] = (x['pos'][2], x['pos'][3])
                if x.get('alive') == 0 and x['i'] in own and alive[x['i']]:
                    alive[x['i']] = 0; steps[x['i']].append(['D', r]); open_c[x['i']] = None; deaths += 1
                if x.get('alive') == 1: alive[x['i']] = 1
        for c in R[r]['champs']:
            if c[3] >= 0: pos[c[0]] = (c[3], c[4])
            alive[c[0]] = c[9]
        # attacked groups whose camps are all dead and no reward came within 10 rounds (enemy took it): close
        for i in own:
            oc = open_c[i]
            if oc is None: continue
            gi = steps[i][oc][3]
            live = [c for c in R[r]['camps'] if c[7] == gi and c[5]]
            if live: dead_since.pop((i, gi), None)
            else:
                d0 = dead_since.setdefault((i, gi), r)
                if r - d0 >= 10: steps[i][oc][2] = d0; open_c[i] = None
    out = {}
    for i, name in own.items():
        ss = []
        for s in steps[i]:
            if s[0] == 'x': continue
            if s[0] == 'C':
                if s[2] < 0: s[2] = s[1]   # never captured (interrupted): keep as a visit
                x, y = gfirst[s[3]]
                ss.append(['C', s[1], s[2], x, y, s[4], s[5]])
            else: ss.append(s)
        out[name.lower()] = ss
    shops = {c['typeName'].lower(): shop_plan(c) for c in SUMMARY[g['match']]['champions'] if c['team'] == t}
    return out, deaths, shops

res = collections.defaultdict(dict)
for g in sel:
    if g['team'] != 'mite': continue
    sc, deaths, shops = script(g)
    key = g['map']; side = g['side']
    cand = dict(match=g['match'], opp=g['opp'], res=g['res'], rounds=g['rounds'], deaths=deaths, draft=[NAMES[d] for d in g['draft']], champs=sc, shops=shops)
    best = res[key].get(side)
    if best is None or (deaths, -g['rounds']) < (best['deaths'], -best['rounds']): res[key][side] = cand
    print(g['map'], side, g['opp'][:12], g['res'], g['rounds'], 'deaths', deaths, 'steps', {k: len(v) for k, v in sc.items()})
json.dump(res, open(sys.argv[4], 'w'), indent=0)
for k in sorted(res):
    for side, c in sorted(res[k].items()): print('BEST', k, side, c['opp'][:12], c['res'], c['rounds'], 'deaths', c['deaths'])

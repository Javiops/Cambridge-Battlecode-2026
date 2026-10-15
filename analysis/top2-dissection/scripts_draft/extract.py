import sys, json, collections, os
# usage: python3 -I extract.py $S  -> writes $S/reports/scripts_draft/shop.json with per-game, per-champion purchase sequences + summary stats
S = sys.argv[1]
sel = json.load(open(f'{S}/ws/selected.json'))
ITEMS = [l.strip() for l in open('/mnt/project-files/analysis/data/items.txt') if l.strip()]
CH = ['ryth','vesper_vale','vendetta','cassi_and_issac','stellar','prism','marcella','willow','ren','varg','tavi']

def load(match):
    rounds = {}; order = []; events = collections.defaultdict(list); summary = None
    for line in open(f'{S}/ws/steps/{match}.c.jsonl'):
        d = json.loads(line)
        if d['t'] == 'round':
            rounds[d['r']] = d; order.append(d['r'])
        elif d['t'] == 'ev': events[d['r']].append(d)
        elif d['t'] == 'summary': summary = d
    return rounds, order, events, summary

def spawn_tiles(mp, side):
    x0, y0, x1, y1 = mp['spawnA']; w, h = mp['w'], mp['h']
    tiles = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    if side == 0: return set(tiles)
    s = mp['sym']
    def mir(p):
        x, y = p
        if s == 'V': return (x, h - 1 - y)
        if s == 'H': return (w - 1 - x, y)
        return (w - 1 - x, h - 1 - y)
    return set(mir(p) for p in tiles)

maps = {m: json.load(open(f'{S}/ws/mapsj/{m}.json')) for m in 'collision corners elkring expanse interlock lanes monolith packs rows'.split()}
out = []
for rec in sel:
    m = rec['match']; tm = 0 if rec['side'] == 'a' else 1
    rounds, order, events, summary = load(m)
    mp = maps[rec['map']]
    sp = spawn_tiles(mp, tm)
    r0 = rounds[order[0]]
    champs = {c[0]: c[2] for c in r0['champs'] if c[1] == tm}
    # live state
    gold = {c[0]: c[8] for c in r0['champs']}
    pos = {c[0]: (c[3], c[4]) for c in r0['champs']}
    hp = {c[0]: c[5] for c in r0['champs']}; mhp = {c[0]: c[6] for c in r0['champs']}
    alive = {c[0]: c[9] for c in r0['champs']}
    per = {i: dict(ty=champs[i], buys=[], recalls=[], deaths=[], respawns=[], earned=0, spawn_rounds=0) for i in champs}
    last_r = order[-1]
    for r in order:
        for e in events[r]:
            for x in e['eff']:
                i = x['i']
                if 'pos' in x:
                    nx, ny = x['pos'][2], x['pos'][3]
                    if i in champs and alive.get(i) and x.get('alive') is None and max(abs(nx - x['pos'][0]), abs(ny - x['pos'][1])) > 2 and (nx, ny) in sp and e['ph'] == 14:
                        per[i]['recalls'].append(dict(r=r, hp=hp[i], mhp=mhp[i], gold=gold[i]))
                    pos[i] = (nx, ny)
                if 'gold' in x:
                    if x['gold'] > 0 and i in champs: per[i]['earned'] += x['gold']
                    if e['k'] == 13 and e['ak'] == 1 and e['a'] == i and x['gold'] < 0 and i in champs:
                        per[i]['buys'].append(dict(r=r, gold=-x['gold'], maxhp=x.get('maxhp', 0), dead=int(not alive[i]), onspawn=int(pos[i] in sp), before=gold[i], after=gold[i] + x['gold'], hp=hp[i], mhp=mhp[i]))
                    gold[i] += x['gold']
                if 'hpnow' in x: hp[i] = x['hpnow']
                if 'maxhp' in x: mhp[i] += x['maxhp']
                if 'alive' in x:
                    alive[i] = x['alive']
                    if i in champs:
                        (per[i]['deaths'] if x['alive'] == 0 else per[i]['respawns']).append(r)
        snap = rounds[r]
        for c in snap['champs']:
            gold[c[0]] = c[8]; pos[c[0]] = (c[3], c[4]); hp[c[0]] = c[5]; mhp[c[0]] = c[6]; alive[c[0]] = c[9]
            if c[0] in champs and c[9] and (c[3], c[4]) in sp: per[c[0]]['spawn_rounds'] += 1
    # summary stats
    sm = {c['index']: c for c in summary['stats']['champions']} if summary else {}
    for i in champs:
        s = sm.get(i)
        if s:
            per[i]['items'] = {ITEMS[k]: v for k, v in enumerate(s['itemsBought']) if v}
            per[i]['consumables'] = s['consumablesBought']
            per[i]['earnedGold'] = s['earnedGold']; per[i]['spentGold'] = s['spentGold']; per[i]['goldEnd'] = s['gold']
            per[i]['kills'] = s['kills']; per[i]['deaths_n'] = s['deaths']
        per[i]['final_gold'] = gold[i]
    out.append(dict(match=m, team=rec['team'], side=rec['side'], map=rec['map'], opp=rec['opp'], res=rec['res'], score=rec['score'], oscore=rec['oscore'], rounds=rec['rounds'], draft=rec['draft'], draftPicks=summary['stats']['draftPicks'] if summary else None, champs=per, last_round=last_r))
json.dump(out, open(f'{S}/reports/scripts_draft/shop.json', 'w'))
print('games', len(out))

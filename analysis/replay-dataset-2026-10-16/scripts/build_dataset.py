"""Build a per-champion-turn decision dataset from decoded top-team replays.

usage: build_dataset.py STEPS_DIR SELECTED_JSON MAPS_DIR OUT_DIR

One row per (match, round, champion) where the champion is alive at the start of the round,
not mid-channel at round start, and at least one living enemy champion is within Chebyshev 8.
Features use the state at the start of the round (end-of-previous-round snapshot).
Labels come from the champion's own actions in that round; outcomes from the next rounds.
"""
import sys, os, json, glob, collections, csv
from multiprocessing import Pool

STEPS, SEL, MAPS, OUT = sys.argv[1:5]
MELEE = {'Issac', 'Ryth', 'Vendetta', 'Marcella', 'Ren', 'Varg'}
VIS = 8
K_MOVE, K_ATK, K_CAST, K_RECALL, K_TRIB, K_BUY = 4, 5, 6, 11, 12, 13


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def mirror(m, x, y):
    w, h, s = m['w'], m['h'], m['sym']
    if s == 'H':
        return (w - 1 - x, y)
    if s == 'V':
        return (x, h - 1 - y)
    return (w - 1 - x, h - 1 - y)


def bfs(m, src):
    g = m['grid']; w, h = m['w'], m['h']
    dist = [[-1] * w for _ in range(h)]
    q = collections.deque()
    for x, y in src:
        dist[y][x] = 0; q.append((x, y))
    while q:
        x, y = q.popleft(); d = dist[y][x]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and dist[ny][nx] < 0 and g[ny][nx] not in '#o':
                    dist[ny][nx] = d + 1; q.append((nx, ny))
    return dist


MAPCACHE = {}


def mapinfo(name):
    if name in MAPCACHE:
        return MAPCACHE[name]
    m = json.load(open(os.path.join(MAPS, name + '.json')))
    x0, y0, x1, y1 = m['spawnA']
    spA = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    spB = [mirror(m, x, y) for x, y in spA]
    alt = [(x, y) for y, row in enumerate(m['grid']) for x, c in enumerate(row) if c == 'A']
    info = dict(m=m, sp=[set(spA), set(spB)], dsp=[bfs(m, spA), bfs(m, spB)], dalt=bfs(m, alt))
    MAPCACHE[name] = info
    return info


def load(path):
    snaps = {}; evs = collections.defaultdict(list)
    for line in open(path):
        d = json.loads(line)
        if d['t'] == 'round':
            snaps[d['r']] = d
        elif d['t'] == 'ev':
            evs[d['r']].append(d)
    return snaps, evs


def process(args):
    match, recs = args
    path = os.path.join(STEPS, match + '.c.jsonl')
    if not os.path.exists(path):
        return [], [], {}
    side_tag = {}
    for r in recs:
        side_tag[0 if r['side'] == 'a' else 1] = r['team']
    mp = recs[0]['map']
    info = mapinfo(mp)
    snaps, evs = load(path)
    R = max(snaps)
    rounds = sorted(snaps)
    ch = {r: {c[0]: c for c in snaps[r]['champs']} for r in rounds}
    idxs = sorted(ch[0])
    team = {i: ch[0][i][1] for i in idxs}
    typ = {i: ch[0][i][2] for i in idxs}

    def total(r, t):
        s = snaps[r]['sub'][t]
        return s + sum(c[7] for c in snaps[r]['champs'] if c[1] == t and c[9])

    tot = {r: (total(r, 0), total(r, 1)) for r in rounds}

    # per round per champion: damage dealt to champions, damage taken from anything, actions
    dealt = collections.defaultdict(int); taken = collections.defaultdict(int)
    taken_ch = collections.defaultdict(int)
    acts = collections.defaultdict(list)       # (r, i) -> list of events (ph 10)
    casts = collections.defaultdict(list)      # i -> rounds with a cast
    recall_start = {}                          # (r,i)
    for r in rounds:
        for e in evs.get(r, []):
            a = e['a'] if e['ak'] == 1 else None
            for f in e['eff']:
                if f.get('hp', 0) < 0:
                    taken[(r, f['i'])] += -f['hp']
                    if a is not None and team.get(a) != team.get(f['i']):
                        dealt[(r, a)] += -f['hp']
                        taken_ch[(r, f['i'])] += -f['hp']
            if e['ak'] == 1 and e['ph'] == 10:
                acts[(r, a)].append(e)
                if e['k'] == K_CAST:
                    casts[a].append(r)

    # channel tracking: recall start k11 -> channel until jump to own spawn or 7 rounds or damage
    chan_until = collections.defaultdict(int)  # (i) -> list of (start, end)
    in_chan = set()
    rec_ok = 0; rec_n = 0
    for (r, i), lst in acts.items():
        for e in lst:
            if e['k'] in (K_RECALL, K_TRIB):
                if e['k'] == K_RECALL and tuple(e['apos']) in info['sp'][team[i]]:
                    continue  # recall on own spawn = no-op (some bots spam it)
                dur = 6 if e['k'] == K_RECALL else 1 + (ch.get(r - 1, {}).get(i, [0] * 10)[7] + 9) // 10
                end = r + dur
                if e['k'] == K_RECALL:
                    rec_n += 1
                    for rr in range(r + 1, min(r + 8, R) + 1):
                        c = ch.get(rr, {}).get(i)
                        if c and c[9] and (c[3], c[4]) in info['sp'][team[i]] and cheb((c[3], c[4]), e['apos']) > 2:
                            rec_ok += 1; end = rr; break
                        if taken.get((rr, i), 0) > 0:
                            end = rr; break
                for rr in range(r + 1, end):
                    in_chan.add((rr, i))

    rows = []; trows = []
    for r in rounds:
        if r == 0 or r - 1 not in ch:
            continue
        pre = ch[r - 1]; post = ch[r]
        alive = [i for i in idxs if pre[i][9]]
        for i in alive:
            if (r, i) in in_chan:
                continue
            ci = pre[i]; t = team[i]; pos = (ci[3], ci[4])
            ens = [j for j in alive if team[j] != t and cheb(pos, (pre[j][3], pre[j][4])) <= VIS]
            if not ens:
                continue
            als = [j for j in alive if team[j] == t and j != i and cheb(pos, (pre[j][3], pre[j][4])) <= VIS]
            def d(j):
                return cheb(pos, (pre[j][3], pre[j][4]))
            ne = min(ens, key=lambda j: (d(j), pre[j][5]))
            en_hp = sum(pre[j][5] for j in ens)
            al_hp = sum(pre[j][5] for j in als)
            rc = lambda j: sum(1 for x in casts[j] if r - 8 <= x < r)
            # labels
            lst = acts.get((r, i), [])
            ks = [e['k'] for e in lst]
            hit = collections.Counter()
            hit_camp = 0
            for e in lst:
                if e['k'] in (K_ATK, K_CAST):
                    for f in e['eff']:
                        if f.get('hp', 0) < 0 and team.get(f['i']) != t:
                            hit[f['i']] += -f['hp']
                    if any(f.get('hp', 0) < 0 for f in e['keff']):
                        hit_camp = 1
            c2 = post.get(i)
            npos = (c2[3], c2[4]) if c2 and c2[9] else pos
            if cheb(npos, pos) > 2:  # recall arrival/teleport: not a walking decision
                npos = pos
            npos_walk = pos
            for e in lst:
                if e['k'] == K_MOVE or (e['k'] == K_CAST and any(f['i'] == i and 'pos' in f for f in e['eff'])):
                    for f in e['eff']:
                        if f['i'] == i and 'pos' in f:
                            npos_walk = (f['pos'][2], f['pos'][3])
            if cheb(npos_walk, pos) > 2:  # teleport crystal etc.: not a walking step
                npos_walk = pos
            nep = (pre[ne][3], pre[ne][4])
            delta = cheb(npos_walk, nep) - cheb(pos, nep)
            # mean change over all visible enemies (smoother)
            dmean = sum(cheb(npos_walk, (pre[j][3], pre[j][4])) - d(j) for j in ens) / len(ens)
            if K_RECALL in ks and pos not in info['sp'][t]:
                act = 'recall'
            elif K_TRIB in ks:
                act = 'tribute'
            elif hit and delta > 0:
                act = 'kite'
            elif hit:
                act = 'hit'
            elif delta < 0:
                act = 'advance'
            elif delta > 0:
                act = 'retreat'
            else:
                act = 'hold'
            act3 = {'recall': 'retreat', 'retreat': 'retreat', 'kite': 'engage', 'hit': 'engage',
                    'advance': 'engage', 'hold': 'hold', 'tribute': 'hold'}[act]
            tgt = max(hit, key=hit.get) if hit else -1

            def died(n):
                for rr in range(r, min(r + n, R) + 1):
                    c = ch.get(rr, {}).get(i)
                    if c and not c[9]:
                        return 1
                return 0

            def endied(n):
                k = 0
                for j in ens:
                    for rr in range(r, min(r + n, R) + 1):
                        c = ch.get(rr, {}).get(j)
                        if c and not c[9]:
                            k += 1; break
                return k

            def sumw(dct, n):
                return sum(dct.get((rr, i), 0) for rr in range(r, min(r + n, R + 1)))

            r20 = min(r - 1 + 20, R)
            while r20 not in tot:
                r20 -= 1
            sw = (tot[r20][t] - tot[r - 1][t]) - (tot[r20][1 - t] - tot[r - 1][1 - t])
            row = dict(
                match=match, map=mp, round=r, champ=i, team=t, team_tag=side_tag.get(t, 'opp'),
                type=typ[i], melee=int(typ[i] in MELEE),
                hp=ci[5], maxhp=ci[6], hp_frac=round(ci[5] / ci[6], 4), gems=ci[7], gold=ci[8],
                d_altar=info['dalt'][pos[1]][pos[0]], d_spawn=info['dsp'][t][pos[1]][pos[0]],
                own_casts_last8=rc(i), dmg_taken_last1=taken.get((r - 1, i), 0),
                dmg_taken_last3=sum(taken.get((rr, i), 0) for rr in range(r - 3, r)),
                n_ally8=len(als), n_ally4=sum(1 for j in als if d(j) <= 4), ally_hp8=al_hp,
                ally_lowfrac8=round(min([pre[j][5] / pre[j][6] for j in als], default=1.0), 4),
                n_en8=len(ens), n_en4=sum(1 for j in ens if d(j) <= 4), n_en3=sum(1 for j in ens if d(j) <= 3),
                n_en1=sum(1 for j in ens if d(j) <= 1),
                en_hp8=en_hp, en_maxhp8=sum(pre[j][6] for j in ens),
                near_en_dist=d(ne), near_en_hpfrac=round(pre[ne][5] / pre[ne][6], 4), near_en_melee=int(typ[ne] in MELEE),
                min_en_hp=min(pre[j][5] for j in ens),
                min_en_hpfrac=round(min(pre[j][5] / pre[j][6] for j in ens), 4),
                en_gems8=sum(pre[j][7] for j in ens), en_casts_last8=sum(rc(j) for j in ens),
                en_ranged8=sum(1 for j in ens if typ[j] not in MELEE),
                hp_ratio8=round((ci[5] + al_hp) / max(1, en_hp), 4),
                en_dmg_last1=sum(taken_ch.get((r - 1, j), 0) for j in ens),
                # labels
                action=act, action3=act3, attacked_champ=int(bool(hit)), cast=int(K_CAST in ks),
                hit_camp=hit_camp, moved_delta=delta, moved_delta_mean=round(dmean, 3), target=tgt,
                # outcomes
                died5=died(5), died10=died(10), died20=died(20),
                dmg_taken5=sumw(taken, 5), dmg_taken10=sumw(taken, 10), dmg_dealt10=sumw(dealt, 10),
                en_died10=endied(10), gem_swing20=sw,
            )
            rows.append(row)
            if hit:
                cands = [j for j in ens if d(j) <= 4]
                if tgt not in cands:
                    cands.append(tgt)
                lowhp = min(pre[j][5] for j in cands)
                near = min(d(j) for j in cands)
                for j in cands:
                    trows.append(dict(
                        match=match, round=r, champ=i, team_tag=row['team_tag'], type=typ[i], cand=j,
                        cand_type=typ[j], chosen=int(j == tgt), n_cands=len(cands), dist=d(j), hp=pre[j][5],
                        hp_frac=round(pre[j][5] / pre[j][6], 4), gems=pre[j][7], melee=int(typ[j] in MELEE),
                        is_lowest_hp=int(pre[j][5] == lowhp), is_nearest=int(d(j) == near),
                        hit_by_team_last1=taken_ch.get((r - 1, j), 0),
                        cand_casts_last8=rc(j)))
    return rows, trows, {'recall_events': rec_n, 'recall_with_jump': rec_ok}


def main():
    sel = json.load(open(SEL))
    by = collections.defaultdict(list)
    for s in sel:
        by[s['match']].append(s)
    os.makedirs(OUT, exist_ok=True)
    with Pool(8) as p:
        res = p.map(process, sorted(by.items()))
    rows = [x for r in res for x in r[0]]
    trows = [x for r in res for x in r[1]]
    st = collections.Counter()
    for r in res:
        st.update(r[2])
    for name, data in (('turns.csv', rows), ('targets.csv', trows)):
        with open(os.path.join(OUT, name), 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader(); w.writerows(data)
    print(len(rows), 'turn rows,', len(trows), 'target rows', dict(st))


main()

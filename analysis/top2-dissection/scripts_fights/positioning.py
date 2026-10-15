"""Round-by-round positioning inside fights: distance to nearest enemy by class, kiting, front body,
formation (pairwise ally distance), terrain, approach grouping, caster-holds-for-melee, contact-without-fight (avoid)."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_fights')
from common import *
F = json.load(open(S + '/reports/scripts_fights/fights.json'))
byg = collections.defaultdict(list)
for f in F: byg[(f['match'], f['team'])].append(f)
def med(x): return st.median(x) if x else None
def mean(x): return round(st.mean(x), 2) if x else None
def pct(a, b): return '%d%%' % round(100*a/b) if b else '-'

D = {t: collections.defaultdict(list) for t in ('mite', 'uni', 'opp')}   # (class/type) -> nearest enemy dist per fight round
ACT = {t: collections.defaultdict(collections.Counter) for t in ('mite', 'uni', 'opp')}  # class -> action counter in fight rounds with enemy <=8
KITE = {t: collections.defaultdict(collections.Counter) for t in ('mite', 'uni', 'opp')}  # type -> what happens the round after an attack/spell
FRONT = {t: collections.Counter() for t in ('mite', 'uni', 'opp')}
FORM = {t: collections.defaultdict(list) for t in ('mite', 'uni', 'opp')}
TILE = {t: collections.Counter() for t in ('mite', 'uni', 'opp')}
TILEBASE = {t: collections.Counter() for t in ('mite', 'uni', 'opp')}
APP = {t: collections.defaultdict(list) for t in ('mite', 'uni')}   # rounds-before-first-hit -> pairwise dist
HOLD = {t: [] for t in ('mite', 'uni')}
AVOID = {t: collections.Counter() for t in ('mite', 'uni')}
AVOIDX = {t: [] for t in ('mite', 'uni')}
CHASE = {t: [] for t in ('mite', 'uni')}
RECALL = {t: [] for t in ('mite', 'uni', 'opp')}
LEAVE = {t: [] for t in ('mite', 'uni', 'opp')}

def nearest(g, r, i, t, maxd=99):
    c = g.rounds[r][i]
    return min([cheb((e['x'], e['y']), (c['x'], c['y'])) for e in g.rounds[r].values() if e['team'] != t and e['alive']], default=maxd)

for rec in selected():
    g = load_game(rec); key = (g.match, g.team)
    fs = byg[key]
    us = g.us
    fight_rounds = set()
    for f in fs:
        for rr in g.order:
            if f['r0'] <= rr <= f['r1']: fight_rounds.add(rr)
    # baseline tiles
    for rr in g.order:
        for c in g.rounds[rr].values():
            if c['alive']:
                tk = g.team if c['team'] == us else 'opp'
                TILEBASE[tk][tile(g, c['x'], c['y'])] += 1
    for f in fs:
        parts = {t: f['sides'][str(t)]['ids'] for t in (0, 1)}
        win = [rr for rr in g.order if f['r0'] <= rr <= f['r1']]
        for rr in win:
            s = g.rounds[rr]
            for t in (0, 1):
                tk = g.team if t == us else 'opp'
                alive = [i for i in parts[t] if s[i]['alive']]
                nd = {}
                for i in alive:
                    d = nearest(g, rr, i, t)
                    if d > 8: continue
                    nd[i] = d
                    ty = g.types[i][1]; c = cls(ty)
                    D[tk][c].append(d); D[tk][ty].append(d)
                    acts = g.acts[i].get(rr, [])
                    a = 'spell' if 'spell' in acts else ('atk' if 'atk' in acts else ('dash' if 'dash' in acts else ('move' if 'move' in acts else 'idle')))
                    ACT[tk][c][a] += 1
                    TILE[tk][tile(g, s[i]['x'], s[i]['y'])] += 1
                    # kiting: after an attack / spell this round, what next round?
                    if a in ('atk', 'spell') and c != 'melee':
                        k = g.ridx[rr]
                        if k + 1 < len(g.order):
                            r2 = g.order[k+1]
                            if g.rounds[r2][i]['alive']:
                                d2 = nearest(g, r2, i, t)
                                acts2 = g.acts[i].get(r2, [])
                                a2 = 'spell' if 'spell' in acts2 else ('atk' if 'atk' in acts2 else ('dash' if 'dash' in acts2 else ('move' if 'move' in acts2 else 'idle')))
                                if a2 in ('move', 'dash'): a2 += ('_back' if d2 > d else ('_fwd' if d2 < d else '_side'))
                                KITE[tk][ty][(a, a2)] += 1
                if nd:
                    # front body: nearest to enemy; ties -> all
                    m = min(nd.values())
                    fr = [i for i in nd if nd[i] == m]
                    if len(alive) >= 2 and len(set(cls(g.types[i][1]) for i in alive)) >= 2:
                        for i in fr: FRONT[tk][cls(g.types[i][1])] += 1 / len(fr)
                        FRONT[tk]['_rounds'] += 1
                        # casters strictly behind a melee?
                        cs = [nd[i] for i in nd if cls(g.types[i][1]) == 'caster']; ms = [nd[i] for i in nd if cls(g.types[i][1]) == 'melee']
                        if cs and ms:
                            FRONT[tk]['_cm_rounds'] += 1
                            if min(ms) < min(cs): FRONT[tk]['_melee_in_front'] += 1
                            FRONT[tk]['_caster_minus_melee'] = FRONT[tk].get('_caster_minus_melee', 0) + (min(cs) - min(ms))
                # formation: pairwise distances among alive participants near the enemy
                near = [i for i in nd]
                if len(near) >= 2:
                    pd = [cheb((s[a]['x'], s[a]['y']), (s[b]['x'], s[b]['y'])) for ai, a in enumerate(near) for b in near[ai+1:]]
                    FORM[tk]['mean'].append(st.mean(pd)); FORM[tk]['max'].append(max(pd)); FORM[tk]['n'].append(len(near))
                    # nearest-ally distance per champion
                    for a in near:
                        FORM[tk]['nearest_ally'].append(min(cheb((s[a]['x'], s[a]['y']), (s[b]['x'], s[b]['y'])) for b in near if b != a))
        # ---- approach grouping (our side): pairwise distance of our participants in the 15 rounds before r0
        ids = [i for i in parts[us]]
        for back in range(15, -1, -1):
            k = g.ridx[f['r0']] - back
            if k < 0: continue
            rr = g.order[k]; s = g.rounds[rr]
            al = [i for i in ids if s[i]['alive']]
            if len(al) >= 2:
                pd = [cheb((s[a]['x'], s[a]['y']), (s[b]['x'], s[b]['y'])) for ai, a in enumerate(al) for b in al[ai+1:]]
                APP[g.team][back].append(max(pd))
        # ---- hold: when our caster hits first, distance to nearest melee ally at that moment; and did the caster move in the 3 rounds before
        if f['first']['at'] == us and cls(f['first']['aty']) == 'caster':
            a = f['first']['a']; pr = prev_round(g, f['r0']); s = g.rounds[pr]
            ml = [cheb((s[a]['x'], s[a]['y']), (s[j]['x'], s[j]['y'])) for j in ids if j != a and s[j]['alive'] and cls(g.types[j][1]) == 'melee']
            al = [cheb((s[a]['x'], s[a]['y']), (s[j]['x'], s[j]['y'])) for j in ids if j != a and s[j]['alive']]
            k = g.ridx[f['r0']]
            moved = sum(1 for x in g.order[max(0, k-3):k] if 'move' in g.acts[a].get(x, []))
            HOLD[g.team].append(dict(melee=min(ml) if ml else None, ally=min(al) if al else None, moved=moved, alone=not al))
        # ---- chase: our hitters following an enemy that retreats
        for rt in f['retreats']:
            if rt['team'] == us: continue
            v = rt['i']; r_ret = rt['r']
            # our champions that hit v in the 3 rounds before the retreat
            hitters = set(h['a'] for h in g.hits if h['v'] == v and r_ret - 3 <= h['r'] <= r_ret and g.types[h['a']][0] == us)
            if not hitters: continue
            k = g.ridx[r_ret]
            for a in hitters:
                # follow: number of consecutive rounds after r_ret in which a moves and its distance to v stays <= 5, and further hits on v
                steps = 0; hits_after = 0; last_hit_dist = None; tiles = 0
                p0 = (g.rounds[r_ret][a]['x'], g.rounds[r_ret][a]['y'])
                for x in g.order[k+1:k+13]:
                    sa = g.rounds[x][a]; sv = g.rounds[x][v]
                    if not sa['alive'] or not sv['alive']: break
                    if 'move' in g.acts[a].get(x, []) or 'dash' in g.acts[a].get(x, []):
                        if cheb((sa['x'], sa['y']), (sv['x'], sv['y'])) <= cheb((g.rounds[g.order[g.ridx[x]-1]][a]['x'], g.rounds[g.order[g.ridx[x]-1]][a]['y']), (g.rounds[g.order[g.ridx[x]-1]][v]['x'], g.rounds[g.order[g.ridx[x]-1]][v]['y'])) + 0 and cheb((sa['x'], sa['y']), (sv['x'], sv['y'])) <= 6:
                            steps += 1
                        else: break
                    hh = [h for h in g.hits if h['a'] == a and h['v'] == v and h['r'] == x]
                    hits_after += len(hh)
                    tiles = cheb(p0, (sa['x'], sa['y']))
                CHASE[g.team].append(dict(aty=g.types[a][1], vty=g.types[v][1], steps=steps, tiles=tiles, hits_after=hits_after, v_hpp=rt['hpp'], v_died=rt['died'], map=g.map, match=g.match, r=r_ret))
        # ---- leave vs kite classification of retreats
        for rt in f['retreats']:
            tk = g.team if rt['team'] == us else 'opp'
            i = rt['i']; k = g.ridx[rt['r']]
            far = False; resumed = False
            for x in g.order[k+1:k+9]:
                c = g.rounds[x][i]
                if not c['alive']: break
                if nearest(g, x, i, rt['team']) >= 8: far = True
                if g.dealt[i].get(x, 0) > 0: resumed = True
            kind = 'leave' if (far or rt['recalled'] or rt['died']) and not resumed else ('kite' if resumed else 'drift')
            LEAVE[tk].append(dict(rt, kind=kind))
    # ---- recalls: all recall starts with an enemy within 10: hp%, dist, completed?
    for i, rs in g.recall_start.items():
        t = g.types[i][0]; tk = g.team if t == us else 'opp'
        for r in rs:
            if r not in g.rounds: continue
            c = g.rounds[r][i]
            if not c['alive']: continue
            d = nearest(g, r, i, t)
            if d > 10: continue
            done = any(r < x <= r + 7 for x in g.recall_arrive[i])
            died = any(not g.rounds[x][i]['alive'] for x in g.order if r < x <= r + 7)
            RECALL[tk].append(dict(hpp=round(100*c['hp']/c['mhp']), d=d, done=done, died=died, ty=g.types[i][1], gems=c['gems']))
    # ---- avoid: contact (enemy within 5 tiles for >=3 consecutive rounds) with no hit in the window -> conditions
    # for each of our champions
    for i in [i for i in g.types if g.types[i][0] == us]:
        run = 0; cur = []
        for rr in g.order:
            c = g.rounds[rr][i]
            if not c['alive']: run = 0; continue
            d = nearest(g, rr, i, us)
            infight = rr in fight_rounds
            if d <= 5 and not infight:
                run += 1
                if run == 3:
                    s = g.rounds[rr]
                    foes = [e for e in s.values() if e['team'] != us and e['alive'] and cheb((e['x'], e['y']), (c['x'], c['y'])) <= 8]
                    ours = [e for e in s.values() if e['team'] == us and e['alive'] and cheb((e['x'], e['y']), (c['x'], c['y'])) <= 8]
                    # any fight starting within next 5 rounds near here?
                    soon = any(f['r0'] - 1 <= rr + 5 and f['r0'] >= rr and cheb(f['loc'], (c['x'], c['y'])) <= 8 for f in fs)
                    if not soon:
                        AVOID[g.team]['n'] += 1
                        AVOID[g.team]['outnumbered'] += len(foes) > len(ours)
                        AVOID[g.team]['outnumber'] += len(foes) < len(ours)
                        AVOID[g.team]['our_hp_lt50'] += c['hp'] < 0.5 * c['mhp']
                        AVOID[g.team]['we_busy_camp'] += rr in g.campatk[i] or rr in g.camphit[i]
                        AVOID[g.team]['they_busy_camp'] += any(rr in g.campatk[e['i']] or rr in g.camphit[e['i']] for e in foes)
                        AVOID[g.team]['they_on_spawn'] += any(g.dspawn[1-us][e['y']][e['x']] <= 1 for e in foes)
                        AVOID[g.team]['we_on_spawn'] += g.dspawn[us][c['y']][c['x']] <= 1
                        AVOID[g.team]['recalling'] += any(rr - 5 <= x <= rr for x in g.recall_start[i])
                        AVOID[g.team]['cooldown'] += any('spell' in g.acts[i].get(x, []) for x in g.order[max(0, g.ridx[rr]-7):g.ridx[rr]]) if cls(g.types[i][1]) == 'caster' else 0
                        AVOID[g.team]['caster'] += cls(g.types[i][1]) == 'caster'
                        AVOID[g.team]['melee'] += cls(g.types[i][1]) == 'melee'
                        AVOIDX[g.team].append((g.map, g.match[:8], rr, g.types[i][1], 'hp%d' % round(100*c['hp']/c['mhp']), 'foes', [e['ty'] for e in foes], 'ours', len(ours), 'enemy_busy' if any(rr in g.campatk[e['i']] or rr in g.camphit[e['i']] for e in foes) else '', 'we_busy' if (rr in g.campatk[i] or rr in g.camphit[i]) else ''))
            else:
                run = 0

print('# 3. distance to nearest enemy during fight rounds (enemy within 8), by class/type: median (p25-p75), n')
for tk in ('mite', 'uni', 'opp'):
    for c in ['melee', 'caster', 'ranged', 'Varg', 'Ryth', 'Issac', 'Ren', 'Marcella', 'Vendetta', 'Stellar', 'Cassi', 'Tavi', 'Prism', 'Vesper Vale', 'Willow']:
        x = sorted(D[tk][c])
        if len(x) < 30: continue
        q = lambda p: x[int(p*(len(x)-1))]
        hist = collections.Counter(min(v, 8) for v in x)
        print('%s %-12s n %5d med %s (%s-%s)  dist hist %s' % (tk, c, len(x), q(.5), q(.25), q(.75), ' '.join('%d:%d%%' % (k, round(100*hist[k]/len(x))) for k in sorted(hist))))
print('\n# 3a. actions per class in fight rounds (enemy within 8)')
for tk in ('mite', 'uni', 'opp'):
    for c, cnt in ACT[tk].items():
        n = sum(cnt.values()); print(tk, c, n, ' '.join('%s %s' % (k, pct(v, n)) for k, v in cnt.most_common()))
print('\n# 3b. kiting: the round after a ranged/caster attack or spell, what did the champion do (move_back = nearest enemy distance grew)')
for tk in ('mite', 'uni', 'opp'):
    for ty, cnt in KITE[tk].items():
        n = sum(cnt.values())
        if n < 20: continue
        agg = collections.Counter()
        for (a, a2), v in cnt.items(): agg[a2] += v
        print(tk, ty, n, ' '.join('%s %s' % (k, pct(v, n)) for k, v in agg.most_common()))
print('\n# 3c. front body (rounds with >=2 classes present): share of rounds each class is the nearest to the enemy; melee strictly in front of casters')
for tk in ('mite', 'uni', 'opp'):
    c = FRONT[tk]; n = c['_rounds']
    print(tk, 'rounds', n, ' '.join('%s %s' % (k, pct(v, n)) for k, v in c.items() if not k.startswith('_')), '| melee strictly in front of casters', pct(c['_melee_in_front'], c['_cm_rounds']), 'caster-melee gap mean', round(c.get('_caster_minus_melee', 0)/max(1, c['_cm_rounds']), 2))
print('\n# 3d. formation during fight rounds: pairwise distance among our champions engaged (>=2 near enemy)')
for tk in ('mite', 'uni', 'opp'):
    fm = FORM[tk]
    mx = fm['max']
    print(tk, 'rounds', len(mx), 'mean pairwise med', med(fm['mean']), 'max pairwise med', med(mx), 'nearest-ally dist med', med(fm['nearest_ally']), 'share max<=2 (ball)', pct(sum(1 for v in mx if v <= 2), len(mx)), 'max 3-5', pct(sum(1 for v in mx if 3 <= v <= 5), len(mx)), 'max>=6 (spread)', pct(sum(1 for v in mx if v >= 6), len(mx)), 'nearest ally <=1', pct(sum(1 for v in fm['nearest_ally'] if v <= 1), len(fm['nearest_ally'])))
print('\n# 3e. terrain in fight rounds vs all rounds (share of champion-rounds on bush / floor / near-wall)')
for tk in ('mite', 'uni', 'opp'):
    a = TILE[tk]; b = TILEBASE[tk]
    print(tk, 'fight: bush', pct(a['"'], sum(a.values())), 'hole', pct(a['o'], sum(a.values())), '| all rounds: bush', pct(b['"'], sum(b.values())), 'hole', pct(b['o'], sum(b.values())))
print('\n# 4. approach: max pairwise distance of our participants N rounds before the first hit (median)')
for tk in ('mite', 'uni'):
    print(tk, ' '.join('-%d:%s' % (b, med(APP[tk][b])) for b in sorted(APP[tk], reverse=True)))
print('\n# 4b. caster hits first: distance to nearest melee ally / any ally at that moment; moves in the 3 rounds before')
for tk in ('mite', 'uni'):
    h = HOLD[tk]
    ml = [x['melee'] for x in h if x['melee'] is not None]; al = [x['ally'] for x in h if x['ally'] is not None]
    print(tk, 'n', len(h), 'melee ally dist med', med(ml), '<=3', pct(sum(1 for v in ml if v <= 3), len(ml)), '>=6', pct(sum(1 for v in ml if v >= 6), len(ml)), '| any ally med', med(al), 'alone (no ally alive)', pct(sum(1 for x in h if x['alone']), len(h)), '| moved in 3 rounds before: 0:', pct(sum(1 for x in h if x['moved'] == 0), len(h)), '3:', pct(sum(1 for x in h if x['moved'] == 3), len(h)))
print('\n# 1x. AVOID: contact episodes (enemy within 5 tiles for 3 rounds, no fight starting within 5 rounds)')
for tk in ('mite', 'uni'):
    c = AVOID[tk]; n = c['n']
    print(tk, 'episodes', n, ' '.join('%s %s' % (k, pct(v, n)) for k, v in c.items() if k != 'n'))
    for x in AVOIDX[tk][:12]: print('   ', x)
print('\n# 1y. CHASE: when an enemy starts retreating from our hitters, how far do we follow')
for tk in ('mite', 'uni'):
    ch = CHASE[tk]
    print(tk, 'episodes', len(ch), 'follow steps med', med([c['steps'] for c in ch]), 'tiles moved in 12 rounds med', med([c['tiles'] for c in ch]), 'no follow (0 steps)', pct(sum(1 for c in ch if c['steps'] == 0), len(ch)), '>=3 steps', pct(sum(1 for c in ch if c['steps'] >= 3), len(ch)), 'hit again', pct(sum(1 for c in ch if c['hits_after'] > 0), len(ch)), 'victim died', pct(sum(1 for c in ch if c['v_died']), len(ch)))
    bycls = collections.defaultdict(list)
    for c in ch: bycls[cls(c['aty'])].append(c)
    for k, v in bycls.items(): print('   chaser', k, len(v), 'steps med', med([c['steps'] for c in v]), '>=3 steps', pct(sum(1 for c in v if c['steps'] >= 3), len(v)), 'hit again', pct(sum(1 for c in v if c['hits_after'] > 0), len(v)))
    low = [c for c in ch if c['v_hpp'] < 35]; hi = [c for c in ch if c['v_hpp'] >= 60]
    print('   victim hp<35:', len(low), '>=3 steps', pct(sum(1 for c in low if c['steps'] >= 3), len(low)), 'kill', pct(sum(1 for c in low if c['v_died']), len(low)), '| victim hp>=60:', len(hi), '>=3 steps', pct(sum(1 for c in hi if c['steps'] >= 3), len(hi)))
    ex = sorted([c for c in ch if c['steps'] >= 4], key=lambda c: -c['steps'])[:4]
    for c in ex: print('    ex', c)
print('\n# 2x. recalls started with an enemy within 10 tiles')
for tk in ('mite', 'uni', 'opp'):
    rc = RECALL[tk]
    if not rc: continue
    print(tk, 'n', len(rc), 'hp% med', med([r['hpp'] for r in rc]), 'dist med', med([r['d'] for r in rc]), 'dist hist', sorted(collections.Counter(r['d'] for r in rc).items()), 'completed', pct(sum(1 for r in rc if r['done']), len(rc)), 'died', pct(sum(1 for r in rc if r['died']), len(rc)))
    byd = collections.defaultdict(list)
    for r in rc: byd[min(r['d'], 10)].append(r)
    print('   completion by dist:', ' '.join('%d:%s(n%d)' % (d, pct(sum(1 for r in v if r['done']), len(v)), len(v)) for d, v in sorted(byd.items())))
print('\n# 3x. retreat kinds: leave (gets >=8 away / recalls / dies, no more damage) vs kite (resumes damage within 8 rounds) vs drift')
for tk in ('mite', 'uni', 'opp'):
    L = LEAVE[tk]; n = len(L)
    for kind in ('leave', 'kite', 'drift'):
        x = [r for r in L if r['kind'] == kind]
        if not x: continue
        print(tk, kind, pct(len(x), n), 'n', len(x), 'hp% med', med([r['hpp'] for r in x]), 'hp<30', pct(sum(1 for r in x if r['hpp'] < 30), len(x)), 'hp<50', pct(sum(1 for r in x if r['hpp'] < 50), len(x)), 'outnumbered', pct(sum(1 for r in x if r['enemies'] > r['allies'] + 1), len(x)), 'died', pct(sum(1 for r in x if r['died']), len(x)), 'recalled', pct(sum(1 for r in x if r['recalled']), len(x)), 'toward spawn', pct(sum(1 for r in x if r['dsp1'] is not None and r['dsp1'] < r['dsp0'] - 2), len(x)), 'toward ally', pct(sum(1 for r in x if r['na0'] is not None and r['na1'] is not None and r['na1'] < r['na0']), len(x)))
    lv = [r for r in L if r['kind'] == 'leave']
    byc = collections.defaultdict(list)
    for r in lv: byc[cls(r['ty'])].append(r)
    for c, x in byc.items(): print('   leave by class', c, len(x), 'hp% med', med([r['hpp'] for r in x]), 'hp<40', pct(sum(1 for r in x if r['hpp'] < 40), len(x)), 'died', pct(sum(1 for r in x if r['died']), len(x)))
    # leave reasons at hp>=50
    hi = [r for r in lv if r['hpp'] >= 50]
    print('   leave at hp>=50: n', len(hi), 'outnumbered', pct(sum(1 for r in hi if r['enemies'] > r['allies'] + 1), len(hi)), 'allies dead', pct(sum(1 for r in hi if r['allies_dead'] > 0), len(hi)), 'took dmg prev 3 rounds', pct(sum(1 for r in hi if r['taken_prev'] > 0), len(hi)), 'no enemy within 3', pct(sum(1 for r in hi if r['d'] > 3), len(hi)))
json.dump({'leave': LEAVE, 'chase': CHASE, 'recall': RECALL}, open(S + '/reports/scripts_fights/positioning_out.json', 'w'))

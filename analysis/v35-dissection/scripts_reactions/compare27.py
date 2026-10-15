"""Side-by-side tables study27 (ws3) vs study26 (ws2) vs opponents in study27. Usage: python3 -I compare27.py ROWS27 STACK27 ROWS26 STACK26 SEL27 SEL26"""
import sys, json, collections, statistics as st, math
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_reactions')
from common import MELEE, CASTER, cls, tier
R27, K27, R26, K26 = [json.load(open(p)) for p in sys.argv[1:5]]
SEL27, SEL26 = [json.load(open(p)) for p in sys.argv[5:7]]
N27, N26 = len(SEL27), len(SEL26)
def pct(a, b): return '%d%%' % round(100 * a / b) if b else '-'
def pf(a, b): return '%.1f%%' % (100 * a / b) if b else '-'
def med(x): x = [v for v in x if v is not None]; return st.median(x) if x else None
def q(x, p):
    x = sorted(v for v in x if v is not None); return x[min(len(x) - 1, int(p * len(x)))] if x else None
def z(a, n, b, m):
    """two-proportion z between a/n and b/m"""
    if not n or not m: return 0
    p = (a + b) / (n + m); se = math.sqrt(p * (1 - p) * (1 / n + 1 / m)) if 0 < p < 1 else 0
    return (a / n - b / m) / se if se else 0
def flag(a, n, b, m): zz = z(a, n, b, m); return ' **(z=%.1f)**' % zz if abs(zz) >= 2.5 else (' (z=%.1f)' % zz if abs(zz) >= 1.8 else '')
COLS = [('study27 us', R27, SEL27, True, N27), ('study26 us', R26, SEL26, True, N26), ('study27 opp', R27, SEL27, False, N27)]
def sub(R, key, us): return [x for x in R[key] if x['us'] == us]
def hdr(cols=None):
    cols = cols or [c[0] for c in COLS]
    return '| | ' + ' | '.join(cols) + ' |\n|---|' + '---|' * len(cols)
def prow(label, vals): return '| %s | %s |' % (label, ' | '.join(str(v) for v in vals))
def prop_row(label, key, pred, denom=None):
    """pred(row)->bool over R[key] rows of each column; show count/total pct; flag 27us vs 26us"""
    cells = []; ab = []
    for name, R, sel, us, ng in COLS:
        X = sub(R, key, us); X2 = [x for x in X if denom(x)] if denom else X
        a = sum(1 for x in X2 if pred(x)); n = len(X2); ab.append((a, n))
        cells.append('%s (%d/%d)' % (pct(a, n), a, n))
    cells[0] += flag(ab[0][0], ab[0][1], ab[1][0], ab[1][1])
    return prow(label, cells)
def med_row(label, key, f, denom=None):
    cells = []
    for name, R, sel, us, ng in COLS:
        X = sub(R, key, us); X2 = [x for x in X if denom(x)] if denom else X
        v = [f(x) for x in X2]; cells.append('%s (n=%d)' % (med(v), len([a for a in v if a is not None])))
    return prow(label, cells)
def pergame_row(label, key, f):
    cells = []
    for name, R, sel, us, ng in COLS:
        X = sub(R, key, us); cells.append('%.2f (%d/%d)' % (sum(f(x) for x in X) / ng, sum(f(x) for x in X), ng))
    return prow(label, cells)

print('## 1. Hit reactions\n')
print('Unit = hit round (champion took damage from an enemy champion). Flag: z = two-proportion z-score study27 us vs study26 us; bold when |z| >= 2.5.\n')
def HR(R, us):
    out = []
    for h in R['hits']:
        if h['us'] != us: continue
        for row in h['rows']: out.append(dict(h, r=row['r'], band=row['band'], seq=row['seq']))
    return out
def simp(c):
    if c == 'fight+lateral': return 'fight'
    if c == 'arrived': return 'recall'
    return c
CL = ['fight', 'fight+away', 'fight+closer', 'away', 'closer', 'lateral', 'camp', 'recall', 'tribute', 'nothing', 'dead']
for k in (0, 1):
    print('### action at t+%d (all hit rounds)\n' % k)
    print('| rows | n | ' + ' | '.join(CL) + ' |\n|' + '---|' * (len(CL) + 2))
    base = None
    for name, R, sel, us, ng in COLS:
        X = HR(R, us); c = collections.Counter(simp(r['seq'][k]) for r in X if len(r['seq']) > k); n = sum(c.values())
        if base is None: base = (c, n)
        cells = []
        for x in CL:
            s = pct(c[x], n)
            if name == 'study26 us': s += flag(base[0][x], base[1], c[x], n).replace('**', '')
            cells.append(s)
        print('| %s | %d | %s |' % (name, n, ' | '.join(cells)))
    print()
print('### action at t+1 by hp band before the hit (fight / away / nothing / dead)\n')
print(hdr())
for b in ('>70', '40-70', '<40'):
    cells = []
    for name, R, sel, us, ng in COLS:
        X = [r for r in HR(R, us) if r['band'] == b]; c = collections.Counter(simp(r['seq'][1]) for r in X if len(r['seq']) > 1); n = sum(c.values())
        cells.append('n=%d: %s / %s / %s / %s' % (n, pct(c['fight'] + c['fight+away'] + c['fight+closer'], n), pct(c['away'], n), pct(c['nothing'], n), pct(c['dead'], n)))
    print(prow('hp ' + b, cells))
print()
print('### hit episodes: death rate, retreat step, group retreat\n')
print(hdr())
print(prop_row('episodes ending in death (within episode + 6 rounds)', 'hits', lambda h: h['died']))
for b in ('>70', '40-70', '<40'): print(prop_row('  died, first hit at hp ' + b, 'hits', lambda h: h['died'], lambda h: h['band'] == b))
for c in ('melee', 'caster'): print(prop_row('  died, ' + c, 'hits', lambda h: h['died'], lambda h: h['cls'] == c))
print(prop_row('episodes with a retreat step', 'hits', lambda h: h['ret_delay'] is not None))
print(med_row('retreat delay (rounds after first hit), median', 'hits', lambda h: h['ret_delay']))
print(prop_row('retreat step with no ally within 6', 'hits', lambda h: h['grp'] == 'no_ally_within_6', lambda h: h['grp']))
print(prop_row('retreat step, allies stay', 'hits', lambda h: h['grp'] == 'allies_stay', lambda h: h['grp']))
print(prop_row('retreat step, all allies also retreat', 'hits', lambda h: h['grp'] == 'allies_also_retreat', lambda h: h['grp']))
print(prop_row('first hit with 2+ allies within 8', 'hits', lambda h: h['allies8'] >= 2))
print(prop_row('first hit with 0 allies within 8', 'hits', lambda h: h['allies8'] == 0))
print(prop_row('episodes hit by 2+ enemy champions', 'hits', lambda h: h['nfoe_hitting'] >= 2))
print()
print('### death rate per hit episode by champion type (us)\n')
print('| type | study27 | study26 | study27 opp |\n|---|---|---|---|')
tys = sorted(set(h['ty'] for h in R27['hits'] + R26['hits']))
for ty in tys:
    cells = []; ab = []
    for name, R, sel, us, ng in COLS:
        X = [h for h in sub(R, 'hits', us) if h['ty'] == ty]; a = sum(1 for h in X if h['died']); ab.append((a, len(X)))
        cells.append('%s (%d/%d)' % (pct(a, len(X)), a, len(X)) if X else '-')
    cells[0] += flag(*ab[0], *ab[1])
    print(prow(ty, cells))
print()

print('## 2. Retreat outcomes\n')
print('Unit = retreat step (see study26 report for the definition). Outcome within 15 rounds.\n')
print(hdr())
print(pergame_row('retreat steps per game', 'retreats', lambda x: 1))
print(med_row('hp% at the retreat step, median', 'retreats', lambda x: x['hp']))
print(med_row('nearest foe distance at the step, median', 'retreats', lambda x: x['dfoe']))
print(prop_row('foe follows (>= 1 closing step)', 'retreats', lambda x: x['follow'] > 0))
print(prop_row('outrun after 5 rounds (distance +3 or more)', 'retreats', lambda x: x['dd5'] is not None and x['dd5'] >= 3))
print(prop_row('caught (no distance gained after 5 rounds)', 'retreats', lambda x: x['dd5'] is not None and x['dd5'] <= 0))
print(prop_row('toward own spawn (dspawn -2 or more after 5 rounds)', 'retreats', lambda x: x['dds5'] is not None and x['dds5'] <= -2))
print(prop_row('toward an ally (-2 or more)', 'retreats', lambda x: x['dda5'] is not None and x['dda5'] <= -2))
for o in ('death', 'recall', 'escape', 'escape_near', 'still_fighting'): print(prop_row('outcome: ' + o, 'retreats', lambda x, o=o: x['out'] == o))
print(prop_row('  death, retreat started below 40% hp', 'retreats', lambda x: x['out'] == 'death', lambda x: x['band'] == '<40'))
print(prop_row('  death, retreat started above 70% hp', 'retreats', lambda x: x['out'] == 'death', lambda x: x['band'] == '>70'))
for c in ('melee', 'caster'): print(prop_row('  death, ' + c, 'retreats', lambda x: x['out'] == 'death', lambda x, c=c: x['cls'] == c))
print(prop_row('recall started within 15 rounds of the step', 'retreats', lambda x: x['recall_delay'] is not None))
print()

print('## 3. Recalls\n')
print('Unit = recall attempt (spam restarts merged).\n')
print(hdr())
print(pergame_row('attempts per game', 'recalls', lambda x: 1))
for o in ('arrived', 'hit_foe', 'hit_camp', 'died', 'moved', 'attacked'): print(prop_row('outcome: ' + o, 'recalls', lambda x, o=o: x['out'] == o))
print(prop_row('interrupted (hit_foe + hit_camp + died)', 'recalls', lambda x: x['out'] in ('hit_foe', 'hit_camp', 'died')))
print(med_row('hp% at start, median', 'recalls', lambda x: x['hp']))
print(prop_row('started with hp < 50', 'recalls', lambda x: x['hp'] < 50))
print(prop_row('started with gems > 0', 'recalls', lambda x: x['gems'] > 0))
print(med_row('nearest foe at start, median', 'recalls', lambda x: x['dfoe']))
print(prop_row('started with a foe within 5', 'recalls', lambda x: x['dfoe'] <= 5))
print(prop_row('  of those, arrived', 'recalls', lambda x: x['out'] == 'arrived', lambda x: x['dfoe'] <= 5))
print(prop_row('started within 3 rounds of being hit by a foe', 'recalls', lambda x: x['hit_recent']))
print(prop_row('  of those, arrived', 'recalls', lambda x: x['out'] == 'arrived', lambda x: x['hit_recent']))
print(prop_row('retry after an interruption/cancel (of interrupted attempts)', 'recalls', lambda x: x['after'] == 'retry', lambda x: x['after'] is not None))
print(prop_row('died within 10 rounds of an interruption', 'recalls', lambda x: x['after'] == 'died', lambda x: x['after'] is not None))
print(prop_row('fought within 10 rounds of an interruption', 'recalls', lambda x: x['after'] == 'fought', lambda x: x['after'] is not None))
print()
print('Recall starts per game by map (us; starts / arrival / interrupted):\n')
maps = sorted(set(s['map'] for s in SEL27 + SEL26))
print('| map | study27 (games) | study26 (games) |\n|---|---|---|')
for mp in maps:
    cells = []
    for name, R, sel, us, ng in COLS[:2]:
        X = [x for x in sub(R, 'recalls', us) if x['map'] == mp]; g = sum(1 for s in sel if s['map'] == mp)
        cells.append('%.1f / %s / %d (%d)' % (len(X) / g, pct(sum(1 for x in X if x['out'] == 'arrived'), len(X)), sum(1 for x in X if x['out'] in ('hit_foe', 'hit_camp', 'died')), g) if g else '-')
    print(prow(mp, cells))
print()

print('## 4. Help\n')
print('Unit = (first hit of an episode, ally alive within 8). Help = ally fought or came within 5 rounds.\n')
print(hdr())
print(pergame_row('victim-ally pairs per game', 'helps', lambda x: 1))
for o in ('fought', 'came', 'kept_farming', 'moved_away', 'other'): print(prop_row('ally ' + o, 'helps', lambda x, o=o: x['res'] == o))
print(prop_row('help (fought+came)', 'helps', lambda x: x['res'] in ('fought', 'came')))
print(prop_row('  ally was farming a camp: kept farming', 'helps', lambda x: x['res'] == 'kept_farming', lambda x: x['ally_was_farming']))
print(prop_row('  ally was farming a camp: helped', 'helps', lambda x: x['res'] in ('fought', 'came'), lambda x: x['ally_was_farming']))
print(prop_row('  ally within 3: helped', 'helps', lambda x: x['res'] in ('fought', 'came'), lambda x: x['d0'] <= 3))
print(prop_row('  victim died: helped', 'helps', lambda x: x['res'] in ('fought', 'came'), lambda x: x['victim_died']))
print(prop_row('  victim survived: helped', 'helps', lambda x: x['res'] in ('fought', 'came'), lambda x: not x['victim_died']))
print(prop_row('share of first hits with an ally within 8 (of episodes)', 'hits', lambda h: h['allies8'] > 0))
print()

print('## 5. Deaths\n')
print(hdr())
print(pergame_row('deaths per game (incl. pair deaths)', 'deaths', lambda d: 1))
print(pergame_row('direct deaths per game', 'deaths', lambda d: 0 if d['pair'] else 1))
print(pergame_row('gems lost to deaths per game', 'deaths', lambda d: d['gems']))
cells = []
for name, R, sel, us, ng in COLS:
    lost = sum(d['gems'] for d in sub(R, 'deaths', us)); trib = sum(s['score'] if us else s['oscore'] for s in sel); cells.append('%s (%d / %d)' % (pf(lost, trib), lost, trib))
print(prow('gems lost as share of gems tributed', cells))
print(prop_row('deaths carrying gems', 'deaths', lambda d: d['gems'] > 0))
print(med_row('bag when > 0, median', 'deaths', lambda d: d['gems'], lambda d: d['gems'] > 0))
DD = lambda d: not d['pair']
print(prop_row('zone: own half (direct deaths)', 'deaths', lambda d: d['zone'] == 'own', DD))
print(prop_row('zone: enemy half', 'deaths', lambda d: d['zone'] == 'enemy', DD))
print(med_row('distance to own spawn, median', 'deaths', lambda d: d['dspawn'], DD))
print(prop_row('within 2 of an altar', 'deaths', lambda d: d['daltar'] <= 2, DD))
for b in ('approaching', 'fleeing', 'idle', 'farming', 'fighting', 'recalling', 'tributing', 'walking'): print(prop_row('doing before the final episode: ' + b, 'deaths', lambda d, b=b: d['before'] == b, DD))
print(med_row('hp% at the first hit of the final episode, median', 'deaths', lambda d: d['hp_first'], DD))
print(prop_row('  hp >= 70 at first hit', 'deaths', lambda d: d['hp_first'] >= 70, DD))
print(prop_row('  hp < 40 at first hit', 'deaths', lambda d: d['hp_first'] < 40, DD))
print(prop_row('1-round deaths (burst)', 'deaths', lambda d: d['ep_len'] == 1, DD))
print(med_row('final episode length (rounds), median', 'deaths', lambda d: d['ep_len'], DD))
print(prop_row('enemy champions dealing damage: 1', 'deaths', lambda d: d['nfoes'] == 1, DD))
print(prop_row('enemy champions dealing damage: 3+', 'deaths', lambda d: d['nfoes'] >= 3, DD))
print(med_row('spell share of episode damage, median', 'deaths', lambda d: d['spell_share'], DD))
print(prop_row('killing blow by spell', 'deaths', lambda d: d['kkind'] == 'spell', DD))
print(prop_row('killing blow by camp', 'deaths', lambda d: d['kkind'] == 'camp', DD))
print(prop_row('camp damage > 50% of the episode', 'deaths', lambda d: d['camp_share'] > 50, DD))
print(prop_row('allies within 6 at death: 0', 'deaths', lambda d: d['allies6'] == 0, DD))
print(prop_row('allies within 6 at death: 2+', 'deaths', lambda d: d['allies6'] >= 2, DD))
print(prop_row('allies within 8 at the first hit: 2+', 'deaths', lambda d: d['allies8_0'] >= 2, DD))
print(prop_row('outnumbered at the first hit (foes8 > allies8+1)', 'deaths', lambda d: d['nfoe8_0'] > d['allies8_0'] + 1, DD))
print(prop_row('recall in progress at death', 'deaths', lambda d: d['recall_active'], DD))
print(prop_row('recall attempted in the episode', 'deaths', lambda d: d['recall_tries'] > 0, DD))
print(prop_row('no retreat move in the episode', 'deaths', lambda d: d['fled'] == 0, DD))
print(prop_row('fought back >= 1 round', 'deaths', lambda d: d['fought'] > 0, DD))
print()
print('### killer type (direct deaths)\n')
print('| killer | study27 us | study26 us | study27 opp |\n|---|---|---|---|')
ks = collections.Counter()
for name, R, sel, us, ng in COLS: ks.update(d['killer'] for d in sub(R, 'deaths', us) if not d['pair'])
for k, _ in ks.most_common(12):
    cells = []
    for name, R, sel, us, ng in COLS:
        X = [d for d in sub(R, 'deaths', us) if not d['pair']]; a = sum(1 for d in X if d['killer'] == k); cells.append('%d (%s)' % (a, pct(a, len(X))))
    print(prow(k, cells))
print()
print('### deaths per champion type (direct deaths; per game in which the type was drafted)\n')
def drafted(sel, us):
    c = collections.Counter()
    for s in sel:
        for x in (s['draft'] if us else s['odraft']):
            for t in ({'cassi_issac': ['Cassi', 'Issac'], 'vesper_vale': ['VesperVale']}.get(x, [x.capitalize()])): c[t] += 1
    return c
print('| type | study27: deaths / games drafted / per game / gems lost | study26 | study27 opp |\n|---|---|---|---|')
tys = sorted(set(d['ty'] for d in R27['deaths'] + R26['deaths']))
for ty in tys:
    cells = []
    for name, R, sel, us, ng in COLS:
        X = [d for d in sub(R, 'deaths', us) if d['ty'] == ty]; Xd = [d for d in X if not d['pair']]; dr = drafted(sel, us)[ty]
        cells.append('%d / %d / %.2f / %d' % (len(Xd), dr, len(Xd) / dr, sum(d['gems'] for d in X)) if dr else '-')
    print(prow(ty, cells))
print()
print('### deaths per game by map (all deaths incl. pair; deaths/game, gems lost/game, games)\n')
print('| map | study27 us | study26 us | study27 opp |\n|---|---|---|---|')
for mp in maps:
    cells = []
    for name, R, sel, us, ng in COLS:
        X = [d for d in sub(R, 'deaths', us) if d['map'] == mp]; g = sum(1 for s in sel if s['map'] == mp)
        cells.append('%.1f / %.0f (%d)' % (len(X) / g, sum(d['gems'] for d in X) / g, g) if g else '-')
    print(prow(mp, cells))
print()
print('### deaths per game by result / tier / draft size\n')
print('| split | study27 us | study26 us | study27 opp |\n|---|---|---|---|')
for key, vals in (('res', ('win', 'loss')), ('tier', ('top10', '11-20', '21-30', 'other')), ('nch', (3, 4, 5))):
    for v in vals:
        cells = []
        for name, R, sel, us, ng in COLS:
            X = [d for d in sub(R, 'deaths', us) if d[key] == v]; g = sum(1 for s in sel if (s['res'] if key == 'res' else tier(s['orank']) if key == 'tier' else len(s['draft'])) == v)
            cells.append('%.1f / %.0f (%d)' % (len(X) / g, sum(d['gems'] for d in X) / g, g) if g else '-')
        print(prow('%s %s' % (key, v), cells))
print()
print('Deaths per game distribution (us): study27 ' + ', '.join('%d:%d' % kv for kv in sorted(collections.Counter(collections.Counter(d['match'] for d in sub(R27, 'deaths', True))[s['match']] for s in SEL27).items())) + '; study26 ' + ', '.join('%d:%d' % kv for kv in sorted(collections.Counter(collections.Counter(d['match'] for d in sub(R26, 'deaths', True))[s['match']] for s in SEL26).items())))
print()

print('## 6. Stacking and deaths\n')
print('"On a camp group" = within 3 tiles of a living camp entity of that group (monster or cluster); stack = number of our living champions on the same group as the victim (victim included); big group = the bot P_STACK_HP rule: a non-monolith camp group (replay group id) whose monsters total >= 3000 hp: the 3-wolf groups of rows (4050, 6 per map) and the elk pairs of corners (4800, 4 per map); every other map has only 1350/2400/2700 groups. Exposure = champion-rounds. Direct deaths only.\n')
def expo(K):
    e = collections.Counter()
    for us, k, big, v in K['expo']: e[(us, k, big)] += v
    return e
SCOLS = [('study27 us', K27, True, N27), ('study26 us', K26, True, N26), ('study27 opp', K27, False, N27)]
print('### exposure: share of champion-rounds by stack size (small groups / big groups)\n')
print('| stack | ' + ' | '.join(c[0] for c in SCOLS) + ' |\n|---|---|---|---|')
for k in (0, 1, 2, 3, 4, 5):
    cells = []
    for name, K, us, ng in SCOLS:
        e = expo(K); tot = sum(v for (u, kk, b), v in e.items() if u == us)
        cells.append('%s / %s (%d / %d)' % (pct(e[(us, k, False)], tot), pct(e[(us, k, True)], tot), e[(us, k, False)], e[(us, k, True)]) if k < 5 else '%s / %s' % (pct(sum(v for (u, kk, b), v in e.items() if u == us and kk >= 5 and not b), tot), pct(sum(v for (u, kk, b), v in e.items() if u == us and kk >= 5 and b), tot)))
    print(prow(str(k) if k < 5 else '5+', cells))
print()
print('### direct deaths by stack size at death, and deaths per 1000 champion-rounds in that state\n')
print('| stack at death | ' + ' | '.join(c[0] for c in SCOLS) + ' |\n|---|---|---|---|')
for k in (0, 1, 2, 3, 4):
    cells = []; ab = []
    for name, K, us, ng in SCOLS:
        e = expo(K); D = [d for d in K['deaths'] if d['us'] == us]
        if k < 4: a = sum(1 for d in D if d['stack'] == k); ex = e[(us, k, False)] + e[(us, k, True)]
        else: a = sum(1 for d in D if d['stack'] >= 4); ex = sum(v for (u, kk, b), v in e.items() if u == us and kk >= 4)
        ab.append((a, len(D)))
        cells.append('%d (%s of deaths; %.2f per 1000 cr)' % (a, pct(a, len(D)), 1000 * a / ex if ex else 0))
    cells[0] += flag(*ab[0], *ab[1])
    print(prow(str(k) if k < 4 else '4+', cells))
print()
print('| | ' + ' | '.join(c[0] for c in SCOLS) + ' |\n|---|---|---|---|')
def srow(label, pred, denom=None):
    cells = []; ab = []
    for name, K, us, ng in SCOLS:
        D = [d for d in K['deaths'] if d['us'] == us]; D2 = [d for d in D if denom(d)] if denom else D
        a = sum(1 for d in D2 if pred(d)); ab.append((a, len(D2))); cells.append('%s (%d/%d)' % (pct(a, len(D2)), a, len(D2)))
    cells[0] += flag(*ab[0], *ab[1])
    return prow(label, cells)
print(srow('death on a big camp group (stack >= 1, big)', lambda d: d['big'] and d['stack'] >= 1))
print(srow('death with 3-4 of ours on the same camp group', lambda d: d['stack'] >= 3))
print(srow('  of those, on a big group', lambda d: d['big'], lambda d: d['stack'] >= 3))
print(srow('5 rounds before death: 3-4 of ours on one camp group', lambda d: d['stack5'] >= 3))
print(srow('living camp monster within 3 at death', lambda d: d['mon3'] >= 1))
print(srow('  awake monster within 3', lambda d: d['mon_awake'] >= 1))
print(srow('hit by a camp in the previous 5 rounds', lambda d: d['camphit5'] >= 1))
print(srow('  camp dealt >= 300 in the previous 5 rounds', lambda d: d['campdmg5'] >= 300))
print(srow('killed by a camp', lambda d: d['killer'] == 'camp'))
print(srow('allies within 6 at death: 0', lambda d: d['allies6'] == 0))
print(srow('allies within 6 at death: 1', lambda d: d['allies6'] == 1))
print(srow('allies within 6 at death: 2+', lambda d: d['allies6'] >= 2))
print(srow('  stack >= 3 deaths: enemies within 8 >= 3', lambda d: d['foes8'] >= 3, lambda d: d['stack'] >= 3))
print(srow('  stack >= 3 deaths: hit by a camp in prev 5 rounds', lambda d: d['camphit5'] >= 1, lambda d: d['stack'] >= 3))
print(srow('  stack 0 deaths: hit by a camp in prev 5 rounds', lambda d: d['camphit5'] >= 1, lambda d: d['stack'] == 0))
print()
print('### gems lost by stack size at death (direct deaths)\n')
print('| stack | ' + ' | '.join(c[0] for c in SCOLS) + ' |\n|---|---|---|---|')
for k in (0, 1, 2, 3):
    cells = []
    for name, K, us, ng in SCOLS:
        D = [d for d in K['deaths'] if d['us'] == us and (d['stack'] == k if k < 3 else d['stack'] >= 3)]
        cells.append('%d gems in %d deaths (%.1f/game)' % (sum(d['gems'] for d in D), len(D), sum(d['gems'] for d in D) / ng))
    print(prow(str(k) if k < 3 else '3+', cells))
print()
print('### hit episodes starting while stacked (hit-round starts after a quiet round), and deaths per such start\n')
print('| stack at hit | ' + ' | '.join(c[0] for c in SCOLS) + ' |\n|---|---|---|---|')
for k in (0, 1, 2, 3):
    cells = []
    for name, K, us, ng in SCOLS:
        H = [h for h in K['hits'] if h['us'] == us and (h['stack'] == k if k < 3 else h['stack'] >= 3)]; tot = sum(1 for h in K['hits'] if h['us'] == us)
        e = expo(K); ex = (e[(us, k, False)] + e[(us, k, True)]) if k < 3 else sum(v for (u, kk, b), v in e.items() if u == us and kk >= 3)
        cells.append('%d (%s; %.1f per 1000 cr)' % (len(H), pct(len(H), tot), 1000 * len(H) / ex if ex else 0))
    print(prow(str(k) if k < 3 else '3+', cells))
print()

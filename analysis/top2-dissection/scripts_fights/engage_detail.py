"""Engage details: victim state at the first hit, baseline camp-busy rate, opener movement, numbers per map, death context, examples."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_fights')
from common import *
F = json.load(open(S + '/reports/scripts_fights/fights.json'))
byg = collections.defaultdict(list)
for f in F: byg[(f['match'], f['team'])].append(f)
def med(x): return st.median(x) if x else None
def pct(a, b): return '%d%%' % round(100*a/b) if b else '-'
def us(f): return f['sides'][str(f['us'])]
def them(f): return f['sides'][str(1-f['us'])]
def real(f): return us(f)['dmg'] + them(f)['dmg'] >= 1000 or us(f)['deaths'] or them(f)['deaths']

VH = {t: [] for t in ('mite', 'uni')}        # victim hp% at our first hit, victim busy, victim recalling, victim alone
BASE = {t: collections.Counter() for t in ('mite', 'uni')}  # baseline: enemy champion-rounds within 8 of us: busy / low / alone
OPEN = {t: collections.Counter() for t in ('mite', 'uni')}
NUM = {t: collections.defaultdict(list) for t in ('mite', 'uni')}
DEATH = {t: [] for t in ('mite', 'uni')}
EX = collections.defaultdict(list)
WL = collections.defaultdict(lambda: [0, 0])
for rec in selected():
    g = load_game(rec); t = g.team; usi = g.us
    WL[(t, g.map)][0 if rec['res'] == 'win' else 1] += 1
    fs = byg[(g.match, t)]
    # baseline
    for rr in g.order[::3]:
        s = g.rounds[rr]
        for e in s.values():
            if e['team'] == usi or not e['alive']: continue
            if not any(c['team'] == usi and c['alive'] and cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8 for c in s.values()): continue
            BASE[t]['n'] += 1
            BASE[t]['busy'] += (rr in g.campatk[e['i']] or rr in g.camphit[e['i']])
            BASE[t]['low50'] += e['hp'] < 0.5 * e['mhp']
            BASE[t]['low30'] += e['hp'] < 0.3 * e['mhp']
            BASE[t]['alone'] += not any(c['team'] != usi and c['alive'] and c['i'] != e['i'] and cheb((c['x'], c['y']), (e['x'], e['y'])) <= 4 for c in s.values())
    for f in fs:
        pr = prev_round(g, f['r0']); s = g.rounds[pr]
        a, v = f['first']['a'], f['first']['v']
        # numbers within 5 of the first hit location
        n5 = {tt: sum(1 for c in s.values() if c['team'] == tt and c['alive'] and cheb((c['x'], c['y']), f['loc']) <= 5) for tt in (0, 1)}
        NUM[t][f['map']].append((n5[usi] - n5[1-usi], f['first']['at'] == usi, real(f)))
        if f['first']['at'] == usi:
            vc = s[v]
            busy = (pr in g.campatk[v] or pr in g.camphit[v] or f['r0'] in g.campatk[v] or f['r0'] in g.camphit[v])
            recalling = any(f['r0'] - 5 <= x < f['r0'] for x in g.recall_start[v]) and not any(f['r0'] - 5 <= x < f['r0'] for x in g.recall_arrive[v])
            alone = not any(c['team'] != usi and c['alive'] and c['i'] != v and cheb((c['x'], c['y']), (vc['x'], vc['y'])) <= 4 for c in s.values())
            VH[t].append(dict(hpp=round(100*vc['hp']/vc['mhp']), busy=busy, recalling=recalling, alone=alone, real=real(f), kills=us(f)['kills'], deaths=len(us(f)['deaths']), vty=g.types[v][1], map=g.map, match=g.match, r=f['r0'], aty=g.types[a][1]))
            if busy and real(f) and len(EX['busy_' + t]) < 4: EX['busy_' + t].append((g.map, g.match[:8], 'r%d' % f['r0'], g.types[a][1], '->', g.types[v][1], 'hp%d%%' % round(100*vc['hp']/vc['mhp']), 'K/D', us(f)['kills'], len(us(f)['deaths'])))
            if vc['hp'] < 0.4 * vc['mhp'] and real(f) and len(EX['low_' + t]) < 4: EX['low_' + t].append((g.map, g.match[:8], 'r%d' % f['r0'], g.types[a][1], '->', g.types[v][1], 'hp%d%%' % round(100*vc['hp']/vc['mhp']), 'K/D', us(f)['kills'], len(us(f)['deaths'])))
            # opener movement pattern (attacker): moved in r0-3, r0-2, r0-1, r0 ; victim moved in r0-1
            k = g.ridx[f['r0']]
            pat = ''.join('m' if ('move' in g.acts[a].get(x, []) or 'dash' in g.acts[a].get(x, [])) else '.' for x in g.order[max(0, k-3):k+1])
            c = cls(g.types[a][1])
            OPEN[t][(c, pat)] += 1
            OPEN[t][(c, '_n')] += 1
            # did the victim walk toward the attacker in the round before / the round of the hit
            if k >= 1:
                sp = g.rounds[g.order[k-1]]
                sp2 = g.rounds[g.order[k-2]] if k >= 2 else sp
                ap = (g.rounds[f['r0']][a]['x'], g.rounds[f['r0']][a]['y'])
                dv = cheb((sp2[v]['x'], sp2[v]['y']), ap) - cheb((sp[v]['x'], sp[v]['y']), ap) if sp2[v]['alive'] else 0
                OPEN[t][(c, 'victim_walked_in')] += dv > 0
    # death context for our champions
    for (r, i, killer) in g.deaths:
        if g.types[i][0] != usi: continue
        pr = prev_round(g, r); s = g.rounds[pr]; c = s[i]
        if not c['alive']: continue
        enemies3 = sum(1 for e in s.values() if e['team'] != usi and e['alive'] and cheb((e['x'], e['y']), (c['x'], c['y'])) <= 3)
        allies4 = sum(1 for e in s.values() if e['team'] == usi and e['alive'] and e['i'] != i and cheb((e['x'], e['y']), (c['x'], c['y'])) <= 4)
        campkill = killer is None
        recalling = any(r - 5 <= x < r for x in g.recall_start[i])
        # hp 6 rounds before death and whether it moved away
        k = g.ridx[r]
        back = g.order[max(0, k-6)]
        hp6 = round(100 * g.rounds[back][i]['hp'] / g.rounds[back][i]['mhp']) if g.rounds[back][i]['alive'] else None
        dsp = g.dspawn[usi][c['y']][c['x']]
        DEATH[t].append(dict(ty=g.types[i][1], enemies3=enemies3, allies4=allies4, campkill=campkill, recalling=recalling, hp6=hp6, dsp=dsp, gems=c['gems'], map=g.map, match=g.match, r=r, killer=g.types[killer][1] if killer is not None else 'camp'))

print('# victim state when WE land the first hit (all fights / real fights) vs baseline enemy champion-rounds in our vision')
for t in ('mite', 'uni'):
    v = VH[t]; b = BASE[t]; vr = [x for x in v if x['real']]
    print(t, 'n', len(v), 'victim hp% med', med([x['hpp'] for x in v]), 'victim <50%', pct(sum(1 for x in v if x['hpp'] < 50), len(v)), '<30%', pct(sum(1 for x in v if x['hpp'] < 30), len(v)), '| busy with camp', pct(sum(1 for x in v if x['busy']), len(v)), '| recalling', pct(sum(1 for x in v if x['recalling']), len(v)), '| victim alone (no ally within 4)', pct(sum(1 for x in v if x['alone']), len(v)))
    print('   baseline (enemy champ-rounds within 8 of us): busy', pct(b['busy'], b['n']), '<50%', pct(b['low50'], b['n']), '<30%', pct(b['low30'], b['n']), 'alone', pct(b['alone'], b['n']))
    for cond, name in ((lambda x: x['busy'], 'victim busy'), (lambda x: x['hpp'] < 50, 'victim<50%'), (lambda x: x['alone'], 'victim alone'), (lambda x: not x['alone'] and x['hpp'] >= 50 and not x['busy'], 'none of these')):
        g_ = [x for x in vr if cond(x)]
        if g_: print('   real fights with %s: n %d K/D %.2f/%.2f' % (name, len(g_), sum(x['kills'] for x in g_)/len(g_), sum(x['deaths'] for x in g_)/len(g_)))
    print('   opener type:', collections.Counter(x['aty'] for x in v).most_common(6), 'victim type:', collections.Counter(x['vty'] for x in v).most_common(6))
print('\n# opener movement pattern (attacker moves in rounds r0-3,r0-2,r0-1,r0: m=moved .=stood), by class')
for t in ('mite', 'uni'):
    for c in ('caster', 'melee', 'ranged'):
        n = OPEN[t][(c, '_n')]
        if not n: continue
        pats = sorted(((k[1], v) for k, v in OPEN[t].items() if k[0] == c and not k[1].startswith('_') and k[1] != 'victim_walked_in'), key=lambda x: -x[1])[:6]
        stood_last = sum(v for k, v in OPEN[t].items() if k[0] == c and not k[1].startswith('_') and k[1] != 'victim_walked_in' and k[1].endswith('..'))
        print(t, c, 'n', n, 'patterns', ' '.join('%s:%s' % (p, pct(v, n)) for p, v in pats), '| stood still in r0-1 and r0:', pct(stood_last, n), '| victim stepped toward attacker in r0-1:', pct(OPEN[t][(c, 'victim_walked_in')], n))
print('\n# local numbers (within 5 of the first hit) per map: our n - their n at first hit; share we hit first when ahead/even/behind (all fights)')
for t in ('mite', 'uni'):
    for mp, xs in sorted(NUM[t].items()):
        ahead = [x for x in xs if x[0] > 0]; even = [x for x in xs if x[0] == 0]; behind = [x for x in xs if x[0] < 0]
        print(t, '%-10s' % mp, 'n', len(xs), 'ahead %s (hit first %s)' % (pct(len(ahead), len(xs)), pct(sum(1 for x in ahead if x[1]), len(ahead))), 'even %s (%s)' % (pct(len(even), len(xs)), pct(sum(1 for x in even if x[1]), len(even))), 'behind %s (%s)' % (pct(len(behind), len(xs)), pct(sum(1 for x in behind if x[1]), len(behind))))
print('\n# death context (our deaths): enemies within 3, allies within 4, hp% 6 rounds earlier, recalling, dist to own spawn, carrying gems')
for t in ('mite', 'uni'):
    d = DEATH[t]; n = len(d)
    print(t, 'deaths', n, 'camp kills', pct(sum(1 for x in d if x['campkill']), n), 'enemies within 3 med', med([x['enemies3'] for x in d]), '>=2 enemies', pct(sum(1 for x in d if x['enemies3'] >= 2), n), 'no ally within 4', pct(sum(1 for x in d if x['allies4'] == 0), n), 'hp% 6 rounds before med', med([x['hp6'] for x in d if x['hp6'] is not None]), 'was >=50% 6 rounds before', pct(sum(1 for x in d if x['hp6'] is not None and x['hp6'] >= 50), n), 'recalling', pct(sum(1 for x in d if x['recalling']), n), 'dist spawn med', med([x['dsp'] for x in d]), 'carrying gems', pct(sum(1 for x in d if x['gems'] > 0), n), 'gems lost total', sum(x['gems'] for x in d))
    print('   by type:', collections.Counter(x['ty'] for x in d).most_common(), ' killer:', collections.Counter(x['killer'] for x in d).most_common(5))
print('\n# win/loss per map')
for k, v in sorted(WL.items()): print(k, 'W-L %d-%d' % tuple(v))
print('\n# examples')
for k, v in EX.items():
    print(k)
    for x in v: print('   ', x)

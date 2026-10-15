"""Aggregate fights.json for our bot (v35) vs opponents in the same games. Prints markdown tables."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_fights')
from common import *
F = json.load(open(FIGHTS))
SEL = selected()
NG = len(set(f['match'] for f in F)); NGAMES = len(SEL)
def us(f): return f['sides'][str(f['us'])]
def them(f): return f['sides'][str(1-f['us'])]
def side(f, who): return us(f) if who == 'us' else them(f)
def real(f): return us(f)['dmg'] + them(f)['dmg'] >= 1000 or us(f)['deaths'] or them(f)['deaths']
def pct(a, b): return '%d%%' % round(100*a/b) if b else '-'
def mean(x): return round(st.mean(x), 2) if x else None
def med(x): return st.median(x) if x else None
def q(x, p):
    x = sorted(x); return x[int(p*(len(x)-1))] if x else None
def we_first(f): return f['first']['at'] == f['us']
def tier(f): return 'top10' if f['orank'] <= 10 else 'r11-30'
MAPS = ['collision', 'corners', 'elkring', 'expanse', 'interlock', 'lanes', 'monolith', 'packs', 'rows']
games_by = collections.defaultdict(set)
for r in SEL:
    games_by['ALL'].add(r['match']); games_by[r['map']].add(r['match']); games_by[r['res']].add(r['match']); games_by['top10' if r['orank'] <= 10 else 'r11-30'].add(r['match'])
    games_by[(r['map'], r['res'])].add(r['match'])
WL = collections.Counter((r['map'], r['res']) for r in SEL)

def splits():
    yield 'ALL', F
    for mp in MAPS: yield mp, [f for f in F if f['map'] == mp]
    for res in ('win', 'loss'): yield res, [f for f in F if f['res'] == res]
    for t in ('top10', 'r11-30'): yield t, [f for f in F if tier(f) == t]

print('# 1. Fights per game and who starts them (all fights | real = >=1000 dmg or a death)')
print('| split | games (W-L) | fights | per game | real | real/game | we hit first (all) | we hit first (real) | our kills | our deaths | K/D per real fight | dmg dealt / taken per real fight | our dmg share | gems we lost / won in fights |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for name, fs in splits():
    n = len(games_by[name]); rf = [f for f in fs if real(f)]
    if not fs: print('| %s | %d | 0 | | | | | | | | | | | |' % (name, n)); continue
    k = sum(us(f)['kills'] for f in rf); d = sum(len(us(f)['deaths']) for f in rf)
    dd = sum(us(f)['dmg'] for f in rf); dt = sum(them(f)['dmg'] for f in rf)
    wl = '%d-%d' % (sum(1 for r in SEL if r['match'] in games_by[name] and r['res'] == 'win'), sum(1 for r in SEL if r['match'] in games_by[name] and r['res'] == 'loss'))
    print('| %s | %d (%s) | %d | %.1f | %d | %.1f | %s | %s | %d | %d | %.2f / %.2f | %d / %d | %s | %d / %d |' % (name, n, wl, len(fs), len(fs)/n, len(rf), len(rf)/n, pct(sum(1 for f in fs if we_first(f)), len(fs)), pct(sum(1 for f in rf if we_first(f)), len(rf)), k, d, k/max(1, len(rf)), d/max(1, len(rf)), dd/max(1, len(rf)), dt/max(1, len(rf)), pct(sum(us(f)['dmg'] for f in fs), sum(us(f)['dmg']+them(f)['dmg'] for f in fs)), sum(us(f)['gems_lost'] for f in fs), sum(us(f)['gems_won'] for f in fs)))

print('\n# 1b. The first hit: who, with what, from how far, when (all fights; opener side = us or them)')
print('| opener | n | spell | basic | dist 1 | dist 2 | dist 3 | dist 4 | dist 5+ | round p25/med/p75 | our n within 6 (mean) | their n within 6 | victim hp% med | victim <50% | victim: walking / farming / idle / recalling / tributing / fighting |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for who in ('us', 'them'):
    fs = [f for f in F if we_first(f) == (who == 'us')]
    n = len(fs)
    dist = collections.Counter(min(f['first']['dist'], 5) for f in fs)
    va = collections.Counter(f['first']['vact'] for f in fs)
    vh = [f['first']['vhpp'] for f in fs if f['first']['vhpp'] is not None]
    print('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s/%s/%s | %.2f | %.2f | %s | %s | %s |' % (who, n, pct(sum(1 for f in fs if f['first']['kind'] == 'spell'), n), pct(sum(1 for f in fs if f['first']['kind'] == 'atk'), n),
          pct(dist[1], n), pct(dist[2], n), pct(dist[3], n), pct(dist[4], n), pct(dist[5], n), q([f['r0'] for f in fs], .25), med([f['r0'] for f in fs]), q([f['r0'] for f in fs], .75),
          mean([us(f)['n6'] for f in fs]), mean([them(f)['n6'] for f in fs]), med(vh), pct(sum(1 for x in vh if x < 50), len(vh)),
          ' / '.join(pct(va[k], n) for k in ('walking', 'farming', 'idle', 'recalling', 'tributing', 'fighting'))))
print('\nOpener champion (type, kind, dist) when WE open:', collections.Counter((f['first']['aty'], f['first']['kind'], f['first']['dist']) for f in F if we_first(f)).most_common(12))
print('Opener champion when THEY open:', collections.Counter((f['first']['aty'], f['first']['kind'], f['first']['dist']) for f in F if not we_first(f)).most_common(12))
print('Victim type when WE open:', collections.Counter(f['first']['vty'] for f in F if we_first(f)).most_common(8))
print('Victim type when THEY open (our champion hit first):', collections.Counter(f['first']['vty'] for f in F if not we_first(f)).most_common(8))
print('Attacker activity (what the opener was doing 1 round before) when WE open:', collections.Counter(f['first']['aact'] for f in F if we_first(f)).most_common())
print('Attacker activity when THEY open:', collections.Counter(f['first']['aact'] for f in F if not we_first(f)).most_common())

print('\n# 1c. Outcome by who started (real fights), with splits')
print('| split | who started | n | our kills | our deaths | K/D per fight | gems we lost | gems we won | our dmg / their dmg per fight | we won the fight (kills>deaths) | we lost it | even |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for name, fs in splits():
    for who in ('us', 'them'):
        g_ = [f for f in fs if real(f) and we_first(f) == (who == 'us')]
        if not g_: continue
        k = sum(us(f)['kills'] for f in g_); d = sum(len(us(f)['deaths']) for f in g_)
        won = sum(1 for f in g_ if us(f)['kills'] > len(us(f)['deaths'])); lost = sum(1 for f in g_ if us(f)['kills'] < len(us(f)['deaths']))
        print('| %s | %s | %d | %d | %d | %.2f / %.2f | %d | %d | %d / %d | %s | %s | %s |' % (name, who, len(g_), k, d, k/len(g_), d/len(g_), sum(us(f)['gems_lost'] for f in g_), sum(us(f)['gems_won'] for f in g_), sum(us(f)['dmg'] for f in g_)/len(g_), sum(them(f)['dmg'] for f in g_)/len(g_), pct(won, len(g_)), pct(lost, len(g_)), pct(len(g_)-won-lost, len(g_))))

print('\n# 1d. Outcome by victim activity at the first hit (real fights)')
print('| opener | victim activity | n | opener side kills | opener side deaths |')
print('|---|---|---|---|---|')
for who in ('us', 'them'):
    byact = collections.defaultdict(list)
    for f in F:
        if real(f) and we_first(f) == (who == 'us'): byact[f['first']['vact']].append(f)
    for act, g_ in sorted(byact.items(), key=lambda x: -len(x[1])):
        sd = side(g_[0], who)
        print('| %s | %s | %d | %.2f | %.2f |' % (who, act, len(g_), sum(side(f, who)['kills'] for f in g_)/len(g_), sum(len(side(f, who)['deaths']) for f in g_)/len(g_)))

print('\n# 2. When WE start: deliberate approach or collision?')
print('deliberate = our opener moved toward the victim in >= 3 consecutive rounds before the hit; collision/they-came = victim closed more distance than the opener over the last 4 rounds;')
print('collision/farming = our opener was hitting or being hit by a camp in the 4 rounds before; other = neither (standing / short approach).')
print('| split | n (we open, with approach data) | deliberate | they came to us | we were farming | other | opener stood still in the 4 rounds | victim stepped in |')
print('|---|---|---|---|---|---|---|---|')
def cat(f):
    a = f['approach']
    if a['closing'] >= 3: return 'deliberate'
    if a['a_farm'] >= 2: return 'farming'
    if a['v_closed'] > a['a_closed']: return 'theycame'
    return 'other'
for name, fs in splits():
    g_ = [f for f in fs if we_first(f) and f.get('approach')]
    if not g_: continue
    c = collections.Counter(cat(f) for f in g_)
    print('| %s | %d | %s | %s | %s | %s | %s | %s |' % (name, len(g_), pct(c['deliberate'], len(g_)), pct(c['theycame'], len(g_)), pct(c['farming'], len(g_)), pct(c['other'], len(g_)), pct(sum(1 for f in g_ if f['approach']['a_moved'] == 0), len(g_)), pct(sum(1 for f in g_ if f['approach']['v_closed'] > 0), len(g_))))
print('\nSame for THEIR openers (how the opponents start on us):')
print('| split | n | deliberate | we walked into them | they were farming | other | opener stood still |')
print('|---|---|---|---|---|---|---|')
for name, fs in splits():
    g_ = [f for f in fs if not we_first(f) and f.get('approach')]
    if not g_: continue
    c = collections.Counter(cat(f) for f in g_)
    print('| %s | %d | %s | %s | %s | %s | %s |' % (name, len(g_), pct(c['deliberate'], len(g_)), pct(c['theycame'], len(g_)), pct(c['farming'], len(g_)), pct(c['other'], len(g_)), pct(sum(1 for f in g_ if f['approach']['a_moved'] == 0), len(g_))))
print('\nClosing rounds of our opener (consecutive rounds walking toward the victim):', sorted(collections.Counter(min(f['approach']['closing'], 7) for f in F if we_first(f) and f.get('approach')).items()))
print('Closing rounds of their opener:', sorted(collections.Counter(min(f['approach']['closing'], 7) for f in F if not we_first(f) and f.get('approach')).items()))

print('\n# 2b. Numbers and hp at the first hit (real fights), split by who opened and by approach category')
print('| who opened | category | n | our n6 vs their n6 (mean) | we outnumber / equal / outnumbered (within 6) | our hp% / their hp% (med) | we healthier (+5) | our K/D | gems lost/won |')
print('|---|---|---|---|---|---|---|---|---|')
for who in ('us', 'them'):
    groups = [('all', [f for f in F if real(f) and we_first(f) == (who == 'us')])]
    bc = collections.defaultdict(list)
    for f in groups[0][1]:
        if f.get('approach'): bc[cat(f)].append(f)
    groups += sorted(bc.items(), key=lambda x: -len(x[1]))
    for cname, g_ in groups:
        if not g_: continue
        out = sum(1 for f in g_ if us(f)['n6'] > them(f)['n6']); eq = sum(1 for f in g_ if us(f)['n6'] == them(f)['n6'])
        print('| %s | %s | %d | %.2f vs %.2f | %s / %s / %s | %s / %s | %s | %.2f / %.2f | %d / %d |' % (who, cname, len(g_), mean([us(f)['n6'] for f in g_]), mean([them(f)['n6'] for f in g_]), pct(out, len(g_)), pct(eq, len(g_)), pct(len(g_)-out-eq, len(g_)),
              med([us(f)['hpp'] for f in g_]), med([them(f)['hpp'] for f in g_]), pct(sum(1 for f in g_ if us(f)['hpp'] > them(f)['hpp'] + 5), len(g_)), sum(us(f)['kills'] for f in g_)/len(g_), sum(len(us(f)['deaths']) for f in g_)/len(g_), sum(us(f)['gems_lost'] for f in g_), sum(us(f)['gems_won'] for f in g_)))
print('\nOur openers by local numbers (within 6) in ALL fights: share we open when ahead / even / behind')
for name, fs in splits():
    ah = [f for f in fs if us(f)['n6'] > them(f)['n6']]; ev = [f for f in fs if us(f)['n6'] == them(f)['n6']]; be = [f for f in fs if us(f)['n6'] < them(f)['n6']]
    if fs: print('  %-9s n %d: ahead %s (we open %s), even %s (%s), behind %s (%s)' % (name, len(fs), pct(len(ah), len(fs)), pct(sum(1 for f in ah if we_first(f)), len(ah)), pct(len(ev), len(fs)), pct(sum(1 for f in ev if we_first(f)), len(ev)), pct(len(be), len(fs)), pct(sum(1 for f in be if we_first(f)), len(be))))
print('\nOpener hp%% (the champion that lands the first hit): us med %s (<50%%: %s); them med %s (<50%%: %s)' % (med([f['first']['a_hpp'] for f in F if we_first(f) and f['first']['a_hpp'] is not None]), pct(sum(1 for f in F if we_first(f) and f['first']['a_hpp'] is not None and f['first']['a_hpp'] < 50), sum(1 for f in F if we_first(f))), med([f['first']['a_hpp'] for f in F if not we_first(f) and f['first']['a_hpp'] is not None]), pct(sum(1 for f in F if not we_first(f) and f['first']['a_hpp'] is not None and f['first']['a_hpp'] < 50), sum(1 for f in F if not we_first(f)))))
print('Opener with how many allies within 6 (incl. itself) when WE open:', sorted(collections.Counter(us(f)['n6'] for f in F if we_first(f)).items()), ' vs enemies within 6:', sorted(collections.Counter(them(f)['n6'] for f in F if we_first(f)).items()))
print('When THEY open: their n6', sorted(collections.Counter(them(f)['n6'] for f in F if not we_first(f)).items()), ' our n6:', sorted(collections.Counter(us(f)['n6'] for f in F if not we_first(f)).items()))

print('\n# 3. When THEY start: where we were, together or split, gems, vision before the hit')
print('| split | n (they open) | our dist to own spawn med | their dist to their spawn med | fight in our half / middle / their half | we within 3 of altar | our champs within 8 / alive (mean) | split (an ally alive but >8 away) | we carry gems | gems carried (mean, carriers) | contact rounds before hit: 1 / 2-3 / 4-7 / 8+ (med) |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for name, fs in splits():
    g_ = [f for f in fs if not we_first(f)]
    if not g_: continue
    ours = sum(1 for f in g_ if us(f)['dspawn'] is not None and them(f)['dspawn'] is not None and us(f)['dspawn'] < them(f)['dspawn'] - 3)
    theirs = sum(1 for f in g_ if us(f)['dspawn'] is not None and them(f)['dspawn'] is not None and them(f)['dspawn'] < us(f)['dspawn'] - 3)
    vr = [f['vision']['rounds'] for f in g_]
    print('| %s | %d | %s | %s | %s / %s / %s | %s | %.2f / %.2f | %s | %s | %.1f | %s / %s / %s / %s (%s) |' % (name, len(g_), med([us(f)['dspawn'] for f in g_ if us(f)['dspawn'] is not None]), med([them(f)['dspawn'] for f in g_ if them(f)['dspawn'] is not None]), pct(ours, len(g_)), pct(len(g_)-ours-theirs, len(g_)), pct(theirs, len(g_)),
          pct(sum(1 for f in g_ if us(f)['daltar'] is not None and us(f)['daltar'] <= 3), len(g_)), mean([us(f)['n8'] for f in g_]), mean([us(f)['alive_total'] for f in g_]), pct(sum(1 for f in g_ if us(f)['far'] > 0), len(g_)), pct(sum(1 for f in g_ if us(f)['gems'] > 0), len(g_)), mean([us(f)['gems'] for f in g_ if us(f)['gems'] > 0]) or 0,
          pct(sum(1 for x in vr if x <= 1), len(vr)), pct(sum(1 for x in vr if 2 <= x <= 3), len(vr)), pct(sum(1 for x in vr if 4 <= x <= 7), len(vr)), pct(sum(1 for x in vr if x >= 8), len(vr)), med(vr)))
print('\nSame when WE open (where we are when we start):')
print('| split | n (we open) | our dist spawn | their dist spawn | our half / middle / their half | we within 3 of altar | our within 8 / alive | we split | we carry gems | gems mean | contact rounds before our hit: 1 / 2-3 / 4-7 / 8+ (med) |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for name, fs in splits():
    g_ = [f for f in fs if we_first(f)]
    if not g_: continue
    ours = sum(1 for f in g_ if us(f)['dspawn'] is not None and them(f)['dspawn'] is not None and us(f)['dspawn'] < them(f)['dspawn'] - 3)
    theirs = sum(1 for f in g_ if us(f)['dspawn'] is not None and them(f)['dspawn'] is not None and them(f)['dspawn'] < us(f)['dspawn'] - 3)
    vr = [f['vision']['rounds'] for f in g_]
    print('| %s | %d | %s | %s | %s / %s / %s | %s | %.2f / %.2f | %s | %s | %.1f | %s / %s / %s / %s (%s) |' % (name, len(g_), med([us(f)['dspawn'] for f in g_ if us(f)['dspawn'] is not None]), med([them(f)['dspawn'] for f in g_ if them(f)['dspawn'] is not None]), pct(ours, len(g_)), pct(len(g_)-ours-theirs, len(g_)), pct(theirs, len(g_)),
          pct(sum(1 for f in g_ if us(f)['daltar'] is not None and us(f)['daltar'] <= 3), len(g_)), mean([us(f)['n8'] for f in g_]), mean([us(f)['alive_total'] for f in g_]), pct(sum(1 for f in g_ if us(f)['far'] > 0), len(g_)), pct(sum(1 for f in g_ if us(f)['gems'] > 0), len(g_)), mean([us(f)['gems'] for f in g_ if us(f)['gems'] > 0]) or 0,
          pct(sum(1 for x in vr if x <= 1), len(vr)), pct(sum(1 for x in vr if 2 <= x <= 3), len(vr)), pct(sum(1 for x in vr if 4 <= x <= 7), len(vr)), pct(sum(1 for x in vr if x >= 8), len(vr)), med(vr)))

print('\n# 3b. What the victim side did in the contact rounds before the first hit (champion-rounds of the victim team with an enemy within 8, share)')
print('| victim side | contact champion-rounds | farming | idle | moved closer | moved away | sideways | recalling |')
print('|---|---|---|---|---|---|---|---|')
for who, name in (('them', 'us (they open on us)'), ('us', 'opponents (we open on them)')):
    w = collections.Counter()
    for f in F:
        if we_first(f) == (who == 'us'):
            for k, v in f['vision']['what'].items(): w[k] += v
    n = sum(w.values())
    print('| %s | %d | %s | %s | %s | %s | %s | %s |' % (name, n, pct(w['farm'], n), pct(w['idle'], n), pct(w['closer'], n), pct(w['away'], n), pct(w['side'], n), pct(w['recall'], n)))
print('\nDominant reaction per fight (victim side, fights with >= 2 contact rounds before the hit):')
for who, name in (('them', 'us'), ('us', 'opponents')):
    c = collections.Counter()
    for f in F:
        if we_first(f) == (who == 'us') and f['vision']['rounds'] >= 2 and f['vision']['what']:
            c[max(f['vision']['what'].items(), key=lambda x: x[1])[0]] += 1
    n = sum(c.values())
    print('  %s: n %d  ' % (name, n) + ', '.join('%s %s' % (k, pct(v, n)) for k, v in c.most_common()))

print('\n# 4. Focus, target choice, chasing, spells, ranged distance (fight windows, all fights)')
print('| side | rounds with 2+ of the side hitting | same victim | target decisions with 2+ enemies in reach | nearest | lowest hp | caster (when one available) | gem carrier (when one available) | basic attacks | target out of range next round | ... and we stepped after it |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for who in ('us', 'them'):
    T = collections.Counter(); multi = same = atk = left = fol = 0
    for f in F:
        sd = side(f, who)
        multi += sd['focus_multi']; same += sd['focus_same']; atk += sd['atk_n']; left += sd['atk_target_left']; fol += sd['atk_followed']
        for k, v in sd['target'].items(): T[k] += v
    print('| %s | %d | %s | %d | %s | %s | %s (n=%d) | %s (n=%d) | %d | %s | %s |' % (who, multi, pct(same, multi), T['n'], pct(T['nearest'], T['n']), pct(T['lowest'], T['n']), pct(T['caster'], T['caster_avail']), T['caster_avail'], pct(T['carrier'], T['carrier_avail']), T['carrier_avail'], atk, pct(left, atk), pct(fol, left)))
print('\nSpells:')
print('| side | real fights | cast within 2 rounds of first hit | casts per real fight (participants) | champion-rounds with enemy <=4 and both slots up | cast | walked instead | spell share of champion damage |')
print('|---|---|---|---|---|---|---|---|')
for who in ('us', 'them'):
    rf = [f for f in F if real(f)]
    early = sum(1 for f in rf if side(f, who)['cast_early']); casts = sum(side(f, who)['casts'] for f in rf)
    on = sum(side(f, who)['opp_n'] for f in F); oc = sum(side(f, who)['opp_cast'] for f in F); om = sum(side(f, who)['opp_moved'] for f in F)
    print('| %s | %d | %s | %.2f | %d | %s | %s | %s |' % (who, len(rf), pct(early, len(rf)), casts/len(rf), on, pct(oc, on), pct(om, on), pct(sum(side(f, who)['dmg_spell'] for f in F), sum(side(f, who)['dmg'] for f in F))))
print('\nSpell timing of the side that did NOT open (real fights): cast within 2 rounds of the first hit, by tier/result')
for name, fs in splits():
    rf = [f for f in fs if real(f)]
    if not rf: continue
    a = [f for f in rf if not we_first(f)]; b = [f for f in rf if we_first(f)]
    print('  %-9s us (they opened): %s of %d | them (we opened): %s of %d | both-slots-up usage us %s them %s | focus same-victim us %s them %s' % (name, pct(sum(1 for f in a if us(f)['cast_early']), len(a)), len(a), pct(sum(1 for f in b if them(f)['cast_early']), len(b)), len(b),
          pct(sum(us(f)['opp_cast'] for f in fs), sum(us(f)['opp_n'] for f in fs)), pct(sum(them(f)['opp_cast'] for f in fs), sum(them(f)['opp_n'] for f in fs)), pct(sum(us(f)['focus_same'] for f in fs), sum(us(f)['focus_multi'] for f in fs)), pct(sum(them(f)['focus_same'] for f in fs), sum(them(f)['focus_multi'] for f in fs))))
print('Game totals: our tributed gems %d, theirs %d; gems lost by death in fights: us %d, them %d' % (sum(r['score'] for r in SEL), sum(r['oscore'] for r in SEL), sum(us(f)['gems_lost'] for f in F), sum(them(f)['gems_lost'] for f in F)))
print('\nRanged/caster champions: distance of their hits on champions (basic attacks and spells), and share of fight rounds spent at distance <= 2 from an enemy')
print('| side | basic d1 | d2 | d3 | spell d1 | d2 | d3 | d4 | d5+ | ranged champion fight-rounds | at distance <= 2 |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for who in ('us', 'them'):
    rd = collections.Counter(); rr = adj = 0
    for f in F:
        sd = side(f, who)
        for k, v in sd['ranged_dist'].items(): rd[k] += v
        rr += sd['ranged_rounds']; adj += sd['ranged_adj']
    na = sum(v for k, v in rd.items() if k.startswith('atk')); ns = sum(v for k, v in rd.items() if k.startswith('spell'))
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %d | %s |' % (who, pct(rd['atk1'], na), pct(rd['atk2'], na), pct(rd['atk3'], na), pct(rd['spell1'], ns), pct(rd['spell2'], ns), pct(rd['spell3'], ns), pct(rd['spell4'], ns), pct(rd['spell5']+rd['spell6'], ns), rr, pct(adj, rr)))
    print('   raw:', dict(rd))

print('\n# 5. Fight length and how fights end')
print('| split | fights | real | length (first-last hit) med / p75 | single-poke (1 round) | >= 10 rounds | contact rounds to separation med | end: kill | wipe | recall | leave | we leave first | they leave first | same round |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for name, fs in splits():
    if not fs: continue
    L = [f['length'] for f in fs]; C = [f['length_contact'] for f in fs if f['length_contact'] is not None]
    e = collections.Counter(f['end']['kind'] for f in fs)
    lv = collections.Counter('both' if f['end']['leaver'] == 'both' else 'us' if f['end']['leaver'] == f['us'] else ('them' if f['end']['leaver'] is not None else None) for f in fs)
    print('| %s | %d | %d | %s / %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (name, len(fs), sum(1 for f in fs if real(f)), med(L), q(L, .75), pct(sum(1 for x in L if x == 1), len(L)), pct(sum(1 for x in L if x >= 10), len(L)), med(C), pct(e['kill'], len(fs)), pct(e['wipe'], len(fs)), pct(e['recall'], len(fs)), pct(e['leave'], len(fs)), pct(lv['us'], len(fs)), pct(lv['them'], len(fs)), pct(lv['both'], len(fs))))
print('\nReal fights only: who leaves first vs who opened, and outcome')
for who in ('us', 'them'):
    g_ = [f for f in F if real(f) and we_first(f) == (who == 'us')]
    lv = collections.Counter('both' if f['end']['leaver'] == 'both' else 'us' if f['end']['leaver'] == f['us'] else ('them' if f['end']['leaver'] is not None else 'none') for f in g_)
    e = collections.Counter(f['end']['kind'] for f in g_)
    wipe_us = sum(1 for f in g_ if f['us'] in f['end']['wipe']); wipe_them = sum(1 for f in g_ if (1-f['us']) in f['end']['wipe'])
    print('  opened by %s: n %d, we leave first %s, they leave first %s, same round %s; ends: kill %s wipe %s (we wiped %d, they wiped %d) recall %s leave %s' % (who, len(g_), pct(lv['us'], len(g_)), pct(lv['them'], len(g_)), pct(lv['both'], len(g_)), pct(e['kill'], len(g_)), pct(e['wipe'], len(g_)), wipe_us, wipe_them, pct(e['recall'], len(g_)), pct(e['leave'], len(g_))))
print('Leave kind by side (all fights where a leaver was found): ', end='')
for who in ('us', 'them'):
    g_ = [f for f in F if f['end']['leaver'] is not None and f['end']['leaver'] != 'both' and ((f['end']['leaver'] == f['us']) == (who == 'us'))]
    print('%s: n %d walk %s recall %s; ' % (who, len(g_), pct(sum(1 for f in g_ if f['end']['leave_kind'] == 'walk'), len(g_)), pct(sum(1 for f in g_ if f['end']['leave_kind'] == 'recall'), len(g_))), end='')
print()
print('Recall started by a participant between the last hit and separation: us %d fights, them %d fights (of %d)' % (sum(1 for f in F if f['us'] in f['end']['recall_sides']), sum(1 for f in F if (1-f['us']) in f['end']['recall_sides']), len(F)))

print('\n# 6. Per opponent (real fights)')
print('| opponent (rank) | games (W-L) | real fights | we hit first | our kills | our deaths | gems lost / won |')
print('|---|---|---|---|---|---|---|')
byopp = collections.defaultdict(list)
for f in F:
    if real(f): byopp[(f['opp'], f['orank'])].append(f)
for (opp, rk), fs in sorted(byopp.items(), key=lambda x: x[0][1]):
    w = sum(1 for r in SEL if r['opp'] == opp and r['res'] == 'win'); l = sum(1 for r in SEL if r['opp'] == opp and r['res'] == 'loss')
    print('| %s (%d) | %d-%d | %d | %s | %d | %d | %d / %d |' % (opp, rk, w, l, len(fs), pct(sum(1 for f in fs if we_first(f)), len(fs)), sum(us(f)['kills'] for f in fs), sum(len(us(f)['deaths']) for f in fs), sum(us(f)['gems_lost'] for f in fs), sum(us(f)['gems_won'] for f in fs)))

print('\n# 7. Examples')
def ex(f, note=''):
    return '%s %s r%d-%d vs %s: %s %s %s d%d on %s (%s, hp %s%%, %d gems) | us %s hp%d%% n6 %d, them %s hp%d%% n6 %d | K/D %d/%d gems -%d/+%d | end %s leaver %s %s' % (f['map'], f['match'][:8], f['r0'], f['r1'], f['opp'][:18], 'WE' if we_first(f) else 'THEY', f['first']['aty'], f['first']['kind'], f['first']['dist'], f['first']['vty'], f['first']['vact'], f['first']['vhpp'], f['first']['vgems'], us(f)['types'], us(f)['hpp'], us(f)['n6'], them(f)['types'], them(f)['hpp'], them(f)['n6'], us(f)['kills'], len(us(f)['deaths']), us(f)['gems_lost'], us(f)['gems_won'], f['end']['kind'], 'both' if f['end']['leaver'] == 'both' else 'us' if f['end']['leaver'] == f['us'] else ('them' if f['end']['leaver'] is not None else '-'), note)
print('## we open, deliberate approach, won')
for f in [f for f in F if we_first(f) and real(f) and f.get('approach') and cat(f) == 'deliberate' and us(f)['kills'] > len(us(f)['deaths'])][:4]: print(' -', ex(f))
print('## we open, deliberate approach, lost')
for f in [f for f in F if we_first(f) and real(f) and f.get('approach') and cat(f) == 'deliberate' and us(f)['kills'] < len(us(f)['deaths'])][:4]: print(' -', ex(f))
print('## we open while outnumbered within 6')
for f in [f for f in F if we_first(f) and real(f) and us(f)['n6'] < them(f)['n6']][:4]: print(' -', ex(f))
print('## they open on us while we farm')
for f in [f for f in F if not we_first(f) and real(f) and f['first']['vact'] == 'farming'][:4]: print(' -', ex(f))
print('## they open on us while we tribute / recall')
for f in [f for f in F if not we_first(f) and real(f) and f['first']['vact'] in ('tributing', 'recalling')][:4]: print(' -', ex(f))
print('## they open after >= 6 rounds of contact (we saw them and kept doing what we did)')
for f in sorted([f for f in F if not we_first(f) and real(f) and f['vision']['rounds'] >= 6 and f['vision']['rounds'] < 39], key=lambda f: -len(us(f)['deaths']))[:4]: print(' -', ex(f, 'contact %d rounds, we did %s' % (f['vision']['rounds'], f['vision']['what'])))
print('## biggest fights (damage)')
for f in sorted(F, key=lambda f: -(us(f)['dmg'] + them(f)['dmg']))[:6]: print(' -', ex(f, 'dmg %d/%d' % (us(f)['dmg'], them(f)['dmg'])))
print('## we lost gems (largest)')
for f in sorted(F, key=lambda f: -us(f)['gems_lost'])[:6]: print(' -', ex(f))
print('## we won gems (largest)')
for f in sorted(F, key=lambda f: -us(f)['gems_won'])[:4]: print(' -', ex(f))
print('## long fights')
for f in sorted(F, key=lambda f: -f['length'])[:4]: print(' -', ex(f, 'len %d' % f['length']))

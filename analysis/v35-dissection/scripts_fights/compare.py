"""Side-by-side fight metrics for two batches (study27 = ws3 vs study26 = ws2) plus the opponents' numbers in the study27 games.
Usage: python3 -I compare.py  (paths below; needs fights_27.json / fights.json and the DUMP files of chase.py / extra.py for both batches)
Each cell carries the count it is based on so differences can be judged against the sample.
"""
import json, collections, statistics as st, math
S = '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
D = S + '/ws2/scripts_fights/'
B = {
    's27': dict(F=json.load(open(D + 'fights_27.json')), SEL=json.load(open(S + '/ws3/selected.json')), CH=json.load(open(D + 'dump_chase_27.json')), EX=json.load(open(D + 'dump_extra_27.json'))),
    's26': dict(F=json.load(open(D + 'fights.json')), SEL=json.load(open(S + '/ws2/selected.json')), CH=json.load(open(D + 'dump_chase_26.json')), EX=json.load(open(D + 'dump_extra_26.json'))),
}
def us(f): return f['sides'][str(f['us'])]
def them(f): return f['sides'][str(1-f['us'])]
def side(f, who): return us(f) if who == 'us' else them(f)
def real(f): return us(f)['dmg'] + them(f)['dmg'] >= 1000 or us(f)['deaths'] or them(f)['deaths']
def we_first(f): return f['first']['at'] == f['us']
def opened_by(f, who): return we_first(f) == (who == 'us')
def pct(a, b, n=True): return ('%d%% (%d/%d)' % (round(100*a/b), a, b) if n else '%d%%' % round(100*a/b)) if b else '-'
def med(x): return st.median(x) if x else None
def mean(x): return round(st.mean(x), 2) if x else None
def q(x, p):
    x = sorted(x); return x[int(p*(len(x)-1))] if x else None
MAPS = ['collision', 'corners', 'elkring', 'expanse', 'interlock', 'lanes', 'monolith', 'packs', 'rows']
# columns: (label, batch, who)
COLS = [('study27 us', 's27', 'us'), ('study26 us', 's26', 'us'), ('study27 opponents', 's27', 'them'), ('study26 opponents', 's26', 'them')]

def table(title, rows):
    print('\n### ' + title)
    print('| metric | ' + ' | '.join(c[0] for c in COLS) + ' |')
    print('|---|' + '---|' * len(COLS))
    for name, fn in rows:
        cells = []
        for lab, b, who in COLS:
            try: cells.append(str(fn(B[b], who)))
            except Exception as e: cells.append('err %s' % e)
        print('| %s | %s |' % (name, ' | '.join(cells)))

def ngames(b): return len(b['SEL'])
def wl(b): return '%d-%d' % (sum(1 for r in b['SEL'] if r['res'] == 'win'), sum(1 for r in b['SEL'] if r['res'] == 'loss'))
def RF(b): return [f for f in b['F'] if real(f)]

# ---------- 1. volume, who opens, conversion
rows = [
 ('games (W-L)', lambda b, w: '%d (%s)' % (ngames(b), wl(b)) if w == 'us' else 'same games'),
 ('games with any fight', lambda b, w: '%d' % len(set(f['match'] for f in b['F']))),
 ('fights / real fights', lambda b, w: '%d / %d' % (len(b['F']), len(RF(b)))),
 ('fights per game / real per game', lambda b, w: '%.1f / %.1f' % (len(b['F'])/ngames(b), len(RF(b))/ngames(b))),
 ('hit first (all fights)', lambda b, w: pct(sum(1 for f in b['F'] if opened_by(f, w)), len(b['F']))),
 ('hit first (real fights)', lambda b, w: pct(sum(1 for f in RF(b) if opened_by(f, w)), len(RF(b)))),
 ('kills / deaths per real fight', lambda b, w: '%.2f / %.2f (%d / %d in %d)' % (sum(side(f, w)['kills'] for f in RF(b))/len(RF(b)), sum(len(side(f, w)['deaths']) for f in RF(b))/len(RF(b)), sum(side(f, w)['kills'] for f in RF(b)), sum(len(side(f, w)['deaths']) for f in RF(b)), len(RF(b)))),
 ('damage dealt / taken per real fight', lambda b, w: '%d / %d' % (sum(side(f, w)['dmg'] for f in RF(b))/len(RF(b)), sum(side(f, 'them' if w == 'us' else 'us')['dmg'] for f in RF(b))/len(RF(b)))),
 ('share of fight damage', lambda b, w: pct(sum(side(f, w)['dmg'] for f in b['F']), sum(us(f)['dmg'] + them(f)['dmg'] for f in b['F']), False)),
 ('gems lost / won in fights', lambda b, w: '%d / %d' % (sum(side(f, w)['gems_lost'] for f in b['F']), sum(side(f, w)['gems_won'] for f in b['F']))),
 ('gems tributed (game totals)', lambda b, w: '%d' % sum(r['score'] if w == 'us' else r['oscore'] for r in b['SEL'])),
]
table('1. Fights per game, who opens, outcome', rows)

def conv(b, w, opener):
    g = [f for f in RF(b) if opened_by(f, opener)]
    k = sum(side(f, w)['kills'] for f in g); d = sum(len(side(f, w)['deaths']) for f in g)
    won = sum(1 for f in g if side(f, w)['kills'] > len(side(f, w)['deaths'])); lost = sum(1 for f in g if side(f, w)['kills'] < len(side(f, w)['deaths']))
    return '%.2f / %.2f (n=%d; %d-%d; won %d%% lost %d%%)' % (k/len(g), d/len(g), len(g), k, d, 100*won/len(g), 100*lost/len(g)) if g else '-'
rows = [
 ('fights this side opened: kills / deaths per fight', lambda b, w: conv(b, w, w)),
 ('fights the other side opened: kills / deaths', lambda b, w: conv(b, w, 'them' if w == 'us' else 'us')),
 ('gems lost / won in fights this side opened', lambda b, w: '%d / %d' % (sum(side(f, w)['gems_lost'] for f in RF(b) if opened_by(f, w)), sum(side(f, w)['gems_won'] for f in RF(b) if opened_by(f, w)))),
 ('gems lost / won in fights the other side opened', lambda b, w: '%d / %d' % (sum(side(f, w)['gems_lost'] for f in RF(b) if not opened_by(f, w)), sum(side(f, w)['gems_won'] for f in RF(b) if not opened_by(f, w)))),
 ('dmg dealt / taken per fight this side opened', lambda b, w: '%d / %d' % (sum(side(f, w)['dmg'] for f in RF(b) if opened_by(f, w))/max(1, sum(1 for f in RF(b) if opened_by(f, w))), sum(side(f, 'them' if w == 'us' else 'us')['dmg'] for f in RF(b) if opened_by(f, w))/max(1, sum(1 for f in RF(b) if opened_by(f, w))))),
]
table('1c. Opener conversion (real fights)', rows)

def byact(b, w, act):
    g = [f for f in RF(b) if opened_by(f, w) and f['first']['vact'] == act]
    return '%.2f / %.2f (n=%d)' % (sum(side(f, w)['kills'] for f in g)/len(g), sum(len(side(f, w)['deaths']) for f in g)/len(g), len(g)) if g else '-'
rows = [('opener on a %s victim: kills / deaths' % a, (lambda a: lambda b, w: byact(b, w, a))(a)) for a in ('walking', 'idle', 'farming', 'recalling', 'tributing')]
table('1d. Opener-side outcome by what the victim was doing (real fights)', rows)

# ---------- 1b. the first hit
def openers(b, w): return [f for f in b['F'] if opened_by(f, w)]
def dist_share(b, w, d):
    g = openers(b, w); return pct(sum(1 for f in g if min(f['first']['dist'], 5) == d), len(g))
rows = [
 ('openers (n)', lambda b, w: len(openers(b, w))),
 ('opener is a spell', lambda b, w: pct(sum(1 for f in openers(b, w) if f['first']['kind'] == 'spell'), len(openers(b, w)))),
 ('opener distance 1 / 2 / 3 / 4 / 5+', lambda b, w: ' / '.join(pct(sum(1 for f in openers(b, w) if min(f['first']['dist'], 5) == d), len(openers(b, w)), False) for d in (1, 2, 3, 4, 5))),
 ('opener round p25 / med / p75', lambda b, w: '%s / %s / %s' % (q([f['r0'] for f in openers(b, w)], .25), med([f['r0'] for f in openers(b, w)]), q([f['r0'] for f in openers(b, w)], .75))),
 ('opener hp% med / <50%', lambda b, w: '%s / %s' % (med([f['first']['a_hpp'] for f in openers(b, w) if f['first']['a_hpp'] is not None]), pct(sum(1 for f in openers(b, w) if f['first']['a_hpp'] is not None and f['first']['a_hpp'] < 50), len(openers(b, w))))),
 ('victim hp% med / <50%', lambda b, w: '%s / %s' % (med([f['first']['vhpp'] for f in openers(b, w) if f['first']['vhpp'] is not None]), pct(sum(1 for f in openers(b, w) if f['first']['vhpp'] is not None and f['first']['vhpp'] < 50), len(openers(b, w))))),
 ('victim isolated (no ally within 4) / baseline', lambda b, w: '%s / %s' % (pct(b['EX']['ISO'][w]['alone'], b['EX']['ISO'][w]['n']), pct(b['EX']['BASE']['them' if w == 'us' else 'us']['alone'], b['EX']['BASE']['them' if w == 'us' else 'us']['n'], False))),
 ('victim walking / farming / idle / recalling / tributing / fighting', lambda b, w: ' / '.join(pct(sum(1 for f in openers(b, w) if f['first']['vact'] == a), len(openers(b, w)), False) for a in ('walking', 'farming', 'idle', 'recalling', 'tributing', 'fighting'))),
 ('opener champion (top 5)', lambda b, w: ', '.join('%s %d' % kv for kv in collections.Counter(f['first']['aty'] for f in openers(b, w)).most_common(5))),
 ('first victim type (top 5)', lambda b, w: ', '.join('%s %d' % kv for kv in collections.Counter(f['first']['vty'] for f in openers(b, w)).most_common(5))),
]
table('1b. The first hit (all fights, by opener side)', rows)

# ---------- 2. numbers at the first hit, approach
def cat(f):
    a = f['approach']
    if a['closing'] >= 3: return 'deliberate'
    if a['a_farm'] >= 2: return 'farming'
    if a['v_closed'] > a['a_closed']: return 'theycame'
    return 'other'
def ropen(b, w): return [f for f in RF(b) if opened_by(f, w)]
def n6(f, w): return side(f, w)['n6']
def o6(f, w): return side(f, 'them' if w == 'us' else 'us')['n6']
rows = [
 ('real fights this side opened (n)', lambda b, w: len(ropen(b, w))),
 ('own n6 vs enemy n6 at the first hit (mean)', lambda b, w: '%.2f vs %.2f' % (mean([n6(f, w) for f in ropen(b, w)]), mean([o6(f, w) for f in ropen(b, w)]))),
 ('outnumber / equal / outnumbered within 6', lambda b, w: '%s / %s / %s' % (pct(sum(1 for f in ropen(b, w) if n6(f, w) > o6(f, w)), len(ropen(b, w))), pct(sum(1 for f in ropen(b, w) if n6(f, w) == o6(f, w)), len(ropen(b, w)), False), pct(sum(1 for f in ropen(b, w) if n6(f, w) < o6(f, w)), len(ropen(b, w))))),
 ('K/D when outnumbering', lambda b, w: (lambda g: '%.2f / %.2f (n=%d)' % (sum(side(f, w)['kills'] for f in g)/len(g), sum(len(side(f, w)['deaths']) for f in g)/len(g), len(g)) if g else '-')([f for f in ropen(b, w) if n6(f, w) > o6(f, w)])),
 ('K/D when outnumbered', lambda b, w: (lambda g: '%.2f / %.2f (n=%d)' % (sum(side(f, w)['kills'] for f in g)/len(g), sum(len(side(f, w)['deaths']) for f in g)/len(g), len(g)) if g else '-')([f for f in ropen(b, w) if n6(f, w) < o6(f, w)])),
 ('opener alone within 6 (all openers)', lambda b, w: pct(sum(1 for f in openers(b, w) if n6(f, w) <= 1), len(openers(b, w)))),
 ('hit-first share when ahead / even / behind (all fights)', lambda b, w: ' / '.join(pct(sum(1 for f in g if opened_by(f, w)), len(g), False) for g in ([f for f in b['F'] if n6(f, w) > o6(f, w)], [f for f in b['F'] if n6(f, w) == o6(f, w)], [f for f in b['F'] if n6(f, w) < o6(f, w)]))),
 ('own hp% / enemy hp% at the hit (med)', lambda b, w: '%s / %s' % (med([side(f, w)['hpp'] for f in ropen(b, w)]), med([side(f, 'them' if w == 'us' else 'us')['hpp'] for f in ropen(b, w)]))),
 ('approach: deliberate / they came / farming / other', lambda b, w: (lambda g: ' / '.join(pct(sum(1 for f in g if cat(f) == c), len(g), False) for c in ('deliberate', 'theycame', 'farming', 'other')) + ' (n=%d)' % len(g))([f for f in openers(b, w) if f.get('approach')])),
 ('deliberate openers: K/D', lambda b, w: (lambda g: '%.2f / %.2f (n=%d)' % (sum(side(f, w)['kills'] for f in g)/len(g), sum(len(side(f, w)['deaths']) for f in g)/len(g), len(g)) if g else '-')([f for f in ropen(b, w) if f.get('approach') and cat(f) == 'deliberate'])),
 ('own champions within 8 / alive (mean)', lambda b, w: '%.2f / %.2f' % (mean([side(f, w)['n8'] for f in ropen(b, w)]), mean([side(f, w)['alive_total'] for f in ropen(b, w)]))),
 ('team split (ally alive > 8 away)', lambda b, w: pct(sum(1 for f in ropen(b, w) if side(f, w)['far'] > 0), len(ropen(b, w)))),
 ('fight in own half / middle / enemy half', lambda b, w: (lambda g: '%s / %s / %s' % tuple(pct(x, len(g), False) for x in ((lambda o, t: (o, len(g)-o-t, t))(sum(1 for f in g if side(f, w)['dspawn'] is not None and side(f, 'them' if w == 'us' else 'us')['dspawn'] is not None and side(f, w)['dspawn'] < side(f, 'them' if w == 'us' else 'us')['dspawn'] - 3), sum(1 for f in g if side(f, w)['dspawn'] is not None and side(f, 'them' if w == 'us' else 'us')['dspawn'] is not None and side(f, 'them' if w == 'us' else 'us')['dspawn'] < side(f, w)['dspawn'] - 3)))))(ropen(b, w))),
]
table('2. Numbers, hp and approach at the first hit (openers of this side)', rows)

# ---------- 3. victim side before the hit: contact rounds and what it did
def victim(b, w): return [f for f in b['F'] if not opened_by(f, w)]   # fights where this side was hit first
def what(b, w):
    c = collections.Counter()
    for f in victim(b, w):
        for k, v in f['vision']['what'].items(): c[k] += v
    return c
def dom(b, w):
    c = collections.Counter()
    for f in victim(b, w):
        if f['vision']['rounds'] >= 2 and f['vision']['what']: c[max(f['vision']['what'].items(), key=lambda x: x[1])[0]] += 1
    return c
rows = [
 ('fights where this side was hit first (n)', lambda b, w: len(victim(b, w))),
 ('contact rounds before the hit: 1 / 2-3 / 4-7 / 8+ (med)', lambda b, w: (lambda v: '%s / %s / %s / %s (%s)' % (pct(sum(1 for x in v if x <= 1), len(v), False), pct(sum(1 for x in v if 2 <= x <= 3), len(v), False), pct(sum(1 for x in v if 4 <= x <= 7), len(v), False), pct(sum(1 for x in v if x >= 8), len(v), False), med(v)))([f['vision']['rounds'] for f in victim(b, w)])),
 ('victim side champions within 8 / alive', lambda b, w: '%.2f / %.2f' % (mean([side(f, w)['n8'] for f in victim(b, w)]), mean([side(f, w)['alive_total'] for f in victim(b, w)]))),
 ('victim side split', lambda b, w: pct(sum(1 for f in victim(b, w) if side(f, w)['far'] > 0), len(victim(b, w)))),
 ('victim side carries gems / mean on carriers', lambda b, w: '%s / %s' % (pct(sum(1 for f in victim(b, w) if side(f, w)['gems'] > 0), len(victim(b, w))), mean([side(f, w)['gems'] for f in victim(b, w) if side(f, w)['gems'] > 0]))),
 ('hit in own half / middle / enemy half', lambda b, w: (lambda g: '%s / %s / %s' % tuple(pct(x, len(g), False) for x in ((lambda o, t: (o, len(g)-o-t, t))(sum(1 for f in g if side(f, w)['dspawn'] is not None and side(f, 'them' if w == 'us' else 'us')['dspawn'] is not None and side(f, w)['dspawn'] < side(f, 'them' if w == 'us' else 'us')['dspawn'] - 3), sum(1 for f in g if side(f, w)['dspawn'] is not None and side(f, 'them' if w == 'us' else 'us')['dspawn'] is not None and side(f, 'them' if w == 'us' else 'us')['dspawn'] < side(f, w)['dspawn'] - 3)))))(victim(b, w))),
 ('contact champion-rounds (n)', lambda b, w: sum(what(b, w).values())),
 ('farming / idle / closer / away / sideways / recalling', lambda b, w: (lambda c: ' / '.join(pct(c[k], sum(c.values()), False) for k in ('farm', 'idle', 'closer', 'away', 'side', 'recall')))(what(b, w))),
 ('dominant reaction per fight: closer / farming / idle / sideways / recall', lambda b, w: (lambda c: ' / '.join(pct(c[k], sum(c.values()), False) for k in ('closer', 'farm', 'idle', 'side', 'recall')) + ' (n=%d)' % sum(c.values()))(dom(b, w))),
]
table('3. Before the first hit, side that gets hit', rows)

# ---------- 4. focus, target, chase, spells, ranged distance
def T(b, w):
    c = collections.Counter(); multi = same = atk = left = fol = 0
    for f in b['F']:
        sd = side(f, w); multi += sd['focus_multi']; same += sd['focus_same']; atk += sd['atk_n']; left += sd['atk_target_left']; fol += sd['atk_followed']
        for k, v in sd['target'].items(): c[k] += v
    return c, multi, same, atk, left, fol
rows = [
 ('focus: same victim when 2+ hit in a round', lambda b, w: (lambda t: pct(t[2], t[1]))(T(b, w))),
 ('focus in wins / losses', lambda b, w: ' / '.join(pct(sum(side(f, w)['focus_same'] for f in b['F'] if f['res'] == r), sum(side(f, w)['focus_multi'] for f in b['F'] if f['res'] == r)) for r in ('win', 'loss'))),
 ('target choice (2+ in reach): nearest / lowest hp', lambda b, w: (lambda t: '%s / %s (n=%d)' % (pct(t[0]['nearest'], t[0]['n'], False), pct(t[0]['lowest'], t[0]['n'], False), t[0]['n']))(T(b, w))),
 ('caster when available / carrier when available', lambda b, w: (lambda t: '%s / %s' % (pct(t[0]['caster'], t[0]['caster_avail']), pct(t[0]['carrier'], t[0]['carrier_avail'])))(T(b, w))),
 ('basic attacks; target out of range next round; stepped after it', lambda b, w: (lambda t: '%d; %s; %s' % (t[3], pct(t[4], t[3], False), pct(t[5], t[4], False)))(T(b, w))),
]
table('4. Focus and target choice (all fights)', rows)

def CH(b, w): return b['CH']['CH'][w]
def RET(b, w): return b['CH']['RET'][w]
rows = [
 ('hitter-retreat episodes (n)', lambda b, w: len(CH(b, w))),
 ('0 steps / 1-2 / >=3 / >=5', lambda b, w: (lambda c: '%s / %s / %s / %s' % (pct(sum(1 for x in c if x['steps'] == 0), len(c), False), pct(sum(1 for x in c if 1 <= x['steps'] <= 2), len(c), False), pct(sum(1 for x in c if x['steps'] >= 3), len(c)), pct(sum(1 for x in c if x['steps'] >= 5), len(c), False)))(CH(b, w))),
 ('>=3 steps when victim < 35% hp', lambda b, w: (lambda c: pct(sum(1 for x in c if x['steps'] >= 3), len(c)))([x for x in CH(b, w) if x['vhpp'] < 35])),
 ('victim died (all) / died when chased >=3', lambda b, w: (lambda c: '%s / %s' % (pct(sum(1 for x in c if x['died']), len(c)), pct(sum(1 for x in c if x['died'] and x['steps'] >= 3), sum(1 for x in c if x['steps'] >= 3))))(CH(b, w))),
 ('hit again after the step', lambda b, w: (lambda c: pct(sum(1 for x in c if x['hits_after'] > 0), len(c)))(CH(b, w))),
 ('>=3 steps by chaser class melee / caster', lambda b, w: ' / '.join(pct(sum(1 for x in CH(b, w) if x['steps'] >= 3 and cl(x['chaser_ty']) == k), sum(1 for x in CH(b, w) if cl(x['chaser_ty']) == k)) for k in ('melee', 'caster'))),
]
MELEE = {'Varg', 'Ryth', 'Issac', 'Vendetta', 'Marcella', 'Ren'}; CASTER = {'Stellar', 'Prism', 'Cassi', 'Tavi'}
def cl(t): return 'melee' if t in MELEE else 'caster' if t in CASTER else 'ranged'
table('4b. Chase (after an enemy\'s first step away, follow rounds by the champions that hit it in the 3 rounds before)', rows)

def spells(b, w):
    rf = RF(b); vic = [f for f in rf if not opened_by(f, w)]
    early = sum(1 for f in vic if side(f, w)['cast_early']); casts = sum(side(f, w)['casts'] for f in rf)
    on = sum(side(f, w)['opp_n'] for f in b['F']); oc = sum(side(f, w)['opp_cast'] for f in b['F']); om = sum(side(f, w)['opp_moved'] for f in b['F'])
    return early, len(vic), casts, len(rf), on, oc, om
rows = [
 ('cast within 2 rounds of the first hit (fights the other side opened)', lambda b, w: (lambda s: pct(s[0], s[1]))(spells(b, w))),
 ('casts per real fight', lambda b, w: (lambda s: '%.2f' % (s[2]/s[3]))(spells(b, w))),
 ('champion-rounds with enemy <= 4 and both slots up: cast / walked', lambda b, w: (lambda s: '%s / %s' % (pct(s[5], s[4]), pct(s[6], s[4], False)))(spells(b, w))),
 ('spell share of champion damage', lambda b, w: pct(sum(side(f, w)['dmg_spell'] for f in b['F']), sum(side(f, w)['dmg'] for f in b['F']), False)),
 ('per champion cast rate (both slots up, enemy <= 4)', lambda b, w: ', '.join('%s %s (n=%d)' % (t, pct(b['EX']['USE'][w][t]['cast'], b['EX']['USE'][w][t]['n'], False), b['EX']['USE'][w][t]['n']) for t in ('Stellar', 'Cassi', 'Tavi', 'Prism', 'Ryth', 'Ren', 'Issac', 'Varg', 'Vendetta') if t in b['EX']['USE'][w])),
]
table('4c. Spells', rows)

def rd(b, w):
    c = collections.Counter(); rr = adj = 0
    for f in b['F']:
        sd = side(f, w)
        for k, v in sd['ranged_dist'].items(): c[k] += v
        rr += sd['ranged_rounds']; adj += sd['ranged_adj']
    return c, rr, adj
rows = [
 ('ranged basic attacks at d1 / d2 / d3', lambda b, w: (lambda c: (lambda n: '%s / %s / %s (n=%d)' % (pct(c['atk1'], n, False), pct(c['atk2'], n, False), pct(c['atk3'], n, False), n))(sum(v for k, v in c.items() if k.startswith('atk'))))(rd(b, w)[0])),
 ('ranged basic attacks at d1-2', lambda b, w: (lambda c: pct(c['atk1'] + c['atk2'], sum(v for k, v in c.items() if k.startswith('atk'))))(rd(b, w)[0])),
 ('spells at d1 / d2 / d3 / d4 / d5+', lambda b, w: (lambda c: (lambda n: '%s / %s / %s / %s / %s (n=%d)' % (pct(c['spell1'], n, False), pct(c['spell2'], n, False), pct(c['spell3'], n, False), pct(c['spell4'], n, False), pct(c['spell5'] + c['spell6'], n, False), n))(sum(v for k, v in c.items() if k.startswith('spell'))))(rd(b, w)[0])),
 ('spells from 1-3', lambda b, w: (lambda c: pct(c['spell1'] + c['spell2'] + c['spell3'], sum(v for k, v in c.items() if k.startswith('spell'))))(rd(b, w)[0])),
 ('ranged champion fight-rounds within 2 of an enemy', lambda b, w: (lambda r: pct(r[2], r[1]))(rd(b, w))),
]
table('4d. Ranged champions: distance', rows)

# ---------- 5. retreat under fire, fight ends
rows = [
 ('retreats under fire (n)', lambda b, w: len(RET(b, w))),
 ('hp% at the step med (p25-p75)', lambda b, w: (lambda h: '%s (%s-%s)' % (med(h), q(h, .25), q(h, .75)))([r['hpp'] for r in RET(b, w)])),
 ('<30% / <50% / >=70%', lambda b, w: (lambda h: '%s / %s / %s' % (pct(sum(1 for x in h if x < 30), len(h), False), pct(sum(1 for x in h if x < 50), len(h), False), pct(sum(1 for x in h if x >= 70), len(h), False)))([r['hpp'] for r in RET(b, w)])),
 ('died within 12 rounds', lambda b, w: pct(sum(1 for r in RET(b, w) if r['died']), len(RET(b, w)))),
 ('died: melee / casters', lambda b, w: ' / '.join(pct(sum(1 for r in RET(b, w) if r['died'] and cl(r['ty']) == k), sum(1 for r in RET(b, w) if cl(r['ty']) == k)) for k in ('melee', 'caster'))),
 ('died by hp band 0-30 / 30-50 / 50-70 / 70+', lambda b, w: ' / '.join(pct(sum(1 for r in RET(b, w) if r['died'] and lo <= r['hpp'] < hi), sum(1 for r in RET(b, w) if lo <= r['hpp'] < hi)) for lo, hi in ((0, 30), (30, 50), (50, 70), (70, 1000)))),
 ('recall within 10 / completed / distance to nearest enemy', lambda b, w: (lambda rs: '%s / %s / %s' % (pct(sum(1 for r in rs if r['recalled']), len(rs), False), pct(sum(1 for r in rs if r['recalled'] and r['arrived']), sum(1 for r in rs if r['recalled'])), med([r['rec_d'] for r in rs if r['recalled'] and r['rec_d'] is not None])))(RET(b, w))),
 ('kite (hits again within 8 rounds)', lambda b, w: pct(sum(1 for r in RET(b, w) if r['back']), len(RET(b, w)), False)),
 ('outnumbered at the step', lambda b, w: pct(sum(1 for r in RET(b, w) if r['outnumbered']), len(RET(b, w)), False)),
]
table('5. Retreat under fire (first step away with an enemy within 4 and damage taken in the previous 3 rounds)', rows)

def lv(f, w):
    l = f['end']['leaver']
    if l is None: return None
    if l == 'both': return 'both'
    return 'us' if (l == f['us']) == (w == 'us') else 'them'
rows = [
 ('fight length med / p75; single pokes; >=10 rounds', lambda b, w: (lambda L: '%s / %s; %s; %s' % (med(L), q(L, .75), pct(sum(1 for x in L if x == 1), len(L), False), pct(sum(1 for x in L if x >= 10), len(L), False)))([f['length'] for f in b['F']])),
 ('ends: kill / wipe / recall / walk', lambda b, w: (lambda e: ' / '.join(pct(e[k], len(b['F']), False) for k in ('kill', 'wipe', 'recall', 'leave')))(collections.Counter(f['end']['kind'] for f in b['F']))),
 ('this side leaves first / other first / same round', lambda b, w: (lambda c: '%s / %s / %s' % (pct(c['us'], len(b['F']), False), pct(c['them'], len(b['F']), False), pct(c['both'], len(b['F']), False)))(collections.Counter(lv(f, w) for f in b['F']))),
 ('this side wiped / wiped the other (real fights)', lambda b, w: '%d / %d' % (sum(1 for f in RF(b) if (f['us'] if w == 'us' else 1-f['us']) in f['end']['wipe']), sum(1 for f in RF(b) if (1-f['us'] if w == 'us' else f['us']) in f['end']['wipe']))),
 ('leave kind: walk / recall', lambda b, w: (lambda g: '%s / %s' % (pct(sum(1 for f in g if f['end']['leave_kind'] == 'walk'), len(g), False), pct(sum(1 for f in g if f['end']['leave_kind'] == 'recall'), len(g))))([f for f in b['F'] if lv(f, w) == 'us'])),
]
table('5b. Fight length and how fights end', rows)

# ---------- 6. per map
print('\n### 6. Per map: games (W-L), real fights, we hit first, our kills-deaths, gems lost/won  (study27 | study26)')
print('| map | s27 W-L | s26 W-L | s27 real fights/game | s26 | s27 we hit first | s26 | s27 kills-deaths | s26 | s27 K/D per real fight | s26 | s27 gems lost/won | s26 |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for mp in MAPS + ['ALL']:
    cells = []
    for bn in ('s27', 's26'):
        b = B[bn]; sel = [r for r in b['SEL'] if mp == 'ALL' or r['map'] == mp]; fs = [f for f in RF(b) if mp == 'ALL' or f['map'] == mp]
        k = sum(us(f)['kills'] for f in fs); d = sum(len(us(f)['deaths']) for f in fs)
        cells.append(dict(wl='%d-%d' % (sum(1 for r in sel if r['res'] == 'win'), sum(1 for r in sel if r['res'] == 'loss')), rpg='%.1f' % (len(fs)/max(1, len(sel))), hf=pct(sum(1 for f in fs if we_first(f)), len(fs), False), kd='%d-%d' % (k, d), kdr='%.2f / %.2f' % (k/max(1, len(fs)), d/max(1, len(fs))) if len(fs) >= 10 else '-', gems='%d / %d' % (sum(us(f)['gems_lost'] for f in fs), sum(us(f)['gems_won'] for f in fs))))
    a, c = cells
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (mp, a['wl'], c['wl'], a['rpg'], c['rpg'], a['hf'], c['hf'], a['kd'], c['kd'], a['kdr'], c['kdr'], a['gems'], c['gems']))

# ---------- 7. per opponent
print('\n### 7. Per opponent (real fights), study27 with the study26 numbers for the same team')
print('| opponent (rank s27 / s26) | s27 W-L | s26 W-L | s27 real fights | we hit first | our kills | our deaths | gems lost / won | s26: fights, hit first, kills, deaths |')
print('|---|---|---|---|---|---|---|---|---|')
def oppstats(b, opp):
    fs = [f for f in RF(b) if f['opp'] == opp]; sel = [r for r in b['SEL'] if r['opp'] == opp]
    if not sel: return None
    return dict(wl='%d-%d' % (sum(1 for r in sel if r['res'] == 'win'), sum(1 for r in sel if r['res'] == 'loss')), n=len(fs), hf=pct(sum(1 for f in fs if we_first(f)), len(fs), False), k=sum(us(f)['kills'] for f in fs), d=sum(len(us(f)['deaths']) for f in fs), gl=sum(us(f)['gems_lost'] for f in fs), gw=sum(us(f)['gems_won'] for f in fs), rank=sel[0]['orank'])
opps = sorted(set(r['opp'] for r in B['s27']['SEL']), key=lambda o: [r['orank'] for r in B['s27']['SEL'] if r['opp'] == o][0])
for opp in opps:
    a = oppstats(B['s27'], opp); c = oppstats(B['s26'], opp)
    print('| %s (%d / %s) | %s | %s | %d | %s | %d | %d | %d / %d | %s |' % (opp, a['rank'], c['rank'] if c else '-', a['wl'], c['wl'] if c else '-', a['n'], a['hf'], a['k'], a['d'], a['gl'], a['gw'], '%d, %s, %d, %d' % (c['n'], c['hf'], c['k'], c['d']) if c else 'not in study26'))
print('\nTop-10 / 11-30 split (real fights, our kills-deaths, hit first):')
for bn in ('s27', 's26'):
    b = B[bn]
    for lo, hi in ((1, 10), (11, 30)):
        fs = [f for f in RF(b) if lo <= f['orank'] <= hi]; sel = [r for r in b['SEL'] if lo <= r['orank'] <= hi]
        print('  %s ranks %d-%d: games %d (%d-%d), real fights %d, we hit first %s, kills-deaths %d-%d' % (bn, lo, hi, len(sel), sum(1 for r in sel if r['res'] == 'win'), sum(1 for r in sel if r['res'] == 'loss'), len(fs), pct(sum(1 for f in fs if we_first(f)), len(fs), False), sum(us(f)['kills'] for f in fs), sum(len(us(f)['deaths']) for f in fs)))

# ---------- 8. worst losses of study27 (by score margin) and their biggest fights
print('\n### 8. Worst study27 losses (score margin) with their costliest fights')
b = B['s27']
byg = collections.defaultdict(list)
for f in b['F']: byg[f['match']].append(f)
for r in sorted([r for r in b['SEL'] if r['res'] == 'loss'], key=lambda r: r['score'] - r['oscore'])[:12]:
    fs = byg[r['match']]; k = sum(us(f)['kills'] for f in fs); d = sum(len(us(f)['deaths']) for f in fs)
    worst = sorted(fs, key=lambda f: -(len(us(f)['deaths'])*100 + us(f)['gems_lost']))[:3]
    print('- %s %s vs %s (rank %d): %d-%d, rounds %d, draft %s vs %s; fights %d, kills-deaths %d-%d, gems lost %d; worst: %s' % (r['map'], r['match'][:8], r['opp'], r['orank'], r['score'], r['oscore'], r['rounds'], '+'.join(r['draft']), '+'.join(r['odraft']), len(fs), k, d, sum(us(f)['gems_lost'] for f in fs),
          '; '.join('r%d-%d %s %s on %s (%s) n6 %d v %d K/D %d/%d -%d gems' % (f['r0'], f['r1'], 'WE' if we_first(f) else 'THEY', f['first']['aty'], f['first']['vty'], f['first']['vact'], us(f)['n6'], them(f)['n6'], us(f)['kills'], len(us(f)['deaths']), us(f)['gems_lost']) for f in worst)))

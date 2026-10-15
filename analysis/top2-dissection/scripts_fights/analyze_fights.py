"""Aggregate fight records (fights.json): outcomes, hit-first, engage conditions, retreats."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_fights')
from common import *
F = json.load(open(S + '/reports/scripts_fights/fights.json'))
def us(f): return f['sides'][str(f['us'])]
def them(f): return f['sides'][str(1-f['us'])]
def real(f): return us(f)['dmg'] + them(f)['dmg'] >= 1000 or us(f)['deaths'] or them(f)['deaths']
def pct(a, b): return '%d%%' % round(100*a/b) if b else '-'
def mean(x): return round(st.mean(x), 2) if x else None
def med(x): return st.median(x) if x else None

print('# 1. fights per team / map  (all | real = >=1000 dmg or a death)')
print('| team | map | games | fights | real | we hit first (real) | kills | deaths | K/D per real fight | dmg dealt/taken per real fight | opp dmg share |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
tot = collections.defaultdict(list)
for team in ('mite', 'uni'):
    for mp in ['collision', 'corners', 'elkring', 'expanse', 'interlock', 'lanes', 'monolith', 'packs', 'rows', 'ALL']:
        fs = [f for f in F if f['team'] == team and (mp == 'ALL' or f['map'] == mp)]
        rf = [f for f in fs if real(f)]
        games = len(set(f['match'] for f in fs)) if mp != 'ALL' else 54
        if not fs: print('| %s | %s | %d | 0 | 0 | - | - | - | - | - | - |' % (team, mp, games)); continue
        k = sum(us(f)['kills'] for f in rf); d = sum(len(us(f)['deaths']) for f in rf)
        hf = sum(1 for f in rf if f['first']['at'] == f['us'])
        dd = sum(us(f)['dmg'] for f in rf); dt = sum(them(f)['dmg'] for f in rf)
        print('| %s | %s | %d | %d | %d | %s | %d | %d | %.2f / %.2f | %d / %d | %s |' % (team, mp, games, len(fs), len(rf), pct(hf, len(rf)), k, d, k/max(1, len(rf)), d/max(1, len(rf)), dd/max(1, len(rf)), dt/max(1, len(rf)), pct(dt, dd+dt)))

print('\n# 1b. all fights (incl. pokes): hit-first share and K/D')
for team in ('mite', 'uni'):
    fs = [f for f in F if f['team'] == team]
    hf = sum(1 for f in fs if f['first']['at'] == f['us'])
    k = sum(us(f)['kills'] for f in fs); d = sum(len(us(f)['deaths']) for f in fs)
    print(team, 'fights', len(fs), 'hit first', pct(hf, len(fs)), 'kills', k, 'deaths', d, 'dmg dealt', sum(us(f)['dmg'] for f in fs), 'taken', sum(them(f)['dmg'] for f in fs))

print('\n# 1c. per opponent (real fights)')
print('| team | opponent (rank) | real fights | hit first | kills | deaths |')
print('|---|---|---|---|---|---|')
for team in ('mite', 'uni'):
    byopp = collections.defaultdict(list)
    for f in F:
        if f['team'] == team and real(f): byopp[f['opp']].append(f)
    for opp, fs in sorted(byopp.items(), key=lambda x: -len(x[1])):
        hf = sum(1 for f in fs if f['first']['at'] == f['us'])
        print('| %s | %s | %d | %s | %d | %d |' % (team, opp, len(fs), pct(hf, len(fs)), sum(us(f)['kills'] for f in fs), sum(len(us(f)['deaths']) for f in fs)))

print('\n# 2. ENGAGE conditions at the first hit (real fights): numbers / hp / position, split by who hit first')
print('| team | who hit first | n | avg our n vs their n | we outnumber / equal / outnumbered | our hp% (med) | their hp% (med) | we healthier | our dist spawn (med) | their dist spawn (med) | we carry gems | they busy w/ camp | kills/deaths |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for team in ('mite', 'uni'):
    for who in ('us', 'them'):
        fs = [f for f in F if f['team'] == team and real(f) and ((f['first']['at'] == f['us']) == (who == 'us'))]
        if not fs: continue
        on = [us(f)['n'] for f in fs]; tn = [them(f)['n'] for f in fs]
        out = sum(1 for f in fs if us(f)['n'] > them(f)['n']); eq = sum(1 for f in fs if us(f)['n'] == them(f)['n']); outn = len(fs) - out - eq
        oh = [us(f)['hpp'] for f in fs]; th = [them(f)['hpp'] for f in fs]
        heal = sum(1 for f in fs if us(f)['hpp'] > them(f)['hpp'] + 5)
        ds = [us(f)['dspawn'] for f in fs if us(f)['dspawn'] is not None]; tds = [them(f)['dspawn'] for f in fs if them(f)['dspawn'] is not None]
        gems = sum(1 for f in fs if us(f)['gems'] > 0)
        busy = sum(1 for f in fs if them(f)['busy'])
        print('| %s | %s | %d | %.2f vs %.2f | %s / %s / %s | %s | %s | %s | %s | %s | %s | %s | %.2f/%.2f |' % (team, who, len(fs), mean(on), mean(tn), pct(out, len(fs)), pct(eq, len(fs)), pct(outn, len(fs)), med(oh), med(th), pct(heal, len(fs)), med(ds), med(tds), pct(gems, len(fs)), pct(busy, len(fs)),
              sum(us(f)['kills'] for f in fs)/len(fs), sum(len(us(f)['deaths']) for f in fs)/len(fs)))

print('\n# 2b. first hit: kind and distance when WE hit first (all fights)')
for team in ('mite', 'uni'):
    fs = [f for f in F if f['team'] == team and f['first']['at'] == f['us']]
    kinds = collections.Counter(f['first']['kind'] for f in fs)
    dist = collections.Counter(f['first']['dist'] for f in fs)
    byty = collections.Counter((f['first']['aty'], f['first']['kind'], f['first']['dist']) for f in fs)
    print(team, 'n', len(fs), 'kind', dict(kinds), 'dist', sorted(dist.items()))
    print('   opener by (type, kind, dist):', byty.most_common(12))
    # approach: who closed
    ap = [f['approach'] for f in fs if f.get('approach')]
    a_closed = sum(1 for a in ap if a['a_closed'] > a['v_closed']); v_closed = sum(1 for a in ap if a['v_closed'] > a['a_closed']); both = len(ap) - a_closed - v_closed
    print('   approach (4 rounds before first hit): attacker closed more %s, victim walked in %s, equal %s; attacker moved med %s tiles, victim %s' % (pct(a_closed, len(ap)), pct(v_closed, len(ap)), pct(both, len(ap)), med([a['a_moved'] for a in ap]), med([a['v_moved'] for a in ap])))
    fs2 = [f for f in F if f['team'] == team and f['first']['at'] != f['us']]
    ap = [f['approach'] for f in fs2 if f.get('approach')]
    a_closed = sum(1 for a in ap if a['a_closed'] > a['v_closed']); v_closed = sum(1 for a in ap if a['v_closed'] > a['a_closed'])
    print('   when THEY hit first (n=%d): enemy attacker closed more %s, our victim walked in %s' % (len(fs2), pct(a_closed, len(ap)), pct(v_closed, len(ap))))

print('\n# 2c. engage outcome by numbers advantage (real fights, we hit first)')
for team in ('mite', 'uni'):
    fs = [f for f in F if f['team'] == team and real(f)]
    byadv = collections.defaultdict(list)
    for f in fs: byadv[max(-2, min(2, us(f)['n'] - them(f)['n']))].append(f)
    for adv in sorted(byadv):
        g = byadv[adv]
        print(team, 'advantage %+d' % adv, 'n', len(g), 'we hit first', pct(sum(1 for f in g if f['first']['at'] == f['us']), len(g)), 'K/D %.2f/%.2f' % (sum(us(f)['kills'] for f in g)/len(g), sum(len(us(f)['deaths']) for f in g)/len(g)),
              'our hp%% med %s their %s' % (med([us(f)['hpp'] for f in g]), med([them(f)['hpp'] for f in g])))

print('\n# 2d. where fights happen: our dist to own spawn vs theirs (real fights), and altar proximity')
for team in ('mite', 'uni'):
    fs = [f for f in F if f['team'] == team and real(f)]
    ours = sum(1 for f in fs if us(f)['dspawn'] is not None and them(f)['dspawn'] is not None and us(f)['dspawn'] < them(f)['dspawn'] - 3)
    theirs = sum(1 for f in fs if us(f)['dspawn'] is not None and them(f)['dspawn'] is not None and them(f)['dspawn'] < us(f)['dspawn'] - 3)
    alt = sum(1 for f in fs if us(f)['daltar'] is not None and us(f)['daltar'] <= 3)
    print(team, 'real fights', len(fs), 'in our half', pct(ours, len(fs)), 'in their half', pct(theirs, len(fs)), 'middle', pct(len(fs)-ours-theirs, len(fs)), 'within 3 of an altar', pct(alt, len(fs)), 'round med', med([f['r0'] for f in fs]))

print('\n# 3. RETREATS (first step away during/after a fight) by team: hp% at the step, context, outcome')
print('| team | retreats | hp% med (p25-p75) | hp%<30 | 30-50 | >50 | outnumbered at step | allies dead | recalled within 10 | arrived home | died within 12 | went toward spawn | toward ally | into bush |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
RT = collections.defaultdict(list)
for f in F:
    for r in f['retreats']:
        key = f['team'] if r['team'] == f['us'] else ('opp_of_' + f['team'])
        RT[key].append(dict(r, map=f['map'], match=f['match'], r0=f['r0']))
for key in ('mite', 'uni', 'opp_of_mite', 'opp_of_uni'):
    rs = RT[key]
    if not rs: continue
    h = sorted(r['hpp'] for r in rs)
    q = lambda p: h[int(p*(len(h)-1))]
    outn = sum(1 for r in rs if r['enemies'] > r['allies'] + 1)
    ad = sum(1 for r in rs if r['allies_dead'] > 0)
    rec = sum(1 for r in rs if r['recalled']); arr = sum(1 for r in rs if r['arrived']); died = sum(1 for r in rs if r['died'])
    tsp = sum(1 for r in rs if r['dsp1'] is not None and r['dsp1'] < r['dsp0'] - 2)
    tal = sum(1 for r in rs if r['na0'] is not None and r['na1'] is not None and r['na1'] < r['na0'])
    bush = sum(1 for r in rs if r['bush'])
    print('| %s | %d | %s (%s-%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (key, len(rs), q(.5), q(.25), q(.75), pct(sum(1 for x in h if x < 30), len(h)), pct(sum(1 for x in h if 30 <= x <= 50), len(h)), pct(sum(1 for x in h if x > 50), len(h)),
          pct(outn, len(rs)), pct(ad, len(rs)), pct(rec, len(rs)), pct(arr, len(rs)), pct(died, len(rs)), pct(tsp, len(rs)), pct(tal, len(rs)), pct(bush, len(rs))))

print('\n# 3b. retreat hp% by champion class and outcome')
for key in ('mite', 'uni'):
    byc = collections.defaultdict(list)
    for r in RT[key]: byc[cls(r['ty'])].append(r)
    for c, rs in byc.items():
        h = [r['hpp'] for r in rs]
        print(key, c, 'n', len(rs), 'hp% med', med(h), 'died', pct(sum(1 for r in rs if r['died']), len(rs)), 'recalled', pct(sum(1 for r in rs if r['recalled']), len(rs)), 'recall dist to nearest enemy med', med([r['rec_d'] for r in rs if r['rec_d'] is not None]))
    # low-hp retreats specifically
    low = [r for r in RT[key] if r['hpp'] < 40]
    print(key, 'retreats at hp<40: n', len(low), 'died', pct(sum(1 for r in low if r['died']), len(low)), 'recalled', pct(sum(1 for r in low if r['recalled']), len(low)))
    hi = [r for r in RT[key] if r['hpp'] >= 60]
    print(key, 'retreats at hp>=60: n', len(hi), 'outnumbered', pct(sum(1 for r in hi if r['enemies'] > r['allies'] + 1), len(hi)), 'took dmg in prev 3 rounds', pct(sum(1 for r in hi if r['taken_prev'] > 0), len(hi)), 'died', pct(sum(1 for r in hi if r['died']), len(hi)))

print('\n# 3c. deaths: did the victim try to retreat before dying? (real fights)')
for team in ('mite', 'uni'):
    fs = [f for f in F if f['team'] == team and real(f)]
    nd = 0; tried = 0
    for f in fs:
        for (r, i, ty) in us(f)['deaths']:
            nd += 1
            if any(x['i'] == i and x['died'] for x in f['retreats']): tried += 1
    print(team, 'our deaths in real fights', nd, 'had started a retreat step', pct(tried, nd))

print('\n# examples: biggest fights per team')
for team in ('mite', 'uni'):
    fs = sorted([f for f in F if f['team'] == team], key=lambda f: -(us(f)['dmg'] + them(f)['dmg']))[:6]
    for f in fs:
        print(team, f['map'], f['match'][:8], 'r%d-%d' % (f['r0'], f['r1']), 'vs', f['opp'][:20], 'us', us(f)['types'], 'hp%', us(f)['hpp'], 'them', them(f)['types'], 'hp%', them(f)['hpp'], 'first', f['first']['aty'], f['first']['kind'], 'd', f['first']['dist'], 'by us' if f['first']['at'] == f['us'] else 'by them', 'K/D', us(f)['kills'], len(us(f)['deaths']), 'dmg', us(f)['dmg'], them(f)['dmg'])

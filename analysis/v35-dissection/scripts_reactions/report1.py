"""Q1 reactions to being hit + Q2 retreat quality. Prints markdown."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_reactions')
from common import *
R = json.load(open(W + '/scripts_reactions/rows.json'))
sel = load_sel(); NG = len(sel)
def pct(a, b): return '%d%%' % round(100 * a / b) if b else '-'
def med(x): x = [v for v in x if v is not None]; return st.median(x) if x else None
def q(x, p):
    x = sorted(v for v in x if v is not None)
    return x[min(len(x) - 1, int(p * len(x)))] if x else None
CLASSES = ['fight', 'fight+away', 'fight+closer', 'away', 'closer', 'lateral', 'camp', 'recall', 'tribute', 'nothing', 'dead']
def simp(c):
    if c == 'fight+lateral': return 'fight'
    if c == 'arrived': return 'recall'
    return c
def table_seq(rows, k, title):
    """distribution of class at offset k"""
    c = collections.Counter(simp(r['seq'][k]) for r in rows if len(r['seq']) > k)
    n = sum(c.values())
    return '| %s | %d | ' % (title, n) + ' | '.join(pct(c[x], n) for x in CLASSES) + ' |'
hits = R['hits']
# flatten per hit-round rows
HR = []
for h in hits:
    for row in h['rows']:
        HR.append(dict(h, r=row['r'], band=row['band'], seq=row['seq']))
print('## Q1. Reaction to being hit\n')
print('Unit = champion-round in which the champion took damage from an enemy champion ("hit round"). Action classes: **fight** = basic attack or damage spell on an enemy champion (fight+away / fight+closer = a melee that also moved); **away / closer / lateral** = moved and the Chebyshev distance to the nearest enemy (enemy positions of the previous round end) grew / shrank / stayed; **camp** = attacked a camp monster; **recall / tribute** = started or continued that channel; **nothing** = no action with an effect (idle, failed action, stunned); **dead**.\n')
print('Counts: hit rounds us %d (%d episodes), opponents %d (%d episodes). Episode = hit rounds of one champion with gaps <= 5 rounds.\n' % (
    sum(1 for r in HR if r['us']), sum(1 for h in hits if h['us']), sum(1 for r in HR if not r['us']), sum(1 for h in hits if not h['us'])))
hdr = '| rows | n | ' + ' | '.join(CLASSES) + ' |\n|' + '---|' * (len(CLASSES) + 2)
for who, lab in ((True, 'US'), (False, 'OPPONENTS')):
    X = [r for r in HR if r['us'] == who]
    print('### %s: action in the hit round (t0) and the next 3 rounds (all hit rounds)\n' % lab)
    print(hdr)
    for k in range(4): print(table_seq(X, k, 't+%d' % k))
    print()
    print('### %s: by champion type, action in the hit round / at t+1 (first hit of each episode only)\n' % lab)
    print(hdr)
    E = [h for h in hits if h['us'] == who]
    for ty in sorted(set(h['ty'] for h in E)):
        Y = [h for h in E if h['ty'] == ty]
        print(table_seq(Y, 0, ty + ' t0')); print(table_seq(Y, 1, ty + ' t+1'))
    print()
    print('### %s: by hp band before the hit (all hit rounds), action at t0 / t+1\n' % lab)
    print(hdr)
    for b in ('>70', '40-70', '<40'):
        Y = [r for r in X if r['band'] == b]
        print(table_seq(Y, 0, 'hp ' + b + ' t0')); print(table_seq(Y, 1, 'hp ' + b + ' t+1'))
    print()
    print('### %s: by champion class x hp band, action at t+1 (all hit rounds)\n' % lab)
    print(hdr)
    for c in ('melee', 'caster'):
        for b in ('>70', '40-70', '<40'):
            Y = [r for r in X if r['band'] == b and r['cls'] == c]
            print(table_seq(Y, 1, '%s hp %s' % (c, b)))
    print()
# retreat delay
print('### Rounds from the first hit of an episode to the first retreat step\n')
print('Retreat step = a move that increases the distance to the nearest enemy and after which that distance is >= 2 larger 3 rounds later (or >= 1 with no attack). Only episodes in which the champion was hit by an enemy champion; "none" = no retreat step within the episode + 3 rounds.\n')
print('| team | episodes | retreat within episode | delay 0 | 1 | 2 | 3 | 4-5 | 6-10 | >10 | median delay | episode died | died with no retreat step | died after a retreat step |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for who, lab in ((True, 'us'), (False, 'opp')):
    E = [h for h in hits if h['us'] == who]
    d = [h['ret_delay'] for h in E if h['ret_delay'] is not None]
    c = collections.Counter(d)
    print('| %s | %d | %s | %d | %d | %d | %d | %d | %d | %d | %s | %d | %d | %d |' % (lab, len(E), pct(len(d), len(E)), c[0], c[1], c[2], c[3], c[4] + c[5], sum(c[x] for x in range(6, 11)), sum(v for k, v in c.items() if k > 10), med(d),
          sum(h['died'] for h in E), sum(1 for h in E if h['died'] and h['ret_delay'] is None), sum(1 for h in E if h['died'] and h['ret_delay'] is not None)))
print()
print('By champion type and hp band at the first hit (us): share of episodes with a retreat step and median delay\n')
print('| type | episodes | retreat | med delay | hp>70: n / retreat / delay | 40-70 | <40 |')
print('|---|---|---|---|---|---|---|')
for who in (True, False):
    E = [h for h in hits if h['us'] == who]
    for ty in sorted(set(h['ty'] for h in E)):
        Y = [h for h in E if h['ty'] == ty]
        cells = []
        for b in ('>70', '40-70', '<40'):
            Z = [h for h in Y if h['band'] == b]; d = [h['ret_delay'] for h in Z if h['ret_delay'] is not None]
            cells.append('%d / %s / %s' % (len(Z), pct(len(d), len(Z)), med(d)))
        d = [h['ret_delay'] for h in Y if h['ret_delay'] is not None]
        print('| %s %s | %d | %s | %s | %s |' % ('us' if who else 'opp', ty, len(Y), pct(len(d), len(Y)), med(d), ' | '.join(cells)))
print()
print('Retreat alone or with the group (allies within 6 at the retreat step; an ally "also retreats" if its distance to the same enemy grows by >= 2 over the next 2 rounds)\n')
print('| team | retreat steps | no ally within 6 | allies stay/fight | some allies retreat | all allies retreat |')
print('|---|---|---|---|---|---|')
for who, lab in ((True, 'us'), (False, 'opp')):
    E = [h for h in hits if h['us'] == who and h['grp']]
    c = collections.Counter(h['grp'] for h in E); n = len(E)
    print('| %s | %d | %s | %s | %s | %s |' % (lab, n, pct(c['no_ally_within_6'], n), pct(c['allies_stay'], n), pct(c['some_allies_retreat'], n), pct(c['allies_also_retreat'], n)))
print()
# Q2
print('## Q2. Retreat quality\n')
RT = R['retreats']
print('Unit = retreat step (as defined above), n us %d, opponents %d. "Foe follows" = in the next 12 rounds the nearest enemy (at the retreat step) made a move that reduced its distance to the retreating champion; chase length = last such round. Outcome within 15 rounds: death, recall arrived, escape (nearest enemy >= 8 and not hit in rounds 8-15), escape_near (not hit in rounds 8-15 but an enemy still within 8), still_fighting (hit again in rounds 8-15).\n' % (sum(1 for r in RT if r['us']), sum(1 for r in RT if not r['us'])))
print('| team | n | hp% med | foe dist at step med | foe follows >=1 | >=3 steps | chase len med (if followed) | dist to foe +5r: med change | outrun (>= +3) | caught (<= 0) | toward spawn (dspawn -2 or more) | away from spawn (+2) | toward ally (-2) | away from ally (+2) | death | recall | escape | escape_near | still_fighting | recall started within 15r |')
print('|---|' * 20)
def rtrow(lab, X):
    n = len(X)
    if not n: return
    f = [r for r in X if r['follow'] > 0]
    o = collections.Counter(r['out'] for r in X)
    print('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
        lab, n, med([r['hp'] for r in X]), med([r['dfoe'] for r in X]), pct(len(f), n), pct(sum(1 for r in X if r['follow'] >= 3), n), med([r['chase_len'] for r in f]),
        med([r['dd5'] for r in X]), pct(sum(1 for r in X if r['dd5'] is not None and r['dd5'] >= 3), n), pct(sum(1 for r in X if r['dd5'] is not None and r['dd5'] <= 0), n),
        pct(sum(1 for r in X if r['dds5'] is not None and r['dds5'] <= -2), n), pct(sum(1 for r in X if r['dds5'] is not None and r['dds5'] >= 2), n),
        pct(sum(1 for r in X if r['dda5'] is not None and r['dda5'] <= -2), n), pct(sum(1 for r in X if r['dda5'] is not None and r['dda5'] >= 2), n),
        pct(o['death'], n), pct(o['recall'], n), pct(o['escape'], n), pct(o['escape_near'], n), pct(o['still_fighting'], n), pct(sum(1 for r in X if r['recall_delay'] is not None), n)))
for who, lab in ((True, 'us'), (False, 'opp')):
    X = [r for r in RT if r['us'] == who]
    rtrow(lab + ' all', X)
    for c in ('melee', 'caster'): rtrow(lab + ' ' + c, [r for r in X if r['cls'] == c])
    for b in ('>70', '40-70', '<40'): rtrow(lab + ' hp ' + b, [r for r in X if r['band'] == b])
    for fc in ('melee', 'caster'): rtrow(lab + ' vs ' + fc + ' foe', [r for r in X if r['foe_cls'] == fc])
print()
print('Us: retreat outcome by map / result / opponent tier / champion type\n')
print('| split | n | hp% med | foe follows | death | recall | escape(+near) | still fighting | recall started |')
print('|---|---|---|---|---|---|---|---|---|')
X = [r for r in RT if r['us']]
def rt2(lab, Y):
    n = len(Y)
    if not n: return
    o = collections.Counter(r['out'] for r in Y)
    print('| %s | %d | %s | %s | %s | %s | %s | %s | %s |' % (lab, n, med([r['hp'] for r in Y]), pct(sum(1 for r in Y if r['follow'] > 0), n), pct(o['death'], n), pct(o['recall'], n), pct(o['escape'] + o['escape_near'], n), pct(o['still_fighting'], n), pct(sum(1 for r in Y if r['recall_delay'] is not None), n)))
for mp in sorted(set(r['map'] for r in X)): rt2('map ' + mp, [r for r in X if r['map'] == mp])
for rs in ('win', 'loss'): rt2('result ' + rs, [r for r in X if r['res'] == rs])
for t in ('top10', '11-20', '21-30', 'other'): rt2('opp ' + t, [r for r in X if r['tier'] == t])
for ty in sorted(set(r['ty'] for r in X)): rt2(ty, [r for r in X if r['ty'] == ty])
print()
print('Examples (us): retreats that ended in death: ' + '; '.join('%s %s %s r%d hp%d%% foe %s at %d' % (r['match'][:8], r['map'], r['ty'], r['r'], r['hp'], r['foe_ty'], r['dfoe']) for r in X if r['out'] == 'death' and r['hp'] >= 40)[:1200])
print()
print('Examples (us): retreats saved by recall: ' + '; '.join('%s %s %s r%d hp%d%% recall after %d rounds' % (r['match'][:8], r['map'], r['ty'], r['r'], r['hp'], r['recall_delay']) for r in X if r['out'] == 'recall')[:600])

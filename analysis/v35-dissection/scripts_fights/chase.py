"""Chase and retreat-under-fire numbers for both sides (comparable with fights.md: chase >=3 follow steps, first step away under fire hp%)."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_fights')
from common import *
F = json.load(open(S + '/ws2/scripts_fights/fights.json'))
byg = collections.defaultdict(list)
for f in F: byg[f['match']].append(f)
def pos(c): return (c['x'], c['y'])
def med(x): return st.median(x) if x else None
def pct(a, b): return '%d%%' % round(100*a/b) if b else '-'
RET = {'us': [], 'them': []}     # retreats under fire
CH = {'us': [], 'them': []}      # chases: per retreating enemy, max follow steps by the chasing side
EX = collections.defaultdict(list)
for rec in selected():
    g = load_game(rec); usi = g.us
    for f in byg[g.match]:
        r0, r1 = f['r0'], f['r1']
        win = [rr for rr in g.order if r0 <= rr <= r1 + 8]
        for t in (0, 1):
            who = 'us' if t == usi else 'them'
            ids = f['sides'][str(t)]['ids']; foe_ids = f['sides'][str(1-t)]['ids']
            for i in ids:
                prevd = None
                for k, rr in enumerate(win):
                    c = g.rounds[rr][i]
                    if not c['alive']: break
                    foes = [e for e in g.rounds[rr].values() if e['team'] != t and e['alive'] and cheb(pos(e), pos(c)) <= 10]
                    if not foes: prevd = None; continue
                    d = min(cheb(pos(e), pos(c)) for e in foes)
                    moved = 'move' in g.acts[i].get(rr, []) or 'dash' in g.acts[i].get(rr, [])
                    if prevd is not None and d > prevd and moved:
                        nxt = win[k+1:k+4]
                        if nxt and all(g.dealt[i].get(x, 0) == 0 for x in nxt):
                            pc = g.rounds[win[k-1]][i]
                            taken_prev = sum(g.taken[i].get(x, 0) for x in win[max(0, k-3):k])
                            under_fire = prevd <= 4 and taken_prev > 0
                            hpp = round(100 * pc['hp'] / pc['mhp'])
                            after = [x for x in g.order if rr < x <= rr + 12]
                            died = any(not g.rounds[x][i]['alive'] for x in after)
                            recalled = any(rr <= x <= rr + 10 for x in g.recall_start[i])
                            arrived = any(rr <= x <= rr + 16 for x in g.recall_arrive[i])
                            allies = sum(1 for e in g.rounds[rr].values() if e['team'] == t and e['alive'] and e['i'] != i and cheb(pos(e), pos(c)) <= 8)
                            # recall distance to nearest enemy at recall start
                            rec_d = None
                            for x in g.recall_start[i]:
                                if rr <= x <= rr + 10:
                                    cc = g.rounds[x][i]; fo = [cheb(pos(e), pos(cc)) for e in g.rounds[x].values() if e['team'] != t and e['alive']]
                                    rec_d = min(fo) if fo else 99; break
                            # back in (kite): deals damage again within 8 rounds
                            back = any(g.dealt[i].get(x, 0) > 0 for x in g.order if rr + 3 < x <= rr + 8)
                            if under_fire:
                                RET[who].append(dict(hpp=hpp, died=died, recalled=recalled, arrived=arrived, rec_d=rec_d, back=back, outnumbered=len(foes) > allies + 1, ty=g.types[i][1], match=g.match, r=rr, map=g.map))
                            # chase (reference definition, fights.md): for each enemy that hit i in the 3 rounds before the step, consecutive rounds after it
                            # in which that hitter moves without increasing its distance to i and stays within 6
                            chaser = 'them' if who == 'us' else 'us'
                            hitters = set(h['a'] for h in g.hits if h['v'] == i and rr - 3 <= h['r'] <= rr and g.types[h['a']][0] != t)
                            kk = g.ridx[rr]
                            for a in hitters:
                                steps = 0; hits_after = 0
                                for x in g.order[kk+1:kk+13]:
                                    sa = g.rounds[x][a]; sv = g.rounds[x][i]
                                    if not sa['alive'] or not sv['alive']: break
                                    px = g.order[g.ridx[x]-1]
                                    if 'move' in g.acts[a].get(x, []) or 'dash' in g.acts[a].get(x, []):
                                        if cheb(pos(sa), pos(sv)) <= cheb(pos(g.rounds[px][a]), pos(g.rounds[px][i])) and cheb(pos(sa), pos(sv)) <= 6: steps += 1
                                        else: break
                                    hits_after += sum(1 for h in g.hits if h['a'] == a and h['v'] == i and h['r'] == x)
                                CH[chaser].append(dict(steps=steps, vhpp=hpp, died=died, chaser_ty=g.types[a][1], hits_after=hits_after, match=g.match, r=rr, map=g.map, vty=g.types[i][1]))
                                if steps >= 5 and len(EX[chaser]) < 5: EX[chaser].append((g.map, g.match[:8], 'r%d' % rr, g.types[a][1], 'follows', g.types[i][1], 'hp%d%%' % hpp, '%d steps' % steps, 'victim died' if died else 'escaped', 'hits after %d' % hits_after))
                            break
                    prevd = d
print('# Retreat under fire (first step away with an enemy within 4 and damage taken in the previous 3 rounds)')
print('| side | n | hp% at the step med (p25-p75) | <30% | <50% | >=70% | kite (hits again within 8 rounds) | outnumbered | recall within 10 | recall completed | recall dist to nearest enemy med | died within 12 |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for who in ('us', 'them'):
    rs = RET[who]; h = sorted(r['hpp'] for r in rs); n = len(rs)
    q = lambda p: h[int(p*(n-1))]
    rec = [r for r in rs if r['recalled']]
    print('| %s | %d | %s (%s-%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (who, n, q(.5), q(.25), q(.75), pct(sum(1 for x in h if x < 30), n), pct(sum(1 for x in h if x < 50), n), pct(sum(1 for x in h if x >= 70), n), pct(sum(1 for r in rs if r['back']), n), pct(sum(1 for r in rs if r['outnumbered']), n), pct(len(rec), n), pct(sum(1 for r in rec if r['arrived']), len(rec)), med([r['rec_d'] for r in rec if r['rec_d'] is not None]), pct(sum(1 for r in rs if r['died']), n)))
for who in ('us', 'them'):
    byc = collections.defaultdict(list)
    for r in RET[who]: byc[cls(r['ty'])].append(r)
    print(who, 'by class:', ', '.join('%s n %d hp%% med %s died %s recalled %s' % (c, len(v), med([r['hpp'] for r in v]), pct(sum(1 for r in v if r['died']), len(v)), pct(sum(1 for r in v if r['recalled']), len(v))) for c, v in byc.items()))
    byb = collections.defaultdict(list)
    for r in RET[who]: byb['0-30' if r['hpp'] < 30 else '30-50' if r['hpp'] < 50 else '50-70' if r['hpp'] < 70 else '70+'].append(r)
    print(who, 'by hp band (n, died, recalled, kite):', ', '.join('%s: %d %s %s %s' % (b, len(v), pct(sum(1 for r in v if r['died']), len(v)), pct(sum(1 for r in v if r['recalled']), len(v)), pct(sum(1 for r in v if r['back']), len(v))) for b, v in sorted(byb.items())))
print('\n# Chase (reference definition): after an enemy champion\'s first step away, consecutive follow rounds by each of our champions that hit it in the previous 3 rounds')
print('| chaser | hitter-retreat episodes | 0 steps | 1-2 | >= 3 | >= 5 | >=3 when victim < 35% hp | victim died (all) | victim died when chased >= 3 | hit again after the step | chaser type for >= 3 |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for who in ('us', 'them'):
    cs = CH[who]; n = len(cs)
    low = [c for c in cs if c['vhpp'] < 35]
    c3 = [c for c in cs if c['steps'] >= 3]
    print('| %s | %d | %s | %s | %s | %s | %s (n=%d) | %s | %s | %s | %s |' % (who, n, pct(sum(1 for c in cs if c['steps'] == 0), n), pct(sum(1 for c in cs if 1 <= c['steps'] <= 2), n), pct(len(c3), n), pct(sum(1 for c in cs if c['steps'] >= 5), n), pct(sum(1 for c in low if c['steps'] >= 3), len(low)), len(low), pct(sum(1 for c in cs if c['died']), n), pct(sum(1 for c in c3 if c['died']), len(c3)), pct(sum(1 for c in cs if c['hits_after'] > 0), n), collections.Counter(c['chaser_ty'] for c in c3).most_common(4)))
    print('   by chaser class:', ', '.join('%s n %d >=3 steps %s' % (c, len(v), pct(sum(1 for x in v if x['steps'] >= 3), len(v))) for c, v in sorted(collections.defaultdict(list, {k: [x for x in cs if cls(x['chaser_ty']) == k] for k in ('melee', 'caster', 'ranged')}).items()) if v))
print('\nexamples of long chases:')
for k, v in EX.items():
    for x in v: print(' ', k, x)

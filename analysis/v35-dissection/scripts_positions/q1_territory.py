"""Q1: where champions are over the game (50-round bins): own/mid/enemy, near altar, near camp, at spawn, idle at spawn. us vs opp.
Invasion episodes both ways; what we do when they invade."""
import sys, collections, statistics as st, json
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
C = collections.defaultdict(collections.Counter)   # (split, who, bin) -> counters
N = collections.Counter()  # (split,who) games
EP = collections.defaultdict(list)  # (split, who) -> invasion episodes
REACT = collections.defaultdict(collections.Counter)  # (split) -> what our champs do while enemy in our half
REACTW = collections.defaultdict(collections.Counter)
ng = 0
for rec, g in games():
    ng += 1; mp = g.mp; keys = split_keys(rec)
    for who, t in (('us', g.us), ('opp', g.them)):
        for k in keys: N[(k, who)] += 1
        inside = {}
        for r in g.order[1:]:
            sn = g.rounds[r]; b = rbin(r)
            mine = [c for c in sn.values() if c['team'] == t and c['alive']]
            ens = [c for c in sn.values() if c['team'] != t and c['alive']]
            for c in mine:
                tr = terr(mp, c['x'], c['y'], t)
                sd = spawn_dist(mp, c['x'], c['y'], t); ad = altar_dist(mp, c['x'], c['y'])
                near_camp = any(cheb((c['x'], c['y']), ct) <= 2 and g.camps[r][ci]['alive'] for ci, k_ in g.camps[r].items() for ct in [(k_['x'], k_['y'])]) if False else None
                # near a living camp monster (<=2)
                nc = any(k_['alive'] and cheb((c['x'], c['y']), (k_['x'], k_['y'])) <= 2 for k_ in g.camps[r].values())
                lab = primary(g.acts[c['i']][r])
                for k in keys:
                    cc = C[(k, who, b)]
                    cc['n'] += 1; cc[tr] += 1
                    if sd <= 2: cc['spawn'] += 1
                    if sd <= 2 and lab in ('nothing', 'buy'): cc['spawn_idle'] += 1
                    if ad <= 2: cc['altar'] += 1
                    if nc: cc['camp'] += 1
                    if lab == 'nothing': cc['nothing'] += 1
                # invasion episodes
                if tr == 'enemy':
                    if c['i'] not in inside:
                        nearest = min([cheb((c['x'], c['y']), (e['x'], e['y'])) for e in ens], default=99)
                        inside[c['i']] = dict(r=r, i=c['i'], ty=c['ty'], nearest=nearest, camp=False, atk=False, hit=False, cap=False, diff=g.sub[r][t]-g.sub[r][1-t], maxdepth=0, trib=False)
                    d = inside[c['i']]
                    a = g.acts[c['i']][r]
                    if a & {'atkcamp', 'spellcamp'}: d['camp'] = True
                    if a & {'atk', 'spell'}: d['atk'] = True
                    if g.taken[c['i']].get(r, 0) > 0: d['hit'] = True
                    if a & {'trib', 'tribdone'}: d['trib'] = True
                    d['maxdepth'] = max(d['maxdepth'], spawn_dist(mp, c['x'], c['y'], t) - spawn_dist(mp, c['x'], c['y'], 1-t))
            for (rr, i, gm) in g.caps:
                if rr == r and i in inside: inside[i]['cap'] = True
            for i, d in list(inside.items()):
                c = sn.get(i)
                if not c['alive'] or terr(mp, c['x'], c['y'], t) != 'enemy':
                    d['end'] = r; d['dead'] = not c['alive']
                    for k in keys: EP[(k, who)].append(d)
                    del inside[i]
            # reaction: enemy champions in OUR half this round -> what are our champs doing
            if who == 'us':
                inv = [e for e in ens if terr(mp, e['x'], e['y'], t) == 'enemy' and False]
                inv = [e for e in ens if terr(mp, e['x'], e['y'], 1-t) == 'enemy']  # enemy standing in its enemy half = our half
                if inv:
                    for c in mine:
                        lab = primary(g.acts[c['i']][r]); tr = terr(mp, c['x'], c['y'], t)
                        dn = min(cheb((c['x'], c['y']), (e['x'], e['y'])) for e in inv)
                        for k in keys:
                            REACT[k][lab] += 1; REACT[k]['_n'] += 1
                            REACTW[k][tr] += 1
                            REACTW[k]['near<=8' if dn <= 8 else 'far'] += 1
                            if dn <= 8: REACTW[k]['near_' + lab] += 1
                    for k in keys: REACTW[k]['_rounds'] += 1
print('games', ng)
def row(k, who):
    out = []
    for b in range(10):
        cc = C[(k, who, b)]; n = cc['n'] or 1
        if cc['n'] == 0: out.append('-'); continue
        out.append('%d/%d/%d' % (round(100*cc['own']/n), round(100*cc['mid']/n), round(100*cc['enemy']/n)))
    return out
print('\n## own/mid/enemy % of alive champion-rounds, by 50-round bin')
print('| split | who | games | ' + ' | '.join(BINS) + ' |'); print('|---'*13 + '|')
for k in ['ALL'] + sorted(set(x[0] for x in C if x[0] != 'ALL')):
    for who in ('us', 'opp'):
        print('| %s | %s | %d | %s |' % (k, who, N[(k, who)], ' | '.join(row(k, who))))
print('\n## other location shares (% of alive champion-rounds): at spawn(<=2) / idle at spawn / near altar(<=2) / near living camp(<=2) / doing nothing')
print('| split | who | ' + ' | '.join(BINS) + ' |'); print('|---'*12 + '|')
for k in ['ALL'] + sorted(set(x[0] for x in C if x[0] != 'ALL')):
    for who in ('us', 'opp'):
        out = []
        for b in range(10):
            cc = C[(k, who, b)]; n = cc['n'] or 1
            if cc['n'] == 0: out.append('-'); continue
            out.append('%d/%d/%d/%d/%d' % tuple(round(100*cc[x]/n) for x in ('spawn', 'spawn_idle', 'altar', 'camp', 'nothing')))
        print('| %s | %s | %s |' % (k, who, ' | '.join(out)))
print('\n## enemy-half episodes (one champion crossing into enemy territory)')
print('| split | who | games | episodes | per game | median len | median start r | hits camp there | hits enemy there | gets hit there | captures there | tributes there | ends dead | median score diff at entry | nearest enemy <=8 at entry |')
print('|---'*15 + '|')
for k in ['ALL'] + sorted(set(x[0] for x in C if x[0] != 'ALL')):
    for who in ('us', 'opp'):
        L = EP[(k, who)]; n = len(L)
        if not n: print('| %s | %s | %d | 0 |' % (k, who, N[(k, who)])); continue
        print('| %s | %s | %d | %d | %.1f | %d | %d | %d%% | %d%% | %d%% | %d%% | %d%% | %d%% | %+d | %d%% |' % (k, who, N[(k, who)], n, n/N[(k, who)], st.median([d['end']-d['r'] for d in L]), st.median([d['r'] for d in L]),
              100*sum(d['camp'] for d in L)/n, 100*sum(d['atk'] for d in L)/n, 100*sum(d['hit'] for d in L)/n, 100*sum(d['cap'] for d in L)/n, 100*sum(d['trib'] for d in L)/n, 100*sum(d['dead'] for d in L)/n, st.median([d['diff'] for d in L]), 100*sum(d['nearest'] <= 8 for d in L)/n))
print('\n## what OUR champions do in rounds when at least one enemy stands in our half')
print('| split | rounds with invader | our champ-rounds | near invader (<=8) | own/mid/enemy where we are | actions (all) | actions when near |')
print('|---'*8 + '|')
for k in ['ALL'] + sorted(set(x[0] for x in C if x[0] != 'ALL')):
    R = REACT[k]; W = REACTW[k]; n = R['_n'] or 1
    acts = ', '.join('%s %d%%' % (a, round(100*v/n)) for a, v in R.most_common() if a != '_n')
    nn = W['near<=8'] or 1
    near = ', '.join('%s %d%%' % (a[5:], round(100*v/nn)) for a, v in sorted(W.items(), key=lambda x: -x[1]) if a.startswith('near_'))
    print('| %s | %d | %d | %d%% | %d/%d/%d | %s | %s |' % (k, W['_rounds'], R['_n'], 100*W['near<=8']/n, 100*W['own']/n, 100*W['mid']/n, 100*W['enemy']/n, acts, near))
# longest episodes examples
print('\n## longest enemy-half episodes (us / opp)')
for who in ('us', 'opp'):
    L = sorted(EP[('ALL', who)], key=lambda d: -(d['end']-d['r']))[:8]
    for d in L: print(who, {k: d[k] for k in ('r', 'end', 'ty', 'camp', 'atk', 'cap', 'dead', 'diff', 'maxdepth')})
json.dump({'EP': {str(k): v for k, v in EP.items() if k[0] == 'ALL'}}, open('q1_ep.json', 'w'))

import sys, json, collections, statistics as st
sys.path.insert(0, '.')
from common import *
R = json.load(open(RP)); sel = load_sel(); NG = len(sel)
def pct(a, b): return '%d%%' % round(100 * a / b) if b else '-'
def med(x): x = [v for v in x if v is not None]; return st.median(x) if x else None
# 1. recall reasons for us
RC = [x for x in R['recalls'] if x['us']]
print('## recall attempt reasons (us)')
hist = collections.Counter(min(x['hp'] // 10 * 10, 100) for x in RC); print('hp hist', sorted(hist.items()))
for lab, f in (('hp<50', lambda x: x['hp'] < 50), ('hp 50-70', lambda x: 50 <= x['hp'] < 70), ('hp>=70', lambda x: x['hp'] >= 70)):
    X = [x for x in RC if f(x)]
    print(lab, len(X), 'gems>0', pct(sum(1 for x in X if x['gems'] > 0), len(X)), 'gold>=30', pct(sum(1 for x in X if x['gold'] >= 30), len(X)), 'gold>=90', pct(sum(1 for x in X if x['gold'] >= 90), len(X)), 'neither', pct(sum(1 for x in X if x['gems'] == 0 and x['gold'] < 30), len(X)), 'dfoe med', med([x['dfoe'] for x in X]), 'dspawn med', med([x['dspawn'] for x in X]), 'hit recent', pct(sum(1 for x in X if x['hit_recent']), len(X)), 'arrived', pct(sum(1 for x in X if x['out'] == 'arrived'), len(X)))
X = [x for x in RC if x['gems'] == 0 and x['gold'] < 30 and not x['hit_recent']]
print('no gems, no gold, not hit: n', len(X), 'hp max', max(x['hp'] for x in X), 'hp hist', sorted(collections.Counter(min(x['hp'] // 10 * 10, 100) for x in X).items()))
print('per type max hp of no-gems/no-gold/not-hit attempts:', {ty: max(x['hp'] for x in X if x['ty'] == ty) for ty in sorted(set(x['ty'] for x in X))})
# opp Tavi/Varg/Vendetta/Marcella-like bots: real recalls hp
# 2. gems lost as share of tributed
D = R['deaths']
for who in (True, False):
    lost = sum(d['gems'] for d in D if d['us'] == who); trib = sum(s['score'] if who else s['oscore'] for s in sel)
    print('gems lost', 'us' if who else 'opp', lost, 'tributed', trib, 'share %.1f%%' % (100 * lost / trib))
# 3. idle-under-fire streaks and tribute at death, melee out of reach
print('## idle under fire')
for who in (True, False):
    G_streak = collections.Counter(); melee_oor = 0; melee_oor_tot = 0; trib_death = 0; trib_death_gems = 0; cap_death = 0
    stand_hits = 0
    for s in sel:
        G = Game(s)
        for i in G.types:
            if (G.team(i) == G.side) != who: continue
            run = 0
            for r in G.order:
                if r == 0: continue
                if G.champ_dmg(r, i) and G.alive(r, i) and G.classify(r, i) == 'nothing': run += 1
                else:
                    if run >= 3: G_streak[min(run, 6)] += 1
                    run = 0
                # melee out of reach: hit by a champion, nearest foe at >= 2 (prev round), class nothing
                if G.champ_dmg(r, i) and G.alive(r, i) and cls(G.ty(i)) == 'melee' and r - 1 in G.rounds:
                    melee_oor_tot += 1
                    if G.nearest_foe(r - 1, i)[0] >= 2 and G.classify(r, i) == 'nothing': melee_oor += 1
            for d in G.death_round[i]:
                if (d, i) in G.pair_death: continue
                if G.tribute_active(d - 1, i) is not None or G.tribute_active(d, i) is not None:
                    trib_death += 1; trib_death_gems += G.rounds[d - 1][i]['gems']
    print('us' if who else 'opp', 'idle-under-fire streaks >=3 rounds:', dict(G_streak), '| melee hit rounds', melee_oor_tot, 'of which standing still with the attacker at >= 2 tiles:', melee_oor, pct(melee_oor, melee_oor_tot), '| deaths during a tribute channel:', trib_death, 'gems', trib_death_gems)
# 4. first-hit episodes: what we do at the first hit while hp>70 and the attacker is a caster at range 4 (poke) - share that step closer
H = R['hits']
for who in (True, False):
    X = [h for h in H if h['us'] == who and h['band'] == '>70']
    c = collections.Counter(h['seq'][1] for h in X)
    print('us' if who else 'opp', 'first hit at hp>70, action at t+1:', c.most_common(6), 'n', len(X))
# 5. deaths by "before": share with hp_first >= 70 and ep_len <= 3 (burst) per team
for who in (True, False):
    X = [d for d in D if d['us'] == who and not d['pair']]
    print('us' if who else 'opp', 'burst deaths (hp_first>=70 & episode<=3 rounds):', sum(1 for d in X if d['hp_first'] >= 70 and d['ep_len'] <= 3), 'of', len(X), '| long fights (episode >8):', sum(1 for d in X if d['ep_len'] > 8), '| died with no ally within 6 and allies alive >= 1:', sum(1 for d in X if d['allies6'] == 0 and d['allies_alive'] > 0))
    print('   killer class of deaths:', collections.Counter(cls(d['killer']) if d['killer'] not in ('camp', 'self', 'other') else d['killer'] for d in X))
    print('   deaths by nch (3-champ vs 4 vs 5 drafts):', {n: (sum(1 for d in X if d['nch'] == n), sum(1 for s in sel if len(s['draft']) == n)) for n in (3, 4, 5)})

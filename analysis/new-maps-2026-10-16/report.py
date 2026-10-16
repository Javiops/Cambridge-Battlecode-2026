# Markdown tables per new map: top-10 winners vs top-10 losers vs us (from data/games.json).
import json, collections, statistics as st, sys
G = json.load(open('../data/games.json'))
MJ = ['stampede', 'pilgrimage', 'ambush', 'eight', 'contest', 'fragment', 'swirl', 'rushbait_v2']
def m(xs, f='{:.0f}'):
    xs = [x for x in xs if x is not None]
    return f.format(st.median(xs)) if xs else '-'
def mean(xs, f='{:.1f}'):
    xs = [x for x in xs if x is not None]
    return f.format(st.mean(xs)) if xs else '-'
ROWS = [('games', lambda g: str(len(g))), ('win rate', lambda g: f"{sum(x['win'] for x in g)/len(g):.0%}"),
        ('final round (median)', lambda g: m([x['final'] for x in g])), ('gems at end', lambda g: m([x['gems'] for x in g])),
        ('gems banked r150 / r300 / r500', lambda g: m([x['sub150'] for x in g]) + ' / ' + m([x['sub300'] for x in g]) + ' / ' + m([x['sub500'] for x in g])),
        ('round reaching 1000 (if)', lambda g: m([x['reach'] for x in g])),
        ('first contact round', lambda g: m([x['contact'] for x in g])),
        ('kills / deaths per game', lambda g: mean([x['kills'] for x in g]) + ' / ' + mean([x['deaths'] for x in g])),
        ('deaths in enemy half', lambda g: mean([x['deaths_enemy_half'] for x in g])),
        ('time in enemy half', lambda g: mean([x['enemy_half'] * 100 for x in g], '{:.0f}%')),
        ('gold earned', lambda g: m([x['gold'] for x in g])),
        ('gold-only captures / gem captures', lambda g: mean([x['gold_caps'] for x in g]) + ' / ' + mean([x['gem_caps'] for x in g])),
        ('first capture / first gem capture', lambda g: m([x['first_cap'] for x in g]) + ' / ' + m([x['first_gem_cap'] for x in g])),
        ('banks per game, median bag', lambda g: mean([x['banks'] for x in g]) + ', ' + m([x['bag'] for x in g])),
        ('recalls per game, median hp at recall', lambda g: mean([x['recalls'] for x in g]) + ', ' + m([x['recall_hp'] for x in g], '{:.2f}')),
        ('first shop buy, buys per game', lambda g: m([x['first_buy'] for x in g]) + ', ' + mean([x['n_buys'] for x in g]))]
def fam(g):
    c = collections.Counter(); n = 0
    for x in g:
        for it, k in x['items'].items():
            p = it.split('_'); c[p[0] + '/' + p[-1]] += k; n += k
    return ', '.join(f'{k} {v/max(n,1):.0%}' for k, v in c.most_common(5))
maps = sys.argv[1:] or list(MJ)
for mp in maps:
    gs = [x for x in G if x['map'] == mp]
    if not gs: continue
    tw = [x for x in gs if x['who'] == 'top' and x['win']]; tl = [x for x in gs if x['who'] == 'top' and not x['win']]
    us = [x for x in gs if x['team'] == 'us']; uo = [x for x in gs if x['who'] == 'opp']
    print(f'\n## {mp}\n')
    print('| | top-10 winners | top-10 losers | us (vs top-30) | our opponents |\n|---|---|---|---|---|')
    for name, f in ROWS:
        print(f'| {name} | ' + ' | '.join(f(g) if g else '-' for g in (tw, tl, us, uo)) + ' |')
    print('| item families (share of buys) | ' + ' | '.join(fam(g) if g else '-' for g in (tw, tl, us, uo)) + ' |')
    print('\nWinning drafts:', '; '.join(f"{' '.join(d)} x{n}" for d, n in collections.Counter(tuple(x['draft']) for x in tw).most_common(4)),
          '| ours:', '; '.join(f"{' '.join(d)} x{n}" for d, n in collections.Counter(tuple(x['draft']) for x in us).most_common(2)))
    # camp groups: who captures what
    def groups(g):
        c = collections.Counter(); info = {}
        for x in g:
            for r, grp, gems, gold, cx, cy in x['cap_seq']: pass
            for grp, n in x['cap_groups']: c[grp] += n
            for r, grp, gems, gold, cx, cy in x['cap_seq']: info[grp] = (gems, gold, cx, cy)
        return c, info
    c1, i1 = groups(tw); c2, i2 = groups(us); info = {**i2, **i1}
    print('\nCaptures per game by camp group (gems/gold, tile): winners vs us')
    for grp in sorted(set(c1) | set(c2), key=lambda k: -(c1[k] / max(len(tw), 1))):
        gi = info.get(grp, ('?', '?', '?', '?'))
        print(f'- group {grp} ({gi[0]} gems, {gi[1]} gold, at {gi[2]},{gi[3]}): {c1[grp]/max(len(tw),1):.1f} vs {c2[grp]/max(len(us),1):.1f}')

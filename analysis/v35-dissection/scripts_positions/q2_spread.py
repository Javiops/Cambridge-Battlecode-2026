"""Q2: spread: mean pairwise distance, largest cluster (<=3 chain), alone (no ally within 6); ranged vs melee relative to enemies."""
import sys, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_positions')
from common import *
A = collections.defaultdict(lambda: collections.defaultdict(list))  # (split,who) -> metric -> values
B = collections.defaultdict(collections.Counter)
FR = collections.defaultdict(collections.Counter)  # formation vs enemy
def clusters(pts):
    n = len(pts); seen = [False]*n; best = 0
    for s in range(n):
        if seen[s]: continue
        stack = [s]; seen[s] = True; sz = 0
        while stack:
            u = stack.pop(); sz += 1
            for v in range(n):
                if not seen[v] and cheb(pts[u], pts[v]) <= 3: seen[v] = True; stack.append(v)
        best = max(best, sz)
    return best
ng = 0
for rec, g in games():
    ng += 1; keys = split_keys(rec)
    for who, t in (('us', g.us), ('opp', g.them)):
        for r in g.order[1:]:
            if r % 2: continue
            sn = g.rounds[r]
            mine = [c for c in sn.values() if c['team'] == t and c['alive']]
            ens = [c for c in sn.values() if c['team'] != t and c['alive']]
            pts = [(c['x'], c['y']) for c in mine]
            if len(pts) >= 2:
                pd = [cheb(a, b) for i, a in enumerate(pts) for b in pts[i+1:]]
                mpd = st.mean(pd); lc = clusters(pts)
                for k in keys:
                    A[(k, who)]['mean_pd'].append(mpd); A[(k, who)]['max_pd'].append(max(pd))
                    A[(k, who)]['largest_cluster'].append(lc); A[(k, who)]['frac_in_cluster'].append(lc/len(pts))
                    B[(k, who)]['rounds'] += 1
                    if lc == len(pts): B[(k, who)]['all_together'] += 1
                    if lc == 1: B[(k, who)]['all_apart'] += 1
                for c in mine:
                    alone = all(cheb((c['x'], c['y']), (o['x'], o['y'])) > 6 for o in mine if o is not c)
                    for k in keys:
                        B[(k, who)]['champ'] += 1; B[(k, who)]['alone'] += alone
                        B[(k, who)]['alone_'+cls(c['ty'])] += alone; B[(k, who)]['champ_'+cls(c['ty'])] += 1
                        # alone while an enemy within 8
                        if alone and any(cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8 for e in ens):
                            B[(k, who)]['alone_near_enemy'] += 1
                        if any(cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8 for e in ens): B[(k, who)]['near_enemy'] += 1
            # formation vs enemy: champs with enemy within 8
            nd = {}
            for c in mine:
                d = min([cheb((c['x'], c['y']), (e['x'], e['y'])) for e in ens], default=99)
                if d <= 8: nd[c['i']] = (d, cls(c['ty']), c['ty'])
            if nd:
                cs = [d for d, c_, _ in nd.values() if c_ == 'caster']; ms = [d for d, c_, _ in nd.values() if c_ == 'melee']; rs = [d for d, c_, _ in nd.values() if c_ == 'ranged']
                for k in keys:
                    for d, c_, ty in nd.values():
                        A[(k, who)]['dist_'+c_].append(d); A[(k, who)]['dist_'+ty].append(d)
                    if cs and ms:
                        FR[(k, who)]['cm_rounds'] += 1
                        if min(ms) < min(cs): FR[(k, who)]['melee_front'] += 1
                        elif min(ms) == min(cs): FR[(k, who)]['level'] += 1
                        else: FR[(k, who)]['caster_front'] += 1
                        A[(k, who)]['caster_minus_melee'].append(min(cs)-min(ms))
                    if rs and ms:
                        FR[(k, who)]['rm_rounds'] += 1
                        if min(ms) < min(rs): FR[(k, who)]['melee_front_r'] += 1
                        elif min(ms) == min(rs): FR[(k, who)]['level_r'] += 1
                        else: FR[(k, who)]['ranged_front'] += 1
                    # how many of ours are within 8 of enemy vs how many alive (do we bring everyone?)
                    FR[(k, who)]['eng_champs'] += len(nd); FR[(k, who)]['alive_champs'] += len(mine)
print('games', ng)
print('\n## spread (every 2nd round, alive champions >=2): mean pairwise Chebyshev distance, max pairwise, largest cluster (chain within 3 tiles), % rounds all together, % rounds all apart, % champion-rounds alone (no ally within 6), alone while enemy within 8 (% of champ-rounds near an enemy)')
print('| split | who | rounds | mean pd | median pd | max pd (mean) | largest cluster (mean) | share of team in largest cluster | all together | all apart | alone | alone: melee/caster/ranged | alone & enemy<=8 |')
print('|---'*13 + '|')
for k in ['ALL'] + sorted(set(x[0] for x in A if x[0] != 'ALL')):
    for who in ('us', 'opp'):
        a = A[(k, who)]; b = B[(k, who)]
        if not b['rounds']: continue
        print('| %s | %s | %d | %.2f | %.1f | %.2f | %.2f | %d%% | %d%% | %d%% | %d%% | %d/%d/%d%% | %d%% |' % (k, who, b['rounds'], st.mean(a['mean_pd']), st.median(a['mean_pd']), st.mean(a['max_pd']), st.mean(a['largest_cluster']), 100*st.mean(a['frac_in_cluster']),
              100*b['all_together']/b['rounds'], 100*b['all_apart']/b['rounds'], 100*b['alone']/b['champ'], 100*b['alone_melee']/(b['champ_melee'] or 1), 100*b['alone_caster']/(b['champ_caster'] or 1), 100*b['alone_ranged']/(b['champ_ranged'] or 1), 100*b['alone_near_enemy']/(b['near_enemy'] or 1)))
print('\n## formation when enemies are within 8: distance to nearest enemy by class (mean / median), melee strictly in front of casters (% of rounds with both classes engaged), caster-minus-melee gap, engaged share of alive champions')
print('| split | who | melee d | caster d | ranged d | rounds caster+melee | melee front | level | caster front | gap | ranged vs melee: melee front/level/ranged front | engaged/alive |')
print('|---'*13 + '|')
for k in ['ALL'] + sorted(set(x[0] for x in A if x[0] != 'ALL')):
    for who in ('us', 'opp'):
        a = A[(k, who)]; f = FR[(k, who)]
        if not f['cm_rounds'] and not f['rm_rounds']: continue
        def md(x): return '%.2f/%d' % (st.mean(x), st.median(x)) if x else '-'
        n = f['cm_rounds'] or 1; m = f['rm_rounds'] or 1
        print('| %s | %s | %s | %s | %s | %d | %d%% | %d%% | %d%% | %+.2f | %d%%/%d%%/%d%% | %d%% |' % (k, who, md(a['dist_melee']), md(a['dist_caster']), md(a['dist_ranged']), f['cm_rounds'], 100*f['melee_front']/n, 100*f['level']/n, 100*f['caster_front']/n, st.mean(a['caster_minus_melee']) if a['caster_minus_melee'] else 0, 100*f['melee_front_r']/m, 100*f['level_r']/m, 100*f['ranged_front']/m, 100*f['eng_champs']/(f['alive_champs'] or 1)))
print('\n## distance to nearest enemy (enemy within 8) by champion type (mean/median)')
tys = sorted(set(k_[5:] for kk in A for k_ in A[kk] if k_.startswith('dist_') and k_[5:] not in ('melee', 'caster', 'ranged')))
print('| who | ' + ' | '.join(tys) + ' |'); print('|---'*(len(tys)+1) + '|')
for who in ('us', 'opp'):
    a = A[('ALL', who)]
    print('| %s | %s |' % (who, ' | '.join(('%.2f/%d (n=%d)' % (st.mean(a['dist_'+t]), st.median(a['dist_'+t]), len(a['dist_'+t]))) if a['dist_'+t] else '-' for t in tys)))

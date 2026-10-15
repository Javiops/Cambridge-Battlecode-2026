"""Q1: target choice on enemy champions, focus, target switching.  python3 -I q1_targets.py [mite|uni]"""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
SINGLE = {('Cassi', 'dmg'), ('Tavi', 'stundmg'), ('Ren', 'stundmg'), ('Marcella', 'dmg'), ('Stellar', 'single'), ('Prism', 'single')}
teams = [sys.argv[1]] if len(sys.argv) > 1 else ['mite', 'uni']
for TEAM in teams:
    hyp = collections.Counter(); n = 0; ncand = []; conflict = collections.Counter()
    hyp_by_ty = collections.defaultdict(collections.Counter)
    focus_rounds = collections.Counter(); share = []
    switch = collections.Counter(); examples = collections.defaultdict(list)
    prev_target = {}  # (match,a) -> (r, target)
    for s, g in focus_games(TEAM):
        t = s['t']; m = s['match'][:8]
        team_dmg_round = collections.defaultdict(float); cur_r = None
        hit_by_team = collections.defaultdict(dict)  # victim -> {r: dmg}
        for r, a, team, ty, acts in iterate_turns(g):
            if r != cur_r:
                if cur_r is not None and team_dmg_round:
                    tot = sum(team_dmg_round.values()); mx = max(team_dmg_round.values())
                    focus_rounds['rounds'] += 1
                    if len(team_dmg_round) == 1: focus_rounds['single_victim'] += 1
                    else: share.append(mx / tot)
                team_dmg_round = collections.defaultdict(float); cur_r = r
            if team != t: continue
            for j, rec in enumerate(acts):
                if rec['kind'] == 'atk': R = atk_range(ty); kindname = 'atk'
                elif rec['kind'] == 'cast' and (ty, rec['slot']) in SINGLE: R = 4; kindname = 'spell'
                else: continue
                if not rec['victims']: continue
                tgt = rec['victims'][0][0]
                for v in rec['victims']: team_dmg_round[v[0]] += v[1]; hit_by_team[v[0]][r] = hit_by_team[v[0]].get(r, 0) + v[1]
                ch, _ = rec['before']
                cands = [(i, c) for i, c in ch.items() if g['types'][i][0] != t and c[4] and c[2] > 0 and cheb(rec['apos'], (c[0], c[1])) <= R]
                # target switching bookkeeping
                key = (m, a)
                prevt = prev_target.get(key, (0, -1))[1] if (key in prev_target and r - prev_target[key][0] <= 3) else -1
                if key in prev_target and r - prev_target[key][0] <= 3 and prev_target[key][0] < r:
                    pr_, pt = prev_target[key]
                    if pt == tgt: switch['same'] += 1
                    else:
                        switch['switched'] += 1
                        pc = ch.get(pt)
                        if not pc or not pc[4] or pc[2] <= 0: reason = 'prev_dead'
                        elif cheb(rec['apos'], (pc[0], pc[1])) > R: reason = 'prev_out_of_range'
                        elif ch[tgt][2] < pc[2]: reason = 'new_lower_hp'
                        elif ch[tgt][2] / ch[tgt][3] < pc[2] / pc[3]: reason = 'new_lower_hp%'
                        else: reason = 'other'
                        switch['sw_' + reason] += 1
                        if len(examples[reason]) < 3: examples[reason].append('%s r%d %s%d %d->%d' % (m, r, ty, a, pt, tgt))
                prev_target[key] = (r, tgt)
                if len(cands) < 2 or tgt not in dict(cands): continue
                n += 1; ncand.append(len(cands))
                d = dict(cands)
                def argmin(f):
                    v = min(f(c) for i, c in cands); return {i for i, c in cands if f(c) == v}
                picks = {}
                picks['lowest_hp'] = argmin(lambda c: c[2])
                picks['lowest_hp%'] = argmin(lambda c: c[2] / c[3])
                picks['nearest'] = argmin(lambda c: cheb(rec['apos'], (c[0], c[1])))
                picks['most_gems'] = argmin(lambda c: -c[5])
                picks['ranged_first'] = {i for i, c in cands if g['types'][i][1] in RANGED} or set(d)
                picks['lowest_maxhp'] = argmin(lambda c: c[3])
                dmg_now = {i: team_dmg_round.get(i, 0) - (rec['victims'][0][1] if i == tgt else 0) for i, c in cands}
                picks['ally_damaged_this_round'] = {i for i in d if dmg_now[i] > 0} or set(d)
                recent = {i: sum(v for rr, v in hit_by_team[i].items() if r - 3 <= rr < r) for i in d}
                picks['team_hit_last3'] = {i for i in d if recent[i] > 0} or set(d)
                picks['sticky'] = {prevt} if prevt in d else set(d)
                mydmg = rec['victims'][0][1]
                picks['killable'] = {i for i, c in cands if c[2] <= mydmg} or set(d)
                hyp['n'] += 1
                for h, p in picks.items():
                    if tgt in p: hyp[h] += 1; hyp_by_ty[ty][h] += 1
                    hyp[h + '_informative'] += (len(p) < len(d))
                    if len(p) < len(d): hyp[h + '_inf_hit'] += tgt in p
                hyp_by_ty[ty]['n'] += 1
                # pairwise conflicts among key hypotheses (unique picks only)
                for h1, h2 in [('lowest_hp', 'nearest'), ('lowest_hp', 'lowest_hp%'), ('lowest_hp', 'ranged_first'), ('lowest_hp', 'ally_damaged_this_round'), ('lowest_hp', 'most_gems'), ('nearest', 'ranged_first'), ('lowest_hp%', 'ranged_first'), ('lowest_hp', 'sticky'), ('ally_damaged_this_round', 'nearest'), ('nearest', 'sticky'), ('lowest_hp', 'killable')]:
                    p1, p2 = picks[h1], picks[h2]
                    if len(p1) == 1 and len(p2) == 1 and p1 != p2:
                        conflict[(h1, h2, 'n')] += 1
                        if tgt in p1: conflict[(h1, h2, h1)] += 1
                        elif tgt in p2: conflict[(h1, h2, h2)] += 1
    print('=== TEAM', TEAM, 'decisions with >=2 enemies in range:', n, 'mean candidates %.2f' % statistics.mean(ncand), 'random baseline %.2f' % statistics.mean(1 / x for x in ncand))
    for h in ['lowest_hp', 'lowest_hp%', 'nearest', 'most_gems', 'ranged_first', 'lowest_maxhp', 'ally_damaged_this_round', 'team_hit_last3', 'sticky', 'killable']:
        inf = hyp[h + '_informative']
        print('  %-26s hit %.2f   (when hypothesis singles out a subset: n=%d hit %.2f)' % (h, hyp[h] / n, inf, hyp[h + '_inf_hit'] / inf if inf else 0))
    print('  by champion type (n, lowest_hp, nearest, ranged_first, ally_damaged):')
    for ty, c in sorted(hyp_by_ty.items()):
        print('    %-9s n=%4d  low=%.2f near=%.2f ranged=%.2f allydmg=%.2f sticky=%.2f' % (ty, c['n'], c['lowest_hp'] / c['n'], c['nearest'] / c['n'], c['ranged_first'] / c['n'], c['ally_damaged_this_round'] / c['n'], c['sticky'] / c['n']))
    print('  CONFLICTS (when two hypotheses pick different unique targets):')
    for (h1, h2, k), v in sorted(conflict.items()):
        if k == 'n': print('    %s vs %s: n=%d  %s wins %.2f  %s wins %.2f' % (h1, h2, v, h1, conflict[(h1, h2, h1)] / v, h2, conflict[(h1, h2, h2)] / v))
    print('  FOCUS: rounds with team dmg on champions %d, single victim %.2f, mean share on main victim when >=2 victims %.2f' % (focus_rounds['rounds'], focus_rounds['single_victim'] / focus_rounds['rounds'], statistics.mean(share) if share else 0))
    tot = switch['same'] + switch['switched']
    print('  SWITCHING: consecutive hits (<=3 rounds apart) n=%d switched %.2f ; reasons: %s' % (tot, switch['switched'] / tot, {k: round(v / switch['switched'], 2) for k, v in switch.items() if k.startswith('sw_')}))
    for k, v in examples.items(): print('    ex', k, v)

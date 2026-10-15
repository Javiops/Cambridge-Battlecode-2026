"""Q4: action order within a turn; Q5: kill securing / last hits.  python3 -I q4q5_order_kills.py"""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
EXCLUSIVE = {('Cassi', 'dmg'), ('Tavi', 'stundmg'), ('Ren', 'stundmg'), ('Marcella', 'dmg'), ('Stellar', 'single'), ('Stellar', 'aoe'), ('Prism', 'single'), ('Prism', 'aoe'), ('Ryth', 'aoestun')}
for TEAM in ['mite', 'uni']:
    seqs = collections.defaultdict(collections.Counter); order = collections.defaultdict(collections.Counter)
    kills = collections.Counter(); killer_ty = collections.Counter(); weapon = collections.Counter(); hold = collections.Counter(); hold_ex = []
    gems_taken = []; victim_gems = collections.Counter(); kill_by_game = collections.defaultdict(collections.Counter)
    topdmg = collections.Counter()
    for s, g in focus_games(TEAM):
        t = s['t']; m = s['match'][:8]
        dmg_recent = collections.defaultdict(lambda: collections.defaultdict(float))  # victim -> attacker -> dmg (last 4 rounds, decayed by reset)
        dmg_hist = collections.defaultdict(list)  # victim -> [(r, attacker, dmg)]
        round_turns = collections.defaultdict(list)
        for r, a, team, ty, acts in iterate_turns(g):
            round_turns[r].append((a, team, ty, acts))
        for r in sorted(round_turns):
            for a, team, ty, acts in round_turns[r]:
                for rec in acts:
                    for v in rec['victims']: dmg_hist[v[0]].append((r, a, v[1]))
                if team != t: continue
                kinds = [x['kind'] if x['kind'] != 'cast' else ('cast:' + x['slot']) for x in acts]
                hits_champ = any(x['victims'] for x in acts)
                hits_camp = any(x['kvictims'] for x in acts)
                if hits_champ or hits_camp:
                    tag = 'champ' if hits_champ else 'camp'
                    ks = [k.split(':')[0] for k in kinds]
                    seqs[(ty, tag)][' '.join(k for k in kinds if k != 'other')] += 1
                    if 'mv' in ks and 'atk' in ks:
                        order[(ty, tag)]['atk_then_mv' if ks.index('atk') < ks.index('mv') else 'mv_then_atk'] += 1
                        # for melee: hit then step away or step toward?
                    elif 'atk' in ks: order[(ty, tag)]['atk_no_move'] += 1
                    for j, x in enumerate(acts):
                        if x['kind'] == 'cast':
                            ex = (ty, x['slot']) in EXCLUSIVE
                            moved_before = any(y['kind'] == 'mv' for y in acts[:j]); moved_after = any(y['kind'] == 'mv' for y in acts[j + 1:])
                            order[(ty, tag)][('excl_' if ex else 'free_') + ('cast_then_mv' if moved_after else ('mv_then_cast' if moved_before else 'cast_no_move'))] += 1
                            if x['dashed']:
                                order[(ty, tag)]['dash_then_atk' if any(y['kind'] == 'atk' for y in acts[j + 1:]) else ('atk_then_dash' if any(y['kind'] == 'atk' for y in acts[:j]) else 'dash_only')] += 1
                # kills
                for j, rec in enumerate(acts):
                    for vi in rec['kills']:
                        if g['types'][vi][0] == t: continue
                        kills['n'] += 1; killer_ty[ty] += 1; kill_by_game[m][ty] += 1
                        weapon['spell' if rec['kind'] == 'cast' else 'atk'] += 1
                        gems_taken.append(rec['gems']); victim_gems['victim_had_gems'] += rec['before'][0][vi][5] > 0
                        # top damage dealer in last 4 rounds
                        dd = collections.defaultdict(float)
                        for rr, at, d in dmg_hist[vi]:
                            if r - 4 <= rr <= r: dd[at] += d
                        if dd: topdmg['killer_is_top_dmg'] += max(dd, key=dd.get) == a; topdmg['n'] += 1
                        # holding: allies that acted earlier this round with the victim in range but did not attack it
                        vc = rec['before'][0][vi]
                        for a2, team2, ty2, acts2 in round_turns[r]:
                            if team2 != t or a2 == a: continue
                            if acts2 and acts2[0]['r'] == r and round_turns[r].index((a2, team2, ty2, acts2)) < round_turns[r].index((a, team, ty, acts)):
                                p2 = acts2[0]['apos']
                                if cheb(p2, (vc[0], vc[1])) <= atk_range(ty2) and acts2[0]['before'][0][vi][4]:
                                    hold['ally_in_range_acted_before'] += 1
                                    hitv = any(v[0] == vi for x in acts2 for v in x['victims'])
                                    if hitv: hold['ally_hit_victim'] += 1
                                    elif any(x['victims'] for x in acts2): hold['ally_hit_other'] += 1
                                    else:
                                        hold['ally_did_not_attack'] += 1
                                        if len(hold_ex) < 4: hold_ex.append('%s r%d %s%d in range of victim %s%d (hp %d) did not attack; %s%d killed' % (m, r, ty2, a2, g['types'][vi][1], vi, acts2[0]['before'][0][vi][2], ty, a))
    print('=== TEAM', TEAM)
    print('  ACTION ORDER (turns that hit something):')
    for k, c in sorted(order.items()): print('    %-20s %s' % (k, dict(c.most_common())))
    print('  TOP SEQUENCES:')
    for k, c in sorted(seqs.items()): print('    %-20s %s' % (k, c.most_common(5)))
    print('  KILLS n=%d by type %s weapon %s' % (kills['n'], dict(killer_ty.most_common()), dict(weapon)))
    print('  killer is top damage dealer (last 4 rounds): %.2f' % (topdmg['killer_is_top_dmg'] / max(1, topdmg['n'])))
    print('  gems taken per kill: mean %.1f, kills where victim carried gems %.2f' % (statistics.mean(gems_taken) if gems_taken else 0, victim_gems['victim_had_gems'] / max(1, kills['n'])))
    print('  HOLDING (allies in range of victim who acted earlier in the kill round): %s' % dict(hold))
    for e in hold_ex: print('    ex', e)
    # kill share per game of the most-killing type
    shares = []
    for m, c in kill_by_game.items():
        tot = sum(c.values()); shares.append(max(c.values()) / tot)
    print('  per game: share of kills by the top killer type: mean %.2f' % statistics.mean(shares))

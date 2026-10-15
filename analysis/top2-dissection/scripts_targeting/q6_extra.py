"""Extra measurements: camp first-hit by group composition, aggro holder vs presence, camp-spell usage while farming,
Stellar/Prism slot choice when both available, Cassi stun on monsters, focus with >=2 attackers, stun vs recall, examples.
python3 -I q6_extra.py"""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
DMG_SPELLS = {('Cassi', 'dmg'), ('Tavi', 'stundmg'), ('Ren', 'stundmg'), ('Marcella', 'dmg'), ('Stellar', 'single'), ('Stellar', 'aoe'), ('Prism', 'single'), ('Prism', 'aoe'), ('Ryth', 'aoestun')}
for TEAM in ['mite', 'uni']:
    comp = collections.Counter(); aggro = collections.Counter(); present = collections.Counter()
    campspell = collections.Counter(); choice = collections.Counter(); cstun = collections.Counter(); focus2 = collections.Counter()
    recall = collections.Counter(); ex = collections.defaultdict(list); nhit_eng = []
    group_last = {}
    for s, g in focus_games(TEAM):
        t = s['t']; m = s['match'][:8]
        last = collections.defaultdict(lambda: -99)
        recall_start = {}
        mon_attacks = collections.defaultdict(set)  # r -> monsters that attacked
        for r in g['order']:
            for e in g['events'][r]:
                if e['ak'] == 2 and e['k'] == 5: mon_attacks[r].add(e['a'])
        eng = {}  # (grp) -> dict(start, hitters set, first_hit_victim)
        turns = list(iterate_turns(g))
        round_turns = collections.defaultdict(list)
        for r, a, team, ty, acts in turns: round_turns[r].append((a, team, ty, acts))
        for r, a, team, ty, acts in turns:
            for rec in acts:
                if rec['k'] == 11: recall_start[a] = r
                if rec['kind'] == 'mv' and rec['to'] != rec['apos']: recall_start.pop(a, None)
            if team != t: continue
            ch, cs = acts[0]['before']; apos0 = acts[0]['apos']
            enemies4 = [(i, c) for i, c in ch.items() if g['types'][i][0] != t and c[4] and c[2] > 0 and cheb(apos0, (c[0], c[1])) <= 4]
            cast_slots = {x['slot']: x for x in acts if x['kind'] == 'cast'}
            # Stellar / Prism choice when both available and an enemy champion is in range
            if ty in ('Stellar', 'Prism') and enemies4 and r - last[(a, 'single')] >= 8 and r - last[(a, 'aoe')] >= 8:
                choice[(ty, 'both_avail_enemy_in4')] += 1
                if 'single' in cast_slots: choice[(ty, 'chose_single')] += 1
                elif 'aoe' in cast_slots: choice[(ty, 'chose_aoe')] += 1
                else: choice[(ty, 'no_cast')] += 1
                # cluster available?
                best = 0
                for x in range(apos0[0] - 4, apos0[0] + 5):
                    for y in range(apos0[1] - 4, apos0[1] + 5):
                        best = max(best, sum(1 for i, c in enemies4 if cheb((x, y), (c[0], c[1])) <= 1))
                if best >= 2:
                    choice[(ty, 'both_avail_cluster2')] += 1
                    if 'aoe' in cast_slots: choice[(ty, 'cluster2_chose_aoe')] += 1
                    elif 'single' in cast_slots: choice[(ty, 'cluster2_chose_single')] += 1
            # camp-spell usage while actually farming (basic-attacked a camp this turn, no enemy champion within 6)
            atkc = [x for x in acts if x['kind'] == 'atk' and x['kvictims']]
            enemies6 = [(i, c) for i, c in ch.items() if g['types'][i][0] != t and c[4] and cheb(apos0, (c[0], c[1])) <= 6]
            if atkc and not enemies6:
                ci = atkc[0]['kvictims'][0][0]; mon = cs[ci]
                for slot in ('dmg', 'stundmg', 'single', 'aoe', 'aoestun', 'stun', 'shield'):
                    if (ty, slot) in DMG_SPELLS or (ty, slot) in {('Cassi', 'stun'), ('Varg', 'shield')}:
                        if r - last[(a, slot)] >= 8:
                            campspell[(ty, slot, 'farm_opp')] += 1
                            campspell[(ty, slot, 'farm_opp', mon[5])] += 1
                            if slot in cast_slots:
                                campspell[(ty, slot, 'farm_used')] += 1; campspell[(ty, slot, 'farm_used', mon[5])] += 1
                                campspell[(ty, slot, 'farm_used_awake' if mon[4] else 'farm_used_asleep')] += 1
                            else: campspell[(ty, slot, 'farm_skip_awake' if mon[4] else 'farm_skip_asleep')] += 1
            # Cassi stun on monsters
            if ty == 'Cassi' and 'stun' in cast_slots:
                rec = cast_slots['stun']; ch2, cs2 = rec['before']
                en = [(i, c) for i, c in ch2.items() if g['types'][i][0] != t and c[4] and c[2] > 0 and cheb(rec['apos'], (c[0], c[1])) <= 4]
                mons = [(i, c) for i, c in cs2.items() if c[3] and c[4] and cheb(rec['apos'], (c[0], c[1])) <= 4]
                if not en and mons:
                    cstun['camp_stun'] += 1
                    # monster that attacked last round but not this/next round
                    skipped = [i for i, c in mons if i in mon_attacks.get(r - 1, set()) and i not in mon_attacks.get(r, set()) | mon_attacks.get(r + 1, set())]
                    cstun['monster_skips_attack'] += bool(skipped)
                    # who was the monster hitting? Cassi herself?
                    cassi_hit_prev = any(x.get('hp', 0) < 0 and x['i'] == a for e in g['events'].get(r - 1, []) if e['ak'] == 2 for x in e['eff'])
                    cstun['cassi_was_being_hit'] += cassi_hit_prev
                    ally_hit_prev = any(x.get('hp', 0) < 0 and g['types'][x['i']][0] == t for e in g['events'].get(r - 1, []) if e['ak'] == 2 for x in e['eff'])
                    cstun['team_was_being_hit'] += ally_hit_prev
                    cstun['cassi_attacks_camp_same_turn'] += bool(atkc)
                    if len(ex['cassi_camp_stun']) < 3 and skipped: ex['cassi_camp_stun'].append('%s r%d Cassi%d stuns %s%d (monster skips its attack)' % (m, r, a, cs2[skipped[0]][5], skipped[0]))
                elif en:
                    cstun['champ_stun'] += 1
                    tg = [i for i, c in en if i in recall_start and recall_start[i] < r and r - recall_start[i] <= 5]
                    cstun['target_recalling'] += bool(tg)
                    if tg and len(ex['cassi_stun_recall']) < 3: ex['cassi_stun_recall'].append('%s r%d Cassi%d stun with %s%d recalling (started r%d)' % (m, r, a, g['types'][tg[0]][1], tg[0], recall_start[tg[0]]))
            # stun spells vs recalling targets (Tavi, Ren, Ryth, Prism single)
            for slot, rec in cast_slots.items():
                if (ty, slot) in {('Tavi', 'stundmg'), ('Ren', 'stundmg'), ('Ryth', 'aoestun'), ('Prism', 'single')} and rec['victims']:
                    vi = rec['victims'][0][0]
                    recall[(ty, 'n')] += 1
                    if vi in recall_start and recall_start[vi] < r and r - recall_start[vi] <= 5:
                        recall[(ty, 'target_recalling')] += 1
                        if len(ex['stun_recall']) < 4: ex['stun_recall'].append('%s r%d %s%d %s on recalling %s%d (recall started r%d)' % (m, r, ty, a, slot, g['types'][vi][1], vi, recall_start[vi]))
            # recall interrupts by any damage: how often is an enemy recall interrupted by this team (first hit after recall start)?
            for rec in acts:
                for v in rec['victims']:
                    vi = v[0]
                    if vi in recall_start and recall_start[vi] < r and r - recall_start[vi] <= 5:
                        recall[('any', 'hits_on_recalling')] += 1
                        recall[('any', 'by_spell' if rec['kind'] == 'cast' else 'by_atk')] += 1
                        recall_start.pop(vi, None)
            for slot in cast_slots: last[(a, slot)] = r
            # camp engagements: composition & aggro
            for rec in acts:
                if not rec['kvictims']: continue
                ch2, cs2 = rec['before']; ci = rec['kvictims'][0][0]; grp = cs2[ci][6]; key = (m, grp)
                if r - group_last.get(key, -99) >= 12:
                    mons = [(i, c) for i, c in cs2.items() if c[6] == grp and c[3]]
                    tys = tuple(sorted(c[5] for i, c in mons))
                    if len(set(tys)) >= 2:
                        comp[(tys, 'first=' + cs2[ci][5])] += 1
                    big = max(mons, key=lambda x: x[1][2])
                    if len(mons) >= 2 and len({c[2] for i, c in mons}) >= 2:
                        comp[('mixed_hp', 'first_is_highest_hp')] += ci == big[0]; comp[('mixed_hp', 'n')] += 1
                    eng[key] = dict(start=r, hitters={a}, first=(a, ty), tank=None)
                group_last[key] = r
                if key in eng: eng[key]['hitters'].add(a)
                break
        # aggro: first monster hit of each engagement on this team
        for key, E in eng.items():
            grp = key[1]; r0 = E['start']
            nhit_eng.append(len(E['hitters']))
            for r in range(r0, r0 + 15):
                hit = None
                for e in g['events'].get(r, []):
                    if e['ak'] == 2 and e['k'] == 5 and g['camps0'][e['a']]['group'] == grp:
                        for x in e['eff']:
                            if x.get('hp', 0) < 0 and g['types'][x['i']][0] == t: hit = x['i']
                    if hit is not None: break
                if hit is not None:
                    vt = g['types'][hit][1]
                    aggro['n'] += 1; aggro['first_hitter_is_tank'] += hit == E['first'][0]
                    aggro['tank_' + ('melee' if vt in MELEE else 'ranged')] += 1
                    # ranged present (hitters) but melee tanks?
                    hit_tys = {g['types'][h][1] for h in E['hitters']}
                    if any(x in MELEE for x in hit_tys) and any(x in RANGED for x in hit_tys):
                        aggro['mixed_n'] += 1; aggro['mixed_melee_tanks'] += vt in MELEE
                    break
        # focus when >=2 attackers hit champions in a round
        for r, lst in round_turns.items():
            victims_by_attacker = {}
            for a, team, ty, acts in lst:
                if team != t: continue
                vs = {v[0] for x in acts for v in x['victims']}
                if vs: victims_by_attacker[a] = vs
            if len(victims_by_attacker) >= 2:
                focus2['rounds'] += 1
                allv = set().union(*victims_by_attacker.values())
                focus2['all_same_victim'] += len(allv) == 1
                # were there >=2 distinct enemies in range of at least two attackers? (choice existed)
    print('=== TEAM', TEAM)
    print('  CAMP first hit by group composition: %s' % {k: v for k, v in sorted(comp.items(), key=str)})
    print('  AGGRO: %s  | champions hitting per engagement: %s' % (dict(aggro), collections.Counter(nhit_eng).most_common(4)))
    print('  CAMP-SPELL usage while farming (basic-attacked a camp this turn, no enemy within 6, slot available):')
    keys = sorted({(k[0], k[1]) for k in campspell})
    for ty, slot in keys:
        o = campspell[(ty, slot, 'farm_opp')]; u = campspell[(ty, slot, 'farm_used')]
        bytype = {mt: '%.2f(n%d)' % (campspell[(ty, slot, 'farm_used', mt)] / campspell[(ty, slot, 'farm_opp', mt)], campspell[(ty, slot, 'farm_opp', mt)]) for mt in ('elk', 'wolf', 'gem_cluster', 'gold_cluster') if campspell[(ty, slot, 'farm_opp', mt)]}
        ua, sa = campspell[(ty, slot, 'farm_used_awake')], campspell[(ty, slot, 'farm_skip_awake')]; us, ss = campspell[(ty, slot, 'farm_used_asleep')], campspell[(ty, slot, 'farm_skip_asleep')]
        print('    %-8s %-8s used %.2f (n=%d) by monster %s | awake %.2f (n=%d) asleep %.2f (n=%d)' % (ty, slot, u / o if o else 0, o, bytype, ua / (ua + sa) if ua + sa else 0, ua + sa, us / (us + ss) if us + ss else 0, us + ss))
    print('  STELLAR/PRISM slot choice when both slots available and enemy in 4: %s' % dict(choice))
    print('  CASSI STUN: %s' % dict(cstun))
    print('  STUN vs RECALL: %s' % dict(recall))
    print('  FOCUS with >=2 attackers in a round: %s (%.2f same victim)' % (dict(focus2), focus2['all_same_victim'] / max(1, focus2['rounds'])))
    for k, v in ex.items(): print('    ex', k, v)

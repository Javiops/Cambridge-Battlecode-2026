"""Examples + small checks: Cassi camp stun effect, target-choice examples, multi-target casts, dash as travel.  python3 -I q7_examples.py"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
SINGLE = {('Cassi', 'dmg'), ('Tavi', 'stundmg'), ('Ren', 'stundmg'), ('Marcella', 'dmg'), ('Stellar', 'single'), ('Prism', 'single')}
for TEAM in ['mite', 'uni']:
    ex = collections.defaultdict(list); cst = collections.Counter(); dash = collections.Counter(); multi = collections.Counter()
    prev_target = {}
    for s, g in focus_games(TEAM):
        t = s['t']; m = s['match'][:8]
        mon_attacks = collections.defaultdict(set)
        for r in g['order']:
            for e in g['events'][r]:
                if e['ak'] == 2 and e['k'] == 5: mon_attacks[r].add(e['a'])
        for r, a, team, ty, acts in iterate_turns(g):
            if team != t: continue
            kinds = [x['kind'] for x in acts]
            for j, rec in enumerate(acts):
                ch, cs = rec['before']
                if rec['kind'] == 'cast' and rec['slot'] == 'dash':
                    dash['n'] += 1; dash['with_walk_same_turn'] += 'mv' in kinds
                    en = [c for i, c in ch.items() if g['types'][i][0] != t and c[4] and cheb(rec['apos'], (c[0], c[1])) <= 8]
                    dash['no_enemy_within8'] += not en
                if ty == 'Cassi' and rec['kind'] == 'cast' and rec['slot'] == 'stun':
                    en = [i for i, c in ch.items() if g['types'][i][0] != t and c[4] and c[2] > 0 and cheb(rec['apos'], (c[0], c[1])) <= 4]
                    mons = [i for i, c in cs.items() if c[3] and c[4] and cheb(rec['apos'], (c[0], c[1])) <= 4]
                    if not en and mons:
                        cst['camp_stun_awake_mon_in4'] += 1
                        att_next = any(i in mon_attacks.get(r + 1, set()) for i in mons)
                        att_prev = any(i in mon_attacks.get(r - 1, set()) for i in mons)
                        cst['mon_attacked_prev_round'] += att_prev; cst['mon_attacks_next_round'] += att_next
                        cst['prev_yes_next_no'] += att_prev and not att_next
                        cst['mon_type_' + cs[mons[0]][5]] += 1
                if rec['kind'] == 'cast' and rec['slot'] in ('aoe', 'aoestun') and len(rec['victims']) >= 3 and len(ex['multi_' + ty]) < 3:
                    ex['multi_' + ty].append('%s r%d %s%d %s hits %d champions: %s' % (m, r, ty, a, rec['slot'], len(rec['victims']), [(g['types'][v[0]][1], v[1]) for v in rec['victims']]))
                if rec['kind'] == 'cast' and rec['slot'] in ('aoe', 'aoestun'):
                    multi[(ty, 'n_on_champs')] += bool(rec['victims']); multi[(ty, '2plus')] += len(rec['victims']) >= 2
                if ty in ('Tavi', 'Willow', 'VesperVale') and rec['kind'] == 'cast' and rec['slot'] == 'reset' and 'mv' in kinds[:j] and any(x['kind'] == 'atk' and x['victims'] for x in acts[j + 1:]) and len(ex['ranged_move_reset_shoot']) < 3:
                    ex['ranged_move_reset_shoot'].append('%s r%d %s%d walks, resets, shoots %s' % (m, r, ty, a, [(g['types'][v[0]][1], v[1]) for x in acts[j + 1:] for v in x['victims']]))
                # target choice conflict examples
                if (rec['kind'] == 'atk' or (rec['kind'] == 'cast' and (ty, rec['slot']) in SINGLE)) and rec['victims']:
                    R = atk_range(ty) if rec['kind'] == 'atk' else 4
                    tgt = rec['victims'][0][0]
                    cands = [(i, c) for i, c in ch.items() if g['types'][i][0] != t and c[4] and c[2] > 0 and cheb(rec['apos'], (c[0], c[1])) <= R]
                    if len(cands) >= 2:
                        low = min(cands, key=lambda x: x[1][2]); near = min(cands, key=lambda x: cheb(rec['apos'], (x[1][0], x[1][1])))
                        nd = cheb(rec['apos'], (near[1][0], near[1][1]))
                        uniq_near = sum(1 for i, c in cands if cheb(rec['apos'], (c[0], c[1])) == nd) == 1
                        if uniq_near and low[0] != near[0]:
                            desc = '%s r%d %s%d (%s) hits %s%d hp%d d%d; alternatives %s' % (m, r, ty, a, 'atk' if rec['kind'] == 'atk' else rec['slot'], g['types'][tgt][1], tgt, ch[tgt][2], cheb(rec['apos'], (ch[tgt][0], ch[tgt][1])), [(g['types'][i][1], c[2], cheb(rec['apos'], (c[0], c[1]))) for i, c in cands if i != tgt])
                            key = 'picked_nearest' if tgt == near[0] else ('picked_lowest' if tgt == low[0] else 'picked_other')
                            if len(ex[key]) < 3: ex[key].append(desc)
    print('=== TEAM', TEAM)
    print('  CASSI camp stun check:', dict(cst))
    print('  DASH:', dict(dash))
    print('  AOE casts on champions hitting 2+:', {k: v for k, v in multi.items()})
    for k, v in sorted(ex.items()):
        print('  ', k); [print('     ', e) for e in v]

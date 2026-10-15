"""Q2: targeting on camps: first monster hit, same-monster share, attack distance, who tanks.  python3 -I q2_camps.py"""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
for TEAM in ['mite', 'uni']:
    first = collections.Counter(); samemon = collections.Counter(); dist = collections.defaultdict(collections.Counter)
    tank = collections.Counter(); tank_present = collections.Counter(); firsthitter = collections.Counter(); aggro = collections.Counter()
    spells_on_camp = collections.Counter(); engage_ex = []
    group_last = {}
    monster_hp0 = {}
    for s, g in focus_games(TEAM):
        t = s['t']; m = s['match'][:8]
        ctypes = {i: c['ty'] for i, c in g['camps0'].items()}
        for i, c in g['camps0'].items(): monster_hp0[c['ty']] = c['hp']
        round_hits = collections.defaultdict(lambda: collections.defaultdict(set))  # r -> group -> set(monster)
        round_attackers = collections.defaultdict(lambda: collections.defaultdict(set))
        eng_first_hitter = {}
        for r, a, team, ty, acts in iterate_turns(g):
            if team != t: continue
            for rec in acts:
                if not rec['kvictims']: continue
                ch, cs = rec['before']
                for (ci, dmg, hpnow, alive) in rec['kvictims'][:1]:
                    grp = cs[ci][6]
                    key = (m, grp)
                    if r - group_last.get(key, -99) >= 12:
                        # new engagement: describe group state
                        mons = [(i, c) for i, c in cs.items() if c[6] == grp and c[3]]
                        first['engagements'] += 1
                        first['type_' + cs[ci][5]] += 1
                        if len(mons) >= 2:
                            first['multi'] += 1
                            if cs[ci][2] == min(c[2] for i, c in mons): first['multi_lowest_hp'] += 1
                            if cs[ci][2] == max(c[2] for i, c in mons): first['multi_highest_hp'] += 1
                            if cs[ci][4]: first['multi_awake'] += 1
                            if cheb(rec['apos'], (cs[ci][0], cs[ci][1])) == min(cheb(rec['apos'], (c[0], c[1])) for i, c in mons): first['multi_nearest'] += 1
                            if cs[ci][5] == 'gold_cluster': first['multi_gold_first'] += 1
                            if len(engage_ex) < 4: engage_ex.append('%s r%d %s%d hits %s%d (%d hp) of group %s' % (m, r, ty, a, cs[ci][5], ci, cs[ci][2], [(c[5], c[2]) for i, c in mons]))
                        firsthitter[ty] += 1
                        eng_first_hitter[key] = (r, a, ty)
                    group_last[key] = r
                    round_hits[r][grp].add(ci); round_attackers[r][grp].add(a)
                    d = cheb(rec['apos'], (cs[ci][0], cs[ci][1]))
                    dist[(ty, 'atk' if rec['kind'] == 'atk' else 'spell')][d] += 1
                    if rec['kind'] == 'cast': spells_on_camp[(ty, rec['slot'])] += 1
        for r, gd in round_hits.items():
            for grp, mons in gd.items():
                if len(round_attackers[r][grp]) >= 2:
                    samemon['rounds_2plus_attackers'] += 1
                    if len(mons) == 1: samemon['same_monster'] += 1
        # who tanks: monster attacks on focus team
        for r in g['order']:
            for e in g['events'][r]:
                if e['ak'] == 2 and e['k'] == 5:
                    for x in e['eff']:
                        if x.get('hp', 0) < 0 and g['types'][x['i']][0] == t:
                            vt = g['types'][x['i']][1]; tank[vt] += 1
                            ci = e['a']; cpos = None
                            # present: focus-team champions within 3 of the monster (snapshot of round)
                            snap = g['rounds'][r]
                            if ci in g['camps0']:
                                # find monster pos from round snapshot
                                pass
                            for i, c in snap.items():
                                if c['team'] == t and c['alive']: tank_present[c['ty']] += 0
                            # was the tank the first hitter of this group?
                            grp = g['camps0'][ci]['group']
                            fh = eng_first_hitter.get((m, grp))
                            if fh and r - fh[0] <= 12: aggro['first_hitter_tanks' if fh[1] == x['i'] else 'other_tanks'] += 1
    print('=== TEAM', TEAM)
    print('  FIRST MONSTER of an engagement: %s' % dict(first))
    print('  first hitter by type: %s' % dict(firsthitter))
    print('  SAME MONSTER when >=2 champions hit the group in a round: %.2f (n=%d)' % (samemon['same_monster'] / max(1, samemon['rounds_2plus_attackers']), samemon['rounds_2plus_attackers']))
    print('  ATTACK DISTANCE to monster per type:')
    for k, v in sorted(dist.items()): print('    ', k, sorted(v.items()))
    print('  MONSTER HITS TAKEN by type (who tanks): %s' % dict(tank.most_common()))
    print('  aggro: %s' % dict(aggro))
    print('  spells cast on camps by (type, slot): %s' % dict(spells_on_camp.most_common()))
    for e in engage_ex: print('    ex', e)

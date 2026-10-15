"""Q3: spell usage per champion type and slot: usage rate when off cooldown, distance, target class, contexts,
spell damage share.  python3 -I q3_spells.py"""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
DMG_SPELLS = {('Cassi', 'dmg'), ('Tavi', 'stundmg'), ('Ren', 'stundmg'), ('Marcella', 'dmg'), ('Stellar', 'single'), ('Stellar', 'aoe'), ('Prism', 'single'), ('Prism', 'aoe'), ('Ryth', 'aoestun')}
SLOTS = {'Cassi': ['dmg', 'stun'], 'Issac': ['reset', 'dash'], 'Ryth': ['aoestun', 'reset'], 'VesperVale': ['reset', 'dash'], 'Prism': ['single', 'aoe'], 'Stellar': ['single', 'aoe'],
         'Vendetta': ['reset', 'dash'], 'Marcella': ['reset', 'dmg'], 'Tavi': ['reset', 'stundmg'], 'Willow': ['heal', 'reset'], 'Ren': ['stundmg', 'dash'], 'Varg': ['reset', 'shield']}
def pct(a, b): return '%.2f' % (a / b) if b else '-'
for TEAM in ['mite', 'uni']:
    casts = collections.Counter(); dists = collections.defaultdict(collections.Counter); nvict = collections.defaultdict(collections.Counter)
    opp = collections.Counter(); gap8 = collections.Counter()
    ctx = collections.defaultdict(collections.Counter); ctx_ex = collections.defaultdict(list)
    dmg = collections.defaultdict(float)  # (type, 'atk'/'spell', 'champ'/'camp') -> dmg
    games = 0
    for s, g in focus_games(TEAM):
        t = s['t']; m = s['match'][:8]; games += 1
        last = collections.defaultdict(lambda: -99)   # (a, slot) -> round
        chan = {}  # champion -> round of last channel start (recall k11 / tribute k18)
        moved_since = {}
        acted_round = collections.defaultdict(set)  # champion -> rounds in which it acted (for stun detection)
        turns = list(iterate_turns(g))
        for r, a, team, ty, acts in turns:
            acted_round[a].add(r)
            for rec in acts:
                if rec['k'] in (11, 18): chan[a] = r
                if rec['kind'] == 'mv' and rec['to'] != rec['apos']: chan.pop(a, None)
        # map r -> index for lookahead of positions
        def pos_at(i, r):
            rr = max([x for x in g['order'] if x <= r] or [0]); c = g['rounds'][rr][i]; return (c['x'], c['y']), c['hp'], c['alive']
        prev_dist = {}
        for r, a, team, ty, acts in turns:
            if team != t: continue
            ch, cs = rec_before = acts[0]['before'] if acts else ({}, {})
            apos0 = acts[0]['apos'] if acts else None
            # opportunities per slot (evaluated at turn start)
            enemies4 = [(i, c) for i, c in ch.items() if g['types'][i][0] != t and c[4] and c[2] > 0 and cheb(apos0, (c[0], c[1])) <= 4]
            camps4 = [(i, c) for i, c in cs.items() if c[3] and cheb(apos0, (c[0], c[1])) <= 4]
            atk_champ = any(x['kind'] == 'atk' and x['victims'] for x in acts)
            atk_camp = any(x['kind'] == 'atk' and x['kvictims'] for x in acts)
            cast_slots = {x['slot'] for x in acts if x['kind'] == 'cast'}
            for slot in SLOTS.get(ty, []):
                avail = r - last[(a, slot)] >= 8
                if not avail: continue
                if (ty, slot) in DMG_SPELLS or (ty, slot) in {('Cassi', 'stun')}:
                    if enemies4: opp[(ty, slot, 'champ_in4')] += 1; opp[(ty, slot, 'champ_in4_used')] += slot in cast_slots
                    elif camps4: opp[(ty, slot, 'camp_only')] += 1; opp[(ty, slot, 'camp_only_used')] += slot in cast_slots
                elif slot == 'reset':
                    if atk_champ: opp[(ty, slot, 'atk_champ')] += 1; opp[(ty, slot, 'atk_champ_used')] += slot in cast_slots
                    elif atk_camp: opp[(ty, slot, 'atk_camp')] += 1; opp[(ty, slot, 'atk_camp_used')] += slot in cast_slots
                elif slot == 'shield':
                    if enemies4: opp[(ty, slot, 'champ_in4')] += 1; opp[(ty, slot, 'champ_in4_used')] += slot in cast_slots
                    elif camps4: opp[(ty, slot, 'camp_only')] += 1; opp[(ty, slot, 'camp_only_used')] += slot in cast_slots
            for j, rec in enumerate(acts):
                if rec['kind'] == 'atk':
                    for v in rec['victims']: dmg[(ty, 'atk', 'champ')] += v[1]
                    for v in rec['kvictims']: dmg[(ty, 'atk', 'camp')] += v[1]
                if rec['kind'] != 'cast': continue
                slot = rec['slot']; k = (ty, slot)
                for v in rec['victims']: dmg[(ty, 'spell', 'champ')] += v[1]
                for v in rec['kvictims']: dmg[(ty, 'spell', 'camp')] += v[1]
                casts[k] += 1
                if r - last[(a, slot)] == 8: gap8[k] += 1
                if last[(a, slot)] > -99: gap8[k + ('n',)] += 1
                last[(a, slot)] = r
                ch, cs = rec['before']
                if rec['victims']: casts[k + ('champ',)] += 1
                elif rec['kvictims']: casts[k + ('camp',)] += 1
                else: casts[k + ('none',)] += 1
                if rec['victims'] or rec['kvictims']:
                    tgt = rec['victims'][0] if rec['victims'] else rec['kvictims'][0]
                    tp = ch[tgt[0]] if rec['victims'] else cs[tgt[0]]
                    dists[k][cheb(rec['apos'], (tp[0], tp[1]))] += 1
                    nvict[k][(len(rec['victims']), len(rec['kvictims']))] += 1
                # ---- contexts
                if slot in ('stundmg', 'dmg') and rec['victims'] and ty in ('Tavi', 'Cassi', 'Ren', 'Marcella'):
                    vi, d, hpnow, alive = rec['victims'][0]; vc = ch[vi]
                    c = ctx[k]; c['n'] += 1
                    c['kill_now'] += hpnow <= 0
                    # died within 2 rounds
                    _, hp2, al2 = pos_at(vi, r + 2)
                    c['dead_in2'] += (not al2) or hp2 <= 0
                    c['target_hp%<35'] += vc[2] / vc[3] < 0.35
                    c['target_channeling'] += vi in chan and r - chan[vi] <= 5 and chan[vi] < r
                    pd = prev_dist.get((a, vi))
                    c['target_was_fleeing'] += pd is not None and cheb(rec['apos'], (vc[0], vc[1])) > pd
                    c['first_hit_of_fight'] += 0
                    c['caster_hp%<40'] += ch[a][2] / ch[a][3] < 0.4
                    if slot == 'stundmg' and (vi in chan and r - chan[vi] <= 5 and chan[vi] < r) and len(ctx_ex[k + ('chan',)]) < 3: ctx_ex[k + ('chan',)].append('%s r%d %s%d stuns %s%d (channeling)' % (m, r, ty, a, g['types'][vi][1], vi))
                    if slot == 'stundmg' and hpnow <= 0 and len(ctx_ex[k + ('kill',)]) < 3: ctx_ex[k + ('kill',)].append('%s r%d %s%d kills %s%d with spell' % (m, r, ty, a, g['types'][vi][1], vi))
                if ty == 'Cassi' and slot == 'stun':
                    c = ctx[k]; c['n'] += 1
                    en = [(i, cc) for i, cc in ch.items() if g['types'][i][0] != t and cc[4] and cc[2] > 0 and cheb(rec['apos'], (cc[0], cc[1])) <= 4]
                    stunned = [i for i, cc in en if (r + 1) not in acted_round[i] and (r + 1) in [x for x in g['order']]]
                    c['enemy_in4'] += bool(en); c['enemy_skips_next_turn'] += bool(stunned)
                    cm = [(i, cc) for i, cc in cs.items() if cc[3] and cheb(rec['apos'], (cc[0], cc[1])) <= 4]
                    c['no_enemy_but_camp'] += (not en) and bool(cm)
                    c['nothing_in4'] += (not en) and not cm
                    if en:
                        tg = stunned[0] if stunned else en[0][0]; vc = ch[tg]
                        c['target_hp%<35'] += vc[2] / vc[3] < 0.35
                        c['target_channeling'] += tg in chan and r - chan[tg] <= 5 and chan[tg] < r
                        c['cassi_hp%<40'] += ch[a][2] / ch[a][3] < 0.4
                        pd = prev_dist.get((a, tg)); c['target_was_fleeing'] += pd is not None and cheb(rec['apos'], (vc[0], vc[1])) > pd
                        c['cassi_moves_away_after'] += any(x['kind'] == 'mv' and cheb(x['to'], (vc[0], vc[1])) > cheb(x['apos'], (vc[0], vc[1])) for x in acts[j + 1:])
                        c['cassi_also_casts_dmg_same_turn'] += 0
                        if (tg in chan and r - chan[tg] <= 5 and chan[tg] < r) and len(ctx_ex[k + ('chan',)]) < 3: ctx_ex[k + ('chan',)].append('%s r%d Cassi%d stun, %s%d channeling' % (m, r, a, g['types'][tg][1], tg))
                if slot == 'dash':
                    c = ctx[k]; c['n'] += 1
                    en = [(i, cc) for i, cc in ch.items() if g['types'][i][0] != t and cc[4] and cc[2] > 0]
                    if en:
                        near = min(en, key=lambda e: cheb(rec['apos'], (e[1][0], e[1][1])))
                        d0 = cheb(rec['apos'], (near[1][0], near[1][1])); d1 = cheb(rec['to'], (near[1][0], near[1][1]))
                        if d0 <= 6:
                            c['enemy_within6'] += 1
                            c['toward_enemy'] += d1 < d0; c['away_from_enemy'] += d1 > d0
                            c['attack_after_dash'] += any(x['kind'] == 'atk' and x['victims'] for x in acts[j + 1:])
                            c['hp%<40_at_dash'] += ch[a][2] / ch[a][3] < 0.4
                            if d1 > d0 and len(ctx_ex[k + ('escape',)]) < 3: ctx_ex[k + ('escape',)].append('%s r%d %s%d dash away (hp %d/%d)' % (m, r, ty, a, ch[a][2], ch[a][3]))
                        else: c['no_enemy_near'] += 1
                    else: c['no_enemy_near'] += 1
                    cm = [(i, cc) for i, cc in cs.items() if cc[3] and cheb(rec['to'], (cc[0], cc[1])) <= 1]
                    c['dash_lands_adjacent_to_camp'] += bool(cm)
                if slot == 'reset':
                    c = ctx[k]; c['n'] += 1
                    c['double_hit_champ'] += any(x['kind'] == 'atk' and x['victims'] for x in acts[:j]) and any(x['kind'] == 'atk' and x['victims'] for x in acts[j + 1:])
                    c['double_hit_camp'] += any(x['kind'] == 'atk' and x['kvictims'] for x in acts[:j]) and any(x['kind'] == 'atk' and x['kvictims'] for x in acts[j + 1:])
                    c['after_move_then_attack(ranged)'] += (ty in RANGED) and any(x['kind'] == 'mv' for x in acts[:j]) and any(x['kind'] == 'atk' for x in acts[j + 1:])
                    c['no_second_attack'] += not any(x['kind'] == 'atk' for x in acts[j + 1:])
                    if ty == 'Vendetta': c['right_after_kill_same_turn'] += any(x['kills'] or x['ckills'] for x in acts[:j])
                if slot == 'shield':
                    c = ctx[k]; c['n'] += 1
                    en = [(i, cc) for i, cc in ch.items() if g['types'][i][0] != t and cc[4] and cc[2] > 0 and cheb(rec['apos'], (cc[0], cc[1])) <= 4]
                    c['enemy_in4'] += bool(en); c['hp%<50'] += ch[a][2] / ch[a][3] < 0.5
                    c['attacking_camp_this_turn'] += any(x['kind'] == 'atk' and x['kvictims'] for x in acts)
                    c['attacking_champ_this_turn'] += any(x['kind'] == 'atk' and x['victims'] for x in acts)
                if slot == 'heal' and rec['healed']:
                    c = ctx[k]; c['n'] += 1; hi, amt = rec['healed'][0]; hc = ch[hi]
                    c['target_hp%<50'] += hc[2] / hc[3] < 0.5; c['target_hp%<70'] += hc[2] / hc[3] < 0.7
                    en = [(i, cc) for i, cc in ch.items() if g['types'][i][0] != t and cc[4] and cheb((hc[0], hc[1]), (cc[0], cc[1])) <= 4]
                    c['target_has_enemy_in4'] += bool(en)
                if ty in ('Stellar', 'Prism') and slot in ('single', 'aoe') and (rec['victims'] or rec['kvictims']):
                    c = ctx[k]; c['n'] += 1
                    en = [(i, cc) for i, cc in ch.items() if g['types'][i][0] != t and cc[4] and cc[2] > 0 and cheb(rec['apos'], (cc[0], cc[1])) <= 5]
                    # best cluster: max enemies within radius 1 of a tile within 4
                    best = 0
                    for x in range(rec['apos'][0] - 4, rec['apos'][0] + 5):
                        for y in range(rec['apos'][1] - 4, rec['apos'][1] + 5):
                            best = max(best, sum(1 for i, cc in en if cheb((x, y), (cc[0], cc[1])) <= 1))
                    c['cluster>=2_available'] += best >= 2
                    c['hit_champs_%d' % len(rec['victims'])] += 1
                    c['other_slot_on_cd'] += (r - last[(a, 'aoe' if slot == 'single' else 'single')] < 8)
                    c['camp_target'] += not rec['victims'] and bool(rec['kvictims'])
                # track distance to targets for fleeing detection
            for rec in acts:
                for v in rec['victims']:
                    vc = rec['before'][0][v[0]]; prev_dist[(a, v[0])] = cheb(rec['apos'], (vc[0], vc[1]))
    print('=== TEAM', TEAM, 'games', games)
    print('  CASTS per (type, slot): n, on champ / on camp / none, cast exactly 8 rounds after previous (first opportunity), distance distribution, n victims (champ,camp):')
    for ty in SLOTS:
        for slot in SLOTS[ty]:
            k = (ty, slot)
            if not casts[k]: continue
            n8 = gap8[k + ('n',)]
            print('    %-10s %-8s n=%5d (%.1f/game) champ %s camp %s none %s | gap==8 %s | dist %s | nvict %s' % (ty, slot, casts[k], casts[k] / games, pct(casts[k + ('champ',)], casts[k]), pct(casts[k + ('camp',)], casts[k]), pct(casts[k + ('none',)], casts[k]), pct(gap8[k], n8), sorted(dists[k].items()), nvict[k].most_common(5)))
    print('  USAGE RATE when slot available (turn-level opportunities):')
    for ty in SLOTS:
        for slot in SLOTS[ty]:
            row = []
            for o in ('champ_in4', 'camp_only', 'atk_champ', 'atk_camp'):
                if opp[(ty, slot, o)]: row.append('%s %s (n=%d)' % (o, pct(opp[(ty, slot, o + '_used')], opp[(ty, slot, o)]), opp[(ty, slot, o)]))
            if row: print('    %-10s %-8s %s' % (ty, slot, ' | '.join(row)))
    print('  CONTEXTS:')
    for k, c in sorted(ctx.items()):
        n = c['n']; print('    %s n=%d %s' % (k, n, {kk: round(v / n, 2) for kk, v in c.items() if kk != 'n'}))
    for k, v in ctx_ex.items(): print('    ex', k, v)
    print('  DAMAGE (per game) by type: basic vs spell, on champions vs camps; spell share:')
    tys = sorted({k[0] for k in dmg})
    totc = sum(v for k, v in dmg.items() if k[2] == 'champ'); tots = sum(v for k, v in dmg.items() if k[2] == 'champ' and k[1] == 'spell')
    for ty in tys:
        ac, sc, ak, sk = dmg[(ty, 'atk', 'champ')], dmg[(ty, 'spell', 'champ')], dmg[(ty, 'atk', 'camp')], dmg[(ty, 'spell', 'camp')]
        print('    %-10s champ: atk %6.0f spell %6.0f (spell share %s) | camp: atk %6.0f spell %6.0f (spell share %s)' % (ty, ac / games, sc / games, pct(sc, ac + sc), ak / games, sk / games, pct(sk, ak + sk)))
    print('    TEAM champion damage/game %.0f, spell share %.2f' % (totc / games, tots / totc))

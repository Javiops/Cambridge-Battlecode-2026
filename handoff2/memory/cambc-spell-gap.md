---
name: cambc-spell-gap
description: 2026-10-14 "Ganar al top 4" study: the top 4 out-damage us 3.5x with spells on champions; P_SWEEP (cast ready spells at enemies in range) and its results
metadata:
  type: project
  modified: 2026-10-14T09:29:46.483Z
---

09:18 UTC 2026-10-14 the user chose "Ganar al top 4" (study how VeryGood, Univardisty, procless and Mite
beat us; general changes only, see [[cambc-new-maps-rule]]).

**Data:** 75 online games vs the top 4 (ws/ours11-14, profiled with studyrep.py). Tools in ws/tools:
`top4.py DIR...` (per game: bank gap at r150/r300, deaths/kills, captures, loot, dead champion-rounds,
monster damage, drafts), `fightcmp.py DIR...` (champion damage by spells vs attacks, death geometry),
`spelluse.py MAPS DIR...` (per champion: casts, casts with an enemy within 4, hits, and "ready%" = share
of enemy-within-4 rounds with no cast in the last 8 rounds).

**Findings:** on the fight maps we die 10-23 times a game with 0-3 kills. Their spells hit our champions
1813 times for 421k damage; ours 539 times for 121k (basic attacks equal, ~61 a hit). Ready% with an
enemy within 4: our Stellar 57%, Tavi 52%, Ryth 70%, Prism 49%, Cassi 37%; theirs 17-22%. Cause in code:
v22 has P_FRONT_CAST 0 and P_SHOOT 1, and the avoid/flee/back_off paths never cast. Cassi and Issac die
together (one body dies, both die). Farm maps: same draft on rows (procless), they deal 73k monster
damage vs our 54k in 378 rounds (more camp rounds per champion), still unexplained.

**P_SWEEP** (fbase main.cpp, `spell_sweep()` after play_turn): 1 = every turn a ready damage/stun spell
goes on an enemy champion within 4 (stun the closest foe that can reach us, else damage the weakest);
2 = only in a fight (hit in the last 3 rounds, a non-farm mode, or the foe below 60% hp / channeling).
`P_SWEEP_LOG` prints each cast. Arena (bots sw1 = v22+SWEEP 1, sw3 = v22+SWEEP 2; s14f = master with v22
params, identical to study14): vs spar4 v22 10-8 (deaths 118, kills 42), sw1 12-6 (92/57), sw3 13-5;
vs spar6 11-7 / 12-6 / 13-5; hunter2 18-0 all; vs v22 on 9 maps 7-11 for both (the sweep fires 0-11 times
a game there, so it is chaos noise); generated maps 43-45 (sw1), 43-45 (sw3).

Wide test vs 7 caster-style bots (spar2/3/4/6, study13, ballall, study15) on the 6 fight maps, 84 games:
v22 32-52 (deaths 609, kills 179), sw1 37-47 (535/217), sw3 40-44 (566/208).
**09:31 UTC: study16 = site version 24** (`bot/mybot_study16.zip`, main/params/fight_study16; arena bot
`study16` = sw3 = v22 + P_SWEEP 2), uploaded with `cambc submit bots/study16`. Online games keep landing
in ws/ours14 (fetch since 08:59); v24 games are the ones after 09:31 with the v22 draft.

**Online v24 (ws/ours15 = ours14 games after 09:31, 15 vs top 4): 3-12, same as v22/v23.** Its spells hit champions
35 times (theirs 313). **Engine rule found 09:45:** Tavi slot1, Ryth slot0, Cassi slot0 are
`exclusive_with_movement` (ability_properties): they fail after a step (error 126) and casting them blocks moving
that round (error 127), so an end-of-turn sweep only fires Cassi's free stun. Cast-before-move variants (P_SWEEP 3
always; 5 = only when standing is safe, P_SW5_OUT/P_SW5_ALLY team checks, then shoot) were worse vs spar4 on the
fight maps: 5-7, 2-10, 3-9, 5-7 (sw3 7-5, v22 4-8) and farm slower. Casting more alone does not close the gap.
10:10 farm-gap checks on v24 (card "Farmeo del top 4" recommended, not yet chosen): P_PAIR 3 (cp3) neutral
(farmbench 3520 vs 3534, gen 23542 vs 23560, 9-9); P_PAIR 1 worse; P_CAPDPS 1 (captures to ranged first, cd1)
worse: farmbench 3658, gen 23930, 4-14 vs v24. Online lanes: they take gem clusters (24) far more than wolves.

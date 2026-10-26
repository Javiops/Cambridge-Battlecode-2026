---
name: cambc-caster-ball
description: 2026-10-14 caster sparring bot (VeryGood copy: P_KITE, P_BALL, P_DRAFTCAST) and study13 = site v21 (caster ball on corners/collision/interlock/packs)
metadata:
  type: project
  modified: 2026-10-14T08:34:47.077Z
---

08:24 UTC 2026-10-14 the user chose "Sparring de casters": build a local rival that fights like the top caster
teams, because every fight rule that won locally failed online ([[cambc-centre-hold]]).

**What VeryGood does (v20 replays, ws/ours12):** drafts Stellar, Tavi, Cassi&Issac, Willow, Prism; all 6 move
as one ball (within ~2 tiles) to the centre by r20 on corners and stay; on interlock 3-4 of them sit in our
half. Spells: range 4 (Chebyshev), cooldown 8; Tavi target dmg x2.2 + 1-round stun, Cassi dmg x2.0 + a pure
stun, Stellar dmg x2.0 + ground AoE x1.4 r1, Ren stun x1.25. Measured with P_RANGES probe in fbase.

**New fbase switches:** P_KITE (fight.h `kite()`: step to a tile no foe reaches next round with the focus
within 4, stun whoever can reach us, damage spells on the weakest foe, shoot at 3; P_KITE_OUT bodies of
outnumbering allowed, P_KITE_ZONE engage distance, 0 = any foe within 7), P_BALL W (first living ally in
draft order leads; the rest take its claimed camp x W and avoid camps >8 from it; retarget every 3 rounds),
P_DRAFTCAST (VeryGood draft everywhere), P_DRAFTMAP 2 (that draft only on corners/collision/interlock/packs),
P_CASTGATE (KITE/BALL/HOLD only when we have 3+ ranged champions). Both teams can draft the same champion.

**Sparring bot `spar4`** (k5 params + DRAFTCAST, KITE, HOLD 200, KITE_OUT 2, BALL 5): 7-3 vs v19 on the 5
fight maps (like VeryGood online, except it loses elkring). `spar6` (+KITE_ZONE 5) 7-3 incl. elkring 2-0.

**08:34 UTC: study13 = site version 21** (`bot/mybot_study13.zip`, main/params/fight_study13, arena bot
`study13` = `v21a`) = v19 + P_DRAFTMAP 2 + CASTGATE + KITE + HOLD 200 + KITE_OUT 2 + BALL 5. Identical to v19
on elkring and the farm maps. Arena: 8-2 vs v19 on the fight maps, 8-0 vs hunter2, 6-4 vs spar4 (mirror,
collision can stall 0-0 for 2000 rounds), but alone it farms 15-38% slower (corners 382 vs 276 rounds).
KITE_ZONE 5 (v21b) lost the mirror badly (47 deaths on collision) and went 6-4 vs v19: rejected.

**Online v21 (ws/ours13, 08:36 batch, 70 games): 24-46, vs top-10 teams 5-25** (v20 batch 7-28). Ball maps:
corners 1-8, packs 2-7, collision 4-4, interlock 5-4; VeryGood still crushed the ball with the same draft
(corners 96-1006, collision 110-1012, interlock 110-1022, packs 488-1012). The ball chased a lot (up to
800 chase rounds a game on corners, `tools/chase.py COMPACT TEAM`).
**08:42 the user: "we chase forever; a fight ends when they retreat or die, then farm".** P_NOCHASE 1 (fbase):
a foe that stepped away from our last tile (or toward its spawn) stays "away" 3 rounds; away + out of our
attack range + < P_CHASE_GEMS gems = not a target, front line/kite do not step toward it, kite returns to
farming when no live foe is within 5 and we were not hit for 2 rounds. Arena: v19+rule (`k5n`) 9-9 vs v19,
v21+rule (`v21n`) 7-3 vs v21; no chase streaks of 6+ left. 08:59 uploaded **v22 = study14 = v19 + NOCHASE**
and **v23 = study15 = v21 + NOCHASE** (bot/mybot_study14.zip, mybot_study15.zip); recommended v22.

**09:20 verdict: the ball does not generalize.** `ballall` (ball + NOCHASE on every map) vs v22: 6-12 on the 9 maps,
**0-32 on the 16 generated maps** (ws/maps_gen), including the 4 with the shortest spawn path (33-49, like the real
fight maps): 0-8 there. Online v23 since 09:05: 22-38 (ball maps collision 6-4, corners 3-5, interlock 2-6, packs
1-5). No map feature found that picks the ball profitably; recommended keeping v22 active.


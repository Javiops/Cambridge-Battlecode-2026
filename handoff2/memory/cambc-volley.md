---
name: cambc-volley
description: 2026-10-14 "Rehacer la pelea": old sparring bots barely cast (step first); cast-first spar7 beats v24 2-10 like online; P_VOLLEY volley-aware movement; fight modes P_FM 1/2 rejected
metadata:
  type: project
  modified: 2026-10-14T10:38:46.628Z
---

10:12 UTC 2026-10-14 the user chose "Rehacer la pelea" (design a full fight mode). Engine facts in
[[cambc-game-mechanics]] (spell table: damage spells are exclusive_with_movement, range 4, cd 8, dmg = mod x focus).

**Sparring flaw found 10:50:** spar4/spar6/study13/ballall cast through kite()/front_line AFTER stepping, so their
exclusive damage spells mostly fail (error 126). `spar7` = current fbase + spar4 params + P_SWEEP 3 (cast every
ready spell at a foe within 4 before moving): **v24 2-10 vs spar7** (deaths 129, kills 23) while 7-5 vs spar4 and
vs spar7r (same rebuild without the sweep). Matches online 3-12 vs top 4. spar8 = spar6+SWEEP 3, spar9 =
study13+SWEEP 3, spar10 = ballall+SWEEP 3. Use these cast-first bots as the fight benchmark from now on.

**Rejected (vs old casters spar4/spar6/study13/study15/ballall, 60 games, v24 29-31):** P_FM 1 fight mode
(force ratio, one focus) ~4-8 vs spar4; P_FM 2 (+ volley model: hold outside ready volleys) 23-37, 0-12 vs spar7;
fm3 (= P_FM 2 + volley retreat) 20-40. Cast-first for us (P_SWEEP 3/5 on v24) vs spar7: 3-9, 2-10.

**P_VOLLEY N** (fbase main.cpp step_towards; threat_of/danger_at before struct Foe): in non-fight modes a tile
where the visible foes' ready spells + attacks reach N% of our hp is a wall; standing in one we first step to the
least-danger neighbour. vs spar7 vo50 5-7 (deaths 92, kills 51). vs the old casters it looked worse (24-36).
Logging: P_DZLOG prints `[dz] round name mode hp danger_before danger_after`; scratchpad dzan.py classified
v24 deaths vs spar4: about half start on a tile already inside a ready volley (avoid, flee/recall, front).
**Lean version (10:40):** the first P_VOLLEY scanned a 13x13 box per step_towards call and skipped 93-264 turns a
game (k26). Now spell data is cached per champion type (`spells_of`), foes beyond 10 ignored, only the 8
neighbours checked (P_VOLLEY_R 1; 2 was no better). Lean vo50 vs spar7/8/9/10: 6-6, 4-8, 4-8, 5-7 = 19-29
(v24 11-37, deaths 301 vs 379); vs v24 pool 11-7, gen 48-40; hunter2 17-1 (old build). P_VOLLEY_FIGHT 1/2
(also in fights): 22-26 / 17-31, not better.
**10:46 UTC: study17 = site version 25** = study16 + `#define P_VOLLEY 50` (bot/mybot_study17.zip,
main/params/fight_study17; arena bot study17 = vo50), uploaded with `cambc submit bots/study17`.
**Online v25 (10:47-10:51, 75 unranked games vs 15 top teams): 16-59.** vs the 6 rivals v24 also met: 3-27
(v24 5-25); 17 repeated map+rival games: +16 gems a game for v25, wins 1 vs 3 but Mite changed version in
between (its captures differ from r19). 10:51 the user chose to keep **v24 active**. P_VOLLEY_FARM 0 (no dodging
while farming, vo50nf) lost the fight-map gain (13-35 vs spar7-10): rejected. Online since 09:31 (155 games):
fight maps we capture 839 gems a game vs their 1028 and lose 76 on death (theirs 44); farm maps 951 vs 1033.
New tool `ws/tools/mkvar.sh NAME BASE "UNDEFS" "DEFINES"` (copy in arena/tools/study).

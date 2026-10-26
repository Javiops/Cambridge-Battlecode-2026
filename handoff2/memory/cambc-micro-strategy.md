---
name: cambc-micro-strategy
description: The user's fight doctrine for the CAMBC bot (2026-10-14 07:38): front-to-back, no chasing unless 150+ gems, hold position, focus one target, tank peels
metadata:
  type: feedback
---

2026-10-14 07:38 UTC the user asked for this micro: "front to back the fights, chasing is really bad,
we should aim to kite but to hold our position not retreat, we should be usually all hitting one,
the DPS hold their distance and the tank peels the dps. The only instance we should chase is if they
have > 150+ gems."

**Why:** the top-10 study ([[cambc-top10-study-1014]]) showed fights decide 5 of 9 maps and we have
the fewest kills; the user wants their own doctrine coded, not the local-arena rules that failed online.
**How to apply:** melee/tank = front line, ranged (Cassi, Tavi, Stellar, Willow) keep max range behind
it; all focus the same enemy (nearest to our front); no pursuit past our line except carriers of 150+
gems; do not run back, hold the line and kite in place. Build it as P_ switches on fbase and compare
vs the site version, then upload for an online test.

Versions: study10 = site **v18** (07:40 UTC, bot `f1`, mybot_study10.zip) = v17 + capture fix
(P_CAPCLAIM, per-ally vision try) + P_SHOP_PLAN 3 (Issac power-s first, Tavi focus, Cassi power-f).
Arena 14-4 vs v17. P_BAG 70/130 (carry more when no foe seen) lost 8-10 vs v17: rejected. Online
games go to ws/ours11 (since 07:40).

07:50 UTC: study11 = site **v19** (bot `k5`, mybot_study11.zip) = v18 + P_FRONT 1 (fight::front_line in
fight.h) + P_FRONT_LOCAL 1 (only with an ally within 4 and foes within 5 <= allies+1) + P_FRONT_OUT 130.
Without the local check (k1) it held alone and died 54 vs 28 kills against v18; k5: 10-8 vs v18, 32 kills
30 deaths, hunter 17-1. Next: map-aware draft. During the draft bc::draft::team_size(), map altars and
walls work (camp_groups throws); (team_size, altars, walls): collision 3,2,84; elkring 5,2,0; expanse
3,10,224; interlock 4,4,76; lanes 5,18,0; monolith 5,6,98; packs 3,6,0; rows 4,2,214; corners 5,5,44.
current_draft(bc::team::enemy) gives the opponent's picks so far.

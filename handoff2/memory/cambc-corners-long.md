---
name: cambc-corners-long
description: 2026-10-14 "mapas largos y corners como el #1": FINISH 30 = v30; every long-map draft rule (caster, #1 farm drafts, open/many-altar) lost locally
metadata:
  type: project
  modified: 2026-10-14T16:57:09.996Z
---

16:38 UTC 2026-10-14 the user asked to make corners and the long maps (lanes, expanse, monolith, rows) play like
the #1. Follows [[cambc-top1-study]] and [[cambc-sparring-v27]].

**Corners:** the #1 finishes low enemies (47% of kills on foes below 30%, corners 52%; v27 32%/27%); same focus share.
P_FINISH N (fbase fight.h low_foe: never "gone" and kite walks after a focus below N% hp within 6) = w1.
w1 (study21 + FINISH 30): panel spar11/16/12 22-8 (v29 20-10), spar7-10 32-16 (v29 29-19), official maps vs v29 9-9,
gen vs study21 49-39, hunter2 18-0. **16:56 UTC study22 = site version 30** (= w1; bot/mybot_study22.zip, main/params/
fight_study22). Seen in a sparring replay: after winning the first trade both caster teams stand 5 tiles apart for
~50 rounds with nobody banking (each waits for the other to step into range 4), an artefact of mirror engines.

**Long maps (all rejected, vs study21 or w1, both sides):** the #1 is not better there (12-16, same farm race).
- Caster draft on long gen maps 14-40 (w6), ts5 only 4-8 (w5; lanes 2-0).
- The #1's farm drafts (P_UNI_FARM: 4 = C&I/Stellar/Tavi/Varg, 5 = Ryth/C&I/Stellar/Ren/Varg) 16-34.
- Wall-free 5-pick maps (P_UNI_OPEN 1, scratchpad genopen.py) 3-9 on the long ones; many altars (P_UNI_ALT 12,
  genalt.py, 12-18 altars) 6-18. Lanes alone likes casters (5-1 over variants) but no map feature generalizes it,
  and per-map plans are against [[cambc-new-maps-rule]].
Draft features measured with P_MAPFEAT (scratchpad mapfeat.txt): gen maps have 4-19 walls per 1000 tiles; lanes 0,
monolith 39, expanse 35, rows 85. Long-map gap = farm speed ([[cambc-farm-speed]]), not the #1's play.

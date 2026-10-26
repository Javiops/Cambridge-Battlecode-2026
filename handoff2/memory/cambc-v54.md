---
name: cambc-v54
description: 10-17 09:09 v54 = v53 + full two-sided fight model (P_PVSIM) + kite-and-call-for-help (P_PVKITE) + wards (P_R5_WARD); user uploaded mybot_v53_simkitew.zip as v54 to test online; loop reports it by site label vs v53/v52
metadata:
  type: project
  modified: 2026-10-17T09:09:41.582Z
---

2026-10-17 09:09 user: "es la v54". Zip /mnt/project-files/bot/mybot_v53_simkitew.zip (built in the thread "Revisión de partidas de v53", cmsg_017gbamt2g1g8hMHRHQBc6qbDuHeM3HDGpCbdyxCp1DSxJ, branch claude/v53-replay-review-qop5ws); that thread moves it into the repo as v54 by renaming the folder ([[cambc-repo-versioning]]).

v54 = v53 plus:
- P_PVSIM 1: at first contact simulate the fight for both sides over 8 rounds with real strength, focus and hp (items count), spell uses by current cooldown, real spell damage (2.0-2.2x focus), stuns, durability emblems, Ren's passive, Cassi+Issac shared hp. Ratio below 0.6 = verdict "leave".
- P_PVKITE 1: on "leave", name the nearest foe in shared memory so allies that see it come to hit it; hold the tile and shoot while no foe can reach next round; step back toward allies only when one can. Replaces fleeing home.
- P_R5_WARD 1: wards on bushes and blind zones.

Local numbers vs v53 (flips, panel 12:52 / panel v51): +7 / -2 (noise on wins), deaths per game 11.0 -> 8.3 and 10.4 -> 8.6 (lowest of any variant). Weak spot: aggressive caster team on the 12:52 panel, 47% wins vs 71% for v53. Wards alone were +10/+6 (mybot_v53_ward.zip) but the user chose the three-switch version for the online test.


**Why:** the user values dying less and judging fights with real damage ([[cambc-v53-review-1017]]); online is the only judge for fight rules ([[cambc-online-ab]]).
**How to apply:** v54 is the lineage after v53 until the online result says otherwise; report later work against v54 and keep v53 (mybot_v53.zip) as the rollback.

**Online verdict (loop, 10-17):** v54 09:5x batch 42-103 (29%), paired vs v53 42-49 (flips 17-24). v55 (teammate: v54 + Varg solo-camp estimate, active ~10:57) 36-94, ties v54 36-37, vs v53 36-41. Dissection (45 v54 vs 38 v53 replays): deaths/game 8.7 vs 6.6 (opposite of local), fleeing deaths 55% vs 48%, alone 17% vs 12%; collision 18.1 deaths/game. Likely cause P_PVKITE: holding the tile vs advancing range-4 casters. 11:13 user asked to revert to v53; loop recommended v53, then v53+wards (mybot_v53_ward.zip) as next test. Report analysis/v54-online-2026-10-17/.
Tooling: 10-17 the site engine changed; replay decoding needs `pip install -U cambc` (2.2.5) + `cambc view` once for new assets; dissect.py downloads replays with the cookie.

**ONLINE VERDICT 10-17 ~11:45 (loop thread): v54 REJECTED.** Paired vs v53 42-49 and 36-41 (as v55); dies more online, 8.7 vs 6.6 deaths/game, deaths while fleeing 55% vs 48%, alone 17% vs 12%, gems/100 rounds 115 vs 130, collision 18 deaths/game. Read: P_PVKITE holding the tile vs advancing range-4 casters keeps us in range. User reverted the site to v53. Do not ship P_PVKITE as built; next candidate = v53 + wards only (mybot_v53_ward.zip). Fight-model work must fix the leave action vs advancing casters, not the ratio. Local panels said the opposite (fewer deaths): another case of [[cambc-online-ab]].
12:03 user's 3 ideas as switches on v54 src (commit 4cb994c): P_PV_NEWFOE 1 (re-judge when foes within 6 increase), P_PV 2+P_PV_FIGHT+P_PVCOMMIT 8 (all in on weakest), P_PVOUT 50 (least-danger leave). Panels vs v53 (flips 12:52/v51, deaths): simw base +10/-2 8.5/8.6; nf +18/0; commit200 +15/-4; commit300 +10/+1; leave80 +11/-1; out50 +9/-3; ALL (fight 250) +15/+7 deaths 7.2/7.7 = recommended zip /mnt/project-files/bot/mybot_v53_simw_all.zip, user uploaded it 12:10 UTC (also _nf.zip).
13:45 v56 (=simw_all) online 43-46 paired vs v53, deaths 6.7 vs 7.3, but lanes lost (fuel). Cause: wards widen vision -> refresh_groups state() on many groups. Fix P_GREF_R 10 + P_PVFUEL 25000 -> mybot_v53_simw_all_fuel.zip: lanes 19/20 (v56 15), panels +16/+10 vs v53. Tool: analysis/.../scripts/mapcheck.py.

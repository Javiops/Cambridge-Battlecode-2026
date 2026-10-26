---
name: cambc-simw-candidates-1017
description: 10-17 12:03 next online candidates after v54's rejection: v53 + wards + full fight model (simw) and the user's three verdict ideas (re-judge on new enemy, all-in when winning, leave early); simw_all +15/+7 recommended; zips and numbers
metadata:
  type: project
  modified: 2026-10-17T13:34:52.285Z
---

After v54/v55 lost online ([[cambc-v54]]), the user (11:51, loop thread) wanted the improved fight recognition kept and used in our favour, and at 11:55 chose three ideas from the loop thread's list: 1) re-judge the fight when a new enemy arrives, counting those who can reach; 2) when the estimator says we win, go all in (hit first, chase the fleer, focus one); 3) when it says we lose, leave early or do not enter, as v53 did, never holding the tile. Built as switches in the thread "Revisión de partidas de v53" (cmsg_017gbamt2g1g8hMHRHQBc6qbDuHeM3HDGpCbdyxCp1DSxJ, branch claude/v53-replay-review-qop5ws) on the base v53 + P_R5_WARD 1 + P_PVSIM 1 with P_PVKITE 0.

Zips in /mnt/project-files/bot/ and local flips vs v53 (panel 12:52 / panel v51), deaths per game (v53 = 11.0 / 10.4):
- mybot_v53_simw.zip = base (estimator alone, flees like v53): +10 / -2, deaths 8.5 / 8.6.
- mybot_v53_simw_nf.zip = base + re-judge on new enemy: +18 / 0, deaths 7.9 / 8.7.
- all-in alone at 2x: +15 / -4 (deaths 9.2 / 10.2); at 3x: +10 / +1. Leave early (cut 0.8): +11 / -1. Safest-tile leave: +9 / -3. All ties alone; all-in alone dies more.
- mybot_v53_simw_all.zip = base + the three (all-in at 2.5x): +15 / +7, deaths 7.2 / 7.7, 79% vs the aggressive caster on the v51 panel (v53 68%). RECOMMENDED by both threads for the next online test (12:03); upload is the user's.

Caveat stated to the user: v54 also died less locally and died more online, so only the loop decides ([[cambc-online-ab]]); +7 on the v51 panel is under the +10 bar ([[cambc-panel-noise]]).

**How to apply:** when a new site label appears, the loop records which zip it is and pairs it vs v53 with deaths, deaths while fleeing and caster teams split out. Later fight work builds on simw_all's switches, not on v54's kite.

**12:10 UTC user: "okey v53 simw_all esta online! vamos a ver que tal"**: mybot_v53_simw_all.zip uploaded by the user (site label pending, likely 56; v53 itself was not re-uploaded in between, the site went v55 -> simw_all). The loop's 12:46 batch runs on it; the user has given it no version number yet.

**13:34 v56 ONLINE (site label 56 = simw_all), 12:5x batch, 28 groups:** 43-97 (31%). Paired same rival and map: vs v53 43-46 of 140 (flips 18/21, noise), vs v54 43-43, vs v55 43-38; vs casters 38-45 paired with v53. Deaths per game (replays): v53 7.3, v54 8.7, v56 6.7, so kite removal fixed v54's deaths; deaths while fleeing still 56%. Fuel-exhausted turns per game: v53 0.6, v54 1.2, v56 2.5. LANES is the hole shared by v54/v55/v56 (wards + fight model): v56 4 of 28, v55 2 of 54, v54 6 of 32 vs v53 115 of 355; deaths there only 2.8/game but gems banked 794 vs v53's 924 (rivals ~1000). Loop's suspicion (not isolated): fuel cost of the fight model/wards on lanes (5 champions, 18 altars). Scorecard /mnt/project-files/analysis/v54-online-2026-10-17/scorecard_v56_vs_v53.md. 13:35 coordinator asked the review thread to isolate the lanes fuel cost (v53, +wards, +PVSIM, simw_all on lanes both sides) and ship a cheaper simw_all if fuel is the cause. v56 stays online until the user says otherwise.

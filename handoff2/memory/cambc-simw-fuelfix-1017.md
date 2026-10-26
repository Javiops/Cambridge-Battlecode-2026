---
name: cambc-simw-fuelfix-1017
description: 10-17 13:44 lanes hole in v54/v55/v56 was fuel (wards see more camps, every visible group read each turn); fix = far camp groups read 1 round in 4 + re-judge only with fuel left; mybot_v53_simw_all_fuel.zip +16/+10 vs v53, first over the bar on both panels
metadata:
  type: project
  modified: 2026-10-17T13:44:45.527Z
---

Follow-up to [[cambc-simw-candidates-1017]]. Online, v54, v55 and v56 (all with wards + the fight model) collapsed on lanes (v56 4 of 28 vs v53 115 of 355) while dying little there; gems banked 794 vs 924; fuel-exhausted turns per game 2.5 vs 0.6. The review thread ("Revisión de partidas de v53", cmsg_017gbamt2g1g8hMHRHQBc6qbDuHeM3HDGpCbdyxCp1DSxJ) isolated it 13:44: with wards the bot sees many more camps and read the state of every visible camp group every turn; on lanes (18 altars, many camps) that exhausted fuel and lost turns; re-judging the fight every round added a little; the fight model itself costs almost nothing.

Fix (switches on the same branch): camp groups farther than 10 tiles are read one round in four (own and nearby groups every round); the fight is re-judged only if fuel remains. Zip /mnt/project-files/bot/mybot_v53_simw_all_fuel.zip = v56 (simw_all) + fix.

Lanes locally vs the 10 panel rivals, both sides: v53 19/20 wins, 196 gems per 100 rounds, 4.5 fuel-lost turns per game; v56 15/20, 174, 12.7; fixed 19/20, 190, 6.8. All 17 site maps, flips vs v53: +16 on the 12:52 panel, +10 on the v51 panel (v56 was +15/+7): the first variant to clear the +10-on-both bar ([[cambc-panel-noise]]). Posted to the user in the project chat 13:45; upload is theirs; the loop pairs the new site label vs v53 and v56.

**Why:** every version since v54 lost online partly through this fuel hole, not through fights; it was invisible on the panels until lanes was looked at by gems and fuel-lost turns.
**How to apply:** any switch that widens vision (wards) must be checked for fuel on lanes and monolith (gems per 100 rounds and fuel-lost turns both sides) before upload; keep the far-group read cadence when building on this base.

**14:20 v58 (teammate, files from user 14:11) checked:** v58 = v54 switches + draft_plan.h (P_DP_BANK/WARDS/FINISH). Lanes 5/20 not fuel (3.3 fuel-outs): P_DP_BANK (carry up to 60 gems on long maps when quiet) kills lanes; without it 16/20. Panels vs v53: v58 -1/-3, v58+fuel +2/-3, +fuel no bank +2/-2; simw_all_fuel beats v58 +17/+13. Recommended simw_all_fuel; alt zip mybot_v58_fuel_nobank.zip.

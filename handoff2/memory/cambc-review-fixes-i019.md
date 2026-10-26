---
name: cambc-review-fixes-i019
description: 2026-10-16 four reviewer fixes (altar choice, gold recall, camp-survival model, walking-distance chaining) = ideas I019-I022, PR #16; RecallCost (I020, P_RECALLCOST 2) later PASSED the gate (+1% gems, zip ready, not uploaded), the other three fail; study27 v36 still online
metadata:
  type: project
  modified: 2026-10-16T08:02:00.000Z
---

2026-10-16 07:00 UTC the user asked to try four fixes from a code review (written against fran/study27-economy), through the harness. Thread "Four fixes: altar, recall, camp model, chaining" tested them as switches on study28 (what main holds) and recorded them as ideas I019-I022. Results (maps won both sides, fresh maps; gate = hold60+dev200, +fresh300+f150 = 710 maps), all in PR #16 (draft, switches OFF) and docs/I019-I022-review-fixes.md in the repo:
- I019 P_ALTARPICK, altar choice with walking distance + nearby enemies/allies + distance home: 86-103 on 710 maps. No gain; the nearest altar is almost always the right one.
- I020 P_RECALLCOST 2, gold-only recall must pay for the walk back: 117-104 on 710 maps, undecided; gold-only recalls are 7% of 4351 recorded recalls. Paused.
- I021 camp-survival model: data confirms the user's mechanism (front champion takes 67-81% of camp damage, 35-42% of fights exceed the old n^2 model's prediction), but every more cautious variant loses (tank 4-21, tank at camp 15-36, reserve -30 10-25): farming 5-13% slower and camp deaths are only 3% of fights.
- I022 P_CHAINWALK, gem chaining with walking distance (+ clear/capture time): 19-23 and 24-38. The metric mix the reviewer cited exists only in Fran's economy branch, not in study28 (on study28 chaining's altar distance is straight-line too).
Kept as useful: two new logs (P_LOGRECALL: reason of every recall; P_LOGCAMP: predicted vs actual camp damage; scripts in analysis/four-fixes/) and walking-distance fields (built once per turn, all at init cost turns).
Harness bug found: gate.py's fuel check compares bots on different games (cand in game X vs base in game Y) and fails on noise; on the same 34 games the variant used less fuel (593 vs 645 exhausted turns). The thread ran the gate with --no-fuel and proposed a fix in the doc.
**How to apply:** do not retry these four as written; the camp-survival data log is the base for any future survival model. Related: [[cambc-harness]] [[cambc-eval-method]] [[cambc-study28-rejected]] [[cambc-study28-chancancel]]

**2026-10-16 08:02 UTC update:** the user asked to fix gate.py and check whether RecallCost is more than noise. Result: I020 `P_RECALLCOST 2` (gold-only recall must pay for the walk back) PASSES the gate: 200-161 on 1260 fresh maps (p=0.045), vs a no-op build 63-64 on the same 1000 maps; levels 1/2/3 all positive on 500 more maps (+9/+9/+14); less fuel than base; caster panel 19-8. Effect: 43% fewer gold-only recalls (302 -> 171), each spending more gold (274 vs 224), about +1% gems per round; on its worst map it buys nothing and dies more (16 vs 13). gate.py fuel check fixed: counts both bots' fuel on the same games, both sides (the variant that failed on noise now passes, 309 vs 363). Zip ready for the user: /mnt/project-files/bot/mybot_study28_recallcost2.zip (study28 + P_RECALLCOST 2; note study28 also carries the recall/tribute cancel that the live study27 v36 lacks). All in PR #16; board shows I020 PASS. Upload is the user's decision; not uploaded as of 08:02.
**2026-10-16 08:35 UTC:** the ONLINE bot is study27-economy (fran/study27-economy; PR #17 syncs main to it). RecallCost ported onto it
(shop trips only; economy already has its own cr_ capture-recall return check) is NULL: levels 1/2/3 = 123-130, 131-132, 132-129 on
1000 fresh maps. I020 paused, no upload; the study28 zip is moot.
- 2026-10-16 08:45 PR #18 (branch claude/econ-review-switches, based on PR #17): the I019-I022 switches + loggers ported onto study27-economy, all off, for teammates to test; doc docs/I019-I022-switches-study27-economy.md.

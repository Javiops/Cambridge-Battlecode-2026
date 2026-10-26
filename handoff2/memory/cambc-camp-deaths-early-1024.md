---
name: cambc-camp-deaths-early-1024
description: 10-24 deaths thread: camp deaths r<150 near maps V20 0.29/team-game vs top10 0.13; 40% of the gap = gold_rush monolith (we wake it, 2.2 deaths/game); monoguard-v1 piece
metadata:
  type: project
  modified: 2026-10-24T09:25:33.461Z
---
Thread "Cómo muere" (cmsg_017gbamt2g1g8hMHRHQBc6qbHXbGbRJnfVW1WKFTx1zR7b), 10-24 morning, after Javier's 08:41 refocus to r0-150 near maps.
Split agreed with API thread: stall thread owns "dying outnumbered" r0-150; this thread owns camp deaths.
Data/scripts: analysis/fights-1023/early150/ (README, early.py, campdeath.py, campep.json, dec150.sh -> steps139/ = 200 V20 near games decoded r0-160 with camps).
- Camp deaths r<150 per team-game: top10 0.13, V20 0.29, v136 0.41, v122 0.54. Vs our rivals 30-60 equal (0.35 vs 0.42), so not why we lose to them.
- Gap: monolith 0.065 (gold_rush: 44 our deaths <r150 in 20 games vs rival 19; whole game 103 vs 65; lost_world equal ~5/game each side); entering camps <40% hp 0.26/game vs 0.11 (kill rate ~20% both); elk+gem+gold group 29% death/episode (n31) vs top10 2.9% (n137, they take it r41, we r81).
- Mechanism: gold_rush centre monolith (20000 hp, 200/round, range 5) shares a group with four 120-hp gold clusters; killing one wakes the whole group ~20 rounds; we woke it 4/7 times and lost 11 vs 6 in the next 25 rounds; our champions keep farming/fighting inside range.
- Piece monoguard-v1c (bundles/monoguard-v1c.zip 87e46a7d, bot/monoguard-v1/FICHA.md, on v20c, not uploaded): awake monolith whose group has
  gem/gold clusters and is not our target -> range 5 is a wall + step out. Exempt: mono_only (contest), monolith map (>=half gems in mono groups
  with gem clusters; de_map does not detect it), cluster-less monoliths (boss_battle boss, broken_curve). Monobench: gold_rush W 11 vs 8, our
  deaths 269->132; lost_world 243->169; contest identical. Hard panel -3/480 (bar 17.8) PASS veto; v1 -25 (blocked boss), v1b -7. Sent to API
  10-24. ONLINE chain 10: +7 (14/7, bar 9.2), gold_rush +3 (only rule map drawn; rest = fuel chaos). Rides in the package with the r0-150 piece.
Related: [[cambc-stall-root-cause-1024]] [[cambc-contest-monolith]] [[cambc-late-collapse-1023]]

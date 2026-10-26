---
name: cambc-strategy-1016
description: 2026-10-16 12:00 the user's strategic decision: pursue points 2-5 of the coordinator's plan (aim search at fights, learn from winners' replays, diversity/hall of fame, freeze discipline for 3 Nov); the LOCAL tournament winner is the upload candidate because online feedback is limited
metadata:
  type: feedback
  modified: 2026-10-16T12:00:00.000Z
---

Coordinator's 5-point recommendation, 2026-10-16 11:58 UTC:
1. Fix the judge: ghost/sparring rivals locally, online only as fitness.
2. Aim the search at fights: we lose by dying and by 3.5x spell damage; macro is at parity.
3. Learn from Mite/Univardisty replays: a supervised fight/flee value and behaviour cloning.
4. Islands with diverse scopes/seeds, migrants between them, a hall of fame.
5. One stable champion online, hourly cadence, no new ideas from ~30 Oct, validate the best three.

The user's reply, 11:59: "Orchestrate to do 2-5 thats where the money is! we can only receive a limited amount of feedback ... the best bet is to choose the local winner".

**Why:** online A/B gives ~30 groups/hour and cannot judge candidates fast enough; Mite's real bot is not available locally.
**How to apply:** the farm produces a champion via a final local tournament (ga-farm/CHAMPION.md, zip in /mnt/project-files/bot/) against the full rival pool (replay ghosts, spar11/12/16, v44, hall of fame); the coordinator hands the zip to the user; online only confirms.

Threads: "Imitation learning from top replays" cmsg_017gbamt2g1g8hMHRHQBc6qbUUfW58h6QoNFBstoRw6iTe (dataset under /mnt/project-files/analysis/replay-dataset-2026-10-16/, behaviour cloning, migrants); "Deep Q-learning for the micro" cmsg_017gbamt2g1g8hMHRHQBc6qbAtqtPcREAqYViqgM2BaGCn (fight/flee value from replays).
Freeze reminder scheduled for 2026-10-30 08:00 UTC (trigger trig_01GDRNqz15R4fNvtauQgPkCi).
Cloud credits: the user has 250 cloud session credits and wants them spent on more islands; the coordinator plans 6 more islands once island.py runs end to end.
Related: [[cambc-ga-farm]] [[cambc-rl-assessment]] [[cambc-local-testing-review]] [[cambc-deadline]] [[cambc-coordinator-updates]].

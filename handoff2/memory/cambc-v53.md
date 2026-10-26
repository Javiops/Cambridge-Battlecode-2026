---
name: cambc-v53
description: 2026-10-16 21:50 v53 = v52 + fight verdict + fuelfix/retreat + dash over holes (PR #32, mybot_v53.zip, user uploading); panels -6/+8 vs v52; dash init scan costs ~70 fuel-lost turns, fixed in mybot_v53b.zip (13); alt mybot_v53_retdash.zip
metadata:
  type: project
  modified: 2026-10-16T21:53:23.119Z
---

Thread root cmsg_017gbamt2g1g8hMHRHQBc6qbGMY7Stm3ba5Crs5CF5QyJ3, branch claude/v53-verdict-fuel-dash-hcgxm8, PR #32 (commit 1 adds bots/v52 = online zip, commit 2 renames to v53 + changes).
v53 switches: P_PV 1/LEAVE 60/ER 6 (verdict.h), P_ROSTER 1 + P_OCMEMO 1 + P_TRACK 1 + P_TRACK_RET 6 (track.h), P_MP_DASHHOLE 4 (mapplan_game.h, value 4 = the measured one; switch is a tile threshold, not a bool).
User 21:46: upload v53 and watch online stats.
Local (17 site maps, both sides; panels rebuilt with cambc 2.2.3, so absolute counts differ from other threads):
- h2h v53 vs v52 20-14 games, maps 6-3, deaths 8.9 vs 11.1.
- Panels of 170 (12:52 / v51): v52 124/120, v53 118/128, pv 130/129, ret 128/127, dash 128/131, ret+dash 129/131 (mybot_v53_retdash.zip), pv+dash 118/128, pv+ret 127/121. Pieces don't stack; verdict drags the 12:52 panel.
- Fuel-lost turns (34 games vs sp_castera): v52 93, ret 12, v53 82, v53 without dash 11; dash costs ~70 (ambush 32, pilgrimage/stampede 12, swirl 8): the cost is mp_find_dashholes at init (2 dash champions stalled r2-9), NOT the per-step field (caching it saved 0).
- 22:30 v53b = v53 + P_MP_DH_FAST 1 (hole set from 4 board shifts; PR #32 commit 3, off in bots/v53): 34/34 identical at unlimited fuel, fuel-lost 82 -> 13, panels 119/121 (v53 118/128): fuel saved, no panel gain. Zip /mnt/project-files/bot/mybot_v53b.zip, not uploaded.
- Interplay: verdict decides stay/leave, RET only picks the retreat tile; dash rule also runs inside flee() and can make a fleeing dash champion wait at a hole edge.
**How to apply:** if v53 underperforms online, candidates: v53b (same play, fewer fuel stalls on ambush/pilgrimage/stampede) or the retdash zip. Related: [[cambc-fight-verdict]] [[cambc-micro-tracking]] [[cambc-new-maps-strategy-1016]] [[cambc-panel-noise]].

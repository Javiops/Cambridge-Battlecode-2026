---
name: cambc-farm-macro-history-1021
description: Dated timeline 10-21 22:00 to 10-23 01:50 UTC of the farm/macro thread (stallfix, orch, need2, soloelk, waitwalk, plans, stay); summary in [[cambc-farm-macro-1021]]
metadata:
  type: project
  modified: 2026-10-23T01:15:00Z
---

Full numbers: /mnt/project-files/analysis/farm-route-1021/orch/RESULTS.md and analysis/farm-route-1021/soloelk-online/README.md.

10-21 22:20 stallfix-v1 (fff2bbda, on v102: holefix, islefix, respawnfix) panel +7, stalls halved; PASSED online +11 -> V13 v105.
10-21 22:37 orch-v1 (user's central-orchestrator design via 8 bytes) 38/70 vs 43, gems -10%; user said delete it. orch-v2..v5
(recruit/pull walkers) +7 vs pC, flat on panel; orch-v3 LOST online -8; need2-orch-v1 0 online. v12-v14 (sticky orders) lose.
10-22 04:30 feas-a = P_NEED_CAP 2 (need2-v1 0faf0955) panel +7, gems +0.2..6%, bad-9 maps 9/18; USER PROMOTED 06:05 -> V14 v110.
10-22 07:40 soloelk-v1 (P_NEED_SOLO 200) panel +18 bar 15.2, gold400 +2.5%, deaths -0.5. Online v112 +3/+8 = +11 of 49 (bar 14).
Pooled 239 pairs 29/19, elk<r400 +0.20/g, deaths +0.09: small real gain. need2b (RESERVE -140) +11 held.
10-22 07:14 USER: wait-respawn ring in walking distance. waitwalk-v1 (ae6bfbc7) panel +11; measured 3 blind rounds/game -> 0,
only 12 standing-wait rounds/game. Online v115 0 of 56 (noise). 12:49 USER asked why rejected: explained butterfly effect.
10-22 10:12 USER: why elk changes underperformed online -> soloelk_online.py study; batch-1 contact-map reading reversed by batch 2.
soloquiet-v1 (063e2aea, solo only if no foe seen 40 rounds) panel +15, flat vs soloelk.
10-22 21:27 USER: port pathfinding onto V17 + audit. 110 dist() uses: 4 Chebyshev sites fixed (walkfix-v1 8591580e), rest are
ranges. waitwalk-v2 (eece4251) panel -13, walkfix -12 (noise; 17/400 identical games).
10-22 22:11 USER: "better farming plan, all yours for the night". plan-v1/v2/v3 (altar territories) panel17 -47/-71/-40; holdcamp
and Vesper territory (shop thread) also lose. stay-v1 (walk x1.5) panel17 +28, stay125 +15, stay200 worse -> API thread.
10-23 01:50 stay+gemrace-v7 (4e8dac75) vs gemrace-v7: pHuntF 2/5, rFarm1 18/8 (+10, bar 10.2), gems +8%. 01:13 gemrace-v7 REJECTED
online (b2 -4) -> combo withdrawn; stay-v1 alone next online.
10-23 02:53 stay-v1 v128 REJECTED online -3 (far -6, near +3); local far 37/16 -> local far rivals invert online again.
10-23 03:50 far-map autopsy (online-far/): rival first 20+ gem capture r182 vs ours r343 with ~3 champions; local rivals r412, 12 deaths/g
(invalid far judge). 04:20 bigrush-v1..v6 CLOSED: capture r90 but gold400 -4..-31%, deaths +0.8..2.5, lose locally.
- 10-23 12:50 MIRRORS (online-far/mirror.py): near-map drop vs 60-79 = five teams that adopted our exact draft overnight (DOOMSDAY 1-20, Bamboo 39%, Agentic 42%, Hidden Altar 39%, Mania 35%); v122 vs them 39%, other mirrors 55%, different drafts 59%; in mirrors gold@150 lead wins 70/28. Dissect target (loop/deaths), not farm. openbig-gf (gem_fields 71-gem opening) CLOSED: 2-2 on gem_fields, deaths 3->14 on one side. LESSONS: P_XP traced build costs fuel -> use only for exposure, never for gates; mech test base results are not bit-identical to our builds: ~10 flips/160 noise floor on maps a rule never touches.

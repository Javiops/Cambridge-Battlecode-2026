---
name: cambc-v58-teammate
description: 2026-10-17 teammate's site v58 (13:20) and v59 (14:44, battlecode_mate_all_wards_alerts_v2.zip): switches, online 24-91 and 24-116, lanes collapse caused by draft_plan P_DP_BANK (not fuel), local panels vs v53, zips
metadata:
  type: project
  modified: 2026-10-17T14:21:38.900Z
---

**What v58 is** (the user attached its 12 source files in the project chat 14:10 UTC; the review thread "Revisión de partidas de v53", root cmsg_017gbamt2g1g8hMHRHQBc6qbDuHeM3HDGpCbdyxCp1DSxJ, holds them): the teammate's bot on the v54 line with a new draft_plan.h (draft-memory bytes 32-255: P_DP_BANK 1 = carriers hold up to 60 gems on long maps / 40 on mid maps with no enemy seen, P_DP_WARDS 1 = two map-chosen bush anchors for the first 2 champions, P_DP_FINISH 1 = safe finish) plus verdict switches P_PV 2, P_PV_FIGHT 250, P_PV_NEWFOE 1, P_PVOUT 50 (leave verdict steps to the least-danger tile), P_PVCOMMIT 8, P_PVKITE 0, P_PVSIM 1, P_R5_WARD 1, P_FUELGUARD 1, P_TRACK 1 / P_TRACK_RET 6. No P_V53_VARG_SOLO_ESTIMATE line in its params.h.

**Online (loop thread, 13:5x batch, 23 groups):** 24-91 (21%), worst batch of the day. Paired same rival + map: vs v53 24-37 of 115 (flips 13 for / 26 against, 67% against, above the 57% noise bar); vs v56 24-31 (11/18). By map interlock 7-16, collision 6-17, elkring 6-17, corners 5-18, lanes 0-23. By rank: top 10 3-37, 11-20 11-34, 21-30 5-10. First version of the day that loses for real, not noise.

**Lanes is not fuel in v58** (review thread, 14:20): only 3.3 fuel-lost turns per game. The cause is P_DP_BANK: on long maps carriers hold to 60 gems before banking. Lanes vs the 10 rivals: v53 19/20 (196 gems/100 rounds), simw_all_fuel 19/20 (190), v58 5/20 (151), v58+fuel 9/20 (154), v58+fuel without bank 16/20 (189), v58+fuel without new wards 6/20, v58+fuel without finish 8/20.

**17 site maps vs v53 (panel 12:52 / panel v51, flips; deaths per game):** simw_all_fuel +16/+10 (6.8/8.2); v58 -1/-3 (9.6/9.2); v58+fuel +2/-3 (9.7/9.3); v58+fuel no bank +2/-2 (9.6/9.6). simw_all_fuel beats v58 head to head +17/+13.

**Zips:** /mnt/project-files/bot/mybot_v58_fuel_nobank.zip (v58 + lanes fuel fix, P_DP_BANK off) if the team insists on v58; the recommended upload remains /mnt/project-files/bot/mybot_v53_simw_all_fuel.zip (see [[cambc-simw-fuelfix-1017]]). Neither uploaded as of 14:21 UTC; v58 still the active site version.

**v59 (teammate, active since 14:44, zip name battlecode_mate_all_wards_alerts_v2.zip, code not available; by name the v58 line with more wards and alerts). Online 14:5x batch, 28 groups: 24-116 (17%), worst version of the day. Paired: vs v53 24-46 of 140 (flips 9 for / 31 against, 78% against), vs v56 19-39, vs v58 15-24. By map collision 7-21, corners 6-22, elkring 5-23, interlock 5-23, lanes 1-27. By rank top 10 1-49, 11-20 8-32, 21-30 6-19. 14:51 the user asked for simw_all_fuel and the coordinator handed the zip over in the project chat; upload not yet confirmed at 15:13.

**Why:** the teammate's draft_plan pieces (bank, map wards, finish) do not improve v53 locally and v58 dies more than simw_all_fuel; the lanes loss looked like the v54-v56 fuel hole but has a different cause.
**How to apply:** do not treat a lanes collapse as fuel without measuring fuel-lost turns first; any future teammate base carrying P_DP_BANK needs the bank cut tested on lanes. Related: [[cambc-teammate-1017]] [[cambc-v55-teammate]] [[cambc-simw-candidates-1017]] [[cambc-online-loop]].

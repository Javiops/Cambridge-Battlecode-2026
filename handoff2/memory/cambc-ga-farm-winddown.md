---
name: cambc-ga-farm-winddown
description: 2026-10-16 18:59 user chose "Wind down" for the GA farm (decision card): islands stopped, checkpoints/migrants/tooling kept, no re-base on the teammate bot; final island states
metadata:
  type: project
  modified: 2026-10-16T19:00:23.073Z
---
18:59 UTC 2026-10-16 the user tapped "Wind down" on the coordinator's decision card (options: wind down / re-base on the teammate bot / keep as is), after the farm thread paused its champion run at 18:23 because the control (v49) was no longer the online bot (v51, teammate fixes) and the b672 port gave no site-map win. Coordinator told the farm thread and islands cloud-b..g, the structure island and the PC island to stop island.py, self-wakes and keep-alive loops, disable (not delete) their scheduled tasks and keep everything on disk; the farm thread writes a final note in /mnt/project-files/ga-farm/ on what exists and how to restart.
- cloud-b: stopped, 58 generations (100,390 games); best last-gen c9628bc9c1 +0.149 (n=1), most consistent 137994c5d9 ~+0.12 over 12 gens; none validated on v100. Checkpoint ga-farm/islands/cloud-b/, 53 migrants in ga-farm/migrants/cloud-b/.
- cloud-c: stopped, 65 gens (~112k games); best e2304cc502 +0.16 over 11 gens, d2ecc6d3d5 led gens 52-58 at +0.16; v100 validation cancelled, none validated. Checkpoint ga-farm/islands/cloud-c/, migrants ga-farm/migrants/cloud-c/.
- cloud-d: stopped, 73 gens (127,816 games); board best 84fa3430d3 +0.091 (5 gens, not validated); own check c9490ad43d 82-64 pairs, 31-14 maps vs v44 (p=0.16, null); its genome that held is b672ef97f6 (= 06c663eb13), 138-77 pairs vs the online bot on generated maps (ga-farm/champion/CONFIRM-2026-10-16-1807.md) but no site-map win. Checkpoint ga-farm/islands/cloud-d/.
- cloud-e: stopped at gen 60; best validated 9271169af0 +0.103 (n=8), won v100 vs v44 p=0.041 but gate tie 63-67 on 260 sealed maps and lost on fixes2 (125/170 vs 131). Checkpoint ga-farm/islands/cloud-e/, migrants ga-farm/migrants/cloud-e/.
- cloud-f (NEAT): stopped at gen 66; best cc48aced36 +0.161 training (n=4); top three on v100 all null (-0.005, +0.015, +0.011), lose to sp_castera; net genes add nothing measurable. Checkpoint ga-farm/islands/cloud-f/.
- cloud-g (all scopes): stopped 19:00, 82 gens (143,923 games); best 17e085aa5b +0.216 (n=4, not validated); validated leaders b5ff18510e and d1e4578253 tied the control on v100 (81-82, 83-72 pairs, p>=0.42). Checkpoint ga-farm/islands/cloud-g/, 63 migrants in ga-farm/migrants/cloud-g/.
- structure island: stopped at gen 69 (120,368 games); no validated genome beats v44 (two leaders tie); last leading family = NEAT net with 4 links (retreat, kite, recall, farm) +0.17 training over 7 rounds, validation unfinished. PR #22 stays open as a draft with the three levels. Checkpoint and migrants in ga-farm.
- PC island: stopped 19:01 after 202 generations, no processes left, no scheduled task; everything on the git branch ga-farm; resume with start-pc-island.ps1 if ever wanted.
- Other islands: see their threads ([[cambc-ga-farm-threads]]) for final states.
**Why:** three days of GA produced no online gain and the base moved to the teammate bot ([[cambc-teammate-base-1630]]).
**How to apply:** do not restart islands or champion runs unless the user asks; GA-found ideas can still be tried as switches on the fixes base, site maps first ([[cambc-teammate-fixes2]]).
Final state note: /mnt/project-files/ga-farm/FINAL.md (what exists, where, how to restart); code stays on draft PR #25; farm stopped 19:01.
Related: [[cambc-ga-farm]] [[cambc-ga-farm-tool]] [[cambc-ga-champions-2]].

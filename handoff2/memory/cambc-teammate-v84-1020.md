---
name: cambc-teammate-v84-1020
description: 2026-10-20 teammate's ppo-topdraft-v6 source (= site v84 "topdraft-v6 | movement trial") vs v82 locally on engine 1.0.1: loses 17-53 on the 35 site maps, 54-66 on hold60
metadata:
  type: project
  modified: 2026-10-20T22:25:03.899Z
---
22:07 UTC the user attached the teammate's bot source (16 files, saved at /mnt/project-files/analysis/teammate-v84-vs-v82/src). Header "ppo-topdraft-v6" -> it is the site v84 line, not v83.
WHAT IT IS: team-fight-v1 (v76) + (1) PPO target picker (ppo-adapter.h, 305-weight net, only re-picks among >=2 attackable targets, fires rarely: ~0-23 calls per champion per 1000 rounds); (2) fixed draft stellar/heart/ren/cassi/ryth (copied from rank-1 Intercontinental Fish); (3) objective rally on maps with exactly one gem-paying camp group (P_OBJECTIVE_START 350, period 360, window 240; fired in 4 of 70 site games); (4) "stage7" fuel yield: throws out of the turn below 30000 fuel (FUEL_RESERVE 16000), so the engine counts 0 fuelExhausted but turns are still cut.
MISSING vs v82: econ3 rescale, fuelfix, sealed-altar fix (boss_battle 0 gems both sides), vision wards (0 vs ~143 per game), draft-meta HoR kind fix; it plays Cassi+Issac (pair dies together).
LOCAL (22:15-22:40 UTC, cambc 3.0.2 --release, both sides): site35 17-53 (24%), gems 471/880, deaths (Cassi+Issac merged) 19.8/10.3, kills 6.6/14.4, faults 0/0. hold60 54-66 (45%, side A 33-27, B 21-39). Results: analysis/teammate-v84-vs-v82/results.txt.
Not uploaded/activated anything; online pair offered only. Related: [[cambc-next-rl-lab]] [[cambc-v58-teammate]] [[cambc-site-maps-download]]

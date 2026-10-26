---
name: cambc-danger-level
description: 2026-10-15 the user's "danger level" (0-1) idea: P_DLEVEL on study24, formula, results (no local win), death-cause stats, zip and doc paths
metadata:
  type: project
  modified: 2026-10-15T08:46:56.945Z
---

2026-10-15 08:10 UTC the user asked for a 0-1 danger level per spot: stop hitting camps while the enemy is there,
only start farming when safe, maybe wards (they will explore the 8 shared bytes themselves).

Built as P_DLEVEL on study24 ([[cambc-teammate-bot]]); name P_DANGER was already taken (enemy pack spot, byte 7).
danger = theirs/(theirs+ours), power = (sum hp within 8 of camp - other side's ready spells [- camp cost for us]) x
(sum dps); dps = str (x1.125 reset) + focus*mod/8. Hooks: choose_target skip, farm before each hit ->
contest (engage foe nearest the camp if danger without camp < P_DLEVEL_HI) or danger-leave (bad_until P_DLEVEL_T).
Zip bot/mybot_danger.zip (T 70, HI 50, WHERE 3), source bot/danger/, doc analysis/danger-level.md; also pushed to
team repo branch claude/project-thread-483hkk (bots/danger, docs/danger-level.md).

Results: no variant beats study24 locally (T 40-50 clearly lose; T 60-70 = noise; with wards too). Death stats
(s24): 21% (vs v30 gen) / 37% (vs spar11) of deaths come within 10 rounds of a camp hit with a foe near; rule halves
those but total deaths do not drop: 65-70% of deaths happen in flee/recall (dying while running away). Next lever:
leave earlier by danger of own tile, remember foes in fog.
Probe tools in scratch ws only (dlstat.py, ddstat.py; [dd] death history probe).
08:50 UTC user asked to try 1+2+3 (point 3 = P_DLEVEL_FLEE/FLEE_HP: flee when own-tile danger >= F and hp < H).
All 5 variants worse by maps-won-both-sides (vs s24 gen 5-8 won / 9-12 lost; vs v30 gen 13-16 / 11-15, s24 18/8);
deaths not lower. Leaving earlier = flee40 lesson again. Table in analysis/danger-level.md.
09:50 UTC: stand-and-cast (P_DLEVEL_STAND), back-to-camp (P_DLEVEL_BACK) also no gain. User's idea "recall while
capturing" = study24's P_CAPRECALL (only on for lanes): **P_CAPRECALL 2 on every map = study25** (bot/mybot_study25.zip):
vs s24 gen 16/6, fresh hold60 19/13; danger rules on top lose to it on hold60 5/15. Full danger source bot/danger_full/.
09:55 UTC: study25 merged into the team repo main (PR #1, bots/study25 = study24 + P_CAPRECALL 2).

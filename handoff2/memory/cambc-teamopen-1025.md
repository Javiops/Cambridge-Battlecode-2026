---
name: cambc-teamopen-1025
description: 10-25 farm thread: o68 dash-hole root cause (reverse_spiral); gem macro = top 10 open with the whole team, but o69 teamopen (v1, v2 own-side) over b32 is neutral near / negative far -> opening-ball line CLOSED 11:55 UTC (408 local games)
metadata:
  type: project
---

Farm thread 2026-10-25 (branch claude/project-thread-jhnqzy, handoff/fuelfit-farm/NOTES.md + opts/).

- o68 (P_MP_HOLE): mapplan rule 5 (dash champions route across dash-able holes) stood behind fuel_ok(40000) in kvvl (never ran) and is always on in the deterministic b15+ bots; on reverse_spiral HoR/Vesper took the hole shortcut alone next to the enemy spawn and died r24-27 in 8/8 games. P_MP_HOLE 2 (no hole route when a dash-less ally shares the target) = best of 208 local games (155 vs b29 143, h0 149). Integrator builds b31 (h0), b32 (h2), b33.
- Gem macro (coordinator's elk+gem request): the gap is the OPENING, not elk handling. Top 10 (40 near games): first capture r22 with 3 champions, 55% of the first three captures with 3+ champions, elk+gem captures by r50 0.62/game, deaths <= r100 0.35. b29/kvvl: first capture r25-26 with 2 (gold cluster in 47/80), 31%/26% with 3+, elk by r50 0.29/0.23, deaths 0.65/0.51. From r50 on our elk capture rate equals theirs.
- o69_teamopen.py (teamopen-v1): until P_TO_R=40 the first alive ally leads with the dormant `pack` hook (value for the whole team), the others follow its claim x P_GROUP_W (ball code), re-choose every 3 rounds; P_TO_NEAR for near maps only. No fuel read. Prior related lines: elk-opening-v1 (pairs) +5 bar 18; squad-v1/elksquad/joincall steering all game cost clears; open32/opening-near-v1 closed. This piece differs: whole team, one group, <= 40 rounds.
- o69 local panel 10-25 10:15 UTC vs b29: near 80 61 vs 55 (+13 -7), far 56 47 vs 43 (+10 -6; far deaths <= r100 18 -> 33, big_world/great_wall), total 108 vs 98 (bar 12). Mechanism: first capture r29 with 3 champions (b29 r25 with 2), first-3 with 3+ 50% (b29 31%, top10 55%), elk by r50 0.51 (0.29/0.62), early deaths unchanged 0.70. Package bundles/teamopen-v1-b29.zip (644d36e9); commit 2 of NOTES has the tables. Variants for PC: P_TO_NEAR 1, P_TO_R 25.
- o69 v1 over b32 (= b29h2) 11:00 UTC: near 58 vs 58 (+11 -11), far 44 vs 48 (deaths 13 -> 34) => NOT a candidate; cause = leader takes the team to the rich centre group (gemfight/packs/gold_rush), 2 die r27-45. v2 P_TO_OWN 1 (own-side groups only) panel over b32 running.
- o69 v2 (P_TO_OWN 1) over b32: near 59 vs 58, far 42 vs 48 (deaths 13 -> 35, big_world/great_wall). LINE CLOSED: the opening ball moves the mechanism, not the result; early deaths (62-71% with an enemy within 3) are fight outcomes. Do not reopen team-opening/ball/pack ideas without a new mechanism.
- Tools: /tmp/claude-0/ff/gem (capseq.py, ebmetrics.py with replay cache, openshape.py, trace.py); near-80 results res/*_n80 in /tmp/claude-0/ff/ws.

**Why:** user goal = play like the top 10 in r0-150 on near maps; opening shape is a measurable mechanism (first capture round, champions present).
**How to apply:** judge o69 by the mechanism metrics (first capture with 3+, elk by r50, deaths <= r100) plus W/N; if far maps lose, ship P_TO_NEAR 1. See [[cambc-fuelfit-1025]], [[cambc-fieldreuse-closed-1025]], [[cambc-top10-plan-1024]].

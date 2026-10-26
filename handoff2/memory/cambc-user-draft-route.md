---
name: cambc-user-draft-route
description: The user's own draft.cpp map-type rule (zones by dA-dB, POI BFS distances, greedy camp route, exposure): code facts and 9-map results
metadata:
  type: project
---

Continues [[cambc-user-own-bot]]. Their file: C:\Users\Javier\Cambc2026\bots\mibot\src\draft.cpp; copy of the 14:25
version at /mnt/project-files/docs/ejercicios/mi-draft/draft.cpp; scratch mirror ws/bots/mibot (revisit variant ../draft_revisit.cpp).

13:00-14:05 UTC: idea = 3 zones + best-efficiency route over own+middle groups; draft.cpp builds poi_dist (0 our spawn,
1 enemy, 2+i groups; one BFS each via export_linear_buffer) + GroupInfo. rows centre 600g/448 gems but 41k HP. Fuel facts in
[[cambc-game-mechanics]].

14:20 UTC: user chose zones by dA-dB with M = dist/12 (enemy side dropped, region 0 ours / 1 middle); saved in their
draft.cpp (folder not a git repo). Counts ours/middle/theirs: rows 4/1/4, corners 11/8/11, lanes 12/18/12, expanse
12/6/12, monolith 9/4/9, collision 9/2/9, interlock 6/4/6, elkring 5/0/5, packs 3/2/3; fuel max 476k (expanse).
Caveat flagged: elkring (fight map) has no middle; lanes (farm) has 18 middle. Region viewer: C:\...\Cambc2026\analisis\regiones.html,
artifact https://claude.ai/artifact/8vrtahLbWcJnhjceTHYP1V. Next: efficiency + greedy route -> map_type.

14:25 UTC: their draft.cpp has plan_route(): greedy 4-stop route by (gold+3*gems)/(steps+hp/100+5); FIGHT if route has a
middle group or exposure (min dB - stay) < 0. vs top-10 labels only 4/9 right (elkring/corners/packs FIGHT ok, expanse
FARM ok; collision +1, interlock +6 -> FARM wrong; rows/lanes/monolith -> FIGHT wrong). Plain spawn_path rule gets 9/9.
Causes: rows has 3 own groups so 4 stops forces the centre; monolith huge group stay time. Suggested: allow revisits after respawn.

14:30: VS Code stale tab dropped the '#' of #include (use File: Revert File). Revisit variant (free_at[i] = t + respawn):
6/9; wrong interlock/collision (exp 6/1 -> FARM) and lanes (middle 39/42 -> FIGHT).
17:30 UTC: region viewer artifact (same URL) v3 = the user's own route logic (default = their code, 4/9) + "Ruta" toggle for the
revisit variant (6/9) + top-10 label per map, score and dashed border on misses. Verified identical to the bot output in both modes.
Source: scratchpad page/regiones_v3.html. Their PC copy analisis\regiones.html is the older version without the top-10 comparison.
17:40 UTC: user's idea "min distance between both optimal routes -> fight" tested (scratchpad pagetools/meet.js): plain fight
6/15/16/24/30 vs farm rows 0, lanes 3, monolith 27, expanse 53; best 7/9 (revisit, <=30). Time-aware contact also overlaps.
Told them: top-10 fights are invasions, so cheapness of invading separates: d 26-41 vs 49-85 (9/9, gap 8); our spawn to nearest
enemy-route stop 24-32 vs 36-73 (9/9, gap 4). Recommended: draft by d, use the route for the in-game farm plan.
17:45: time-horizon route (no ROUTE_STOPS, revisit after respawn, pagetools/cycle.js) settles into a fixed loop by ~150 rounds; classify 5/9 (expanse adds far middle groups 64/60, 65/68). Loop = good in-game farm plan, not a fight signal.
17:50: user accepts cycle as the farm plan, wants heuristics matching the meta. Scan of 18 cycle/map features (pagetools/scan.js,
report docs/ejercicios/heuristicas-ciclo.md): only d (<=41 vs >=49, gap 8) and inv = our spawn -> nearest enemy-cycle group
(<=34 vs >=37, gap 3) give 9/9; exposure 8/9 (monolith 5), loop/d 8/9, area 8/9. Proposed map_type = dist < 45 (+inv), cycle for farming.
17:55: artifact 8vrtahLbWcJnhjceTHYP1V now = cycle version (both cycles drawn, heuristic selector mindb/cdist/expo/d/mid/combo,
meta per map editable in localStorage, default mindb<=33 = 9/9; mindb == our 'inv' by symmetry). Also on their PC analisis\regiones.html.
My unpublished variant: scratchpad page/regiones_v4.html. Asked the user whether they write map_type = dist < 45 + cycle themselves.

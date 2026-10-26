---
name: cambc-unseen-maps
description: The qualifying tournament uses brand-new maps: no per-map plans or map detection; strategy must come from measuring the map (pathfinding) at game start
metadata:
  type: feedback
---

2026-10-14 09:05 UTC the user said: the maps we qualify on will be totally new, unknown beforehand, so we cannot
have a prior plan; recognising the right strategy from pathfinding, not a predetermined per-map plan, is very
important.

**Why:** map detection by team size / altars / walls / camp counts (P_DRAFTMAP, usar_eficiencia in
docs/ejercicios) only works on the 9 current maps and does nothing on new ones.
**How to apply:** any per-map switch must be replaced by a rule computed from map features at runtime (path
distances from the distance field, camp gems/hp, spawn-to-camp distances, team size). Test candidates on maps
not used for tuning (arena/maps/gen*, or hold some official maps out). Related: [[cambc-exercises]],
[[cambc-caster-ball]].

09:20 UTC results (v19 base, vs idle; 44 generated maps in docs/ejercicios/mapas-nuevos.zip = arena/maps/gen*):
the user's test: a general rule that ties the hand-made per-map plan is the goal. Per-map plan (efficiency on
rows/interlock/expanse/corners) 6937 rounds on the 9 maps, 47347 on new maps; v19 7178 / 47354. P_RUTA 1 (travel
= real path length from a per-turn distance_field from pos, walls|holes|altars) 7127 / 47137, 12-6 vs v19, 11-7
vs v22, 44-44 vs v19 on new maps. The plan's edge came from efficiency scoring that skipped P_HALF / doorstep
rules and farmed the idle enemy's half (fake gain); with those rules kept it is slower (7355).

Draft facts checked 09:30 UTC (cambc 2.1.6, probe on v19): in run_draft camp_groups() WORKS (gem_value, gold_value,
camps() is_wolf/is_elk/is_monolith, spawn_tiles, max_respawn_timer); walls/holes/bushes/altars, spawn_region(ally/
enemy), width/height, distance_field all work; vision::camps() throws; self() not available. First draft turn has
~840k fuel. current_draft(enemy) shows rival picks of previous rounds only (simultaneous picks). Draft memory is
1024 bytes (our bot uses 0-20 and 24-27). Coaching file for the user: docs/ejercicios/draft.md (they code it).

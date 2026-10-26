---
name: cambc-new-maps-rule
description: The CAMBC qualifying maps will be brand new, so the bot must pick its strategy from map features (pathfinding, camps, distances), never from per-map fingerprints
metadata:
  type: feedback
  modified: 2026-10-14T09:06:12.827Z
---

2026-10-14 09:05 UTC the user said: "los mapas sobre los que clasifiquemos serán totalmente nuevos y no
podremos saber antes ni haber hecho un plan previo; poder reconocer la strat correcta basada en pathfinding
y no en un plan predeterminado es muy importante".

**Why:** rules keyed to the 9 known maps (P_DRAFTMAP 1/2 fingerprints by team size + altars + walls, any
"only on corners/collision" switch) never fire on the qualifying maps, and tuning on the 9 known maps can
overfit them.
**How to apply:** decide from what the bot can measure at draft/init time (team size, altar positions vs
both spawns, camp groups and their distances, walls/paths via distance fields). P_HOLD's detection (an
altar about as far from both spawns with 2+ gem camps near it) is already feature-based; P_DRAFTMAP
fingerprints are not. Test every candidate on generated unseen maps too (`arena/tools/genmaps.py OUTDIR N
SEED`; sets in `arena/maps/gen`, `gen2`, `gen3`), not only on the 9 official maps. v22 (study14 = v19 +
P_NOCHASE) has no map-specific rule (18-14 vs v19 on the 16 maps in arena/maps/gen, copied to ws/maps_gen); v23 caster ball only fires on 4 known maps, so on new maps v23 = v22.
Related: [[cambc-caster-ball]], [[cambc-arena-setup]].
Draft-time probe `P_MAPFEAT` (fbase, uses native `bc::distance_field::compute`; a manual BFS runs out of draft
fuel). spawn_path (path length between spawn regions): known fight maps 26-41, farm maps 49-85, generated maps
33-73 (gen11_02 33, gen11_15 41, gen11_10 47, gen11_07 49, rest 53-73). The ball lost on all of them, so spawn
path alone does not say "fight map" ([[cambc-caster-ball]]).
2026-10-18 12:19 UTC user restated it for the v53 plan: sprints and the qualifying tournament use totally new maps; no rules hardcoded to official maps; when a cause shows on one map (elkring) understand the map feature behind it and fix the general logic, tested on generated maps with that feature. Written into next\STRATEGY.md 'New direction' ('No rule keyed to a map'). The loop's 5 official maps find problems, they are not tuning targets.
2026-10-18 13:25 FACT (audit thread read base-v53 and base-v53-clean source + compile_commands on the PC; corrects a 13:20 note): de_rules.h fingerprints the 9 old maps (P_D34_FAMILY 1), but every P_D34_DRAFT_* is 0 (#ifndef default, no -D in the build), so no per-map draft. Active map rules: rows (chain 60, bag 48, bank within 4), monolith (capture split cap, altar cost 100), expanse (altar cost P_R34_BANKCOST 300), lanes (P_CAPRECALL forced 1 vs global 2: a LOOP map). corners/interlock reset check is moot (P_U34_RESET_LIVE 2 global). Never fires on new maps. Proposal to user: base-v53-nofp removes them; lanes measured online.

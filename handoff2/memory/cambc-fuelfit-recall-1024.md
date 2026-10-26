---
name: cambc-fuelfit-recall-1024
description: fuelfit recall/altars/camps pieces o21-o23 (exact 52/52) and the finding that thrown engine errors cost 5-8k fuel each
metadata:
  type: project
  modified: 2026-10-24T23:35:41.844Z
---
10-24/25 champ thread delivered fuelfit pieces for recall/altars/camps on fuelfit-a1: branch claude/project-thread-l6gm1j commit ca75169, handoff/fuelfit-recall/ (opts o21_camps, o22_altars, o23_campread + README). All exact vs a1 with --fuel-quantum 2000000 on 52 games.
- o22 removes every fuel_ok in altar/trip code; brcache altar fields built on fixed turns (P_BRC_PER 2/turn from P_BRC_R0 3).
- Camps section max 94k -> 23k; best_altar 47k -> 12k; br_plan 45k -> 6k.
- KEY: a raw sdk_camp read costs ~60 fuel, but an engine error thrown and caught by attempt() costs ~5-8k. ~25 per champion per game (32 unreachable, 97 not in vision, 63 cannot act). Read raw return codes instead of throwing.
- Remaining recall/bank peaks are in step_towards, choose_target and flee (farm/fight threads).
Related: [[cambc-det-fuel-1024]] [[cambc-stall-root-cause-1024]]
- 10-25: o34 on fuelfit-b6 (commit 3e28685): sealed-altar board algebra + cr_return_walk without fuel_ok, exact 52/52. Section has no fuel_ok left; tribute >76k turns are fight/foes/post-sweep/step_towards + [econ]/init logs every 50 rounds. Moving altar_sealed static setup to a fixed early turn is NOT exact (boss_battle).
- Each champion is its own wasm instance: statics/one-off inits run once PER CHAMPION.

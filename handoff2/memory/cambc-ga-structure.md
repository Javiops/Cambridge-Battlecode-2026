---
name: cambc-ga-structure
description: 2026-10-16 structural evolution of the fight micro (thread "Evolucionar la estructura de la micro", PR #22, tools/ga/STRUCTURE.md): rules on/off+order, GP conditions, NEAT; now farm island `structure`; results vs v44 so far not significant
metadata:
  type: project
  modified: 2026-10-16T16:03:01.895Z
---

Thread "Evolucionar la estructura de la micro" (branch claude/ga-structure-054bwb, draft PR #22, doc tools/ga/STRUCTURE.md). Judge only against the control in the same wasm, never the original build. Related: [[cambc-ga-micro]] [[cambc-ga-farm]] [[cambc-ga-farm-tool]]
- Level 1: 10 ordered micro rules (flee, near recall, fm, kite, front, avoid-low, avoid, engage, recall/shop, walk home), on/off + order genes, plus existing fight switches. Level 2: postfix GP of the AVOID (GP0) and ENGAGE (GP1) conditions. Level 3: NEAT net, "default" output defers to the rules; new links born as threshold rules (`neat.add_rule`, else the whole population plays the seed's games). Defaults/seeds = base bot exactly (68/68 identical, unlimited fuel).
- Noise floor ~+0.07 on 6 maps. Turning off recall/shop or flee, or walk-home on, lose clearly.
- 11:25 on study27-economy weights: best 4fe4dd2392 (NOCHASE 0, FRONT_LOCAL 0, AVOIDLOW off, ENGAGE before AVOID) 108-82 pairs vs control on v100 (p=0.07); vs v44 215e622beb 23-20 maps.
- 12:20 on v44 (= ga65a6) weights: no structure genome beats v44 (best 87-92 pairs): the structure's aggression and v44's weights are the same idea, they do not stack.
- Since 12:20 the thread runs farm island `structure` (scope structure,gp,neat) from worktree /home/user/farm (detached origin/claude/ga-farm-d37xlq; maps, cmake, sdk symlinked from the repo). Keep-alive: background `tail --pid=<island pid> -f /dev/null` (timeout 2 h) + send_later every 30 min running `island.py ensure`.
- Gotchas: after a pid.json format change `ensure` can start a 2nd process: check `ps aux | grep "[i]sland.py run"`. Never `pkill -f`/`pgrep -f` with a pattern matching your own shell (kills the Bash call, exit 144).
- island.py validate KeyError (cid vs state id) fixed upstream in cae2273; no local patch needed any more.
- 13:45 gen 15 v100 vs control v44: top 55-43 pairs (p=0.27).
- 16:02 gen 36 v100: leader fd444ac101 (2 siblings identical games) 20-18 maps vs v44, 60-45 pairs (p=0.17), not significant. Leader genes: FRONT off, FRONT_LOCAL off, NOCHASE 0, ALLYDUTY on, AVOIDLOW off, ENGAGE before AVOID, NN one link -> recall. Then pulled 4fa99e8 (specialist panel rivals), stop + ensure; layout re-keyed to 640 ints.
- 17:03 gen 45 on the specialist panel: stable leaders 80c62b3935/16ef11cc52 (same family as fd444ac101) 20-18 vs v44, 73-70 pairs vs control (p=0.87); better vs sp_centre/sp_hunt (87-0, 85-0), worse vs sp_castera (56-14 vs 63-12). Island plateaued at v44 level.
- 19:00 user wound down the GA farm (base moved to the teammate's bot): island structure stopped at gen 69 (120k games), watchdog disabled, checkpoint ga-farm/islands/structure and migrants kept. Last leader family f79d936666 (NEAT 4 links: back off/kite/recall/farm, base rule order) +0.17 over 7 gens, never validated.

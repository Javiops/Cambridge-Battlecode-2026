---
name: cambc-ga-farm
description: 2026-10-16 12:18 all in on the genetic path (cloud + PC); islands via tools/ga/island.py (draft PR #25, FARM.md); 7 cloud islands a-g + PC island (16 jobs, data branch ga-farm) + macro GA; `island.py champion` every 2h writes CHAMPION.md and zips the winner; BOARD.md; thread ids in [[cambc-ga-farm-threads]]
metadata:
  type: project
  modified: 2026-10-16T12:18:00.000Z
---

11:36 UTC user: "go all in on the genetic path, dedicate most of my resources from the cloud and my pc to running possible candidates not only with Micro tweaks but everywhere and I want you to orchestrate it". Coordinator orchestrates; one thread per island, ids in [[cambc-ga-farm-threads]].
- **Island model:** one evolution per machine (own seed, scope, rivals) via `tools/ga/island.py --name --scope --base --migrate`; best genomes (fitness + base hash) exchanged via /mnt/project-files/ga-farm/migrants/ (cloud) or the data-only git branch `ga-farm` (PC); each island writes a line in /mnt/project-files/ga-farm/BOARD.md. Genome = 22 fight weights + rule switches/order + GP conditions + NEAT net + ~30 macro genes; --scope micro|structure|macro|gp|neat|all; checkpoint per generation in ga-farm/islands/<name>/; `island.py ensure` restarts dead islands; early drop after half the maps.
- Base: main = study27-economy + P_MONO with v44 (ga65a6) params; online = v44. gate.py passers go to the user as zips; online A/B decides.
- Lesson: idle containers restart (micro island lost gens after 28); checkpoint each gen + periodic self wake.

12:08 UTC: island.py ready (draft PR #25, how-to tools/ga/FARM.md). Rivals = v44 + spar11/12/16 + 6 replay ghosts + hall of fame (self-play ~1 of 10). `island.py champion` builds the 2 best per island as upload builds (fuel guard + contest fix), plays 120 sealed maps vs all rivals, writes ga-farm/CHAMPION.md, zips winner as bot/mybot_<id>.zip; farm thread runs it every 2 h. Islands: cloud-a (farm thread) micro+structure+gp first; cloud-b/c micro seeds 1002/1003; cloud-d structure 1004; cloud-e gp 1005; cloud-f neat 1006; cloud-g all 1007; macro thread runs its own 49-gene GA; macro genes use the macro thread's table. Micro, structure and PC threads switched to island.py.
- Speed: generation 0 on cloud islands is slow because the 9 rival bots are built once (~135 s); steady state ~7-8 games/s per 4-core island.

12:18 UTC PC island `pc`: runs tools/ga/island.py (PR #25 branch claude/ga-farm-d37xlq) with --scope all --jobs 16 low priority from ga65a6, ~1 min/gen, pushes migrants/status to data-only branch `ga-farm` every generation. Old run ended at gen 10 (best 84b6c6552c +0.080); its top 8 genomes are on ga-farm as migrants/pc/*.json. Scripts C:\Users\Javier\Cambc2026\start-pc-island.ps1 and stop-pc-island.ps1 (run start again after a reboot). Exchange cloud->PC not live until a cloud island pushes to ga-farm (user card pending in the farm thread).
**Apply:** read BOARD.md, CHAMPION.md and island threads. Related: [[cambc-ga-farm-threads]] [[cambc-ga-farm-tool]] [[cambc-ga-micro]] [[cambc-ga-structure]] [[cambc-dev-speed]] [[cambc-online-loop]] [[cambc-online-is-economy]] [[cambc-deadline]] [[cambc-rl-assessment]]

- 14:02 UTC lesson (island cloud-g): a background Bash task (run_in_background, timeout 2 h) looping `while pgrep -f "island.py run --name X"; do sleep 60; done` stops idle container recycling (before: the island died every ~10 min); re-arm it from the 15-min self wake. cloud-g restart = `bash /mnt/project-files/ga-farm/islands/cloud-g/restart.sh`.
16:47 UTC cloud-f v100 check: 13ebc26628 (+0.099 training over 11 gens, tiny NN 1 hidden/3 links on engage + migrant micro/structure) = control on v100 (-0.005, pairs 74-80, 19-28 vs v44): training margins of ~+0.1 do not survive validation. `validate --ids X --jobs 2` takes ~12 min. 17:46 150107f60e (+0.122, n=9): v100 +0.015, pairs 83-78 p=0.75, 30-20 vs v44 — no edge either. 18:52 f79d936666 (+0.162, n=5): +0.011, 81-78. All three share a migrant micro (wins 30-20 vs v44 but sp_castera 51-16 vs control 63-12); the net genes add nothing measurable.

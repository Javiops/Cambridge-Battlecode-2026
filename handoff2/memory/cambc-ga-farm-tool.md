---
name: cambc-ga-farm-tool
description: 2026-10-16 tools/ga/island.py mechanics (PR #25, FARM.md): unified genome, commands, rivals (ghosts, hall of fame), exchange, champion tournament that builds the upload zip; champion results in cambc-ga-champions
metadata:
  type: project
  modified: 2026-10-16T15:50:55.534Z
---

Built 2026-10-16 12:00 UTC by the farm thread (branch claude/ga-farm-d37xlq, draft PR #25, how-to tools/ga/FARM.md). See [[cambc-ga-farm]] for the plan and roles.
User decisions: the **local winner is what gets uploaded** (online feedback too scarce); micro/structure first, macro second.
- Genome: structure.SCALARS = 22 weights + structure switches + macro (macro.py = PR #24's macro_genome.py + farm extras), 627 ints 'GAS1'. Macro literals applied after struct.patch (re-indented). Default = base build 34/34 identical (unlimited fuel).
- `island.py run|ensure|stop|board|validate|export|champion`; checkpoint per generation in ga-farm/islands/<name>/ (cloud) or out/islands/<name> (PC); `ensure` = restart, keep a send_later self-wake.
- Rivals: v44 (genome:start), spar11/12/16, 6 ghosts pinned to map/side (bots/gh_*, maps_ghost/), hall of fame (2 other islands' best + own 2 past champions). Racing drops half the pop after half the maps.
- Exchange: migrants/<island>/<cid>.json; also reads the other GA threads' flat migrants/*.json and the PC's old pc-island branch (--legacy-branch). Git branch `ga-farm` for the PC (cloud pushes approved 13:05).
- champion: islands' top 2 built on the fuel-guard base (PR #23 ref, 3-way merge; v44 control = mybot_ga65a6_fuelguard.zip, 34/34 identical), 120 sealed maps, CHAMPION.md + /mnt/project-files/bot/mybot_<cid>.zip.
- ~7 games/s on 4 cores, 2-4 min/gen; training pool 415 maps (maps_train incl. cousins, committed).
Related: [[cambc-ga-micro]] [[cambc-ga-structure]] [[cambc-ghost-arena]] [[cambc-fuel-budget]]

- 13:05 UTC 16 Oct: pair genes (tools/ga/pair.py, micro family, from the DQN death-rate finding): P_GA_SS_ALLY/P_GA_SS_HOME, P_PAIR_N/FOE/STICK/ENGAGE; defaults = base. User approved cloud pushes to `ga-farm` (cloud-a runs without --git-readonly). Layout changes re-key state automatically (rekey also renames champions since 4dde634).
- 13:20 UTC 16 Oct (d84d598): fitness weights v44 x3, spar x0.5 each, ghosts x1 together (ghosts were 43% of fitness but always won). Champion needs pairs vs v44 not worse. Lesson: rivals we already beat dominate a GA's score unless down-weighted.

**14:19 UTC leader persistence (commit a667ff7):** islands play 8 maps per generation, elites replayed on fresh maps each gen, fitness = shrunk mean over gens, but new leaders often had n=1-2. Now a genome migrates only after 3 generations (--min-n 3, was 2) and enters the champion tournament only after 4 (champion --min-n 4, 32+ training maps). Champion tournament = 60 sealed maps vs control + v44 pair check, every 2 h (14:15 run used the old rule; next 16:16 UTC). Macro GA lesson: run-2 leaders (+0.10 training, 16 maps/candidate) tied on 100 validation maps (38-37), so it moved to 40 maps x 12 candidates. Islands b-g and PC told to pull/ensure at 14:20.

**15:49 UTC panel in island fitness (commit 4fa99e8):** rivals = start bot x3, sp_castera x2, sp_casterh x2, sp_centre x1, sp_hunt x0.5, ghosts x1 together; sp_farm out, spar11/12/16 dropped; bots in bots/sp_* build from the repo; islands pick it up with git pull + stop + ensure (run defaults, no state change). cloud-a2 runs on the panel from online1520 (cloud-a stopped, state kept). 16:16 champion plays the panel with the online bot as control and an im_p graft on every finalist, but its finalists were selected under the old rivals; first panel-selected champion 18:16 at the earliest. See [[cambc-local-judge]].

Champion tournament results: see [[cambc-ga-champions]].
- 18:07 UTC 16 Oct: **upload candidate mybot_06c663eb13.zip** = b672ef97f6 (cloud-d) on the online zip base: 100 fresh maps vs the online bot with panel rivals +0.127, pairs 138-77, 33-13 vs online (also held 100-48 vs v44). im_p off alone = +0.030 n.s. Runner-up 835d2c8a14 (cloud-b) 151-91. Not uploaded (user decides). Reports: ga-farm/champion/CONFIRM-*.md.
- 18:30 UTC 16 Oct: user rule = official site maps first, big wins there. b672 ported to teammate fixes bot (v51) as P_B672 + 7 sub-switches (/mnt/project-files/bot/teammate_fixes1_b672.patch): site maps no win (six-change variant 17-10, h2h 2-3), 100 sealed maps six 97-51. Champion cadence paused (online bot is now the teammate bot); re-base awaits the user's card.
- 19:05 UTC 16 Oct: **farm wound down** (user chose "Wind down" 18:59): no re-base on the teammate bot, no more champion runs, islands stopped with state kept. Final state + restart steps: /mnt/project-files/ga-farm/FINAL.md.

---
name: cambc-contest-monolith
description: 2026-10-16 contest 0-gem bug fixed as P_MONO (I031, PR #21 MERGED 09:29); monolith facts; stampede/eight are other problems; fuel noise makes "identical games" checks need --fuel 100000000
metadata:
  type: project
  modified: 2026-10-16T09:29:00.000Z
---

**Bug:** on contest the only gems are 2 monoliths (20000 hp, 200 str, 200 gems + 300 gold, respawn 150) + 10 gold clusters. study27-economy skipped the monolith (squad_needed > roster) and all gold (P_NOGOLD) -> 0 gems, 0 gold; 0-0 at r2000 is lost on the gold-earned tiebreak (rules: gems, then lifetime gold earned, then kills, then team B).
**Fix:** P_MONO 1 (main.cpp): when only monolith groups have gems, gold clusters are targets and the monolith is a whole-roster target. Local contest: 1000 gems by r1436-1670, 10/10 vs base/v30/study25/spar11/12/16. PR #21 (draft, base claude/online-bot-sync = PR #17), zip /mnt/project-files/bot/mybot_study27_economy_mono.zip, not uploaded.
**Monolith facts (replay of rank 1, engine 0.0.1):** it hits one champion ~126/round, top team rotates the tank; damage does NOT regenerate while nobody is near (persistent chip works); top team farms gold+items ~600 rounds first, then all bodies on it, 1000 gems at r1057.
**Stampede** (no monolith): one central group of 6 elks + 6 gem clusters (17400 hp, 360 gems) both teams fight over, plus many gold clusters; we chip it and get it stolen, and with P_NOGOLD our champions stay at 700-1300 hp vs their 1600-3100 from gold items. **Eight**: small 41x30 map with normal camps (270 gems/side); not monolith; we lose by tempo/fights. Both still open.
**Method lesson:** small code changes alter games on fuel-tight maps (corners, lanes, expanse, pilgrimage) even with the switch off. To prove "same logic elsewhere", compare cand-vs-base with base-vs-base at `cambc run --fuel 100000000` (script idea: scratch same.py). Online replays decode only with the visualiser wasm v0_0_1 (CAMBC_VIS_WASM). Bundle download: GET /api/v1/matches/<id>/bundle, poll pollUrl when pending.
Related: [[cambc-online-is-economy]] [[cambc-game-mechanics]] [[cambc-local-testing-review]] [[cambc-new-maps-1016]] [[cambc-harness]]
**09:22 thread extras:** rank 1 is Mite; fix is 19 lines, branch claude/monolith-contest, 10/10 both sides incl. vs online bot; 276/277 maps identical with unlimited fuel; gate.py --kind fight PASS, --kind farm undecided (fuel noise); not tested vs a rival that also hunts monoliths. Eight: rivals hit 1000 at r350-600, we end at 66-500. Next: gold pickup on stampede (P_NOGOLD costs hp), eight pace.
**09:29 UTC:** PR #21 merged; main = study27-economy + P_MONO. Upload of mybot_study27_economy_mono.zip to the site is the user's step, not done as of 09:29.

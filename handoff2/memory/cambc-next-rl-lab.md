---
name: cambc-next-rl-lab
description: 2026-10-20 the Codex-built next/ RL lab (stages 1-7, branch feat/stage7-promotion): what it is, honest results, engine pin, site v83, Windows setup guide path
metadata:
  type: project
  modified: 2026-10-20T20:00:51.152Z
---

The user's "RL system in the github" = `next/` on branch chain feat/stage2..feat/stage7-promotion (not on main; last commit d644fc3, 10-20 19:30 UTC, made with Codex).
Stages: lab/league (1), v76 demos (2), BC 305-param net (3), outcome critic (4), PPO (5), C++ runtime (6), `ppo-league-v12` = v76 rules + PPO picks attack targets only (7).
Honest results: PPO alone banks ~1.5 gems/game; v12 wins 140/140 vs starter but the PPO-off control wins equally -> no measured RL gain; never tested vs v76/v82/ladder.
Engine pin: requirements cambc==3.0.1, lab/mapgen.py needs mapeditor asset `v1_0_0-*.wasm` with fixed SHA (fails under 3.0.2 / patch 1.0.1 unless CAMBC_ENGINE_WASM set).
SITE: v12 was uploaded as platform **v83**; selection first cancelled (live v81 -> v82), then another team account ACTIVATED v83 at 2026-10-20 19:41 UTC and ranked games play it. Loop paused 20:02, user deciding keep v83 / back to v82 / judge v83.
archive/ and datasets/ gitignored -> re-freeze on a fresh clone. Tests: 122 pass after pip install.
Windows guide: /mnt/project-files/next-pc/RL-local-setup.md (thread "Running the RL system locally", 10-20 20:05 UTC).
Related: [[cambc-rl-assessment]] [[cambc-dqn]]

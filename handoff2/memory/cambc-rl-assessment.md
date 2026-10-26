---
name: cambc-rl-assessment
description: 2026-10-15 is RL viable for CAMBC: measured NN fuel cost per turn, why full RL is out before 3 Nov, the two viable pieces (CMA-ES tuning, learned fight/flee value)
metadata:
  type: project
  modified: 2026-10-15T22:23:59.515Z
---

Report: /mnt/project-files/analysis/rl-assessment-2026-10-15/README.md (+ fuelprobe_nn.cpp probe).
Deadline the user gave: bot done by 2026-11-03.

Measured (official toolchain, -O3 simd128): champion turn budget 100k fuel; dense net costs ~2.5 fuel per
multiply with SIMD (32-64-64-8 = ~17k, 128-256-256-16 = ~83k), scalar ~4x worse; reading visible champions ~5.4k.
So only a net of ~2-5k multiplies (or logistic regression) evaluated once per turn fits beside the bot.

Verdict: full-policy RL not viable (no step simulator, ~6 local games/s, self-play misleads per [[cambc-online-ab]],
online ~30 groups/hour only for validation). Viable: (A) CMA-ES over existing P_ params, weights patched into the
wasm without recompiling, opponent pool = sparrings + ghosts, top 3 validated online; (B) supervised fight/flee
value (die-in-N-rounds label) from decoded online replays, replacing the retreat threshold (cf. [[cambc-danger-level]]).

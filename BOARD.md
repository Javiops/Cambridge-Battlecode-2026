# GA farm board

Regenerated 2026-10-16 12:22:22 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 7 | 4808 | 16.9 | 9817d96ad8 (+0.036, 3) | {"P_FRONT": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_GP0_ON": 1, "P_NN_ON": 1, "P_HOLD": 187, "gp0": "((not FAV and (TDIST > 7)) and (((HP < 60) or not (NEAR >... | 11/0 | 2026-10-16 12:22:21 UTC |

Code: branch `ga-farm-pr@3948070`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

# GA farm board

Regenerated 2026-10-16 12:31:40 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 14 | 13236 | 14.3 | 8fbf792780 (+0.046, 1) | {"P_FRONT": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_GP1_ON": 1, "P_NN_ON": 1, "gp1": "((KILL or TCHAN) or ((REACH and FAV) or (HELP and (NEAR < GEMS))))", "nn... | 14/0 | 2026-10-16 12:31:39 UTC |

Code: branch `ga-farm-pr@cf1032f`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

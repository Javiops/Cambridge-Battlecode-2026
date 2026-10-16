# GA farm board

Regenerated 2026-10-16 12:54:21 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 29 | 32784 | 13.8 | f8b5439119 (+0.062, 3) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order": "FLEE>NEARRECALL>... | 28/0 | 2026-10-16 12:54:20 UTC |

Code: branch `ga-farm-pr@cf1032f`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

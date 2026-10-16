# GA farm board

Regenerated 2026-10-16 12:50:59 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 27 | 30172 | 12.9 | f8b5439119 (+0.053, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order": "FLEE>NEARRECALL>... | 26/0 | 2026-10-16 12:50:58 UTC |

Code: branch `ga-farm-pr@cf1032f`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

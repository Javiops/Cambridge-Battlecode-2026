# GA farm board

Regenerated 2026-10-16 14:16:50 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 28 | 42314 | 6.2 | 5648baa8db (+0.119, 4) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 25/69 | 2026-10-16 14:14:49 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 16 | 23084 | 4.8 | fb7fd31286 (+0.109, 1) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_KITE_HP": 147, "P_VOLLEY": 39, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 21/41 | 2026-10-16 14:09:03 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 11 | 14922 | 5.4 | 2e65494694 (+0.149, 1) | {"P_FLEE_PCT": 30, "P_BAIL_PCT": 25, "P_FRONT_ZONE": 2, "P_VOLLEY": 20, "P_CHASE_GEMS": 94, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_... | 13/26 | 2026-10-16 14:12:32 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 18 | 27076 | 6.0 | 36982c3986 (+0.101, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HOLD_R": 7, "P_TELE": 5, "order": "F... | 14/41 | 2026-10-16 14:12:33 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 13 | 19616 | 5.8 | 19f3461842 (+0.098, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 13/29 | 2026-10-16 14:10:40 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 20 | 29439 | 7.0 | 49f4345f2a (+0.082, 3) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 21/50 | 2026-10-16 14:12:22 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 16 | 24246 | 6.7 | 2d6bd9b5ce (+0.188, 1) | {"P_BAIL_PCT": 7, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 7, "P_GA_TRI... | 20/82 | 2026-10-16 14:13:15 UTC |
| micro | vm | micro | ga65a6 | 4 | 15 | 22786 | 5.7 | 6335759bfa (+0.067, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 15/32 | 2026-10-16 14:09:15 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 69 | 96700 | 14.9 | 94bd2723b9 (+0.173, 11) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 60/115 | 2026-10-16 14:16:49 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 18 | 27014 | 5.4 | ce552c8e22 (+0.073, 2) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "order": "FLEE>NEAR... | 17/43 | 2026-10-16 14:12:38 UTC |

Code: branch `claude/ga-farm-d37xlq@d2420cb`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

# GA farm board

Regenerated 2026-10-16 14:10:18 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 27 | 40648 | 7.5 | 5648baa8db (+0.160, 3) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 25/67 | 2026-10-16 14:10:14 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 16 | 23084 | 4.8 | fb7fd31286 (+0.109, 1) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_KITE_HP": 147, "P_VOLLEY": 39, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 21/41 | 2026-10-16 14:09:03 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 10 | 13552 | 6.0 | d20281a41e (+0.090, 2) | {"P_AVOID_DIST": 3, "P_ENGAGE2": 83, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_DANGER_T": 37, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 12/24 | 2026-10-16 14:08:17 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 17 | 25406 | 6.7 | 94bd2723b9 (+0.104, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 13/39 | 2026-10-16 14:07:55 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 12 | 17850 | 5.2 | 5648baa8db (+0.158, 1) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 12/27 | 2026-10-16 14:05:32 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 19 | 27653 | 5.8 | 49f4345f2a (+0.130, 2) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 21/48 | 2026-10-16 14:08:03 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 15 | 22516 | 7.0 | 31a2cc263e (+0.071, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 7, "order": "FLEE>NEARRECALL>... | 19/74 | 2026-10-16 14:08:53 UTC |
| micro | vm | micro | ga65a6 | 4 | 15 | 22786 | 5.7 | 6335759bfa (+0.067, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 15/32 | 2026-10-16 14:09:15 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 65 | 90342 | 15.4 | 94bd2723b9 (+0.218, 7) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 59/95 | 2026-10-16 14:09:40 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 17 | 25254 | 5.8 | 552562f454 (+0.089, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/41 | 2026-10-16 13:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@d2420cb`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

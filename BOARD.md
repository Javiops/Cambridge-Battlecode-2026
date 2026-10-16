# GA farm board

Regenerated 2026-10-16 14:09:41 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 26 | 39062 | 6.9 | 5648baa8db (+0.136, 2) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 24/65 | 2026-10-16 14:06:35 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 15 | 21582 | 4.0 | 49f4345f2a (+0.137, 2) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 21/39 | 2026-10-16 14:03:45 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 9 | 12190 | 5.8 | d20281a41e (+0.164, 1) | {"P_AVOID_DIST": 3, "P_ENGAGE2": 83, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_DANGER_T": 37, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 10/22 | 2026-10-16 14:04:27 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 16 | 23630 | 5.7 | 8b5b1deea0 (+0.096, 1) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_TWIN": 1, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, ... | 13/37 | 2026-10-16 14:03:28 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 12 | 17850 | 5.2 | 5648baa8db (+0.158, 1) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 12/27 | 2026-10-16 14:05:32 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 18 | 26025 | 5.5 | 6335759bfa (+0.083, 5) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 19/45 | 2026-10-16 14:03:24 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 14 | 20820 | 7.3 | 44141b7bfa (+0.073, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_BAG_QUIET": 37... | 17/70 | 2026-10-16 14:04:48 UTC |
| micro | vm | micro | ga65a6 | 4 | 14 | 20992 | 4.6 | 6335759bfa (+0.077, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 14/30 | 2026-10-16 14:03:58 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 65 | 90342 | 15.4 | 94bd2723b9 (+0.218, 7) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 59/95 | 2026-10-16 14:09:40 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 17 | 25254 | 5.8 | 552562f454 (+0.089, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/41 | 2026-10-16 13:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@d2420cb`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

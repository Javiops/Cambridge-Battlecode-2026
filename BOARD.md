# GA farm board

Regenerated 2026-10-16 16:29:50 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 9 | 14306 | 3.4 | b03930f2a0 (+0.140, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 6/20 | 2026-10-16 16:29:40 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 36 | 57202 | 4.3 | 0e45e3ff04 (+0.162, 2) | {"P_FLEE_PCT": 21, "P_AVOID_DIST": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_... | 29/99 | 2026-10-16 16:27:26 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 38 | 60112 | 7.6 | fd095a2e9c (+0.149, 4) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_KITE_ZONE": 3, "P_VOLLEY": 20, "P_CHASE_GEMS": 30, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "... | 29/102 | 2026-10-16 16:25:00 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 44 | 72738 | 6.8 | 6fdb489afd (+0.086, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 25/118 | 2026-10-16 16:27:04 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 36 | 59568 | 5.9 | 38d9b3078d (+0.118, 11) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 21/93 | 2026-10-16 16:28:04 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 42 | 67797 | 6.5 | cbcd8bcb0f (+0.099, 2) | {"P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHA... | 32/118 | 2026-10-16 16:26:40 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 47 | 77183 | 7.3 | b5ff18510e (+0.126, 14) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 37/311 | 2026-10-16 16:29:42 UTC |
| micro | vm | micro | ga65a6 | 4 | 43 | 70594 | 6.0 | 314e9672aa (+0.096, 6) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_CHASE_GEMS": 126, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW":... | 41/114 | 2026-10-16 16:27:39 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 135 | 211573 | 12.2 | e7cd1add65 (+0.136, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_FRONT_OUT": 174, "P_GA_KITE_HP": 143, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_D... | 83/342 | 2026-10-16 16:29:39 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 43 | 70850 | 6.3 | 80c62b3935 (+0.134, 14) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 32/110 | 2026-10-16 16:27:31 UTC |

Code: branch `claude/ga-farm-d37xlq@a6bc6ab`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

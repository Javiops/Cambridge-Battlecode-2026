# GA farm board

Regenerated 2026-10-16 16:24:32 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 8 | 12574 | 5.2 | 4541b4515c (+0.068, 4) | {"P_UNI_FLEE": 43, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_SHOOT": 0, "P_CALLHELP": 1, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 6/18 | 2026-10-16 16:21:06 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 35 | 55264 | 4.0 | d6df17a265 (+0.155, 2) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 99, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 28/91 | 2026-10-16 16:19:53 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 37 | 58030 | 5.5 | d266d9a549 (+0.138, 6) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 20, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 29/99 | 2026-10-16 16:20:26 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 42 | 68870 | 6.6 | 0f5b108ea6 (+0.110, 4) | {"P_UNI_FLEE": 39, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_... | 25/113 | 2026-10-16 16:17:11 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 34 | 55558 | 3.2 | 38d9b3078d (+0.121, 9) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 21/86 | 2026-10-16 16:15:35 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 40 | 63731 | 4.7 | 0f5b108ea6 (+0.105, 5) | {"P_UNI_FLEE": 39, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_... | 32/109 | 2026-10-16 16:15:26 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 45 | 73271 | 7.6 | b5ff18510e (+0.154, 12) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 37/296 | 2026-10-16 16:20:53 UTC |
| micro | vm | micro | ga65a6 | 4 | 41 | 67250 | 6.2 | 314e9672aa (+0.103, 4) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_CHASE_GEMS": 126, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW":... | 40/108 | 2026-10-16 16:19:13 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 133 | 207925 | 16.2 | e7cd1add65 (+0.167, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_FRONT_OUT": 174, "P_GA_KITE_HP": 143, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_D... | 80/340 | 2026-10-16 16:24:31 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 41 | 67008 | 6.6 | 8161284fa4 (+0.138, 4) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 32/106 | 2026-10-16 16:16:30 UTC |

Code: branch `claude/ga-farm-d37xlq@cae2273`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

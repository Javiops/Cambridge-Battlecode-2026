# GA farm board

Regenerated 2026-10-16 17:32:46 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 14 | 24482 | 3.4 | 607b44a953 (+0.148, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 152, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_SAFESTEP": 0, "P_NOCHASE":... | 10/30 | 2026-10-16 17:25:44 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 44 | 73086 | 5.3 | 0792539a34 (+0.106, 1) | {"P_AVOID_DIST": 7, "P_KITE_ZONE": 5, "P_GA_KITE_HP": 150, "P_VOLLEY": 40, "P_CHASE_GEMS": 192, "P_DANGER_T": 67, "P_DANGER_R": 8, "P_FRONT": 0, "P_SAFESTEP"... | 33/120 | 2026-10-16 17:22:46 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 49 | 81192 | 5.6 | d2ecc6d3d5 (+0.158, 2) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 34/153 | 2026-10-16 17:23:49 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 54 | 92092 | 6.2 | de22596d2f (+0.139, 5) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": ... | 32/145 | 2026-10-16 17:23:57 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 46 | 78810 | 5.6 | 20a6e65633 (+0.113, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 24/122 | 2026-10-16 17:23:29 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 51 | 85337 | 5.2 | 150107f60e (+0.124, 8) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 37/140 | 2026-10-16 17:21:39 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 60 | 102113 | 8.7 | b5ff18510e (+0.116, 26) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 41/400 | 2026-10-16 17:22:12 UTC |
| micro | vm | micro | ga65a6 | 4 | 54 | 88974 | 6.0 | 47dcc0639a (+0.114, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 45/153 | 2026-10-16 17:23:41 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 164 | 265395 | 13.9 | 9543e4f42a (+0.177, 9) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT... | 90/397 | 2026-10-16 17:32:45 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 52 | 88364 | 5.9 | 8a8db659ae (+0.117, 19) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 35/131 | 2026-10-16 17:23:49 UTC |

Code: branch `claude/ga-farm-d37xlq@cae2273`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

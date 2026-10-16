# GA farm board

Regenerated 2026-10-16 18:00:36 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 17 | 30182 | 3.1 | 4a1104f279 (+0.114, 6) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TELE": 5, "P_NE... | 12/37 | 2026-10-16 17:55:38 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 48 | 81046 | 4.7 | 69b69e7e2b (+0.152, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 34/131 | 2026-10-16 17:49:38 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 55 | 92754 | 7.5 | d2ecc6d3d5 (+0.180, 8) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 37/171 | 2026-10-16 17:53:20 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 60 | 103522 | 6.3 | 69b69e7e2b (+0.133, 3) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/170 | 2026-10-16 17:54:54 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 50 | 86560 | 5.7 | 20a6e65633 (+0.100, 6) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 25/133 | 2026-10-16 17:51:18 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 56 | 94899 | 4.5 | 8c6abfb7e1 (+0.234, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 42/154 | 2026-10-16 17:52:38 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 68 | 117183 | 8.1 | 9543e4f42a (+0.150, 6) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT... | 45/448 | 2026-10-16 17:55:09 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 177 | 289471 | 13.8 | 441aaece6c (+0.183, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0,... | 91/421 | 2026-10-16 18:00:35 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 57 | 97858 | 6.2 | 9608510352 (+0.164, 2) | {"P_UNI_FLEE": 39, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_S... | 38/145 | 2026-10-16 17:51:11 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

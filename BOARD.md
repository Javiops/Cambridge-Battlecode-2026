# GA farm board

Regenerated 2026-10-16 18:34:17 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 22 | 39908 | 8.3 | 5badfecec9 (+0.141, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 14/48 | 2026-10-16 18:34:09 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 54 | 92596 | 4.7 | 137994c5d9 (+0.111, 15) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/146 | 2026-10-16 18:29:28 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 62 | 106344 | 6.3 | 8d58b7c017 (+0.200, 2) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 126, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 39/194 | 2026-10-16 18:30:12 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 68 | 118528 | 7.0 | c9490ad43d (+0.103, 11) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 36/195 | 2026-10-16 18:31:53 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 57 | 99698 | 6.5 | 9271169af0 (+0.156, 5) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 29/152 | 2026-10-16 18:29:15 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 63 | 108501 | 5.6 | e74d543089 (+0.193, 4) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 49/179 | 2026-10-16 18:32:03 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 76 | 132385 | 7.8 | c960496a4e (+0.182, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_GA_FAV": 77, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER... | 48/492 | 2026-10-16 18:30:35 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 192 | 317827 | 13.2 | 0f67b1ab8c (+0.162, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_ENGAGE2": 75, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P... | 102/437 | 2026-10-16 18:34:15 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 65 | 112992 | 5.5 | f79d936666 (+0.194, 4) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 43/165 | 2026-10-16 18:32:48 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

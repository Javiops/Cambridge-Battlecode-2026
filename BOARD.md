# GA farm board

Regenerated 2026-10-16 17:17:39 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 13 | 22444 | 3.0 | 4a1104f279 (+0.126, 2) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TELE": 5, "P_NE... | 9/28 | 2026-10-16 17:15:41 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 42 | 69202 | 4.9 | a7974643e4 (+0.162, 3) | {"P_AVOID_DIST": 7, "P_KITE_ZONE": 5, "P_VOLLEY": 40, "P_CHASE_GEMS": 192, "P_DANGER_T": 67, "P_DANGER_R": 8, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 32/116 | 2026-10-16 17:09:34 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 47 | 77334 | 5.9 | 82abc2023a (+0.116, 9) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1... | 33/149 | 2026-10-16 17:12:26 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 52 | 88212 | 6.8 | 41614bbc09 (+0.130, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 30/141 | 2026-10-16 17:13:53 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 44 | 75118 | 6.2 | 33cbab259d (+0.123, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 23/118 | 2026-10-16 17:12:43 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 50 | 83357 | 6.9 | 39cb7f84d2 (+0.138, 3) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 37/138 | 2026-10-16 17:15:15 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 58 | 98369 | 7.9 | 441aaece6c (+0.154, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0,... | 41/389 | 2026-10-16 17:15:00 UTC |
| micro | vm | micro | ga65a6 | 4 | 52 | 85682 | 5.2 | 5f9da0c758 (+0.096, 20) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 44/149 | 2026-10-16 17:10:00 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 157 | 252883 | 13.9 | 9543e4f42a (+0.179, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT... | 89/378 | 2026-10-16 17:17:36 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 50 | 84412 | 6.5 | 47b779d1e8 (+0.117, 5) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_NOCHASE": 0, "... | 34/127 | 2026-10-16 17:11:46 UTC |

Code: branch `claude/ga-farm-d37xlq@cae2273`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

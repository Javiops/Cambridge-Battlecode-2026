# GA farm board

Regenerated 2026-10-16 15:59:59 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 3 | 4158 | 6.0 | 8161284fa4 (+0.100, 3) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 3/6 | 2026-10-16 15:58:56 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 32 | 49192 | 4.5 | 3b80fd2bd1 (+0.124, 8) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 28/81 | 2026-10-16 15:54:46 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 33 | 50092 | 5.6 | 258ebbcee4 (+0.185, 2) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1... | 26/82 | 2026-10-16 15:53:47 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 38 | 61090 | 4.5 | 6898bd017e (+0.109, 3) | {"P_FLEE_PCT": 27, "P_AVOID_DIST": 3, "P_GA_KILL_X": 8, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_O... | 24/97 | 2026-10-16 15:57:54 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 32 | 51574 | 6.2 | e4eae6a7a8 (+0.145, 7) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 20/81 | 2026-10-16 15:54:56 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 37 | 57743 | 4.6 | 3f0c56031d (+0.159, 2) | {"P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 32/100 | 2026-10-16 15:58:00 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 41 | 65867 | 4.8 | b5ff18510e (+0.180, 8) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 36/247 | 2026-10-16 15:56:48 UTC |
| micro | vm | micro | ga65a6 | 4 | 37 | 60744 | 4.0 | 5f9da0c758 (+0.087, 8) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 37/93 | 2026-10-16 15:58:45 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 122 | 186399 | 13.0 | 6fdb489afd (+0.124, 10) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 78/291 | 2026-10-16 15:59:58 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 38 | 61224 | 4.0 | 615e23fad9 (+0.145, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 30/96 | 2026-10-16 15:53:47 UTC |

Code: branch `claude/ga-farm-d37xlq@4fa99e8`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

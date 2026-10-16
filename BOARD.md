# GA farm board

Regenerated 2026-10-16 15:55:02 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 2 | 2636 | 4.7 | 8161284fa4 (+0.129, 2) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 0/4 | 2026-10-16 15:54:35 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 31 | 47334 | 3.9 | bfa257ae73 (+0.137, 7) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 28/79 | 2026-10-16 15:47:57 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 33 | 50092 | 5.6 | 258ebbcee4 (+0.185, 2) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1... | 26/82 | 2026-10-16 15:53:47 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 37 | 59122 | 6.3 | 660af4d8d9 (+0.137, 2) | {"P_FLEE_PCT": 27, "P_AVOID_DIST": 3, "P_GA_KILL_X": 8, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_O... | 22/95 | 2026-10-16 15:49:30 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 31 | 49892 | 6.2 | e4eae6a7a8 (+0.167, 6) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 20/79 | 2026-10-16 15:50:24 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 36 | 55775 | 4.8 | 9bc5193917 (+0.148, 1) | {"P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 31/98 | 2026-10-16 15:48:02 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 40 | 64171 | 7.6 | 7530068f4c (+0.177, 7) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 36/243 | 2026-10-16 15:46:16 UTC |
| micro | vm | micro | ga65a6 | 4 | 36 | 59070 | 6.7 | 5f9da0c758 (+0.098, 7) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 36/91 | 2026-10-16 15:51:42 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 120 | 182277 | 11.8 | 2ccff80827 (+0.138, 10) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT... | 78/287 | 2026-10-16 15:54:59 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 38 | 61224 | 4.0 | 615e23fad9 (+0.145, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 30/96 | 2026-10-16 15:53:47 UTC |

Code: branch `claude/ga-farm-d37xlq@4fa99e8`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

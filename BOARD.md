# GA farm board

Regenerated 2026-10-16 16:04:40 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 4 | 5686 | 7.2 | 8161284fa4 (+0.069, 4) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 3/9 | 2026-10-16 16:02:35 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 32 | 49192 | 4.5 | 3b80fd2bd1 (+0.124, 8) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 28/81 | 2026-10-16 15:54:46 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 34 | 52060 | 4.5 | 7ca0b89cdf (+0.190, 1) | {"P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 28/85 | 2026-10-16 16:01:27 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 39 | 63106 | 7.5 | 51d8bf8c16 (+0.097, 3) | {"P_BAIL_PCT": 13, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 24/100 | 2026-10-16 16:02:26 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 32 | 51574 | 6.2 | e4eae6a7a8 (+0.145, 7) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 20/81 | 2026-10-16 15:54:56 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 38 | 59687 | 7.3 | 13ebc26628 (+0.126, 7) | {"P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R... | 32/103 | 2026-10-16 16:02:27 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 41 | 65867 | 4.8 | b5ff18510e (+0.180, 8) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 36/247 | 2026-10-16 15:56:48 UTC |
| micro | vm | micro | ga65a6 | 4 | 37 | 60744 | 4.0 | 5f9da0c758 (+0.087, 8) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 37/93 | 2026-10-16 15:58:45 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 124 | 190353 | 16.7 | 8342e650ad (+0.133, 1) | {"P_LOWHP": 49, "P_CHASE_GEMS": 94, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_GEMS": 5, "P_TRIBUTE_NEAR": ... | 79/300 | 2026-10-16 16:04:39 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 39 | 62934 | 4.0 | c1d63b6631 (+0.143, 5) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP1_ON": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "o... | 31/99 | 2026-10-16 16:00:58 UTC |

Code: branch `claude/ga-farm-d37xlq@4fa99e8`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

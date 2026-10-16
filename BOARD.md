# GA farm board

Regenerated 2026-10-16 16:07:07 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 5 | 7264 | 6.0 | 4541b4515c (+0.091, 1) | {"P_UNI_FLEE": 43, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_SHOOT": 0, "P_CALLHELP": 1, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 3/11 | 2026-10-16 16:07:02 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 33 | 51232 | 3.3 | 858c305f08 (+0.116, 4) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 192, "P_DANGER_T": 67, "P_DANGER_R": 8, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHA... | 28/83 | 2026-10-16 16:05:27 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 34 | 52060 | 4.5 | 7ca0b89cdf (+0.190, 1) | {"P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 28/85 | 2026-10-16 16:01:27 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 40 | 65062 | 7.5 | e7ba90eac2 (+0.085, 1) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLO... | 24/102 | 2026-10-16 16:06:46 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 33 | 53542 | 3.4 | 38d9b3078d (+0.149, 8) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 20/83 | 2026-10-16 16:05:07 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 38 | 59687 | 7.3 | 13ebc26628 (+0.126, 7) | {"P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R... | 32/103 | 2026-10-16 16:02:27 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 42 | 67661 | 3.1 | b5ff18510e (+0.171, 9) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 37/251 | 2026-10-16 16:06:33 UTC |
| micro | vm | micro | ga65a6 | 4 | 38 | 62346 | 3.7 | 5f9da0c758 (+0.079, 9) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 37/97 | 2026-10-16 16:06:04 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 125 | 192283 | 15.4 | b03930f2a0 (+0.128, 11) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 79/311 | 2026-10-16 16:06:48 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 39 | 62934 | 4.0 | c1d63b6631 (+0.143, 5) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP1_ON": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "o... | 31/99 | 2026-10-16 16:00:58 UTC |

Code: branch `claude/ga-farm-d37xlq@a6bc6ab`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

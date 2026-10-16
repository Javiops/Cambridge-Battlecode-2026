# GA farm board

Regenerated 2026-10-16 16:49:22 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 10 | 16304 | 2.9 | b03930f2a0 (+0.178, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 6/22 | 2026-10-16 16:41:17 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 37 | 59212 | 4.3 | 70ac586e7d (+0.121, 12) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL":... | 30/102 | 2026-10-16 16:35:18 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 40 | 63896 | 6.3 | 1e63d4e561 (+0.125, 1) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 49, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW":... | 31/115 | 2026-10-16 16:35:47 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 46 | 76632 | 7.1 | 5f8b15c564 (+0.134, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 26/125 | 2026-10-16 16:36:32 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 38 | 63612 | 6.6 | 38d9b3078d (+0.102, 13) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 21/103 | 2026-10-16 16:38:39 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 43 | 69723 | 5.1 | 13ebc26628 (+0.099, 11) | {"P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R... | 33/121 | 2026-10-16 16:32:59 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 49 | 81035 | 8.3 | b5ff18510e (+0.121, 16) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 37/322 | 2026-10-16 16:37:53 UTC |
| micro | vm | micro | ga65a6 | 4 | 45 | 74032 | 4.9 | 872451f39c (+0.100, 1) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_RECALL_PCT": 41, "P_GA_SPAWN_HEAL": 92, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUT... | 41/123 | 2026-10-16 16:37:44 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 144 | 228715 | 14.1 | c9490ad43d (+0.182, 5) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 85/359 | 2026-10-16 16:49:21 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 45 | 74784 | 5.7 | 95d5790e6f (+0.130, 2) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_TWIN": 1, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON"... | 33/116 | 2026-10-16 16:37:52 UTC |

Code: branch `claude/ga-farm-d37xlq@cae2273`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

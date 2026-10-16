# GA farm board

Regenerated 2026-10-16 16:58:39 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 11 | 18374 | 2.7 | b03930f2a0 (+0.140, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 8/24 | 2026-10-16 16:54:23 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 39 | 63094 | 4.7 | 045529512f (+0.114, 4) | {"P_FLEE_PCT": 12, "P_GA_FAV": 88, "P_GA_KILL_X": 7, "P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P... | 31/107 | 2026-10-16 16:49:37 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 43 | 69772 | 6.3 | f14ffa808a (+0.154, 2) | {"P_RECALL_PCT": 39, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 20, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 31/135 | 2026-10-16 16:52:01 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 48 | 80498 | 3.6 | 441aaece6c (+0.164, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0,... | 27/131 | 2026-10-16 16:51:06 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 40 | 67354 | 6.0 | 38d9b3078d (+0.093, 15) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 21/108 | 2026-10-16 16:48:55 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 45 | 73597 | 4.2 | a54c7b1269 (+0.190, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 34/126 | 2026-10-16 16:48:48 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 52 | 87009 | 8.4 | 4a1104f279 (+0.177, 3) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TELE": 5, "P_NE... | 38/344 | 2026-10-16 16:51:10 UTC |
| micro | vm | micro | ga65a6 | 4 | 49 | 80550 | 6.8 | 8502b05de3 (+0.101, 5) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_RECALL_PCT": 42, "P_ENGAGE2": 71, "P_GA_SPAWN_HEAL": 85, "P_CHASE_GEMS": 126, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHA... | 43/133 | 2026-10-16 16:53:04 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 148 | 236389 | 15.2 | 20a6e65633 (+0.213, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 87/361 | 2026-10-16 16:58:37 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 47 | 78606 | 5.1 | 2e52cd4353 (+0.126, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_SHOOT": 2, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 34/120 | 2026-10-16 16:50:46 UTC |

Code: branch `claude/ga-farm-d37xlq@cae2273`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

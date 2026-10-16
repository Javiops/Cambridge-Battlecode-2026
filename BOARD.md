# GA farm board

Regenerated 2026-10-16 18:44:57 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 24 | 43750 | 7.2 | 805a843f0a (+0.134, 9) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "P_NE_POWER_O... | 15/53 | 2026-10-16 18:43:19 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 56 | 96488 | 4.9 | 00040e377a (+0.135, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_BAIL_PCT": 1, "P_AVOID_DIST": 2, "P_GA_AVOID_HP": 66, "P_GA_KILL_X": 8, "P_FRONT_OUT": 159, "P_VOLLEY": 35, "P_CHAS... | 36/152 | 2026-10-16 18:43:00 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 64 | 110038 | 4.4 | 41cca0b813 (+0.171, 5) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 139, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 41/200 | 2026-10-16 18:42:14 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 70 | 122226 | 7.0 | 76c8587a3d (+0.133, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 37/200 | 2026-10-16 18:40:14 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 58 | 101526 | 3.7 | 9271169af0 (+0.136, 6) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 29/155 | 2026-10-16 18:37:30 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 64 | 110367 | 6.5 | f79d936666 (+0.162, 5) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 49/182 | 2026-10-16 18:36:53 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 78 | 136355 | 7.9 | c960496a4e (+0.152, 5) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_GA_FAV": 77, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER... | 49/502 | 2026-10-16 18:39:04 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 197 | 327007 | 14.5 | f05e630831 (+0.203, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_ENGAGE2": 75, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P... | 105/451 | 2026-10-16 18:44:55 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 67 | 116626 | 5.8 | c960496a4e (+0.210, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_GA_FAV": 77, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER... | 43/169 | 2026-10-16 18:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

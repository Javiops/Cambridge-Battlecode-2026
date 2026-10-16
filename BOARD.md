# GA farm board

Regenerated 2026-10-16 18:53:22 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 26 | 47424 | 7.5 | c960496a4e (+0.147, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_GA_FAV": 77, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER... | 15/57 | 2026-10-16 18:51:43 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 57 | 98426 | 3.9 | f0726743d1 (+0.118, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_CHASE_GEMS": 161, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P... | 37/154 | 2026-10-16 18:51:16 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 64 | 110038 | 4.4 | 41cca0b813 (+0.171, 5) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 139, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 41/200 | 2026-10-16 18:42:14 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 71 | 124126 | 5.3 | c9490ad43d (+0.099, 14) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 37/202 | 2026-10-16 18:46:14 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 59 | 103420 | 3.9 | 1f25dcef88 (+0.129, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 29/158 | 2026-10-16 18:45:40 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 65 | 112275 | 4.4 | 0fde53f045 (+0.156, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 49/185 | 2026-10-16 18:44:13 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 80 | 140233 | 8.2 | 17e085aa5b (+0.228, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_GA_FAV": 77, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 100, "P_DANGER": 5, "P_DANGER... | 50/511 | 2026-10-16 18:48:09 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 201 | 334151 | 14.3 | f05e630831 (+0.187, 8) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_ENGAGE2": 75, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P... | 107/454 | 2026-10-16 18:53:20 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 68 | 118470 | 4.8 | f79d936666 (+0.171, 7) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 44/171 | 2026-10-16 18:49:03 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

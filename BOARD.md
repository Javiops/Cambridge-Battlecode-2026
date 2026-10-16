# GA farm board

Regenerated 2026-10-16 18:58:31 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 27 | 49312 | 7.3 | 9c25a22c56 (+0.118, 2) | {"P_GA_AVOID_HP": 52, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_S... | 15/59 | 2026-10-16 18:56:07 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 57 | 98426 | 3.9 | f0726743d1 (+0.118, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_CHASE_GEMS": 161, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P... | 37/154 | 2026-10-16 18:51:16 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 65 | 112060 | 3.1 | e2304cc502 (+0.164, 11) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 139, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 41/202 | 2026-10-16 18:53:14 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 72 | 125918 | 5.2 | c9490ad43d (+0.094, 15) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 37/204 | 2026-10-16 18:51:57 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 60 | 105304 | 4.1 | 9271169af0 (+0.103, 8) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 30/160 | 2026-10-16 18:53:18 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 66 | 114307 | 4.5 | e2304cc502 (+0.162, 3) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 139, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 50/187 | 2026-10-16 18:51:42 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 82 | 143923 | 8.0 | 17e085aa5b (+0.216, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_GA_FAV": 77, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 100, "P_DANGER": 5, "P_DANGER... | 53/522 | 2026-10-16 18:55:41 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 203 | 337785 | 11.7 | 27ab065f9c (+0.189, 2) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1... | 107/456 | 2026-10-16 18:58:29 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 69 | 120368 | 6.6 | c9490ad43d (+0.161, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 44/173 | 2026-10-16 18:53:53 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

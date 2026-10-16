# GA farm board

Regenerated 2026-10-16 17:36:51 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 15 | 26410 | 3.0 | 3b1330baa8 (+0.139, 3) | {"P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, ... | 11/32 | 2026-10-16 17:36:27 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 46 | 77092 | 5.6 | 6c41b87c04 (+0.107, 1) | {"P_FRONT_ZONE": 2, "P_KITE_OUT": 0, "P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SH... | 33/126 | 2026-10-16 17:35:01 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 51 | 85114 | 6.8 | e2304cc502 (+0.195, 1) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 139, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 35/158 | 2026-10-16 17:33:43 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 56 | 95996 | 5.8 | de22596d2f (+0.108, 7) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": ... | 33/159 | 2026-10-16 17:34:18 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 47 | 80694 | 3.0 | 20a6e65633 (+0.117, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 24/125 | 2026-10-16 17:33:49 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 53 | 89165 | 4.0 | 1bd34728cd (+0.112, 3) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 39/146 | 2026-10-16 17:34:54 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 63 | 107785 | 7.5 | 9543e4f42a (+0.178, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT... | 41/421 | 2026-10-16 17:33:44 UTC |
| micro | vm | micro | ga65a6 | 4 | 56 | 92374 | 6.8 | 47dcc0639a (+0.115, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 45/157 | 2026-10-16 17:33:18 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 166 | 269147 | 15.3 | 086b00fcb5 (+0.148, 14) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 90/397 | 2026-10-16 17:36:49 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 54 | 92142 | 7.3 | 8a8db659ae (+0.117, 21) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 35/136 | 2026-10-16 17:33:35 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

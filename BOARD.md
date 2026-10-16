# GA farm board

Regenerated 2026-10-16 18:42:46 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 23 | 41790 | 7.1 | 3b1330baa8 (+0.142, 8) | {"P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, ... | 15/51 | 2026-10-16 18:38:38 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 55 | 94596 | 4.7 | bccdedfce9 (+0.144, 2) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL":... | 35/149 | 2026-10-16 18:36:33 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 63 | 108234 | 6.2 | 8d58b7c017 (+0.175, 3) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 126, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 41/197 | 2026-10-16 18:35:19 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 69 | 120374 | 8.0 | 96d3234ad3 (+0.136, 2) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_SPAWN_HEAL": 68, "P_FRONT_ZONE": 4, "P_KITE_ZONE": 3, "P_VOLLEY": 20, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFES... | 36/197 | 2026-10-16 18:35:47 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 58 | 101526 | 3.7 | 9271169af0 (+0.136, 6) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 29/155 | 2026-10-16 18:37:30 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 64 | 110367 | 6.5 | f79d936666 (+0.162, 5) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 49/182 | 2026-10-16 18:36:53 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 77 | 134409 | 7.8 | c960496a4e (+0.166, 4) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_GA_FAV": 77, "P_FRONT_ZONE": 2, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER... | 49/497 | 2026-10-16 18:34:55 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 196 | 325171 | 14.5 | f05e630831 (+0.191, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_ENGAGE2": 75, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P... | 105/448 | 2026-10-16 18:42:45 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 66 | 114868 | 6.6 | d3fe1b2b4f (+0.190, 5) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": ... | 43/167 | 2026-10-16 18:37:36 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

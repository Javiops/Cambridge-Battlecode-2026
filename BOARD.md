# GA farm board

Regenerated 2026-10-16 18:07:34 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 18 | 32100 | 3.8 | b2b563efc2 (+0.121, 5) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TE... | 13/39 | 2026-10-16 18:04:16 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 50 | 84986 | 5.1 | 248e9ff225 (+0.141, 1) | {"P_FLEE_PCT": 31, "P_RECALL_PCT": 61, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP":... | 35/137 | 2026-10-16 18:02:44 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 57 | 96804 | 6.0 | d2ecc6d3d5 (+0.158, 10) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 37/182 | 2026-10-16 18:03:39 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 61 | 105512 | 5.9 | 69b69e7e2b (+0.107, 4) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/174 | 2026-10-16 18:00:35 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 52 | 90270 | 6.5 | 20a6e65633 (+0.106, 8) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 26/140 | 2026-10-16 18:01:31 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 57 | 96879 | 5.4 | 8c6abfb7e1 (+0.203, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 43/158 | 2026-10-16 17:58:45 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 69 | 119141 | 7.8 | 56fd53c8f2 (+0.163, 7) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1... | 45/455 | 2026-10-16 17:59:22 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 180 | 295079 | 13.4 | 441aaece6c (+0.167, 5) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0,... | 93/423 | 2026-10-16 18:07:33 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 59 | 101704 | 6.6 | 8161284fa4 (+0.112, 7) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 38/151 | 2026-10-16 18:01:08 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

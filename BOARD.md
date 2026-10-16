# GA farm board

Regenerated 2026-10-16 18:19:33 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 20 | 35910 | 3.7 | b2b563efc2 (+0.145, 7) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TE... | 13/43 | 2026-10-16 18:19:28 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 52 | 88864 | 4.6 | 137994c5d9 (+0.114, 13) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/142 | 2026-10-16 18:16:17 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 59 | 100716 | 6.3 | d2ecc6d3d5 (+0.160, 12) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 37/187 | 2026-10-16 18:13:58 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 65 | 113088 | 6.9 | 06c61eebb4 (+0.126, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/188 | 2026-10-16 18:19:10 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 55 | 95942 | 6.0 | 9271169af0 (+0.164, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 27/147 | 2026-10-16 18:18:21 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 60 | 102829 | 6.2 | f79d936666 (+0.191, 4) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 48/172 | 2026-10-16 18:15:32 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 72 | 124923 | 8.2 | e0710ee0e6 (+0.133, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0,... | 46/474 | 2026-10-16 18:13:25 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 185 | 304213 | 15.0 | 2d2901de65 (+0.142, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 96/428 | 2026-10-16 18:18:28 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 62 | 107352 | 5.1 | c9490ad43d (+0.142, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 39/159 | 2026-10-16 18:17:59 UTC |

Code: branch `claude/ga-farm-d37xlq@a6bc6ab`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

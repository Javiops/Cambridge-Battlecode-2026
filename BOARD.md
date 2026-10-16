# GA farm board

Regenerated 2026-10-16 18:16:22 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 19 | 33988 | 5.1 | 2c9b271d24 (+0.157, 1) | {"P_UNI_FLEE": 47, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE"... | 13/41 | 2026-10-16 18:10:36 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 51 | 86916 | 5.0 | 137994c5d9 (+0.125, 12) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/139 | 2026-10-16 18:09:13 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 58 | 98726 | 6.4 | d2ecc6d3d5 (+0.151, 11) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 37/184 | 2026-10-16 18:08:41 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 63 | 109280 | 6.6 | 06c61eebb4 (+0.204, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/179 | 2026-10-16 18:09:52 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 53 | 92258 | 5.4 | 20a6e65633 (+0.107, 9) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0,... | 26/142 | 2026-10-16 18:07:38 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 59 | 100935 | 5.7 | f79d936666 (+0.186, 3) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 46/165 | 2026-10-16 18:10:27 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 71 | 123009 | 6.3 | 56fd53c8f2 (+0.134, 9) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1... | 45/469 | 2026-10-16 18:09:31 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 184 | 302365 | 14.4 | f0726743d1 (+0.142, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_CHASE_GEMS": 161, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P... | 95/428 | 2026-10-16 18:16:21 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 60 | 103642 | 5.6 | 84954d0cc5 (+0.145, 2) | {"P_GA_AVOID_HP": 36, "P_ENGAGE2": 62, "P_KITE_ZONE": 3, "P_VOLLEY": 20, "P_CHASE_GEMS": 94, "P_DANGER_R": 3, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 38/154 | 2026-10-16 18:06:55 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

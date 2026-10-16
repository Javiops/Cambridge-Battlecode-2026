# GA farm board

Regenerated 2026-10-16 17:49:21 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 16 | 28254 | 3.5 | 805a843f0a (+0.127, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "P_NE_POWER_O... | 12/34 | 2026-10-16 17:45:12 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 47 | 79050 | 4.4 | 6c41b87c04 (+0.137, 2) | {"P_FRONT_ZONE": 2, "P_KITE_OUT": 0, "P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SH... | 33/128 | 2026-10-16 17:42:32 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 53 | 88994 | 6.5 | d2ecc6d3d5 (+0.181, 6) | {"P_RECALL_PCT": 39, "P_GA_AVOID_HP": 36, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": ... | 36/165 | 2026-10-16 17:43:52 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 57 | 97934 | 4.5 | de22596d2f (+0.104, 8) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": ... | 33/161 | 2026-10-16 17:41:28 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 48 | 82572 | 5.7 | 33cbab259d (+0.102, 8) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 24/127 | 2026-10-16 17:39:23 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 54 | 91011 | 5.9 | 69b69e7e2b (+0.136, 3) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 40/148 | 2026-10-16 17:40:08 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 65 | 111539 | 6.0 | 07ba5d0c1c (+0.188, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_RECALL_NEAR": 9, "P_GA_FAV": 69, "P_VOLLEY": 40, "P_CHASE_GEMS": 94, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P... | 43/432 | 2026-10-16 17:43:12 UTC |
| micro | vm | micro | ga65a6 | 4 | 58 | 95690 | 6.3 | 5f9da0c758 (+0.098, 26) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 45/166 | 2026-10-16 17:41:38 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 172 | 280087 | 14.6 | 032889f775 (+0.165, 2) | {"P_UNI_FLEE": 39, "P_RECALL_PCT": 51, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": ... | 91/406 | 2026-10-16 17:49:20 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 55 | 94032 | 5.3 | 41614bbc09 (+0.166, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_RECALL_NEAR": 9, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, ... | 36/139 | 2026-10-16 17:39:35 UTC |

Code: branch `claude/ga-farm-d37xlq@e2d1227`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

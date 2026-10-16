# GA farm board

Regenerated 2026-10-16 13:41:57 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 20 | 28808 | 7.5 | 2d44fc6f82 (+0.162, 2) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP"... | 23/49 | 2026-10-16 13:40:36 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 11 | 15352 | 4.1 | 5161205461 (+0.118, 1) | {"P_ENGAGE2": 62, "P_LOWHP": 57, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREE... | 14/29 | 2026-10-16 13:38:30 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 7 | 9498 | 6.1 | a3acc3dcf4 (+0.048, 1) | {"P_FLEE_PCT": 30, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_N": 2} | 8/16 | 2026-10-16 13:28:23 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 11 | 14958 | 6.6 | 9b62634fb7 (+0.089, 2) | {"P_GA_AVOID_HP": 54, "P_KITE_OUT": 1, "P_KITE": 0, "P_NOCHASE": 0, "P_CALLHELP": 1, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>AV... | 10/24 | 2026-10-16 13:39:34 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 7 | 9636 | 5.9 | a6e9c99bc3 (+0.116, 1) | {"P_KITE": 0, "P_FRONT_LOCAL": 0, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>AVOIDLOW>AVOID>FRONT>ENGAGE>WALKHOME>RECALLSHOP"} | 8/15 | 2026-10-16 13:23:04 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 13 | 17103 | 6.3 | c3edb55c4a (+0.070, 2) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_NN... | 15/33 | 2026-10-16 13:37:07 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 11 | 15454 | 7.5 | 19f3461842 (+0.135, 3) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 13/55 | 2026-10-16 13:31:13 UTC |
| micro | vm | micro | ga65a6 | 4 | 9 | 12412 | 6.5 | 11daa35986 (+0.056, 2) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_KILL_X": 6, "P_LOWHP": 49, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT_OUT": 174, "P_K... | 10/19 | 2026-10-16 13:09:44 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 50 | 66008 | 15.5 | af81463315 (+0.126, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_GA_OVERHEAD": 11, ... | 47/51 | 2026-10-16 13:41:55 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 16 | 23548 | 4.6 | 8abd827dcb (+0.080, 3) | {"P_UNI_FLEE": 43, "P_FRONT_OUT": 161, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE... | 14/38 | 2026-10-16 13:37:46 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

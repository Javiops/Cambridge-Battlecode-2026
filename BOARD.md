# GA farm board

Regenerated 2026-10-16 13:57:57 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 24 | 35660 | 7.5 | 4f97657e5f (+0.130, 6) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0, "P_R_AVOIDLOW... | 23/60 | 2026-10-16 13:57:52 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 14 | 20084 | 4.2 | 49f4345f2a (+0.154, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 19/36 | 2026-10-16 13:57:24 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 8 | 10844 | 5.6 | a3acc3dcf4 (+0.058, 2) | {"P_FLEE_PCT": 30, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_N": 2} | 9/19 | 2026-10-16 13:40:40 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 14 | 20330 | 6.1 | d20281a41e (+0.121, 3) | {"P_AVOID_DIST": 3, "P_ENGAGE2": 83, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_DANGER_T": 37, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 13/31 | 2026-10-16 13:54:23 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 10 | 14450 | 5.9 | 806a4297ec (+0.093, 2) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 11/22 | 2026-10-16 13:55:35 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 16 | 22457 | 5.2 | 6335759bfa (+0.151, 3) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 17/39 | 2026-10-16 13:53:39 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 12 | 17312 | 7.4 | 52f03c349e (+0.105, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order": "FLEE>NEARRECALL>... | 15/60 | 2026-10-16 13:55:32 UTC |
| micro | vm | micro | ga65a6 | 4 | 13 | 19218 | 6.5 | 3828b4b7bb (+0.051, 2) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_FAV": 92, "P_GA_KILL_X": 6, "P_LOWHP": 53, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT... | 14/28 | 2026-10-16 13:57:32 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 58 | 78468 | 15.7 | dd2665b278 (+0.087, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL":... | 53/73 | 2026-10-16 13:56:04 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 17 | 25254 | 5.8 | 552562f454 (+0.089, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/41 | 2026-10-16 13:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

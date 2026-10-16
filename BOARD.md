# GA farm board

Regenerated 2026-10-16 13:54:16 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 23 | 34016 | 7.8 | 49f4345f2a (+0.148, 4) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 23/58 | 2026-10-16 13:54:08 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 13 | 18526 | 4.8 | e2da166eb6 (+0.182, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 17/33 | 2026-10-16 13:51:15 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 8 | 10844 | 5.6 | a3acc3dcf4 (+0.058, 2) | {"P_FLEE_PCT": 30, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_N": 2} | 9/19 | 2026-10-16 13:40:40 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 13 | 18482 | 6.1 | d20281a41e (+0.165, 2) | {"P_AVOID_DIST": 3, "P_ENGAGE2": 83, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_DANGER_T": 37, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 13/29 | 2026-10-16 13:49:20 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 9 | 12720 | 6.1 | 806a4297ec (+0.075, 1) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 10/19 | 2026-10-16 13:50:43 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 16 | 22457 | 5.2 | 6335759bfa (+0.151, 3) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 17/39 | 2026-10-16 13:53:39 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 11 | 15454 | 7.5 | 19f3461842 (+0.135, 3) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 13/55 | 2026-10-16 13:31:13 UTC |
| micro | vm | micro | ga65a6 | 4 | 12 | 17380 | 6.1 | 3828b4b7bb (+0.058, 1) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_FAV": 92, "P_GA_KILL_X": 6, "P_LOWHP": 53, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT... | 13/25 | 2026-10-16 13:52:47 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 57 | 76808 | 16.1 | c1785edb2f (+0.097, 7) | {"P_GA_AVOID_HP": 59, "P_GA_KITE_HP": 94, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72... | 52/71 | 2026-10-16 13:54:14 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 17 | 25254 | 5.8 | 552562f454 (+0.089, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/41 | 2026-10-16 13:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

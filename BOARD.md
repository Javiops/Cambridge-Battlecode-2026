# GA farm board

Regenerated 2026-10-16 14:03:54 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 25 | 37348 | 6.5 | f769c046e8 (+0.172, 1) | {"P_FLEE_PCT": 24, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order":... | 23/63 | 2026-10-16 14:02:20 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 14 | 20084 | 4.2 | 49f4345f2a (+0.154, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 19/36 | 2026-10-16 13:57:24 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 8 | 10844 | 5.6 | a3acc3dcf4 (+0.058, 2) | {"P_FLEE_PCT": 30, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_N": 2} | 9/19 | 2026-10-16 13:40:40 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 15 | 22050 | 6.5 | d20281a41e (+0.092, 4) | {"P_AVOID_DIST": 3, "P_ENGAGE2": 83, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_DANGER_T": 37, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 13/34 | 2026-10-16 13:58:48 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 11 | 16120 | 6.3 | 806a4297ec (+0.073, 3) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 12/24 | 2026-10-16 14:00:00 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 17 | 24251 | 6.9 | 6335759bfa (+0.119, 4) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 19/42 | 2026-10-16 13:57:59 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 13 | 19026 | 5.6 | 2d44fc6f82 (+0.095, 1) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP"... | 16/64 | 2026-10-16 14:00:41 UTC |
| micro | vm | micro | ga65a6 | 4 | 13 | 19218 | 6.5 | 3828b4b7bb (+0.051, 2) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_FAV": 92, "P_GA_KILL_X": 6, "P_LOWHP": 53, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT... | 14/28 | 2026-10-16 13:57:32 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 62 | 85298 | 17.2 | 94bd2723b9 (+0.186, 4) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 58/84 | 2026-10-16 14:03:52 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 17 | 25254 | 5.8 | 552562f454 (+0.089, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/41 | 2026-10-16 13:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

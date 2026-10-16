# GA farm board

Regenerated 2026-10-16 13:50:24 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 22 | 32298 | 6.2 | 49f4345f2a (+0.149, 3) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 23/54 | 2026-10-16 13:50:21 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 12 | 16922 | 3.6 | 5161205461 (+0.112, 2) | {"P_ENGAGE2": 62, "P_LOWHP": 57, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREE... | 16/31 | 2026-10-16 13:45:43 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 8 | 10844 | 5.6 | a3acc3dcf4 (+0.058, 2) | {"P_FLEE_PCT": 30, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_N": 2} | 9/19 | 2026-10-16 13:40:40 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 13 | 18482 | 6.1 | d20281a41e (+0.165, 2) | {"P_AVOID_DIST": 3, "P_ENGAGE2": 83, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_DANGER_T": 37, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 13/29 | 2026-10-16 13:49:20 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 8 | 11198 | 4.6 | aae1734f50 (+0.077, 3) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 10/17 | 2026-10-16 13:46:31 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 15 | 20631 | 5.0 | 6335759bfa (+0.122, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_HALF_D": 7, "P_TELE": 5, "order":... | 17/37 | 2026-10-16 13:47:43 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 11 | 15454 | 7.5 | 19f3461842 (+0.135, 3) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 13/55 | 2026-10-16 13:31:13 UTC |
| micro | vm | micro | ga65a6 | 4 | 11 | 15650 | 5.2 | 7812664bac (+0.093, 1) | {"P_ENGAGE2": 69, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HOLD_R": 7, "P_TELE... | 12/23 | 2026-10-16 13:48:01 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 54 | 72238 | 15.6 | 2d3e1aecc5 (+0.091, 2) | {"P_FRONT_ZONE": 5, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HOLD_R": 7, "P_TE... | 52/61 | 2026-10-16 13:48:43 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 17 | 25254 | 5.8 | 552562f454 (+0.089, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/41 | 2026-10-16 13:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

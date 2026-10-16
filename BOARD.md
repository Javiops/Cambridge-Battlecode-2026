# GA farm board

Regenerated 2026-10-16 13:15:15 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 14 | 18460 | 7.6 | 56fb791b22 (+0.033, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0, "P_NN_ON": 1,... | 15/34 | 2026-10-16 13:14:57 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 7 | 9214 | 5.2 | 70d8dab816 (+0.049, 4) | {"P_BAIL_PCT": 6, "P_ENGAGE2": 59, "P_GA_FAV": 84, "P_FRONT_OUT": 161, "P_KITE_OUT": 3, "P_GA_KITE_HP": 102, "P_DANGER_T": 43, "P_DANGER_R": 4, "P_DANGER": 3} | 7/20 | 2026-10-16 13:13:22 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 6 | 8088 | 6.1 | 90b9fb2146 (+0.068, 1) | {"P_FLEE_PCT": 35, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_ENGAGE": 1} | 7/14 | 2026-10-16 13:09:53 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 4 | 5276 | 6.2 | 376912874c (+0.042, 1) | {"P_GA_AVOID_HP": 54, "P_LOWHP": 48, "P_KITE_OUT": 1, "P_VOLLEY": 32, "P_CHASE_GEMS": 155, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_ALLYDUTY": 1, ... | 4/8 | 2026-10-16 12:45:38 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 5 | 6666 | 5.8 | bf48dc1184 (+0.041, 4) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME"} | 4/10 | 2026-10-16 13:00:03 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 10 | 12235 | 5.5 | 0227a5bb94 (+0.033, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_GP0_ON": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P... | 12/25 | 2026-10-16 13:13:38 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 8 | 10680 | 5.6 | 9b92558015 (+0.112, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_GA_GOLD_ROUND": 510, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR... | 11/38 | 2026-10-16 13:08:46 UTC |
| micro | vm | micro | ga65a6 | 4 | 9 | 12412 | 6.5 | 11daa35986 (+0.056, 2) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_KILL_X": 6, "P_LOWHP": 49, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT_OUT": 174, "P_K... | 10/19 | 2026-10-16 13:09:44 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 36 | 42106 | 16.1 | 9d4d06f48a (+0.111, 1) | {"P_CHASE_GEMS": 118, "P_DANGER_T": 31, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_TWIN": 1, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HOLD_... | 34/11 | 2026-10-16 13:15:14 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 12 | 16708 | 5.2 | 5c0ccda8ef (+0.041, 8) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "orde... | 10/26 | 2026-10-16 13:08:23 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

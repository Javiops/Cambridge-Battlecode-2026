# GA farm board

Regenerated 2026-10-16 13:22:54 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 16 | 21884 | 7.4 | 4f97657e5f (+0.075, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0, "P_R_AVOIDLOW... | 17/40 | 2026-10-16 13:22:49 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 8 | 10558 | 3.9 | 26ace046f1 (+0.047, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "nn": "0 hidden, 2 links, ... | 8/22 | 2026-10-16 13:19:29 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 6 | 8088 | 6.1 | 90b9fb2146 (+0.068, 1) | {"P_FLEE_PCT": 35, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_ENGAGE": 1} | 7/14 | 2026-10-16 13:09:53 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 6 | 7052 | 6.7 | a6e9c99bc3 (+0.061, 4) | {"P_KITE": 0, "P_FRONT_LOCAL": 0, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>AVOIDLOW>AVOID>FRONT>ENGAGE>WALKHOME>RECALLSHOP"} | 7/13 | 2026-10-16 13:19:59 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 6 | 8058 | 5.3 | aae1734f50 (+0.072, 1) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 6/13 | 2026-10-16 13:18:36 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 10 | 12235 | 5.5 | 0227a5bb94 (+0.033, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_GP0_ON": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P... | 12/25 | 2026-10-16 13:13:38 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 10 | 13724 | 8.4 | dc28fb84ca (+0.097, 4) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order": "FLEE>NEARRECALL>... | 13/51 | 2026-10-16 13:21:14 UTC |
| micro | vm | micro | ga65a6 | 4 | 9 | 12412 | 6.5 | 11daa35986 (+0.056, 2) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_KILL_X": 6, "P_LOWHP": 49, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT_OUT": 174, "P_K... | 10/19 | 2026-10-16 13:09:44 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 40 | 48432 | 15.7 | ceae84d4a3 (+0.148, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_GOLD_W_EARLY": 23, "P_SHAREEXP": 72, "... | 36/22 | 2026-10-16 13:22:21 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 14 | 20122 | 3.8 | cb699afaab (+0.074, 2) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "orde... | 11/34 | 2026-10-16 13:22:29 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

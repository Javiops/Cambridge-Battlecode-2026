# GA farm board

Regenerated 2026-10-16 13:30:19 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 17 | 23546 | 7.3 | 2d44fc6f82 (+0.101, 1) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP"... | 18/42 | 2026-10-16 13:26:44 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 9 | 12198 | 4.0 | 8a8b0af8ec (+0.135, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HOLD_R": 7, "P_TELE": 5, "order": "F... | 11/25 | 2026-10-16 13:26:24 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 6 | 8088 | 6.1 | 90b9fb2146 (+0.068, 1) | {"P_FLEE_PCT": 35, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_ENGAGE": 1} | 7/14 | 2026-10-16 13:09:53 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 7 | 8462 | 7.7 | 63a7f6cba3 (+0.068, 4) | {"P_GA_AVOID_HP": 54, "P_LOWHP": 48, "P_KITE_OUT": 1, "P_VOLLEY": 32, "P_CHASE_GEMS": 155, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_ALLYDUTY": 1, ... | 7/15 | 2026-10-16 13:23:04 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 7 | 9636 | 5.9 | a6e9c99bc3 (+0.116, 1) | {"P_KITE": 0, "P_FRONT_LOCAL": 0, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>AVOIDLOW>AVOID>FRONT>ENGAGE>WALKHOME>RECALLSHOP"} | 8/15 | 2026-10-16 13:23:04 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 10 | 12235 | 5.5 | 0227a5bb94 (+0.033, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_GP0_ON": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P... | 12/25 | 2026-10-16 13:13:38 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 10 | 13724 | 8.4 | dc28fb84ca (+0.097, 4) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order": "FLEE>NEARRECALL>... | 13/51 | 2026-10-16 13:21:14 UTC |
| micro | vm | micro | ga65a6 | 4 | 9 | 12412 | 6.5 | 11daa35986 (+0.056, 2) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_KILL_X": 6, "P_LOWHP": 49, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT_OUT": 174, "P_K... | 10/19 | 2026-10-16 13:09:44 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 44 | 55384 | 14.8 | 47b0e8f6c3 (+0.113, 1) | {"P_GA_AVOID_HP": 58, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 39/34 | 2026-10-16 13:30:18 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 14 | 20122 | 3.8 | cb699afaab (+0.074, 2) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "orde... | 11/34 | 2026-10-16 13:22:29 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

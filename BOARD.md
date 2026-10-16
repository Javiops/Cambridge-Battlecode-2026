# GA farm board

Regenerated 2026-10-16 14:54:09 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 32 | 48936 | 3.3 | fe2c58c27b (+0.136, 5) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, ... | 27/79 | 2026-10-16 14:43:51 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 21 | 30068 | 4.7 | dd2665b278 (+0.113, 5) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL":... | 24/51 | 2026-10-16 14:40:14 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 18 | 23946 | 5.0 | 58a307fdb6 (+0.178, 1) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_R34_BANKCOST": 184, "P_TRIBUTE_NEAR":... | 19/43 | 2026-10-16 14:42:51 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 24 | 36990 | 5.4 | a98df63b30 (+0.061, 1) | {"P_AVOID_DIST": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_NN... | 14/56 | 2026-10-16 14:43:19 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 18 | 27286 | 6.5 | 77927f0dcd (+0.116, 2) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 14/40 | 2026-10-16 14:41:50 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 24 | 35225 | 5.5 | 94524497e5 (+0.106, 3) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, ... | 23/62 | 2026-10-16 14:42:31 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 24 | 36741 | 7.8 | a905ba706f (+0.097, 3) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 27/127 | 2026-10-16 14:43:40 UTC |
| micro | vm | micro | ga65a6 | 4 | 21 | 33240 | 5.8 | 7812664bac (+0.032, 7) | {"P_ENGAGE2": 69, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HOLD_R": 7, "P_TELE... | 22/44 | 2026-10-16 14:39:25 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 90 | 130275 | 17.6 | 143621b7b3 (+0.152, 1) | {"P_UNI_FLEE": 43, "P_BAIL_PCT": 13, "P_GA_KITE_HP": 115, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1... | 64/181 | 2026-10-16 14:54:08 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 24 | 37212 | 5.3 | 7057988e75 (+0.160, 3) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 23/55 | 2026-10-16 14:42:56 UTC |

Code: branch `claude/ga-farm-d37xlq@6b9e4c7`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

# GA farm board

Regenerated 2026-10-16 14:38:28 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 31 | 47308 | 3.1 | 38f5633b35 (+0.134, 4) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 27/77 | 2026-10-16 14:35:29 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 20 | 28274 | 5.1 | 9dac1d5d56 (+0.124, 2) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 24/49 | 2026-10-16 14:33:49 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 16 | 20914 | 4.9 | 19f3461842 (+0.164, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/37 | 2026-10-16 14:33:25 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 22 | 33358 | 7.5 | dd2665b278 (+0.069, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL":... | 14/50 | 2026-10-16 14:32:55 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 16 | 23836 | 6.8 | fe2c58c27b (+0.115, 1) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, ... | 14/35 | 2026-10-16 14:31:55 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 22 | 31745 | 6.6 | fbf1e4f552 (+0.077, 1) | {"P_BAIL_PCT": 13, "P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_FRONT": 0, "P_SAFESTEP": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_N... | 22/57 | 2026-10-16 14:32:34 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 21 | 31787 | 8.3 | fcdb3b057a (+0.109, 2) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_GA_DOOR": 58, "P_TELE": 5, "order": ... | 26/113 | 2026-10-16 14:32:01 UTC |
| micro | vm | micro | ga65a6 | 4 | 20 | 31496 | 7.2 | 983a63d165 (+0.050, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 0, "P_FRONT_OUT": 171, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECAL... | 20/42 | 2026-10-16 14:34:22 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 81 | 115935 | 17.3 | cfeb263573 (+0.154, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL":... | 61/149 | 2026-10-16 14:38:26 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 22 | 33824 | 5.6 | 7057988e75 (+0.212, 2) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 22/51 | 2026-10-16 14:32:42 UTC |

Code: branch `claude/ga-farm-d37xlq@6b9e4c7`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

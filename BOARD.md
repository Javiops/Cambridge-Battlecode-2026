# GA farm board

Regenerated 2026-10-16 15:36:57 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 29 | 43804 | 4.3 | bfa257ae73 (+0.148, 5) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 27/75 | 2026-10-16 15:34:27 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 29 | 43142 | 6.9 | b670db8fae (+0.105, 2) | {"P_FLEE_PCT": 30, "P_BAIL_PCT": 25, "P_AVOID_DIST": 9, "P_ENGAGE2": 62, "P_FRONT_ZONE": 2, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 20, "P_CHASE_GEMS"... | 23/73 | 2026-10-16 15:34:59 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 34 | 53988 | 5.6 | 9bc5193917 (+0.150, 3) | {"P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 21/88 | 2026-10-16 15:35:50 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 28 | 44760 | 7.1 | e4eae6a7a8 (+0.103, 3) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 18/68 | 2026-10-16 15:35:57 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 33 | 50861 | 6.1 | e07012c3b0 (+0.169, 1) | {"P_BAIL_PCT": 13, "P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_A... | 30/90 | 2026-10-16 15:33:51 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 37 | 59001 | 7.0 | 7530068f4c (+0.186, 4) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 34/223 | 2026-10-16 15:35:10 UTC |
| micro | vm | micro | ga65a6 | 4 | 32 | 52224 | 6.6 | 2076715ed7 (+0.101, 2) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 34/78 | 2026-10-16 15:33:59 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 111 | 166387 | 15.5 | 15c8d1ac89 (+0.120, 6) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 74/242 | 2026-10-16 15:35:43 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 35 | 56156 | 6.2 | 49cb7f807e (+0.167, 2) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_NOCHASE": 0, "... | 28/87 | 2026-10-16 15:36:24 UTC |

Code: branch `claude/ga-farm-d37xlq@a6bc6ab`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

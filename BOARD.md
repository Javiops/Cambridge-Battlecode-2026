# GA farm board

Regenerated 2026-10-16 16:17:48 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 7 | 10846 | 7.0 | 426517d710 (+0.069, 2) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_NOCHASE": 0, "... | 5/15 | 2026-10-16 16:15:27 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 34 | 53326 | 5.5 | d6df17a265 (+0.162, 1) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 99, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 28/86 | 2026-10-16 16:11:52 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 36 | 56020 | 5.7 | 5f7d1fa11b (+0.142, 5) | {"P_GA_AVOID_HP": 36, "P_GA_KITE_HP": 84, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1... | 28/94 | 2026-10-16 16:14:18 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 41 | 66946 | 5.7 | 0f5b108ea6 (+0.105, 3) | {"P_UNI_FLEE": 39, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_... | 25/107 | 2026-10-16 16:12:18 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 33 | 53542 | 3.4 | 38d9b3078d (+0.149, 8) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 20/83 | 2026-10-16 16:05:07 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 39 | 61715 | 5.9 | 1c6ffc6db0 (+0.108, 6) | {"P_BAIL_PCT": 13, "P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_FRONT": 0, "P_SAFESTEP": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_N... | 32/105 | 2026-10-16 16:08:14 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 43 | 69391 | 5.3 | b5ff18510e (+0.166, 10) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 37/268 | 2026-10-16 16:12:04 UTC |
| micro | vm | micro | ga65a6 | 4 | 40 | 65600 | 6.6 | 314e9672aa (+0.097, 3) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_CHASE_GEMS": 126, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW":... | 40/103 | 2026-10-16 16:14:43 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 130 | 202167 | 15.7 | 137994c5d9 (+0.118, 15) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 80/336 | 2026-10-16 16:17:47 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 40 | 64902 | 4.0 | 9bdc9183de (+0.140, 2) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 31/102 | 2026-10-16 16:11:11 UTC |

Code: branch `claude/ga-farm-d37xlq@cae2273`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

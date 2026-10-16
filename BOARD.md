# GA farm board

Regenerated 2026-10-16 16:11:29 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 6 | 9058 | 7.6 | 426517d710 (+0.090, 1) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_NOCHASE": 0, "... | 4/13 | 2026-10-16 16:11:05 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 33 | 51232 | 3.3 | 858c305f08 (+0.116, 4) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 192, "P_DANGER_T": 67, "P_DANGER_R": 8, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHA... | 28/83 | 2026-10-16 16:05:27 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 35 | 53998 | 4.7 | 5f7d1fa11b (+0.160, 4) | {"P_GA_AVOID_HP": 36, "P_GA_KITE_HP": 84, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1... | 28/91 | 2026-10-16 16:08:23 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 40 | 65062 | 7.5 | e7ba90eac2 (+0.085, 1) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLO... | 24/102 | 2026-10-16 16:06:46 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 33 | 53542 | 3.4 | 38d9b3078d (+0.149, 8) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 20/83 | 2026-10-16 16:05:07 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 39 | 61715 | 5.9 | 1c6ffc6db0 (+0.108, 6) | {"P_BAIL_PCT": 13, "P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_FRONT": 0, "P_SAFESTEP": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_N... | 32/105 | 2026-10-16 16:08:14 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 42 | 67661 | 3.1 | b5ff18510e (+0.171, 9) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 37/251 | 2026-10-16 16:06:33 UTC |
| micro | vm | micro | ga65a6 | 4 | 39 | 63966 | 6.0 | 314e9672aa (+0.108, 2) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_CHASE_GEMS": 126, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW":... | 40/99 | 2026-10-16 16:10:34 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 127 | 196189 | 12.8 | 137994c5d9 (+0.122, 12) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 79/323 | 2026-10-16 16:11:27 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 39 | 62934 | 4.0 | c1d63b6631 (+0.143, 5) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP1_ON": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "o... | 31/99 | 2026-10-16 16:00:58 UTC |

Code: branch `claude/ga-farm-d37xlq@4fa99e8`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

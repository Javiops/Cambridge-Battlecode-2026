# GA farm board

Regenerated 2026-10-16 14:59:43 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 33 | 50754 | 2.9 | fe2c58c27b (+0.133, 6) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_KITE_OUT": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 146, "P_FRONT": 0, "P_SAFESTEP": 0, ... | 27/86 | 2026-10-16 14:54:26 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 23 | 33410 | 4.2 | 7aee2622fc (+0.143, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 25/61 | 2026-10-16 14:53:07 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 20 | 27406 | 5.7 | 18a189c199 (+0.127, 1) | {"P_RECALL_NEAR": 9, "P_GA_AVOID_HP": 59, "P_ENGAGE2": 62, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE":... | 19/47 | 2026-10-16 14:52:21 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 26 | 40348 | 4.9 | a8b00ea2c8 (+0.073, 2) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SH... | 16/65 | 2026-10-16 14:54:18 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 20 | 30674 | 4.6 | 73285bd2e0 (+0.133, 1) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 15/50 | 2026-10-16 14:54:17 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 26 | 38767 | 6.6 | 3e59888b85 (+0.088, 4) | {"P_DANGER_T": 47, "P_FRONT": 0, "P_SAFESTEP": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_TELE": 5, "order": "FLEE>N... | 24/71 | 2026-10-16 14:53:08 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 27 | 41687 | 7.7 | 01d085456c (+0.089, 3) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOI... | 28/144 | 2026-10-16 14:54:04 UTC |
| micro | vm | micro | ga65a6 | 4 | 23 | 36710 | 5.6 | 2426959181 (+0.029, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 25/53 | 2026-10-16 14:49:25 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 93 | 135199 | 14.2 | 48224301b2 (+0.112, 7) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 64/192 | 2026-10-16 14:59:41 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 25 | 38882 | 5.0 | 6ca1f870ef (+0.188, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 23/58 | 2026-10-16 14:48:33 UTC |

Code: branch `claude/ga-farm-d37xlq@6b9e4c7`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

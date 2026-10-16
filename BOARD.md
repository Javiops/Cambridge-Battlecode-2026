# GA farm board

Regenerated 2026-10-16 14:30:43 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 30 | 45610 | 4.5 | 38f5633b35 (+0.160, 3) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 27/75 | 2026-10-16 14:26:12 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 18 | 25222 | 5.0 | dd2665b278 (+0.185, 2) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_KITE_OUT": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL":... | 22/45 | 2026-10-16 14:22:21 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 14 | 18110 | 6.7 | 2e65494694 (+0.122, 4) | {"P_FLEE_PCT": 30, "P_BAIL_PCT": 25, "P_FRONT_ZONE": 2, "P_VOLLEY": 20, "P_CHASE_GEMS": 94, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_... | 15/33 | 2026-10-16 14:24:41 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 20 | 29896 | 5.4 | 36982c3986 (+0.128, 4) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HOLD_R": 7, "P_TELE": 5, "order": "F... | 14/46 | 2026-10-16 14:24:06 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 14 | 21362 | 6.9 | aae1734f50 (+0.070, 6) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME", "... | 13/31 | 2026-10-16 14:14:53 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 21 | 31129 | 7.1 | 92f48e03f5 (+0.076, 8) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_NN... | 22/55 | 2026-10-16 14:16:20 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 19 | 28369 | 7.9 | 0440f4d00e (+0.157, 3) | {"P_VOLLEY": 35, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 7, "order": "... | 24/101 | 2026-10-16 14:24:53 UTC |
| micro | vm | micro | ga65a6 | 4 | 18 | 28004 | 5.6 | 4f97657e5f (+0.037, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0, "P_R_AVOIDLOW... | 17/38 | 2026-10-16 14:25:16 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 77 | 109345 | 16.6 | 94bd2723b9 (+0.140, 19) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 60/139 | 2026-10-16 14:30:41 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 20 | 30428 | 6.9 | feaad2b76b (+0.100, 2) | {"P_UNI_FLEE": 43, "P_FRONT_OUT": 161, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0,... | 20/47 | 2026-10-16 14:22:27 UTC |

Code: branch `claude/ga-farm-d37xlq@a667ff7`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

# GA farm board

Regenerated 2026-10-16 15:27:42 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 36 | 55894 | 3.7 | 3b80fd2bd1 (+0.139, 3) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 29/93 | 2026-10-16 15:26:00 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 27 | 40186 | 4.6 | 5f9da0c758 (+0.184, 3) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 27/70 | 2026-10-16 15:18:25 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 26 | 37870 | 6.3 | 19f3461842 (+0.121, 7) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 23/60 | 2026-10-16 15:21:08 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 31 | 48752 | 4.2 | 7aee2622fc (+0.135, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 19/76 | 2026-10-16 15:20:40 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 25 | 39460 | 5.3 | 52fec11234 (+0.162, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 17/62 | 2026-10-16 15:21:04 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 31 | 47435 | 5.5 | e6bf3e0da7 (+0.169, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 29/83 | 2026-10-16 15:24:41 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 34 | 53767 | 7.5 | 6f9cb00aff (+0.153, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 31/183 | 2026-10-16 15:22:01 UTC |
| micro | vm | micro | ga65a6 | 4 | 30 | 48748 | 6.4 | 5f9da0c758 (+0.078, 1) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 32/71 | 2026-10-16 15:24:14 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 107 | 159267 | 15.7 | 15c8d1ac89 (+0.183, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 74/229 | 2026-10-16 15:27:41 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 32 | 50868 | 5.9 | 7057988e75 (+0.178, 9) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 26/79 | 2026-10-16 15:21:30 UTC |

Code: branch `claude/ga-farm-d37xlq@ef19483`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

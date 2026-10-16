# GA farm board

Regenerated 2026-10-16 15:45:47 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 1 | 1296 | 2.9 | 8161284fa4 (+0.151, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "or... | 0/2 | 2026-10-16 15:45:39 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 30 | 45534 | 5.0 | 5f694cc3a3 (+0.131, 1) | {"P_UNI_FLEE": 51, "P_GA_AVOID_HP": 74, "P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1... | 27/77 | 2026-10-16 15:40:16 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 31 | 46692 | 5.8 | 58001aa0fb (+0.132, 1) | {"P_RECALL_NEAR": 9, "P_ENGAGE2": 62, "P_GA_FAV": 69, "P_KITE_ZONE": 3, "P_VOLLEY": 20, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "... | 24/77 | 2026-10-16 15:44:12 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 36 | 57512 | 7.2 | f6edbdb6a9 (+0.126, 2) | {"P_BAIL_PCT": 13, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 21/92 | 2026-10-16 15:45:12 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 29 | 46438 | 5.8 | e4eae6a7a8 (+0.115, 4) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 19/72 | 2026-10-16 15:40:46 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 35 | 54085 | 6.7 | dafef84c39 (+0.189, 1) | {"P_FLEE_PCT": 27, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "... | 31/94 | 2026-10-16 15:42:10 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 39 | 62441 | 8.3 | 7530068f4c (+0.152, 6) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 35/235 | 2026-10-16 15:42:26 UTC |
| micro | vm | micro | ga65a6 | 4 | 34 | 55552 | 7.1 | 5f9da0c758 (+0.109, 5) | {"P_VOLLEY": 40, "P_CHASE_GEMS": 157, "P_DANGER_T": 51, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_HO... | 35/87 | 2026-10-16 15:42:15 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 115 | 173417 | 15.2 | 78bc644efc (+0.246, 3) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 77/274 | 2026-10-16 15:43:50 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 36 | 58014 | 6.5 | fd444ac101 (+0.156, 13) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 28/90 | 2026-10-16 15:41:09 UTC |

Code: branch `claude/ga-farm-d37xlq@a6bc6ab`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

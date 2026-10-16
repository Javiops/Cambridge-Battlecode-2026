# GA farm board

Regenerated 2026-10-16 13:45:42 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 21 | 30588 | 6.0 | 49f4345f2a (+0.140, 2) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_LOWHP": 57, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0... | 23/51 | 2026-10-16 13:45:38 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 11 | 15352 | 4.1 | 5161205461 (+0.118, 1) | {"P_ENGAGE2": 62, "P_LOWHP": 57, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREE... | 14/29 | 2026-10-16 13:38:30 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 8 | 10844 | 5.6 | a3acc3dcf4 (+0.058, 2) | {"P_FLEE_PCT": 30, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_N": 2} | 9/19 | 2026-10-16 13:40:40 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 12 | 16752 | 6.0 | d20281a41e (+0.195, 1) | {"P_AVOID_DIST": 3, "P_ENGAGE2": 83, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_DANGER_T": 37, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY":... | 11/26 | 2026-10-16 13:44:33 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 7 | 9636 | 5.9 | a6e9c99bc3 (+0.116, 1) | {"P_KITE": 0, "P_FRONT_LOCAL": 0, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>AVOIDLOW>AVOID>FRONT>ENGAGE>WALKHOME>RECALLSHOP"} | 8/15 | 2026-10-16 13:23:04 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 14 | 18897 | 6.2 | 1bcf0facd6 (+0.083, 3) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "P_NN... | 16/35 | 2026-10-16 13:41:57 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 11 | 15454 | 7.5 | 19f3461842 (+0.135, 3) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 13/55 | 2026-10-16 13:31:13 UTC |
| micro | vm | micro | ga65a6 | 4 | 10 | 14102 | 5.4 | 11daa35986 (+0.046, 3) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_KILL_X": 6, "P_LOWHP": 49, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT_OUT": 174, "P_K... | 11/21 | 2026-10-16 13:43:03 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 52 | 69124 | 16.3 | 8e8a1f7aea (+0.188, 1) | {"P_BAIL_PCT": 13, "P_AVOID_DIST": 3, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_NEARRECALL": 0, "P_R_AVOIDLOW... | 49/55 | 2026-10-16 13:45:15 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 17 | 25254 | 5.8 | 552562f454 (+0.089, 2) | {"P_GA_AVOID_HP": 59, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, ... | 16/41 | 2026-10-16 13:42:39 UTC |

Code: branch `claude/ga-farm-d37xlq@d84d598`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

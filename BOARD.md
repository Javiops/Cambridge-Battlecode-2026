# GA farm board

Regenerated 2026-10-16 13:05:57 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 12 | 15918 | 7.7 | ec6f7d3d1c (+0.066, 2) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TELE": 5, "orde... | 14/27 | 2026-10-16 13:05:54 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 5 | 6544 | 5.7 | 89127a46dd (+0.064, 2) | {"P_BAIL_PCT": 6, "P_ENGAGE2": 59, "P_GA_FAV": 84, "P_FRONT_OUT": 161, "P_KITE_OUT": 3, "P_GA_KITE_HP": 102, "P_DANGER_T": 43, "P_DANGER_R": 4, "P_DANGER": 3} | 6/10 | 2026-10-16 13:03:13 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 4 | 5286 | 5.2 | 456c9eb6e6 (+0.041, 1) | {"P_FLEE_PCT": 35, "P_GA_KITE_HP": 146, "P_VOLLEY": 20} | 4/8 | 2026-10-16 12:58:19 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 4 | 5276 | 6.2 | 376912874c (+0.042, 1) | {"P_GA_AVOID_HP": 54, "P_LOWHP": 48, "P_KITE_OUT": 1, "P_VOLLEY": 32, "P_CHASE_GEMS": 155, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_ALLYDUTY": 1, ... | 4/8 | 2026-10-16 12:45:38 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 5 | 6666 | 5.8 | bf48dc1184 (+0.041, 4) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME"} | 4/10 | 2026-10-16 13:00:03 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 8 | 9363 | 6.4 | 5c0ccda8ef (+0.045, 4) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "orde... | 9/16 | 2026-10-16 13:05:09 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 7 | 9102 | 7.3 | ec6f7d3d1c (+0.075, 1) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TELE": 5, "orde... | 9/34 | 2026-10-16 13:04:01 UTC |
| micro | vm | micro | ga65a6 | 4 | 8 | 10834 | 6.2 | 11daa35986 (+0.063, 1) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_KILL_X": 6, "P_LOWHP": 49, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT_OUT": 174, "P_K... | 9/17 | 2026-10-16 13:05:41 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 33 | 37878 | 16.8 | c6a236c4d4 (+0.053, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_HITFIRST": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order": ... | 32/0 | 2026-10-16 13:00:22 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 11 | 14934 | 4.5 | 5c0ccda8ef (+0.056, 7) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "orde... | 9/24 | 2026-10-16 13:02:44 UTC |

Code: branch `claude/ga-farm-d37xlq@5132c9d`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

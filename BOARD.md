# GA farm board

Regenerated 2026-10-16 13:10:17 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 13 | 17552 | 6.4 | e7275444e7 (+0.044, 3) | {"P_GA_AVOID_HP": 73, "P_DANGER_R": 4, "P_FRONT": 0, "P_R_AVOIDLOW": 0, "P_GP0_ON": 1, "gp0": "((not FAV and not (KILL or (RATIO > 147))) and (((HP < 60) or ... | 15/30 | 2026-10-16 13:10:13 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 6 | 7936 | 4.7 | d9c8223031 (+0.058, 2) | {"P_RECALL_PCT": 47, "P_RECALL_NEAR": 9, "P_ENGAGE2": 95, "P_GA_SPAWN_HEAL": 90, "P_KITE_ZONE": 5, "P_KITE_OUT": 1, "P_GA_KITE_HP": 129, "P_VOLLEY": 51, "P_C... | 7/13 | 2026-10-16 13:09:12 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 6 | 8088 | 6.1 | 90b9fb2146 (+0.068, 1) | {"P_FLEE_PCT": 35, "P_GA_AVOID_HP": 81, "P_FRONT_OUT": 142, "P_GA_KITE_HP": 146, "P_VOLLEY": 20, "P_GA_SS_ALLY": 6, "P_PAIR_ENGAGE": 1} | 7/14 | 2026-10-16 13:09:53 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 4 | 5276 | 6.2 | 376912874c (+0.042, 1) | {"P_GA_AVOID_HP": 54, "P_LOWHP": 48, "P_KITE_OUT": 1, "P_VOLLEY": 32, "P_CHASE_GEMS": 155, "P_SAFESTEP": 0, "P_RETREAT": 1, "P_NOCHASE": 0, "P_ALLYDUTY": 1, ... | 4/8 | 2026-10-16 12:45:38 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 5 | 6666 | 5.8 | bf48dc1184 (+0.041, 4) | {"P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "order": "FLEE>NEARRECALL>FM>KITE>FRONT>AVOIDLOW>ENGAGE>AVOID>RECALLSHOP>WALKHOME"} | 4/10 | 2026-10-16 13:00:03 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 9 | 10725 | 5.9 | 6cfff14837 (+0.043, 1) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVO... | 10/19 | 2026-10-16 13:09:01 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 8 | 10680 | 5.6 | 9b92558015 (+0.112, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_GA_GOLD_ROUND": 510, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR... | 11/38 | 2026-10-16 13:08:46 UTC |
| micro | vm | micro | ga65a6 | 4 | 9 | 12412 | 6.5 | 11daa35986 (+0.056, 2) | {"P_RECALL_PCT": 44, "P_RECALL_NEAR": 9, "P_ENGAGE2": 50, "P_GA_KILL_X": 6, "P_LOWHP": 49, "P_GA_SPAWN_HEAL": 85, "P_FRONT_ZONE": 4, "P_FRONT_OUT": 174, "P_K... | 10/19 | 2026-10-16 13:09:44 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 33 | 37878 | 16.8 | c6a236c4d4 (+0.053, 1) | {"P_CHASE_GEMS": 118, "P_FRONT": 0, "P_HITFIRST": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TELE": 5, "order": ... | 32/0 | 2026-10-16 13:00:22 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 12 | 16708 | 5.2 | 5c0ccda8ef (+0.041, 8) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0, "orde... | 10/26 | 2026-10-16 13:08:23 UTC |

Code: branch `claude/ga-farm-d37xlq@5132c9d`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

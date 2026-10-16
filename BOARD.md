# GA farm board

Regenerated 2026-10-16 15:07:21 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 34 | 52388 | 3.4 | e2da166eb6 (+0.151, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 27/89 | 2026-10-16 15:02:35 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 24 | 35112 | 4.5 | 7aee2622fc (+0.202, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 25/64 | 2026-10-16 14:59:27 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 22 | 30926 | 6.0 | 51886649e9 (+0.152, 1) | {"P_FLEE_PCT": 8, "P_GA_AVOID_HP": 59, "P_ENGAGE2": 62, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 20/52 | 2026-10-16 15:02:01 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 28 | 43688 | 6.6 | 193f15a08c (+0.104, 3) | {"P_AVOID_DIST": 3, "P_GA_KITE_HP": 122, "P_CHASE_GEMS": 118, "P_KITE": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1,... | 19/69 | 2026-10-16 15:02:11 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 21 | 32596 | 4.9 | e2da166eb6 (+0.110, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 15/53 | 2026-10-16 15:00:53 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 27 | 40467 | 6.0 | 64249d1612 (+0.107, 2) | {"P_UNI_FLEE": 43, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "o... | 25/74 | 2026-10-16 14:57:53 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 29 | 45181 | 7.0 | f2c83fa75a (+0.163, 1) | {"P_CHASE_GEMS": 94, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TELE": 5, "P_NE_POWER_OPEN": ... | 28/157 | 2026-10-16 15:01:41 UTC |
| micro | vm | micro | ga65a6 | 4 | 25 | 40240 | 6.8 | b3b63c0122 (+0.086, 2) | {"P_UNI_FLEE": 43, "P_GA_KITE_HP": 182, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, ... | 30/58 | 2026-10-16 14:59:49 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 97 | 142095 | 15.9 | 18a189c199 (+0.117, 1) | {"P_RECALL_NEAR": 9, "P_GA_AVOID_HP": 59, "P_ENGAGE2": 62, "P_KITE_ZONE": 3, "P_VOLLEY": 21, "P_CHASE_GEMS": 223, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE":... | 65/200 | 2026-10-16 15:07:19 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 27 | 42434 | 6.3 | fd444ac101 (+0.158, 6) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 25/67 | 2026-10-16 14:59:17 UTC |

Code: branch `claude/ga-farm-d37xlq@6b9e4c7`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

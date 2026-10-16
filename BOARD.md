# GA farm board

Regenerated 2026-10-16 15:21:05 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 35 | 54134 | 3.0 | e2da166eb6 (+0.148, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 28/91 | 2026-10-16 15:12:30 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 26 | 38466 | 5.1 | e2da166eb6 (+0.139, 5) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 26/68 | 2026-10-16 15:12:07 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 24 | 34434 | 6.6 | d5d920f0eb (+0.176, 3) | {"P_RECALL_NEAR": 9, "P_GA_AVOID_HP": 59, "P_ENGAGE2": 62, "P_FRONT_ZONE": 2, "P_KITE_ZONE": 3, "P_VOLLEY": 20, "P_CHASE_GEMS": 223, "P_DANGER_T": 76, "P_FRO... | 22/56 | 2026-10-16 15:11:41 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 29 | 45342 | 5.0 | 4e8dcfa3b1 (+0.143, 1) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "order": "FLEE>NEARREC... | 19/72 | 2026-10-16 15:07:44 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 23 | 36048 | 5.9 | 6f9cb00aff (+0.098, 2) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 16/58 | 2026-10-16 15:10:51 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 29 | 43859 | 5.5 | 8950477aa6 (+0.079, 2) | {"P_CHASE_GEMS": 118, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_FRONT": 0, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_U34_ENGAGE_FALLBACK": 1, "P_R... | 27/79 | 2026-10-16 15:07:40 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 31 | 48621 | 8.6 | 48224301b2 (+0.172, 3) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_... | 30/169 | 2026-10-16 15:09:35 UTC |
| micro | vm | micro | ga65a6 | 4 | 27 | 43670 | 7.1 | ce2e6a7aec (+0.080, 3) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 31/63 | 2026-10-16 15:08:24 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 104 | 154047 | 14.3 | 734237134e (+0.153, 4) | {"P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P... | 71/221 | 2026-10-16 15:21:04 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 29 | 45812 | 5.5 | c1d63b6631 (+0.179, 3) | {"P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_GP1_ON": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "o... | 26/72 | 2026-10-16 15:08:20 UTC |

Code: branch `claude/ga-farm-d37xlq@6b9e4c7`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

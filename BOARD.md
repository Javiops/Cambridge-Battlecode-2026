# GA farm board

Regenerated 2026-10-16 17:15:21 UTC by the islands (tools/ga/island.py). Fitness = margin over the island's own control (its start genome) on the same games, shrunk mean over generations (n = generations evaluated).

| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cloud-a | vm | micro,structure,gp | ga65a6 | 4 | 37 | 57566 | 2.6 | 91965fe93c (+0.178, 1) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_KITE_ZONE": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1,... | 29/95 | 2026-10-16 15:36:51 UTC |
| cloud-a2 | vm | micro,structure,gp | online1520 | 4 | 12 | 20446 | 3.5 | 4a1104f279 (+0.111, 1) | {"P_CHASE_GEMS": 94, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_NN_ON": 1, "P_SHAREEXP": 72, "P_TRIBUTE_NEAR": 10, "P_TELE": 5, "P_NE... | 8/26 | 2026-10-16 17:04:19 UTC |
| cloud-b | vm | micro | ga65a6 | 4 | 41 | 67114 | 5.3 | a7974643e4 (+0.145, 2) | {"P_AVOID_DIST": 7, "P_KITE_ZONE": 5, "P_VOLLEY": 40, "P_CHASE_GEMS": 192, "P_DANGER_T": 67, "P_DANGER_R": 8, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, ... | 31/111 | 2026-10-16 17:02:29 UTC |
| cloud-c | vm | micro | ga65a6 | 4 | 45 | 73488 | 6.3 | 0e45e3ff04 (+0.128, 3) | {"P_FLEE_PCT": 21, "P_AVOID_DIST": 3, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_... | 32/139 | 2026-10-16 17:01:33 UTC |
| cloud-d | vm | structure | ga65a6 | 4 | 49 | 82346 | 3.9 | 5f8b15c564 (+0.133, 5) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 29/133 | 2026-10-16 16:59:08 UTC |
| cloud-e | vm | gp | ga65a6 | 4 | 42 | 71278 | 5.2 | 33cbab259d (+0.141, 2) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 43, "P_FRONT_ZONE": 2, "P_VOLLEY": 40, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0, "P_NOCHASE": 0, "P_ALLYDUTY": 1, "P_R_A... | 21/112 | 2026-10-16 17:01:40 UTC |
| cloud-f | vm | neat | ga65a6 | 4 | 47 | 77607 | 5.7 | 150107f60e (+0.156, 4) | {"P_FLEE_PCT": 27, "P_RECALL_NEAR": 9, "P_AVOID_DIST": 2, "P_GA_KILL_X": 8, "P_VOLLEY": 40, "P_CHASE_GEMS": 118, "P_DANGER": 5, "P_FRONT": 0, "P_SAFESTEP": 0... | 35/131 | 2026-10-16 17:00:13 UTC |
| cloud-g | vm | all | ga65a6 | 4 | 55 | 92681 | 8.1 | 29da5364ec (+0.160, 1) | {"P_FLEE_PCT": 22, "P_UNI_FLEE": 43, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW": 0, "P_NN_ON": 1, "P_... | 38/369 | 2026-10-16 17:03:00 UTC |
| micro | vm | micro | ga65a6 | 4 | 50 | 82198 | 4.4 | f59ed9ccd6 (+0.100, 2) | {"P_FLEE_PCT": 26, "P_UNI_FLEE": 43, "P_CHASE_GEMS": 126, "P_DANGER_R": 4, "P_FRONT": 0, "P_NOCHASE": 0, "P_FRONT_LOCAL": 0, "P_ALLYDUTY": 1, "P_R_AVOIDLOW":... | 44/138 | 2026-10-16 16:59:16 UTC |
| pc | DESKTOP-N35CN0S | all | ga65a6 | 16 | 156 | 251035 | 14.1 | e9570b1624 (+0.200, 1) | {"P_FLEE_PCT": 27, "P_UNI_FLEE": 39, "P_GA_SPAWN_HEAL": 93, "P_FRONT_OUT": 174, "P_CHASE_GEMS": 118, "P_DANGER_R": 4, "P_FRONT": 0, "P_KITE": 0, "P_NOCHASE":... | 89/378 | 2026-10-16 17:15:19 UTC |
| structure | vm | structure,gp,neat | ga65a6 | 4 | 48 | 80616 | 3.3 | 4fc8e505b0 (+0.124, 3) | {"P_UNI_FLEE": 43, "P_FRONT_OUT": 161, "P_DANGER_T": 47, "P_DANGER_R": 4, "P_SAFESTEP": 0, "P_FRONT_LOCAL": 0, "P_U34_ENGAGE_FALLBACK": 1, "P_R_AVOIDLOW": 0,... | 34/123 | 2026-10-16 17:01:03 UTC |

Code: branch `claude/ga-farm-d37xlq@cae2273`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); state: `islands/<island>/`.

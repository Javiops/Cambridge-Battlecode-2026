---
name: cambc-fight-search-1021
description: 10-21 thread "Motor de pelea con búsqueda" pairs with the user on a search-based fight engine to replace fight.h/verdict.h; facts doc link and design status
metadata:
  type: project
  modified: 2026-10-21T17:38:01.409Z
---

Started 2026-10-21 17:33 UTC (thread cmsg_017gbamt2g1g8hMHRHQBc6qbNed5z8z938V5Rz7J13UhBn). The user (olympiad medallist,
competitive programmer) designs the algorithm: state model, lookahead, pruning, evaluation. Claude supplies the engine
facts, ports it to the bc:: API on top of v98 horfocus-v1, filters it on the rival panel ([[cambc-local-filter-panel-1021]])
and hands it to the online loop.

The engine facts doc (Spanish, patch 1.0.2 numbers) is a Claude Doc at https://claude.ai/artifact/DNs1ceuuJA3PRM9NNbJFsV.
Key facts for the design:
- Turns are sequential, alternating champion by champion between the teams.
- Each champion is its own program: no shared vision, and all 8 bytes of shared memory are already used.
- C++ gets 100k fuel per turn, and API calls are the expensive part.
- Live enemy cooldowns are readable while the enemy is in vision.
- We win even trades against similar-rank rivals but enter fights outnumbered.

Status 17:45 UTC: waiting for the user's search design.
17:54 UTC USER PIVOT (cmsg_017gbamt2g1g8hMHRHQBc6qbF9ZhtPLMRkmybigHyaNA6T): "our macro is trash", HoR "lost over the map": work on FARMING, micro parked.
18:25 UTC finding (analysis/farm-route-1021/, 70 local games v98 vs pC with a per-turn mode log): HoR walks 12% of rounds to camps it abandons (6-round re-choice thrash 2/3, camp taken 1/3), waits 11% at respawning camps, hits camps 24%. Root cause: choose_target is per-champion greedy single-trip value/rounds with ~15 hand multipliers, no route, no team assignment. Proposed: a leader plans all 5 targets and publishes them in shared memory (5x6 bits); asked the user how to set up the optimisation.
Local toolchain in the cloud: pip install cambc (3.0.4); curl wasi-sdk-33, cmake 3.31.8, ninja 1.12.1 into /root/.cache/cambc (rustls download fails through the proxy); `cambc init --yes DIR`; CAMBC_WASMTIME_CACHE must be an absolute path; bot stdout is inside the .repl26a zip (team-a.stdout); use --log-limit 30000000.
18:08 UTC coordinator: camp deaths 3.1/g vs top 10 1.6 (analysis/shop-v96-1021/stellar_campsafe_1021.md; campsafe-v1 at the API thread) -> the team planner objective must include camp-death risk when sending 2-3 to elk.
20:07 UTC coordinator: camp deaths are mostly fights next to camps; Stellar solo at the monolith dies on 38% of entries; groups that kill a full-hp champion in <8 rounds: we die on 18-28% of entries vs rival 10-21% (analysis/shop-v96-1021/camp_entry_1021.md; camp-fragile-v1 at the API thread) -> the planner sends 2+ to dangerous groups.
20:17 UTC coordinator (deaths thread): after horfocus deaths no longer decide losses vs 71-95 (31 gems lost/g, rival dies 4.5x); we lose on farm/kill throughput; retreat rules powerv v1/v2 failed locally (cost farm).
20:17 UTC (API/deaths threads): NEW BASE v101 treasure-v1; online band ranks 66-90. powerv-v2 panel -38 (deaths 6.8->5.9 but gems -3%), campsafe -13. Judge farming changes on gems, clears, elk share; add no camp exits/retreats. Build the planner on v101, not v98.
20:31 UTC: BASE BACK TO v98 (user reverted 20:27; ignore the v101 line above). Shop thread: in losses rivals clear 18.9 elk groups/g vs our 10.2 (before r400 3.4 vs 1.4); wolves even, clear speed even; jungle-early-v1 dropped -> the gap is which groups choose_target opens early (analysis/shop-v96-1021/jungle_early_1021.md).
20:50 UTC sticky-target-v1 (map/macro thread) REJECTED locally: wins 42=42, gems -4.5%; abandoned episodes fell but abandoned rounds did not. The periodic re-choice mostly finds genuinely better camps; the waste is walks cut by fights/tribute/recall -> the planner must be robust to interruptions, frequent replanning is fine (analysis/map-macro-v96-1021/sticky-target-v1/RESULT.md).
21:10 UTC USER asked for the macro/farming code commented: delivered v98-commented (comments only, release wasm byte-identical to v98) at analysis/farm-route-1021/v98-commented/src + bundles/v98-commented.zip; generator scripts/annotate.py. Guide main.cpp:392, choose_target_impl :1803 with [M1]-[M9] multiplier tags, farm() :2572. The Windows Cambc2026 folder was not connected to this thread (only the Mac Downloads folders).
21:12 UTC told user: joincall-v1 -23 panel (clears 86 vs 89), elksquad-v1 -27, sticky -4.5% gems -> grouping/forcing elk costs clears; macro thread suspects early per-champion strength (shop). Planner must win on clear count.
21:14 UTC correction (shop thread, analysis/shop-v96-1021/elk_opening_1021.md): not item strength (our solo elk clears equal/better). Gap = OPENING: before r400 rival enters elk as a pair, no enemy near, 11.2x vs our 3.7; first elk r29 vs our r63 -> opening plan (first ~400 rounds) is a concrete planner target. Edited the user message.
21:22 UTC elk-opening-v1 (map/macro thread; first two champions open our nearest elk together before r60): panel +5 (bar 18), gems +1%, first elk r380->r221, deaths/clears flat = first no-harm farming change; bundles/elk-opening-v1.zip; API thread decides online. 21:21 user asked why fight/farm-map drafts failed: answered (classifier fine, the play per type was the problem; 3.0 meta draft everywhere).
21:30 UTC USER 'we feel so lost'. Proposed ONE direction to 30 Oct: computed opening plan (first ~400 rounds, 5-champion assignment + order as routing with time windows, solved at first turn), user designs model/objective/algorithm; Claude builds an offline Python farm simulator from real maps, then ports to C++; compare vs elk-opening-v1 on the panel. Asked whether to build the simulator tonight (awaiting answer).

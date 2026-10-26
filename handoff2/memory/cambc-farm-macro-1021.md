---
name: cambc-farm-macro-1021
description: Thread "Farmeo y macro del bot" (farm/pathfinding/coordination): current state, open candidates, closed lines and lessons; detail in [[cambc-farm-macro-history-1021]] and RESULTS.md
metadata:
  type: project
  modified: 2026-10-23T09:00:00Z
---

Thread cmsg_017gbamt2g1g8hMHRHQBc6qbNed5z8z938V5Rz7J13UhBn (user-paired). Full log: /mnt/project-files/analysis/farm-route-1021/orch/RESULTS.md
(dated sections, diffs orch/*.diff). Bundles in /mnt/project-files/bundles/. Cloud ws /tmp/claude-0/ws (bots/, maps/site40, m_*.txt, o_*/).

STATE 11:40 UTC 10-23 (far-map autopsy and idlerush detail moved to the history file) (base V17 = v122 t10shop-v2 0fbe0733):
- stay-v1 (d2e55f65, travel = max(gd*1.5, wait)) REJECTED online 02:53 UTC as v128: -3 (12/15), far maps -6 (3/9), near +3.
  4th far-map farm candidate inverted online (mega-far, gemrace-v7, stay); autopsy 07:05: pure noise (68 pairs, all metrics within noise).
- waitwalk-v2 (eece4251): correct but unmeasurable; USER 08:34 10-23: NO solo batch, rides inside the next candidate.

LESSONS (whole thread):
- Local gates for farm changes: gold@r400 >= base (scripts gates.py/gold400.py), deaths not up, pHuntF >= 0, rFarm1 (bundles/rFarm1.zip,
  online-like far farmer) for far-map claims. panel17 runner: BASE=t10shop-v2 bash .../local-filter-1021/scripts/runpanel17.sh
  /tmp/claude-0/p17 CAND NAME 4 (800 games/20 min, online scale = net x 120/800).
- User: short Spanish replies with numbers, Madrid time (UTC in brackets); "que las resuelvan sus hilos".
- 10-23 15:30 spread-v1 (655875fb, no 4th joiner on <6000 hp camps from r150; mirrors 12:50 in [[cambc-farm-macro-history-1021]]): runmech +10/240 but panel17 -13/800 (gems -1.3%): CLOSED flat 1040 g, not a rider. Chain tables (user rule 14:35): online-far/chain/; fuelcut gate = unlimited-fuel identity ([[cambc-fuel-1023]]).
- 10-23 18:15 capkind tool (analysis/farm-route-1021/capkind/): captures by group kind from any replay via camp captureTeam, 3 s/game. Top 10 r150-400 142 gems/g (10.2/cap) vs V19 100 (6.6/cap): same captures, ours small (gold <6 10.2 vs 6.8/g, gold+wolf 2.7 vs 1.7; gem+gold+wolf far 0.52 vs 1.43). Reference table ck_table_1023.txt. Chain-2 pipeline: online-far/chain/chain2_run.sh VERSION (pairs: gems, fuel, tb, deaths+cascades, [bcf] entries, kinds).
- 10-23 18:25 CHAIN 2 v138 (v6a bcf engage) vs v136, 125 pairs: +9 (18/9); near 15/24 vs 9/24, mid 28/48 vs 25/48, FAR 9/34 vs 9/34 (26% both, untouched). Changed pairs decided by deaths both ways (gains: base dead 23.5%, cand 8.2%; losses: cand 14.7 vs 5.9). Fuel irrelevant. bcf fires 2x in changed games (74/g vs 38). Captures r150-400 115 vs 94 gems/g, gems/cap still 6.1 (t10 10.2). Output online-far/chain/chain2_v138_1819.txt.
- 10-23 18:40 v139 (v6d=v6a+richcap-v2) 61-64 vs v136 50-75 (+11, 22/11): near 15/24 (=v138), mid 24/48 (v138 28), FAR 12/34 (v136/v138 9/34, +4/-1), new 10/19. Own end gems far 742 vs 664/683, rival same: richcap moves the far gem race, costs on mid. File online-far/chain/chain2_v139_mapclass_1840.txt. Pairing by (map,opp) from games.jsonl is exact.

- 10-23 19:30 v139 FULL 125 replays (corrects biased 160): r150-400 121 gems/g 7.8/cap (v136 96/6.1, t10 142/10.2); wins 143, losses 101 (v136 72); far 107 vs 89; gem_cluster caps 3.08 vs 1.86/g. richcap-v2 = +25 gems/g = 55% of the gap, no extra deaths (same pairs 10.0 vs 9.6). v139 losses = r400+ collapses. v140 (v9d) -4 vs v139, own gems -80 near. File chain2_v138_v139_full_1923.txt.
- 10-23 20:35 v140 (v9d) vs v139 same games: -4; losses = campguard [cg] leaves 12.9/g (vs 4.9 gains) -> captures 11.6 vs 14.1, r150-400 gems 98 vs 135, AND deaths r400+ 15.8 vs 4.7 (not prevented). v141 (v10d, tags tf/brc) -8 vs v139, far 7/34 vs 12/34, far gems 94 vs 107. fuelcut-v4 works, changes nothing. Rider bar for chain 3: same-pair r150-400 gems >=121, captures >=15.6. Tools: tag_entries.py CAND REF TAG..., chain2_mapclass.py CAND REF...

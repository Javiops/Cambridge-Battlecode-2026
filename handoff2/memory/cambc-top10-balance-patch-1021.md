---
name: cambc-top10-balance-patch-1021
description: 2026-10-21 top-10 vs top-10 study on balance patch 1.0.2 (draft, deaths, fights, economy) and the cambc 3.0.2 summary-enum decoding gap
metadata:
  type: project
  modified: 2026-10-21T08:37:59.274Z
---
Thread "Top 10 games after the balance patch" (cmsg_017gbamt2g1g8hMHRHQBc6qb5QJHZEZQDYpXo7q8KdjJQK), asked 10-21 07:50 UTC. Repeat of [[cambc-top10-after-patch-1020]] on site patch 1.0.2 (notes published 01:31 UTC; first 1.0.2 games 05:18 UTC; match patchId starts "1.0.2", public API).
DATA: analysis/top10-balance-patch-1021/: games_top10.json (1042 top-10 games 05:18-07:51), draft_compare.py/.txt, match_ids_sample.txt (240, even over 35 maps/10 teams), summaries/ (loop downloads, 15-45 s each), t10_stats.py (now also reads the 10-20 set as src top10_old, our versions via env US_VERSIONS, default 82) + t10_report.py.
DECODING GAP: cambc 3.0.2 `summary` writes numeric enums ("Unknown champion (k)" = champion_type index, entity kind 1 champion / 2 camp / 6 altar_lock, consumable 0 teleport crystal / 2 altar lock). Scripts matching names silently drop those deaths. t10_stats.load() fixes it (verified identical to cambc 3.0.4 decoding on 10 games, summaries_304/; 3.0.4 = engine 1.0.2 and names everything). The 10-20 "v81 labelling change" caveat was this gap.
DRAFT 1.0.2: HoR 100% (87 before), Ren 80, Ryth 78, Stellar 70 (86), Marcella 54 (19), Varg 23 (45), Vesper 17 (63% win when only one side), Vendetta 17, Cassi 8.
FINAL 10:50 (240 games, same conclusions; top deaths 7.9/g, 60% 3-4 attackers; v82 1.0.2 deaths 14.2/g, gold@1000 2978). REPORT 09:40 (132 games) top10_balance_patch_report.md: top deaths 7.6/g (10.0), 62% to 3-4 attackers, fights 5.9 rounds; top farm -6%. CORRECTED: v82 already died like the top on 1.0.1 (51% 3-4 attackers); gap = death COUNT (v82 1.0.2 14.0/g). v82 farm fell 21% on 1.0.2 (gold@1000 3845->3012); hypothesis: strength-only HoR build hit by the str nerf.
First cut (52 games): fewer deaths (9.4/g vs 12.2), even more die to 3-4 attackers (59% vs 48%), fights longer (6.0 vs 5.1 rounds), teleport crystal 3.2/g, altar lock 5.3/g.

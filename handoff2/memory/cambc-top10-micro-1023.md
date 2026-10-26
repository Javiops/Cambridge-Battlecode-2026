---
name: cambc-top10-micro-1023
description: 10-23 thread "Qué hace mejor el top 10": USER rule = benchmark is top-10 vs top-10 play, not mid-table rivals; data/tools for the top-10 replay study
metadata:
  type: project
  modified: 2026-10-23T11:38:14.652Z
---
Thread cmsg_017gbamt2g1g8hMHRHQBc6qbBdt3Cqy7w8tYFiNejQcHf9 (user 11:12 UTC 10-23: "analiza los ultimos games del top10").
USER RULE 11:37 UTC: "no compares nuestros games con nuestros adversarios actuales, el objetivo es el top10 ... no conformarnos con media tabla". Benchmark = how top 10 play each other (plan, micro, economy, timings, abilities); our games only to show where we differ. This thread is the lead for top-10 study; other analysis threads support with data.
**How to apply:** never use mid-table rivals as the reference in top-10 studies.
DATA: 10-23 00:00-11:20 UTC: 929 top10-vs-top10 groups (4645 games, 274 ranked). Sample 100 (60 t10-t10 ranked, 40 t10 vs ranks 58-90): /mnt/project-files/analysis/top10-micro-1023/games_1023.json, match_ids_1023.txt, replays/ (fetched by loop thread with its cookie). Decode: replaydump.js needs CAMBC_VIS_WASM=analysis/local-filter-1021/scripts/v1_0_3-DRqNt1t2.wasm; ~2.4 min/replay --every-step.
We were rank 88 at 11:35 UTC. Draft-mirror teams (DOOMSDAY, Mania, Hidden Altar Keepers, Agentic Loop Builders, Bamboo) are ranks 61-93, none top 10; map thread studies their first 150 rounds.
12:30 UTC FIRST REPORT (FINDINGS.md in that folder; 178 t10 team-games vs 38 ours): (1) Vesper capture gold@400 584 vs 231, share 32% vs 13.5%, gets reward in 38% vs 16% of groups she helps (dmg share equal); within t10 high-share tercile WR 60 vs 41. Cause other_captures main.cpp:2496 (P_CAPPRIO 0, nearest ally keeps reward). Map thread builds vespcap-v1 (single candidate). vtreas-v1 (Treasure build) failed locally 12:14 because she doesn't capture; Treasure goes after vespcap. (2) finishing 57% vs 36% (deaths thread finish-v1). (3) gems/capture 12.3 vs 8.5 (map thread). EQUAL: deaths<150, target choice, focus, Vendetta dashes, low-hp retreat (we die less).
13:05 UTC update (59 ours): Vesper credit 18% vs 38% confirmed. Diff 4 far r150-400: gold equal, gems 126 vs 92; we repeat gold+wolf 7.4 vs 2.3/g, they take gem+gold+wolf / elk+gem+gold. Not different: enemy-half captures (1.8 vs 1.9), tributes, spell/atk ratio, melee move-then-hit order. capkind.py "enem" column is wrong (last-hit attribution); use steal.py.
13:25 UTC §5-6: games shorter because t10 winners submit ~1.5x faster from r200 (500 gems r828 vs our winners r973); closing (tributes, grouping) same. Gem flow r0-600: capture gems 331 vs 273; ALL of gap = groups with gem clusters 201 vs 124; wolf/gold equal, kills -6, we lose fewer on death. Vesper captures 85 vs 32. Open: why our choose_target skips gem-cluster groups (goldval?).
13:40 UTC: richcap mechanism sent to map thread: V18 choose_target gold_w=1.0 until r940 (P_E1, P_GOLD_W_EARLY 100) while captures pay ~5.4 gold/gem -> ~85% of group value is gold; gem clusters x0.3 with a claimer, P_PAIR cap. Map thread builds richcap and vespcap.
17:55 UTC ROUND 2 vs V19 (v136 online, 43 decoded; FINDINGS §8, AUC inside t10): open = capture gems 215 vs 165 (AUC .79; gem-cluster groups 141 vs 81, 20+ caps 4.2 vs 2.8) -> richcap/far-v1; camp damage -13% with equal gold (AUC .74), our tanks +15-43% max hp, Vendetta -19% camp dmg -> item allocation hp vs damage (asked API who builds); k150 0.58 vs 0.26 -> teamfight-v1. CLOSED by finish-v1: finishing .36 vs .38. Weak predictors: Vesper share (AUC .58, vespcap -5 online), ally3 (.57).
18:10 UTC: per-champion target table sent to shop thread (campdmg_r400_t10_vs_v19.txt; shop builds shop-t10-v3). 4th gap search: recalls equal, time budget equal except HoR (camp 13% vs 20.5%); no large free gap. Thread now supports map thread (measure group mix of far-v1/richcap locally).
18:25 UTC v6d (richcap-v2) LOCAL vs V19 (40+40 vs rTop1, farm thread capkind_light.py; local-v6d/ck_v6d_v19_local.txt), r150-400 per team-game: gems 106 vs 96 (top10 142) = closes ~22% of gap; far 94 vs 78 (t10 128) ~32%. gem_cluster caps 2.67 vs 1.55 (t10 2.15, overshoot), gold+wolf 2.05 vs 2.75 (t10 1.73). NOT closed: gems/cap 7.1 (t10 10.2), <6-gem caps 9.3 (t10 6.8), 20+ caps 2.0 (t10 2.8), far gem+gold+wolf 0.58 (t10 1.43). Online v6d check pending.
19:20 UTC v139 (v6d) ONLINE (33 changed-pair games, biased; farm ck_chain2.jsonl): r150-400 gems 160 vs v136 99 vs t10 142 -> gap §8.1 CLOSED on gems (gems/cap 10.1, <6 caps 6.8, 20+ 3.4, first 20+ r95 all at/above t10). Mix differs: pure gem_cluster 5.85 caps/g (t10 2.15); mixed gem+gold+wolf 0.55 (t10 1.00), elk+gem 0.67 (0.78). Only 5 far games: far unproven. Table local-v6d/ck_v139_online_vs_t10.txt.
19:35 UTC CORRECTION: the 19:20 figure of 160 came from the changed pairs only. Full v139 sample (125 games), r150-400: gems 121 vs v136 99 vs t10 142 (~51% of gap closed; far 107/87/128, near 127/104/150). gems/cap 7.8 vs 10.2.
Left to close:
- near elk+gem_cluster 0.40 vs 1.07 caps/g (12 vs 41 gems);
- far gem+gold+wolf 0.50 vs 1.43;
- far gold+wolf 2.50 vs 2.12;
- near pure gem_cluster overshoots, 3.89 vs 2.81.
19:34 UTC (relayed by the API thread): the user promoted v139 -> V20 = v6d. From now on gaps are measured against V20. The map thread owns the near elk+gem_cluster piece.
21:05 UTC DRAFTS v1 WAS WRONG (draft ids mis-mapped). CORRECTED 21:40. API draft ids (verified on 100 decoded games): 0 ryth, 1 vesper, 2 vendetta, 3 cassi&issac, 4 stellar, 5 prism, 6 marcella, 7 willow, 8 ren, 9 varg, 10 tavi, 11 hor. These are NOT the champion_type ids.
Corrected t10 pick rates (2140 team-games): vesper 93, hor 80, marcella 77, vendetta 60, ryth 56, prism 32 (far WR 59), tavi 14, cassi 12 (WR 62), willow 11, varg 7, ren 1.
Top t10 draft = OURS (hor marcella ryth vendetta vesper, 371). Real differences:
- far maps: HoR 86%, Ren 2% (our farswap Ren is off-meta);
- Prism in 32%.
21:20 UTC built v20-draft (bot/v20-draft, bundles/v20-draft.zip ee11539a): V20 + P_T10DRAFT draft tavi vesper ryth prism vendetta on every map, tavi.h/prism.h empty (generic rules). Asked by the API thread, local only; sent to the local filter thread for the hard panel.
21:16 UTC v20-draft HARD PANEL vs V20: -117/480 (51/168, bar 29.6), negative far -32 / mid -47 / near -38. Deaths 8.15->13.09/game. Tavi D3.83 K1.65, Prism D3.19 K1.28 (vs HoR D1.33 K2.52, Marcella D1.41 K2.68), the excess mostly after r400. The draft swap alone does NOT work with our code; it needs Tavi/Prism micro (range, retreat) first.
21:40 UTC: v20-draft (-117) was built on the mis-mapped premise. tavi_prism_t10.txt: t10 Prism 48 team-games, dmg/contact round 28 (90% spell), K 2.3 D 2.6 per game; Tavi 36, D 2.2.
Continued (plan view, hfarm, bags, far numbers, respawn waits) in [[cambc-top10-plan-1024]].

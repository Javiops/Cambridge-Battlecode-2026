---
name: cambc-marcella-near-1024
description: 10-24 Marcella near-map fights vs top 10: same starts, but t10 burst with a 2xFocus spell (437 vs our 186) and leave; mcgo-v1 -20, mcf-v1 -14 on hard panel (closed)
metadata:
  type: project
  modified: 2026-10-24T04:16:10.441Z
---
Thread "Tienda y habilidades", asked by the API thread 03:05 10-24. Sheet: /mnt/project-files/bot/mcgo-v1/FICHA.md; tools analysis/power-1023/goldsrc/mfight_v2.py, mpost.py, mstat.py, vbuild/.
- DATA BUG: in decoded steps `keff` holds CAMP indices that collide with champion ids 0-5; use only `eff` for champion targets (mfight v1 was wrong).
- Near r150-800 (13 t10 sides vs 40 ours): same starts (she strikes first 58/68%, at a camp 52/53%). But episodes last 2.9 vs 5.1 rounds; dealt/taken 1.51 vs 0.89; her spell on champions 437 vs 186 dmg (2 x Focus; t10 Focus shards r200/400/600 1.9/4.4/7.7 vs ours 0/0.4/2.6). After the spell t10 make 0.33 basic attacks and leave; ours make 1.68. On mid maps t10 also stay (2.06 basics).
- Hard panel vs v6d: mcgo-v1 ae53a6d8 (leave after the spell, near maps) -20, near -15, deaths +0.39. mcf-v1 ec6f5ba8 (Bruiser-f earlier) -14. Focus on Marcella keeps losing locally (dmgm-c -18 too). Both closed in this form.
- Item rules (docs/tactics/shopping-research): shard 30 g; 5 identical shards make an emblem (150, never bought directly); Power = 6 pts, Bruiser = 5 + 1 of each other stat. Vesper table: analysis/power-1023/goldsrc/vbuild/ITEMS_VESPER.md (t10 Vesper spends 1410 g by r800 vs ours 714).
Related: [[cambc-shop-top10-1023]] [[cambc-top10-micro-1023]]
- 10-24 06:20 Jungle/Durab earlier (API ask): our farmers already carry Jungle 2nd, completed later only for lack of gold. Hard panel: dfirst-v1 (Durab-h 3rd) -17, dmon-v1 (+Monster-h) -19; heal recalls <40% hp unchanged (25.5 -> 25.3/25.1 per game, [hrec] counter, v20c-hr -2 = noise). Emblem ORDER line closed: bot/dmon-v1/FICHA.md.
- 10-24 05:00 Treasure: we already open Treasure on HoR/Marcella/Ryth/Vendetta (93-98%, same rounds as t10, +73..138 gold@800); only Vesper lacks it (t10 74% r210, +141). Covered by vshop (bcf thread); vtreas closed 10-23. Tables analysis/power-1023/goldsrc/vbuild/.
- 10-24 06:28 ONLINE chain 6 vgold-far-c (v154) vs v139, 33 far pairs (replays): Vesper gold r800 494->604 (+110 se 33, +22%), max hp r800 1303->1406 (+103 se 38), deaths same, far wins 11->12/33. Local +20% gold confirmed online; t10 Vesper hp 2420@800 still far above. Script scratch c6vesp.py.
- 06:55 final 50 far pairs: Vesper gold r800 +71 (se 28, +13%), max hp r800 +70 (se 31), deaths 0.94->0.80, far wins 17/50 both: gold shows online, no wins.
- 10-24 08:45 PIVOT (Javier 08:41, thread 'Encontrar la causa real del estancamiento'): late pieces paused; focus r0-150 near maps; judge = state r300-400 (analysis/stall-1024/a14.py) + fixed losses (fixed_keys.json). r0-150 near shop (a12): team spend ~450 vs rivals 473; only clear diff = rival Vesper opens Treasure-s vs our Durab-s (= vshop in bcf thread). This thread has no other r0-150 shop line; waiting for that study.

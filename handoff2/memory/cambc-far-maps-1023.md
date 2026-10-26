---
name: cambc-far-maps-1023
description: 10-23 thread "Por qué perdemos en mapas lejanos": gap opens r400-800 in our own half; fgw33 (far gold weight 0.33 r400-800) passes runhard/runmech; decision-side levers closed, far gap = damage per hit (power)
metadata:
  type: project
  modified: 2026-10-23T21:57:09.571Z
---
Thread cmsg_017gbamt2g1g8hMHRHQBc6qbUxbgSPLp9vPnusV9eHZpHC (user 10-23 18:31 UTC). Far = mapfeat40 d_spawn>=60 (14 maps).
Report analysis/far-maps-1023/README.md (§1-8), sheet bot/fargw-v2/FICHA.md (§1-12), tools analysis/far-maps-1023/tools.tar.gz.
FINDINGS:
- Submitted gems far, V19 losses vs rival: r400 133 vs 154, r800 347 vs 521 (88% of gap in r400-800).
- Own-half gems r0-800: V19 275 with rival, 276 solo; t10 winners 411; rival steals 28. Rich groups idle 67-82%.
- Cheaper rich groups / no company penalty / stricter hp budget (farres) all WORSEN the solo bench: decision side CLOSED.
- Execution: t10 removes 160 hp per big-group hit-round vs ours 115; same champion r400-800 monster dmg per hit-round t10/us:
  Vesper 174/117 Marcella 172/120 Ryth 148/112 Vendetta 190/145. t10 buy more Strength (Marcella 44 vs 23%), t10 Vesper 741 gold
  by r500 vs ours 337. We abandon big groups by heal recall at 20-40% hp (instrumented abdn build), not retargets.
- Strength probes (far only): solo race -40 rounds but far -3, deaths +0.43 -> handed to shop (lshop-v2) and per-champion threads.
PIECE: v20-fgw33 = V20 + gold_w 0.33 on far in r400-800 (composes with richcap by min). runhard +5 (19/14 bar 11.5) all far,
deaths +0.02; runmech veto +4 (bar 7.5) 6 gauges ok. On v20c: bundles/v20c-fgw33.zip 32a03dd5 -> API thread package (V20+lshop+fgw33).
REJECTED (runhard): fgw 0.2 (deaths r800+ +0.38), vcapfar (Vesper captures first on far) -1 / -6 vs fgw33,
no-farswap HoR on far -8 (fgw33-nofs -5 in far): keep Ren on far.
LOCAL OVERESTIMATES FAR (23:10, README §9): online far rival 453 gems@800 (local rivals 250-340, clones slow each other), only 4/39 online far games within 60 gems at r800 vs 28/84 local; Vesper contact rounds r400+ online 29-35/g vs local 49-76. v144/v145 changed 3/40, 5/26 far pairs. Judge far by gem-margin delta x 0.0009 wins/gem/game (filter fargem.py; margins online_far_margins_v139.json). Far needs ~+150 gems@800 to show online.
POWER (10-24 01:10, README §11): online far same attack count but monster dmg per hit -28..-39% (Vesper 96 vs 157); rivals 53 Strength shards by r600 vs our 22. farplan-v1 (rivals' far build per champion .h) solo +17..+24 gems@800 but bench -15..-19, deaths +0.8..+1.75 (Vendetta doubles); Marcella-only -2/+24, Ryth-only +6. fgw r150/r250/r1100 +0..+9: gold lever exhausted. Far +150 needs survival with a Strength build (deaths/fight threads).
CONTACT (10-24 01:20, §12-13): far deaths are PvP (champ dmg taken +44%); after contact we die 9.7% vs 3.1% (outnumbered 21 vs 0%); rival recalls at contact at any hp. Local bench does NOT reproduce online deaths (local we die less than rivals) -> survival pieces judged online only. Chain 5 mejora2 = v20c-vk + farout(outnum2 recall far r400+) + fp4: bundles/v20c-vk-fo2r-fp4.zip 32fc235c, FICHA bot/farout-v1, far bench +8.3 vs v20c-vk; hard panel -10 -> NOT taken; fp4 closed (far -11, deaths +0.83). v20c-vk-fo2r c4671e86 (farout only) hard panel -7 (far -8, late deaths +0.27): fails -5 veto, but API sent it anyway as chain 5 mejora2 (02:04): analyse its far games vs v20c-vk on same groups (foeapp/dmgtaken/fargem). Re-measure survival pieces vs rPunish (deaths thread, punishes like online) when it exists.
PAUSED 10-24 08:41 (Javier, via API): far + late pieces paused, focus r0-150 near maps; open nothing new on far. Chain5 online far (§15): v151 farout 12/30 wins vs v150 8/30, barely fires (noise).
BENCH: scratchpad w/solo.sh (bot vs passive rIdle, 14 far maps, 1 min, null change 27/28 identical), w/farmech.sh (84 far games
vs pHuntF/rRushHunt/rTop1); scripts an/gauge.py farcmp.py late.py bigexec.py dph.py items.py gold.py. Local judge = filter
thread runhard.sh (session_011TyD2DVFMA94FLL41QS7m2). Per-champion code goes in <champion>.h (user 20:36).
Related: [[cambc-map-class-1022]] [[cambc-farm-macro-1021]] [[cambc-top10-micro-1023]]

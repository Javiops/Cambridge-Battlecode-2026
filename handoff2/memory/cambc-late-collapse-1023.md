---
name: cambc-late-collapse-1023
description: V20 (v6d) late collapse r400+ in lost pairs: bcf-linked by association, but blocking late bcf ENGAGE (bcflate-v2/L/R) loses on the hard panel -14..-19/480
metadata:
  type: project
---
10-23 ~20:40 UTC, deaths thread. v139 lost pairs (11): deaths r400+ 13.5 vs 3.0, late cascades 2.64 vs 0.18; 52% start within 15r of a [bcf] vs 24% coverage (v138 69 vs 32%); not bags (12% of r800+ deaths carry 20+; team carries less than v136).
Tested bcflate-v2 (r400+ ENGAGE only as clear 2-on-1; PASS / v2L step home / v2R step to nearest mate) on runhard vs v6d: -14, -19, -14 (bars 15, 18, 14). Closed negative: fewer late fights is NOT the lever.
laterecall (r400+ leave below 45/50%, all or HoR-only): hard panel -5/-9/-12, deaths -0.36..-0.64 but kills drop the same: closed. Per-champion splits of panel kills/deaths are noise (chaos 96 changed pairs even for a HoR-only rule).
Late bursts vs top 10 (analysis/fights-1023/burst/README.md): same frequency, lethality and position; Ryth/Vendetta/HoR late dmg and kills >= top 10. Late gap = Vesper + Marcella only. Front closed 10-23 21:15.
Kill conversion (analysis/fights-1023/convert/README.md, 10-24 00:30): t10 kill weak rival in 10r 44 vs 38% (adv), rival recalls finish 54-62 vs 76-84%; recallcut-v1 -23/480, v1b -11, bc punrec -15: chasing recalls CLOSED; gap = damage.
vendstand-v1 (vendetta.h: no distance back-off at 2 when healthy) hard panel -12/480: closed; Vendetta at d=2 backs off via generic avoid 51% (trace bot vt). Online clash dmg/hit 89 vs 193 = build.
10-24 night: vendbuy-v1 (Vendetta Power-S for Durab-H) -26/480, v1b (Power-S added) -5; laterecall-v3 (far hot recall in contact) +0, v3e -4. Ryth/HoR buy >= top-10 damage already (fights-1023/buy).
rPunish (bot/rPunish-v5/README.md; filter panel17/rPun5, RIVS=rPun5 runhard.sh): pure-damage V20c-vk rival, V20 WR 64%, our r400-800 deaths 3.55 vs 2.96; rival never survives like online (3.1%). laterecall-v3 +2/80, farout -2/80 on it.
campguard-v3b online (v140 vs v139, 125 pairs, deaths100/cg_online_140v139.txt): 6+ [cg] games WR 40 vs 47%, rival takes the camp after each flee.
Files: analysis/fights-1023/deaths100/ (latecasc.py, late800.py, cg_online2.py). Related: [[cambc-v96-deaths-1021]] [[cambc-bc-top10-1023]]

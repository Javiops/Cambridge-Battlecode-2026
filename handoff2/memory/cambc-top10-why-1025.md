---
name: cambc-top10-why-1025
description: "10-25 PC session top10 - why top10 play works for them (questions A/B/C/D), measured on 95 fresh top10-vs-top10 replays vs kvvl/b35nohp chain 21; tools in lab\\top10"
metadata:
  node_type: memory
  type: project
  originSessionId: b5076897-29a8-4051-8ae1-ec231f97d07c
  modified: 2026-10-25T15:22:15.008Z
---

Measured 2026-10-25 15:00-16:23 Madrid by the PC side session "top10" (lab\top10\INFORME.md, README.md). User directives via coordinator 15:25/15:30 (A/B/C: why it works for them, not what they do) and 16:05 (D: deaths with gems; un-parks post-r400 work).

- Data: 95 top10-vs-top10 replays 25-10 11:40-14:06 UTC (158 near sides) vs chain 21 kvvl v164 / b35nohp v175 (same rivals 57-71; replays in lab\eval\online\c21). Rivals differ -> fight gaps split by situation.
- Tools: lab\top10\tools\replaydump.js reads ability cooldowns (+92/+96 of champion struct), per-champion vision (perspective {team, champion}; vision is per champion) and per-step hp deltas; scripts\ext.py -> dec2\*.json.gz; scripts\abc.py = ONE definition per metric for A/B/C/D (evaluador uses it unchanged); keynums.py tables.
- Replay bundles need the cookie; server may answer {"status":"pending"} instead of a zip (retry later). My bulk download of our games hit 429 -> stop, reuse other sessions' downloads.
- A: grouping costs top10 too (gems/participant-round 0.33 group vs 0.54 solo); time budget equal. Gap = who farms solo: their Vendetta/Marcella camp dmg per hit-round 121 vs ours 78-90 (Vendetta 53 shards vs 34); our HoR does 2.7 solo kills/g vs 1.15 and takes the gold. Hyp "2nd champion free" false; "pair opens rich camps" true.
- B: caught farming with 2+ allies <=4 they hit the intruder next round 24% vs our 11-12% (HoR 10 vs 2-3%, Vesper 28 vs 17-19, Ryth 21 vs 10; Marcella/Vendetta equal); HoR hits from >=3 tiles 15% of hits (stun-dash) vs 3%. Not vision, not abilities ready. Peleas found hidden var: they turn on intruders arriving <80% hp (46%).
- C: camp deaths = rival finds us hurt and alone at a camp; they start camps >=95% hp 61-68% vs 50-57%.
- D: premise false: top10 die with MORE gems; gems transfer to the killer (123 top10 deaths >=50 gems ~309 each); winners net +118 gems/near game from kills. Losers (theirs and ours) die in own half, submit alone.
- Specs sent 16:10: farmeo F1 (small camps to damage carries, HoR off), F2 (group only on rich), F3 (enter camps full); peleas P1 (punish intruder: HoR/Vendetta dash+hit, never step in without hitting), P2 low. Notes: side-session-notes\top10_ABC_especificaciones.md, top10_D_respuestas.md.
Related: [[cambc-top10-fresh-1025]] [[cambc-top10-micro-1023]] [[cambc-buddy-1025]] [[cambc-vin-1025]]
- 10-25 19:00-19:30 Madrid: summaries (signed url, `cambc summary` -> JSON; lab\top10\scripts\sum_dl.py, items_at.py). r400 near: our Marcella Focus shards 0.2-0.5 vs top10 9.2 (gold 391-450 vs 640, gems tributed 31-33 vs 59; Marcella earns gold per gem tributed); Vendetta Strength 2.3-2.5 vs 9.1; our HoR has MORE gold/hp and half the monster damage. Cause: our shop_plan starts with a whole Treasure-HEALTH emblem and completes emblems one by one; top10 buy loose damage-stat shards. Piece F4 "damage stat first" sent to farmeo. D refined: with >=20 gems near own altar and a rival <=4, top10 fight 47% / submit 7% in 5 rounds (ours 29-35% / 18-23%).
- RULE (coordinator, 26-10 night): only the loop session downloads replay bundles (the site prepares one bundle at a time per account and other downloads block the loop); other sessions pass match-id lists to the loop. Summaries via API are still allowed (sum_dl.py, p2.py only fetch summaries).

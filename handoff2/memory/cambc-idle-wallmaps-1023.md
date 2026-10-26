---
name: cambc-idle-wallmaps-1023
description: 10-23 shop thread: v122 champions stand idle hundreds of rounds on wall maps (shortcut/fracture/conc/great_wall); idletpc-v1 fix + crystals, panel17 +13
metadata:
  type: project
  modified: 2026-10-23T01:23:30.585Z
---
10-23 ~01:00 UTC, thread "Tienda y habilidades".
- Online v122 idle champion-rounds/game (gaps >=200 rounds with no damage/gold/gems/hits/deaths change): shortcut 621, fracture 407, concentrated_wealth 291, great_wall 123, others <20.
- Root causes: tribute trip flips with farm; walled reward unreachable; Vesper flips 2 tiles across a hole.
- Bundles: idlefix-v1 d761d541 (trip continues, no-step capture dropped after 4, 50-round no-progress watchdog; panel17 -2); tpc-v3 5c886ddb (carry tp crystal only on spawn walk >=80, flash when 8+ steps saved; panel17 +9, gold +1.3%); STACK idletpc-v1 5fd5d22c panel17 +13 bar 25.4, deaths =, gold +0.9%. Sent to API loop thread. ONLINE 10-23 04:05: REJECTED +10,-5 = +5 vs bar 14 (v129; v128 = stay-v1); pending check whether online idle on wall maps fell (v122 baseline 1217 g: wall maps 341 idle/g WR 34%, rest 18 WR 58%).
- 10-23 06:30 nightpack-v1 be5096ce = V17 + idletpc-v1 + flpoke (P_FLPOKE 1, P_FLP_ADD 11) + farswap-ren; pHuntF 69-11, pPoke 75-5, deaths not up, 0 faults, pPoke fuel run-outs 9.4 vs 5.8; sent to loop (no panel17). API rule 04:38: a candidate needs ~+80/800 on panel17 (realistically +150) to pass in one online batch.
- 10-23 07:30 ONLINE v129 idle (73/250 summaries): wall-map idle 294->45/g, shortcut 487->0: fix works online. Tonight v122 (1630 g): rivals mostly mirror our draft (mirror WR 50.7%); 15 teams beating us >=60% win FIGHTS: r400 champ dmg -14%, kills 1.58 vs 2.19, deaths 2.94 vs 2.45, gems 137 vs 171 (gap from r200); strong rivals buy Power shards (we 0) but vesppow was panel -13. No +80 draft/shop lever.
- 10-23 09:40 paired v129 vs v122 (117 g): wall idle 220->32, net +2/14; crystals 26-35/g on wall maps. Built RIDER idlefix-v2 9d1b3c56 (crystal cap: 1 held, 1 buy/100r/champion, gain 20+; counters tpc=/wd=/unreach=/holdto= in status line); sheet bot/idlefix-v2/FICHA.md; vs pHuntF six indicators ok except fuel +0.8, first20 +9r.
- 10-23 10:00 idlefix-v3 462c0837 (v2 + fuel_ok(40000) check only, gskip counter; fuel 5.2 vs v2 5.5 vs V17 4.7) sent as rider. BUG (unfixed, V17-level?): Vesper trapped at (69,77) on 01big_world for 1000+ rounds (seen in tpc-v3 and idle6 runs), every target unreachable, ~500 fuel run-outs; suspect own ward closing corridor. Moving spawn-path field out of init_paths fixes +10 early run-outs on big_world (idle6, not sent).
- 10-23 09:50 USER asked nightpack-v2: built 740d4232 = V17 + idlefix-v3 + farswap-ren (no flpoke); pHuntF 72-8, pPoke 73-7; swap maps (14/40, path>=60) +4/+1, control +1/+1; worse: first20+ +11..18r, pPoke deaths +0.39 (Vesper +0.26). Sheet bot/nightpack-v2/FICHA.md; sent to loop, its call.
- 10-23 ~11h map thread: big_world Vesper trap CAUSE = dash into hole-ring pocket (8 neighbours blocked, not visited -> no dash step, all targets unreachable). pocketfix-v1 fe296c22 fixes locally (441->2 cuts), mech test gate pass/unresolved; ONLINE ~0 (747 v122 night losses, 0 cases) -> rider only, does not explain big_world stalls. Sheet bot/pocketfix-v1/FICHA.md.
- 10-23 12:30 nightpack-v3 0f49ec8d = V18 (nightpack-v2, promoted 10:56) with idlefix-v5 c41e0e74 ([trip] counter, spawn path via draft byte 29, [isle] v3: off-mainland champion walks to pocket edge, dashes over holes to mainland; traps big_world (71,80), ambush moat room via crystal). Kept [isle], not pocketfix. vs V18 240g net -5 gate pass, deaths +0.28 watch; rider only. Lesson: a full-map search on every unreachable-goal turn = fuel FAIL (tail 28 vs 12).
- Local gates are chaotic: any change flips ~1/3 of 80 games (even a 10-gold buy on near maps); keep near-map behaviour bit-identical when targeting far maps.
- Scripts analysis/overnight-1021/scripts idle.py, six.py (compare idle only within one source).
Related: [[cambc-shop-abilities-v96-1021]] [[cambc-map-class-1022]]

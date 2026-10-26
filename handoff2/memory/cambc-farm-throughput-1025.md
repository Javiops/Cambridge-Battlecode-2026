---
name: cambc-farm-throughput-1025
description: 10-25 farm thread: farm gap vs top 10 is THROUGHPUT (+28% champion-rounds near monsters, +9% dmg/round); o79b (no hold bonus) small +; o80 gold weight and o81 stacking CLOSED (trios at top-10 level do not win); online judge method, h2h vs kvvl gate
metadata:
  type: project
---
Farm thread 2026-10-25 13:00 UTC (branch claude/project-thread-jhnqzy, handoff/fuelfit-farm/NOTES.md; tools in /mnt/project-files/analysis/farm-route-1021/capkind/: goldcmp.py, contact.py, ctparse.py, cmpwin2.py).
- Ground truth (statistics JSON medians r150/r300, top 10 online near 40 games vs our near 80 panel): gold earned 562/1410 vs b35 496/1112; gems collected 65/159 vs 38/106; monster damage 12102/25392 vs 8010/15852.
-TIME BUDGET 13:00 UTC (gem/contact.py): top10 35% of alive rounds within 4 of a monster (16% at 3-4) vs us 26% (9%); walking 42% vs 51%; dmg per near round 63.8 vs 58.6 (+9%); rounds near monsters/game 419 vs 328 (+28%) -> the gap is champions standing at the SAME group (present at capture 3 vs 2), same mechanism as [[cambc-buddy-1025]]. Piece o81_stack.py (P_STACK_HP 0 so value/team^0.75 applies to every monster group; variant P_SHAREEXP 50) running 12:05 UTC (bots/e81, e81b).
- o79 (hold-altar x2 only for >= 15 gems): near 63 vs 62, far equal. o79b (no hold x2 at all): near 63 vs 62 (+8 -7), far 49 vs 48, monster dmg +16/+26%, gold r150 557. Zip nohold-b35.zip in git handoff/fuelfit-farm/zips/ (commit adf7313) offered to the PC.
- o80 (gold weight 50/70 before r600) CLOSED: near 54/60 vs 62, far 46/45 vs 48; gold and gem income unchanged.
- o81 stacking (share exponent 0.75/0.50 for all or monster-only groups) CLOSED 13:40 UTC, 544 games: 0.50 reproduces top-10 TRIOS (g3 41/31/22%) and gems r150 44, but rounds near monsters unchanged (329 vs t10 419) and far maps collapse (40/56); 0.75 neutral. Trio formation by itself does not win: top-10 trios are trios AT camps (more members per camp + range 3-4 presence).
- Instrumenting choose_target costs fuel (47/80 vs 60/80): run instrumented bots with --fuel-quantum 2000000.
**Why:** user wants whole-system causes measured against the top 10; this decomposition says which lever (time at the same group) before touching the model again.
**How to apply:** METHOD (user 10-25 12:10 UTC via coordinator): the judge is ONLINE (each candidate alone on 15 pinned groups, ~3/hour); local panels are prediction only and the one local requirement is beating kvvl head-to-head (ws/h2h.sh NAME: 26 near maps x 2 sides). b35 loses online near maps (-4 vs kvvl, fight-camp deaths); pieces go online once a base matches kvvl. Locally still judge farm pieces by rounds near monsters, champions at capture, monster damage r300, gold/gems r150 (gem/goldcmp.py, gem/contact.py) plus W/N near 80 / far 56 vs b35; PC J2 decides. See [[cambc-elkval-1025]], [[cambc-buddy-1025]].

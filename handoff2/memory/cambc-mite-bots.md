---
name: cambc-mite-bots
description: 2026-10-15 two Mite-style bots (Mite rules on study25, Mite from scratch) and their measured win rates vs study25/study24/v30/v29; which Mite rules transfer and which lose
metadata:
  type: project
  modified: 2026-10-15T10:50:46.149Z
---

2026-10-15 10:09 UTC the user asked to build a bot with Mite's behaviour on top of ours, a Mite from scratch, and measure
both vs previous bots. Report `/mnt/project-files/analysis/mite-bots-2026-10-15/README.md` (sources, logs, zips
`/mnt/project-files/bot/mybot_mite_s25.zip`, `mybot_mite_scratch.zip`); also in repo branch claude/project-thread-ztmd0i.

**Results (maps won both sides / lost both; official, 44 gen, 60 hold):** mite_s25 (study25 + Mite shop order + Mite
fight: focus one, always engage, melee wall, KITE/VOLLEY off, HALF 10) vs study25 3/2, 15/9, 12/13 = equal to study25;
beats v29/v30/study24 on hold (22/10, 20/10, 26/15). mite_s25_full (+ Mite draft + hp<50% recall) loses official 0/6,
even gen, best on hold (20/12 vs study25, 33/9 vs v29): noise vs study25. mite_scratch (literal 1400-line clone):
15% win rate everywhere, 84-4 lost vs mite_s25; farms 130-165 gems/100 rounds vs our 200-240.

**Lessons:** Mite's draft (6-22) and early recall (6-17) lose on our engine; shop order and fight rules are neutral.
The replay-measured rules are not sufficient to reproduce Mite (pack movement, per-map openings, walk-vs-recall
over a game were not captured). Our farm engine is the better base; no upload recommended.
Related: [[cambc-top2-dissection]] [[cambc-eval-method]] [[cambc-top1-cycle]]

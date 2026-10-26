---
name: cambc-focus-farming
description: 2026-10-14 the user set the day's priority to farming speed only (not fights); findings on why top teams outfarm us, and the study8/study9 uploads
metadata:
  type: feedback
  modified: 2026-10-14T06:51:27.608Z
---

2026-10-14 06:26 UTC the user said: "we should 100% focus on farming better today", then "they still
outfarm us without fighting". Work on how fast we bank gems (camp choice, squad size, captures, shop),
not on fight micro.

**Why:** fight rules that won locally (P_TWIN, study7: 13-5 arena) went 0-25 online.
**How to apply:** measure with `farmbench.sh` (rounds to 1000 vs idle), then `tools/stbatch4.sh TAG BOTS`
(vs the site version, REF=d1 by default; header text still says study6) and `stsum2.py TAG BOTS`.
Online banked gems per 100 rounds: `tools/late.py`, `farm.py`, `vcmp2.py`. Answer in the user's language.

Versions: study8 = study6 + P_DANGER 3 = site v16 (06:35, arena bot `d1`); online 11-39 (ws/ours9).
study9 = v16 + P_RESERVE_PCT -60 + P_SHOP_PLAN 2 (Mite's tank shop: durab-s, jungle-s, bruiser-h,
power-s) = site **v17** (06:50, arena bot `r2sd`, mybot_study9.zip). Arena 15-3 vs d1, deaths 15 vs 37,
farmbench 3638 vs ~3786. Online games go to ws/ours10 (fetch since 06:51).

Findings (ws/ours8, ours9; Mite rows replay 7345b4fc): we lead at r300 and fall behind after; 7 deaths
per game vs 1.4. Mite on rows: all 5 bodies kill each of the 3 wolf camps on their half in rotation,
ONE champion captures all 66, the rest walk on; a capture every ~22 rounds, 132-gem tribute bags, no
recalls, 1122 gems by r377. We use only 2 of our 3 wolf camps (g0, g2; g4@42,4 rarely) and split
captures 22/22/22, 594 by r378. The 108-gem 3-monster camps on expanse get need=2-3 and score low
(distance-dominated). P_STEPOFF was slower in farmbench (4011 vs 3950). Related: [[cambc-study-versions]].

06:55 bug found (fbase main.cpp, not uploaded yet): other_captures() wrapped the ally loop in one attempt,
so an ally out of vision threw and every champion on the tiles captured (22/22/22 splits). Fixed with a
per-ally try, plus P_CAPCLAIM 1 (only allies still claiming count). Farmbench 3570 vs study9 3638, rows
465 vs 502 (bots c1x/c2x). 06:58 the user stopped the bot work to study 100 fresh top-10 games (ws/top10x).

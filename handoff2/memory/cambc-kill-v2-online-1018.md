---
name: cambc-kill-v2-online-1018
description: 2026-10-18 online verdicts of kill-v2 (site v68) and fuel-v1 (kill-v2 + fuel fixes), both REJECTED on the 19:00 UTC v65 random draw; how to judge fresh from the site; noise floor of one batch
metadata:
  type: project
  modified: 2026-10-18T21:06:12.185Z
---
kill-v2 (finish window, parent bank-v1b-clean, fuel +0.116 accepted by the user's choice B) = site v68, active 20:00:51 UTC. fuel-v1 = kill-v2 + fuel fixes (same decisions with unlimited fuel; local 54.0% vs bank-v1b-clean), uploaded by the user ~20:59 = site v69, active 21:00:31 UTC, batch 21:00:31-21:04 (loop judge: online/judge.py 69 65 --since 2026-10-18T21:00:31; loop thread confirmed the same numbers). Both replayed draw data/draws/2026-10-18T190032Z.json (29 groups; v65 played it 19:00-19:46 = 23-122).
JUDGE FRESH: games.jsonl can lag (collector stopped 20:16), so fetch from the site (no cookie): audit scratchpad judge/judge_site.py SINCE OUTDIR (lists our side-a unranked groups) then judge/judge_fresh.py OUTDIR/groups_all.json OUTDIR -v (pairs vs latest v65 loop game per key = rule, and vs v68 key by key). online/judge.py 68 65 --since ... is the loop's own version.
kill-v2 FINAL 20:50 UTC: 27-118 vs v65 23; changed 13 for / 9 against (+4 < 9.4) -> REJECT; score 51 higher / 43 lower; corners 4-0, packs +2, lanes -2.
fuel-v1 FINAL 21:05 UTC: 26-119; changed 17-14 (+3 < 11.1) -> REJECT; score 53 higher / 65 lower (guard ok); vs kill-v2 same keys 17-18; lanes not better.
KEY FACTS: two same-decision bots (kill-v2, fuel-v1) differ in 35/145 results -> one batch only sees ~8-10 point win-rate gains; the kill line is ~+2-3 points. v65 vs itself 15:00 -> 19:00 UTC on 48 same keys: 1 for / 7 against, so old references are biased against a candidate; never pair extra groups with old v65 games.
21:02 user asked "another 20 just to make sure"; 21:05 I advised not to (adds ~+3; combined +7 vs 14.6; a clean version needs a new draw plus a v65 replay); waiting on the user.
By rule after a fail: v65 back on the site (user) + one fresh v65 batch. help-v1 ([[cambc-help-v1-1018]]) was planned on fuel-v1; parent now to be settled.
Related: [[cambc-kill-strategy-1018]] [[cambc-judge-power-1018]] [[cambc-online-decides-rule-1018]].
21:47 UTC loop: replays of the 19:00 draw in online/data/replays: v65 145/145, v68 110/145; v69 not fetched (only needed if someone checks kill-v2's finishing online).

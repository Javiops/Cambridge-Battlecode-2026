---
name: cambc-v55-teammate
description: 10-17 10:56 site version 55 = the teammate's upload, v54 + P_V53_VARG_SOLO_ESTIMATE (Varg splash not counted on single-monster camps); user asked to measure it vs v54; thread id and loop labelling
metadata:
  type: project
  modified: 2026-10-17T11:11:18.441Z
---

2026-10-17 11:01 UTC the user attached their teammate's bot sources (de_rules.h, fight.h, main.cpp, mapplan_game.h, mapplan.h, opening_replace.h, params.h, profile.h, track.h, utility.h, verdict.h) in the project chat and asked to measure it against v54. The teammate had already uploaded it to the site: games are labelled version 55 from about 10:56 UTC (first found by the thread below in online/data/games.jsonl).

What v55 changes over v54 (from the thread's first diff): one switch, P_V53_VARG_SOLO_ESTIMATE 1 in params.h and main.cpp, so Varg's splash damage is only counted when the camp group has two or more monsters. Everything else matches bots/v54 ([[cambc-v54]]).

Threads: "Teammate bot vs v54" (root cmsg_017gbamt2g1g8hMHRHQBc6qb315YqVVNHGtczTJ5p5vMrE, branch stem claude/teammate-vs-v54) measures it locally on the two panels and head to head on the 17 site maps both sides, bar as in [[cambc-panel-noise]]. The online loop ([[cambc-online-loop]]) was told 11:03 to record version 55 in versions.jsonl, split the 10:5x batch by site label, and pair v55 vs v54 and v53 on the same rival and map.

**Why:** the site runs one bot at a time, so from 10:56 the loop's batches measure v55, not v54; v54's online record is the 09:5x batch plus part of 10:5x only.
**How to apply:** report online numbers by site label (54 vs 55), never by upload time; v55 is the teammate's line, v54 ours, and the user decides which stays online.

**11:10 results.** Local (thread "Teammate bot vs v54", branch claude/teammate-vs-v54-yhmg9q, bot in bots/teammate_1017, logs /mnt/project-files/analysis/teammate-1017/): flips vs v54 7-2 for v54 on the 12:52 panel, 5-6 on the v51 panel; deaths per game equal (8.2 vs 8.3, 8.5 vs 8.6); 17 site maps both sides 0 won / 4 lost (contest, interlock, rushbait-v2, swirl), 8 identical games; 260 generated maps 37-36. Verdict: same bot within noise, the switch only shifts the fuel budget. Online (loop, 10:5x batch, 26 groups): v55 36-94 (28%) vs v54 42-103 (29%); paired same rival and map v55 vs v54 36-37 in 130 pairs (flips 8-9), vs v53 36-41 (flips 14-19); lanes 1-25. Both v54 and v55 sit two batches below v53 (flip share 41-42%).

---
name: cambc-pinned-replay-1019
description: Unranked "Previous match" replay (sourceGroupId) pins rival bot versions; how the loop pairs candidate vs base exactly since 10-19 11:11 UTC
metadata:
  type: project
---
10-19 11:05 UTC USER pointed at the site option "Replay against the bot version used in an earlier match" and asked that both batches match (bots, sides, maps).
API: POST /api/v1/challenges {teamId, sourceGroupId, mapIds} -> rival plays the version it used in that source group (version hidden in the group: null). Same maps/sides verified 120/120.
Loop tooling (scratchpad of the loop thread): replay_src.py SINCE UNTIL TAG (replays every group sent in the window, rows tagged replay_tag + source in challenges.jsonl), pair_exact.py TAG (exact pair judge, replay side = for).
Why it matters: judge.py "latest base game per (rival,map)" mixed rival versions: v76 team-fight-v1 was 13/13 that way, +5 (17/12) pinned. Use pinned pairing for every candidate from now on.
Related: [[cambc-judge-two-step-1019]] [[cambc-site-access]]
12:18 UTC USER DECISION: v76 team-fight-v1 = BASELINE V4 ("seguimos descartando reglas que en vdd son mejores por ser muy estrictos"). Pinned evidence: 31-55 +5 (17/12); 71-95 (rivals since 11:23 UTC user) draw 120434Z v72 61-59 vs v76 71-49, +10 (21/11, bar 11.3). v76 active+selected; 2nd 71-95 batch cancelled. Next candidates: fresh v76 draw on 71-95, candidate pinned.

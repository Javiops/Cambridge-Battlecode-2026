---
name: cambc-games-side-bug-1023
description: 10-23 games.jsonl flips result/gems/draft for 4.8% of games (group side vs per-match side); judge unaffected; corrected rows in analysis/overnight-1021/sidefix
metadata:
  type: project
---
Found 10-23 ~11:30 UTC (map thread). online/collect.py took `side` from the GROUP, but the site swaps sides per match (matches[].sides[].teamId).
441/9180 v110+ rows flipped (312 real wins logged as losses, 129 reverse), all in NON-loop groups (challenges.jsonl groups: 0) -> judge.py verdicts OK;
any all-games study (map WR, rival tables, night analysis, summaries us/them via g['side']) was skewed. v122 real 58.7% vs logged 55.3%; boss_battle 91% vs 68%.
Night 10-23 near-map "drop" was an artifact (real 66->69%); mid 69->64%.
Patch (2 lines) + corrected rows: analysis/overnight-1021/sidefix/ (collect_patch.md, rows_v110plus.jsonl, check_sides.py). Sent to loop thread (owner of collect.py); 10-23 11:23 loop: NOT applied, waits for Javier OK; non-loop readers must use rows_v110plus.jsonl.
**How to apply:** until fixed, take our side/result per match from groups/<gid>.json matches[].sides[] (teamId 292625c5...), not games.jsonl, for non-loop games. ExCode runs a copy-like bot; its HoR idles at (12,30) on boss_battle.
Related: [[cambc-online-loop]] [[cambc-map-class-1022]]

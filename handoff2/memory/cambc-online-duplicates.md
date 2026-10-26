---
name: cambc-online-duplicates
description: Online rematches are byte-identical games (deterministic engine); 22% of games.jsonl are duplicates - dedupe before any stat or judge
metadata:
  type: project
---
Found 10-23 11:50 UTC (deaths thread). Engine is deterministic: same two bots + map + side = same game (local check: identical seed/result). In online/data/games.jsonl 9486 of 42325 win/loss games (22.4%) are exact duplicates on key (version, opp_id, map, side, rounds, gems, opp_gems); v122 20%, candidates 0-4%.
**Why:** base stats and judge pairs overweight rematched games (e.g. ExCode starvation "12 games", 4 copies of one HoR death).
**How to apply:** dedupe on that key in every online analysis and in the judge. See [[cambc-fight-model-1022]], [[cambc-judge-two-step-1019]].
Judge impact (audit 10-23 11:40): within a pinned tag 12/7845 base copies; across b1+b2 108/4243 pairs are copies (23 flips); re-judging 18 two-step candidates moves net by <=1, no pass/fail changes. Scratchpad judge/judge_pinned.py TAG,TAG_B2 counts a copied pair once; loop should skip b1 (opp, map, side) keys when drawing b2. [[cambc-audit-1021]]

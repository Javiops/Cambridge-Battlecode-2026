---
name: cambc-fuelfix-1020
description: audit verdicts on engine-3.0 candidates 10-20 (fuelfix, econ3c-ff, sealed, vision-v1, draft-meta v82): code checks, audit rules, judge script usage
metadata:
  type: project
  modified: 2026-10-21T01:00:27.921Z
---
- fuelfix-nd 7f70bfab = first build a7529446; decay build rejected (cut turns 3x on big_world). econ3c-ff 3f74dda1 = v80: E3/E4 correct, P_CHASE_GEMS is a fight rule (own flag P_E1C 0). Batch 1 vs v76 +13 (bar 10.8), target maps 9-0.
- sealed-v1 f0e3acde: guard fires only when the only altar is camp-walled; rode inside vision-v1 as a bug fix; boss_battle 4-0 online.
- vision-v1 63ab1b1f = v81: end-of-turn ward_turn, never pre-empts an attack; batch 1 +8 (bar 10.6), promoted by Javier. Ward-vision cache parity 70/70 but no fuel saved (wards cost ~+2.2 cut turns/g, split/lanes). Rule: a parity-proven fuel saving may replace a judged build without a new pair; a change of choices needs one.
- draft-meta-v1b 70bba5e2 = v82: RULE champion properties from engine queries (attack_range, ability is_dash), never name lists (HoR was seen as ranged by allies, its dash as none; same bug as P_DASHFIX). Per-champion shop builds may stay name-keyed. Batch 1 +15 (bar 12.2). Mechanism: Cassi+Issac die in the same round (537/537), so merge the pair in death metrics; v82 cut death events 16.1 -> 11.0/g (champions 11.1 -> 7.8, other 5.0 -> 3.3), kills 9.6 -> 10.0, gems +80.
- Patch rule: a pair straddling a site patch is judged only where the patch cannot favour the candidate (v82 pair: vs no-HoR rivals 83 pairs net +14).
- Judge: scratchpad judge/judge_pinned.py TAG[,TAG_B2] BASE CAND [TARGET_MAPS]; dedupes games by match and copied pairs across batches ([[cambc-audit-1021]]). Mechanism scripts: scratchpad v82m/ (events.py merges the pair).
Related: [[cambc-audit-1021]] [[cambc-engine-3-1020]] [[cambc-judge-two-step-1019]]

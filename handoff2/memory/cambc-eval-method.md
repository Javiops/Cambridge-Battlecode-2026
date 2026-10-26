---
name: cambc-eval-method
description: How to score local head-to-heads honestly (maps won both sides, mirror games, noise floor); side-symmetric tie-breaks tested and rejected; 2026-10-15 audit
metadata:
  type: project
  modified: 2026-10-15T15:46:00.000Z
---

2026-10-15 audit (`analysis/audit-2026-10-15.md`, scripts `analysis/tools/audit/`): of 794 map pairs in
analysis/teammate logs, 261 were exact mirrors (both versions played identically; the side decided) and 524
split 1-1. Game counts like 43-45 mostly count identical games.

**How to apply:** report head-to-heads as maps won on both sides / lost both / split (`sign.py LOGS`), call a
winner only at about +6 net maps on 44 generated maps (p<0.05), and use 100+ generated maps when possible.
study24 vs v30 gen = 18-8 (p 0.08), the only moderately supported gain; teammate switches and panel gaps are noise.
The caster panel (spar11/12/16 on 5 maps) is 15 pairs: a veto, not a ranking (wards 29-1 there, lost head-to-head).

**Side asymmetry tested 09:50 UTC, rejected:** our bot plays differently by side because ties are broken in map
coordinates (compass order of next_moves_from, first index, truncated centres). `P_SYM` (bot/study24_sym/) mirrors
all tie-breaks: sides identical on 37/44 gen maps, but farm speed unchanged (47734 -> 47665) and head to head vs study24
9-19 gen maps. The gap is chaos, not bias; being side a online costs nothing on average. Noise floor: a fuel-only
no-op change still decides 12 of 44 gen maps (5-7). Tools: analysis/tools/audit/divg.sh, trajcmp.py.

Online A/B: games are deterministic, so challenge the same rivals/maps with A then B right away and compare per
game; dedupe repeats. P_VOLLEY 50's "16-59" was not worse than v24 on shared rivals (3-27 vs 5-25). [[cambc-volley]]
2026-10-15 08:42 ladder: #52 of 374 (1615); the user said 08:53 UTC that site version 34 is active (likely the teammate's study24 code, whose rules namespace is v34de: inferred, not confirmed). Update this line when the active version changes. 11:32 UTC the user said the new active bot is site version 35 (likely study26 = study25 + 3 fixes, merged 11:13; which zip was uploaded is unconfirmed). 12:08 UTC study27 active (site version number pending). study28 (PR #6) = site version 37, uploaded 13:59 UTC (the 13:39 unranked batch ran study27, 14:38 ran study28). 15:40 UTC the user switched the site back to study27 (v36) after study28 went 16-29 ranked; study27 is active.
**10:30 UTC part 2:** noise = fuel-only no-op builds decide 6-20 of 44 gen maps, net within ±4. Ablation: study24's gen
edge is only P_E_RETARGET 6 (off: 6-17); per-map family rules identical on gen, worth 0-5 maps off on official.
**maps_gen (44) is now a training set:** on 60 fresh maps `arena/maps/hold60` (genmaps seed 20261015, keep sealed,
never tune on it) retarget 20 vs 6 is 10-14 and study24 vs v30 21-15 (gen 18-8). Report both sets for every candidate.
Top-10 caster drafts on fight maps: 24-6 by Univardisty/VeryGood, only 5-4 by other teams (team strength, not draft).
Logs analysis/audit-logs/, report analysis/audit-2026-10-15.md part 2.
**11:55 UTC re-check on study27** (user asked "why do we play differently per side, 100% a bug"): self-play splits at
round 1 (equal-length first step, tie by map order). P_SYM merged onto study27 (git merge-file from study24_sym, clean):
107/212 vs study27 on 563 maps, ~4% slower farm; its flip work makes side B run out of fuel on turn 1 (rows: all 5 B
champs, lose round 2). With P_SYM, expanse self-play mirrored 455 rounds; last round the engine's in-round order let B bank
first. Self-play side wins: study27 A33/B20, sym A21/B32 (no side bias). Recommended leaving it; user not yet answered.

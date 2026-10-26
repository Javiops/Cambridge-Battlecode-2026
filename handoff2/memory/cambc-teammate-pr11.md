---
name: cambc-teammate-pr11
description: 2026-10-15 19:48 teammate's PR #11 (study27 + edge area spell + cooldown-aware dash): 89-55 vs study27 locally, the edge area spell is the gain; main holds study28, not study27
metadata:
  type: project
---

2026-10-15 19:48 UTC the user asked to study the teammate's bot in PR #11 of Javiops/Cambridge-Battlecode-2026
against "our main, currently v27". Finding: **main holds bots/study28 (PR #6), not study27**; study27 is the
version online (v36). Report: /mnt/project-files/analysis/teammate-pr11-2026-10-15/README.md.

PR #11 = study27 with two fight tweaks in fight.h (the other 4 files identical):
1. **Area spell at the edge**: if nothing was cast this turn, aim the area spell at a nearer tile to reach an
   enemy at range 5 (previously outside the range-4 sweep). This alone: 65-22 maps both sides (p 0.00), 31-12 on
   300 fresh generated maps. **This is the gain.**
2. **Cooldown-aware dash**: a melee with dash counts as reach 3 only when the dash is ready. Alone 76-59 (noise);
   on top of 1 it adds nothing (68-65), slightly better vs caster sparring (1339 vs 1324 of 1614).

Whole PR vs study27: 89-55 on 613 maps (p 0.01), 18% fewer deaths; vs study28 98-61. It is a fight change, not
farming (gems +1.5% from kills). Caveat from [[cambc-online-ab]]: fight rules that win locally can tie online, so
the real test is the online A/B. The PR adds a whole bot copy plus ~20 MB of evidence, against the repo rule in
[[cambc-repo-versioning]]; the clean way in is its 107-line patch applied to the current bot folder. Nothing
merged or uploaded. Related: [[cambc-teammate-bot]] [[cambc-study26-fixes]]

2026-10-15 21:20 UTC param sweep on the PR 11 bot (study27+corners+edge AoE), report analysis/sweep-pr11-2026-10-15/sweep.txt: **P_RECALL_PCT 50 (was 55) wins** 43-26 on 313 maps + 48-32 on 300 fresh maps (arena/maps/fresh300, seed 777001) = 91-58. Losers: P_RESPAWN 0 (49-146), P_NEXTW lookahead (second-lap rule) 59-101. P_TRIBUTE_GEMS/P_SHOP_GOLD change nothing (draft memory overrides). Others noise.

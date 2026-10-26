---
name: cambc-online-is-economy
description: 2026-10-16 08:30 the bot active on the site is Fran's study27-economy (branch fran/study27-economy), not study27 v36 nor study28; PR #17 MERGED 09:25, PR #21 (P_MONO contest fix) MERGED 09:29: main = online bot + P_MONO; PR #18 adds the 4 review switches OFF on it for teammates (P_CHAINWALK untested); RecallCost (I020) is noise on study27-economy; later versions in cambc-online-versions-1016
metadata:
  type: project
  modified: 2026-10-16T15:20:49.411Z
---

2026-10-16 08:05-08:30 UTC: the six uploaded source files of the online bot were byte-identical to Fran's branch `fran/study27-economy` (main held study28); PR #17 renames `bots/study28` to `bots/study27-economy` with that code on top (harness, gate.py repointed). So I019-I022 results in [[cambc-review-fixes-i019]] (PR #16, incl. RecallCost PASS) were measured on study28; lineage lines in [[cambc-study26-fixes]], [[cambc-study28-chancancel]], [[cambc-eval-method]] saying study27 (v36) is active are stale. Build/measure on bots/study27-economy and label online data accordingly. Related: [[cambc-teammate-pr11]] [[cambc-harness]] [[cambc-repo-versioning]]
08:22 RecallCost on study27-economy = noise (1000 maps, 166.5 vs 166.4 gems/round), I020 paused. 08:30 PR #18 (claude/econ-review-switches) ports switches `P_ALTARPICK`, `P_RECALLCOST`, `P_CAMPMODEL`, `P_CHAINWALK` + loggers `P_LOGRECALL`, `P_LOGCAMP`, all OFF = online bot on 60/61 maps; doc docs/I019-I022-switches-study27-economy.md; first test P_CHAINWALK; PR #16 superseded.

**09:25 UTC:** the user merged PR #17: main now holds bots/study27-economy = the online bot. PR #18 and PR #21 (P_MONO contest fix, 3 files +77 -2) rebased onto main, no conflicts.

**09:29 UTC:** PR #21 merged too: main = online bot + P_MONO (contest fix); the site still runs study27-economy without P_MONO until the user uploads the mono zip. PR #18 still open.

Version timeline from 10:46 on: see [[cambc-online-versions-1016]].

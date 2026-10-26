---
name: cambc-study28-bugaudit
description: 2026-10-15 16:13 bug audit of study28: recall cancel/restart loop (study28-only), 4 minor fixes, PR #9, zip mybot_study28_fixes.zip; local tie vs study28
metadata:
  type: project
  modified: 2026-10-15T16:14:30.384Z
---

Bug audit of study28 (thread "Bug audit of study28", 2026-10-15 16:13). Five fixes, all behind switches, in PR #9 on Javiops/Cambridge-Battlecode-2026; ready zip at /mnt/project-files/bot/mybot_study28_fixes.zip. Not uploaded to the site.

- P_CHANFIX 1: study28's cancel rule stopped a recall when a foe was 5-6 tiles away and the same turn the near-recall/flee rule restarted it (325 of 391 cancelled recalls restarted at once on the 9 official maps; one Ren stood still 8 rounds). Fix: do not start a recall that would be cancelled next turn. Only exists since study28 (see [[cambc-study28-chancancel]]).
- P_CHANTHR: channel_threat no longer counts foes that cannot hit us (on their spawn, tributing, recalling).
- P_DANGERFIX: update_danger shared byte 7 wrapped every 256 rounds so an old enemy-pack sighting looked new; team avoided camps/altar ~40 rounds for nothing.
- P_UNJAMFIX: step_towards "never farther from goal" check never blocked anything (never triggers locally).
- P_FULLFIX: farm's "even at full hp can't take this camp" check used the old 0.75 reserve.

Results: all five vs study28 locally 35-36 maps (tie); vs the three caster test bots on official maps 48-6 (study28: 44-10). None of these is why we lose; see [[cambc-online-ab]] and [[cambc-corners-why]] for where the losses are.

**Why:** the user asked "any bugs in the code?" when stuck; this records what was checked so nobody re-audits.
**How to apply:** build on study28 + these fixes (or study27 if the recall-cancel rollback in [[cambc-study28-chancancel]] is chosen); judge fight rules online, not locally.

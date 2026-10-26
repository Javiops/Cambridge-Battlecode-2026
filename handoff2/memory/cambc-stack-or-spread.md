---
name: cambc-stack-or-spread
description: 2026-10-15 when to put several champions on one camp: per camp by hp (3000+ stack, else spread), study26_stack zip, idle-champion tests rejected
metadata:
  type: project
  modified: 2026-10-15T11:36:14.415Z
---

2026-10-15 11:35 UTC (thread "stack or spread", report analysis/top1-cycle-2026-10-15/stack-or-spread.md):
- **Rule that wins: decide per camp by hp.** Camps of 3000+ hp (2-3 elks, elk+wolves, 3 wolves; ~1 in 4) get up to 4
  champions, valued at gems/team^0.75. Smaller camps stay solo (pair on gem clusters). Switches `P_MAX_SHARE 4`,
  `P_SHAREEXP 75`, `P_STACK_HP 3000` (one line in choose_target's value). study26+rule vs study26: 154/106 maps won/lost
  both sides on 563 maps, positive on every set incl. 150 maps made after tuning (maps_f150, genmaps seed 31337).
  Behaviour: big-camp kills 2.0 -> 2.4 champions, 26.7 -> 21.5 rounds, +28% big kills; small camps unchanged.
  = **study27** (team repo PR #4, bots/study27, zip `bot/mybot_study27.zip`; same binary as mybot_study26_stack.zip). PR #4 merged by the user 12:06 UTC (study26 folder renamed to study27 + edited; body has a Spanish handoff study24->27). Not uploaded to the site as of 12:06.
  Extra map sets shared at arena/maps/v100 (seed 1015) and arena/maps/f150 (seed 31337, untouched by tuning).
- **Rejected:** threshold 2400 (gain gone, 125/120); Mite's squad rule literally (2 on every small camp) 68/138;
  whole team on the first camp 89/75 (noise); map-level features (camps per champion, spacing) do not predict.
- **Idle:** our champions do not wander (2-5% wasted steps, same as Mite). Standing by a camp about to respawn is
  11% of turns and is right: P_NOIDLE 0/2/5 (leave to join or walk elsewhere) lost 45/131, 40/127, 52/120.
**How to apply:** don't re-test pairing small camps or no-idle variants; build on the 3000-hp rule.
Related: [[cambc-top1-cycle]] [[cambc-ab-tool]] [[cambc-eval-method]]

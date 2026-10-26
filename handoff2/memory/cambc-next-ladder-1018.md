---
name: cambc-next-ladder-1018
description: 2026-10-18 10:23 chronological Elo ladder on the PC: core-v57 ranks 27 of 28, far below every old bot; lab measured against too-weak rivals; user decision pending
metadata:
  type: project
  modified: 2026-10-18T10:24:00.000Z
---
2026-10-18 09:29 USER DECISION: a separate measurement-only ranking (does not touch lab.toml, the gate or rule choice) of core-v57 against the old versions, including ones that never passed the online loop, to place the new line on the timeline. Package next\online-ladder\ (zips\ with 26 bots v3..v58_fuel_nobank, timeline.md, online-winrates.md) extracted by the user 09:39; report next\results\online-ladder.md.
RESULT 10:23: core-v57 is 27th of 28, only above starter-v1. v3 (13 Oct) beats it 79-80%; online-era bots 87-100%; v53 and the fixed-design versions 97-100%. Site maps round 500: v53 767 gems vs core-v57 294; deaths per game 10.6 ours vs 2.1 theirs. Elo: core-v57 1676 (starter 1500), online-era bots 2300-2390. All 26 old zips compile and run on the current engine. Local order vs online win rate: only noise with 5-7 versions, no online estimate. Thread withdrew its recommendation to upload core-v57.
Cause: all core-v1..v57 progress was gated against starter and own-code sparrings (user rule: no old bots in next/ to avoid overfitting), so the lab never saw the real gap. Method (gate, fuel rule, mirrored tie-breaks, one rule per version) is judged sound; the opponents were the problem. Earlier the audit thread had proposed v53 as a held-out judge only (never parent or tuning target); the user had not decided. Decision on how to continue pending at 10:23.
How to apply: any future lab opponent set must include at least one strong external bot (e.g. v53 frozen as judge); do not trust 47-53% plateaus against own bots as a sign of strength. Related: [[cambc-next-lab]] [[cambc-next-lab-round3]] [[cambc-v53]].

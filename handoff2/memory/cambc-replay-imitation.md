---
name: cambc-replay-imitation
description: 2026-10-16 replay dataset + behaviour cloning of Mite/Univardisty fights; v44 retreats too early; im_a (Mite retreat curve) uploaded 15:09 in mybot_online1252_jackgo_imitation.zip but dies 89 vs casters; im_p (Mite thresholds only with ally within 2) is the thread's pick, swap pending; round 3: remaining gap is formation, pair-movement test go-ahead 15:33
metadata:
  type: project
  modified: 2026-10-16T15:34:43.118Z
---

2026-10-16 12:00-12:55 UTC thread "Imitation learning from top replays" (user: GA/RL path, "choose the local winner").
Data: /mnt/project-files/analysis/replay-dataset-2026-10-16/ (README, turns_top101 115k contact turns from the top2-dissection
steps.tgz, turns_us_v44 24k from 27 of our v44 games vs top 10, targets, bc/ model json, scripts). Repo PR #28 (docs + I060).
**Findings:** top teams' engage/retreat = mostly an hp cut at ~42% (72% acc; logistic with 29 features 74%, MLP no better).
Targets: nearest 85% (Mite), team focus 59%, lowest hp near random; Univardisty picks most-gems target 84%.
v44 retreats in contact at 40-50% hp 68% vs Mite 42%, above 60% ~25% vs ~17%, and still dies more (died10 14.8% vs 11.7%).
Cause: P_UNI_FLEE 44, P_LOWHP 50, unfavourable rule (P_GA_AVOID_HP 60 / P_AVOID_DIST 4).
**I060 gates vs v44 zip:** im_a PASS 54-25 p=0.001 panel 11/19; im_b PASS 56-27; im_c FAIL; zip mybot_ga65a6_imitation.zip, not uploaded.
Decoding new online replays needs visualiser v0_0_2 (run `cambc view <zip>` once to fetch assets); toolchain by curl per
[[cambc-arena-setup]]. Related: [[cambc-top2-dissection]] [[cambc-rl-assessment]] [[cambc-ga-farm]] [[cambc-harness]]

Coordinator 12:57: hold upload; 12:52 online bot needs 2-3 batches alone. Related: [[cambc-strategy-1016]] [[cambc-dqn]] [[cambc-online-is-economy]].

**14:21 UTC:** im_a rebuilt on 12:52 online bot PASS 63-38 p=0.017, casters 17-20; stronger variant 50-37; zip mybot_ga65a6_mono_fuelguard_jackpot_imitation.zip supersedes mybot_ga65a6_imitation.zip.

Rounds 2-3 (im_p, formation gap, pair test): see [[cambc-imitation-rounds]].

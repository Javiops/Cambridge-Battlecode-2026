---
name: cambc-teammate-1017
description: 10-17 11:00 teammate's upload = v54 + P_V53_VARG_SOLO_ESTIMATE only; local judge says noise (panels +5/-1 for v54, site h2h 0-4 maps); site label 55 since 10:56
metadata:
  type: project
  modified: 2026-10-17T11:10:46.919Z
---

2026-10-17 the user attached the teammate's source ("my teammate has uploaded, measure it against v54"). Diff vs bots/v54: one change only, P_V53_VARG_SOLO_ESTIMATE 1 (my_dps drops Varg's 1.5x splash when the camp has a single monster; used in squad sizing, claim and chain checks). No P_CAPTURE_RECALL_FIX in it. Folder bots/teammate_1017 on branch claude/teammate-vs-v54-yhmg9q (stacked on PR #33's branch).

Local judge (cambc 2.2.5, v54 panel numbers reproduce the v53 review's panel4 exactly): 12:52 panel flips 7-2 for v54, v51 panel 5-6; deaths/game equal (8.2 vs 8.3, 8.5 vs 8.6). Site maps h2h: 0 won both, 4 lost both (contest, interlock, rushbait-v2, swirl), 8 identical games, deaths 10.0 vs 9.2; hold60 8-8, dev200 29-28. Under the bar: a fuel-sized noise change. Logs /mnt/project-files/analysis/teammate-1017/.

Site: our match groups carry version label 55 from 10:56 UTC (likely this upload, not confirmed by hash); coordinator told to have the loop label it separately from v54.
**How to apply:** treat 55 as v54-equivalent locally; only online pairing vs v54 can tell. Related: [[cambc-v54]] [[cambc-panel-noise]] [[cambc-online-loop]].

---
name: cambc-defense-ablation-1018
description: 2026-10-18 defense-v1/v2 local ablation and judge numbers (DH1-DH5)
metadata:
  type: project
  modified: 2026-10-18T14:51:00.000Z
---
2026-10-18 ~12:12-12:30 UTC, Phase 2 on the PC, h2h vs base-v53-mod (125 maps, 250 games). defense-v1 = full DH1-DH5 defence rewrite: 34% (28-40) FAIL. Ablation from v1: without DH3 ('wait for the second before fighting') 47%, without DH1 (memory of out-of-sight rivals) 40%, without DH5 37%, without DH4 34%, without DH2 (team force comparison) 28%: only DH2 helps. defense-v2 = v1 minus DH3-wait, DH1, DH5: 55% (48-61) inconclusive. Vs 4 judges base/v1/v2: score 43.9/26.6/48.1%, deaths 4.39/4.30/6.80, own-half deaths 3.16/3.52/3.97, kills 4.66/4.11/9.53, gems r500 739/678/675. Fuel same as base. lab.toml champion = base-v53-mod.
How to apply: a defence rewrite that waits for allies or trusts stale enemy memory loses farm faster than it saves deaths in this engine; DH2 (force comparison) is the only piece with signal. Related: [[cambc-defense-results-1018]] [[cambc-defense-system-1018]].
Moved from [[cambc-defense-results-1018]] (summary as first recorded there):
2026-10-18 12:12 UTC bot thread (Learning from Carson Burke's bots), Phase 2 result on the PC. defense-v1 = full DH1-DH5 defence rewrite: 34% vs base-v53-mod, 26.6% vs judges. defense-v2 = v1 without DH3-wait, DH1, DH5: 55% vs base (95% interval 48-61%, inconclusive); judges 43.9% -> 48.1%; not the defence intended (kills double, own-half deaths up, gems at r500 down). Only DH2 (team force comparison) has signal; full ablation and judge numbers in [[cambc-defense-ablation-1018]]. Plateau rule says switch to the elkring farm route; alternative under the 11:33 online-decides rule: paired online batch of defense-v2. No zip made. Card posted.
How to apply: a defence rewrite that waits for allies or trusts stale enemy memory loses farm faster than it saves deaths in this engine; DH2 (force comparison) is the only piece with signal so far. Related: [[cambc-defense-system-1018]] [[cambc-online-decides-rule-1018]] [[cambc-v53-top30-diagnosis-1018]].

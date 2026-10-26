---
name: cambc-teammate-dash-survival-1021
description: 2026-10-21 teammate's bot2_osc_dash_survival_v1 (v98 + dash/camp-probe/engage fixes) vs v98 locally: site35 43-27 (+8 net maps), hold60 63-57 flat
metadata:
  type: project
  modified: 2026-10-21T15:42:10.146Z
---
15:37 UTC the user attached the teammate's bot "bot2_osc_dash_survival_v1" (13 files; same md5 as their Mac folder ~/Downloads/bot2_osc_dash_survival_v1/src). It is v98 horfocus-v1 with only main.cpp changed + combat_policy_v1.h + camp_probe_policy.h:
HoR dash rewrite (range 2, valid_tiles, multi-hit scoring), lethal-camp escape (never fired), camp probe gives up after 12 near turns (fixes endless A->B->A on hidden camps), failed engage lets the champion farm when no foe within 5.
LOCAL cambc 3.0.4 --release both sides: site35 43-27 (A 25-10, B 18-17), maps won both 12 / lost both 4 / split 19; gems 752/668, deaths 12.1/13.7, kills 10.3/9.0, faults 0. hold60 63-57 (10/7/43), gems flat.
Files analysis/teammate-vs-v98-1021/ (README.md, results.txt, diff, src). Nothing uploaded; online pair offered to the user. Related: [[cambc-teammate-v84-1020]] [[cambc-online-decides-rule-1018]]
ONLINE (API thread, 17:51): uploaded as mate-dash-v1 = site v102, pinned on v98 draw vs 71-95: v98 58-62, v102 62-58, +4 (14/10 flips, bar 9.8): positive but below bar; batch 2 vs 91-115 playing. Audit follow-ups: read dash range/radius from the ability instead of hard-coded 2/1, gate on dash effect not champion name, lethal-camp escape never fired (needs a camp hit >= 1.04 x hp+shield; near-dead code).

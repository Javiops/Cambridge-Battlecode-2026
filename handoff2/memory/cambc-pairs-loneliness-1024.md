---
name: cambc-pairs-loneliness-1024
description: 10-24 pairs/loneliness line (near maps r60-150): what was tried locally, online origin/rate/compactness of top-10 pairs, mgwp in chain 13
metadata:
  type: project
---
Thread "Primera pelea en cercanos" (opening clash -> v20c piece), working with stall thread [[cambc-stall-root-cause-1024]]. User 10-24 12:43: keep exploring this line.
- Online (stall thread): pw3 / mg1c+pw3 cut loneliness 2-3 pts (42.9->41.3) with no result change (-1/250). Stall thread: need ~30% to matter; accept a piece only if gold r300 drop <= ~30.
- Local near mech test (120 g, 6 rivals) is DETERMINISTIC: identical code reruns give identical numbers; the +-3 pt loneliness / +-100 gold "noise" is chaos from any code change.
- Closed locally (loneliness 43-47%, no gain vs pw3): sync departures psa/psb/psc/psd/pst (wait fires ~1 round/champ), fixed duos dua/dub/due (gold worse), compact-v1 cma/cmb (loneliness -3/-4 but gold r300 -115; gold-exempt cmc: no gain).
- waitpair-v1 (wait for respawn next to ally): pw3+wp 39%, but on mg1c base 44% (= chaos). mgwp (mg1c+pw3+waitpair, 0fd65cfa, git handoff/mgwp commit 2294e10) hard panel +1/480; loop queued as chain 13 mejora1.
- Local diagnosis (pw3): lonely rounds are approach 61%, capture 60%, wait-respawn 63% alone; fight-camp only 29%.
- Online top10 vs V20 near r60-150 (scripts analysis/bc-top10-1023/late/pairorigin.py, pairrate.py, compact.py): paired walks originate the same way (spawn 16/17%, both converge 27/24%, one detours 55/57%) -> shared-memory "destination+arrival" not justified. Difference = formation rate 5.0 vs 3.4 per 100 champ-rounds, streak 9.1 vs 8.0; team more compact (centroid dist 5.3 vs 6.4, nearest ally 5.0 vs 6.5), same depth 0.70.
- 15:00-16:00: online chain 13 mgwp (v161) net 0. Execution gap online (focus.py, analysis/bc-top10-1023/late): same-target rounds 25% vs 15%, 2nd hitter <=3r 33% vs 23%, kill hitters 1.82 vs 1.24, deaths 0.75 vs 1.16/g. focus-v1 (target bonus, handoff/focus) no effect. join-v1 (status bit "in fight" on claim byte, walk to fighting ally): local near deaths better but hard panel hja -11, hjb -13, mgj (v157+join) -18 near -16, gold r300 -98 vs mg1c; v157 alone hard panel -5. Byte 7 = danger-altar, not free for help calls.
- 16:00-17:00 OPENING (analysis/bc-top10-1023/late/opening.py, open40*.py, earlybuild.py, farmexec.py): top10 near r40 own monster dmg 2676 vs our 2079; gap is r0-20 (Vendetta 534 vs 160 dmg by r20, first hit r6 vs r24; HoR r11 vs r22); nobody buys before r40 (not build). opening-near-v1 (v157 + far groups priced down until r20/30, opa-ope) reproduces top10 r20-40 damage but loses gold and damage by r300; stall a14 logit@300 local 0.33-0.48 vs v157 0.59 -> closed. hitlast-v1 fires ~0 (no-hit adjacent rounds are passing non-target camps). hitpass-v1 (hit awake/guardless camps in passing) dmg r300 +2273 vs +1265 but gold -50, a14 0.53 vs 0.59 = neutral. Local a14 script: scratch a14loc.py (not shared).

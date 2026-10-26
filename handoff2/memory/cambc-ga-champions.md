---
name: cambc-ga-champions
description: 2026-10-16 GA farm champion tournaments: 14:15 run winner d20281a41e (75-38, 22-10 vs v44), 100-map confirmation with PC leaders, report columns (pairs vs v44 / others, deaths vs casters and v44), zips in /mnt/project-files/bot/
metadata:
  type: project
  modified: 2026-10-16T15:54:44.122Z
---

**15:17 UTC first champion tournament (14:15 run, CHAMPION-2026-10-16-1415.md):** winner d20281a41e (cloud-a), as upload build (fuel guard + contest fix) on 60 sealed maps vs v44 + spar11/12/16: 75-38 pairs (p=0.001), vs v44 alone 22-10. Changes: front-line rule off, safe step off, joins fights near allies, chases only gem carriers, evolved net on. Same mix spreading across islands. Best-of-21 on the same maps, so replaying on 100 fresh sealed maps with the next 3 and the PC leaders (94bd2723b9, fd444ac101, 9dac1d5d56). Zip /mnt/project-files/bot/mybot_d20281a41e.zip, not uploaded. Coordinator asked for deaths vs caster panel and vs v44, and the v44/caster split of the gain, in the replay report; champion becomes the upload candidate after the im_p decision, not stacked with it. Macro GA run 2 leader also failed (21-31 vs online bot, gain all from casters 80-1); run 3 scores only vs the online bot, 40 maps/gen.

**15:18 UTC:** commits 5be3765 (new MICRO gene P_PAIR_LOWHP: back off up to 40% hp earlier when alone; "fight only when paired" = P_PAIR_N 2 + P_PAIR_ENGAGE) and ef19483 (CHAMPION.md columns: pairs vs v44 and vs other rivals separately, deaths per game vs casters and vs v44, for every finalist and the control); the 100-map confirmation started before ef19483, the report will be rerun from cached games. Confirmation cids map to new layout: 617c178e26=d20281a41e, 2760fcd394=94bd2723b9, ee33400f1c=4f97657e5f, a9a87ec5ce=b672ef97f6, f37fcf381e=aae1734f50, 15f525d8e0=9dac1d5d56, e415836ff3=fd444ac101. Islands told to pull/stop/ensure at end of generation (15:18).

Related: [[cambc-ga-farm-tool]] [[cambc-ga-farm]] [[cambc-replay-imitation]] [[cambc-local-judge]].

**15:36 UTC (commit a6bc6ab):** im_p carried as genes (P_IM_PAIRED, P_IM_PAIR_R, paired values of the 4 retreat thresholds; defaults = base, 36/36 identical). Champion control = the online bot: genome 'online1520' (ga65a6 + P_IM_PAIRED 1) built on mybot_online1252_jackgo.zip as overlay (overlays can be zips); 36/36 identical to mybot_online1252_jackgo_imp.zip with unlimited fuel, so champion zips = online bot + genome. `--graft '{"P_IM_PAIRED":1}'` tests every finalist with im_p on; the 16:16 run uses --per-island 1 with that graft. Coordinator decision 15:38: only cloud-a restarts as a new island from `--start online1520` (new name, new control); other islands keep their populations, graft decides; migrate others one at a time if the graft shows their edge does not transfer. Farm to adopt the Local judge specialist panel (casters x2, farmer x0, replaces spar11/12/16) once buildable. 100-map confirmation ~50% at 15:36.

**15:47 UTC panel predictions on record (Local judge thread, analysis/local-judge/README.md, 5 fight maps, 50 games/bot, written before the 15:46 batch results):** jackgo vs 12:52 identical off stampede; im_p build vs 12:52 flat/slightly worse (2-6 flips, p=0.29; deaths vs caster+hunters 11.6 vs 6.6); im_p vs study27-economy better (12-4, p=0.08); champion d20281a41e vs 12:52 worse (3-10, p=0.09). 77-map run firming up. Coordinator: hold d20281a41e until the 100-map confirmation (with deaths) and the panel verdict on the im_p graft; the 15:46/16:46 online batches of im_p decide which local judge to trust. Related: [[cambc-local-judge]] [[cambc-online-loop]].

Continued in [[cambc-ga-champions-2]] (15:52 confirmation: d20281a41e fails, b672ef97f6 holds).

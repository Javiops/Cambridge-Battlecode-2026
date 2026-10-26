---
name: cambc-v53-replay-review
description: 2026-10-17 user's v53 replay cases (Nameless, Silver Samurai): causes, switches on v53 (wards best +10/+6), fight-estimate calibration (real spell damage AUC 0.63 vs 0.59)
metadata:
  type: project
  modified: 2026-10-17T08:45:07.942Z
---

Thread root cmsg_017gbamt2g1g8hMHRHQBc6qbDuHeM3HDGpCbdyxCp1DSxJ, branch claude/v53-replay-review-qop5ws (switches on bots/v53, all off by default). Folder /mnt/project-files/analysis/v53-replay-review-2026-10-17: decoded replays, cases_*.md, panels/, calib/, scripts (window.py replay viewer, fuelcheck.py, calib.py).
- Setup in a fresh container: replays need cookie (ask the Online loop thread); replaydump needs `cambc view` once (downloads engine wasm); panels = tools/panel from branch claude/local-judge-1mgyqy, built as bots/pa_sp_* (12:52 zip) and bots/pb_sp_* (v51 zip).
- Causes: verdict judged once at contact and never again when 0 (packs r115, 2.6 -> 0.1); no wards (P_R5_WARD 0); spells spent on camps with foes at 6 (114/808 casts); v52 engage counts bodies (r620 pilgrimage winnable fight skipped); tribute with foe adjacent; blind farm dashes; attack tile picked next to other awake camps (corners); ambush squad check only on intact camps.
- Panels, flips vs v53 (12:52 / v51): P_R5_WARD 1 +10/+6 (deaths -2/game); P_CAMPHOLD 6 +4/+2; wards+camphold +6/+5; P_TRIBSAFE 3 +1/+3; P_DASHCALM 10 +7/0; P_PVSP -1/-11; P_PV_REJUDGE +3/-5.
- Calibration (16,344 first contacts, build that never leaves): AUC for "lost fight": old unit_dps 0.587, P_PVSP 0.628, P_PVSIM 0.632. Even at ratio <0.3 we lose only ~55%: leaving is the costly part, not the estimate.
- Leave-cut test (calib/): never-leave vs leave<0.6 (sim): 246 = 246 games won of 340, deaths 9.8 vs 10.3: leaving moves deaths, does not win.
- Panel 4 vs v53 (new base, same play): P_PVSIM +4/+2 (fixed the P_PVSP -1/-11); P_PVKITE (kite + call help on leave, user idea) +3/-1, with sim +7/-2; sim+ward +10/-2. Zip /mnt/project-files/bot/mybot_v53_ward.zip (v53 + P_R5_WARD 1, +10/+6) offered 09:4x, upload pending user. 09:08 user chose to test ONLINE mybot_v53_simkitew.zip (v53 + P_PVSIM 1 + P_PVKITE 1 + P_R5_WARD 1; panels +7/-2, fewest deaths 8.3/8.6 vs 11.0/10.4); 09:09 user: "es la v54" (uploaded). Repo: bots/v53 -> bots/v54 with the 3 switches on, PR #33 (base = PR #32 branch), identical wasm to the zip; loop thread asked to log v54 and compare vs v53 by site label incl. deaths/game.
- 09:37 teammate claim "v54 places no wards" checked: false. 5 online v54 games: ours 53/41/31/19/1 (collision has few bushes), top rivals ~2x ours. In compact.py jsonl, ward placement is event k=14 (not 20); team index 0 = side A.
**How to apply:** better estimates help only with a decision rule calibrated on them; measure leave-vs-stay by ratio band before choosing a cut.
Related: [[cambc-fight-verdict]] [[cambc-v53]] [[cambc-panel-noise]]

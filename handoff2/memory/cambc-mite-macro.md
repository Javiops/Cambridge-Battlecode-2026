---
name: cambc-mite-macro
description: 2026-10-15 P_MITEMACRO harness - Mite's per-map macro (draft, items, camp order, recalls, tributes) hardcoded on study28 to test only micro; fidelity and panel results
metadata:
  type: project
---

2026-10-15 19:24 UTC the user asked to hardcode Mite's macro per map so only our micro / mid-game decisions are tested.
Built on bots/study28 behind `P_MITEMACRO` (default 0 = identical games). 1 = Mite draft + emblem build + per-champion
ordered camp groups (who takes the reward, recall-on-capture), recalls, tributes at Mite's altars; 2 = draft + items only.
Code: bots/study28/src/mite_exec.h + generated mite_macro.h; tools/mitemacro/ (extract.py, genheader.py, panel.py,
compare.py, lag.py, campdmg.py, README.md in Spanish). Source = least-death Mite game per map/side from the top-2
dissection steps.tgz, mirrored to the other side. Zip: /mnt/project-files/bot/mybot_mitemacro_study27.zip (not uploaded).

**Results (local):** pace near Mite on expanse/interlock/rows; slower elsewhere (our camp kill speed, e.g. Varg 162 vs
238 dmg/round on rows) and mirror plans collide on fight maps. Vs panel (x_s27, spar11/12/16, v30, study25; 108 games):
study27 85-23, +Mite draft/items 66-42, +full macro 34-74: our micro does not fit Mite's plan. study28 vs study27 both
with the macro: 7-10 differing games (p 0.63). Execution lessons: skip late steps only before starting them (mid-step
abandon cascaded), cap waits for company (P_MM_RALLY 12), credit ally captures only near Mite's time (P_MM_EARLY 20).
Related: [[cambc-mite-offscreen]] [[cambc-top2-dissection]] [[cambc-online-ab]] [[cambc-new-maps-rule]]

2026-10-15 20:50 UTC bug hunt on study27 (ab.py, 313 maps both sides), all no effect, reverted: capture gold to fewest-items ally 58-64; ground AoE aimed at most camps 14-22; Varg targets the camp its splash covers 4-4. Ren low-fuel start does not happen in the normal bot. Recommended next: PR 11 online.

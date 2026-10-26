---
name: cambc-study28-chancancel
description: 2026-10-15 study28 = study27 + P_CHANCANCEL 60 (cancel doomed tribute/recall): PR #6 = site v37; local 24-5 but online equal and ranked 36% -> rollback to study27 (v36) recommended 15:36
metadata:
  type: project
  modified: 2026-10-15T15:46:00.000Z
---

2026-10-15 13:30-14:05 UTC, thread "try and test those changes" (built on the study27 online dissection [[cambc-study27-dissection]]).
**study28 = study27 + `P_CHANCANCEL 60`**: while channelling a tribute (1 round per 10 gems) or a recall (5 rounds), sum the damage
from every visible foe that reaches us before the channel ends (first hit = max(1, d - fight::reach + 1), hits x fight::unit_dps);
at 60% of our hp cancel (cancel_submit_gems / cancel_recall) and let the turn run on. vs study27: gen 3-2, hold60 4-3, dev200 24-5
(p 0.00), official 2-0; caster panel spar11/12/16 unchanged (78-11 / 97-2 / 79-11). Threshold 40 = 14-13 dev, 80 = 18-10: keep 60.
Team repo PR #6 merged by the user 13:58 UTC (branch study28, study27 folder renamed + edited in place; main now has bots/study28), zip bot/mybot_study28.zip (hash = measured wasm).
Not uploaded/activated by Claude: activation is the user's call.
Rejected switches and their numbers: [[cambc-study28-rejected]].
**How to apply:** local fight-rule gains are not trusted until the online loop shows them ([[cambc-online-loop]]); measure study28
like-for-like vs study27 on the same opponent+map pairings once the user activates it. Noise floor seen today: a fuel-only no-op
(s28 with all switches off) still decided 5 of 53 maps (2-0 on official+gen).
**Status 14:46 UTC:** PR #6 merged ("main is study28", 14:00). The user confirmed the 14:38 online batch ran on study28 (site version number not given). First study28 sample: 47-103 (31%), top-10 9-41; like-for-like on shared opponent+map pairings 15-15 vs the 13:39 batch and 17-19 vs the 12:37 study27 batch, i.e. same as study27 online so far. Three ~150-game batches today: 37%, 25%, 31%, no real change. The loop runs until 16:38 UTC (batches 15:37, 16:37); the thread adds study27 reports to current-state in PR #7.
**15:05 UTC online verification (150 decoded unranked games):** the cancel fires as intended: deaths inside a tribute channel 8 (292 gems) vs 23 (1436) on study27, recalls now cancelled 6% of attempts, deaths within 10 rounds of an interrupted channel 8% vs 18%, deaths/game 5.5 vs 5.8. But gems lost/game unchanged (63.7 vs 63.5): bags now die in outnumbered/alone fights instead (first hit with no ally within 8: 22% vs 17%).
**15:30 UTC "test those changes" / "run them locally first":** study28 + P_MSQUAD 1 (Mite squad size on every camp, ported from bot-st25-card) vs study28: official 0-6, gen 7-21, hold 14-21, dev 29-102 (farms 6% slower), caster panel 66-13/93-2/66-14 vs study28's 78-11/97-2/79-11: rejected again, the panel veto makes it a real loss, not only self-play. study28 + P_ROWSEND 150 vs study28: no-op everywhere except the official rows map, where it loses on both sides (banks 1000 at r404 vs r401 mirror): rejected. Zips kept in bot/mybot_study28_msquad.zip and mybot_study28_rowsend.zip, not uploaded. Uploading to the site (POST /api/v1/submissions multipart file=zip) is blocked by the auto-mode classifier as a production deploy; the user must upload or allow it.
**15:36 UTC ranked regression, thread recommends rolling back to study27 (site version 36):** ranked today by active version: before v35 179-166 (52%, opp median rank 48); study27 29-31 (48%, median 26, 5-0 vs rank 31+); study28 16-29 (36%, median 34, 14-21 vs rank 31+); on 25 ranked games with same opponent+map as earlier today, 8 wins vs 13 before; elkring 1-5, monolith 0-4, lanes 2-5.
**15:46 UTC ranked decode (45 s28 vs 60 s27):** cancel not the cause (deaths/game 4.2 vs 5.0); lost worse fights (first hit outnumbered 44% vs 28%, died with gems 35% vs 24%). Cost: recalls with a foe within 5 arrive 54% vs 73%. Unproven either way; needs alternation vs same teams. Table: analysis/v35-dissection-2026-10-15/ranked_28_vs_27.md. study27 (v36) live.

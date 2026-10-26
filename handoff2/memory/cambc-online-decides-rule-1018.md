---
name: cambc-online-decides-rule-1018
description: 2026-10-18 online rules: 11:13 only games since BASELINE V1 upload valid; 11:33 USER DECISION 'online decides' (hourly paired loop vs top 30 is the main judge, local only filters, keep if > 57% of changed games, steps 13-15); 11:36 elo no longer matters, goal top 10
metadata:
  type: project
  modified: 2026-10-18T14:55:00.000Z
---
2026-10-18 11:13 UTC USER RULE (loop thread 11:11): only games from 12:59 Madrid = 10:59 UTC (BASELINE V1 upload) are valid; applied by default to the DH2 dataset and diagnosis recheck (older 16-17 Oct v53 games only if the user asks).
11:33 UTC USER RULE / DECISION: ONLINE DECIDES. The online loop (v63 BASELINE V1 vs the current top 30, hourly, paired by rival and map) is the MAIN feedback loop and main judge; online paired matches have more priority/value than local measures, the way the lab once used 90% vs starter and >50% vs champion. Local gate and judges are only the filter before an online batch (go online if not clearly worse: high end of 95% > 50%, no faults, no more fuel turns); the online paired result is the verdict.
Online process (Phase 2 steps 13-15, amendment block given to the user to paste; audit thread writes it into STRATEGY.md 'New direction'): 13 paired vs BASELINE V1 games (same rivals/maps/sides); 14 at least 2 hourly batches; 15 keep the version only if > 57% of changed games go our way; plateau (two versions without gain) is counted online, not locally.
11:36 UTC USER RULE: ranked elo no longer matters; the goal is top 10 and the only trustworthy signal is win rate against real online rivals, even at the cost of losing elo while testing candidates online. Local bots never decide; the local filter is kept only to save online hours on broken bots.
Context: [[cambc-defense-system-1018]] (DH1-DH5 design, phase 1 status). Related: [[cambc-v53-base-decision-1018]] [[cambc-online-loop]].
12:20 UTC user: upload defense-v2 BEFORE the 12:46 UTC batch; BASELINE V1 (v63) has one full batch on the new top-30 list (11:5x, rivals refreshed 11:08), enough to pair since games are near-deterministic (v53 vs v53 batch-to-batch 11 flips of 140). defense-v2 plays 12:46 and 13:46 UTC, paired vs v63 11:5x; coordinator told to brief the loop thread.

12:20 UTC FACT: v63 (same zip as v53) first full batch 11:5x = 38-112 (25%); paired vs v53 games of 16-17 Oct it loses changed games 10-21, so rivals drift stronger within a day: pair candidates only against recent BASELINE V1 batches (11:5x onward), never old v53 batches.

14:53 UTC FACT: ranked games are NOT a judge (ranked rivals rank 54-111; defense-v2 68% ranked while failing the loop). Only the unranked paired loop decides.

15:09 UTC USER DECISION: v65 bank-v1b-clean (BASELINE V1 + BK1 bank rule) APPROVED as new online base: paired vs v63 13:46 Madrid batch 17 for / 4 against (81%) over 2 batches, gains elkring +8 interlock +5. v64 defense-v2 failed 14/27 (34%). Next candidates (micro-v1c...) pair vs latest full v65 batches. Ranked games are not a judge (rivals rank 54-111, defense-v2 68% ranked while failing).

15:43 UTC USER: loop PAUSED (hourly task trig_01UJvsLsP87W3R5rKZtcRCHD disabled, not deleted) until a candidate worth testing; v65 stays online. Resume = re-enable the task when the user uploads the next candidate; pair it vs v65's 15:46 and 16:46 Madrid batches.

18:22 UTC USER DECISION 'Juez nuevo' (card in audit thread) replaces steps 14-15 from draft-v1 on: ONE batch per candidate; pair each candidate game with the latest reference game on the same (rival, map); keep if (for-against) >= 2*sqrt(for+against) on changed results AND harm guard does not fire (gems capped 1000, pair by pair: reject if lower-higher >= 2*sqrt(lower+higher)); report both lines (+ old >57% once for draft-v1). Fail -> v65 back + one fresh v65 batch; pass -> candidate's batch becomes the reference. Script: online/judge.py CAND REF [--since ISO]. Reason: same bot flips 5-8% hour to hour, second batch adds little.
18:57 UTC USER DECISION (Javier 20:56 Madrid): local fuel limit raised to +0.1 lost turns/game vs parent (was +0.02). kill-v2 = option B (lazy ally damage reads, identical decisions to kill-v1).

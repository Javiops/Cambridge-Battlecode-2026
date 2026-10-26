---
name: cambc-strategy-md-1018
description: State of next\STRATEGY.md on the PC (audit thread owns edits): sections under 'New direction' and their status as of 2026-10-18 14:30 UTC; how the audit thread edits and syncs it
metadata:
  type: project
  modified: 2026-10-18T14:31:47.742Z
---
Source of truth: C:\Users\Javier\Cambc2026\next\STRATEGY.md (PC). Audit thread ('How Carson starts a bot') edits it with device_bash python read-modify-write + assert, backup $HOME/STRATEGY.bak-HHMM.md, then stages and copies to /mnt/project-files/next-strategy/STRATEGY.md. Bot thread never writes it.
Sections under '## New direction (Javier, 2026-10-18 10:31)', status 14:30 UTC:
- 'Online decides' bullet: local = filter only; fuel tolerance PROPOSED 14:30 (<= +0.1 fuel-lost turns/game vs parent, none with a rival in sight), user's call.
- 'No rule keyed to a map' bullet + 13:25 fact: base-v53-clean has 4 active map rules (rows, monolith, expanse, lanes capture recall), drafts off; base-v53-nofp proposed.
- Diagnosis 10:49 + BASELINE V1 baseline 11:46 UTC (25%).
- Phase 2 defence DH1-DH5: defense-v1 34%, defense-v2 local 55%, ONLINE 12:46 UTC 12 for / 27 against -> dropped, plateau.
- Second cause bank trips BK1-BK3: bank-v1 no gain; bank-v1b; correction 13:15 (base-v53-mod fuel artefact, measure on base-v53-clean); bank-v1b-clean online since 13:20 UTC (v65), first batch 9 for / 2 against.
- Micro: converting fights (approved 14:18): diagnosis (low champion dies 48% vs 11% vs top 10), MI1 finish, MI2 recall escape, MI3 target that dies soonest, MI4 short chase kept for later; Expected written; micro-v1 being refined (fuel, why finishing barely moves).
Analysis data: /mnt/project-files/analysis/micro-v63-top10-2026-10-18 (scripts reusable on any version's replays; decoder needs engine v0_0_3 wasm, a copy in the audit thread's scratchpad, origin %LOCALAPPDATA%\cambc\assets on the PC).
14:48 STRATEGY.md: micro-v1 result + micro-v1b revision (target first, close in up to 2 steps approved by Javier 14:38 card 'Acercarse', fuel cache) + guard: MI1/close-in never for our own champion below 45%; every micro version reports our recall share after going low (defense-v2 online cut it 25% -> 13% while finishing rose 12% -> 20%, from 46 v64 replays vs top 10).
14:53 STRATEGY.md: micro-v1b result (fails fuel +0.12/+0.14; finishing 20->29%, our low champions dead 36->26%) + micro-v1c proposal (drop 2-step approach, target choice back in the fight step behind fuel checks, keep target-first spell, max-hp cache, 14:48 guard); to be given to the user after the bank-v1b verdict (user asked to focus on it, 14:50).
15:08 STRATEGY.md: 'Online result of bank-v1b-clean' paragraph after the 13:15 correction: 17 for / 4 against (81%) over two batches, passes; gains elkring/interlock, top 10 flat; recommend keep as new base, next candidates paired vs v65's batches. micro-v1c block (on bank-v1b-clean only) given to the user at 15:08.
15:09 UTC USER DECISION: bank-v1b-clean (v65) APPROVED as the new base (written in STRATEGY.md); user pasting the micro-v1c block into the bot thread.
15:21 STRATEGY.md: micro-v1c result (fuel +0.07, no gain; parent 36% vs 27% between runs = v1b gain likely noise) + recommendation: park MI1 (plateau), build MI2 alone as micro-v2 on bank-v1b-clean; block given to the user.
15:33 STRATEGY.md: micro-v2 result (deaths 22->27%, gems 748->716) + 'Why micro stops here' (online replays: recall already like theirs, median 7 tiles; same walk-away behaviour we die 24% vs 5% = rival's finishing, not reproducible locally); micro parked (plateau, 4 versions), next = macro diagnosis by the audit thread. Scripts recallhow.py, stuck.py copied to analysis/micro-v63-top10-2026-10-18/scripts (run from the scratchpad micro dir, needs steps/).

---
name: cambc-duel-v1-1019
description: 2026-10-19 duel study, duel-v1/v1c (per-duel decline/commit on v76, P_DUEL), the hurt-phase / recall-channel finding, audits and Javier's decisions
metadata:
  type: project
---
STUDY 21:19 UTC (top30_diag s6): vs top 30 full-hp 1v1 duels we die 11%/kill 9%, they 3%/27% (2.79 vs 0.72 deaths/game); draft not the cause; first 3 rounds equal; we are side a in all 497 decoded games. Duels <0.85 hp ratio = 1.46 deaths/game on both pools.
21:20 UTC USER DECISION (API card): build duel-v1 on v76, judge on TOP 30.
duel-v1 = duel.h, P_DUEL 1 (0 = team-fight-v1): (me+allies within 3) hp x unit_dps over every rival within 8; <0.85 decline, >1.2 commit (not gone(), not mid-capture). Measured: early step-back saves only 18.7->14.8% -> Expected -0.3 deaths/game top 30 (under bar). Container 154 self-play: deaths 4.0 vs 5.1, kills 3.6 vs 2.5, h2h 78-76; drop mostly commit + third-party counting.
duel-v1c = + fuel guards (judge fuel_ok 30000, keep-out 40000, re-choice every 3 rounds) + no commit mid-capture; site fuel +0.12 accepted; h2h 68-86 (noise). FINAL zip bundles/duel-v1c.zip sha 0d7f7117..., AUDIT CLEARED.
21:4x UTC card to Javier, audit thread (cmsg_017gbamt2g1g8hMHRHQBc6qbQHgZr3uaPqRkDnaZCKHmwh): test duel-v1c on top 30 (recommended) or drop. Loop needs a fresh v76 top-30 draw first.
HURT PHASE CHAIN (duel_win_1019.md s4-8, top 30): hurt episodes 8.52/game each side, ours die 51% vs 23%. Ruled out or small: recall levers (shelved), damage per hit, movement direction, target switching, farm-first non-joins, leaving when a 2nd rival arrives (P_PV never re-judges a first 'stay', but leaving saves only 0.06-0.35). At EQUAL engaged numbers the top 30 out-fight us; 71-95 even. 23:07 v65 vs v72 EXACT PAIRS (31-55): P_RC_QUIET cut hurt recall starts 42->35% with no rise in hurt deaths (4.87->4.77) -> RECALL LINE CLOSED; dives on our ranged unchanged 3.35->3.18.
Ranged/dive lead from 22:07 -> [[cambc-ranged-dive-1019]].
See [[cambc-spacing-1019]], [[cambc-power-at-contact-1019]].
23:3x UTC 8f/8g:
- No ambush or dash difference; reaction equal. Once dived, at even numbers we die 3x whatever we do; shooting helps only when we outnumber.
- Their melee sits 3 tiles from the dived ranged already 10 rounds before (a standing pair near rivals, not a converge signal); ours 6-7.
- front_line (fight.h:257) is LIVE at main.cpp:3305, but its peel needs the melee within 4, so it never fires.
- Design = pairing before contact. Audit will message Javier once there is an Expected (do not send him a second message).
23:4x UTC AUDIT: design and build the formation system now. The bar only governs online; the audit sends Javier ONE message with the container result, the Expected and the bar question (do not message him separately).
formation_design_1019.md: F1 pairing, F2 ranged keeps partner within 3 when a rival is within 8, F3 melee screens, F4 shoot-not-kite when we outnumber. Expected top 30 -0.5 deaths / +0.3 kills; 71-95 -0.35 / +0.2. Build subagent running (bot/formation-v1, bundles/formation-v1.zip).
22:47 UTC (loop, via coordinator): the challenge pool is now 21 maps: the 11 old ones renamed "00..." plus 10 new "01..." maps (big_world, boss_battle, broken_curve, concentrated_wealth, corridors, elk_arena, fracture, gold_rush, hooks, islands). The local arena "site maps" are the old set only, so local site-map numbers no longer cover the online pool.
23:0x UTC v65_v72_pairs_1019.md (125 exact pairs vs 31-55): P_RC_QUIET lowered hurt recall starts (42%->35%) but hurt deaths did not rise (4.87->4.77/game). Dives unchanged (3.35->3.18). Wins 28%->36%. Recall line CLOSED; formation-v1 remains the lead.
23:3x UTC formation-v1: AUDIT NOT A PASS (mechanism flat), not online, not to Javier.
- Vision fact: ally position() throws outside own vision (main.cpp:194); only the claim bytes are team-wide.
- Camp-level pairing: theirs do NOT co-farm with melee (8% vs our 14% near rivals).
- Their ranged stops hitting camps near rivals (10.2 rounds/game vs ours 22.8; 71-95: 19.1 vs 30.5). Farm-first again = Javier's call.
- Exposure lever PARKED with the 3x-at-even-numbers residual.

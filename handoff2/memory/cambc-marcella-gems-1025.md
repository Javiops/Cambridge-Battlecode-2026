---
name: cambc-marcella-gems-1025
description: 10-25 why Marcella does 31% less camp damage than top 10 (gold/gems, not execution) and the o71 mgems piece on b27
metadata:
  type: project
  modified: 2026-10-25T09:09:07.880Z
---
Champ thread, 10-25. Source: top-10 online near summaries plus replays (81 games with Marcella), compared with b27 local (312 games, normal fuel, panel17 rivals).
- Execution matches. In r30-150 she spends about the same rounds in contact (24.5 vs 25.6) with the same median hit (45). Spike rounds (reset / 2xFocus spell) give about 50% of the damage in both.
- The gap is gold. By r150, t10 Marcella has collected 25.6 gems and earned 202 gold; ours 6.4 gems and 93 gold.
  - Shards bought: 4.8 vs 2.0 at r150, 21 vs 11 at r400.
  - Median hit in r150-400: 70 vs 52.5 (Marcella strength is 45 + 5 per strength shard).
- Where t10 gets the gems: captures of elk+gem groups (0.45 captures and about 13 gems before r150) vs ours 0.06. Her passive pays 2 gold per gem tributed.
- Piece o71_mgems.py (scratch fz/opts):
  - marcella::gem_w makes a gem worth 1 + P_MGEM% x 2 x gold_w in choose_target's value.
  - P_MGEM_CO drops the 0.7 company penalty for her on gem groups.
  - Variants: mA 100/0, mB 50/0, mC 100/1.
- Tools (scratch an/): mcamp.py (contact/hit decomposition), mbuy.py (shards by round), mgold.py, allgems.py, mcap.py (captures by group kind).
Related: [[cambc-marcella-near-1024]] [[cambc-camp-execution-1024]] [[cambc-fuelfit-1025]]
- RESULT 10-25 (commit 5b1c63d, handoff/marcella-gems on l6gm1j): probe +20 clean (0/52), 312 local vs b27 (232 W): mA 222, mB 232, mC 208 -> FAIL. Marcella gems barely move. ROOT is TEAM: before r150 t10 capture elk+gem groups 1.80/game (45.7 gems) vs b27 0.61 (11.3) = almost the whole team gem gap. Proposed to coordinator as farm-macro front.
- 10-25 ~12:00 o81 mfocus (Marcella shop: Treasure-f / +Bruiser-f first / Treasure-s) on b32, commit 5d437a0 handoff/marcella-focus: focus reaches t10 level, mob dmg r400 +8%, gold +11%, but 312 local wins 236/241/233 vs b32 244 -> neutral/negative. Probe clean. Only variant 2 offered to PC. Lesson: re-splitting half the gold doesn't help; team gem income is the bottleneck.
- 10-25 ~11:10 Marcella fight per-hit (mstep.py, every-step): spell t10 128/200 (r<150/r150-300) vs b32 117/116, basic 56 vs 48. o81 v2 brings spell to 196, v3 basic to 59, wins 241/233 vs 244 -> per-hit line CLOSED (commit 3bc6683).

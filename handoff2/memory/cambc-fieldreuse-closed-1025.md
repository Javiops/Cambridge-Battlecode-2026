---
name: cambc-fieldreuse-closed-1025
description: o65 exact distance-field reuse CLOSED 10-25 (never lands on heavy turns); SDK prices on 100x100; first-turn forward field cannot be bounded exactly on ambush/starvation
metadata:
  type: project
  modified: 2026-10-25T08:52:46.669Z
---

Farm thread, 2026-10-25 10:30 UTC. o65 (reuse step_towards' goal field and the dash-hole field under an exact rule) is CLOSED and NOT adopted; script in handoff/fuelfit-farm/opts/not-adopted/, write-up in handoff/fuelfit-farm/NOTES.md (branch claude/project-thread-jhnqzy, commits d19ef14 + e961593).

Facts:
- Exact rule verified (0 mismatches / 240k) and hits 60-72% of walking searches overall, but only on quiet solo walks. Of 87 turns >= 86k on 6 heavy far maps, 58 are camp-probe walks (goal mask rebuilt every turn) and the rest miss because a teammate stepped ahead (a tile became a wall at cached distance < D). Six versions; best (v5/v6, no copies) = heavy-turn count unchanged, +0.4-0.9k on common turns.
- SDK prices on 100x100 (x65m): bitboard copy 480, == 222, xor/and/not/shift ~390, is_empty 217, count 215, positions(n) 450+45n, is_set 61, get 64, camp_tiles 384, champion_tiles 1007, compute_to min 2.9k (+3.4/visited tile), std::vector 1250 B 1.7k. 41x41 about half. A C++ loop iteration ~10.
- fuel_ok() is a STUB returning true in b15 and above (o07): no decision reads fuel; the dash-hole search (13-20k on 100x100) always runs. It is real behaviour on ambush/starvation/fracture (used 56-82% of calls) and pure cost on big_world/lanes (reached 0/766, 0/168). Exact Chebyshev skip covers only 3-6% of calls.
- First-turn forward field of choose_target (26-31k): bounding it exactly needs the 12th-nearest group reached and every unreached group provably beyond; on ambush (12 groups, 2 statically unreachable) and starvation (12th nearest at walking distance 160-180) the needed bound covers 89-97% of the field, so no exact saving there; big_world could save ~48% but the bound must be guessed (Chebyshev underestimates walking distance by 1.5-2x on these maps) and a miss doubles the cost.

**Why:** the deterministic-bot work needs heavy turns cheaper; caches whose misses are the heavy turns cannot help, and every bitboard op costs 200-500 so a reuse test must cost ~0 on a miss.
**How to apply:** do not reopen field reuse or forward-field bounding; remaining exact first-turn wins are small (read-out loop, snapshot vs direct reads on 100x100). See [[cambc-fuel-model-1024]], [[cambc-stall-root-cause-1024]].

Delivered 10-25 (same branch): o66_readout.py EXACT (far 56/56 + near 80/80), -0.6/-0.8k per turn on 100x100; o67_rfdefer.py (defer the periodic target refresh, P_E_RETARGET=6, until the reverse fields exist; maps >= 5000 tiles only): 136/136 replays identical to b15 on the local panel, removes the 26-31k r8-r9 forward field; fracture (4331 tiles) excluded because deferring there lost 4/4 A-side games. Integrator anchors o66 on b28; o67 goes to the PC as a separate piece.

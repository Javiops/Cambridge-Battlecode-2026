---
name: cambc-fuel-1023
description: Engine 1.0.3 fuel facts measured 2026-10-23 — 100k per turn reset each turn, ~9 fuel per loop iteration (1 fuel ~ 1 wasm instruction), V18 uses 50-60k per turn
metadata:
  type: project
---

Measured 2026-10-23 12:15 UTC (farm thread, analysis/farm-route-1021/orch/RESULTS.md, patch orch/fuelcal.diff):
- Every turn starts with 99,992 fuel; nothing carries over between turns.
- A volatile do-nothing loop costs 8.8-9.0 fuel per iteration (N=1000 -> 9,011; N=3000 -> 26,511); two fuel_remaining() calls cost 9. So fuel ~ wasm instruction count.
- V18 (nightpack-v2) spends 49-60k on turns that still log a status line (log needs 18k left); r<100 is the dearest phase. Some turns already hit the floor.
- Burning 26.5k/turn (3000 iterations) = shop thread's fuel-only control: -43 wins/240 locally, 1-1 in 2 games; 90k/turn loses every game.

- Online replay bundles carry team-x.fuel: 13-byte header + 8 u64, then one u64 per champion per round = fuel used (100000 = turn cut by exhaustion, >82000 = status line suppressed). Per-version table: analysis/farm-route-1021/online-far/chain/chain_fuel.py. V17 6.0 cuts/game, V18 9.8, v133 fuelcut 2.1 (online, 15:10 UTC 10-23).
- Unlimited-fuel equivalence gate for same-decision refactors: `cambc run-batch --fuel-quantum 100000000` (global option, not a manifest option), compare finalInput/outcome/rounds per map with the base.

**Why:** fuel cost is a hidden interaction of every new rule (the process audit's "unmeasurable changes"); any candidate that adds per-turn work must be compared against a fuel-only control of the same cost.
**How to apply:** estimate a rule's fuel as its instruction count x 1; if it adds >5k/turn, run the fuel control ([[cambc-mechtest-1023]]); fuel SAVINGS in r<100 are a candidate lever (shop thread owns it). See [[cambc-game-mechanics]].
- 17:05 UTC FIGHT FUEL (V19 pack-v1w, 100 g local): fight turns with 2+ foes within 6 = 7% of turns, 38% of cuts, 17-23% end <18k (no-foe 3%); mean 67k vs 37k. Surplus = 6 ally vision scans + enemy scan (~15k) + spell_sweep 8.5k. Skipped there: path search 9% of turns, greedy 4%, casts 0.4%. Tool: tools/fuelprof/fp_fight_apply.py (buckets [fpb] + scopes 30-38), fpb_parse.py. Data online-far/fuelprof/fpb_v19_1023.txt. fuelcut-v4 = one ally scan/turn + cache foe max_health/attack_range (identity gate applies).
- 17:25 UTC fuelcut-v4 (shop, eb4e66ee = V19 + my_champs + spell_sweep early-out): 2+ foe turns <18k 22.8% -> 9.4%, cuts/g 4.38 -> 2.03, path fallbacks in big fights 9% -> 2.5%; spell_sweep early-out saved 6.5k/turn alone. Rider for chain 2 (fuel never decided fights). Data online-far/fuelprof/fpb_fuelcut4_1023.txt.

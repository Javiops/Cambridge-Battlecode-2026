# t10plan-v16 (2026-10-29): online v14 death classes; v16 = v14 + dash-range leave; local 84/140 (v14 91); v14 stays the deliverable

## 1. Online v14 (pcassets/replays_c37/v14 @ 2d30cb2d, 80 games, `MAXR=160 shop13dec.py`, death15.py / state14.py with index.json)
| class (deaths/game r30-150) | v14 online | kvvl online | v4o2 online |
|---|---|---|---|
| fled, caught by chase | 0.38 | 0.38 | 0.30 |
| fled, caught by dash | **0.24** | 0.12 | 0.23 |
| fled, caught by ranged | 0.07 | 0.14 | 0.16 |
| condition met, stayed | 0.42 | 0.60 | 0.42 |
| nolv 1 foe / late | 0.01 / 0 | 0.01 / 0.03 | 0.01 / 0 |
| camp death alone / with allies | **0.15 / 0.24** | 0.01 / 0.10 | 0.15 / 0.26 |
| total | 1.51 | 1.39 | 1.54 |
Fled-death killers v14: Vendetta 16, HoR 14, Marcella 11. state14: dead rounds r30-150 v14 77.3 vs kvvl 64.0; champion-killed 74% vs 92%;
v14 deaths with 3+ foes within 6: 61% (kvvl 48%). v14 differs from kvvl in two classes: dash catches (2x) and camp deaths (0.39 vs 0.11).

Online geometry (an/death16geo.py): in fled deaths the killer is at 1-2 tiles for the 8 rounds before death (no real escape), the v14
condition proxy was met 8-20 rounds earlier, mostly at full hp. 18/19 dash deaths had, 4-20 rounds before (median ~15), 2+ foes within 6
and an HoR/Vendetta within 4 tiles (at that round the killer itself was at 3-4 tiles in 13/18).

## 2. v14 vs kvvl games with different results (same map, rival, side; an/late16.py, decoded to r700)
v14 lost / kvvl won: anvil Sponge, breadcrumbs prism, gato Univardisty, gold_rush Sponge; v14 won / kvvl lost: breadcrumbs meow, gato Trzy.
- Not decided by r150 or r300 gems: in all 6 the r300 holdings are even or swing back; decided r300-600 by deaths and camp captures.
- v14 losses: more deaths r300-700 (anvil 7 vs rival 3; prism 5 vs 0) and fewer late captures (anvil 14 vs 29; gold_rush r600+ 1 vs 6).
- v14 wins: kvvl died late there (breadcrumbs meow kvvl 5 deaths r300-600 vs 0) while v14 kept 1-for-1 trades; late survival decides.

## 3. v16 (diff `src/t10plan-v16_vs_v14.diff`, zip `zips/e1foco-t10plan-v16.zip`)
verdict.h v14_judge: if v14 would not leave, from r>=30, 2+ foes within 6 (off their spawn), power ratio x100 < 100 (P_V16_RATIO) and a
melee foe whose dash is ready (cooldown <= 1, read from the engine) within 4 tiles (P_V16_D = dash 2 + hit 1 + move 1), the verdict is
leave (same walk home / recall as a v14 leave). One `[v16-dash]` line per firing; no init printf; draft/shop/micro untouched.
Local 70 maps x 2 vs kvvl: **84/140** (v14 91). Firings 1.83/game (r30-150 0.26); at d 4/3/2/1: 131/55/40/30. [err] lines 2224 (v14 2236).
Fires in the online situation by construction (18/19 online dash deaths meet the geometry); kvvl locally rarely brings HoR/Vendetta, so
the bench cannot show the gain and shows a 7-win cost. Not a replacement for v14 unless tested online.

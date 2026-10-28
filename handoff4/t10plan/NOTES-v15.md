# t10plan-v15 (2026-10-28): four single-lever variants on v14; none beats v14 locally; v14 stays the deliverable

## 0. Online v14 replays: not available
The task polled `claude/pc-e1-assets` (`git fetch --depth=1`) 12 times over 60 min (22:48-23:52 UTC). `pcassets/replays_c37/` still held
only kvvl / t10plan4o2 / v10 / v9c (80 each); `v14/` never appeared. **The online v14 vs v4o2 comparison (deaths r30-150, dead rounds)
and the classification of v14's online deaths are still to do.** When the folder lands: decode with `MAXR=160 python3 -I an/shop13dec.py`,
then `an/state14.py DIR --index index.json` and `an/death15.py DIR --index index.json`.

## 1. Death classes (an/death15.py; inferred from movement, no stdout online)
Leave condition proxy (v14_judge): first round in r-20..r-1 with 2+ foes within 6 (not on their spawn) or alone <50% hp with a foe within 6.
fled = after it, closer to own spawn in >= half the moves. Caught by: dash (killer moved 2-4 tiles in a round in the last 3), ranged (all
champion damage in the last 5 rounds from cheb >= 2), else chase. camp = < 50% of the hp lost in the last 10 rounds was champion damage.

| class (deaths/game r30-150) | v4o2 online (80) | v4o2 local (140) | v14 local (140) | v15d local (140) |
|---|---|---|---|---|
| fled, caught by chase | 0.30 | 0.24 | 0.23 | 0.22 |
| fled, caught by dash | 0.23 | 0.01 | 0.03 | 0.03 |
| fled, caught by ranged | 0.16 | 0.05 | 0.04 | 0.04 |
| condition met, stayed (ratio >= 0.8 / still engaged) | 0.42 | 0.31 | 0.21 | 0.21 |
| leave never possible: 1 foe only / foes late | 0.01 / 0 | 0.01 / 0 | 0.01 / 0 | 0.01 / 0 |
| camp death, alone / with allies near | 0.15 / 0.26 | 0.10 / 0.28 | 0.08 / 0.26 | 0.08 / 0.26 |
| total | 1.54 | 1.01 | 0.86 | 0.85 |
Fled-death killers online (v4o2): HoR 18, Vendetta 13, Marcella 8, Tavi 6; locally kvvl's Marcella dominates. Online dash catches are 8x local.

## 2. Variants (each on v14, gate r>=30, no init printf, one stdout line per firing; draft/shop/micro untouched). 70 maps x 2 vs kvvl.
| variant | lever | firings/game r30-150 (whole game) | wins |
|---|---|---|---|
| v14 | - | - | **91/140** |
| v15a | leave at 1 foe within 6 + a 2nd approaching within 10, ratio over all < 0.8 (`[v15-early]`) | 1.56 (26.3) | 79 |
| v15b | a v14 leave walks to an ally farther from the foes than us and nearer than the spawn (`[v15-ally]`) | 0 (0.04) | 89 (= v14, rule dormant) |
| v15c | P_V14_RATIO 80 -> 110 (the "stayed" class) | - | 81 |
| v15d | alone, before the first hit: afford = hp + 20% max hp (was +60%) (`[v15-reserve]`) | 0.41 (5.4) | 86; deaths r30-150 0.85, dead 43.0 (v14 0.86 / 43.1) |

Reading: the largest local classes (stayed 0.21, chase 0.23, camp-with-allies 0.26) do not yield to these levers: leaving more (a, c) costs
more than the deaths it saves; v15b's geometry almost never holds (allies are behind the foe or past the spawn); v15d drops groups but not
deaths. Online the classes that differ most from local are **dash catches (0.23 vs 0.03) and stayed (0.42)**; the local kvvl bench cannot
show those, so the next step needs the online v14 replays. Deliverable unchanged: **v14** (`zips/e1foco-t10plan-v14.zip`).
Files: `src/t10plan-v15{a,b,c,d}_vs_v14.diff`, `zips/e1foco-t10plan-v15{a,b,c,d}.zip` (SHA256SUMS), `an/death15.py`.

# t10plan-v17 (2026-10-29, cloud): camp deaths are the v16 vs kvvl death gap; v17 = v16 + full camp-damage model (P_INC_PCT 100)

Zip `zips/e1foco-t10plan-v17.zip` sha256 `875c8e63aa68d02105dce670df2ceb8ff6b18b28a383cd3d0ad0e67b8f9cb09c`, diff `src/t10plan-v17_vs_v16.diff`
(one line: `P_INC_PCT 50 -> 100`, the value kvvl uses). No new printf, no init change.

## 1. Online c37 deaths r30-150 (pcassets/replays_c37 @ 59349b78, `MAXR=300 an/shop13dec.py`, `an/death15.py --index`)
| class (per game) | v16 (75) | kvvl (80) | v14 (80) |
|---|---|---|---|
| fled-chase | 0.40 | 0.38 | 0.38 |
| fled-dash | 0.31 | 0.12 | 0.24 |
| fled-ranged | 0.11 | 0.14 | 0.07 |
| stayed | 0.36 | 0.60 | 0.42 |
| camp alone / with allies | **0.16 / 0.21** | 0.01 / 0.10 | 0.15 / 0.24 |
| total | 1.56 | 1.39 | 1.51 |
The v16 dash rule did not cut dash deaths online (0.24 -> 0.31). The steady gap since v4o2 is camp deaths (+0.26/game).

`an/camp17.py` (each camp death): 28 v16 camp deaths, most at FULL hp when the engagement starts, dead 7-9 rounds later, 0-1
co-hitters, no foe within 6, in groups of 5-20k hp (lost_world 20480, shortcut 10080, big_world 6510). Per-round trace: the champion
deals 45-90/round and loses 150-240/round. kvvl has 9 such deaths in 80 games.

## 2. Root cause
Squad admission `squad_needed()` models the incoming camp damage as `P_INC_PCT` % of strength x clear time. e1foco (o100) set it to 50
("measured 46-63%"); kvvl keeps 100. With 50, one or two champions are sent into groups that out-damage them 2-4x.

## 3. Tried here (local 70 maps x 2 vs kvvl; v16 = 84/140; local r30-150 deaths from the 70 side-a games, `death15.py`)
| bot | vs kvvl | deaths r30-150 | camp deaths |
|---|---|---|---|
| v16 | 84 | 0.83 | 0.41 |
| v17a: race rule (bail when we die before the group, engagement-average rates) | 87 | 0.83 | 0.40 |
| v17c: race rule with last-2-round loss rate | 73 | 0.82 | 0.38 |
| **v17 (= v17d): P_INC_PCT 100** | **92** | **0.57** | **0.16** |
| v17e: v17 + the squad check also when joining a woken group | 88 | 0.59 (44 games) | 0.18 |
The race rule fires at 60-70% hp and the champion still dies: an awake group chases and out-damages a fleeing champion
(`an/racechk.py`). Bailing out does not work; the only fix is not to enter. v17e adds nothing over v17.

## 4. Next (v18)
Dash deaths online (0.31 vs kvvl 0.12): v16's dash leave fires but the champion still gets caught; same lesson as the camps:
leaving late does not work.

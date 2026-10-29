# t10plan-v18 (2026-10-29, cloud): v17 + concede a 3-rival pack (P_DANGER 4 -> 3)

## 1. v17 online (c37, pcassets/replays_c37/v17 @ d9531d9a, 80 games; verdict 10/80 vs kvvl 9, vs v16 7 vs 9 on 75)
Camp deaths r30-150 dropped as built: 0.14/game (v16 0.37, kvvl 0.11); all deaths r30-150 1.23 (v16 1.56), r151-300 1.49 (1.60).
Fewer deaths did not add gems: captured gem value r0-300 per game v17 139, v16 135, kvvl 140; rivals 218-235 (`an/gemsel.py`).

## 2. Where the gem gap is (`an/gem40b.py`, group gems >= 40, r0-300, zones by spawn distance +-3)
| captures/game | us (v17) | rival |
|---|---|---|
| 40+ gems, own half | 0.25 | 0.40 |
| 40+ gems, centre | 0.29 | 0.88 |
| 40+ gems, other half | 0.01 | 0 |
Rivals take the centre rich groups with 3-5 hitters, uncontested (0.72 of 0.88), at any time r0-300 (`an/centre.py`).
In the 40 rounds before each such rival capture our champions spend 24.8 champion-rounds/game within 8 of the group:
17.6 with a foe within 6 and not hitting, 6.5 idle, 0.7 hitting it, 0.9 hitting another group (`an/centre2.py`).

## 3. v18
`P_DANGER 3`: the existing danger rule (a pack of P_DANGER+ foes within 4 of each other; groups within P_DANGER_R 5 of it are skipped
by choose_target for P_DANGER_T 45 rounds and the spot is broadcast) now fires on a 3-pack. We concede the centre group we lose anyway
and spend those rounds on other groups. Zip `zips/e1foco-t10plan-v18.zip`, diff `src/t10plan-v18_vs_v17.diff`.
Local: 90/140 vs kvvl (v17 92), 67/140 vs v17. Local rivals rarely pack, so only online can judge it.

## 4. v18 online: 9/80 (kvvl 9, net 0); vs v17 one changed game. A 3-pack within 4 of each other is rare online: the rule barely fires.

## 5. v19 = v17 + P_NEED_CAP 3
The centre 40+ groups we do take go mostly to 1-2 of ours (`an/centre.py`: hitters_us 1 in 0.14 of 0.29/game); rivals use 3-5.
A group may now "need" 3 champions (rally until 3 are there) instead of being capped at 2. Local 88/140 vs kvvl (v17 92; local deaths
r30-150 0.56, camp 0.13). Zip `zips/e1foco-t10plan-v19.zip`, diff `src/t10plan-v19_vs_v17.diff`.

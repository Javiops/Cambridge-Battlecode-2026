# Strategy card from map features, checked against the #1 (Mite) on all 9 maps

15-10-2026. The goal was a rule set that reads only the map and gives the same strategy Mite plays, on all 9 official maps. Result: **9/9 on every part of the card.** The camp-set part is fragile, though (see "How much to trust it").

## The card (what the evaluator computes at game start)

| part | rule (map features only) | vs Mite |
|---|---|---|
| Fight or farm | spawn-to-spawn path `d` ≤ 45 means fight, otherwise farm | 9/9 |
| Draft | team size plus `sa` = home to the nearest altar. If `sa` ≤ 8 (altar next to home), take casters. 3 picks: Ren, Stellar, Cassi (else Varg, Ryth, Cassi). 4 picks: Varg, Ryth, Cassi, Ren. 5 picks: Varg, Stellar, Cassi, Tavi, Ren (Ryth instead of Tavi when `sa` > 8) | 9/9 (Mite plays the same draft in ≥ 90% of games per map) |
| Banking | after a capture, **recall if home is closer to an altar than the camp is** (`home->altar < camp->altar`); start it on the capture tile. A map is a "recall map" when half or more of its farm camps qualify | 9/9 on the majority mode; 81% of 1,237 single captures |
| Farm camps | score each camp `gems / (travel + hp/150 + 5 + bank trip + damage taken)`, where damage taken = `3 × strength × kill time × (distance from home + 5) / 900`. Keep only camps clearly on our side: farm maps ≥ 0.1·d closer to us, fight maps at most 2 closer to them. Add camps greedily. Stop below 0.55 × (fight map) or 0.25 × (farm map) the median score of the `nch` best camps | 9/9: every camp Mite takes ≥ 3 times a game is in, no camp it takes < 1 time is in |
| Order inside the set | go to the nearest camp that is up, with no fixed loop; recall is the reset | measured before: 38-41% top-1 vs 6% random |

On fight maps "travel" is the detour from the commute to the contested altar, not the distance from home.

## Per map

| map | d / mode | sa | draft | banking (share of set camps that recall / Mite's actual recall share) | farm set (all of Mite's core camps found) |
|---|---|---|---|---|---|
| collision | 34 fight | 21 | Varg Ryth Cassi | walk (0 / 21%) | 5 wolves, 5/5 core |
| corners | 40 fight | 19 | Varg Stellar Cassi Ryth Ren | walk (0 / 20%) | the 4 gem clusters at the centre altar, 4/4 |
| elkring | 31 fight | 23 | Varg Stellar Cassi Ryth Ren | walk (0 / 8%) | all 5 elks, 5/5 |
| interlock | 41 fight | 17 | Varg Ryth Cassi Ren | walk (0 / 16%) | 3 wolves + 3-gem cluster, 4/4 |
| packs | 26 fight | 3 | Ren Stellar Cassi | recall (100% / 64%) | 2 gold/gem packs + near wolves, 3/3 |
| expanse | 85 farm | 7 | Ren Stellar Cassi | recall (50% / 53%) | 3 gem pairs + 3 wolves, 6/6 |
| lanes | 81 farm | 7 | Varg Stellar Cassi Tavi Ren | walk, mixed (33% / 33%) | 6 gems on the altar lane + 3 elks, 6/6 |
| monolith | 49 farm | 25 | Varg Stellar Cassi Ryth Ren | walk (0 / 10%) | 7 wolf/elk camps, 5/5 |
| rows | 73 farm | 10 | Varg Ryth Cassi Ren | recall (100% / 79%) | the 3 own wolf packs, 3/3 |

The recalls on fight maps (8-21%) are retreats and heals, not banking.

## How much to trust it

- **Fight/farm, banking and draft are simple rules with wide gaps.** Fight paths are 26-41 and farm paths 49-85. Recall maps have `sa` 3-10 and walk maps 17-25.
  - Caveat on the draft: only 3 maps have an altar next to home, and there is no 4-pick map like that, so the 4-pick near-altar draft is a guess.
- **The camp set is 9/9 for only 232 of 108,864 setting combinations.** Most one-step changes drop it to 8/9. The settings that matter are the damage weight (2.5-4) and the two cut-offs; the others don't matter.
- **Leave one map out** (fit on 8 maps, predict the 9th) gets the held-out camp set right on:
  - collision, elkring, monolith, packs and rows, every time;
  - corners and lanes, half the time;
  - expanse, 10% of the time;
  - interlock, never.
  - So on a truly new map, expect about 6 of 9 to match exactly. The misses are one extra or one missing borderline camp, usually an elk.
- **What the fit taught:**
  - Mite avoids camps that hurt. Elks hit 3 times harder than a wolf, and the cost of walking home to heal grows with distance. Without the damage term no setting gets past 7/9.
  - It farms fewer camps on fight maps, keeping champions for the fight. One cut-off for both kinds of map cannot fit corners and rows together.

## Generated (unseen) maps

The card runs on all 60 new generated maps (`data/gen_cards.json`): 48 farm and 12 fight, 17 recall maps, farm sets of 0-9 camps (median 3). The small sets are real: these maps have only 2-3 camps on each side. One map gets no farm set at all, because every camp is closer to the enemy.

## Files

- `scripts/card.py MAP.json`: prints the card for any map (JSON from `tools/mapjson.js`).
- `scripts/strategy5.py`: camp-set model and grid search. `scripts/lomo5.py`: leave-one-map-out check.
- `data/deposit_rows.json`: every Mite capture and what it did next. `data/mite_caps.json`: Mite's captures per camp per game.

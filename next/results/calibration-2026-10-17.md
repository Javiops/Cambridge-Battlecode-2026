# League report (screen maps)

Generated 2026-10-17 20:23 UTC · panel v1 · champion `starter-v1` · 300 games on 12 maps

## Leaderboard

Rating on the Elo scale (mean 1500), fitted on all games at once; the range is a 90% bootstrap over maps.

| # | version | rating | 90% range | games | score | changelog |
|---|---|---|---|---|---|---|
| 1 | `calib-seed-v1` | 1838 | 1770–1923 | 96 | 76% | calib-seed-v1: starter with a different random seed. Same strength by design: its gap to starter-v1 is the noise floor. |
| 2 | `calib-skip10-v1` | 1830 | 1770–1918 | 96 | 75% | calib-skip10-v1: starter that skips every 10th round. A known small handicap: the league should rank it below starter-v1. |
| 3 | `starter-v1` | 1777 | 1719–1857 | 96 | 69% | starter-v1: the SDK C++ starter bot, unchanged (cambc 2.2.5). The weak reference. |
| 4 | `calib-skip2-v1` | 1384 | 1292–1436 | 96 | 30% | calib-skip2-v1: starter that acts only on even rounds. A known large handicap. |
| 5 | `dummy-v1` | 672 | 601–704 | 96 | 0% | dummy-v1: the floor of the league. Drafts the first free champion, then never acts. |

## Win matrix

Score of the row against the column, both sides, all maps.

| row \ col | `calib-seed-v1` | `calib-skip10-v1` | `starter-v1` | `calib-skip2-v1` | `dummy-v1` |
|---|---|---|---|---|---|
| `calib-seed-v1` | · | 58% (24) | 50% (24) | 96% (24) | 100% (24) |
| `calib-skip10-v1` | 42% (24) | · | 58% (24) | 100% (24) | 100% (24) |
| `starter-v1` | 50% (24) | 42% (24) | · | 83% (24) | 100% (24) |
| `calib-skip2-v1` | 4% (24) | 0% (24) | 17% (24) | · | 100% (24) |
| `dummy-v1` | 0% (24) | 0% (24) | 0% (24) | 0% (24) | · |

## How each version plays

Averages over that version's games in this report. Gems are banked gems; r1000 is the median snapshot round where it reached 1000 gems (games where it did).

| version | gems r500 | r1000 | final gems | reached 1000 | deaths | kills | gold | faults | fuel lost | camps cleared | distinct camps | wards |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `calib-seed-v1` | 268 | 1204 | 853 | 66% | 29.8 | 2.6 | 4594 | 0 | 0.0 | 40.9 | 6.1 | 0.0 |
| `calib-skip10-v1` | 234 | 1424 | 840 | 64% | 32.9 | 2.3 | 4571 | 0 | 0.0 | 40.7 | 6.1 | 0.0 |
| `starter-v1` | 241 | 1423 | 824 | 59% | 29.9 | 2.7 | 4493 | 0 | 0.0 | 39.1 | 6.1 | 0.0 |
| `calib-skip2-v1` | 123 | 1915 | 510 | 9% | 34.6 | 1.2 | 2936 | 0 | 0.8 | 29.3 | 4.3 | 0.0 |
| `dummy-v1` | 0 | – | 0 | 0% | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Seat split and symmetry

Carson: a bot that wins from one side and loses from the other has an edge from the start position, not a strategy.

| version | score as side A | score as side B | gap |
|---|---|---|---|
| `calib-seed-v1` | 67% | 85% | -19 |
| `calib-skip10-v1` | 65% | 85% | -21 |
| `starter-v1` | 54% | 83% | -29 |
| `calib-skip2-v1` | 25% | 35% | -10 |
| `dummy-v1` | 0% | 0% | +0 |

Mirror games (a version against itself): side A wins this share. Far from 50% means the maps or the bot favour one side.

- `calib-seed-v1`: side A 25% of 12
- `calib-skip10-v1`: side A 33% of 12
- `calib-skip2-v1`: side A 25% of 12
- `dummy-v1`: side A 0% of 12
- `starter-v1`: side A 17% of 12

## Strategy coverage

What each version actually does. If one draft or one item takes almost every game, the strategy has collapsed (Carson's kaggriculture bot bought the same land in every game and he saw it too late).

| version | distinct drafts | top drafts | top items |
|---|---|---|---|
| `calib-seed-v1` | 23 | Marcella, Prism, Cassi, Issac, Tavi, Stellar (8%); Varg, Stellar, Vendetta, Ryth, Prism (4%) | Power Shard of Health ×5221, Power Shard of Strength ×3135, Power Shard of Focus ×2766 |
| `calib-skip10-v1` | 23 | Ren, Vesper Vale, Stellar, Ryth, Willow (8%); Tavi, Marcella, Vesper Vale, Vendetta, Ryth (4%) | Power Shard of Focus ×4756, Power Shard of Strength ×4168, Power Shard of Health ×2225 |
| `starter-v1` | 23 | Ren, Vesper Vale, Stellar, Ryth, Willow (8%); Tavi, Marcella, Vesper Vale, Vendetta, Ryth (4%) | Power Shard of Focus ×4692, Power Shard of Strength ×3988, Power Shard of Health ×2534 |
| `calib-skip2-v1` | 23 | Ren, Vesper Vale, Stellar, Ryth, Willow (8%); Tavi, Marcella, Vesper Vale, Vendetta, Ryth (4%) | Power Shard of Focus ×3405, Power Shard of Strength ×2532, Power Shard of Health ×1391 |
| `dummy-v1` | 3 | Ryth, Vesper Vale, Vendetta, Cassi, Issac, Stellar (58%); Ryth, Vesper Vale, Vendetta (33%) |  |

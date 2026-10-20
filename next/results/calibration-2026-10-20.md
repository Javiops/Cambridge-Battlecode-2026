# League report (screen maps)

Generated 2026-10-20 12:14 UTC · panel v3 · champion `starter-week2-v1` · 99 games on 11 maps

## Leaderboard

Rating on the Elo scale (mean 1500), fitted on all games at once; the range is a 90% bootstrap over maps.

| # | version | rating | 90% range | games | score | changelog |
|---|---|---|---|---|---|---|
| 1 | `calib-seed-week2-v1` | 1813 | 1749–1902 | 44 | 82% | calib-seed-v1: starter with a different random seed. Same strength by design: its gap to starter-v1 is the noise floor. |
| 2 | `starter-week2-v1` | 1719 | 1631–1780 | 44 | 68% | starter-v1: the SDK C++ starter bot, unchanged (cambc 2.2.5). The weak reference. |
| 3 | `dummy-week2-v1` | 968 | 935–972 | 44 | 0% | dummy-v1: the floor of the league. Drafts the first free champion, then never acts. |

**Noise band:** `starter-week2-v1` and `calib-seed-week2-v1` have the same strength by construction. Here they differ by **94 points** and score 36% head to head over 22 games. A gap between two versions smaller than this is not a result.

## Win matrix

Score of the row against the column, both sides, all maps.

| row \ col | `calib-seed-week2-v1` | `starter-week2-v1` | `dummy-week2-v1` |
|---|---|---|---|
| `calib-seed-week2-v1` | · | 64% (22) | 100% (22) |
| `starter-week2-v1` | 36% (22) | · | 100% (22) |
| `dummy-week2-v1` | 0% (22) | 0% (22) | · |

## How each version plays

Averages over that version's games in this report. Gems are banked gems; r1000 is the median snapshot round where it reached 1000 gems (games where it did).

| version | gems r500 | r1000 | final gems | reached 1000 | deaths | kills | gold | faults | fuel lost | camps cleared | distinct camps | wards |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `calib-seed-week2-v1` | 93 | 1821 | 502 | 11% | 46.3 | 3.0 | 4509 | 0 | 0.0 | 62.8 | 6.7 | 0.0 |
| `starter-week2-v1` | 86 | 1896 | 436 | 2% | 42.3 | 2.9 | 4159 | 0 | 0.0 | 56.1 | 6.2 | 0.0 |
| `dummy-week2-v1` | 0 | – | 0 | 0% | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Seat split and symmetry

Carson: a bot that wins from one side and loses from the other has an edge from the start position, not a strategy.

| version | score as side A | score as side B | gap |
|---|---|---|---|
| `calib-seed-week2-v1` | 73% | 91% | -18 |
| `starter-week2-v1` | 59% | 77% | -18 |
| `dummy-week2-v1` | 0% | 0% | +0 |

Mirror games (a version against itself): side A wins this share. Far from 50% means the maps or the bot favour one side.

- `calib-seed-week2-v1`: side A 27% of 11
- `dummy-week2-v1`: side A 0% of 11
- `starter-week2-v1`: side A 0% of 11

## Strategy coverage

What each version actually does. If one draft or one item takes almost every game, the strategy has collapsed (Carson's kaggriculture bot bought the same land in every game and he saw it too late).

| version | distinct drafts | top drafts | top items |
|---|---|---|---|
| `calib-seed-week2-v1` | 21 | Marcella, Prism, Cassi, Issac, Tavi, Stellar (9%); Varg, Stellar, Vendetta, Ryth, Prism (5%) | Power Shard of Health ×2213, Power Shard of Focus ×1509, Power Shard of Strength ×1500 |
| `starter-week2-v1` | 21 | Ren, Vesper Vale, Stellar, Ryth, Willow (9%); Tavi, Marcella, Vesper Vale, Vendetta, Ryth (5%) | Power Shard of Focus ×1904, Power Shard of Strength ×1797, Power Shard of Health ×1231 |
| `dummy-week2-v1` | 3 | Ryth, Vesper Vale, Vendetta, Cassi, Issac, Stellar (73%); Ryth, Vesper Vale, Vendetta (18%) |  |

## Best rating per league run

Carson's stopping rule: when the best rating gains less than 20 points for two runs in a row, the current idea has plateaued; change direction.

| run | best version | rating | gain |
|---|---|---|---|
| 10-20 12:14 | `calib-seed-week2-v1` | 1813 |  |

## Lineage

Each version and the version it was copied from, with its changelog line.

```
calib-seed-week2-v1  (calib-seed-v1: starter with a different random seed. Same strength by design: its gap to s)
dummy-week2-v1  (dummy-v1: the floor of the league. Drafts the first free champion, then never acts.)
starter-week2-v1  (starter-v1: the SDK C++ starter bot, unchanged (cambc 2.2.5). The weak reference.)
```

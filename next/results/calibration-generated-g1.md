# Stage 1 calibration (generated screen maps)

Generated 2026-10-20 14:26 UTC · panel v4 · champion `starter-week2-v1` · 2500 games on 100 maps

## Leaderboard

Rating on the Elo scale (mean 1500), fitted on all games at once; the range is a 90% bootstrap over maps.

| # | version | rating | 90% range | games | score | changelog |
|---|---|---|---|---|---|---|
| 1 | `starter-week2-v1` | 1828 | 1786–1918 | 800 | 75% | starter-v1: the SDK C++ starter bot, unchanged (cambc 2.2.5). The weak reference. |
| 2 | `calib-seed-week2-v1` | 1812 | 1758–1906 | 800 | 73% | calib-seed-v1: starter with a different random seed. Same strength by design: its gap to starter-v1 is the noise floor. |
| 3 | `calib-skip10-week2-v1` | 1790 | 1758–1868 | 800 | 71% | calib-skip10-v1: starter that skips every 10th round. A known small handicap: the league should rank it below starter-v1. |
| 4 | `calib-skip2-week2-v1` | 1384 | 1335–1463 | 800 | 30% | calib-skip2-v1: starter that acts only on even rounds. A known large handicap. |
| 5 | `dummy-week2-v1` | 687 | 369–806 | 800 | 0% | dummy-v1: the floor of the league. Drafts the first free champion, then never acts. |

**Noise band:** `starter-week2-v1` and `calib-seed-week2-v1` have the same strength by construction. Here they differ by **16 points** and score 50% head to head over 200 games. A gap between two versions smaller than this is not a result.

## Win matrix

Score of the row against the column, both sides, all maps.

| row \ col | `starter-week2-v1` | `calib-seed-week2-v1` | `calib-skip10-week2-v1` | `calib-skip2-week2-v1` | `dummy-week2-v1` |
|---|---|---|---|---|---|
| `starter-week2-v1` | · | 50% (200) | 56% (200) | 94% (200) | 100% (200) |
| `calib-seed-week2-v1` | 50% (200) | · | 54% (200) | 90% (200) | 99% (200) |
| `calib-skip10-week2-v1` | 44% (200) | 46% (200) | · | 93% (200) | 100% (200) |
| `calib-skip2-week2-v1` | 6% (200) | 10% (200) | 7% (200) | · | 99% (200) |
| `dummy-week2-v1` | 0% (200) | 1% (200) | 0% (200) | 1% (200) | · |

## How each version plays

Averages over that version's games in this report. Gems are banked gems; r1000 is the median snapshot round where it reached 1000 gems (games where it did).

| version | gems r500 | r1000 | final gems | reached 1000 | deaths | kills | gold | faults | fuel lost | camps cleared | distinct camps | wards |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `starter-week2-v1` | 87 | 1858 | 469 | 2% | 64.6 | 5.4 | 3552 | 0 | 0.0 | 86.8 | 8.3 | 0.0 |
| `calib-seed-week2-v1` | 79 | 1860 | 449 | 2% | 58.7 | 6.8 | 3653 | 0 | 0.0 | 82.6 | 8.3 | 0.0 |
| `calib-skip10-week2-v1` | 80 | 1786 | 434 | 1% | 66.0 | 4.9 | 3316 | 0 | 0.0 | 82.7 | 8.0 | 0.0 |
| `calib-skip2-week2-v1` | 44 | – | 219 | 0% | 64.5 | 2.0 | 1693 | 0 | 0.0 | 49.5 | 6.0 | 0.0 |
| `dummy-week2-v1` | 0 | – | 0 | 0% | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Seat split and symmetry

Carson: a bot that wins from one side and loses from the other has an edge from the start position, not a strategy.

| version | score as side A | score as side B | gap |
|---|---|---|---|
| `starter-week2-v1` | 66% | 85% | -19 |
| `calib-seed-week2-v1` | 64% | 83% | -19 |
| `calib-skip10-week2-v1` | 62% | 79% | -16 |
| `calib-skip2-week2-v1` | 27% | 34% | -7 |
| `dummy-week2-v1` | 0% | 1% | -1 |

Mirror games (a version against itself): side A wins this share. Far from 50% means the maps or the bot favour one side.

- `calib-seed-week2-v1`: side A 36% of 100
- `calib-skip10-week2-v1`: side A 42% of 100
- `calib-skip2-week2-v1`: side A 47% of 100
- `dummy-week2-v1`: side A 0% of 100
- `starter-week2-v1`: side A 30% of 100

## Strategy coverage

What each version actually does. If one draft or one item takes almost every game, the strategy has collapsed (Carson's kaggriculture bot bought the same land in every game and he saw it too late).

| version | distinct drafts | top drafts | top items |
|---|---|---|---|
| `starter-week2-v1` | 73 | Vesper Vale, Varg, Ren, Cassi, Issac (18%); Vesper Vale, Varg, Ren, Cassi, Issac, Prism (16%) | Power Shard of Strength ×47786, Power Shard of Health ×19854, Power Shard of Focus ×17590 |
| `calib-seed-week2-v1` | 71 | Vesper Vale, Prism, Stellar, Vendetta (18%); Vesper Vale, Prism, Stellar, Vendetta, Varg (16%) | Power Shard of Strength ×53428, Power Shard of Focus ×17000, Power Shard of Health ×15854 |
| `calib-skip10-week2-v1` | 73 | Vesper Vale, Varg, Ren, Cassi, Issac (18%); Vesper Vale, Varg, Ren, Cassi, Issac, Prism (16%) | Power Shard of Strength ×45239, Power Shard of Health ×17813, Power Shard of Focus ×16284 |
| `calib-skip2-week2-v1` | 73 | Vesper Vale, Varg, Ren, Cassi, Issac (18%); Vesper Vale, Varg, Ren, Cassi, Issac, Prism (16%) | Power Shard of Strength ×22110, Power Shard of Health ×9181, Power Shard of Focus ×9086 |
| `dummy-week2-v1` | 3 | Ryth, Vesper Vale, Vendetta, Cassi, Issac (37%); Ryth, Vesper Vale, Vendetta, Cassi, Issac, Stellar (32%) |  |

## Best rating per league run

Carson's stopping rule: when the best rating gains less than 20 points for two runs in a row, the current idea has plateaued; change direction.

| run | best version | rating | gain |
|---|---|---|---|
| 10-20 14:26 | `starter-week2-v1` | 1828 |  |

## Lineage

Each version and the version it was copied from, with its changelog line.

```
calib-seed-week2-v1  (calib-seed-v1: starter with a different random seed. Same strength by design: its gap to s)
calib-skip10-week2-v1  (calib-skip10-v1: starter that skips every 10th round. A known small handicap: the league s)
calib-skip2-week2-v1  (calib-skip2-v1: starter that acts only on even rounds. A known large handicap.)
dummy-week2-v1  (dummy-v1: the floor of the league. Drafts the first free champion, then never acts.)
starter-week2-v1  (starter-v1: the SDK C++ starter bot, unchanged (cambc 2.2.5). The weak reference.)
```

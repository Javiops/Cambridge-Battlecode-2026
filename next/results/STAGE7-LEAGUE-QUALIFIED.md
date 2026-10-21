# League report (screen maps)

Generated 2026-10-20 19:00 UTC · panel v4 · champion `starter-week2-v1` · 3000 games on 100 maps

## Leaderboard

Rating on the Elo scale (mean 1500), fitted on all games at once; the range is a 90% bootstrap over maps.

| # | version | rating | 90% range | games | score | changelog |
|---|---|---|---|---|---|---|
| 1 | `ppo-league-v12` | 2593 | 2429–2533 | 1000 | 100% | ppo-league-v12: keep the cooperative budget throw out of line; expect reproducible source-bundle WASM. |
| 2 | `starter-week2-v1` | 1608 | 1599–1710 | 1000 | 60% | starter-v1: the SDK C++ starter bot, unchanged (cambc 2.2.5). The weak reference. |
| 3 | `calib-seed-week2-v1` | 1593 | 1571–1697 | 1000 | 59% | calib-seed-v1: starter with a different random seed. Same strength by design: its gap to starter-v1 is the noise floor. |
| 4 | `calib-skip10-week2-v1` | 1571 | 1570–1660 | 1000 | 56% | calib-skip10-v1: starter that skips every 10th round. A known small handicap: the league should rank it below starter-v1. |
| 5 | `calib-skip2-week2-v1` | 1166 | 1140–1259 | 1000 | 24% | calib-skip2-v1: starter that acts only on even rounds. A known large handicap. |
| 6 | `dummy-week2-v1` | 469 | 164–621 | 1000 | 0% | dummy-v1: the floor of the league. Drafts the first free champion, then never acts. |

**Noise band:** `starter-week2-v1` and `calib-seed-week2-v1` have the same strength by construction. Here they differ by **16 points** and score 50% head to head over 200 games. A gap between two versions smaller than this is not a result.

## Win matrix

Score of the row against the column, both sides, all maps.

| row \ col | `ppo-league-v12` | `starter-week2-v1` | `calib-seed-week2-v1` | `calib-skip10-week2-v1` | `calib-skip2-week2-v1` | `dummy-week2-v1` |
|---|---|---|---|---|---|---|
| `ppo-league-v12` | · | 100% (200) | 100% (200) | 100% (200) | 100% (200) | 100% (200) |
| `starter-week2-v1` | 0% (200) | · | 50% (200) | 56% (200) | 94% (200) | 100% (200) |
| `calib-seed-week2-v1` | 0% (200) | 50% (200) | · | 54% (200) | 90% (200) | 99% (200) |
| `calib-skip10-week2-v1` | 0% (200) | 44% (200) | 46% (200) | · | 93% (200) | 100% (200) |
| `calib-skip2-week2-v1` | 0% (200) | 6% (200) | 10% (200) | 7% (200) | · | 99% (200) |
| `dummy-week2-v1` | 0% (200) | 0% (200) | 1% (200) | 0% (200) | 1% (200) | · |

## How each version plays

Averages over that version's games in this report. Gems are banked gems; r1000 is the median snapshot round where it reached 1000 gems (games where it did).

| version | gems r500 | r1000 | final gems | reached 1000 | deaths | kills | gold | faults | fuel lost | camps cleared | distinct camps | wards |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `ppo-league-v12` | 262 | 1269 | 995 | 93% | 10.9 | 11.4 | 5888 | 0 | 0.0 | 115.7 | 13.1 | 0.0 |
| `starter-week2-v1` | 75 | 1858 | 383 | 1% | 60.5 | 4.4 | 3037 | 0 | 0.0 | 75.1 | 7.6 | 0.0 |
| `calib-seed-week2-v1` | 69 | 1860 | 366 | 2% | 54.8 | 5.5 | 3103 | 0 | 0.0 | 71.2 | 7.5 | 0.0 |
| `calib-skip10-week2-v1` | 70 | 1786 | 355 | 1% | 61.9 | 4.0 | 2844 | 0 | 0.0 | 71.7 | 7.3 | 0.0 |
| `calib-skip2-week2-v1` | 38 | – | 179 | 0% | 60.3 | 1.6 | 1480 | 0 | 0.0 | 43.8 | 5.5 | 0.0 |
| `dummy-week2-v1` | 0 | – | 0 | 0% | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Seat split and symmetry

Carson: a bot that wins from one side and loses from the other has an edge from the start position, not a strategy.

| version | score as side A | score as side B | gap |
|---|---|---|---|
| `ppo-league-v12` | 100% | 100% | +0 |
| `starter-week2-v1` | 52% | 68% | -15 |
| `calib-seed-week2-v1` | 51% | 66% | -15 |
| `calib-skip10-week2-v1` | 50% | 63% | -13 |
| `calib-skip2-week2-v1` | 22% | 27% | -6 |
| `dummy-week2-v1` | 0% | 1% | -1 |

## Strategy coverage

What each version actually does. If one draft or one item takes almost every game, the strategy has collapsed (Carson's kaggriculture bot bought the same land in every game and he saw it too late).

| version | distinct drafts | top drafts | top items |
|---|---|---|---|
| `ppo-league-v12` | 3 | Cassi, Issac, Ren, Stellar, Tavi (37%); Ryth, Stellar, Prism, Ren, Tavi (32%) | Power Shard of Focus ×111093, Power Shard of Strength ×31596, Durability Shard of Health ×18963 |
| `starter-week2-v1` | 73 | Vesper Vale, Varg, Ren, Cassi, Issac (18%); Vesper Vale, Varg, Ren, Cassi, Issac, Prism (16%) | Power Shard of Strength ×50626, Power Shard of Health ×21190, Power Shard of Focus ×19036 |
| `calib-seed-week2-v1` | 71 | Vesper Vale, Prism, Stellar, Vendetta (18%); Vesper Vale, Prism, Stellar, Vendetta, Varg (16%) | Power Shard of Strength ×56053, Power Shard of Focus ×18463, Power Shard of Health ×16950 |
| `calib-skip10-week2-v1` | 73 | Vesper Vale, Varg, Ren, Cassi, Issac (18%); Vesper Vale, Varg, Ren, Cassi, Issac, Prism (16%) | Power Shard of Strength ×48042, Power Shard of Health ×19134, Power Shard of Focus ×17684 |
| `calib-skip2-week2-v1` | 73 | Vesper Vale, Varg, Ren, Cassi, Issac (18%); Vesper Vale, Varg, Ren, Cassi, Issac, Prism (16%) | Power Shard of Strength ×24004, Power Shard of Health ×10015, Power Shard of Focus ×9874 |
| `dummy-week2-v1` | 3 | Ryth, Vesper Vale, Vendetta, Cassi, Issac (37%); Ryth, Vesper Vale, Vendetta, Cassi, Issac, Stellar (32%) |  |

## Best rating per league run

Carson's stopping rule: when the best rating gains less than 20 points for two runs in a row, the current idea has plateaued; change direction.

| run | best version | rating | gain |
|---|---|---|---|
| 10-20 12:55 | `starter-week2-v1` | 1828 |  |
| 10-20 18:29 | `ppo-league-v8` | 2593 | +766 |
| 10-20 18:47 | `ppo-league-v11` | 2593 | +0 |
| 10-20 19:00 | `ppo-league-v12` | 2593 | +0 |

**Plateau:** the last two runs gained less than 20 points each.

## Lineage

Each version and the version it was copied from, with its changelog line.

```
calib-seed-week2-v1  (calib-seed-v1: starter with a different random seed. Same strength by design: its gap to s)
calib-skip10-week2-v1  (calib-skip10-v1: starter that skips every 10th round. A known small handicap: the league s)
calib-skip2-week2-v1  (calib-skip2-v1: starter that acts only on even rounds. A known large handicap.)
dummy-week2-v1  (dummy-v1: the floor of the league. Drafts the first free champion, then never acts.)
ppo-league-v12  (ppo-league-v12: keep the cooperative budget throw out of line; expect reproducible source-)
starter-week2-v1  (starter-v1: the SDK C++ starter bot, unchanged (cambc 2.2.5). The weak reference.)
```

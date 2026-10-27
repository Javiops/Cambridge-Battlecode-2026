# o92 mcarry: Marcella goes first in the carry order on shared rewards

Order: Marcella, then Vesper, then the rest. This replaces P_VCARRY's Vesper-first order.
- Variant 1: the new order.
- Variant 2: variant 1 plus Marcella's no-leave on a waiting reward.

## Why
On engine 1.0.3, top-10 Marcella gained 32 gems in r0-150 and ours 6. Marcella's passive pays 2 gold per gem tributed,
so the gems she carries turn into shards.

## Results on engine 2.0.0 (cloud bench, 2026-10-27)
Panel: p17_rTop1, rD and mV19 on all 70 pool maps, both sides, 420 games. The +20 probe changed 0 of 70 games, on
both b35 and E1.

| base | variant | wins | + / - | bar |
|---|---|---|---|---|
| b35 (295) | 1 | 312 | +55 / -38 | 19.3 |
| b35 (295) | 2 | 295 | +43 / -43 | - |
| E1 (298) | 1 | 304 | +46 / -40 | 18.5 |

Reference: kvvl 273 (+59 / -84 vs E1), b35 295.

Mechanism, whole-game run-batch statistics per game on E1:

| champion | gems | gold | deaths |
|---|---|---|---|
| Marcella | 240 -> 305 | 1947 -> 2332 | 2 -> 1 |
| Vesper | 226 -> 196 | 1697 -> 1405 | - |
| team | 1000 -> 1021 | 6660 -> 6681 | - |

## Verdict
On E1 it is neutral (+6, below the bar). It is a small rider (`pieza pequeña`): the gems move to Marcella as intended,
but team income hardly changes.

## Zip
`zips/e1mcarry.zip` = E1 (sha f967edfe...) with o92 v1 applied. The stdout marker is `[init] o92mc1`, printed once per
champion; it is a printf string only, and the games are identical to the run without it. The sha256 is in
`zips/SHA256SUMS`.

# chact2.py: per-champion activity in r1-150 (engine 2.0.0 replays)

`chact2.py SRC OUT.json` counts, per champion type over r1-150:
- rounds by activity, each round in exactly one bucket:
  - dead;
  - spawn (within 2 of the start tile);
  - fight (a rival within 3);
  - camp (within 2 of a live camp);
  - walk (moved);
  - idle;
- gems gained;
- groups cleared with the champion within 3, by group kind (elk, elk+gem, gem, gold, wolf*) and by company (how many
  of us were within 3, capped at 3).

SRC is a local res dir (A_/B_ bundles; only our side is counted) or `t10f` (a top-10 r300 jsonl sample, both sides).
It uses `../replay2/dump2.py`. quadrants and concentrated_wealth are skipped, because group ids got mixed in 1.0.3 dumps.

`b35_2_0_0_panel3.json` = b35 vs p17_rTop1 / rD / mV19, all 70 pool maps, both sides (420 games, b35 won 295; 408 decoded).

Per champion per game, r1-150:

| champion | gems | walk | camp | fight | dead |
|---|---|---|---|---|---|
| Marcella | 9.5 | 65 | 39 | 15 | 7 |
| HoR | 13.0 | 56 | 36 | 22 | 12 |
| Vesper | 21.7 | 56 | 20 | 13 | 10 |
| Ryth | 8.2 | 65 | 38 | 14 | 13 |
| Vendetta | 10.0 | 69 | 42 | 8 | 8 |

Captures with 3 of us at the clear: 0.7-1.0 per champion per game; solo: 0.7-1.4, mostly gold clusters and wolves.

There is no top-10 2.0.0 sample yet. Compare when one arrives (run `chact2.py` on decoded jsonl rows from dump2.py).

# V84 first live experiment

Platform v84 / `ppo-topdraft-v6` compiled successfully on the server and is now
the active live bot. V83 is retained as rollback. The server's Clang 22.1.0 build
linked successfully and injected the same one budget check into one function as
the verified local release build. No server binary hash is claimed.

Eight challenges were available by the time this request was checked, and all
eight were used for **40 unranked games** across 20 maps, pairing every matchup
in both seats. Thirty games were nearby benchmarks and ten were a stretch
benchmark. The official previous-match selector pins each opponent to its
earlier A-seat source group, listed in the batch plan. All requested/finished
groups record platform version 84. Final observed challenge allowance: zero.

## Results and limits

**V84 wins 16/40, with zero bot faults and zero fuel-exhausted turns.** The
corresponding v83 historical blocks won 14/40 with 12 fuel losses (10 big-world,
two ambush). The new native replay audit reproduces winner, final round, banks,
and each champion's gold, collected/submitted gems, kills and deaths exactly.

| Opponent | V83 wins | V84 wins | V83 fuel losses | V84 fuel losses |
|---|---:|---:|---:|---:|
| Dirty Coding | 2/10 | 4/10 | 0 | 0 |
| Pathfinders | 3/10 | 5/10 | 0 | 0 |
| Preyas | 3/10 | 4/10 | 10 | 0 |
| Tozo's Disciples | 6/10 | 3/10 | 2 | 0 |

This is a small historical comparison, not proof of higher overall strength.
The historical B-seat opponent binary hash is not exposed by the site. Its
groups were requested close together, but that does not prove byte identity
with the pinned A-seat source. V84 also includes several accumulated changes
relative to v83; it does not isolate the movement fix alone.

Mean banked gems fell from 557.55 to 536.13 and mean team deaths rose from 28.63
to 30.40. These tradeoffs remain visible even though win count and fuel losses
look better. The candidate stays live under Fran's explicit experimental policy;
no formal promotion or new model training is claimed. The prior 139 tests and
independent source rebuilds remain the code validation; no bot code changed
during this match batch. An automatic ranked 1/5 loss to SkibidiSloppers was
observed separately and is excluded from these unranked totals; none was initiated.

## What the games teach us

- **Stampede:** wins both seats, banking 1,000/1,040 gems versus v83's 320/960.
  Own logs contain 28/22 champion assault-release events, confirming that the
  rally can release. These are individual champion events, not counts of whole
  team assaults. One opponent pair is an encouraging diagnostic, not map mastery.
- **Elk-arena:** still loses both seats, but deposits rise from 0/0 to 96/144.
  Logs contain 18/14 assault releases. The earlier zero-release rally bug is not
  the current explanation; inspect sustained damage, survival and collection.
- **Big-world:** zero fuel losses, but only 101/0 banked and 203/0 collected.
  In the B-seat game, multiple healthy carriers repeatedly remain at the same
  logged positions in `tribute` mode holding 15 gems. For example Cassi remains
  at (41,96) in rounds 1,050 and 1,100, and Ren at (26,84) in rounds 1,025–1,125.
  This is a concrete banking-progress problem. A greedy obstacle trap or an
  early budget yield is a hypothesis; the logs alone do not distinguish them.
- **Ambush:** deposits stay around 1,015.5 on average and fuel losses fall from
  two to zero, but wins fall from 2/2 to 1/2. Keep runtime and outcome separate.
- **Pilgrimage and reverse-spiral:** mean deaths rise to 59.5 and 68, with lower
  mean deposits. Fight exposure and retaining collected gems remain concerns.

Next isolate a general banking-progress fix: maintain an obstacle-aware route
or otherwise give carrying champions a bounded opportunity to move before
optional planning consumes the turn. Reproduce the repeated-position case and
test both seats on broad generated obstacle layouts and ordinary maps. Preserve
the improved fuel behavior; do not add a big-world name check, raise the global
initialization reserve, or roll back solely because aggregate wins dip.

## Evidence

`results/stage7-live-v84*.json` and the per-game JSONL contain compact records;
the validation package contains all 40 downloaded statistics/replay bundles,
native reconstructions, the compiler log, objective diagnostics, source/WASM
identity and the historical comparison. Frozen weights and consumed confirmation
cohorts are unchanged; no new confirmation games were used.

# Contact-first combat experiment: ppo-topdraft-v12

V12 moves the unchanged front-line contact test before gathering ally metadata.
When there is no qualifying contact, the old code still paid for an ally roster
scan and could abort before returning to farming/banking. Qualifying fights
retain the same rules. This is one change from frozen topdraft v8; it is distinct
from qualified `ppo-league-v12`. Observation, trained weights, RNG, thresholds
and initialization reserve are unchanged. No map/opponent name cases are added.

## Targeted result

A frozen **v8 mirror** reproduces the generated-layout failure with the same
opponent binary: B banks 105 and exhausts 94 turns; A banks 85 without exhaustion.
Replacing B with v12 banks **245 with zero exhaustion** against frozen v8.
V12 also has zero losses in the other seat (97 banked versus 135); one seat's
win is not overall dominance. Native snapshots corroborate the change: old
Stellar is at (23,18) at all nine sampled round boundaries; v12 has multiple
positions. The official engine independently reproduces terminal banks exactly.
These samples do not prove continuous movement on every intervening turn.

The diagnostic probes narrow the wasted work to front-line ally gathering and
related combat paths. Instrumentation changes the trajectory, so its abort counts
are diagnostic evidence rather than the original replay's hard-loss count. The
unmodified before/after release fixtures are the performance evidence.

Both big-world starter canaries remain wins, banking **692/800**, zero faults
and zero fuel losses. Thus the positive-cargo banking fix from v8 is retained.

## Broad development results

| Schedule | Starter wins | Development wins | Faults | Fuel-exhausted turns |
|---|---:|---:|---:|---:|
| v12 vs v8 | 69/70 | 157/302 | 0 | 6 |
| v12 vs fixed v6 | 69/70 | 150/302 | 0 | 5 |

Each schedule covers 35 official maps and 116 generated development layouts,
including 16 large geometries, with both seats. The fixed-v6 schedule has five
total fuel losses versus v8's fourteen on the same fixture set. Residual losses
remain; this is not a zero-exhaustion claim. Mean banks against parent v8 are
702.93/695.80, and against fixed v6 are 694.85/717.82. These outcomes do not
establish a general strength improvement or a lab promotion.

The 744 broad runs are 674 unique candidate/map/opponent/seat fixtures: 70
starter fixtures repeat exactly. Ten full-log canaries repeat broad fixtures
and match outcome and champion statistics. All candidate games have zero faults.
The source ZIP independently rebuilds to the identical frozen release WASM.
Prior 139 judge tests remain applicable; no judge code changed. All original
Stage 1–7 certificates/model bindings remain intact, and 70 new confirmation
layouts still have zero games played. No promotion gate was run.

V9, v10 and v11 failed their targeted runtime hypotheses and remain rejected.
They are frozen for evidence, not uploaded. See RUNTIME-PROBES.md for limits.

## Live deployment and identity

Updated after field tests: this source is platform **v87**, compiled and active.
The temporary teammate hold expired with their batch complete. The three staged
banking pairs are complete (30 native-verified games); a further 44 groups / 220
v87 games are complete with 75 wins, zero faults and one fuel loss. See
BANKING-FIELD.md and V87-CURRICULUM.md. The coordination plan below records the
pre-upload state and is historical, not a pending hold or unstarted batch.

The teammate hold takes precedence: v82 was restored as selected, and no live
uploads, selections or initiated games occur before 23:10:20 UTC / 01:10:20 CEST
unless Fran releases earlier. Check LIVE-HOLD.json and actual teammate activity.
V85/topdraft v7 remains the last server-verified experiment; zero v85 unranked
groups have been initiated. V8 and v12 are independently rebuilt and ready offline.

After the hold and any running teammate batch, reproduce the pinned Preyas
benchmark in both seats with v85, then field-test v8 and v12 in order as quota
allows. Verify and collect each pair before the next activation. These are
planned stages, not queued requests. Match IDs/versions must be persisted at request.

- Source ZIP SHA256: `63307a7f21d3dc877914fd4f3bbedd24c92ad8777e7275c8e98b3cd93bf6a8de`.
- Release WASM SHA256: `fcd2cdc3c2c69e8defc939f28d1145e60aa8fb176466dc4ef720ccdbf8bd96ea`.
- Official CLI 3.0.2 / rules 1.0.1, pinned engine build in the result records.

The validation package includes full results/replays, frozen sources, native
snapshots, development maps and a verified file-hash manifest. Restore the
archived versions and map paths, then use `tools/topdraft_screen.py` with the
matching `experiments/topdraft-v12/` configuration against an isolated pinned
official runtime. Compact per-game records are committed under `results/`.

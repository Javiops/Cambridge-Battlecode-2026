study27 threat-aware farming experiments
======================================

Prerequisites: Python 3.10+, Git, the official cambc CLI/SDK (tested with CLI
2.1.6, game engine 0.0.1/statistics schema 2), and a local repository clone with
both pinned commits already present. Run cambc init --yes in that clone before
building. Set CAMBC_CLI to a single executable path when it is not on PATH.

The tool reads exact sources using local git show and verifies every file hash:
  study27: c462346d4ace741bfd8f5251fb0e5e2eee69b800
  spar11/12/16: 43d003323cd16059cda6a54de14ed86e2da3b788
It never fetches commits, submits bots or changes tracked bot source. All writes
are isolated in out/study27-micro. Existing immutable output names cannot silently
be reused with different source or patch-module provenance.
Output roots and descendants reject symlinks, Windows junctions and reparse
points, including redirects to another location inside the same clone.

Keep bench.py, patch_farm.py and compare.py together. Example from the clone:

  python tools/study27_micro/bench.py --candidate volley-backoff --features farm_volley_backoff --prepare-only
  python tools/study27_micro/bench.py --candidate volley-backoff --features farm_volley_backoff --maps "maps/*.map26a" "maps_gen/*.map26a" "maps_dev200/*.map26a"

Features (one guard and/or one reserve; comma-separated for combinations):
  farm_outnumbered_hold, farm_outnumbered_backoff
  farm_volley_hold, farm_volley_backoff
  farm_contested_hold, farm_contested_backoff
  reserve_cc3, reserve_cc6
An empty --features "" creates a control source copy. Use separate candidate
names for each immutable variant. Selection/development data do not establish
general superiority; confirm the frozen candidate on a separately fixed cohort.

By default every unique map is played on both sides for candidate vs original
and all three sparring bots, plus unchanged original vs each spar (14 slots/map).
--opponents can select a subset; --no-baseline-panel skips the original spar
panel when deliberately unnecessary. --jobs defaults to 1 to avoid Windows
metadata races; increase only if the local runtime supports it reliably.

Use --maps with archived confirmation maps after extracting their ZIP into an
ordinary folder, e.g. --maps "out/confirmation/*.map26a". ZIP extraction is not
performed by this tool. Map aliases with identical file hashes are deduplicated;
topological or cosmetic correlation needs a separate audit.

Compare candidate with original against the exact same spar/map/side panel:

  python tools/study27_micro/compare.py out/study27-micro/runs/RUN/results.json --names volley-backoff

compare.py needs the complete three-spar baseline panel. It sums outcome-score
deltas across both sides and all spars per map before the sign test; it does not
treat correlated spar/side observations as independent maps. Draws score 0.5.

Run plans pin sources, compiled WASMs, CLI executable/version, project config,
SDK header, exact maps, settings and expected actual engine version. CLI does
not expose a selector for an engine WASM; completed statistics must report
engine 0.0.1 and schema 2. Identical ordered physical inputs reuse a persistent
cache and never count as additional evidence. Complete raw statistics are kept;
the first map for each pair/side plus faults/reinitializations retain native
replay bundles. Reported faults and init markers are audited. SDK-error/low-fuel
log samples are diagnostics, not an exact count of native fuel exhaustion.

Locks prevent simultaneous writes to the same preparation/build/cache key.
If interrupted, check that the owning process has stopped before removing a
stale lock. Failed/timeout game artifacts are retained for inspection.

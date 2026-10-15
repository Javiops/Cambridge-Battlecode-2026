study27 threat-aware farming experiments
======================================

Research result: none of the 22 evaluated policies improved both the direct
study27 comparison and the matched three-spar panel. No production bot change
is recommended by this experiment. These transforms are reproducible rejected
experiments, not a release. See REPORT.txt and the evidence bundle alongside
this file for results, source identities and the separate Corners map cohort.

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

Keep bench.py, patch_farm.py, patch_farm_refined.py, patch_corners.py,
patch_reentry.py, patch_reentry_active.py and compare.py together.
Example from the clone:

  python tools/study27_micro/bench.py --candidate volley-backoff --features farm_volley_backoff --prepare-only
  python tools/study27_micro/bench.py --candidate volley-backoff --features farm_volley_backoff --maps "maps/*.map26a" "maps_gen/*.map26a" "maps_dev200/*.map26a"

Original features (one guard and/or one reserve; comma-separated combinations):
  farm_outnumbered_hold, farm_outnumbered_backoff
  farm_volley_hold, farm_volley_backoff
  farm_contested_hold, farm_contested_backoff
  reserve_cc3, reserve_cc6
Narrow follow-up development policies:
  start_only_backoff, start_only_retarget
  no_contact_dash
  reserve_cc_contact5, reserve_cc_contact3
These follow-ups were developed after inspecting the broad guards' development
results; they are not an independent confirmation of the first-stage policies.
Select one policy that modifies the live-camp branch, optionally combined with
reserve_cc3 or reserve_cc6. The contact-only CC policies already modify that
branch and cannot be composed with another farm policy or another CC reserve.
The start-only policies record both patch module hashes because they invoke the
original outnumbered/backoff transform. Other refined policies pin their actual
module; original features pin patch_farm.py. Source manifests record the exact
feature sequence and dependency hashes used for each immutable output name.

Verified team v39 reconstruction and all nonempty corners component ablations:
  corners_lone, corners_reentry, corners_flee
  corners_lone_reentry, corners_lone_flee, corners_reentry_flee
  corners_v39
The full corners_v39 transform exactly reconstructs the separately archived
team ZIP source. This establishes source identity, not superiority over study27.
Other corners features independently enable the held-camp lone-entry exclusion,
buddy relaxation of danger exclusion, and/or corners-specific flee threshold.
Standalone geometry-based held-camp policies (without a named-map condition):
  reentry16, reentry32
Active-geometry variants used for the recorded re-entry simulations:
  reentry16_active, reentry32_active
Before any re-entry games, a separate one-line activity precondition was added
to skip buddy SDK queries entirely when s.hold<0. The original reentry16/32
registered sources/builds remain immutable and unplayed. The active wrappers
pin both patch_reentry_active.py and its patch_reentry.py dependency.
All seven corners sets can be composed with any reentry policy. Re-entry
support uses Chebyshev-distance heuristics; walls/reachable paths are not proved.

Feature order is canonicalized before source generation and recording:
  optional corners set -> one generic farm/refined/re-entry policy -> optional global CC reserve
For example:
  --features corners_v39,reentry16_active
  --features corners_lone,farm_volley_backoff,reserve_cc3
Only one corners set and one generic policy may be selected. Two CC reserves
are rejected. Corners runs first because it verifies the complete original
main.cpp/params.h pins. Every module actually used, including transitive
start-only dependencies, is SHA256-pinned. The default original comparator is
still unchanged c462346d study27; v39 is an experimental candidate like others.

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

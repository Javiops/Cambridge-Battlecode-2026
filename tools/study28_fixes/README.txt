STUDY28 FIX EXPERIMENTS

Baseline: 43d003323cd16059cda6a54de14ed86e2da3b788, bots/study28/src.

Run cambc init --yes once in a Git clone. The neighboring bench.py reconstructs and verifies the immutable baseline from local Git history; it creates variants only under out/study28-fixes and never submits a bot or edits tracked source.

Example, from the repository root:
python tools/study28_fixes/bench.py --candidate handoff --features capture_handoff --maps "maps/*.map26a" "maps_gen/*.map26a" "maps_dev200/*.map26a"

Use --prepare-only to inspect sources without running games. Use comma-separated features for combinations. The patch modules retain rejected experiments for review; they do not enable those changes in the production bot. Default jobs=1 avoids Windows build-metadata races; CAMBC_CLI may specify the executable.

Results, exclusions, source hashes, and the separate frozen confirmation cohort are documented in analysis/study28-fixes/results.txt. Both sides of each map are paired; deterministic repeats and cache hits are not new evidence.

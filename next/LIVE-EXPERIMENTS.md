# Live experimental versions

Fran clarified on 20 October that real-game iteration should continue even when
fixing a mistake initially weakens aggregate results. Requiring every upload to pass
the promotion gate was too restrictive. A promotion establishes a proven lab champion;
an experimental upload gathers evidence about a frozen, functional candidate.

## Current selection

- Platform **v84**: `ppo-topdraft-v6`, uploaded with note `topdraft-v6 | movement trial`.
- Submission: `922f3836-7d6c-49c5-bbbd-e80c39f78c66`.
- Observed state: **selected for the next match; server compilation pending**.
- Platform v83 / qualified `ppo-league-v12` remains the previous working fallback.
- The site starts compilation on matchmaking. Do not initiate ranked matches to force
  compilation. Verify compilation and the actual version of the first new game.

V84 includes the leader draft, reachable-point objective rally and v6's bounded
low-fuel movement fallback. V6 changes only movement relative to its v3 parent;
comparing v84 with platform v83 tests several accumulated changes and cannot isolate
their individual contributions. Offline version comparisons retain that distinction.

The uploaded source ZIP and the source downloaded back from the server both have
SHA256 `3e9819880e134285a34c84d2f61ae605fe59aea275af9c3f3189c1fe3b246e52`.
Its independently rebuilt local release WASM has SHA256
`f21d27dce9cc364a26c61780367fc0b5c16ce39f643c37929e3b599fe471f534`.
This verifies source delivery and local reproducibility, not yet server compilation.

## Evaluation and iteration

Prior screening is 67/70 versus starter and 149/302 versus qualified v12. This
does not demonstrate greater strength. The targeted runtime observation is 14 fuel
losses versus parent v3's 23 in the same 302 head-to-head games. All candidate
screening games completed with zero bot faults. Existing tests: 139 passed.

Use the next available unranked quota with paired nearby/stretch benchmarks. Track
fuel-exhausted turns, useful movement and gem collection on large/dense geometries;
track objective damage, collection and deaths for the rally. Keep map/opponent/seat
and actual platform versions in every record. Compare repeated matchups against the
v83 data separately from new scouting. Overall wins remain a guardrail and outcome,
but an initial drop is not by itself grounds to discard a targeted fix.

Keep the latest usable experimental version selected while diagnosing and versioning
the next change. Roll back for compilation failure, persistent faults or stalled play;
record failed hypotheses and decide whether to amend or replace them. Fresh holdouts
remain reserved for a formal promotion claim. The 250-game v83 report is historical;
its pre-upload `uploaded: false` development records are not current deployment state.

The existing hourly automation has been updated with this policy. Do not create a
duplicate automation. Current machine-readable state is in
`results/topdraft-v6-deployment.json` and `experiments/CURRENT.json`.

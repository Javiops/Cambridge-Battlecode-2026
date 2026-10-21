# Live experimental versions

Fran clarified on 20 October that real-game iteration should continue even when
fixing a mistake initially weakens aggregate results. Requiring every upload to pass
the promotion gate was too restrictive. A promotion establishes a proven lab champion;
an experimental upload gathers evidence about a frozen, functional candidate.

## Current selection

**V87 / ppo-topdraft-v12 is compiled and live.** V86/topdraft v8 and v85/topdraft
v7 are retained. The teammate hold expired at 23:10:20 UTC with their batch
complete. Thirty matched banking games are downloaded and native-verified: each
version wins 5/10 with zero faults/fuel losses. Big-world deposits improve from
202/90 to 381/336; elk B acquisition regresses. See BANKING-FIELD.md.

All 44 broader v87 groups / 220 games are complete and native-verified: 75 wins,
zero faults and one fuel loss. Historical same-label v83 results have 87 wins and
70 fuel losses; overall strength has regressed despite runtime improvement.
Old opponent-B and seed equivalence are not certified. See V87-CURRICULUM.md. Exact IDs,
queued versions, allowance observations and completed counts are recorded in
CURRENT.json and v87-curriculum-plan.json. The last request used the last available
challenge. Do not duplicate planned/completed requests or mistake incoming and
automatic ranked games for this agent's tests. Historical cohort labels are
comparison strata, not a claim about current difficulty based on rank.

## Historical teammate handoff

Platform **v85 / ppo-topdraft-v7** compiled and was observed live. It continues
healthy, quiet existing banking trips before optional planning; see
[BANKING-V7.md](BANKING-V7.md). Its source ZIP matches the server download and
independently rebuilds to the frozen release WASM.

Fran requested temporary teammate use immediately afterward. **V82 / BASELINE V7
is restored as selected for the next match.** No uploads, selection changes or
initiated matches until 23:10:20 UTC / 01:10:20 CEST, unless Fran releases earlier.
Continue offline work and let a still-running teammate batch finish. Never
overwrite a newer teammate selection based on stale state. The live header may
continue to show v85 until the next v82 match compiles; the selected version is
the relevant next-match choice.

Read `experiments/LIVE-HOLD.json` before any live action and
`experiments/CURRENT.json` for the newest state. V84 remains the preceding
usable experimental bot; qualified v12/platform v83 remains preserved. Zero
v85 unranked challenges have been initiated. V8 is independently rebuilt and
ready offline: big-world starter deposits 692/800, starter 69/70, fixed-v6
comparison 146/302 with 14 fuel losses. It is not uploaded during the hold.
The v9 optional spell-scan guard did not fix the reproduced runtime case and
is rejected. See BANKING-V8.md and BANKING-V9-REJECTED.md. Historical v84 evidence below
describes its completed 40-game batch, not the current selection.

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
`results/topdraft-v7-deployment.json`, `experiments/LIVE-HOLD.json` and `experiments/CURRENT.json`.

The first eight live challenge groups are complete and native-verified: 16/40 wins, zero faults/fuel losses. See [V84-SPARRING.md](V84-SPARRING.md) for the historical comparison and next banking-progress hypothesis.

Topdraft v12 checks contact before ally gathering. The targeted B-seat 94 fuel losses become zero, with big-world starter banks still 692/800. Broad results: 157/302 parent v8 (six schedule fuel losses) and 150/302 fixed v6 (five), zero faults. It was uploaded as v87 after the hold. See CONTACT-V12.md.

Latest field state: **v87 / topdraft v12 is compiled and live**. The teammate hold has expired and their batch is complete. Three native-verified paired benchmarks are complete (v85, v86, v87: 5/10 each, zero faults/fuel losses). Big-world banks improve from 202/90 to 381/336, while elk B acquisition regresses. The staged plan is complete; continue v87 on the remaining actual curriculum allowance. See BANKING-FIELD.md and CURRENT.json.

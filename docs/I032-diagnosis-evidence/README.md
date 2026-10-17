# I032 diagnosis evidence

This package records the bounded follow-up investigation of the experimental mate_bwf combination. It is separate from the earlier I032 evaluation with thousands of correlated variant runs.

- `final-v2-summary.json`, `final-v2-games.csv` and `final-v2-builds.json` contain only final v2 candidates, current raw v59 controls, the explicitly labelled old light-all control on the same12 diagnosed maps, and integrated v2 mechanism checks. Every current source/build/runtime and saved map/replay/statistics hash was checked. Per-game native faults, fuel exhaustion and caught SDK messages are separate fields. Reused physical streams are deduplicated in the unique game count.
- `exploratory-v1-*` preserves preceding exploratory variants separately. Its results must not be attributed to final v2 binaries.
- `native-cases.zip` contains eight finite replay examples: isolated and integrated repairs for Monolith and gen47, plus the Interlock channel-denial comparison. The original repair callsite repeated the startup fuel regression when combined; v2 performs ordinary movement first and retries the remote camp approach only after failure.
- `maps.zip` and `maps.json` contain frozen input maps by hash. The targeted set was selected from diagnosed regressions and controls. The separate fresh and Prism subsets are labelled by their freeze manifests; they are not a universal unseen-map gate.
- `tests.zip` provides a portable, argument-driven runner with actual-source helper/cache/protocol/order fixtures. `test-results.json` records one full production SDK object compile and nine passed mechanism fixtures on the exact final13-file source. Native cost and outcomes remain separate evidence.
- `candidate-source.zip` has exactly13 source files immediately under `src/`. Its source hashes match the portable fixture report. It is included for review, not automatically submitted or activated.

The final candidate is experimental. A small head-to-head lead, a targeted regression recovery or zero native crashes does not establish ladder improvement. Report final-v2 and exploratory-v1 separately, use actual panel slot counts, and do not describe the retained earlier replay examples as newly simulated games.

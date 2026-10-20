# Stage 1 acceptance: PASS

Validated on 2026-10-20 with CLI/SDK 3.0.1 and the pinned October 20 rules build.
`python -m lab stage1 ready` passes against the final source/configuration hashes.
The complete regression suite reports **61 passed**, with no skips.

| Check | Verified result |
|---|---|
| Generated pool | 100 screen + 60 holdout maps; 160 unique hashes; exact regeneration |
| Official calibration | 2,500 completed release games; zero faults or fuel exhaustion |
| Controls | starter 1,828; seed 1,812; skip10 1,790; skip2 1,384; idle 687 |
| Release/native parity | 2,560 actor frames over four complete 2,000-round games |
| Coverage | 3/4/5 picks, both seats, Cassi/Issac, moves, attacks, spells, shop, recall, tribute |
| Terminal parity | winner, round and final banks agree on all four games |
| Inference | Python float32 and C++ WASM SIMD scores/masks/argmax agree |
| Two-pass encode/inference | maximum 55,610 ordinary-turn fuel; limit 65,000 |
| Controller before logging | maximum 71,444 ordinary-turn fuel; limit 85,000 |
| Official probe diagnostics | zero faults and zero fuel exhaustion |
| Actor privacy | hidden health mutation invariant; hidden state/enemy inventory queries denied |
| Protocol | wrong/stale actors, bad numeric inputs/drafts and closed episodes rejected; batch error isolation |
| Batched observation throughput | 2,068 actor turns/s, 16 environments, 1,600 observed turns |
| Native idle tail | 599,387 turns/s; excludes intermediate observations and is not a training rate |
| Source bundle | `contract-probe-v1.zip` rebuilds to exact frozen release WASM |

Frozen diagnostic WASM SHA-256:
`2af3dad9b0bdf4ac5491ddfa3d739d7110966d8720cd053c913c4dfa89722182`.
Frozen archives and generated map binaries are local reproducible artifacts, not tracked repository files.

Machine-readable evidence: `stage1-ready.json`, `stage1-parity.json`,
`stage1-throughput.json`, `stage1-calibration.json`; full calibration report:
`calibration-generated-g1.md`. Reproduction and contract: `../STAGE1.md`.

The fuel envelope covers the measured 305-parameter, two-decision micro-policy. New
architectures/features need fresh release checks. The small handicap's rating interval
overlaps starter's; use map-level uncertainty in future comparisons. The 60 generated
and ten site confirmation maps remain unplayed. No candidate was promoted.
**Stage 2 data collection has not started.**

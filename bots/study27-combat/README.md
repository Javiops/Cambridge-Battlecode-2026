# study27 combat micro

Based on stable `study27` at `c462346d4ace741bfd8f5251fb0e5e2eee69b800`.
Two changes: use legal AoE centres to hit enemies beyond the old four-tile sweep
cutoff; use known dash cooldowns in the existing melee reach estimate. Nearby
casts retain priority. Those behavior changes affect `main.cpp` and `fight.h`.
The delivered `params.h` also removes the earlier redundant `P_U34_RESET_LIVE 1`,
leaving the later effective `P_U34_RESET_LIVE 2` as its single definition.

The frozen combination won **1,074–974** against original study27 on 1,024 fresh
maps, both sides. Its matched three-spar panel gained **161/6,144 wins (+2.62
percentage points)**. All recorded confirmation gates and the independent final
audit passed. Results concern these generated maps and fixed older spars.

Those 14,336 confirmation games tested the frozen source before this macro
cleanup. Separate checks confirm identical preprocessed C++, effective macros
and a successful SDK build whose WASM hash matches the historical candidate.
The full game cohort was not rerun. See `cleanup-validation.json`, the separate
`cleanup-wasm-equivalence.json` byte comparison, and the source manifest.

The incremental dash comparison against AoE alone was weak (development
258–248, p=0.603). Fresh confirmation tests the combination, not each component.
Reach remains a geometric heuristic; caught SDK errors still occur.

From a CAMBC C++ project root with CLI/SDK 2.1.6:

```powershell
cambc build bots/study27-combat
cambc run bots/study27-combat bots/study27 --map maps/corners.map26a -o replay-combat --statistics statistics-combat.json
```

The smoke example assumes the original bot and that map exist. For submission,
upload `cambc-study27-combat-tested.zip` from `analysis/study27-combat`; it contains
exactly the six current files under `src/`. It includes the post-confirmation
macro cleanup and has a new archive/source identity. A rebuild in a different
directory may produce a different WASM; source hashes identify this delivery.

See [results and reproduction](../../analysis/study27-combat/README.md) for the
complete paired tests, source manifest, evidence and limitations.

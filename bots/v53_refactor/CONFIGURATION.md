# Config precedence and reproducible experiments

There is **no new configuration system** in this step, to preserve byte-exact behavior.

1. The original `src/legacy_config.inc` starts by including `src/params.h` if present.
   The test/tuning harness uses that file to change compile-time `P_*` values.
2. Remaining `#ifndef` blocks in `legacy_config.inc` fill only **missing** knobs.
3. Some other original includes contain their own fallback `#ifndef` blocks.
4. `struct Params` initializes four runtime fields from the resulting `P_*` macros.
5. Draft memory transports some parameters into champion processes; runtime profile and
   map code can further alter policy fields on particular map families.

Therefore, **macro value =/= necessarily final in-game value**. You must inspect runtime
`PR`, `P`, and map-specific choices separately. Never infer that a feature is active
solely from its macro being nonzero.

The script `tools/config_report.py` produces `CONFIG_EFFECTIVE.md`, collecting preprocessor
macro values and their locations without modifying the bot or its build. It is a reference,
not an assertion that the listed controls are all meaningful/independent.

Every experimental candidate should record:

- original bot hash and compiled WASM hash (when available),
- a diff of `src/params.h` and the relevant code modules,
- which map sets and seeds were used,
- paired-side A/B results, gem metrics, crashes and fuel,
- the decision to keep or revert and why.

Avoid enabling historical switches in the name of cleanup: disabled systems may have been
empirically worse and often interact with later fixes.

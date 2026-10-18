# Cambridge Battlecode 2026 — v53-refactor-step2

This is **the same v53 bot**, not an upgraded strategy. It reorganizes the source and
adds regression tests and configuration/decision documentation without changing the C++
code that is executed (only the way it is included in `src/main.cpp`).

## Build and use

Keep the entire `src/` folder. Existing build commands for v53-refactor-step1 should
continue to work. `src/main.cpp` remains the sole C++ entrypoint, with original `params.h`
in its usual location. Source files ending in `.inc` are textual includes, not separate
translation units and should not be compiled independently.

## Verify (no replays)

```
python tests/verify_refactor.py
python tests/verify_preprocessed.py
python tools/config_report.py
```

These tests do not simulate gameplay or generate replays. For game verification, run `tests/parity_no_replays.py` (also available as a separate download)
on your Windows machine against the step1 bot, **both sides**, on
identical maps and opponents. Exact deterministic parity should remain unchanged.

## Where to look

- `ARCHITECTURE.md`: files, responsibilities, build constraints.
- `POLICY_FLOW.md`: current precedence of spells, retreat, banking, farming.
- `CONFIGURATION.md` / `CONFIG_EFFECTIVE.md`: what controls are actually compiled.
- `DECISION_OWNERSHIP.md`: strategy overlaps intentionally not fixed yet.
- `CHANGELOG.md`: change record.

The next meaningful phase will decompose the large `play_turn` into callable stages with
explicit action outcomes. That changes the preprocessed code and must have its **own** local
parity testing, unlike this byte-exact split.

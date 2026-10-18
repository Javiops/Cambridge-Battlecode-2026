# Change log

## v53-refactor-step1

- Added 12 textual sections extracted exactly from the original `src/main.cpp`.
- Replaced their original source ranges with in-order `#include` directives.
- Preserved every line of remaining `main.cpp` (including all champion/turn code and the entrypoint).
- Preserved `src/params.h` and all other originally included headers byte-for-byte.
- Added a deterministic byte-for-byte source reconstitution test.
- **No logic, numerical constants, defaults, macros, attack order, routing, or SDK calls changed**.
- Runtime match parity remains unverified until SDK and testing harness are supplied.

## v53-refactor-step2 — structural and diagnostic cleanup (no gameplay changes)

- Split unrelated helpers (`cm_edge_aoe`, `cr_*`) from the 748-line `play_turn` function.
- Put the post-turn slot-name diagnostic helper in its own section without reordering it.
- Moved the complete `run_game()` into `src/run_loop.inc`; the C++ entrypoint `src/main.cpp` is now short.
- The original `src/params.h`, all macro defaults, all original headers, all decision order, and
  every line of actual C++ code are unchanged. Only `#include` boundaries differ.
- Added a v53 config/reference report generator and module dependency map.
- Updated byte-for-byte reconstruction and C++ preprocessing verification for the nested sections.
- This version has not been re-run under the actual game engine in this environment.

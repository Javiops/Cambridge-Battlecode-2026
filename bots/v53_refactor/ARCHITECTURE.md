# v53 refactor — architecture and constraints (step 2)

**Gameplay and all tunable values remain identical to v53.** Module separation is mechanical.
These `.inc` files intentionally behave like textual includes, *not* independently compiled
C++ objects. `src/main.cpp` is the only `.cpp` entrypoint. The extraction preserves declaration
order, anonymous namespace, early returns, SDK action ordering, and fuel checks.

## Modules in their original order

| File | Main responsibility |
| --- | --- |
| `src/legacy_config.inc` | `params.h` override include, compatibility macro defaults |
| `src/runtime_foundation.inc` | Runtime globals, params instance, profiling and SDK wrappers |
| `src/draft_impl.inc` | Draft, draft memory, map family knowledge |
| `src/game_state.inc` | Champion state, group data, vision and ability metadata |
| `src/setup_shop.inc` | Initialization, equipment, map caches |
| `src/movement_actions.inc` | Pathing and action helpers |
| `src/team_camp_planning.inc` | Team claims, camp estimates, target selection |
| `src/banking_tactics.inc` | Banking, retreat and smaller tactical primitives |
| `src/capture_farming.inc` | Farming and capture resolution |
| `src/turn_helpers.inc` | AOE edge targeting and capture-recall helper functions |
| `src/turn_policy.inc` | `play_turn()` — current single top-level policy **with its early returns** |
| `src/turn_labels.inc` | Slot label diagnostics (must remain after turn policy) |
| `src/diagnostics.inc` | Debugging and output |
| `src/spell_sweep.inc` | Spell selection before and after `play_turn()` |
| `src/utility.h` | Original final include |
| `src/run_loop.inc` | Per-champion event loop, exception handling, end-turn bookkeeping |
| `src/main.cpp` | Compilation wiring and tiny program entrypoint |

Every original `.h` file is unchanged. `params.h` **must** remain next to `main.cpp` so
original tools and tuning scripts can patch it. See `CONFIGURATION.md` for the actual source
of configuration defaults/overrides and `POLICY_FLOW.md` for behavior precedence.

## Validation

```
python tests/verify_refactor.py
python tests/verify_preprocessed.py
python tools/config_report.py
```

The first two scripts independently compare source bytes and the C++ preprocessor outputs
against original v53. This is stronger than matching final scores, but does not substitute
for a real SDK compile and deterministic mirrored local games.

## Important limitations and next migration

1. `play_turn` is still large; splitting it into callable sub-policies **will change** the
   preprocessed code and can change instruction fuel / action behavior. That should be a
   separately tested refactor, not hidden in this mechanical stage.
2. `spell_sweep` still precedes `play_turn`; `kite`, `twin_guard`, `front_line` and other
   fight mechanisms still have their original precedence. No shadowed policy was deleted.
3. Active knobs live in original `params.h`, fallback defaults in `legacy_config.inc`,
   and profile/map overrides in their existing code. The report makes them inspectable
   rather than moving or silently changing the precedence.

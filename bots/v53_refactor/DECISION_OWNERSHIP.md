# Decision ownership: as-is (before any policy fixes)

This document makes the existing decision hierarchy visible; it does not assert
that v53 has a clean ownership hierarchy yet.

## Current run-loop precedence

The unchanged `src/main.cpp` invokes, in this order:

1. `spell_sweep(s, true)` when `s.sweep >= 3` (before `play_turn()`).
2. `play_turn(s)` from `src/turn_policy.inc`.
3. An optional post-turn sweep for `s.sweep` 1–2, and other optional spell cases.
4. Post-turn consumable/ward operations (subject to their switches).
5. Status reporting, `bc::end_turn()`.

The **pre-sweep acts before** the rest of the turn planner. It may use an
exclusive movement spell, so this ordering is strategically significant.
Do **not** move it without treating that as a policy change.

## `play_turn` decision sequence (as-is)

1. Staged initialization and fuel guard.
2. Dead-champion shopping, target reset, or continued channel.
3. Shopping and map/vision/group/threat refresh.
4. Support spells, nearby loot preservation, spawn healing, urgent flee/recall.
5. Enemy fight decisions, including the `P_PV` escape verdict, optional `fight_mode`,
   `front_line`, `kite`, linked-twin guard, engage/avoid checks.
6. Recall, shopping return, altar approach/tribute.
7. Grouping / special combat-vs-camp checks, then `farm` and opportunistic final hit.

Most branches return early. Later planners may not run after an earlier one acts.
Some planners consume only a sub-action and deliberately fall through. As a
result, a refactor that changes a `return`, moves a call, or changes a single
`can_move()/can_attack()` test can change whole-turn decisions.

## Existing multiple ownership (to fix **after** parity testing)

| Decision | Current participating code | Why it needs a single owner |
| --- | --- | --- |
| Fight or flee | `src/turn_policy.inc`, `src/fight.h`, `src/verdict.h`, sweep | Early casts, kiting and late retreats can compete for move/cast allowance |
| Camp objective | `team_camp_planning.inc`, `capture_farming.inc`, `mapplan_game.h`, runtime profile | Claimed target, squad request and actual nearby allies can diverge |
| Altar choice / gem security | `banking_tactics.inc`, `turn_policy.inc`, `capture_farming.inc` | Camp profitability ignores portions of later banking cost |
| Capture ownership | `capture_farming.inc`, shared claims and `src/profile.h` | Additional reward occupants don't accelerate capture |
| Configuration | `legacy_config.inc`, `src/params.h`, `src/profile.h`, `src/de_rules.h` | Enabled/disabled features and family overrides are spread out |
| Champion damage forecasts | `team_camp_planning.inc`, `src/fight.h`, `src/verdict.h` | Estimators currently disagree on spells and damage concentration |

## Safe migration order

- **Now:** stable file boundaries, frozen source, source + preprocessor parity tests.
- **Next, once SDK/harness available:** actual compile and deterministic match parity, two-sided mirrored seeds; include logs and fuel.
- **Then:** consolidate configuration presentation and explicit decision ownership *without moving the active action order*; each consolidation requires parity checks.
- **Then:** change one gameplay decision at a time, with an experiment ID, baseline hash and paired A/B results.

The first semantic bugfix should not be bundled with the restructuring.

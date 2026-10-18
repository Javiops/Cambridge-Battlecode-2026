# Actual decision flow and ownership (v53: unchanged)

The presence of a subsystem in the code **does not mean it always runs**: many earlier
branches return before it can act. This file is a review map, not a recommendation to
reorder the operations.

## Top-level (`run_loop.inc`)

1. Reset diagnostic mode / farm state; optional profiling reset.
2. `spell_sweep(s, true)` if `s.sweep >= 3` — can consume movement-exclusive spell action.
3. `play_turn(s)` — see below; always executes barring exception/fuel suspension.
4. `spell_sweep(s)` for `s.sweep` 1–2, or special case 5.
5. Conditional post-free sweep; altar lock / ward routines (subject to flags).
6. Catch failures, diagnostic output, `bc::end_turn()`.

## Main `play_turn` ordering (`turn_policy.inc`)

| Original order | Section | Early-return behavior to preserve |
| --- | --- | --- |
| 1 | Staged init / emergency fuel guard | May end turn before observation |
| 2 | Dead champion: shop and drop target | Immediately returns |
| 3 | Detect camp reward, shop, health tracking | Updates state before other logic |
| 4 | Ongoing channel / low fuel | Immediately returns |
| 5 | Update visible enemies, threats, camps and paths | May update shared data and targets |
| 6 | Support spells, opportunistic capture, unstick | Can consume an action or return |
| 7 | Heal on spawn, capture-recall, urgent flee | Can return before combat |
| 8 | Fight verdict, front line, kite, twin guard, engage | Several early exits; order matters |
| 9 | Shop/health recall and nearby banking | Can recall/tribute/return |
| 10 | Ordinary banking, gem chaining, grouping | Can return without farming |
| 11 | Farm and opportunistic enemy hit | Final action layer |

## Known overlaps that are NOT resolved

- A pre-turn exclusive spell can prevent movement after a flee decision.
- `fight::kite()` can return before Cassi/Issac linked-death protection.
- A tactical retreat does not necessarily invalidate the camp objective.
- Shared camp assignment and actual teammate arrival are not equivalent.
- Default camp score and banking cost do not consistently share an objective.

**Do not remove or reorder these branches as part of a "no logic change" patch.**
Implement explicit action requests / ownership once ready for a separately measured
policy migration. Treat every early-return and `me.can_move()`/`me.can_attack()` interaction
as a regression-sensitive interface.

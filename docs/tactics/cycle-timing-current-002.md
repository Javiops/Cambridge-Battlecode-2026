# Current 0.0.2 capture and channel timing

**Twelve controlled cases, 97 passing assertions.** These are mechanics and API checks, not bot matches, a strategy-strength experiment, a tested decision policy, or proof of the current server binary. The suite uses the official CLI 2.2.2 viewer's `v0_0_2-DFj19m76.wasm`, SHA-256 `e123b59d9dea198762ab7a04db9b3cb6d06dfa991088e41c24750fc4cb88b947`.

The probe script (`work/economy-cycle-research/policy/probe-cycle-timing-current.mjs` in the [evidence archive](resource-cycle-evidence-2026-10-16.zip)) imports the version-selectable combat harness and requires that exact engine hash. It uses the current `Game_Runner_DraftChampion(game, choice, 0)` adapter and refuses a snapshot ABI other than 184696/40152 bytes. Full [native observations](resource-cycle-evidence-2026-10-16.zip) (`policy/native-cycle-timing-current.json` under the retained work tree) retain every starting state, action result, owner-end/runner-step observation, public query, host capture state and assertion. The [compact case summary](native-cycle-timing-summary.json) omits the full trace only. Sandbox operations construct positions, items, initial bags and killed camps; actual recall, tribute, enemy region-entry movement, occupied-tile rejection, basic attack and phase progression use real game actions. No bot source is modified.

## Setup and outcomes

The main fixture is a 32×32 open map with altar (13,15), a cardinally connected wolf at (13,14) and gold cluster at (14,14), and their untouched mirrored counterparts. The tested home group pays 22 gems and 125 gold. Actor 0 stands on (13,14). The extra allied holder, when present, stands on (14,14). A separate single-tile fixture contains only the wolf, paying 22 gems and 90 gold. All native champion identities/types and groups are recorded. Team A has two actors; Team B has two. Only the self body in these cases is instructed to start the tested channel.

`hold=1` means the body enters the freshly waiting reward during its round-1 input and remains there through one complete owner-to-owner interval, starting recall at its round-2 input. The first capture phase establishes timer 5; it does not both establish and decrement that timer. These host timer values explain the observation and are not supplied as bot inputs.

| Case | Actual timing/outcome |
| --- | --- |
| Normal recall immediately, hold 0 | Starts round 1 with timer 5; departs round 6; no payout. Emptying the region loses progress. |
| Normal recall after hold 1 | Starts round 2 with timer 5; receives 22 gems at round-7 capture resolution while channel timer is 0; recall then resolves in round 7. |
| Home recall immediately, hold 0 | Starts round 1 with timer 3; departs round 4; no payout. |
| Home after hold 1 | Starts round 2 with timer 3; departs round 5; no payout. The normal one-hold rule does not transfer to Home. |
| Home after hold 3 | Starts round 4 with timer 3; receives 22 gems before departing in round 7. |
| Normal after hold 1, then enemy contest | Enemy actually moves (15,14)→(14,14) during round 3. The next capture phase resets owner/progress, while recall continues. Enemy later leaves. Actor 0 recalls in round 7 without payout. |
| Normal immediate, actual other holder | Actor 0 departs round 6; actor 1 remains and receives all 22 gems in round 7. This validates a real holder's timing contribution, not the proposed handoff protocol or future willingness. |
| Single tile, normal after hold 1 | Enemy actually attempts (14,14)→(13,14) during its own turn. Engine rejects with error 22, `Known occupied destination.` The capture is not contested. Actor 0 receives 22 before round-7 recall. |
| Home after hold 3, then enemy contest | Enemy actually enters the unoccupied second region tile during round 5. Progress resets while the three-tick recall continues; actor 0 departs round 7 without payout. Enough initial hold does not protect against a later contest. |
| Normal after hold 1, actual enemy basic | An actual enemy basic from outside the capture region interrupts recall. Actor 0 remains physically on (13,14), continues holding and receives 22 gems in round 7. Channel interruption and capture abandonment are separate events. |
| Capture reward during active tribute | Start with 31 gems in round 4: initial duration 4. At round-7 capture, bag becomes 53 while tribute remains active with timer 1. It banks 53 in round 8. Receipt does not extend initial duration. |
| Reward before pending one-tick tribute | Start with 5 gems in round 6: duration 1. Timer reaches 0 at that owner end. Round-7 capture adds 22, then tribute completes for 27 at the following owner start. |

## Public state versus host evidence

The actual `Game_API_CampGroup_GetState` query returns **2, reward available** in all of these different host states:

- Before any capture has begun: no capture owner, timer 0.
- Established allied capture: timer 5, or timer 3 later.
- After a brief enemy contest reset: no capture owner, timer 0.

The corresponding `Game_API_CampGroup_GetCooldown` calls fail with error 106 while the reward waits; they do not leak capture progress. After payout the group becomes state 3, respawning, and cooldown is the supported lifecycle timer. The exported public camp-group API provides `GetState` and `GetCooldown`, without a capture owner/countdown getter. `Game_Visualiser_CaptureTime()` is the **constant 5**, not a live per-group progress API. The host snapshot's capture owner and countdown are research-only evidence.

The numeric native channel values are directly confirmed after accepted starts: **recall = 1, tribute = 2**. The public `Game_API_Champion_GetChannelTime` is independently queried and agrees with retained host remaining times, including returning **0 while the channel is still active/pending**. Without an active channel it returns error 115. The native champion type/flags are separate enums; do not substitute one for another.

## Owner-end and completion semantics

All successful unbroken channels in this suite decrement during the **starting owner turn end**. Timer 0 remains pending through the rest of the round and resolves at the next owner start. Thus a one-tick tribute begun round 6 banks in round 7, rather than at round-6 end. Capture mutation is observed at native phase 7 before channel resolution at phase 14 in these traces. The exact phase snapshots, current actor and turn index are retained; the report does not reconstruct order from round numbers alone.

No correction is needed to the handbook's statements that the starting turn end counts, zero remains pending, and capture resolves before channel completion. The important correction is to preserve both **capture setup phase** and inventory-dependent recall duration: normal requires the demonstrated one prior hold interval, Home requires three, in the uncontested setup. A five-tick capture is not a reward after only five phases including the initial start phase.

## Policy consequence and tradeoff

Do not discard verified overlap merely because no capture-progress getter exists. A local overlap candidate names all of these requirements:

1. Fresh observed waiting reward, our actual on-region position and a local hold history whose capture-continuity assumptions are justified.
2. Actual owned Home state/expected recall duration, checked against public remaining time after accepted start. Under the tested mechanics, the nominal prior hold is `max(0, capture_time + 1 − recall_duration)`: one for normal five ticks and three for Home three ticks. This is a mechanics-derived timing bound, not an optimized economic threshold.
3. Credible survival and no relevant capture reset before payout/departure. A public state-2 observation alone supplies neither. A single-tile region plus our uninterrupted living physical presence excludes ordinary enemy occupancy there under the tested rejection rule; full channel survival/interruption checks still apply. A multi-tile region permits a separate enemy to contest while we remain. Any missing continuity/contest evidence remains unknown.
4. A worthwhile recovery/purchase/re-entry mission under chapters 10/11. Overlap does not remove return walking or missed field work.

The **planned v1 narrow geometry exception** may use that single-tile continuity proof and nominal hold, with fresh duration, survival, mission-benefit and actual-position checks. The normal single-tile sequence is directly confirmed here; combining Home's verified three-hold timing with the occupancy proof is a mechanics-based inference that still needs implementation coverage. More general multi-tile overlap needs an explicit supported no-contest/continuity bound, or an actual replacement satisfying the acyclic handoff contract. An actually present second body is not proof of its future hold commitment.

When these checks cannot establish continuity, **payout first is the conservative fallback**, not a superior universal policy. In the uncontested examples it delays departure by five owner intervals for normal recall or three for Home relative to the successful overlap. That can reduce income/recovery timing and can lose against the existing reference. Compare the guarded-overlap and fallback variants with activation, forfeited captures, occupied time, completed banks and return costs; no comparative benefit has been measured here.

An enemy can reset a multi-tile capture without damaging the recalling body, so “recall is still active” cannot stand in for “capture is still progressing.” Conversely, damage can interrupt recall without emptying the capture, so interruption need not automatically abandon the reward. These are the tested reasons to keep typed channel outcome and capture continuity as separate local state.

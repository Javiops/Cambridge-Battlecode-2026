# Positive-cargo banking follow-up: topdraft v8

V8 changes one condition from frozen v7: the early healthy/quiet continuation
of an existing banking trip accepts any positive cargo, rather than at least
12 gems. It does not change when trips start. The original unsticking and
late-game policies can start smaller trips, which otherwise return to the
late, low-budget movement path. No new map/opponent name cases or model changes.

On the big-world starter reproduction, deposits rise from v7's 316/105 to
**692/800** in both seats, winning both games with zero faults/fuel losses.
The sampled stationary positive-cargo banking sequences disappear in these
two fixtures. Official-engine snapshots independently reproduce terminal banks;
sampled positions do not establish continuous movement on every turn.

| Schedule | Starter wins | Development wins | Candidate faults | Fuel losses |
|---|---:|---:|---:|---:|
| V8 vs parent v7 | 69/70 | 152/302 | 0 | 106 |
| V8 vs fixed v6 | 69/70 | 146/302 | 0 | 14 |
| Earlier v7 vs fixed v6 | 67/70 | 148/302 | 0 | 14 |

Each broad schedule covers 35 official maps and 116 generated development
layouts, including 16 large geometries, with both seats. These are development
results, not proof of overall strength or a promotion. The repeated 70 starter
fixtures in the two v8 schedules match exactly; eight full-log canaries also
repeat fixtures and are not independent evidence. No new holdouts were used.

The changed opponent matters to runtime: 94 of v8's losses against v7 occur
on one B-seat generated layout, g1-screen-093. In the reverse seat game, v7
also loses exactly 94 turns in B. The same layout against fixed v6 has zero
candidate fuel losses in both v7 and v8. Thus the 106 versus 14 aggregate does
not by itself prove a new v8 regression. The repeated B-seat runtime failure
still needs a fix. Heavy per-phase printf instrumentation consumes enough fuel
to change behavior substantially and is excluded from performance evidence.
A lighter breadcrumb diagnostic also changes the trajectory; it does not
establish a specific native call as the cause.

Next isolate the optional spell scan: its existing entry guard permits it to
start below the controller's normal budget checkpoint. Test a bounded entry
guard for that optional scan, without increasing initialization's global reserve.
Keep the fixed-opponent comparison to measure collateral changes.

V8 is frozen and independently rebuilt to identical release WASM, but **not
uploaded** during the teammate hold. V82 remains selected; read LIVE-HOLD.json
before any online action. V85/v7 is the latest server-verified experiment, with
zero initiated unranked groups. After the hold, first reproduce its pinned
Preyas matchup in both seats, then test the newest usable prepared generation.
Keep an active teammate batch undisturbed. The lab champion remains qualified v12.

- Source ZIP SHA256: `7cb32c43786e6df0cca50de081f619405cd2a65dbc43cf97696bdf3e3081c7cb`.
- Release WASM SHA256: `c92a39613426dab54e4e02363cdf7ec50882865329ac869bcc155da9db0c9b89`.
- Runtime: official CLI 3.0.2, rules 1.0.1, pinned build in the result records.
- Tests: prior 139 judge tests remain applicable; no judge code changed. New bot
  behavior is checked by 744 broad release runs and eight full-log repeats:
  674 unique candidate/map/opponent/seat fixtures. Full raw evidence is retained
  locally under the experiment directories; compact records are committed.

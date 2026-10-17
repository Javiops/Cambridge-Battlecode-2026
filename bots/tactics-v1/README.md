# Tactics v1

A new, modular implementation of the team's tactics handbook. This is a correctness-first
candidate for review and subsequent tuning; it is not a claim of perfect play or a proven
replacement for the live bot.

Specification baseline: [`docs/tactics`](../../docs/tactics/README.md), including the
[common decision contract](../../docs/tactics/cycle-decision-contract.md) at commit
`20c97a701bc9ddb45a23951e6ea28a79f7f22df9`. Historical **Current behavior** paragraphs
describe the previous bot; they do not override the new **Tactic** paragraphs.

## Structure

| File | Responsibility |
| --- | --- |
| `types.h` | SDK-free state, action/result types, timing and bounded claim codec |
| `geometry.h` | Immutable terrain, legal altar rings and bounded walking-field cache |
| `sdk_world.h` | Personally observed state and fresh SDK observations |
| `actions.h` | The sole gateway for gameplay mutations and explicit action outcomes |
| `log.h` | Bounded, allocation-free audit records that preserve the action budget |
| `coordinator.h` | Mission arbitration, channel continuity and confirmed progress |
| `economy.h` | Clear/collect/deliver/recover cycles, fresh proposals and safety |
| `resource.h`, `ranking.h`, `cycles.h` | Resource purpose, bounded job shortlist and common completed-cycle comparison |
| `chain.h` | Funded one-extra-job proposal, ordinary-walking bounds and finite delivery obligation |
| `solo.h`, `solo_bounds.h` | Supported singleton clear/arrival certificates and explicit optimistic lower bounds |
| `squads.h` | Bounded minimum sufficient locally ready crew selection |
| `farm_readiness.h` | Present legal camp contribution; unpriced future help never becomes current damage |
| `coordination.h`, `assembly.h` | Fresh local crew forecasts and finite prospective arrival/exit contracts |
| `camp_actions.h`, `camp_collateral.h` | Shared actual/model camp action effects and external-group/contact safety |
| `crew_sequence.h` | One-use actual-action receipts for a paid stationary crew turn |
| `information.h`, `strategic.h` | Bounded warnings, route progress and observed exit/cutoff checks |
| `combat.h` | Legal one-cast exchanges, useful control, protection and escape |
| `vision.h` | Personal mission observation, retained-ward comparison and bounded placement |
| `shopping.h` | Private inventory, first useful passives and verified Tavi transactions |
| `draft.h` | Legal geometry-based initial draft fallback |
| `main.cpp` | Owner-turn orchestration, shared claim publication and fuel boundaries |

There are no map-name or map-signature strategy branches. Public map design may be cached;
positions, HP, actions, targets, inventory and channels are observations with an owner epoch.
The two spell slots share one cast budget. Readiness does not imply movement compatibility.

`sdk_world.h` isolates a version-pinned SDK 2.2.2 adapter for the official imported
champion/camp snapshot records. Reading each accessor separately repeats the same host query
and can starve later decisions. The adapter preserves the host's personal-visibility and
dead-state checks; upgrade it together with the pinned SDK and native regressions.

## Decision flow

1. Observe the current owner epoch. A resumed computation cannot act on its old epoch.
2. Preserve an actual active channel, or cancel once for a concrete useful escape.
3. Preserve a safe immediate deciding delivery. A wounded carrier funds survival/recovery
   before an expensive distant altar comparison; a real reward holder keeps its own contract.
4. Resolve immediate survival, ally protection and relevant interruption opportunities.
5. Keep a real capture holder until payout or an actual safe local handoff. Overlapping a
   recall requires observed continuous holding and the owner's actual Home/normal duration.
6. Compare needed recovery, bank now, and at most one extra feasible reward then bank.
7. Clear only with real readiness and a paid safe reply. Prospective assembly names actual
   arrival/exit paths and a finite lease, then rechecks the real crew before attacking.
   Geometry hints never preserve old HP, cooldowns, readiness or occupancy. Expire failed
   assemblies and vacate original tiles while a camp is respawning.
8. Admit compatible shopping under the same owner and fuel budget. A cash-first investment
   must really earn its named cash, buy its exact bundle and complete its named gem return.
   An optional ward is considered after choosing an ordinary mission/action, before executing
   it; required survival and paid camp follow-ups do not wait for optional ward work.
9. Reobserve affected state before another action. If the remaining fuel cannot fund a
   correct new observation/decision, end the owner opportunity instead of reusing old facts.

An accepted channel start is not completed score. Logs distinguish ordinary applied actions,
blocked/rejected actions, starts, cancellations and lock hits. Collection and channel completion
are observed later. An enemy lock is selected by team even if our own lock occupies the altar.

## Explicit first-version boundaries

- Draft recipes are the handbook's legal initial fallback, not a fitted counterdraft solver.
- Team coordination uses actual local bodies and the existing eight-byte channel; a claim is
  an intention. A distant claim does not contribute damage or establish a capture holder.
- Locally priced crews compare solo/pair/larger local subsets. The bot does not pretend
  to assign a globally optimal team partition or price every ally's remote alternative.
- Farm and bank cycle estimates are coarse, use declared inherited gold weights and initial
  safety margins, and never count the carried bag twice. Hidden group members remain uncertain;
  only SDK-visible death may remove a member from the estimate.
- Recent missing enemies create bounded uncertain regions; they are not legal targets.
  Long channel forecasts use a conservative upper bound, not a certified enemy route.
- Item selection uses useful first unique passives, coherent components and a stated stat
  fallback. Treasure/Home forecasts default to zero without a named future-income/return
  schedule. There is no invented optimal item-payback model.
- Optional teleport and speculative altar-lock purchase/placement are deferred. Existing
  opposing locks are detected, priced and removed or routed around correctly.
- Compact advisory warnings use the existing shared bytes. Remote accepted-role/ETA
  negotiation, a full territory controller and global route-loop optimization remain future
  work. The coverage audit records these limits rather than marking all 96 topics fully
  implemented or verified.

These are implementation limits, not assertions that those strategies are unhelpful. The
initial constants are exposed in `Settings` or their owning module for later controlled tuning.

## Build and bundle

Use the official CLI/SDK **2.2.2** and engine **0.0.2** for the recorded checks:

```sh
cambc build bots/tactics-v1
cambc build bots/tactics-v1 --release
cambc bundle bots/tactics-v1 --output tactics-v1.zip
```

On Windows, the first normal build creates the compile database that this CLI release also
looks up during its first release build. Only the release module is used in recorded matches.
The submission ZIP must contain `src/main.cpp` and its headers at the ZIP root's `src/` path.

## Current validation status

Integration20 finished **0 wins and 28 losses**, with zero candidate fuel/native/API events;
38 pure suites and 28 standalone headers passed. Strict autonomous crew-to-bank activation
passed 3/4 controlled games. A separate real-income partial-emblem prelude followed by
unchanged main produced cash -> exact purchase -> Elk -> actual bank on both sides. These
are scoped correctness results, not strength proof.

Integration21 finished **1 win and 27 losses**. Its 39 pure suites and 30 standalone headers
passed, and its early solo clear/capture/bank activated on both sides. The development panel
nevertheless exposed an unbudgeted local route search: one Lanes side had 222 candidate fuel
pauses and scored zero. The isolated two-file repair reduced that same candidate to zero fuel
events and 220 gems; the original still won. Baseline fuel events remain separately reported.
The failed integration21 snapshot is retained and is not a submission recommendation.

Integration22 combines the funded route repair, typed direct-cast-only outer-range solo
itinerary and broader local crew comparison. Its 41 pure suites and 30 standalone headers
pass; all 28 development games have zero candidate fuel/native/caught/API events, but the
result remains **1 win and 27 losses**. Exact native full-main Expanse activation supports
18 casts over 137 owners without HP loss, then collection and bank. The exact investment
case also passes both sides. Separate cooperative conversion metrics are 2/4 fixed-primary
and 3/4 any-objective; the latter cannot reconstruct unlogged selected crew IDs. No early
rendezvous activates in those four controlled games. Safe long clears are not automatically
better than faster crews.

Integration23 fixes expired unnamed staging before optional planning, reserves a singleton
hypothesis without calling it affordable/ready, and stops treating a fully personally
observed unready camp as new information. Its 43 pure suites and 31 standalone headers pass.
Exact normal Expanse side A improves from 66 to 242 gems and from 3 to 11 clears/banks;
the formerly idle Issac performs 505 actual actions and banks 44 gems. Those gains do not
generalize to competitive strength: the complete development panel is **0 wins and 28
losses**, with one candidate fuel pause (caster-ball/Corners/A, R12 Ryth0) and no candidate
native/caught/API errors. The four controlled autonomous fixtures retain 2/4 fixed-primary
and 3/4 separately measured any-objective cooperative conversions; early rendezvous still
does not activate. Long healthy idle intervals remain on multiple geometries.

Integration24r1 passes 45 pure suites and 32 standalone header checks. Its complete
development panel remains **0 wins and 28 losses**, with zero candidate fuel suspensions,
native faults, caught errors or action/API errors. The equivalent fixed-array squad
selector reduces one retained actual input from 33,136 to 6,026 fuel; that is a computation
repair, not evidence of stronger play. An exact-source quiet controller test now earns
24 gems, captures one extra 24, and banks 48 once; its direct-bank control converts the
first 24. Typed cast-only controller and real-cooldown regressions also pass.

The exact integration24r1 lawful investment regression **fails on both sides**. A real receipt is
created, but its named objective is beyond the bounded three-owner first-hit quote and
has no finite travel executor. Earlier22 success depended on an incidental approach to
another target. Current work adds explicit cash and installed-gem travel controllers,
fresh actual-current awake entry, bounded candidate scheduling, and strict separation
between coarse ranking estimates and action certificates. These changes require their
own frozen combined-source validation; isolated or historical successes do not establish
complete tactical implementation or competitive improvement.

All failed versions and adverse results remain retained. All 18 holdout games remain sealed.
The bot remains a draft until its implementation and competitive gaps close.

See `validation/` for source coverage and final integration evidence, and
[`tools/tactics-v1-validation`](../../tools/tactics-v1-validation/README.md) for production-helper fixtures.
Local match results measure this frozen artifact on the recorded opponents/maps; they do not
prove ladder strength or certify every tactical edge case.

## Exact published checkpoint

integration26: 1W/27L; 56 pure suites, 35 standalone headers and their combined include check pass. Candidate events: 0 fuel pauses, 0 native faults, 0 caught errors, 0 action/API errors.

Release module: `cb7be3431e179848678df8107dca6624a15bb664230b9e6ab3cfddc684b75e11`. This draft is not a live activation recommendation. The 18 final holdout games remain sealed. See [validation](validation/README.md).

## Checkpoint26 review

This checkpoint repairs a mismatch between a scalar farming schedule and its
executor: a Basic that was priced together with a current Damage/Reset now
requires a paid, typed same-owner continuation. The continuation reads fresh
actual self/target state through a restricted snapshot and ends the owner after
the final action or a failed obligation. Basic-only and independently repriced
first-owner schedules cannot borrow an unexecuted cast. Typed Combined versus
DirectCastOnly mode and slot persist across owners. A conservative current lethal
basic removes only the killed selected singleton's response from its safety test.

It also adds a bounded safe adjacent observation detour, one funded current useful
multi-camp cast before elective work, and a narrowly certified self-release from
an already active harmless two-body job while retaining the actual collector.
The latter is not general dynamic grouping/splitting.

**Development result: 1W/27L, 2,860 scored gems.** Against checkpoint25r1,
7 case scores rise, 19 fall and 2 are equal; total scored gems fall by1,545.
Against the original this is1W/15L, and against three sparring styles0W/12L.
All28 games have zero candidate fuel suspensions, native faults, caught errors
and action/API errors. This is not a stronger bot or an activation recommendation.

All56 policy suites and35 standalone headers plus their combined include pass.
Ten scoped native contracts pass on these frozen production sources: lawful
cash/item/gem conversion, extra-job banking, cast-only/full-main and cooldown,
ordinary/boundary awake entry, funded current casting, current self-release,
and positive/negative current-cast budget admission. Their wrappers have different
controlled scopes. The two admission cases instrument guest budget and record
separate compiled-source/module identities; resizing does not execute Bot::turn.
Passing these tests does not prove autonomous opening or all future inputs.

Productive grouping/splitting, group travel, camp selection and opening allocation
remain required partials. Owner-start funding, actual pair formation and reward
conversion are being addressed in the next isolated changes, not represented as
already fixed here. All18 final holdout games remain sealed.

Release module: `cb7be3431e179848678df8107dca6624a15bb664230b9e6ab3cfddc684b75e11`.

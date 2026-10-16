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
| `economy.h` | Clear/collect/deliver/recover cycles, safety and one-extra-reward comparison |
| `resource.h`, `ranking.h`, `cycles.h` | Resource purpose, bounded job shortlist and common completed-cycle comparison |
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
- Minimum sufficient crews compare solo/pair/larger local subsets. The bot does not pretend
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

Integration20 is a **draft: 0 wins and 28 losses** on the retained development panel.
All 28 games have zero candidate fuel pauses, native faults, caught errors or action/API errors.
The corrected source-matched validation package passes 38 pure suites and 28 standalone headers.
The source manifest matches the build of release module
`78f3d89e9fbf7ea4167ad91bd36af8c49eb3fa353a3fa58f71729e04790776bc`.
Do not activate or submit this as an improvement over the original.

Three of four controlled autonomous-main games pass the strict paid co-clear -> actual receipt
-> recipient bank assertion; the five-pick SideB primary cycle remains incomplete. All four are
free of fuel/fault/API events. 14 early rendezvous moves are joined to actual native actions,
plus one accepted wait. These are activation evidence, not competitive success.

Separate actual/native evidence confirms the solo camp-phase clock and the corrected cache
costs. The former cash-investment positive case is now honestly obsolete: corrected Cassi can
clear its Wolf without the formerly required Health shard. That scenario must not force a buy;
a separate positive case now passes both sides: a scripted native prelude really earns 210 gold
and buys seven shards; unchanged main then captures its next 35 gold, buys the fifth Jungle Health
shard, clears an Elk and banks 36 gems. No wallet/stat injection is used. This is one controlled
starting kit, not whole-team competitive success. Older records retain their source scope.
The final 18 holdout games stay sealed.

See [validation](validation/README.md) for exact source, adverse results and scope, and
[the validation tools](../../tools/tactics-v1-validation/README.md) for reproduction.

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
| `coordinator.h` | Mission arbitration, channel continuity and confirmed progress |
| `economy.h` | Clear/collect/deliver/recover cycles, safety and one-extra-reward comparison |
| `squads.h` | Bounded minimum sufficient locally ready crew selection |
| `combat.h` | Legal one-cast exchanges, useful control, protection and escape |
| `vision.h` | Personal mission observation, retained-ward comparison and bounded placement |
| `shopping.h` | Private inventory, first useful passives and verified Tavi transactions |
| `draft.h` | Legal geometry-based initial draft fallback |
| `main.cpp` | Owner-turn orchestration, shared claim publication and fuel boundaries |

There are no map-name or map-signature strategy branches. Public map design may be cached;
positions, HP, actions, targets, inventory and channels are observations with an owner epoch.
The two spell slots share one cast budget. Readiness does not imply movement compatibility.

## Decision flow

1. Observe the current owner epoch. A resumed computation cannot act on its old epoch.
2. Preserve an actual active channel, or cancel once for a concrete useful escape.
3. Prefer a feasible deciding delivery over discretionary work; retain hard survival checks.
4. Resolve immediate survival, ally protection and relevant interruption opportunities.
5. Keep a real capture holder until payout or an actual safe local handoff. Overlapping a
   recall requires observed continuous holding and the owner's actual Home/normal duration.
6. Compare needed recovery, bank now, and at most one extra feasible reward then bank.
7. Clear only with real readiness and a safe reply. Stage without waking the camp when help
   is missing; expire failed assemblies. Vacate original tiles while a camp is respawning.
8. Admit compatible shopping/ward proposals under the same owner and fuel budget.
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
- Strategic warning sharing, a full territory controller and global route-loop optimization
  are future work. The coverage audit records these limits rather than marking all 96 topics
  fully implemented or verified.

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

See `validation/` for production-helper fixtures, source coverage and final integration evidence.
Local match results measure this frozen artifact on the recorded opponents/maps; they do not
prove ladder strength or certify every tactical edge case.

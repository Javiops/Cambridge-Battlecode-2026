# Follow-up runtime probes, 20 October

Prepared v8 remains unchanged and not uploaded during the teammate hold.

| Probe | Target result | Decision |
|---|---|---|
| V10: PPO tile lookup instead of repeated roster scans | 94 B-seat fuel losses remain | Reject targeted fix; no broad screen or upload |
| V11: learn a conservative cost after budget-aborted full target choice | 94 remain; big-world banks 390/507 versus starter, ambush 37/74 | Reject; restore v8 |

Each candidate has ten release canaries, zero faults and an exact independent
source rebuild. Both archives stay immutable. V10 preserves observation/weights
and seeks lookup efficiency, but it does not solve the named symptom; no global
eligible-target parity claim is made from these canaries alone. V11 changes only
the planner-cost estimate after failure and does not alter initialization reserve.

A separate actor-disabled control wins both seats against v8 on the development
layout, banking 190/127 with zero faults/fuel losses. This removes both model work
and model-induced action changes, so it cannot isolate cost as the cause. The
unchanged v8/v9/v10 Stellar counter stays at 25 completed PPO evaluations from
round 100 through 2,000, while the first hard loss is around round 291. That does
not rule out observation work which returns before model evaluation.

Verbose profiling changes fuel behavior too much. A lighter phase-only probe
also changes the trajectory, but records 1,297 budget aborts in the broad combat
phase, versus 31 in post-sweep and 27 in farming. These are aborts in the diagnostic,
not the original candidate's hard-exhaustion count. It motivates narrower combat
phase markers; it does not prove a specific function caused the frozen replay's
94 hard losses. All diagnostic code stays outside the production source.

No map-name exceptions, model changes, new holdout games or live actions.

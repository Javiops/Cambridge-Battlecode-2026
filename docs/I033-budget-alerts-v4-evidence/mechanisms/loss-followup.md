# Follow-up on the single final sparring loss

The final bot loses **882-1020** on `fresh-compact-open`, side B, against spar12. The same saved slot was won by fuel-alerts (1020-832), budget-v2 (1028-794), and raw v59 (1006-758). Four existing replay streams were reconstructed and checked against their recorded outcomes; no new games or code changes were made.

| Candidate | Score | Deaths | Gems lost | Fuel events |
|---|---:|---:|---:|---:|
| final-loss | 882-1020 | 23 | 124 | 22 |
| fuel-alerts-control | 1020-832 | 13 | 22 | 50 |
| budget-v2-control | 1028-794 | 12 | 0 | 85 |
| raw-v59-control | 1006-758 | 18 | 22 | 20 |

## Earliest verified regression

The first **764 global action records match** budget-v2. The first change is Issac at **round31, input785**: the same body at `(23,6)`, 660/900 HP, moves to `(24,7)` instead of `(24,6)`. This precedes the first final-candidate fuel exhaustion at round44. Removing only cohort additions makes the complete relevant source match budget-v2.

At round25, while world state and actions still match, the final bot has **1,562 less fuel on both Cassi and Issac**; the other four bodies also have less remaining fuel (1,005-2,373). The cache performs an extra owned-handle copy and bookkeeping when that allied list is used only once. This is an avoidable single-use cost, even though repeated combat scans can save fuel. Existing path and tactical guards react to remaining fuel before an exhaustion event occurs.

The exact round31 movement guard is **not established** by this release replay: it does not record the private mode/target or decision fuel. The movement could come from full pathing, native `move_towards`, greedy fallback or a tactical local step. Assigning it specifically to the 31k/20k movement guards would require an additional trace, which was not run. There is no stale-list witness and no proven causal chain from this first one-tile difference to the final loss.

## Concrete weaknesses in the resulting game

The final bot collects **1,050 gems**, but delivers882, loses124 and still holds44 when the opponent finishes. Three deaths account for all lost gems: Ren36 at round128, Ryth44 at430, Issac44 at585.

Ren starts submission at **215/900 HP with36 gems in round125**, after killing Prism, and dies at `(17,9)` in round128 before delivery. This matches the inherited preference to bank nearby while badly hurt and then persist in the channel. At round585, Cassi dies and takes Issac with her while Issac carries44 gems. The control also has a coupled-life gem loss, at round386. These are concrete existing policy weaknesses in the encountered states; neither establishes that the new cache caused those states.

The justified follow-up is to remove unnecessary single-use cohort overhead and obtain a narrow trace of the first movement divergence before changing combat policy. The current source remains frozen. Fewer fuel events (22 versus50/85 in the two controls) alone did not prevent this regression.

`loss-followup.json` pins all replay records, hashes, command excerpts, reserve comparisons and unresolved attribution.

# Next hypothesis: bound the age of a propagated join

Implemented and frozen as v19 after the complete250-game v92 audit. See AGE-V19.md;the predeclared hypothesis below remains the original request.

The shared protocol fixes the selected first-cycle failure: Preyas elk A,
game b65f98bf-65bd-46dc-bbfd-b84782ec628c, unit4 authorizes at175; unit0 Stellar
joins176 rather than continuing to rally200. The same game reveals a later
case: unit4 authorizes516; Stellar joins560,44 rounds after the decision.

Read-only native replay probes from each own champion's perspective show
Stellar dead at the beginning of516,517 and540. At560 it is alive at(7,30),
full1125 health. Cassi3 and Issac4 are dead,Ren2 is498/1200 health at(20,23),
Heart1 is at(7,16),Ryth5 at(19,26). These are beginning-of-round snapshots,
not the exact later per-champion inputs. Their engine/replay hashes and terminal
36/1044 bank agree with the official statistics. Probe request/results are under
live/shared-20261021-r1/shared-diagnostics/. They do not establish that the late
join caused a death,or that suppressing it will win.

V18 records receipt before dead/shop/healing/banking early returns. A receiver
can therefore retain an authorization until much later in the240-round campaign.
The first receipt round is not logged in v18. Do not call its exact age measured:
44 is the age of the authorizing decision,not a directly observed receipt timer.

Predeclare one next experiment from frozen18: allow a propagated join only
within16 rounds of that instance's first receipt. An older cached decision
falls through to the unchanged local staging/quorum check;it does not cause
an unconditional join. Keep the local quorum authorization,65% entry health,
50% ally health,distance5,80% quorum,120/360/240 clock,two-round message protection,
combat/survival/banking,draft/model/RNG and initialization reserve unchanged.
Log receipt age on joins and rejected stale joins so the hypothesis is testable.
No new map/opponent-name strategy cases.

Sixteen is a predeclared development choice to preserve immediate joins while
rejecting the44-round case,not a value selected from confirmation outcomes.
Current tag delivery remains best effort: late initialization/reset can first
observe an old tag. This change cannot infer an unencoded global send timestamp.
Already-latched local release after later death is also outside this experiment.

Measure prompt first-cycle shared release,late-join counts,fresh objective gems,
credited sole-group campClear,deposits,deaths and runtime. Repeat the same broad
procedural sole/split development fixtures and both seats. Reject a change that
only hides joins or stalls squads without useful play. Keep formal promotion
separate;70 fresh confirmation maps stay unplayed.

The generic campfoe rule is another possible interruption,but the source branch
alone is not trace evidence that it caused this failure. Do not disable it in
the age experiment or combine other combat/draft/timing changes.

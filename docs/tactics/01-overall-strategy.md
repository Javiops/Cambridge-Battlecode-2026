# Overall strategy

**Chapter 01 of 12** · [Tactics index](README.md)

The objectives and tradeoffs that guide every champion.

## Contents

1. [Win condition](#1-win-condition)
2. [Score awareness](#2-score-awareness)
3. [Gems versus gold](#3-gems-versus-gold)
4. [Aggression level](#4-aggression-level)
5. [Game phases](#5-game-phases)
6. [Power spikes](#6-power-spikes)
7. [Opportunity cost](#7-opportunity-cost)
8. [Playing ahead or behind](#8-playing-ahead-or-behind)

This chapter uses the [16 October reference snapshot](reference-snapshot-2026-10-16.md). The pinned repository source is not a confirmed byte-for-byte match to the screenshot's live v43. Implemented describes reachable source behavior; Planned identifies a material missing condition. This documentation audit ran no bot builds, matches or competitive experiments.

## 1. Win condition

Optimize for tributed gems, accounting for the 1,000-gem victory threshold and 2,000-round limit.

**Status:** Planned

**Tactic:** Make completed tribute the primary objective: carried gems are potential score until banked. Prefer a delivery that can reach 1,000 before the opponent; otherwise compare feasible tribute by the deadline, then the game's tiebreaks. Stop a farm or fight whose credible completion and delivery time cannot improve that result. Use gold and kills as supporting means, except when their tiebreak becomes relevant.

**Current behavior:** The reference changes to late banking at round 1,850 and tries to bank any positive bag when this branch is reached. Higher-priority survival, combat and recall branches can still consume the turn; there is no explicit winning-delivery or deadline calculation. The official rules saved on 16 October 2026 specify 1,000 tributed gems to win; at the 2,000-round limit, compare tributed gems, lifetime gold earned, champion kills, then award a complete tie to Team B. A local runner's earlier stop is a separate experiment setting. [Official rules](https://2026a.battlecode.co.uk/game/docs); [late-bank branch](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3152-L3199); [earlier priorities](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2740-L3150).

## 2. Score awareness

Adjust decisions according to both teams' scores and how close either team is to winning.

**Status:** Planned

**Tactic:** At each new decision, compare both teams' banked scores, credible bags and earliest delivery times. If our safe delivery wins, protect its completion; if an enemy delivery wins first, choose a feasible interruption, denial or faster conversion. Recompute after a score, death, capture, lock or channel change. Fall back to the ordinary risk and income policy when a necessary observation is unavailable; do not invent an unseen enemy bag or position.

**Current behavior:** The action policy reads the owner's bag and visible enemy bags. Enemy target scoring rewards low health, channeling and carried gems, but the baseline does not query team score to choose a finish, protect a lead or force an interception. The constant late-round threshold is not score awareness. [owner observations and channel guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2756-L2787); [visible-enemy observations and target score](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2803-L2887); [bank trigger](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3152-L3199).

## 3. Gems versus gold

Balance immediate scoring against investments that improve future farming and fighting.

**Status:** Implemented

**Tactic:** Rank eligible camp groups by estimated personal reward per estimated travel, clear, capture and recovery time. Gold has weight 0.25 before round 600 and 0.24 thereafter, alongside gems; sharing reduces value, with a 0.75 exponent for non-monolith camps of at least 3,000 HP and an even split otherwise. Penalize camps still needing company and retain the current target with a 1.25 multiplier to reduce switching.

The active no-gold filter normally excludes groups with no gems. Its exception is runtime monolith-only economy: at least one gem-bearing monolith and no gem-bearing non-monolith group. That enables gold-only groups and can increase monolith staffing; it does not force every actor to attack a monolith or disable monoliths globally. The general banking-cost flag is 0, while Expanse/Monolith receive the separate active return-cost term. These are heuristic exchange rates, not measured optimal values. Earlier combat, recovery and banking decisions can override the camp choice. See [08](08-farming-and-capture.md) and [11](11-shopping-and-investment.md). [monolith feature gate](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1153-L1160); [camp value and filters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1825-L1918); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L1-L20).

## 4. Aggression level

Decide how much risk to take based on strength, information, carried gems, and available objectives.

**Status:** Planned

**Tactic:** Accept a fight or contested objective only when the available legal actions and credible enemy reply justify its health, cooldown, death and delivery risk. Increase the required advantage for a large bag or an uncertain route. End pursuit when the target escapes useful reach, support cannot arrive in time, or a safer scoring opportunity becomes better; use a legal escape, protected channel or productive camp as the fallback.

**Current behavior:** Risk is a branch hierarchy rather than one common value model. Spawn healing and emergency escape precede ordinary combat, recovery and banking. Emergency thresholds are below 35% HP for the qualifying caster draft and below 25% otherwise. Active kite/front routines can precede the generic numerical engage test, which asks for at least as many nearby allies and 120% of enemy aggregate HP. The generic below-50%-HP avoidance check comes later than those routines. Visible enemy bags affect target choice, but the owner's dedicated carry modifier is disabled. Do not describe this as universal survival-first or bag-protection logic. See [07](07-combat-and-survival.md). [active risk hierarchy](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2910-L3089); [carry and monolith defaults](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L108-L122); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L21-L50).

## 5. Game phases

Define how priorities change between the opening, economic development, contested play, and the finish.

**Status:** Implemented

**Tactic:** Begin with draft/map initialization, fixed purchase-plan construction and the ordinary action ladder; then keep choosing local combat, recovery, conversion and farming opportunities. The explicit global time changes are the camp gold weight at round 600 and late banking at round 1,850. They alter a heuristic inside the existing priority order, rather than switching the whole team into a new synchronized state.

Geometry also changes the rules. On Rows, the chain-farm bag limit is 60 instead of 36; after more than 40 rounds without an observed enemy, the ordinary bag target becomes 48 instead of 12. A nearby altar or late-bank trigger can lower the effective delivery threshold. Stop interpreting these constants as a universal safe opening, economic phase or finish guarantee: combat and recovery still run before ordinary banking. [initial purchase-plan construction](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L997-L1027); [time-dependent gold weight](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1825-L1831); [turn setup](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2740-L2787); [Rows and late-bank changes](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3152-L3199); [active parameters](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L1-L20).

## 6. Power spikes

Recognize when purchases, available abilities, or returning teammates create a temporary advantage.

**Status:** Planned

**Tactic:** Recognize a power spike only after the relevant purchase, ability readiness or teammate arrival changes a concrete legal action sequence. Compare that sequence with the enemy reply and the next productive alternative. Commit only within the useful window; stop or reassign when the ability is spent, the target leaves reach, the ally cannot arrive, or banking becomes more valuable. A purchase alone is not a team engage command.

**Current behavior:** Fixed shopping and combat routines use installed stats and available actions, but there is no shared readiness/arrival plan or team-wide spike schedule. The turn also caches maximum HP and gold before shopping, then reads current HP afterward; the resulting health ratio is not guaranteed to use a newly increased maximum HP on that same decision. The active group/help flags do not provide the richer contract in [06](06-team-coordination.md). [shopping observation order](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2756-L2787); [combat decisions](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2978-L3089); [disabled group modes](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L181-L190); [help and danger defaults](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L359-L367).

## 7. Opportunity cost

Compare every fight, journey, recall, or waiting period with what the champion could accomplish elsewhere.

**Status:** Planned

**Tactic:** Compare actions over a common useful horizon: time to the next reward or prevented loss, including travel, waiting, clearing, capture, recovery, delivery and the opportunity left to teammates. Include the chance that an objective or ally is gone when we arrive. Abandon a stale or dominated plan when a fresh feasible alternative is better; fall back to a low-risk productive action when the comparison is too uncertain.

**Current behavior:** The camp selector approximates travel, clear time, a fixed six-round overhead, incoming damage and a recall/heal/return cycle. It adds a specialized bank-trip cost on Expanse and Monolith. An optional extra capture-recall separately prices return distance: healing must beat a cutoff clamped between 65% and 90% HP, or non-Tavi spending must meet 90 + 3 times the return walk capped at 50. An unavailable path rejects that optional extra trip. These partial models do not compare every fight, delivery, recall and wait on one value scale. [camp time model](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1892-L1912); [optional return-trip test](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2686-L2737); [ordinary recall exceptions](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3092-L3140).

## 8. Playing ahead or behind

Decide when to protect an advantage and when a losing position requires greater risk.

**Status:** Planned

**Tactic:** When ahead, protect the deliveries and reliable income needed to remain ahead; avoid a fight whose plausible loss hands over the winning bag. When behind, seek a feasible change in scoring rate, objective ownership or delivery order, and take extra risk only when the safer continuation is unlikely to recover. Reassess from score, remaining time, actionable information and available routes, rather than from kills alone. If those estimates are missing, keep a productive conservative fallback.

**Current behavior:** Enemy-doorstep and far-enemy-half camp penalties, danger alerts, a caster hold-area bonus and generic combat thresholds can look defensive, but they do not depend on the actual score margin. Likewise, chasing a valuable visible enemy does not establish a deliberate comeback plan. Lead protection, loss recovery and urgency tied to opponent finish time remain to be implemented. [geographic camp preferences](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1865-L1912); [enemy target scoring](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2878-L2887); [fixed finish heuristic](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3152-L3199).

---

[Tactics index](README.md) · [Map understanding and adaptation →](02-map-understanding.md)

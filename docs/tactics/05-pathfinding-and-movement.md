# Pathfinding and individual movement

**Chapter 05 of 12** · [Tactics index](README.md)

How each champion reaches a useful position safely and efficiently.

## Contents

1. [Route selection](#1-route-selection)
2. [Destination selection](#2-destination-selection)
3. [Immediate step selection](#3-immediate-step-selection)
4. [Dynamic obstacles](#4-dynamic-obstacles)
5. [Hidden blockers](#5-hidden-blockers)
6. [Unsticking and loop prevention](#6-unsticking-and-loop-prevention)
7. [Dash usage](#7-dash-usage)
8. [Arrival timing](#8-arrival-timing)

**Source scope:** The [reference snapshot](reference-snapshot-2026-10-16.md) pins the inspected bot at `a0c0fa2`, including its checked-in `params.h`, and explains the unconfirmed live-upload identity. **Implemented** means the stated reachable source behavior; **Planned** retains material policy work. This completion adds no build, simulation or performance validation.

## 1. Route selection

Choose routes according to travel time, danger, destination value, and the champion's current task.

**Status:** Implemented

**Tactic**

For an ordinary task route, remove currently blocked goal tiles, then use the native distance field from useful goals toward the acting position. Static blockers are walls, holes, altars and enemy spawn; each normal turn adds visible champion/camp tiles and clears the acting tile. When the fresh local volley model applies, first try a lower-danger neighboring tile if current estimated damage is at least70% of current HP; otherwise exclude nearby tiles meeting that threshold from this route attempt. This is a local heuristic, not a global minimum-risk route guarantee. Active `P_VOLLEY_FIGHT=0` excludes the helper overlay in fight/front/kite/fm-engage/twin modes; `P_VOLLEY_FARM=1` leaves it available in farming. Combat micro has its own local movement heuristics.

**Conditions**

- Run only when a higher-priority action has selected a movement goal and movement or an allowed ready dash is still possible.
- Return without movement for an empty goal set, arrival inside it, an unavailable action, or a volley-constrained route with no field. Existing channels and the main turn’s low-fuel gate yield before normal routing.

**Exceptions and fallback**

With insufficient field-computation fuel (`fuel_ok(25000)` false), use `move_towards` on the nearest remaining goal by Chebyshev distance. Other failed fields use jam recovery or the same SDK fallback. The low-fuel shortcut does not preserve every heuristic risk wall; do not describe it as a certified safe route.

**Implementation:** [Exact route helper and fallback order](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1362-L1485), [Channel/fuel gates and dynamic blocker refresh](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2740-L2800), [Pre-sweep precedes normal turn planning](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3594-L3622), [Exact volley-mode scope](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1344-L1360), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L24-L51).

## 2. Destination selection

Navigate to a useful, legal interaction tile rather than directly onto an occupied or impassable target.

**Status:** Implemented

**Tactic**

Route to a legal interaction region rather than blindly onto the target’s occupied tile. Combat/camp engagement builds the current basic-attack-range region around the selected target; the blocker mask removes occupied/impassable cells. Banking uses the altar’s adjacent region. Reward capture uses the camp group’s spawn mask. A not-yet-ready camp uses its explicit staging ring, and recovery uses the own-spawn region.

**Conditions**

- Build the region for the current task and current target/range. Exclude blocked destinations and remove the current tile when probing an unseen camp would otherwise make arrival a false success.
- Stop ordinary travel when the body is already in the useful goal set; then let the caller attempt the actual attack, capture hold, submission or recovery action. A position alone does not prove that action succeeded.

**Exceptions and fallback**

If no useful goal remains, return failure to the caller or choose a different objective; do not substitute a target centre that is illegal to occupy. Retain SDK legality/result checks after movement. Actual combat spell range may differ from the basic-range approach, so this helper is not a universal spell-position optimizer.

**Implementation:** [Engagement interaction region and action order](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1553-L1566), [Altar approach/submit](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2138-L2162), [Five-tile rally ring](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2535-L2542), [Capture, respawn staging and unseen-camp goals](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2583-L2640).

## 3. Immediate step selection

Choose the next tile with enemy ranges, visibility, allied positions, and escape options in mind.

**Status:** Planned

**Tactic**

Choose the next legal action position from current personal observations and the task’s required follow-up. Compare incoming ready actions, retained attack/cast access, useful nearby support and an actual escape route; include a deliberate hold when moving sacrifices a more valuable legal cast or channel. Nearby allies count as possible support only after checking what is actually known of their reach/readiness. Re-read position and target legality after an earlier cast, attack or movement changes the state.

**Conditions**

- Apply before a normal step, combat reposition or dash landing; re-evaluate after a revealing or displacement action.
- Yield to an imminent survival/protection need or to the active useful channel. Stop chasing a target when its credible action window or task value disappears.

**Exceptions and fallback**

Use the current legal local heuristic when a richer next-action comparison is unavailable. An unseen threat is uncertainty, not zero danger; a visible ally is not a guarantee of its next action. See [Chapter 07](07-combat-and-survival.md) for the authoritative combat decision order.

**Current behavior:** `P_SAFESTEP=1` backs away using threat count, distance to an observed ally above 40% HP and distance home. Active caster kiting scores enemy reach, spell/basic range and distance from local mates. `P_KITE=1`, `P_KITE_ZONE=4`, `P_KITE_OUT=2`, `P_FRONT=1` and `P_KITEFRONT=0` mean a successful kite branch returns before front-line handling. These heuristics do not implement the complete readiness/escape/information policy.

**Implementation:** [Existing ready-damage approximation](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L865-L881), [Safe-step threat-count score](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L130-L179), [Kite local step score](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L458-L550), [Kite precedes front-line fallback](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2970-L2985), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L28-L51).

## 4. Dynamic obstacles

Replan when champions or monsters block an otherwise useful route.

**Status:** Implemented

**Tactic**

Rebuild dynamic occupancy from visible champions and camps each normal turn. If a native route fails and local volley exclusions were not the reason, `P_UNJAM=1` may compute a planning field through champion positions while retaining static terrain and visible camps as blockers. This alternative field is a direction hint, not permission to walk through another body. Try SDK steps and respect rejection; then try the normal fallback and, if still movable, a free reached neighbor no more than one field-distance step worse.

**Conditions**

- Use after a task goal has been selected and the occupancy-respecting field cannot reach the current position.
- Do not discard active volley exclusions to solve a jam. End the attempt after a successful action, no legal candidate, unavailable movement or exhausted helper fallback.

**Exceptions and fallback**

A dash landing and the final free-neighbor rescue check the original blocked mask. Ordinary `df.next_moves_from` candidates are still checked by the actual SDK action, even when the alternative field ignored a champion. Rebuild next turn instead of treating a failed move as proof the obstruction is permanent.

**Implementation:** [Fresh dynamic occupancy](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2793-L2800), [Unjam field, SDK steps and final local rescue](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1427-L1484), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L24-L25).

## 5. Hidden blockers

Handle movement failures caused by unseen occupants and use the newly revealed information.

**Status:** Planned

**Tactic**

When a move attempt fails, distinguish current action unavailability from a newly revealed occupant or terrain/target error using actual SDK state. Re-read the acting position, personal visibility and useful goal legality, then update the local route. As the initial planned retry bound, allow one replan after genuinely new blocker information in the same turn; repeated attempts against an unchanged obstruction yield instead of consuming the remaining decision budget.

**Conditions**

- Start on an ordinary-movement failure for which the task is still useful and enough fuel/action availability remains.
- Stop retrying if no new information arrives, the body has already moved, the target is invalid, or a combat/channel priority takes over.

**Exceptions and fallback**

Preserve the known useful objective or select a reachable alternative next turn. Do not infer an unseen blocker’s identity/team merely from failure, and do not assume failure always costs no action. Information acquisition remains governed by [Chapter 04](04-vision-and-information.md).

**Current behavior:** Current movement catches false/throwing actions and tries another field step or fallback. Its `s.blocked`/`s.vis` snapshot is not explicitly rebuilt inside that helper after a hidden-occupant failure. The camp-specific probe counter abandons after more than three failed approach calls for 25 rounds, but there is no general failure-reason-aware reveal/replan protocol.

**Implementation:** [Current generic exception/result wrapper](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L489-L499), [Current repeated SDK step/fallback attempts](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1462-L1484), [Hidden-camp probing and temporary exclusion](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2625-L2640), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L24-L25).

## 6. Unsticking and loop prevention

Detect repeated failures, oscillation, and routes that make no meaningful progress.

**Status:** Planned

**Tactic**

Track progress against the current goal/task, not just tile changes. Exempt useful attacking, capturing, channeling, recovery and scheduled waits. Detect an unchanged-goal A→B→A return without productive progress, then re-evaluate the blocked edge and destination once; release or temporarily exclude an unproductive task if it remains unresolved. A necessary kite, dodge or changed objective is not an indecision loop.

**Conditions**

- Apply when the same task repeatedly fails to get closer or perform useful work. Reset history after a real goal/task change, confirmed productive action or respawn.
- Stop the recovery branch once a useful action or route is restored, or yield to survival/banking priorities. Do not force a move simply to clear a counter.

**Exceptions and fallback**

Use the existing stationary and camp-probe safeguards as bounded fallback. The full progress window/exclusion tuning remains unvalidated; do not claim that the source already detects general route oscillation.

**Current behavior:** `P_UNSTICK=30` handles a body at one tile for 30 normal turns, outside spawn, with nearest visible foe farther than 4, no nearby awake camp, and no recent active capture hold. It temporarily excludes the target for 30 rounds, tries banking, then safe recall or home movement if below 90% HP, and clears the counter if continuing. It does not detect A→B→A movement. `P_E_RETARGET=6` refreshes only uncommitted farm travel; damaged camps/capture holds have separate persistence.

**Implementation:** [Six-round uncommitted retargeting](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2451-L2463), [Approach probe counter](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2625-L2640), [Same-tile counter](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2793-L2794), [Thirty-turn stationary recovery](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2890-L2908), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L24-L25).

## 7. Dash usage

Decide when a dash is worth spending for travel, engagement, escape, or crossing holes.

**Status:** Planned

**Tactic**

Spend a dash when its useful travel, engagement or escape action outweighs losing that cooldown during the next credible threat window. Query the kit’s actual range, target/landing restrictions and movement compatibility. For hole crossings, model a legal ability transition separately from ordinary walking; verify the landing and subsequent action/escape route before committing. Saving a dash is a valid action when ordinary travel already meets the deadline.

**Conditions**

- Consider only a ready, currently castable dash and a legal landing that changes the task’s next useful action or escape timing.
- Abandon the dash if its target/landing is stale, it loses required combat readiness, or survival/channel obligations dominate. Re-read actual position and remaining movement after success.

**Exceptions and fallback**

Walk, hold or choose another route when no useful legal dash exists. Do not infer that a generic two-tile scan covers all future kits or that a landing across terrain proves a return route. Enemy dash readiness affects the threat estimate, not our permission to dash.

**Current behavior:** The travel helper dashes only when the field distance is at least 3 and a landing within offsets [-2,2] is unblocked, walking-reached and improves field distance by at least 2. It then tries an ordinary step if `can_move()` remains true. That greedy travel rule has no explicit future cooldown reserve or ability-only connectivity graph. Active safe-step escape has a separate local threat-reduction rule.

**Implementation:** [Dash slot discovery](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1250-L1258), [Current travel dash rule](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1442-L1460), [Engage dash permission](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1553-L1566), [Enemy near-ready dash reach](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L69-L102), [Current escape dash score](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L145-L164), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L75-L82).

## 8. Arrival timing

Coordinate arrival with camp respawns, teammate support, enemy movement, and objective availability.

**Status:** Planned

**Tactic**

Compare an observed route/action ETA with the task’s actual window: camp respawn, capture completion, banking channel, useful ally action or enemy arrival. If early, stage on a legal tile outside the relevant threat/camp envelope rather than consume health or block the collector. If late or unsupported, release/reassign the task instead of treating a claim or nearby ally as a completed rendezvous. Preserve actual capture progress only while its required presence remains useful.

**Conditions**

- Plan timing after choosing a task and refresh it after a blocker, threat, readiness change or earlier actor changes the objective.
- End assembly when the useful window closes, survival/protection takes priority, or the task is completed/abandoned. Do not wait indefinitely for unobserved allies.

**Exceptions and fallback**

Use existing respawn staging and local rally distances when a richer ETA model is unavailable. Missing ally position/readiness is uncertainty, not zero travel time. Shared arrival contracts and finite group assembly are authoritative in [Chapter 06](06-team-coordination.md), capture timing in [Chapter 08](08-farming-and-capture.md).

**Current behavior:** `P_RESPAWN=4` admits a respawning target when its remaining wait is no greater than estimated travel+4; no-target healthy staging can use a five-tile ring, and near respawn staging uses distances2–3. Farm rally compares a required squad with nearby bodies/claims. It does not compute a shared action-window ETA, legal ready support or enemy interception forecast for the whole group.

**Implementation:** [Respawn eligibility and travel/wait estimate](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1871-L1896), [Local readiness/count rally and staging](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2516-L2542), [Capture hold timeout and respawn staging](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2599-L2623), [Channel/fuel yield conditions](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2784-L2791), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L17-L20).

---

[← Vision and information](04-vision-and-information.md) · [Tactics index](README.md) · [Team coordination and group movement →](06-team-coordination.md)

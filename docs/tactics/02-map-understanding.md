# Map understanding and adaptation

**Chapter 02 of 12** · [Tactics index](README.md)

The map features that shape routes, compositions, and objectives.

## Contents

1. [Map connectivity](#1-map-connectivity)
2. [Actual travel distances](#2-actual-travel-distances)
3. [Chokepoints and escape routes](#3-chokepoints-and-escape-routes)
4. [Walls and holes](#4-walls-and-holes)
5. [Bush geometry](#5-bush-geometry)
6. [Resource distribution](#6-resource-distribution)
7. [Altar accessibility](#7-altar-accessibility)
8. [Map-dependent planning](#8-map-dependent-planning)

**Source scope:** The [reference snapshot](reference-snapshot-2026-10-16.md) pins the inspected bot at `a0c0fa2`, including its checked-in `params.h`, and explains the unconfirmed live-upload identity. **Implemented** means the stated reachable source behavior; **Planned** retains material policy work. This completion adds no build, simulation or performance validation.

## 1. Map connectivity

Identify connected regions, isolated areas, and routes requiring special movement.

**Status:** Planned

**Tactic**

Build a walking-connectivity description from public terrain at initialization. Keep ordinary walking components separate from legal ability or consumable transitions. A camp, altar approach or return route is eligible for an ordinary journey only when at least one useful interaction tile is connected to the acting body. Treat a route that needs a dash or teleport as a separate plan with its own readiness, landing and channel requirements; do not silently count it as a walking connection.

**Conditions**

- Start when public geometry and the acting body are available; reconsider the local route after movement, a newly observed blocker or a changed destination.
- Stop pursuing the component route when its interaction set is unreachable or an interruption makes the ability transition unavailable. Yield to the combat/escape priorities before entering a trap.

**Exceptions and fallback**

Keep unknown or failed geometry reads distinct from proven isolation. Use the existing legal local movement fallback for the current turn, or choose another reachable objective; do not infer an invisible bridge or an enemy-free island.

**Current behavior:** The source builds `walls | holes | altars | enemy spawn` for ordinary movement and computes several reachability fields. It has no complete component graph with ability-only edges or explicit island classification. `P_ALTAR_REACH=1` attempts altar approach checks once from the initial position. The eligibility array starts permissive, so entries not checked after a failed probe remain allowed; this is narrower than the planned general connectivity policy.

**Implementation:** [Static walking blockers and altar reachability](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1083-L1104), [Spawn/altar distance caches](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1162-L1181), [Runtime movement and fallbacks](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1362-L1485), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L24-L40).

## 2. Actual travel distances

Measure traversable routes between important locations rather than relying only on straight-line distance.

**Status:** Implemented

**Tactic**

Use native distance fields where the active policy computes them. `P_PATHD=1` ranks camp travel by the minimum reached spawn tile of that camp group, with a 200-step search bound. It caches spawn-to-group and altar-to-group estimates for the economic cycle. Active altar routing (`br_policy=1`) computes up to 400 steps to legal adjacent approach tiles, then adds one to preserve existing altar-centre thresholds. These are task-specific distances, not a universal optimal travel-time model.

**Conditions**

- Compute the current camp field when choosing a target; refresh the altar plan when the round or acting position changes.
- A runtime step helper stops when already inside its usable goal set, unable to move/cast as allowed by the caller, or unable to find a successful action.

**Exceptions and fallback**

Camp selection falls back to Chebyshev centre distance when its field fails, or 1.5 times that distance when no group tile is reached. Failed/low-fuel altar planning uses the legacy penalized Chebyshev choice. The spawn/altar camp caches omit altar tiles from their blocker mask and are estimates; actual movement uses the stricter runtime mask and SDK legality checks. An approximate fallback is not proof of reachability.

**Implementation:** [Active path-distance configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L36-L40), [Economic distance cache masks](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1162-L1181), [Current walking distance and explicit approximations](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1850-L1864), [Altar approach distances and fallback](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1947-L2087), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L39-L40).

## 3. Chokepoints and escape routes

Identify places where champions can be trapped, intercepted, or prevented from reinforcing.

**Status:** Planned

**Tactic**

Before entering a narrow approach for combat, farming or banking, identify a legal retreat route and the tiles on which an observed enemy could cut it off. Evaluate the body’s next useful action and escape opportunity, not just the number of adjacent empty tiles. If the only exit can be denied before the commitment pays, stay on the reversible side, choose another approach or abandon that objective. A carrier should preserve a route to a usable altar or recovery area.

**Conditions**

- Apply before a new commitment through a corridor or around an objective, and after an enemy or blocker changes the exit geometry.
- End the commitment when no usable exit remains, the task finishes, or protection/escape takes priority. Do not wait for the stationary unsticking timeout to diagnose a threatened trap.

**Exceptions and fallback**

With insufficient information, retain a known legal retreat and request/obtain relevant personal sight under [04.1 Ward placement](04-vision-and-information.md#1-ward-placement). Do not label a tile safe merely because no enemy is visible. A numeric escape-slack margin remains an explicit future tuning decision.

**Current behavior:** The bot estimates local enemy reach and ready damage and can choose a safer adjacent step. It does not compute named chokepoints, independent escape corridors or interception deadlines. Those local heuristics do not implement this full trap/escape policy.

**Implementation:** [Local ready-damage heuristic](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L865-L881), [Immediate volley avoidance](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1368-L1405), [Threat-count retreat step](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L130-L179).

## 4. Walls and holes

Account separately for their effects on walking, vision, dashes, and teleportation.

**Status:** Planned

**Tactic**

Maintain separate questions for walking, sight, ability traversal and consumable relocation. Walls, holes, altars and the enemy spawn are blocked for ordinary route planning. For a dash or teleport, query the actual ability/item rules and legal landing set; crossing intervening terrain does not imply that the destination is legal or that the same route can be walked back. Personal sight must come from the engine’s visibility, rather than from the walking mask.

**Conditions**

- Apply whenever terrain lies between the body and an intended interaction tile, or when a special move would bypass the ordinary route.
- Reject the special route if its landing, cast/channel availability or required follow-up fails. Resume an ordinary legal route rather than repeatedly attempting an unsupported crossing.

**Exceptions and fallback**

Use a reachable ordinary goal if the kit-specific transition is unknown. Do not assume walls and holes have identical sight effects, that a dash can land on a hole, or that a teleport is instant. The authoritative relocation/consumable decisions belong in [11.6 Consumable budgeting](11-shopping-and-investment.md#6-consumable-budgeting).

**Current behavior:** Ordinary movement combines these blockers. The generic dash scans landing offsets within two tiles and rejects the existing blocked mask, but it requires a walking-reached destination and has no separate ability-edge planner. `P_TELE=0` disables the optional recall-versus-walk banking shortcut; that flag is not a general teleport legality model.

**Implementation:** [Ordinary static mask](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1083-L1088), [Generic dash landing scan](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1442-L1460), [Disabled recall-to-altar distance experiment](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1182-L1193).

## 5. Bush geometry

Understand where bushes conceal enemies and how entering them changes visibility.

**Status:** Planned

**Tactic**

Use actual personal visibility to distinguish a visible empty approach from a concealed or unobserved one. Before a high-cost bush entry, identify which hidden approach could change the next decision and obtain relevant sight when practical. Preserve an uncertainty bound for last-seen enemies; a camp or body absent from sight is not confirmed dead, absent or on cooldown. A new sight change can alter the immediate route or target.

**Conditions**

- Apply before entering occluded terrain, beginning an expensive camp exchange there, or following a target that leaves personal sight.
- Stop blind pursuit when the target’s legal interaction or escape route is no longer established; re-evaluate when new sight or a revealed blocker resolves the uncertainty.

**Exceptions and fallback**

Use the information policy in [Chapter 04](04-vision-and-information.md), not a separate bush-ward scoring rule here. If sight cannot be obtained, prefer a reversible approach or another objective rather than inventing a hidden enemy position.

**Current behavior:** The source reads `me.visible_tiles()` and visible unit positions, but does not analyze bush components or score occluded routes. Hidden-camp travel probes the group’s spawn tiles, abandoning after more than three failed approach calls for 25 rounds. `P_R5_WARD=0` leaves the optional ward helper disabled.

**Implementation:** [Personal visibility snapshot](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2795-L2800), [Currently observed foes and short movement history](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2803-L2844), [Hidden-camp approach and probe failure handling](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2625-L2640), [Post-turn utility gates](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3683-L3686), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L81-L82).

## 6. Resource distribution

Identify valuable farming regions, contested resources, and areas worth defending or invading.

**Status:** Implemented

**Tactic**

Build the public camp-group inventory once: spawn tiles/mask, a representative centre, nominal gems/gold, respawn timer, member count, camp health/strength estimates and whether any member is a monolith. Rank an eligible group using reward, travel/wait, estimated clear time, incoming camp damage, recovery cycle and current claims. The map description supplies inputs to farming; it does not independently order a fight or invasion.

**Conditions**

- At initialization cache up to 250 groups; during play refresh observed availability and cooldown beliefs before choosing the next farm target.
- Exclude temporarily bad groups and groups too early in their respawn cycle. With `P_NOGOLD=1`, skip gold-only groups unless `mono_only` is true. Yield to higher-priority combat, banking, healing and active channels.

**Exceptions and fallback**

If no target is eligible, the farming code may stage at the five-tile ring for an imminent respawn when healthy enough, request recovery, or return toward spawn. A failed inventory read is not evidence that the map has no resources. Detailed commitment, capture and collector rules are authoritative in [Chapter 08](08-farming-and-capture.md).

**Implementation:** [Public group inventory and monolith-only classification](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1124-L1160), [Observed group-state refresh](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1711-L1744), [Active group ranking](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1825-L1918), [No-target fallback](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2464-L2491), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L1-L20).

## 7. Altar accessibility

Evaluate each altar's approach routes, nearby threats, and usefulness within farming cycles.

**Status:** Implemented

**Tactic**

Exclude altars explicitly marked unreachable by the startup adjacent-tile check. The eligibility array starts permissive, and the checks share one exception wrapper: entries not checked after a failure remain allowed. At the current round/position, choose the reachable altar approach with minimum walking length plus the active lock, side and danger penalties; break cost ties by distance toward home and then altar index. Approach an unblocked tile within Chebyshev one of the altar; attempt submission there. A reachable altar is not automatically a safe one.

**Conditions**

- Recompute the private banking plan after a round or position change. `br_plan` requires `fuel_ok(50000)` and at most 64 altars; the distance search is bounded at 400.
- Use the selected approach only while the caller still wants to bank and can act. An existing submit/recall/teleport channel yields immediately in the normal turn logic.

**Exceptions and fallback**

Refresh an enemy-lock belief only from visible altar information; it adds a 40-round belief/40 cost penalty. `P_OWN_ALTAR=20` and a recent danger alert can add side/danger costs; `P_ALTAR_SAFE=0` disables the extra direct enemy-near-altar penalty. If planning fails, use the legacy choice and explicit approximate distance fallback. No altar yields no banking action.

**Implementation:** [Startup adjacent reachability](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1090-L1104), [Legacy choice and visible lock refresh](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1921-L1945), [Active walking policy, penalties and cache](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1947-L2087), [Approach and submit](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2138-L2162), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L16-L18).

## 8. Map-dependent planning

Adapt composition, grouping, aggression, and resource routes to map features.

**Status:** Planned

**Tactic**

Select a coherent plan from measured public geometry and the actual roster: reachable economy, banking cycle, likely contact areas and available escape routes. Keep topology-derived decisions usable on unknown maps; named-family presets may be explicit overrides, not proof that the map is strategically solved. Change a plan only when new geometry, resource availability, enemy contact or objective value invalidates its assumptions.

**Conditions**

- Choose an opening after draft-time geometry is available; refine per-body tasks after actual camp groups and controllable bodies can be read.
- Leave an aggressive/central plan when its readiness, economy or exit assumptions fail. A family label alone never overrides a current emergency.

**Exceptions and fallback**

For an unknown signature or failed probe, retain generic geometry/routing and the baseline draft instead of guessing a family. The composition policy is in [Chapter 03](03-champion-selection.md), grouping in [Chapter 06](06-team-coordination.md).

**Current behavior:** `P_D34_FAMILY=1` recognizes nine signatures and transports the label in draft-memory byte 28. All `P_D34_DRAFT_*` defaults are zero, so their recipe table does not replace the active spawn-path draft. Runtime family exceptions adjust some banking/farm costs. `P_MONO=1` is restricted by `mono_only`: a gem-bearing monolith must exist and no non-monolith group may offer gems. This is not general map-aware optimization or a globally disabled monolith tactic.

**Implementation:** [Nine public-geometry signatures](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/de_rules.h#L46-L63), [Spawn-path draft and inactive family recipes](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L651-L682), [Runtime mono_only guard](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1153-L1160), [Active family-specific economic adjustments](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1888-L1900), [Lanes capture-recall scope](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3106-L3124), [Rows banking/chain adjustments](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3159-L3185), [Active checked-in configuration](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L64-L73).

---

[← Overall strategy](01-overall-strategy.md) · [Tactics index](README.md) · [Champion selection and draft →](03-champion-selection.md)

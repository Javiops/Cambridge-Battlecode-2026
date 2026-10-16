# Vision and information

**Chapter 04 of 12** · [Tactics index](README.md)

What each champion and ward reveals and how the team uses that knowledge.

## Contents

1. [Ward placement](#1-ward-placement)
2. [Ward relocation](#2-ward-relocation)
3. [Personal vision](#3-personal-vision)
4. [Scouting responsibility](#4-scouting-responsibility)
5. [Enemy tracking](#5-enemy-tracking)
6. [Threat estimation](#6-threat-estimation)
7. [Opponent intent](#7-opponent-intent)
8. [Information sharing](#8-information-sharing)

**Evidence and status.** These are **planned tactics**, informed by official rules, engine probes, elite replays and LoL coaching principles. They are not an implemented or proven stronger bot. The [ward research](ward-research-2026-10-16.md) separates mechanics, observed behavior, original proposals, source revisions and validation limits.

**Current source reference (16 October 2026):** The intended tactics below are preserved. Current implementation is checked against [`bots/study27-economy` at `a0c0fa2`](reference-snapshot-2026-10-16.md), which supersedes the older source audit for present-code claims. The screenshot identifies upload v43; its exact source identity is not yet confirmed. Historical research and its limits remain unchanged.

## 1. Ward placement

Decide where, when, and how often each champion should place its ward.

**Status:** Planned

**Mechanics that drive the tactic**

- A ward is free, permanent and invulnerable. Each controlled body has one active ward; replacing it removes that body's old ward. Cassi and Issac have separate wards and separate personal sight.
- A champion's unobstructed sight reaches 8 tiles, including diagonals. A ward reaches 6; its center must be within 2 of its owner. Distances here are Chebyshev distances. Walls and bushes alter the actual sight masks; holes block movement, not sight.
- Consequently, a fresh ward adds **no immediate sight in an unobstructed open field**: `2 + 6 = 8`. Its open-field value is the observation that remains after its owner moves away. Walls and bushes can instead make placement immediately informative.
- One successful placement is available per owner turn: the recharge timer ticks at turn end and the charge returns at the next owner turn start. Placement does not spend the owner's move, basic attack or ability-cast allowance. It is unavailable while dead, stunned or channeling recall, tribute or teleport. Place before beginning a channel when useful; do not cancel a good channel merely to reposition a ward.
- The destination need not already be visible. A ward can be thrown across a wall within placement range. Walls, holes, altars, enemy spawn tiles and allied-ward-occupied tiles are invalid destinations. Champion and camp occupancy alone do not make a destination invalid. Always apply the actual SDK restrictions, handle failure, and stop retrying a rejected tile for that decision.
- A ward cannot capture a camp in place of a champion. Do not purchase, clear or defend wards using LoL routines: ordinary wards cannot be damaged, and the legacy control-ward consumable is not purchasable in this rules snapshot.

These facts are checked against the [official vision rules](https://2026a.battlecode.co.uk/game/docs/vision), public SDK and the engine probes linked in the research. The source of vision is personal; 04.3 and 04.8 govern its use by others.

**Tactic**

Give the ward a concrete observation job before scoring a tile. Protect the next important decision, considering both immediate occlusion and future remote monitoring. Prefer a useful position already within legal placement range. Do not walk into a losing fight or delay a necessary escape just to place a theoretically better ward.

| Situation / trigger | What the owner watches and does | When to keep, stop or change |
|---|---|---|
| A wall corner, bush or concealed branch could change the next move or target | From a legal tile, place on the informative side of the obstruction, re-read personal vision and visible enemies, then recompute the next action. A bush is useful only if its actual mask reveals a relevant branch. | Keep the old ward if it supplies more important information and the step can be taken or avoided without replacement. An open crossing needs no ward for immediate range extension. |
| Starting a camp fight, finishing its monsters, or waiting to capture | Observe the likely enemy entrance and a dangerous flank before spending health/cooldowns or committing to the hold. Prefer warning before enemies reach attack or interruption range; also inspect the target if it is hidden. If natural sight already covers the approaches, value only occluded information or coverage after planned departure. | Re-evaluate after new enemies appear, the last monster dies, the reward is claimed, or the team abandons the camp. The ward alone does not make farming safe. |
| Carrying gems toward an altar or preparing tribute | Watch the selected route's blind approach, the altar's contested access, or the retreat fork. Deploy beside a legal approach tile, not on the altar. Re-check whether to proceed before channeling. | Once already channeling, keep the channel unless the separate survival/tribute policy says to cancel. A stationary open-field ward inside natural sight adds no immediate protection. |
| Recalling or leaving a productive area | Before departure, consider leaving a persistent observer on a relevant enemy transition, camp entrance or return route. Its value is assessed from the owner's future location, including spawn. | Keep an existing remote watcher when it still informs the next mission. There is no expiry timer that requires a refresh. |
| Retreating, low health, or outnumbered | Use a legal no-detour placement to inspect an escape fork or blind flank if that information can change the escape. Prioritize the escape and available survival actions. | Stop scouting detours and expensive candidate searches. Do not automatically ward toward an old farming target while retreating. |
| Safe travel with no immediate uncertainty | Consider a persistent watcher at a meaningful region transition or off-path approach, with future value after departure. | Retain useful old coverage. Do not repeatedly place the ward at maximum range just because the charge is available. |

**Decision order and frequency**

1. At each owner turn, make a cheap readiness and mission-change check. Re-score after a move, new sighting, route fork, changed objective, completed camp or imminent departure; expensive mask searches need not run after every API call.
2. If unseen information could change an irreversible move, fight or channel decision, evaluate placement **before** that decision. After a successful placement, refresh observations and plan again; continuing with a stale pre-ward enemy list wastes its tactical value.
3. Otherwise, consider placement after safe movement when the new position offers a better observer. An earlier success consumes this turn's placement, so choose the timing deliberately.
4. Compare the candidate with retaining the existing ward under 04.2. Allow another placement next owner turn if the job has changed enough. There is no chosen fixed four/eight-round wait and no requirement to cast every round.
5. Bound queries and reserve fuel for movement, combat and ending the turn. If rescoring cannot finish, keep the old observer and take the safest available mission action while retaining an escape option.

**Current behavior:** The pinned reference still has [`P_R5_WARD=0`](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L82), so the late ward call does not execute. Its [dormant bush-only helper](https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/utility.h#L9-L81) is not the mission-aware policy above. The existing danger-byte protocol is active, but no new ward/report protocol is introduced here. This specification still requires implementation. [Historical source audit and test limits](ward-research-2026-10-16.md#our-existing-bot).

**Related decisions:** [Relocation](#2-ward-relocation), [Threat estimation](#6-threat-estimation), [Farming](08-farming-and-capture.md), [Gems and objectives](09-gems-and-objectives.md), [Recall](10-recall-and-recovery.md).

## 2. Ward relocation

Decide when moving a ward provides more value than continuing to monitor its existing location.

**Status:** Planned

**Tactic**

Treat replacement as exchanging one observation point for another. Score **both** the old ward and each legal candidate for the same owner, mission and predicted future positions. The old ward remains relevant even if far away from its owner.

For each meaningful future state—next step, camp hold, departure, retreat or post-recall location—compare the exact ward mask with the owner's predicted natural sight. Weight what is revealed by the decisions it can change:

```text
observer value = useful warning on relevant enemy approaches
               + concealed objective/flank information
               + discrimination between plausible enemy routes
               + useful persistent information after departure
               - unsafe detour, decision delay and fuel cost

replace when candidate value > retained old-ward value + switching margin
```

This is our proposed model, not an established optimal formula. The horizon, weights and switching margin remain parameters to measure. For the first placement, compare with no ward (zero ward contribution). On ties or insufficient confidence, retain the current observer. A first implementation should use a few planned waypoints and existing path fields, rather than an expensive full-map search.

A simple first prototype can use this priority order before tuning numeric weights: (1) information that can change this turn's imminent blind decision; (2) warning on the fastest credible approach to a committed objective or gem carrier; (3) relevant observation after planned departure; (4) other useful route discrimination. Within the same priority, compare the timing and breadth of relevant approaches covered, including what the retained old ward supplies. This ordering is an explicit starting hypothesis, not a measured optimum.

**Conditions and exceptions**

- Do not require immediate new pixels: it would reject every open-field ward by construction. Equally, do not interpret a large mask as useful information without a mission.
- Do not compare only `candidate mask minus current effective vision`; that ignores the old remote coverage being removed. Evaluate keep-versus-replace counterfactuals.
- When a ward watches the only credible approach to a gem carrier, an active camp or a return route, preserve it until that job ends or an alternative covers the job better.
- Re-score when the objective changes, the owner leaves the region, an observed enemy takes another route, or a previously blocked view becomes useful. Do not replace at the same coordinate as a routine refresh.
- Never subtract an ally's ward footprint as if it were shared vision. A fresh communicated warning may substitute for a narrow piece of information, with its delay and uncertainty; it does not substitute for direct sight needed for a legal target.

**Related decisions:** [Placement](#1-ward-placement), [Personal vision](#3-personal-vision), [Enemy tracking](#5-enemy-tracking).

## 3. Personal vision

Plan around each champion seeing through its own vision and ward, with teammate sightings communicated separately.

**Status:** Planned

**Tactic**

Use the engine's current personal mask for legality and the hypothetical owner/ward masks for planning. Account for temporary tile reveals separately. Walls and bushes require actual shadowcasting, not a radius square or distance-to-bush proxy.

Entering or placing inside a connected bush can reveal across that bush; a separate bush remains occluded. A ward on one side of a wall may expose a branch hidden from the owner. Test the actual candidate mask because a nearby wall or map boundary can remove most of its nominal area.

Re-query enemies, camps and action preconditions after a ward changes the view. A teammate report is a belief until this owner can legally observe or target the object. Two owners may rationally need overlapping sight masks from distinct legal ward tiles in a contested bush because their pixels are not shared. Cassi and Issac follow the same per-body rule.

Keep the distinction between static knowledge and dynamic presence. Knowing the map's wall or bush layout does not prove the location is enemy-free. If full map geometry is already known, do not reward discovering it again.

**Validation required:** Engine-mask agreement, hidden-enemy reveal and legal follow-up actions, multiple bush components, wall corners, transient reveals and the Cassi/Issac split.

## 4. Scouting responsibility

Decide who checks contested camps, suspicious bushes, altar approaches, and enemy movement.

**Status:** Planned

**Tactic**

The champion whose next decision depends on the information should normally establish its own observation. Another champion can scout a strategic approach when it can publish a usable warning, but cannot lend direct tactical vision to the protected owner.

Allocate remote jobs across bodies: front approach, flank, return corridor or enemy region transition. Prefer an observer already passing within placement range, with enough health and mobility for the route it is actually taking. A ward is invulnerable; its owner is not. Do not create a dedicated unsafe scouting trip solely to improve map coverage.

When grouping, preserve separate direct sight where multiple bodies need to fight through the same obstruction. Where direct sight is not needed by every body, distribute strategic watchers and communicate high-priority observations. Do not assume the team's wards form one shared camera network. Death preserves a body's ward sight and dead bodies still receive turns; continue useful observation/reporting when possible rather than discarding a remote camera solely because its owner died.

**Stop:** Once a job no longer affects a planned action, release it for reassignment. If an observer stops publishing fresh reports, the absence of a warning is not proof the approach is clear.

**Related decisions:** [Team coordination](06-team-coordination.md), [Information sharing](#8-information-sharing).

## 5. Enemy tracking

Remember last-seen enemies and increase uncertainty as those observations become older.

**Status:** Planned

**Tactic**

Locally store who was observed, where, in which round and phase, and whether the source was direct sight or a team report. Expand a missing enemy's plausible positions using elapsed opportunities, walkable connectivity and known movement abilities. Treat unobserved movement and unknown cooldowns conservatively.

A useful watcher distinguishes routes: one exit seen empty now can reduce the plausibility of that route at that time. A ward failing to show an enemy does not establish safety elsewhere, behind a shadow, or in a different bush. Do not preserve an exact coordinate as a current attack target after the sighting becomes stale.

Use the resulting uncertainty to choose which branch a ward should observe and whether the next camp or channel remains sensible. Full probabilistic tracking is a later implementation step; a small number of timestamped plausible routes is an acceptable first design.

## 6. Threat estimation

Estimate danger from visible enemies and plausible threats outside current vision.

**Status:** Planned

**Tactic**

Judge a warning by whether there is time to react, using movement paths and abilities rather than straight-line distance through walls:

```text
warning slack = earliest plausible enemy time from detection to dangerous contact
              - time needed to escape, reposition or finish/cancel the commitment
              - report/read delay when another owner must react
```

Prefer coverage of relevant approaches with enough warning to change the action. Check the fastest credible uncovered route as well as the average route; one well-covered long approach must not conceal a short blind flank. Account for turn order, dashes, attack range and interruption range. If these are uncertain, lower confidence rather than declaring the route safe.

For farming, include current monster pressure, friendly resources and enemy reinforcement time. A ward that reveals an approaching group should trigger a new fight/farm/retreat decision before another expensive camp action. For tribute, include the vulnerability window and carried-gem stake. The detailed fight and channel policies remain authoritative for their actions.

**Fallback:** Without enough information to rule out a plausible dangerous approach, retain an escape option or choose another action. Do not turn missing information into a zero-threat estimate.

## 7. Opponent intent

Infer whether opponents are farming, grouping, invading, retreating, or preparing to tribute.

**Status:** Planned

**Tactic**

Use sequences of fresh observations to distinguish plausible plans: repeated travel toward an altar, several bodies converging on one entrance, or a group leaving a depleted region. Choose a watcher that can discriminate between the most consequential alternatives. Do not infer intent from one ward coordinate, one champion type or an empty camera alone.

Keep the inference conditional and update it on contradictory sight. Observing a rotation can justify retaining a remote ward or moving the next one to an exit; it does not prove the opponents will follow their shortest route. Elite replay patterns provide candidate habits, not a hardcoded promise about a team or an unseen map.

**Fallback:** If no credible intent separates the alternatives, use the current mission's threatened approaches and preserve uncertainty.

## 8. Information sharing

Choose which sightings and warnings deserve the team's limited shared memory.

**Status:** Planned

**Tactic**

Separate private observation, local memory and team messages. Share the highest-value timely warning: an approaching group, a gem carrier's threatened route, a relevant enemy location or an objective becoming unsafe. Include enough identity/location, observation age and alert meaning for the intended reader to act. Resolve competing writers deterministically so a routine observation cannot overwrite an urgent warning.

Each team has **8 writable shared bytes**, not a shared vision map. The draft's larger memory is frozen during play. The audited source allocates bytes 0–4 to camp claims, 5–6 to camp status and byte 7 to the **active danger alert** when `P_CALLHELP=0`; enabling help uses that byte instead. A new vision protocol needs an explicit layout migration and compatibility check. Do not treat all eight bytes as free or silently overwrite existing coordination. This corrects the earlier description of byte 7 as merely optional help; [source proof](shopping-research-2026-10-16.md#shared-memory-correction).

Do not prescribe a packed message format until verified coordinate limits, round wrapping, body identities, writer ownership and existing fields fit. Specify expiry, priority, missing-data behavior and reader timing before implementation. Reports are approximate, potentially delayed information. A report never grants sight or bypasses SDK targeting restrictions.

**Validation required:** Competing writers, stale alerts, round/timestamp wrap, map coordinate bounds, Cassi/Issac identities, observer death and continued camp-claim correctness. Measure how a received warning changes the recipient's decision, not merely how many messages were written.

---

[Research, elite replay evidence and LoL transfer](ward-research-2026-10-16.md) · [← Champion selection and draft](03-champion-selection.md) · [Tactics index](README.md) · [Pathfinding and individual movement →](05-pathfinding-and-movement.md)

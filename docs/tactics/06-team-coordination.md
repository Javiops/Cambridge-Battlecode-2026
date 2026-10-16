# Team coordination and group movement

**Chapter 06 of 12** · [Tactics index](README.md)

How champions divide work, support each other, and move as a team.

## Contents

1. [Role assignment](#1-role-assignment)
2. [Grouping versus splitting](#2-grouping-versus-splitting)
3. [Group size](#3-group-size)
4. [Formation and spacing](#4-formation-and-spacing)
5. [Group travel](#5-group-travel)
6. [Reinforcement decisions](#6-reinforcement-decisions)
7. [Collective retreat and regrouping](#7-collective-retreat-and-regrouping)
8. [Shared commitments](#8-shared-commitments)

**Evidence and status.** These tactics are **Planned**, not implemented by this document. The [coordination research](coordination-research-2026-10-16.md) separates replay behavior, mechanics, source-derived failure hypotheses, LoL inspiration and original proposals. We cannot recover a private opponent's decision algorithm or establish a causal win-rate benefit from its replay. Our working principle is **concentrate the smallest sufficient ready group on a valuable job, then release it when the job ends**.

## 1. Role assignment

Assign farming, scouting, fighting, capturing, escorting, and defending responsibilities.

**Status:** Planned

**Tactic**

Assign a body a **job for the current mission**, with a completion condition and a next task. A mission can clear a camp, hold its capture, interrupt an enemy tribute, bank a valuable bag, protect a carrier, remove an isolated threat, escape or gather actionable information. The mission names an objective, a latest useful arrival/action window and a safe exit. It does not require a permanent tank/support/carry label for every champion.

| Job | Assign by | When the job ends |
| --- | --- | --- |
| Initiate or take the opening damage | Current HP, mitigation, legal approach and whether follow-up can arrive before the body is lost | The opening is delivered, required follow-up fails or the risk becomes unacceptable |
| Damage or interrupt | Actual usable attacks/spells and target access in the relevant turn sequence | The target dies, the useful window ends or a higher-priority protection/interrupt becomes necessary |
| Protect or enable an ally | A legal disable, heal, shield, threat interception or useful exit position that changes the threatened ally's outcome | The ally escapes, finishes banking or is no longer threatened |
| Hold capture | A body actually on the region, able to remain through the required phases | Reward is confirmed, a real replacement overlaps the handoff or survival requires aborting |
| Carry and tribute | The body's actual bag, safe walkable route and channel window | Tribute completes, the altar becomes unusable or the route must change |
| Independent farm or observation | A reachable productive task with acceptable uncertainty and no essential missing group role | Its reward/information is obtained or a more valuable timely mission needs this body |

One body can do compatible jobs; one cast cannot provide two mutually exclusive effects. Use current equipment, HP, cooldowns, range, movement restrictions and personal vision, rather than copying a role solely from a champion name. Cassi and Issac are separate actors and wallets with linked death risk; count both action contributions while accounting for the pair's coupled loss.

**Reassign** after a role completes or a relevant death, recall, new sighting, blocked route or missed deadline. Emergency survival can revoke a job immediately. Unassigned bodies continue useful safe work; they do not follow the largest group without a reason.

**Current behavior:** The [audited study27 derivative](coordination-research-2026-10-16.md#our-existing-bot) shares camp intentions and makes local combat decisions. Its explicit group/help/twin routines are disabled. A claim is not an acceptance or readiness promise.

**Related decisions:** [Farming and capture](08-farming-and-capture.md), [Gems and objectives](09-gems-and-objectives.md), [Shopping](11-shopping-and-investment.md).

## 2. Grouping versus splitting

Decide when combined strength outweighs the resource coverage gained by spreading out.

**Status:** Planned

**Tactic**

For an additional member, compare **the extra secured value of joining** with that body's best feasible alternative and the travel/absence it creates. The value can be a kill before a response, a saved carrier, a contested capture, a stopped tribute or a safe bank. Count rewards once at team level and retain their personal allocation; there is no pooled shop wallet.

| Situation | Decision | Stop or fallback |
| --- | --- | --- |
| The extra body's timely action changes a credible survival/clear/contest result | Form a temporary group with named jobs and a conversion task | Release it after the threat or required work ends |
| A reachable isolated enemy can be removed before escape/reinforcement | Compare a two-body overload with the existing independent tasks | Decline if help arrives too late or the first body cannot survive until it acts |
| A protected tribute or contested objective needs several capabilities | Assemble enough ready damage, interruption and protection on compatible approaches | Do not start the risky channel/fight assuming missing help will appear |
| Existing participants already suffice and another safe reward is available | Keep or create a productive split assignment | The split body must respect enemy travel/vision uncertainty and its escape window |
| The camp is cleared and uncontested | Keep the required holder; release excess clearers unless protection is still useful | Extra holders do not speed the fixed capture timer |

A four-body group is justified by its third/fourth useful contribution, not by its visual cohesion. Conversely, a split body creates pressure only through a real camp, denial, tribute, interception or information task. Battlecode has no minion wave that automatically pressures a tower after the body leaves. Two unrelated solo farms are not a coordinated split-pressure plan unless their timings create a useful tradeoff for the opponent.

**Fallback:** retain an already useful commitment when a new detour's gain is unresolved. Do not equate missing enemies with no enemies. A coarse danger alert identifies a question to investigate, not a command for the whole team to converge.

## 3. Group size

Choose how many champions each camp, fight, or contested objective actually needs.

**Status:** Planned

**Tactic**

Start with one body, a pair and the available larger group. Choose the smallest candidate that passes the mission's readiness and outcome checks with a stated uncertainty margin. Do not search all team partitions in the first implementation.

For each proposed participant, estimate **time to its first useful legal action**, not distance to the target's center. Include a walkable contribution tile, movement abilities, next scheduled turn, cast/attack allowance, current HP, cooldown and whether the actor has already spent its action. A body behind a wall, channeling, dead, out of range for its assigned useful action or merely holding a stale claim is not ready power.

For a 2v1, require that the first ally can survive the interval until the second contributes, both can access the target, and the enemy cannot cheaply escape or bring sufficient help first. Account for enemy response turns between allied actions. For a four-body objective group, identify what each member adds: for example a holder/carrier, damage, an interrupt and protection. One strong enemy can still beat a nominal numerical advantage; headcount is not a combat simulation.

**Assembly gate:** required members must be observed ready or confirmed through an implemented, fresh protocol. Wait at a reachable safe-side staging point only until a finite latest useful start. That deadline comes from escape, reinforcement, capture/tribute timing and participant ETA. Any additional maximum-wait constant remains an experiment parameter with world-round units, not a claimed optimum.

**Stop/fallback:** if the gate fails, shrink the mission, select another objective, continue split work or withdraw. Do not enter a losing opening to force teammates to follow. Revoke a promised role when availability changes.

## 4. Formation and spacing

Position durable champions, damage dealers, and supports while avoiding unnecessary exposure to area damage.

**Status:** Planned

**Tactic**

Position relative to the **next required action and enemy reach**. Keep the initiator on a survivable approach, damage bodies at legal firing/casting positions, useful heal/shield/peel in range and a valuable carrier on a protected exit. Avoid a compact cluster inside an observed area effect, while preserving the support distances the mission needs.

The first mover must not leave all follow-up behind a wall or occupied choke. Ordinary movement cannot enter another body's occupied tile in the audited engine. Choose different legal destinations and crossing order; do not ask every member to occupy the leader's last square. This supports route planning, not a claim that a champion intercepts all projectiles for an ally.

**Reposition** after a blocked move, new threat, target movement or role change. Prefer a tile that preserves useful action access with less credible incoming damage. Each body still needs its own legal observation: a frontline scout's vision does not grant a backline cast through fog. A shared target report can guide approach but not bypass targeting rules.

**Stop/fallback:** use the next legal useful slot if the ideal one is occupied. If no viable formation exists, change the approach or decline the engage. Do not preserve a diagram by sacrificing a required actor that cannot survive. The last capture holder must remain until reward or verified handoff unless the capture is explicitly aborted for safety.

## 5. Group travel

Keep a moving group sufficiently connected without blocking routes or waiting unnecessarily.

**Status:** Planned

**Tactic**

Travel toward a **mission objective or rendezvous with an arrival window**, rather than indefinitely chasing another body's current position. Use path distance and actual movement abilities. Measure ETA to a legal action tile; a ranged body that walks into range may still need a later turn to attack or use a walking-exclusive spell.

Choose a staging point outside credible enemy/monster reach and reachable by required members. Earlier arrivals can perform safe compatible work or wait briefly; optional late members do not hold an already feasible mission hostage. At a choke, plan the first crossing and where support can actually act. Geometric chains of nearby allies are not necessarily one fighting unit.

Before crossing into exposure, check the same readiness gate as [Group size](#3-group-size). Recheck after an actual move or new observation materially changes the expected arrival. Keep a stable route/objective across minor score fluctuations, but allow a new threat, blocked route or failed required arrival to invalidate it.

**Stop/fallback:** a missed arrival window ends the old rally. Pick a smaller useful job, another route, split work or reset; avoid unlimited leader waiting and serial solo entry. Turn priority can affect **next round**, and enemy actions remain interleaved. It is a scheduling tool, not permission to assume consecutive allied burst.

## 6. Reinforcement decisions

Decide whether nearby allies should abandon their current task to help.

**Status:** Planned

**Tactic**

Treat help as a comparison of outcomes. The receiver estimates whether its first legal damage, disable, heal, shield or escape-cover action arrives **before the threatened event is decided**. The threatened body estimates whether it can survive, kite or disengage until then. Compare the helped objective with the capture, tribute, farm or protection being abandoned.

**Join** when timely contribution changes a valuable outcome and the route/arrival is viable. **Decline** when arrival is too late, help creates another isolated death, or the abandoned task is worth more. A body that cannot save the current exchange can still meet the retreat, protect the carrier's next approach, intercept later or take a productive undefended reward.

An accepted role is distinct from intended travel. A claim without ETA/freshness is not confirmation. A report needs a source, observation age and intended effect in whatever compressed protocol is actually implemented; recipient uncertainty must survive compression. Remote ally live positions and enemy views are not automatically shared.

**Stop/fallback:** expire obsolete help on target death, retreat, new reinforcements, impossible timing or completed objective. Do not travel to a stale coordinate indefinitely. Emergency self-survival remains available, and a declined response must not leave others assuming that capability is coming.

## 7. Collective retreat and regrouping

Withdraw together when necessary and avoid returning to a dangerous area one champion at a time.

**Status:** Planned

**Tactic**

Use **abort → cover/exit → regroup → fresh readiness check** when a required role disappears, the credible exchange becomes losing, the target escapes beyond useful pursuit, or the objective no longer warrants the risk. An endangered body can leave immediately; other bodies revalidate rather than completing its stale engage plan.

Choose a reachable safe-side regroup point. Use legal control, healing or positioning to enable an exit only when the helper's contribution is worth its added risk. Protect bankable gems and linked Cassi/Issac survival. Do not turn one lost exchange into several solo re-entry deaths, nor demand an ineffective sacrificial cover.

Regrouping ends when the minimum useful group can act, the threat no longer requires grouping, or another mission is selected. Coordinate **readiness**, not necessarily identical recall start times. A staggered reset can preserve control through a real role handoff; simultaneous recovery can make sense before a future contest only if the group can return in time. Preserve camp/tribute timing and include the return route and installed shopping power.

**Commitment rule:** minor distance/score changes use a switching margin or a brief lease to suppress oscillation. Hard invalidations—imminent lethal danger, lost essential support, illegal target, missed deadline or a materially stronger enemy arrival—override that persistence immediately. Thresholds and lease lengths are unoptimized parameters to test. A retreat is not indecision merely because direction reverses.

**Related decisions:** [Combat and survival](07-combat-and-survival.md), [Recall and recovery](10-recall-and-recovery.md), [Purchase timing](11-shopping-and-investment.md#1-purchase-timing).

## 8. Shared commitments

Coordinate target reservations and handoffs so champions neither duplicate work nor abandon essential tasks.

**Status:** Planned

**Tactic**

Distinguish **intent → acceptance → readiness → execution**. A mission contract conceptually specifies objective, roles/membership, arrival/action window, success, abort and expiry. A camp reservation proves only an intention, and may already be stale. Derive compatible roles locally where possible rather than transmitting a large role list.

For capture, retain the current holder until a replacement is actually on the region or verified to overlap every required phase. A claim within four tiles is insufficient. Confirm reward receipt before releasing the last required holder. Recall departure, Home's shorter timer and safety aborts use actual phase order.

For combat, align the earliest relevant action with a common **reachable target + action window**, with explicit survival, peel, interrupt and useful area-damage exceptions. Prefer removal/control that changes the next exchange; predict committed damage only from personal observation or fresh implemented reports with valid timing, and re-read after earlier actors so later bodies avoid redundant lethal damage or a dead target. Unseen allied damage is not automatically known. Different personal views can require different legal actions. Shared-recipient damage in a replay does not itself prove a chosen common primary target.

**Protocol requirement:** the existing eight bytes are already allocated to claims0–4, camp lifecycle5–6 and danger7. A remote contract requires an explicit layout/migration, stable identities, bounded fields, writer ownership, arbitration, freshness/wrap rules and invalid-message fallback. Host writes are visible to later allied turns, but a multi-call read–modify–write sequence is not proven atomic across guest fuel suspension. Do not silently overwrite existing coordination or assume an omniscient central planner.

**First implementation boundary:** begin with local readiness, finite assembly and real capture handoff while retaining the existing memory allocation. Test common local focus and commit/reset separately and together. A richer remote contract is a later experiment after a complete byte budget; none is implemented by these instructions.

**Current behavior:** the pinned source can count a channeling or recalling body's stale claim as coming, and its handoff heuristic can nominate a claimed ally still approaching. Its pre-sweep, kite and front-line target choices are local and can disagree. These are source-derived risks, not proof of a particular replay failure. See the [source audit and evaluation plan](coordination-research-2026-10-16.md#our-existing-bot).

**Validation:** compare timely contribution and first-to-last arrival, legal focus conditional on shared visibility, completed captures/banks, waiting, forgone split work, stale help and serial re-entry losses. Keep draft size, body count, champion, map, opponent and time period visible. More proximity or fewer reversals alone does not prove a better policy. No competitive outcome tests were run for this research.

---

[Coordination research, replay cases and LoL transfer](coordination-research-2026-10-16.md) · [← Pathfinding and individual movement](05-pathfinding-and-movement.md) · [Tactics index](README.md) · [Combat and survival →](07-combat-and-survival.md)

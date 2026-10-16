# Combat and survival

**Chapter 07 of 12** · [Tactics index](README.md)

When we fight, how we execute, and when we leave.

**Reference:** Source behavior below uses the [pinned reference snapshot](reference-snapshot-2026-10-16.md) at [`a0c0fa2`](https://github.com/Javiops/Cambridge-Battlecode-2026/commit/a0c0fa2f222557483d665a9f7fce6f64a30b94ba), `bots/study27-economy/src`, with its [active parameters][c07-flags]. Its identity with the live v43 upload is unverified. **Implemented** means the active source implements the stated baseline; no new gameplay tests or improvement measurements accompany this chapter. Proposed changes remain **Planned**. Distances below are Chebyshev tiles unless a walking route is specified.

## Contents

1. [Fight selection](#1-fight-selection)
2. [Local strength assessment](#2-local-strength-assessment)
3. [Target selection and focus fire](#3-target-selection-and-focus-fire)
4. [Range control and kiting](#4-range-control-and-kiting)
5. [Ability selection and timing](#5-ability-selection-and-timing)
6. [Action sequencing](#6-action-sequencing)
7. [Escape decisions](#7-escape-decisions)
8. [Chasing and disengagement](#8-chasing-and-disengagement)

## 1. Fight selection

Decide whether engaging is worthwhile given the objective, likely outcome, and cost of interruption.

**Status:** Planned

**Tactic:** Give an immediate champion threat priority over a discretionary camp action. Select a short exchange with a concrete result: remove a threat, stop a channel, protect a carrier, secure a capture, or create a safe exit. Before closing distance, check the participants who can act before the opponent's response, the damage/control actually ready, and the exit after the exchange. Apply [local strength assessment](#2-local-strength-assessment); a nearby ally or a camp claim alone does not establish support.

Decline or abort when the required action cannot arrive in time, survival fails, or the objective disappears. Use a safer useful task; if the same enemy still threatens the farm, reposition or hold the camp action rather than spending the reserved health or ability there. This is the planned interpretation of the team's reported micro/secure-farming priority, not a ban on farming whenever any enemy is visible.

**Current behavior:** After a possible pre-turn spell sweep, the main body handles spawn recovery, emergency escape and near-enemy recall before caster kite, front-line combat, and fallback combat. These branches can return before recall, banking, and farming. The fallback permits engagement for a target deemed killable, channeling, or reachable in a favourable fight. These are heuristics: `killable` is HP at most twice our Strength, not a complete lethal sequence. `P_FM=0` leaves the larger fight-mode model disabled. See [branch order and engagement gates][c07-mainfight].

**Fallback:** Use current legal escape/positioning with personal observations when readiness cannot be established. Do not invent remote teammate health or future damage. The first prototype is a local threat-and-readiness gate; a remote team contract remains the separate [coordination plan](06-team-coordination.md).

## 2. Local strength assessment

Compare usable damage, health, shields, abilities, positioning, and reinforcement time.

**Status:** Planned

**Tactic:** Count a participant only if it can reach a legal useful action before the exchange or escape is decided. Include movement/attack exclusivity, current ability cooldowns, stuns/channels, legal approach tiles, and the interleaved acting order. Estimate damage and protection over that bounded window, including incoming monster damage if the camp is awake. Keep unknown enemies and unavailable allied observations explicit; hidden health is unknown, not zero.

Start with our own actions and currently observable nearby participants. Use a proposed engage only if it survives the conservative response estimate and achieves the mission before support expires. Recheck after a move, cast, death, new sighting, or failed action. Do not keep engaging because an earlier headcount was favourable. Exact uncertainty margins beyond the existing source thresholds remain experiment parameters; they are not optimized constants.

**Current behavior:** Front-line combat uses ally HP within nine tiles, enemy HP within eight, and a 130% enemy/ally HP ceiling. Its local gate also requires another ally within four, no more enemies within five than local allied bodies including us, and the same HP ceiling. Caster kite instead declines only when enemies exceed allied count by more than two **and** enemy HP exceeds 130% of allied HP. Fallback `P_ENGAGE2=120` requires allied count at least enemy count and allied HP at least 120% of enemy HP around the target. These checks neither synchronize cooldowns nor prove timely contribution. See [front-line assessment][c07-front] and [fallback assessment][c07-mainfight].

**Related decisions:** [Group size](06-team-coordination.md#3-group-size), [Camp combat positioning](08-farming-and-capture.md#3-camp-combat-positioning).

## 3. Target selection and focus fire

Choose valuable, reachable enemies and coordinate damage when concentrating attacks is beneficial.

**Status:** Planned

**Tactic:** Select a personally visible, living target outside enemy spawn that the assigned action can legally affect. Prioritize preventing an immediate loss or interrupting a decisive channel; then compare a secured lethal sequence, a valuable carrier, and the reachable threat blocking the mission. Concentrate only the damage needed within the useful window. A protector may instead disable a diver or heal the threatened ally.

Keep the focus while the useful action remains reachable and the mission remains valid. Requery target visibility, HP, position, and legal action availability after each successful action. Retarget if it dies, becomes unavailable, or a more urgent threat invalidates the old plan. Do not spend a reset or movement on a vanished target. A common remote focus requires the implemented communication and freshness rules described in [Shared commitments](06-team-coordination.md#8-shared-commitments); personal visibility still controls damage legality.

**Current behavior:** Focus differs by branch. Pre-sweep prefers low HP, channeling, and gems; kite minimizes `HP − 300 if channeling + 20 × distance` among eligible targets within five, falling back to the nearest enemy in its within-seven observation list when that scoring finds none. Front-line uses a local allied centroid, with large-bag and melee-peel exceptions. Fallback minimizes `HP − 300 if channeling − 5 × gems + 40 × distance` within six. With `P_KITEFRONT=0`, kite runs before front-line combat and does not use its common-focus alternative. Thus the source does not implement one synchronized team focus. See [kite focus][c07-kite], [front-line focus][c07-front], and [fallback focus][c07-mainfight].

## 4. Range control and kiting

Maintain useful attack distances while accounting for the tradeoff between movement and attacking.

**Status:** Implemented

**Tactic:** With `P_KITE=1`, a team containing Stellar sets the source's `casters` flag. Eligible ranged bodies try caster kite before front-line combat; ordinary Ren is excluded because `P_UNI_RENKITE=0`. Kite considers enemies within seven, but yields when none is within four and we have not been hit in the last two rounds. It also yields when the no-chase rule finds no continuing nearby fight or the source's count/HP rejection applies.

Score our tile and legal neighbouring tiles by fewest predicted enemy reaches first, then keeping the focus within spell/basic range, then avoiding separation beyond four from the nearest visible ally. Move only for a strictly better score. After moving, try control on an enemy predicted to reach us, then an area spell covering at least two enemies, other damage/control, and finally a basic attack in range. If the focus is unavailable to the basic attack, try another in-range enemy.

Enemy basic reach is a heuristic: ranged range plus one; ordinary melee two; supported dash melee three when its dash may be ready by the next opportunity. Cooldown at most one is treated conservatively, not as a complete initiative forecast. Occupied/illegal movement still falls back through action rejection. Front-line combat handles its own ranged positioning if kite declines; neither branch guarantees safety against hidden enemies or all spell effects.

**Implementation:** [Caster activation][c07-casters], [kite and reach][c07-kite], [reach metadata][c07-reach]. The planned stronger readiness assessment is in [07.2](#2-local-strength-assessment).

## 5. Ability selection and timing

Choose between damage, control, healing, shields, resets, and mobility according to the immediate situation.

**Status:** Implemented

**Tactic:** The active baseline uses a champion spell sweep before the main decision when the team contains Stellar (`s.sweep=3`); without Stellar it switches to a post-decision fight-gated sweep (`s.sweep=2`). Sweep excludes dead/channeling bodies and enemies on their spawn. It first tries control on a threatening enemy, then a ready ground area spell hitting at least two, then non-control damage on its weak target, then control. A legal area centre may hit a visible enemy five tiles away when cast range four plus radius one reaches it; the spell centre itself must remain in range. This edge-area fallback requires sweep mode at least three, so it is not available in the no-Stellar mode-two branch.

The main support pass tries a ready shield below 85% HP during local combat, or the first visible legal ally heal that can restore at least half the ability's nominal heal. General offense scans the two ability slots in order. Basic-attack reset is used only after a successful first hit leaves the selected target alive and visible (`P_U34_RESET_LIVE=2`). Stop when an action succeeds or readiness/legality prevents it; failed SDK actions are caught.

**Limits:** `P_SAVECC=0` does not reserve control for a recently seen champion, and `P_CASTSAFE=0` does not protect an urgent escape from a movement-exclusive pre-sweep cast. This describes current behavior; [07.6](#6-action-sequencing) plans the priority correction. Multiple-target geometry is not proof that area damage is always the best tactical choice.

**Implementation:** [Offense, resets and support][c07-helpers], [sweep priorities][c07-sweep], [area-edge fallback][c07-edge].

## 6. Action sequencing

Order movement, attacks, and abilities so one action does not prevent a more important action.

**Status:** Planned

**Tactic:** Before any action that removes movement or another useful action, decide whether the body must escape, complete a critical channel/hold, or execute a stationary damage sequence. For a necessary escape, choose the legal move/dash/control sequence first; allow a stationary lethal cast only if the freshly checked kill removes the relevant danger without losing to the remaining response. For a safe stationary exchange, cast the movement-exclusive spell before spending movement. For a ranged reposition, preserve the move until it is taken, then use only compatible remaining actions. Requery state between actions and stop once the intended result or an emergency abort is reached.

**Current behavior:** `run_game` can pre-sweep **before** `play_turn` calculates the emergency response. Within `play_turn`: initialize/dead-shop; detect a reward gain; shop; return for any active channel; refresh observations; support; unsticking; spawn recovery; emergency escape; near recall; kite/front/fallback combat; ordinary recall; bank; farm; possible spare basic. A post-sweep runs for mode two; altar lock runs afterward; ordinary ward placement is disabled. General `engage` tries a nearby offense spell, basic attack/reset, movement if out of basic range, then basic attack. Caster kite moves before its own spells. Disabled `P_CASTSAFE`, `P_KITEFRONT`, and `P_U34_POST_FREE` must not be described as active fixes.

**Fallback:** If a preferred action fails, refresh its cause and use a remaining legal action that preserves the higher priority. Do not let “attempted combat” silently consume the whole turn while safe work remains. This fallback requires implementation: `P_U34_ENGAGE_FALLBACK=0` and `P_U34_FAILED_CHANNELS=0` still allow several current branches to return after a failed attempt.

**Implementation gap:** [Outer action order][c07-order], [main branch order][c07-mainfight], [engage order][c07-helpers].

## 7. Escape decisions

Decide when to flee, where to go, and whether walking, control, dashing, or recall offers the best survival chance.

**Status:** Planned

**Tactic:** Trigger an escape when the bounded incoming response threatens survival or the mission can no longer be completed safely. Retain the current source's 25% HP emergency threshold, or 35% on its Stellar-containing team, as initial fallback thresholds rather than proof of optimal timing. Do not wait to cross them when a visible ready sequence is already lethal. Protect Cassi/Issac's linked life when choosing the risk.

Compare reachable escape tiles and ready mobility with damage/control that can actually prevent the response. Use a legal lower-threat tile toward a useful ally or recovery route; do not dash into an unobserved occupied landing assumption. Recall only when its full remaining channel is survivable, not because the current tile is momentarily outside basic range. An adjacent useful tribute may take priority when it can secure the carried gems without a survival error; its distinct interruption rules matter.

**Current behavior:** Emergency low HP recalls if `rsafe`; otherwise it tries a permitted hit, routes toward spawn with dash allowed, and shoots afterward if it did not hit. Ordinary avoidance uses `P_SAFESTEP=1`: minimize the number of enemies predicted to reach the tile, then proximity to an ally above 40% HP, then home distance; if that fails, route home. Ranged hit-first yields while movement remains available. `P_VOLLEY=70` adds local ready-damage avoidance to ordinary pathing, but this is a heuristic and its low-fuel fallback is weaker. See [emergency and recall][c07-emergency], [back-off][c07-backoff], and [volley pathing][c07-volley].

**Stop/fallback:** End escape when a useful safe action or recovery channel is available. If no escape is viable, spend remaining legal control/damage to improve survival or protect secured value; do not retry an impossible move indefinitely. See [Recall safety](10-recall-and-recovery.md#2-recall-safety).

## 8. Chasing and disengagement

Decide when pursuing a kill remains worthwhile and when to return to productive objectives.

**Status:** Planned

**Tactic:** Keep the existing no-chase observation as a default stop signal, then require a fresh mission and reachable action window for any exception. A valuable carrier or channel can justify a short intercept, but its value does not remove safety, travel-time, or reinforcement checks. Stop when the target leaves legal useful reach, a response erases the advantage, the target dies, or the opportunity deadline passes. Release the combat commitment and resume a useful camp, capture, bank, protection, or recovery task; do not spend reserved combat resources on the farm while the same threat remains immediate.

**Current behavior:** A continuously observed enemy that moves farther from our previous position, or toward its spawn without coming closer, is marked away for three rounds; entering distance two clears the mark. `P_NOCHASE=1` usually excludes an away target outside our basic range unless it is channeling or has at least 150 gems. Front-line has a large-bag chase exception. These are local observations and exceptions, not a pursuit distance/time budget or proof of profitable pursuit. Caster kite's distant-contact gate also releases otherwise idle standoffs. See [away tracking and target exclusion][c07-away] and [front-line exceptions][c07-front].

**Fallback:** Lost sight does not authorize chasing into fog. Keep the target's last observation distinct from current knowledge and route to the next safe mission unless an implemented scout/ward decision supplies actionable information.

---

[← Team coordination and group movement](06-team-coordination.md) · [Tactics index](README.md) · [Farming and camp capture →](08-farming-and-capture.md)

[c07-mainfight]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2951-L3089
[c07-front]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L295-L455
[c07-kite]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L458-L589
[c07-casters]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1194-L1203
[c07-reach]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L64-L101
[c07-helpers]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1504-L1588
[c07-sweep]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3381-L3566
[c07-edge]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2647-L2683
[c07-order]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L3594-L3697
[c07-emergency]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2862-L2948
[c07-backoff]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/fight.h#L111-L179
[c07-volley]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L1350-L1487
[c07-away]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/main.cpp#L2821-L2887
[c07-flags]: https://github.com/Javiops/Cambridge-Battlecode-2026/blob/a0c0fa2f222557483d665a9f7fce6f64a30b94ba/bots/study27-economy/src/params.h#L1-L82

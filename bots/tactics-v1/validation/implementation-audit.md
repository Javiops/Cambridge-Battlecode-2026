# Independent implementation coverage audit

Independent source audit at the final functional freeze. Final integration execution results are separate. No topic is marked Verified.

The 96-topic specification is broader than one complete exact strategic solver. This table names real bounded implementation, expressly allowed fallback, optional omission and remaining material gaps separately. Passing source compilation or a few games cannot upgrade all rows to Verified.

| Status | Count |
| --- | --- |
| IMPLEMENTED | 44 |
| FALLBACK | 46 |
| PARTIAL | 4 |
| OMITTED_OPTIONAL | 2 |

## Release assessment

Source contains fixes for audited channel, visibility, action-budget, staging and timing errors. Earlier full-bot versions still had fuel/idle failures and are development evidence. Four strategy/coordination scope gaps remain explicit; this is a bounded first architecture, not all 96 topics fully implemented. Final full-production-module activity/fuel evidence is separate from the passing scoped unit and scripted native fixtures.

A first v1 can be reviewed as a bounded new architecture with declared fallbacks; this is different from full implementation or validation of all 96 topics. General route-loop detection, marginal helper assignment, strategic warning sharing and explicit territory planning remain plainly recorded. Existing baseline behavior is not called Verified merely because code compiles.

## Validation provenance

The saved focused reports below retain their recorded source hashes. A scoped-header match is only unit/policy evidence; it is never a native pass for the final release module. A changed hash leaves the report as earlier-source evidence until the final frozen source is retested.

| Saved focused report | Checks in its recorded run | Current source relationship |
| --- | --- | --- |
| channel-risk-tests.json | 27 | EARLIER_SOURCE_ONLY |
| combat-policy-tests.json | 58 | EARLIER_SOURCE_ONLY |
| delivery-tests.json | 13 | EARLIER_SOURCE_ONLY |
| recovery-tests.json | 18 | EARLIER_SOURCE_ONLY |
| results-functional-v12/report.json | 11 | EXACT_SCOPED_HEADERS |

This source audit records no native final-module pass. Release gameplay/fuel results must identify the exact final source/module hash. Earlier versions and repaired failures remain development evidence with their own provenance.

## Current portable policy suite

The recorded results-functional-v12 portable report matches current production headers: **True**. Recorded suite results: policy 9556, combat 58, squads 16, camp-affordability 11, channel 27, recovery 18, delivery 13; SDK header checks 13.

Current matching production headers/pure policy functions and SDK syntax checks only. main.cpp execution, compiled release-module behavior and native fuel results are separate. Most policy checks exhaust claim-codec boundaries, not independent game scenarios.

## Scoped native cycle fixture

Recorded native-cycle-v12: pass **True**, current production headers match **True**, actual engine **0.0.2**, native faults **{'teamA': 0, 'teamB': 0}**, fuel exhaustion **0**.

Scripted native single-tile normal-recall overlap and actual tribute completion on both mirrored bodies, using copied production timing/observer/gateway helpers. Its fixture main/module differs from the competitive bot.

Immediate normal recall departs without the immature reward; after the production helper’s required prior hold, overlap preserves the actual 22-gem payout. Accepted tribute remains unbanked initially; later completion changes the public score and is recognized by the production observer. Home, enemy contest and the full competitive arbiter are outside this fixture.


## Chapter 01

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 01.1 Win condition | IMPLEMENTED | Deciding legal bank now precedes ordinary 95% spawn-heal fallback; prospective delivery movement rejects an actual lethal next reply. Public score/horizon used, no enemy-future guarantee. |
| 01.2 Score awareness | IMPLEMENTED | Uses public scores and visible bags; unseen enemy events are not invented. Interception remains bounded local control. |
| 01.3 Gems versus gold | FALLBACK | Common endpoint/coarse clear+recovery model with inherited gold weights; no optimal private investment valuation. |
| 01.4 Aggression level | FALLBACK | Conservative one-opportunity reply and HP margins; no exact multi-agent exchange simulator or calibrated risk probability. |
| 01.5 Game phases | IMPLEMENTED | Geometry and finish feasibility replace named-map bag overrides;600/1850 remain declared fallback constants. |
| 01.6 Power spikes | IMPLEMENTED | Post-purchase/action state refresh changes actual legal choices; no team-wide spike schedule claimed. |
| 01.7 Opportunity cost | FALLBACK | Farm/one-reward-bank compared on coarse endpoint; recovery still uses explicit HP fallback, not full mission-payoff optimization. |
| 01.8 Playing ahead or behind | FALLBACK | Feasible deciding score and conservative productive fallback; no general lead-dependent/comeback risk model. |

## Chapter 02

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 02.1 Map connectivity | IMPLEMENTED | Native walking connectivity and reachable useful goals; optional special-route planning omitted rather than pretending ordinary reachability. |
| 02.2 Actual travel distances | IMPLEMENTED | Actual static fields plus dynamic legal runtime movement; not exact action ETA for every future ability. |
| 02.3 Chokepoints and escape routes | FALLBACK | Legal lower-threat/homeward alternatives and personal observation implement the conservative local fallback; no explicit global choke/cutoff slack optimization. |
| 02.4 Walls and holes | IMPLEMENTED | Walking, dash traversal and optional teleport are distinct. Dash proposals and the gateway check a bounded path with walls, enemy spawn, visible units/camps and teleport reservations, plus a free legal landing. The SDK valid_tiles mask supplies range only, not a complete path/landing certificate; unseen blockers remain unknown and actual rejection is handled. |
| 02.5 Bush geometry | IMPLEMENTED | Actual shadowcast/visibility and recent possible regions; not omniscient bush absence. |
| 02.6 Resource distribution | IMPLEMENTED | Public inventory and independently visible wandering camps; known dead members and conservative original stats prevent hidden-group undercount; monolith-only economy feature. |
| 02.7 Altar accessibility | FALLBACK | Two geodesic-shortlist altar proposals each test actual legal nonlethal approach; a blocked or lethal first choice cannot erase the second. Enemy-arrival ranking remains a coarse geometric penalty, not a route-safety certificate. |
| 02.8 Map-dependent planning | IMPLEMENTED | No named-map/signature strategy branches; measured geometry and generic fallback. |

## Chapter 03

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 03.1 Champion selection | FALLBACK | Known pinned SDK legal-choice recipe with rejection fallback; not runtime discovery of every future champion choice. |
| 03.2 Pick order | IMPLEMENTED | Prospective final pick serialized before accepting API call; failed choices tracked separately. |
| 03.3 Draft adaptation | FALLBACK | Explicit permitted fixed recipe; does not consume/reorder from enemy revealed draft. |
| 03.4 Team composition | FALLBACK | Explicit permitted size-specific recipe; no computed whole-composition job coverage optimizer. |
| 03.5 Team size | IMPLEMENTED | Actual physical body roster, six-body encoding and explicit unsupported sixth-slot degrade; dead body not ready contributor. |
| 03.6 Champion and map fit | FALLBACK | 45-step coarse path recipe only, explicitly permitted; no per-kit topology utility model. |
| 03.7 Scaling and investment needs | FALLBACK | Role build fallback, no future private income/draft scaling schedule. |
| 03.8 Champion-specific rules | FALLBACK | Critical Ren return, Varg splash, observed linked-removal, actual gem/stat refresh, immunity and reset cast budget implemented. General conservative-kit fallback remains for effects not represented in metadata. |

## Chapter 04

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 04.1 Ward placement | IMPLEMENTED | Bounded own-mission ward scoring uses exact engine visibility masks and keep-versus-replace margin. The current arbiter admits placement only on idle/hold proposals (Action::None), with at least 45000 fuel; active useful actions are not preceded by ward search. This is a conservative timing prototype, not complete opportunistic ward scheduling. |
| 04.2 Ward relocation | IMPLEMENTED | Keep-versus-replace on same mission/future owner mask with tie/switch margin, persistent old observer counted. |
| 04.3 Personal vision | IMPLEMENTED | Owner personal natural/effective masks; reports never used for targeting; exact candidate shadowcasting. |
| 04.4 Scouting responsibility | FALLBACK | Own-mission observer prototype; no distributed remote scouting-role protocol or dead-body warning publication. |
| 04.5 Enemy tracking | IMPLEMENTED | One-to-three-round personally observed identity/location/age is retained and never used as a legal stale target. Exact possible regions with visible-absence pruning are admitted only for uncertainty extent<=2 and sufficient fuel; larger or lower-budget cases use a conservative scalar geometry bound that can preserve impossible through-wall danger. Three rounds and extent two are initial bounded settings, not optima. |
| 04.6 Threat estimation | FALLBACK | Contact-aware bounded response plus mission approach ring; ward placement does not explicitly optimize fastest uncovered-route warning slack. |
| 04.7 Opponent intent | FALLBACK | Explicit uncertain mission-approach fallback; no multiframe farm/invade/tribute intent classifier. |
| 04.8 Information sharing | PARTIAL | Claim layout retained, local observations correct; no implemented fresh strategic warning sharing/danger-byte reader-writer. Bytes5-7 not repurposed. |

## Chapter 05

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 05.1 Route selection | IMPLEMENTED | Selected legal task route with fresh dynamic occupancy and local threat filter; conservative finite failure if no route/fuel. |
| 05.2 Destination selection | IMPLEMENTED | Attack range, altar ring, capture region and spawn interaction goals; arrival does not claim success. |
| 05.3 Immediate step selection | FALLBACK | Short legal hold/cast/basic/escape/approach alternatives; no exhaustive position-and-sequence optimizer. |
| 05.4 Dynamic obstacles | IMPLEMENTED | Refresh blockers and bounded distinct alternatives. No command walks through an occupied tile. |
| 05.5 Hidden blockers | IMPLEMENTED | Rejected movement records tile and refreshes; two failed-move cap. Failure not identified as a particular hidden enemy. |
| 05.6 Unsticking and loop prevention | PARTIAL | Clear stagnation starts from actual clear entry rather than old travel time; first arrival receives its own progress interval, and failed incumbents are suppressed. General route A-B-A/task-progress detection and exclusion remain absent. |
| 05.7 Dash usage | FALLBACK | Ready legal dash considered for escape only; travel/engage dash optional fallback walks/holds. |
| 05.8 Arrival timing | FALLBACK | Helpers qualify by an actual ready hit/cast on any live member of the group, not only a preferred spawn. Finite assembly may approach awake camps when the next reply is affordable; respawn tiles are vacated and waiting jobs excluded. No full turn-order ETA/rendezvous model. |

## Chapter 06

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 06.1 Role assignment | IMPLEMENTED | Per-body mission/phase/target/lease with local clear/hold/bank/protect/escape jobs; no permanent class role. |
| 06.2 Grouping versus splitting | PARTIAL | Actual local helper contributions/sharing modeled; no explicit marginal join value versus helper's best alternative or deliberate split assignment. |
| 06.3 Group size | IMPLEMENTED | minimum_ready_camp_squad is wired into evaluate_farm: enumerate self-containing ready subsets, charge each observed monster to its nearest selected body (full damage to every tie), charge hidden members conservatively to self, and check every selected body over the coarse full clear duration. Choose the smallest affordable crew with deterministic ties; never divide damage by a nearby headcount. The separate monolith-only attrition fallback can proceed without a fully affordable whole-clear squad; no remote readiness or future tank swap is inferred. |
| 06.4 Formation and spacing | FALLBACK | Distinct legal occupancy-aware useful positions; no coordinated support-slot/AoE spacing allocation. |
| 06.5 Group travel | FALLBACK | Stable objective/lease and finite local camp assembly; no explicit group rendezvous/crossing-order protocol. |
| 06.6 Reinforcement decisions | FALLBACK | Immediate visible useful heal/peel and unknown help declined; no remote reinforcement travel/acceptance contract. |
| 06.7 Collective retreat and regrouping | FALLBACK | Local fresh survival/claim release and readiness replan prevent stale promised help; explicit remote group abort/cover/regroup protocol is deferred under local-only v1 boundary. |
| 06.8 Shared commitments | FALLBACK | Allowed v1 local readiness and actual acyclic holder overlap; richer remote accepted readiness/lease protocol intentionally deferred. |

## Chapter 07

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 07.1 Fight selection | IMPLEMENTED | Relevant local reply handled before discretionary camp expenditure; unsafe farm veto cannot call old unsafe helper. |
| 07.2 Local strength assessment | FALLBACK | One-cast legal alternatives, shields/mitigation/return and monsters; conservative coarse horizon, no exact opponent schedule or active-field simulator. |
| 07.3 Target selection and focus fire | IMPLEMENTED | Personally legal target, deterministic ties, local focus persistence, living reset follow-up; no omniscient committed allied damage. |
| 07.4 Range control and kiting | FALLBACK | Stationary cast/basic versus reset/move-compatible approach/escape; no full healthy kiting/spacing optimization. |
| 07.5 Ability selection and timing | FALLBACK | One cast, actual effective spells, lethal heal/peel, primary Ren return/Varg splash boundary; not complete all-passive taxonomy/control refresh optimization. |
| 07.6 Action sequencing | IMPLEMENTED | Short sequence valuation, accepted ordinary-move tracking and exclusive-cast mask/gateway are present; after a world-changing action the next decision refreshes or ends the owner turn. Exact final native behavior is separately validated. |
| 07.7 Escape decisions | IMPLEMENTED | Reply-based escape, current HP/maxHP, return damage and useful rejected-start alternative; conservatively bounded model. |
| 07.8 Chasing and disengagement | IMPLEMENTED | Only near-term useful approach; no pursuit of hidden old target, local focus expires after2 rounds. |

## Chapter 08

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 08.1 Camp selection | FALLBACK | Three-camp shortlist, coarse completed-bank endpoint/sharing; not exact legal clear/next-work payoff optimizer. |
| 08.2 Opening farming allocation | FALLBACK | Smallest affordable ready local subset and per-camp current-nearest tank exposure are modeled. Sleeping/awake assembly can enter a useful actual range under a survivable next reply; one bounded shortlist slot preserves a feasible solo alternative, and an unaffordable incumbent cannot suppress a ready alternative. Team-wide accepted assignment, marginal helper alternatives and future tank rotation remain unresolved. |
| 08.3 Camp combat positioning | FALLBACK | Candidate readiness allocates observed camp pressure by nearest selected subset with full ties and hidden-member self exposure. The separate immediate farm_safe veto still charges all reachable camp replies to self and can reject some otherwise tanked cooperation. No equal headcount division, exact multi-turn aggro simulation or tank-rotation promise. |
| 08.4 Monster targeting | IMPLEMENTED | Visible living selected-group targets, lowest-HP in-range fallback, refreshed reset/live target. Cast/kill transition rechecked. |
| 08.5 Camp commitment and abandonment | IMPLEMENTED | Finite lease/switch margin/clear stall and hard farm safety veto; rejected attack never unlocks unsafe fallback hit. |
| 08.6 Capture ownership and continuity | IMPLEMENTED | Actual sole holder retained, acyclic physical replacement, narrow guarded overlap; missed/contested interval must reset unsupported hold history. |
| 08.7 Reward distribution | FALLBACK | Retain viable holder/actual sharing; richer personal-upgrade collector transfer deferred. Lifecycle/balance log is bounded attribution, not perfect provenance. |
| 08.8 Respawn cycling | FALLBACK | Fresh lifecycle, immediate safe vacating of respawn tiles and excluding waiting candidates avoid capture-site stalls. Full wait-versus-other-cycle optimizer is deferred; take productive live work instead. |

## Chapter 09

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 09.1 Tribute timing | IMPLEMENTED | Bank-now versus one reward under finite latest time; cannot renew chain onto another reward after completion; common threshold fallback. |
| 09.2 Bag size and exposure | IMPLEMENTED | Actual starting-bag ticks and carried value once; Prism/equipment refreshed after actual bag changes. |
| 09.3 Altar selection | FALLBACK | Two walking approach candidates and lock-removal cost; threat/next destination scoring remains coarse, not optimal or certified safe. |
| 09.4 Tribute positioning and protection | FALLBACK | Useful personal warning and independent safe window/local protection; no remote escort acceptance. Deciding priority currently suppresses pre-bank ward insertion. |
| 09.5 Channel continuation or cancellation | IMPLEMENTED | Typed channel start/remaining time/cancel, explicit lock-hit outcome and bounded attempts present. Completion logs are observational proxies, not perfect resource attribution. |
| 09.6 Altar locks | FALLBACK | Existing enemy lock removal versus reroute implemented; optional owned-lock acquisition/placement mission omitted. |
| 09.7 Territory and resource denial | PARTIAL | Resource/return geometry and local contest guard; no explicit territorial defend/deny/invade mission generator or enemy reinforcement-route economy comparison. |
| 09.8 Finishing and deadlines | IMPLEMENTED | Public winning threshold and finish horizon are checked; both shortlisted altar approaches are considered and farm candidates require positive feasible rate before readiness can promote them. A deadline-ineligible ready job cannot erase a convertible alternative. Unavailable tiebreak/future facts are not invented. |

## Chapter 10

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 10.1 Recall timing | FALLBACK | Necessary recovery compares a safe progressing walk ETA from actual speed/geodesic reachable unoccupied spawn endpoint with actual recall duration; disconnected ordinary walking does not veto recall. Elective mission-priced recovery and exact future route risk remain deferred under the documented conservative fallback. |
| 10.2 Recall safety | FALLBACK | Visible and one-to-three-round personally observed missing enemies contribute separate zero-damage control/enhanced-basic interruption risk; known cooldowns, immunity and earlier walking before exclusive cast are handled. Long or low-fuel windows widen to conservative geometric risk; no exact global action-order proof. |
| 10.3 Capture and recall overlap | IMPLEMENTED | Narrow single-tile continuous-hold normal/Home overlap with fallback payout-first; no host capture progress query. |
| 10.4 Recall interruption response | IMPLEMENTED | One channel start per owner round, semantic refresh and bounded useful movement fallback; actual completion separate from command. |
| 10.5 Spawn recovery | FALLBACK | Post-shop HP/maxHP refresh and95% spawn fallback; not a complete mission-specific minimum heal calculation. |
| 10.6 Teleport crystal usage | OMITTED_OPTIONAL | No TP purchase/use proposal. Explicitly optional under contract; already active TP correctly retained and no manual cancel attempted. |
| 10.7 Channel-specific behavior | IMPLEMENTED | Three typed channels; permitted cancels, interruption distinctions and pending completion. Not generic damage cancellation. |
| 10.8 Death and re-entry | IMPLEMENTED | Dead contribution/claims released, legal shopping, fresh current roster/state on return. No assumed ready remote actor. |

## Chapter 11

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 11.1 Purchase timing | FALLBACK | Legal useful components/private budget and no unsupported elective trip; role selector fallback rather than measured upgrade absence payoff. |
| 11.2 Stat selection | FALLBACK | Primary-role/mission-pressure stat fallback; no all-kit exact next-action breakpoint optimizer. |
| 11.3 Emblem family selection | FALLBACK | Unique family saturation and mission-relevant first-passive fallback; Home/Treasure excluded without explicit caller forecast, no invented payback. |
| 11.4 Purchase order | FALLBACK | Useful partial completion/role fallback, stable goal and per-buy refresh; no full numerical three-path counterfactual comparison. |
| 11.5 Completion and stacking rules | IMPLEMENTED | Actual catalogue/inventory, identical-completion identity and family-once mitigation; actual engine stats read after combination. |
| 11.6 Consumable budgeting | OMITTED_OPTIONAL | Named reserve hook/permissions exist but coordinator never requests consumable mission. TP/owned-lock strategic acquisition intentionally omitted. |
| 11.7 Adaptive builds | FALLBACK | Selected damaging-route/pressure/body role, no map names; keep role build if richer adjustment unresolved. |
| 11.8 Shopping exceptions | IMPLEMENTED | Private budgets, exact SDK permissions, field/spawn Health distinction and checked bounded Tavi buy/sell heal pair. |

## Chapter 12

| Topic | Source audit | Exact limit / remaining correction |
| --- | --- | --- |
| 12.1 Decision priorities | IMPLEMENTED | Single arbiter/mutation gateway, compatible shop/ward refresh, no independent pre-/post-sweep. |
| 12.2 Fuel management | FALLBACK | Fuel reserve/round epoch guard/cache separation; reserve not measured worst-case guarantee, actual guest suspensions require integration evidence. |
| 12.3 Turn order and timing | FALLBACK | Actual SDK action flags and verified channel/capture phases; no joint next-round priority/initiative optimizer. |
| 12.4 Memory and coordination limits | IMPLEMENTED | Eight-byte layout retained,6-body/63-group packed case and explicit unsupported degrade; remote commitment protocol not claimed. |
| 12.5 Action validation and fallbacks | IMPLEMENTED | Current target/action checks, ordinary-move/exclusive-cast guard, explicit LockHit and bounded failures are present. After legality queries, every mutation expression rechecks the input epoch and at least 12000 actual fuel; dash-path work separately requires 24000 actual fuel. Recall/tribute attempt bookkeeping follows this final gate. Planning/full refresh have their own bounds, and self-only refresh is limited to own same-epoch transactions/self casts. These source guards are not a native final-module fuel pass. |
| 12.6 Behavior diagnostics | FALLBACK | Bounded 512-byte LogLine records replace locale-heavy per-field iostream output and include objective/target/position/serial/bag/gold/fuel. Detailed per-opportunity rate/last-seen evidence-age aggregation remains external; logging source changes alone do not prove a fuel pass. |
| 12.7 Representative testing | IMPLEMENTED | Separate testing harness builds/hashes/scenarios/maps/sides. Source audit alone verifies no run; final execution report must remain separate. |
| 12.8 Interactions between changes | FALLBACK | One integrated v1 and targeted interaction fixtures; user deprioritized full isolated performance tuning/four-arm promotion for this first implementation. |

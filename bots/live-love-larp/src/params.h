// t10plan-v1: the whole-game camp plan copied from the top 10 (plan_t10.h, 600 top10-vs-top10 games of 2026-10-27).
#ifndef P_T10PLAN
#define P_T10PLAN 0      // choose_target follows the top-10 teams' per-map, per-side, per-50-round camp-group schedule
#endif
#ifndef P_T10_UNTIL
#define P_T10_UNTIL 650  // the plan covers r1-650 (the replays were decoded to r700); later rounds play the base game
#endif
#ifndef P_T10_FROM
#define P_T10_FROM 150     // t10plan-v3: first round of the schedule
#endif
#ifndef P_T10_GOLDM
#define P_T10_GOLDM 100  // t10plan-v3: score % floor of a gold-only group under the schedule
#endif
#ifndef P_T10_CMEM
#define P_T10_CMEM 0  // t10plan-v3i: the escort keeps its carry's last group as lead while the carry recalls
#endif
#ifndef P_T10_LOG
#define P_T10_LOG 1  // t10plan-v3i: count escort rounds >4 from its carry (recall / unseen / elsewhere)
#endif
#ifndef P_T10_V4
#define P_T10_V4 1  // t10plan-v4: carry publishes its next group on capture; escort targets the carry's group (hard follow)
#endif
#ifndef P_T10_ROLEFROM
#define P_T10_ROLEFROM 50  // t10plan-v4o: roles, follow, recall with the carry only from this round (opening = e1foco)
#endif
#ifndef P_T10_FREEVEN
#define P_T10_FREEVEN 1  // t10plan-v4o: only HoR and Ryth escort; Vendetta farms free
#endif
#ifndef P_T10_KEEP
#define P_T10_KEEP 1  // t10plan-v4o: an escort finishes the live group it is clearing before following
#endif
#ifndef P_T10_NEARP
#define P_T10_NEARP 35  // t10plan-v4n: roles only when the spawn-to-spawn walk is shorter than this (0 = every map)
#endif
#ifndef P_T10_NEIGH
#define P_T10_NEIGH 6  // t10plan-v4b: the escort farms an unclaimed group within this of its carry's group (0 = off)
#endif
#ifndef P_T10_FOLLOW
#define P_T10_FOLLOW 4  // t10plan-v3i: an escort walks to its carry until within this (0 = off)
#endif
#ifndef P_T10_BALLW
#define P_T10_BALLW 200  // t10plan-v3i: weight of the opening ball group (no leash on the others)
#endif
#ifndef P_T10_BIGWAIT
#define P_T10_BIGWAIT 25  // t10plan-v3i: rounds the first champion waits 6-8 off a big group for 3 of us (0 = off)
#endif
#ifndef P_T10_ESCHOME
#define P_T10_ESCHOME 1  // t10plan-v3i: an escort goes home when its carry recalls or stands on our spawn
#endif
#ifndef P_T10_RECALLTOG
#define P_T10_RECALLTOG 0  // t10plan-v3: recall with a visible ally within 6 that recalls (when hurt or carrying 60+ gold)
#endif
#ifndef P_T10_DEPART
#define P_T10_DEPART 10  // t10plan-v3: rounds a healed champion waits on the spawn for an ally still healing there (0 = off)
#endif
#ifndef P_T10_FARCUT
#define P_T10_FARCUT 0   // t10plan-v3: the schedule only on near maps (spawn-to-spawn walk below this; 0 = every map)
#endif
#ifndef P_T10_END
#define P_T10_END 800    // t10plan-v3: the plan weight fades linearly from P_T10_UNTIL to this round
#endif
#ifndef P_T10_BALL
#define P_T10_BALL 0    // t10plan-v3: until this round the scheduled group admits the whole team (opening in a ball)
#endif
#ifndef P_T10_BIGSTR
#define P_T10_BIGSTR 120 // t10plan-v3: a scheduled group this strong (two elks or more) admits 4
#endif
#ifndef P_T10ROLES
#define P_T10ROLES 1     // escorts (HoR, Vendetta, Ryth, ...) farm their carry's (Vesper, Marcella) claimed group, within 8 of it
#endif
#ifndef P_T10_ESCW
#define P_T10_ESCW 150   // score % of the carry's group for its escort
#endif
#ifndef P_T10_LO
#define P_T10_LO 50      // score % for a group outside the top-10 plan of this window (plan known for the map)
#endif
#ifndef P_T10_HI
#define P_T10_HI 250     // score % for the window's main group (linear in its share from P_T10_LO)
#endif
#ifndef P_T10_FREE
#define P_T10_FREE 25    // share % of the window's main group from which the half/doorstep penalties and the solo-cluster rule are lifted
#endif
#define P_TRIBUTE_GEMS 12
#define P_TRIBUTE_NEAR 8
#define P_SHOP_GOLD 240
#define P_MAX_SHARE 4
#define P_SHAREEXP 75        // study27: a champion joining a big camp values it at gems / team^0.75 (was an even split)
#define P_STACK_HP 3000      // study27: big camp = 3000+ hp (2-3 elks, elk + wolves, 3 wolves); smaller camps keep the even split
#define P_GOLD_W_EARLY 100
#define P_GOLD_W_LATE 24
#define P_ONE_CAP 1
#define P_SHOP_RECALL 180
#define P_OWN_ALTAR 20
#define P_RESPAWN 4
#define P_CHAIN 36
#define P_HALF 30

#define P_UNSTICK 30
#define P_ALTAR_REACH 1
#define P_PAIR 2
#define P_RESERVE_PCT -60
#define P_SHOPFIX 1     // finish the item list on later turns if init ran out of fuel; no shop trips that buy nothing
#define P_PATHD 1       // camp choice by walking distance (walls), not straight-line distance
#define P_SWEEP 3
#define P_HOLD 200

#define P_E_RETARGET 6


#define P_R34_BANKCOST 300
#define P_R34_SHARE 2
#define P_O36_REPLACE 0

#define P_CAPRECALL 2  // recall on the capture tiles on every map (capture and recall run together)

// study26 (2026-10-15 fix list). Each fix is a switch; measured alone and together vs study25 on 313 maps
// (official 9 + gen 44 + hold60 + dev200), scored by maps won on both sides.
#define P_DASHFIX 1          // enemy Issac (not Cassi) has the dash: reach 3 tiles next round. Bug fix.
#define P_U34_RESET_LIVE 2   // spend the attack reset only if the first hit left the target alive, on every map
#define P_CASTSAFE 0         // skip a rooting cast when we should escape: lost 15-30 (hp only) and 12-29 (70%), off

// 2026-10-16 fuel guard: the same decisions for less fuel (turns that ran out were suspended and played a round
// late). P_FUELPROF 1 + a debug build (`cambc run` without --release) prints fuel per turn section.
#define P_FUELGUARD 1
// ---- genetic algorithm genome (tools/ga): fight parameters ----
#define P_FLEE_PCT 29
#define P_UNI_FLEE 33
#define P_RECALL_PCT 54
#define P_RECALL_NEAR 7
#define P_BAIL_PCT 12
#define P_AVOID_DIST 2
#define P_GA_AVOID_HP 45
#define P_ENGAGE2 74
#define P_GA_FAV 83
#define P_GA_KILL_X 5
#define P_LOWHP 40
#define P_GA_SPAWN_HEAL 87
#define P_FRONT_ZONE 3
#define P_FRONT_OUT 145
#define P_KITE_ZONE 4
// P_VKITE (vkite-v1, 10-23, vesper.h): a ranged champion that steps cannot attack that turn and one that attacks cannot step
// (engine 1.0.3 probe: can_attack 1->0 after every kite step, can_move 0 after 145/145 hits). Our kite stepped first,
// so in reach after r400 our Vesper hit 21% of rounds against 34% for the top 10, and moved+hit 0.3% of its hits
// against 27% (they shoot, then dash). 1: with the focus in range, shoot first, then dash out of reach when the dash
// is ready; with no dash ready, still shoot unless hurt below P_VKITE_HP% and threatened.
#define P_VKITE 1
#define P_VKITE_HP 45
#define P_KITE_OUT 2
#define P_GA_KITE_HP 128
#define P_VOLLEY 43
#define P_CHASE_GEMS (P_E1C ? 60 : 144)  // econ3 E1c (audit: fight-layer rule, own flag): 144 -> 60
#ifndef P_E1C
#define P_E1C 0
#endif
#define P_DANGER 4
#define P_DANGER_T 45
#define P_DANGER_R 5
#define P_JACKPOT (P_E1 ? 550 : 350)  // I042; econ3 E1: 350 -> 550
#define P_JACKGO (P_E1 ? 550 : 350)  // I045: from r350 the jackpot is a team job for P_JACKN champions (stampede)
#define P_JACKN 3
#define P_CAMPFOE 5
#define P_BACKHOME 6
#define P_NEEDHEAL 8
#define P_KITEALLY 12
#define P_NOCHASE2 ((P_TEAM_FIGHT && P_TF_GLOBAL) ? 0 : 1)  // team-fight-v1 lifts it on all paths when P_TF_GLOBAL
#define P_TWIN 1
#define P_MAPPLAN 1
#define P_TRACK_RET 6
#define P_PV 1
#define P_PV_LEAVE 60
#define P_PV_ER 6
#define P_MP_DASHHOLE 4

// Values that used to be #ifndef defaults spread over the headers (base-v53 cleanup: all switches live here).
#define P_ALTAR_SAFE 0
#define P_BAG 0
#define P_BAG_QUIET 40
#define P_CACHE 0
#define P_CAPHOME 0
#define P_CAPHOME_RSAFE 0
#define P_CAPHOME_TRIB 1
#define P_CAPPRIO 0
#define P_CAPRECALL_DELAY 1
#define P_CHAIN_R 8
#define P_DPSFARM 0
#define P_GANG 0
#define P_GROUP_R 0 // > 0: in group mode followers walk back to within this of the leader, and the leader waits
#define P_GROUP_W 5
#define P_HELP_R 6
#define P_HOLD_R 6
#define P_JACKW 10
#define P_LATE_ROUND 1850
#define P_LEAN_RADIUS 12
#define P_MP_ALTARS 4
#define P_MP_CHAINPLAN 0
#define P_MP_CHAIN_N 15
#define P_MP_CHAIN_T 30
#define P_MP_COMPANY 0
#define P_MP_STICK 0
#define P_MP_STICK_D 15
#define P_MP_TS 5
#define P_NOLEAVE 0
// P_VCARRY R (vcarry-v1, 10-24): Vesper is the team's carry on rewards. Top-10 Vesper took 31-42% of her team's capture
// gold (135-158 gold a capture), ours 15-23% (80); of 20+ gem rewards of groups she helped kill the top 10's Vesper
// took 1.6-2.3 a game and their allies 1.1-1.3, ours 0.5-1.2 against 1.5-1.8 for allies, while she was 8 tiles away
// at the capture. With a Vesper drafted: (a) shared rewards use P_CAPPRIO-style priority with Vesper first (allies
// yield when she claims it within R or stands next to it) and everybody else equal (nearest first, as now);
// (b) Vesper does not leave a reward waiting within P_VCARRY_NL tiles (P_NOLEAVE's rule, for her only) unless a
// rival is within P_VCARRY_FOE. 0 = off (no Vesper in the draft = off too).
#define P_VCARRY 4
#define P_VCARRY_NL 6
// vcarry-open (10-24): only until this round. Local vs rTop1, vcarry raised team gold +9% at r150/r300 (Vesper 98 -> 221
// at r150, top 10 196) but not at r800, and the allies died more later (hard panel -16).
#define P_VCARRY_UNTIL 200
#define P_VCARRY_FOE 5
#define P_OUTNUM 0
#define P_POT 0
#define P_PROFILE 0 // 0: one profile for every map (the P_* values); 1: per-family overrides below
#define P_PROF_LONG 40 // at or over this a map is a long farm map
#define P_PROF_RUSH 22 // spawn centre to enemy spawn centre (tiles) at or under which a map is a rush map
#define P_PV_FIGHT 125
#define P_PV_GAP 4
#define P_PV_R 6
#define P_STICK 125 // score bonus in % for the current target (hysteresis)
#define P_SW5_ALLY 1 // P_SWEEP 5: and at least this many of us within 4 (me included)
#define P_SW5_OUT 1 // P_SWEEP 5: stand and cast only with foes within 5 <= allies within 4 (me included) + this
#define P_TRACK_ALLYMEM 2 // rounds a remembered ally still counts at its last tile
#define P_TRACK_FAV 0 // >0: engage verdict = Lanchester power (sum hp x sum dps) of us vs them around the target,
#define P_TRACK_ISO 0 // >0: target a lone enemy (no other known enemy within 6) that the allies near it kill
#define P_TRACK_MEM 3 // rounds an unseen enemy keeps counting at its last tile (ghost)
#define P_TRACK_STATR 10
#define P_TWINFARM 0
#define P_UNI_PATH 45
#define P_UNI_STAND_HP 40
#define P_VOLLEY_FIGHT 0
#define P_VOLLEY_R 1
#define STATUS_EVERY 25

#ifndef P_RC_QUIET
#define P_RC_QUIET 2   // rounds with no hit and no rival within 6 before a recall (0 = off)
#endif

#ifndef P_TEAM_FIGHT
#define P_TEAM_FIGHT 1  // team-fight-v1 finish layer
#endif
#ifndef P_HPSHARE2
#define P_HPSHARE2 1  // hpshare-v1: hp share of shards per champion from engine-3 rivals
#endif
#ifndef P_GOLDONLY
#define P_GOLDONLY 1  // goldfarm-v1: gold-only camp groups are farm targets (valued gold_w per gold)
#endif
#ifndef P_HP_SHOP
#define P_HP_SHOP 1  // team-fight-v1 hp shards
#endif
#ifndef P_TF_GUARD
#define P_TF_GUARD 1  // team-fight-v1: rivals chasing our hurt champions are targets too
#endif
#ifndef P_BCF
#define P_BCF 1  // pack-v4: bcf-v3 (LEAVE = one cheap step home); bcf-v1 (thread "Copiar las decisiones del top 10"): learned engage decision bcfight.h; 2 = also its LEAVE leaves
#endif
#ifndef P_TF_GLOBAL
#define P_TF_GLOBAL 0  // 1: the no-chase lift for hurt rivals applies to every fight path; 0: only the finish block
#endif

// ---- econ3 (2026-10-20): v76 retuned to the cambc 3.0 economy. Design: analysis/claude-api-2026-10-18/econ3_design_1020.md.
// Each lever is a switch; all four at 0 builds the same wasm as team-fight-v1 (tf3).
#ifndef P_E1
#define P_E1 1  // constants and round gates: gold-weight switch r600->r940 and jackpot r350->r550 (3.0 gold income
                // 6.6 vs 10.3 per round, x1.56); P_CHASE_GEMS 144->60 (same share of carried bags and the same rounds of
                // team income as 144 was in 2.2.5)
#endif
#ifndef P_E2
#define P_E2 0  // OFF in the shipped econ3: with it on, 72-90 vs tf3 and -650 gold a game (ablation: 85-77 without it). camp ranking. 1: a wolf-only group scores x P_E2_WOLF/100: the bench ledger (gems + 0.25 gold per
                // champion-round, travel, waits, contest and recovery included) gives wolf 0.31 vs elk 0.40, and the
                // model's gold-heavy value (4 gems + 0.25 x 55 gold) hides that a wolf pays half an elk's gems for the
                // same gold. 2: gold weight 10 (tested, rejected: -28% gold, +33% deaths). 3: gold weight 40.
#endif
#define P_E2_WOLF 78
#ifndef P_MG
#define P_MG 1  // monoguard-v1 (thread "Cómo muere", 10-24): an awake monolith (200 a round to everyone within 5) kills V20 2.2 champions
                // per game on gold_rush before r150 (rival 0.95; top10 0.03/game over all near maps vs our 0.095). Unless every gem is in a
                // monolith group (P_MONO's mono_only: contest) or half the map's gems sit in monolith groups with gem clusters (the monolith map,
                // farmed on purpose; gold_rush's monolith group only has gold clusters), its range is a wall for pathing and a champion inside steps out first. Only for a monolith whose
                // group also holds clusters (killing one wakes it; lone monoliths like boss_battle's are woken on purpose), and not for
                // the group we target.
                // 2: also never target a group that holds a living monolith (its 120-hp clusters wake it).
#endif
#ifndef P_E3
#define P_E3 1  // camp facts: monster stats from the engine design (clusters 120 hp, golem 5000/120), awake checks and the
                // rally ring use each camp's attack_range (elk 4, monolith 5, golem 4)
#endif
#ifndef P_E4
#define P_E4 1  // a spell that kills the camp is not followed by a basic attack on the dead camp: hit another live camp
                // of the group, or step toward it, or onto the reward tiles
#endif

#define P_FUELFIX 1        // cambc 3.0 wide maps: choose without the distance field instead of fuel-waiting
#define P_FUELFIX_NEED 25000
#define P_SEALED 1        // boss_battle: an altar walled in by a camp is no altar; farm instead of waiting at it
#define P_WARD 1           // vision-v1: ward the unseen bushes near us whenever the ward is ready
#define P_WARD_R 6         // look for dark bush tiles within this Chebyshev radius
#define P_WARD_MIN 2       // place only if the ward lights at least this many dark bush tiles
#define P_WARD_TRY 6       // candidate tiles evaluated per turn (one vision query each); fuelfit o10: 12 -> 6
#define P_WARD_FUEL 12000  // fuelcut-v3: ward gate on top of the fuel savings

#ifndef P_META
#define P_META 1  // draft-meta-v1: one draft for every map, the 3.0 top-10 core
#endif
#ifndef P_KINDFIX
#define P_KINDFIX 1  // draft-meta-v1b: melee and dash read from attack_range()/is_dash(), not name lists
#endif

#ifndef P_NEED_CAP
#define P_NEED_CAP 2  // feas-a: a camp group never "needs" more than this many champions
#endif
#ifndef P_ISLEFIX
#define P_ISLEFIX 10  // islefix-v1: fight-camp turns with no step and no hit before the group is dropped
#endif
#ifndef P_RF_DEFER
#define P_RF_DEFER 1  // fuelfit o67: the periodic target refresh waits until the reverse fields exist (1) or not (0 = b15)
#endif
#ifndef P_RF_DEFER_AREA
#define P_RF_DEFER_AREA 5000  // fuelfit o67: only on maps with at least this many tiles (the forward field is cheap below; fracture 61x71 = 4331 lost its first-target correction)
#endif
#ifndef P_RF_DEFER_R
#define P_RF_DEFER_R 60  // fuelfit o67: no deferral from this round on
#endif
#ifndef P_DH_ROUND
#define P_DH_ROUND 6  // o74: round of the dash-hole scan on 12+ group near maps (out of the start-up turn)
#endif
#ifndef P_MP_HOLE
#define P_MP_HOLE 2  // o68: 1 = dash champions plan across crossable holes (mapplan rule 5); 0 = never; 2 = only when no dash-less ally shares the target
#endif
#ifndef P_MP_HOLE_SMALL
#define P_MP_HOLE_SMALL 0  // o68 v3: no hole routes at all on maps with fewer tiles than this (0 = no size rule); 2500 covers reverse_spiral (900) and rushbait_v2 (2400)
#endif
#ifndef P_INC_PCT
#define P_INC_PCT 100  // t10plan-v17: back to the full model (kvvl). With 50 (o100) online v16 r30-150 camp deaths were 0.37/game vs kvvl 0.11: full-hp champions die in 7-9 rounds in groups they cannot clear
#endif
#ifndef P_HOLEFIX
#define P_HOLEFIX 12  // holefix-v1: drop a dash-over-hole route after this many rounds without progress (0 = off)
#endif
#ifndef P_HORFOCUS
#define P_HORFOCUS 1  // horfocus-v1: HoR buys focus and casts its dash onto targets
#endif

#ifndef P_DRAFT_SWAP
#define P_DRAFT_SWAP 1  // draft-marc-v1 (analysis/overnight-1021/v110_drop_champions.md)
#endif

#ifndef P_BRUISER_FILL
#define P_BRUISER_FILL 1  // bruiser-fill-v1 (analysis/overnight-1021/v110_drop_champions.md)
#endif

#ifndef P_DRAFT_SWAP2
#define P_DRAFT_SWAP2 1  // mv-vesp-v1 (analysis/overnight-1021/v110_drop_champions.md)
#endif

#ifndef P_DRAFT_SWAP3
#define P_DRAFT_SWAP3 1
#endif

#ifndef P_DHFUEL
#define P_DHFUEL 1  // t10draft-fx-v1: resumable, fuel-checked dash-hole scan
#endif
#ifndef P_DHFUEL_NEED
#define P_DHFUEL_NEED 150000
#endif

#ifndef P_VESP_CASTER
#define P_VESP_CASTER 1  // t10draft-v2
#endif
#define P_T10SHOP 1

#ifndef P_IDLE_HOLD
#define P_IDLE_HOLD 30
#endif
#ifndef P_IDLE_TRIP
#define P_IDLE_TRIP 1
#endif
#ifndef P_IDLE_NOSTEP
#define P_IDLE_NOSTEP 4
#endif
#ifndef P_IDLE_BAD
#define P_IDLE_BAD 200
#endif
#ifndef P_WD
#define P_WD 50
#endif

#ifndef P_TPC
#define P_TPC 1
#define P_TPC_GAIN 20
#define P_TPC_EVERY 100
#define P_TPC_PATH 80
#endif
#ifndef P_IDLE_FUEL
#define P_IDLE_FUEL 40000
#endif
#ifndef P_ISLE
#define P_ISLE 1
#endif
#ifndef P_ISLE_MAX
#define P_ISLE_MAX 80
#endif
#ifndef P_ISLE_KEEP
#define P_ISLE_KEEP 30
#endif
#ifndef P_ISLE_STILL
#define P_ISLE_STILL 10
#endif

// farswap-v1: on far maps (spawn path >= 60) draft P_FAR_SWAP instead of HoR (HoR farms 3.1k camp damage by r400; rivals 5.4k)
#define P_FAR_SWAP "ren"

#ifndef P_FUELCUT
#define P_FUELCUT 1  // fuelcut-v1: same decisions, fewer engine calls (shop off spawn, group state)
#endif
#ifndef P_BRCACHE
#define P_BRCACHE 1  // brcache-v1: static per-altar fields instead of a field from pos every move
#endif
#ifndef P_BRC_R0
#define P_BRC_R0 3   // fuelfit o22: first round of the altar-field schedule
#endif
#ifndef P_BRC_PER
#define P_BRC_PER 2  // fuelfit o22: altar fields built per turn
#endif
#ifndef P_BRC_BUILD
#define P_BRC_BUILD 45000
#endif

#ifndef P_FINISH
#define P_FINISH 1  // finish-v1: hold flee/avoid/kite one turn to hit a foe below 30% in reach + 1
#endif

// richcap-v2 (map thread 10-23): gold weighs 0.45 of a gem from r150; 20+ gem clusters can be shared
#define P_RC2 1
#define P_RC2_R 150
#define P_RC2_GW 45

#ifndef P_LSHOP
#define P_LSHOP 1  // lshop-v2: champion's late fill mix (champ::late_mix) from P_LSHOP_R
#endif
#ifndef P_LSHOP_R
#define P_LSHOP_R 400
#endif
#ifndef P_PAIRFARM
#define P_PAIRFARM 1     // pairfarm-v2: near maps, r30-150, prefer camps next to an ally's camp (the top 10 are never fully spread)
#endif
#ifndef P_PF_FROM
#define P_PF_FROM 30
#endif
// first round it applies
#ifndef P_PF_UNTIL
#define P_PF_UNTIL 150
#endif
// last round it applies
#ifndef P_PF_MAX
#define P_PF_MAX 35
#endif
// near maps: spawn-to-spawn path length below this
#define P_PF_FAR 40      // score % for a group with no ally's claimed group within P_PF_R
#define P_PF_R 6
#ifndef P_PF_WALK
#define P_PF_WALK 1      // pairfarm-v3: walk with an ally bound for a neighbouring camp (step toward it, at most P_PF_WAIT rounds per target)
#endif
#define P_PF_WAIT 8
#ifndef P_WAITPAIR
#define P_WAITPAIR 1     // waitpair-v1: wait for a respawn next to an ally (near maps, r30-150)
#endif
#define P_WAITPAIR_D 12  // the ally (seen or estimated) at most this far from the camp
#ifndef P_HITLAST
#define P_HITLAST 0      // hitpass-v2: an unused attack at the end of the turn takes a finishing blow on a camp in reach
#endif
#ifndef P_HITLAST_FAR
#define P_HITLAST_FAR 60  // o70 v3: hitpass off when the spawn-to-spawn walk (pf_spawn_path, cached) is 60+ (far maps: PC 800 g lejanos -20, medios +4, cercanos -2)
#endif
#ifndef P_CUT
#define P_CUT 1          // o95 cut: Vendetta and Marcella leave a contact early (0 = off)
#endif
#ifndef P_CUT_PCT
#define P_CUT_PCT 40     // o95: leave when health minus the last 2 rounds' damage is below this % of max
#endif
#ifndef P_CUT_MAX
#define P_CUT_MAX 70     // o95: only below this % of max health
#endif
#ifndef P_FOCO
#define P_FOCO 1         // o107 foco: one focus rival for the team in byte SM_PLAN (0 = off)
#endif
#ifndef P_FOCO_R
#define P_FOCO_R 4       // o107: a rival within this of a visible ally counts as engaged
#endif
#ifndef P_FOCO_D
#define P_FOCO_D 1       // o107: the step-3 target counts distance only beyond reach + 1
#endif
#ifndef P_SHOT
#define P_SHOT 1         // o108 disparo: one firing point (focus in reach, else lowest health in reach) for attacks and damage spells (0 = off)
#endif

// t10plan-v14 (an/state14.py on the 160 online games vs ranks 5-20, r30-150): every alive bucket (hitting, walking, waiting,
// recalling, fighting, fleeing) is the same per alive round; the missing 25 hitter-rounds are 45 champion-rounds DEAD per game
// (1.54 deaths vs 0.65, 60 rounds each). 73% of ours are champion kills: 2+ foes come within 6 about 16 rounds before the death
// with us at 90% hp and 0.8 allies near, the held "stay" is never judged again and we trade down to 0 (5 rounds before:
// 2.7 foes, 0.8 allies, 43% hp). 27% die to a camp, farming alone at ~50% hp.
//   P_V14        0 off (v4o2 byte for byte); 1 on, from round P_V14_R
//   P_V14_RATIO  with 2+ foes within 6, a power ratio x100 under this makes the verdict "leave" (judged every turn, not once)
//   P_V14_LOWHP  alone (no ally within 6) under this hp %, any foe within 6 and ratio < 1: leave
//   P_V14_BAIL   farming with no ally within 6: bail out of the camp under this hp % (v4o2: P_BAIL_PCT 12 for all)
#define P_V14 1
#define P_V14_R 30
#define P_V14_RATIO 80
#define P_V14_LOWHP 50
#define P_V14_BAIL 25
// t10plan-v16 (verdict.h v14_judge): leave when a melee foe with a dash ready is within P_V16_D and 2+ foes within 6, ratio x100 < P_V16_RATIO
#define P_V16 1
#define P_V16_R 30
#define P_V16_D 4
#define P_V16_RATIO 100
// t10plan-v21 (support_spells): the self-shield is cast whenever ready in combat (foe within 4 or an awake camp near), not only under
// 85% hp. Online c37 (v16, 75 games): rival HoR shields 16,895 hp/game, ours 5,188; abilities 14.3 vs 6.4 per 100 alive turns;
// rival HoR dies 0.81/game, ours 4.0.
#define P_V21 1

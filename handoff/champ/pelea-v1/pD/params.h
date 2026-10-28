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
#define P_WARD_TRY 12      // candidate tiles evaluated per turn (one vision query each)
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
#define P_PF_FROM 30     // first round it applies
#define P_PF_UNTIL 150   // last round it applies
#define P_PF_MAX 35      // near maps: spawn-to-spawn path length below this
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

// pelea-v1 per champion (vesper.h vkite-v3, marcella.h mstick-v1)
#ifndef P_VK3
#define P_VK3 1
#endif
#ifndef P_VK3_HP
#define P_VK3_HP 0     // 0 = hp does not matter; else keep shooting above this % hp
#endif
#ifndef P_MS
#define P_MS 0
#endif
#ifndef P_MS_HP
#define P_MS_HP 70
#endif
#ifndef P_MS_NUM
#define P_MS_NUM 0     // back off when 1 + allies - rivals (within 3) <= this
#endif

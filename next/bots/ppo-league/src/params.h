#define P_TRIBUTE_GEMS 12
#define P_TRIBUTE_NEAR 8
#define P_SHOP_GOLD 240
#define P_MAX_SHARE 4
#define P_SHAREEXP 75        // study27: a champion joining a big camp values it at gems / team^0.75 (was an even split)
#define P_STACK_HP 3000      // study27: big camp = 3000+ hp (2-3 elks, elk + wolves, 3 wolves); smaller camps keep the even split
#define P_GOLD_W_EARLY 25
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
#define P_KITE_OUT 2
#define P_GA_KITE_HP 128
#define P_VOLLEY 43
#define P_CHASE_GEMS 144
#define P_DANGER 4
#define P_DANGER_T 45
#define P_DANGER_R 5
#define P_JACKPOT 350  // I042
#define P_JACKGO 350  // I045: from r350 the jackpot is a team job for P_JACKN champions (stampede)
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
#ifndef P_HP_SHOP
#define P_HP_SHOP 1  // team-fight-v1 hp shards
#endif
#ifndef P_TF_GUARD
#define P_TF_GUARD 1  // team-fight-v1: rivals chasing our hurt champions are targets too
#endif
#ifndef P_TF_GLOBAL
#define P_TF_GLOBAL 0  // 1: the no-chase lift for hurt rivals applies to every fight path; 0: only the finish block
#endif

#define P_TRIBUTE_GEMS 12
#define P_TRIBUTE_NEAR 8
#define P_SHOP_GOLD 240
#define P_MAX_SHARE 4
#define P_SHAREEXP 75        // study27: a champion joining a big camp values it at gems / team^0.75 (was an even split)
#define P_STACK_HP 3000      // study27: big camp = 3000+ hp (2-3 elks, elk + wolves, 3 wolves); smaller camps keep the even split
#define P_GOLD_W_EARLY 25
#define P_GOLD_W_LATE 24
#define P_RETREAT 0
#define P_ONE_CAP 1
#define P_SHOP_RECALL 180
#define P_SAFE_RECALL 1
#define P_OWN_ALTAR 20
#define P_RESPAWN 4
#define P_CHAIN 36
#define P_HALF 30

#define P_UNJAM 1
#define P_UNSTICK 30
#define P_ALTAR_REACH 1
#define P_SHOOT 1
#define P_SHOP_PLAN 3
#define P_PAIR 2
#define P_HITFIRST 1
#define P_SAFESTEP 1
#define P_RESERVE_PCT -60
#define P_FRONT 1
#define P_FRONT_LOCAL 1
#define P_NOCHASE 1
#define P_SHOPFIX 1     // finish the item list on later turns if init ran out of fuel; no shop trips that buy nothing
#define P_PATHD 1       // camp choice by walking distance (walls), not straight-line distance
#define P_NOGOLD 1      // skip gold-only clusters
#define P_DRAFTUNI 2   // the #1 (Univardisty) caster draft by team size when the spawn-to-spawn path <= 45
#define P_SHOPUNI 1
#define P_KITE 1
#define P_SWEEP 3
#define P_HOLD 200
#define P_UNI_RN 1

#define P_E_RETARGET 6
#define P_NE_POWER_OPEN 1
#define P_R5_LOCK 1

#define P_D5_PACKED_CLAIMS 1

#define P_U34_ATTACK_LIVE 0

#define P_U34_FARM_REACH 1

#define P_U34_FAILED_CHANNELS 0

#define P_U34_ENGAGE_FALLBACK 0

#define P_U34_POST_FREE 0
#define P_D34_FAMILY 1
#define P_R34_BANKCOST 300
#define P_R34_SHARE 2
#define P_O36_REPLACE 0

#define P_CAPRECALL 2  // recall on the capture tiles on every map (capture and recall run together)
#define P_CAPTURE_RECALL_FIX 1  // prefer safe loot capture over non-emergency recalls; 0 = prior behavior

// study26 (2026-10-15 fix list). Each fix is a switch; measured alone and together vs study25 on 313 maps
// (official 9 + gen 44 + hold60 + dev200), scored by maps won on both sides.
#define P_DASHFIX 1          // enemy Issac (not Cassi) has the dash: reach 3 tiles next round. Bug fix.
#define P_U34_RESET_LIVE 2   // spend the attack reset only if the first hit left the target alive, on every map
#define P_AOE 2              // Stellar's area spell aims at the tile hitting the most foes; goes first with 2+ under it
#define P_CASTSAFE 0         // skip a rooting cast when we should escape: lost 15-30 (hp only) and 12-29 (70%), off
#define P_KITEFRONT 0        // 1 = front line before kite, 2 = kite shoots the team focus: both noise, off
#define P_R5_WARD 0          // wards: 55-58 maps won/lost both sides, noise again, off

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
#define P_NOCHASE2 1
#define P_TWIN 1
#define P_ALLYDUTY 1
#define P_AVOIDFIRST 1
#define P_MAPPLAN 1
#define P_ROSTER 1
#define P_OCMEMO 1
#define P_TRACK 1
#define P_TRACK_RET 6
#define P_PV 1
#define P_PV_LEAVE 60
#define P_PV_ER 6
#define P_MP_DASHHOLE 4

#define P_TRIBUTE_GEMS 12
#define P_TRIBUTE_NEAR 8
#define P_RECALL_PCT 55
#define P_FLEE_PCT 25
#define P_SHOP_GOLD 240
#define P_MAX_SHARE 4
#define P_SHAREEXP 75        // study27: a champion joining a big camp values it at gems / team^0.75 (was an even split)
#define P_STACK_HP 3000      // study27: big camp = 3000+ hp (2-3 elks, elk + wolves, 3 wolves); smaller camps keep the even split
#define P_GOLD_W_EARLY 25
#define P_GOLD_W_LATE 24
#define P_BAIL_PCT 18
#define P_AVOID_DIST 4
#define P_RETREAT 0
#define P_ONE_CAP 1
#define P_SHOP_RECALL 180
#define P_SAFE_RECALL 1
#define P_OWN_ALTAR 20
#define P_RESPAWN 4
#define P_CHAIN 36
#define P_HALF 30

#define P_ENGAGE2 120
#define P_LOWHP 50
#define P_UNJAM 1
#define P_UNSTICK 30
#define P_ALTAR_REACH 1
#define P_SHOOT 1
#define P_SHOP_PLAN 3
#define P_PAIR 2
#define P_HITFIRST 1
#define P_SAFESTEP 1
#define P_RESERVE_PCT -60
#define P_DANGER 3
#define P_FRONT 1
#define P_FRONT_LOCAL 1
#define P_FRONT_OUT 130
#define P_NOCHASE 1
#define P_SHOPFIX 1     // finish the item list on later turns if init ran out of fuel; no shop trips that buy nothing
#define P_PATHD 1       // camp choice by walking distance (walls), not straight-line distance
#define P_NOGOLD 1      // skip gold-only clusters
#define P_DRAFTUNI 2   // the #1 (Univardisty) caster draft by team size when the spawn-to-spawn path <= 45
#define P_SHOPUNI 1
#define P_KITE 1
#define P_KITE_OUT 2
#define P_SWEEP 3
#define P_HOLD 200
#define P_RECALL_NEAR 5 // recall with the nearest foe 5+ tiles away (caster draft only, P_UNI_RN)
#define P_UNI_RN 1
#define P_UNI_FLEE 35   // caster draft: run/recall below 35% hp (vs the v27-engine caster sparring: 20-10, deaths 226 vs 267)
#define P_VOLLEY 70
#define P_KITE_ZONE 4

#define P_E_RETARGET 6
#define P_NE_POWER_OPEN 1
#define P_R5_LOCK 1

#define P_D5_PACKED_CLAIMS 1

#define P_U34_ATTACK_LIVE 0

#define P_U34_RESET_LIVE 1

#define P_U34_FARM_REACH 1

#define P_U34_FAILED_CHANNELS 0

#define P_U34_ENGAGE_FALLBACK 0

#define P_U34_POST_FREE 0
#define P_D34_FAMILY 1
#define P_R34_BANKCOST 300
#define P_R34_SHARE 2
#define P_O36_REPLACE 0

#define P_CAPRECALL 2  // recall on the capture tiles on every map (capture and recall run together)

// study26 (2026-10-15 fix list). Each fix is a switch; measured alone and together vs study25 on 313 maps
// (official 9 + gen 44 + hold60 + dev200), scored by maps won on both sides.
#define P_DASHFIX 1          // enemy Issac (not Cassi) has the dash: reach 3 tiles next round. Bug fix.
#define P_U34_RESET_LIVE 2   // spend the attack reset only if the first hit left the target alive, on every map
#define P_AOE 2              // Stellar's area spell aims at the tile hitting the most foes; goes first with 2+ under it
#define P_CASTSAFE 0         // skip a rooting cast when we should escape: lost 15-30 (hp only) and 12-29 (70%), off
#define P_KITEFRONT 0        // 1 = front line before kite, 2 = kite shoots the team focus: both noise, off
#define P_R5_WARD 0          // wards: 55-58 maps won/lost both sides, noise again, off

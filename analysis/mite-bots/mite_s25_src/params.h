#define P_TRIBUTE_GEMS 12
#define P_TRIBUTE_NEAR 8
#define P_RECALL_PCT 55
#define P_FLEE_PCT 25
#define P_SHOP_GOLD 240
#define P_MAX_SHARE 3
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
#define P_HALF 10

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
#define P_FRONT_LOCAL 0
#define P_FRONT_OUT 250
#define P_NOCHASE 1
#define P_SHOPFIX 1     // finish the item list on later turns if init ran out of fuel; no shop trips that buy nothing
#define P_PATHD 1       // camp choice by walking distance (walls), not straight-line distance
#define P_NOGOLD 1      // skip gold-only clusters
#define P_DRAFTUNI 2   // the #1 (Univardisty) caster draft by team size when the spawn-to-spawn path <= 45
#define P_SHOPUNI 1
#define P_KITE 0
#define P_KITE_OUT 2
#define P_SWEEP 3
#define P_HOLD 200
#define P_RECALL_NEAR 5 // recall with the nearest foe 5+ tiles away (caster draft only, P_UNI_RN)
#define P_UNI_RN 1
#define P_UNI_FLEE 35   // caster draft: run/recall below 35% hp (vs the v27-engine caster sparring: 20-10, deaths 226 vs 267)
#define P_VOLLEY 0
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
#define P_MITE_SHOP 1
#define P_MITE_FIGHT 1
// mite_s25 = study25 + the Mite rules that did not lose on the gen maps: P_MITE_SHOP, P_MITE_FIGHT (+ P_KITE 0, P_VOLLEY 0,
// P_FRONT_LOCAL 0, P_FRONT_OUT 250), P_HALF 10. P_MITE_DRAFT (6-22 maps) and P_MITE_RECALL (6-17) lost and stay off.

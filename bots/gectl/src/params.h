
#define P_UNJAM 1
#define P_ALTAR_REACH 1
#define P_SHOPFIX 1     // finish the item list on later turns if init ran out of fuel; no shop trips that buy nothing
#define P_UNI_RN 1

#define P_R5_LOCK 1

#define P_D5_PACKED_CLAIMS 1

#define P_U34_ATTACK_LIVE 0

#define P_U34_FARM_REACH 1

#define P_U34_FAILED_CHANNELS 0


#define P_U34_POST_FREE 0
#define P_D34_FAMILY 1
#define P_R34_SHARE 2
#define P_O36_REPLACE 0


// study26 (2026-10-15 fix list). Each fix is a switch; measured alone and together vs study25 on 313 maps
// (official 9 + gen 44 + hold60 + dev200), scored by maps won on both sides.
#define P_DASHFIX 1          // enemy Issac (not Cassi) has the dash: reach 3 tiles next round. Bug fix.
#define P_CASTSAFE 0         // skip a rooting cast when we should escape: lost 15-30 (hp only) and 12-29 (70%), off
#define P_KITEFRONT 0        // 1 = front line before kite, 2 = kite shoots the team focus: both noise, off
#define P_R5_WARD 0          // wards: 55-58 maps won/lost both sides, noise again, off


// ---- genetic algorithm genome (tools/ga/structure.py): weights, structure, programs, net ----
#define GA_HAVE_GENOME 1
volatile int ga_s[644] = {827539783, 1592612472, 126, 514, 29, 44, 54, 7, 12, 4, 60, 74, 83, 5, 50, 87, 3, 145, 4, 2, 128, 43, 144, 4, 45, 5, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 0, 0, 0, 25, 24, 600, 1, 4, 75, 3000, 2, -60, 30, 6, 60, 8, 125, 4, 70, 30, 8, 6, 0, 300, 200, 6, 6, 1, 12, 8, 10, 36, 8, 0, 40, 1850, 20, 0, 10, 12, 2, 1, 90, 90, 240, 50, 180, 3, 1, 1, 45, 1, 1, 12, 2, 3, 2, 2, 1, 30, 10, 1, 0, 6, 0, 0, 0, 0, 2, 33, 40, 45, 2, 17, 257, 11, 289, 11, 9, 1, 1922, 8, 33, 130, 13, 11, 10, 513, 11, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 289, 545, 10, 321, 257, 9, 577, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static const int ga_P_FLEE_PCT = ga_s[4];
static const int ga_P_UNI_FLEE = ga_s[5];
static const int ga_P_RECALL_PCT = ga_s[6];
static const int ga_P_RECALL_NEAR = ga_s[7];
static const int ga_P_BAIL_PCT = ga_s[8];
static const int ga_P_AVOID_DIST = ga_s[9];
static const int ga_P_GA_AVOID_HP = ga_s[10];
static const int ga_P_ENGAGE2 = ga_s[11];
static const int ga_P_GA_FAV = ga_s[12];
static const int ga_P_GA_KILL_X = ga_s[13];
static const int ga_P_LOWHP = ga_s[14];
static const int ga_P_GA_SPAWN_HEAL = ga_s[15];
static const int ga_P_FRONT_ZONE = ga_s[16];
static const int ga_P_FRONT_OUT = ga_s[17];
static const int ga_P_KITE_ZONE = ga_s[18];
static const int ga_P_KITE_OUT = ga_s[19];
static const int ga_P_GA_KITE_HP = ga_s[20];
static const int ga_P_VOLLEY = ga_s[21];
static const int ga_P_CHASE_GEMS = ga_s[22];
static const int ga_P_DANGER = ga_s[23];
static const int ga_P_DANGER_T = ga_s[24];
static const int ga_P_DANGER_R = ga_s[25];
static const int ga_P_FRONT = ga_s[26];
static const int ga_P_KITE = ga_s[27];
static const int ga_P_WALKHOME = ga_s[28];
static const int ga_P_HITFIRST = ga_s[29];
static const int ga_P_SAFESTEP = ga_s[30];
static const int ga_P_RETREAT = ga_s[31];
static const int ga_P_NOCHASE = ga_s[32];
static const int ga_P_FRONT_LOCAL = ga_s[33];
static const int ga_P_SHOOT = ga_s[34];
static const int ga_P_GANG = ga_s[35];
static const int ga_P_CALLHELP = ga_s[36];
static const int ga_P_TWIN = ga_s[37];
static const int ga_P_ALLYDUTY = ga_s[38];
static const int ga_P_CARRY = ga_s[39];
static const int ga_P_U34_ENGAGE_FALLBACK = ga_s[40];
static const int ga_P_R_FLEE = ga_s[41];
static const int ga_P_R_NEARRECALL = ga_s[42];
static const int ga_P_R_AVOIDLOW = ga_s[43];
static const int ga_P_R_AVOID = ga_s[44];
static const int ga_P_R_ENGAGE = ga_s[45];
static const int ga_P_R_RECALLSHOP = ga_s[46];
static const int ga_P_O_FLEE = ga_s[47];
static const int ga_P_O_NEARRECALL = ga_s[48];
static const int ga_P_O_FM = ga_s[49];
static const int ga_P_O_KITE = ga_s[50];
static const int ga_P_O_FRONT = ga_s[51];
static const int ga_P_O_AVOIDLOW = ga_s[52];
static const int ga_P_O_AVOID = ga_s[53];
static const int ga_P_O_ENGAGE = ga_s[54];
static const int ga_P_O_RECALLSHOP = ga_s[55];
static const int ga_P_O_WALKHOME = ga_s[56];
static const int ga_P_GP0_ON = ga_s[57];
static const int ga_P_GP1_ON = ga_s[58];
static const int ga_P_NN_ON = ga_s[59];
static const int ga_P_GOLD_W_EARLY = ga_s[60];
static const int ga_P_GOLD_W_LATE = ga_s[61];
static const int ga_P_GA_GOLD_ROUND = ga_s[62];
static const int ga_P_NOGOLD = ga_s[63];
static const int ga_P_MAX_SHARE = ga_s[64];
static const int ga_P_SHAREEXP = ga_s[65];
static const int ga_P_STACK_HP = ga_s[66];
static const int ga_P_PAIR = ga_s[67];
static const int ga_P_RESERVE_PCT = ga_s[68];
static const int ga_P_HALF = ga_s[69];
static const int ga_P_GA_HALF_D = ga_s[70];
static const int ga_P_GA_DOOR = ga_s[71];
static const int ga_P_GA_DOOR_D = ga_s[72];
static const int ga_P_STICK = ga_s[73];
static const int ga_P_RESPAWN = ga_s[74];
static const int ga_P_GA_NEEDCO = ga_s[75];
static const int ga_P_GA_SOLO = ga_s[76];
static const int ga_P_GA_CYCLE = ga_s[77];
static const int ga_P_GA_OVERHEAD = ga_s[78];
static const int ga_P_BANKW = ga_s[79];
static const int ga_P_R34_BANKCOST = ga_s[80];
static const int ga_P_HOLD = ga_s[81];
static const int ga_P_HOLD_R = ga_s[82];
static const int ga_P_E_RETARGET = ga_s[83];
static const int ga_P_ONE_CAP = ga_s[84];
static const int ga_P_TRIBUTE_GEMS = ga_s[85];
static const int ga_P_TRIBUTE_NEAR = ga_s[86];
static const int ga_P_GA_NEAR_GEMS = ga_s[87];
static const int ga_P_CHAIN = ga_s[88];
static const int ga_P_CHAIN_R = ga_s[89];
static const int ga_P_BAG = ga_s[90];
static const int ga_P_BAG_QUIET = ga_s[91];
static const int ga_P_LATE_ROUND = ga_s[92];
static const int ga_P_OWN_ALTAR = ga_s[93];
static const int ga_P_TELE = ga_s[94];
static const int ga_P_GA_TRIB_RC_GEMS = ga_s[95];
static const int ga_P_GA_TRIB_RC_D = ga_s[96];
static const int ga_P_CAPRECALL = ga_s[97];
static const int ga_P_CAPRECALL_DELAY = ga_s[98];
static const int ga_P_GA_CR_HEAL = ga_s[99];
static const int ga_P_GA_CR_GOLD = ga_s[100];
static const int ga_P_SHOP_GOLD = ga_s[101];
static const int ga_P_GA_SHOP_HP = ga_s[102];
static const int ga_P_SHOP_RECALL = ga_s[103];
static const int ga_P_SHOP_PLAN = ga_s[104];
static const int ga_P_SHOPUNI = ga_s[105];
static const int ga_P_NE_POWER_OPEN = ga_s[106];
static const int ga_P_UNI_PATH = ga_s[107];
static const int ga_P_SAFE_RECALL = ga_s[108];
static const int ga_P_PATHD = ga_s[109];
static const int ga_P_LEAN_RADIUS = ga_s[110];
static const int ga_P_DRAFTUNI = ga_s[111];
static const int ga_P_SWEEP = ga_s[112];
static const int ga_P_AOE = ga_s[113];
static const int ga_P_U34_RESET_LIVE = ga_s[114];
static const int ga_P_MONO = ga_s[115];
static const int ga_P_UNSTICK = ga_s[116];
static const int ga_P_GA_SS_ALLY = ga_s[117];
static const int ga_P_GA_SS_HOME = ga_s[118];
static const int ga_P_PAIR_N = ga_s[119];
static const int ga_P_PAIR_FOE = ga_s[120];
static const int ga_P_PAIR_STICK = ga_s[121];
static const int ga_P_PAIR_ENGAGE = ga_s[122];
static const int ga_P_PAIR_LOWHP = ga_s[123];
static const int ga_P_IM_PAIRED = ga_s[124];
static const int ga_P_IM_PAIR_R = ga_s[125];
static const int ga_P_UNI_FLEE_P = ga_s[126];
static const int ga_P_LOWHP_P = ga_s[127];
static const int ga_P_GA_AVOID_HP_P = ga_s[128];
static const int ga_P_AVOID_DIST_P = ga_s[129];
static bool g_ga_paired = false;  // im_p (tools/ga/pair.py), set each turn in play_turn
#define P_FLEE_PCT ga_P_FLEE_PCT
#define P_UNI_FLEE (g_ga_paired ? ga_P_UNI_FLEE_P : ga_P_UNI_FLEE)
#define P_RECALL_PCT ga_P_RECALL_PCT
#define P_RECALL_NEAR ga_P_RECALL_NEAR
#define P_BAIL_PCT ga_P_BAIL_PCT
#define P_AVOID_DIST (g_ga_paired ? ga_P_AVOID_DIST_P : ga_P_AVOID_DIST)
#define P_GA_AVOID_HP (g_ga_paired ? ga_P_GA_AVOID_HP_P : ga_P_GA_AVOID_HP)
#define P_ENGAGE2 ga_P_ENGAGE2
#define P_GA_FAV ga_P_GA_FAV
#define P_GA_KILL_X ga_P_GA_KILL_X
#define P_LOWHP (g_ga_paired ? ga_P_LOWHP_P : ga_P_LOWHP)
#define P_GA_SPAWN_HEAL ga_P_GA_SPAWN_HEAL
#define P_FRONT_ZONE ga_P_FRONT_ZONE
#define P_FRONT_OUT ga_P_FRONT_OUT
#define P_KITE_ZONE ga_P_KITE_ZONE
#define P_KITE_OUT ga_P_KITE_OUT
#define P_GA_KITE_HP ga_P_GA_KITE_HP
#define P_VOLLEY ga_P_VOLLEY
#define P_CHASE_GEMS ga_P_CHASE_GEMS
#define P_DANGER ga_P_DANGER
#define P_DANGER_T ga_P_DANGER_T
#define P_DANGER_R ga_P_DANGER_R
#define P_FRONT ga_P_FRONT
#define P_KITE ga_P_KITE
#define P_WALKHOME ga_P_WALKHOME
#define P_HITFIRST ga_P_HITFIRST
#define P_SAFESTEP ga_P_SAFESTEP
#define P_RETREAT ga_P_RETREAT
#define P_NOCHASE ga_P_NOCHASE
#define P_FRONT_LOCAL ga_P_FRONT_LOCAL
#define P_SHOOT ga_P_SHOOT
#define P_GANG ga_P_GANG
#define P_CALLHELP ga_P_CALLHELP
#define P_TWIN ga_P_TWIN
#define P_ALLYDUTY ga_P_ALLYDUTY
#define P_CARRY ga_P_CARRY
#define P_U34_ENGAGE_FALLBACK ga_P_U34_ENGAGE_FALLBACK
#define P_R_FLEE ga_P_R_FLEE
#define P_R_NEARRECALL ga_P_R_NEARRECALL
#define P_R_AVOIDLOW ga_P_R_AVOIDLOW
#define P_R_AVOID ga_P_R_AVOID
#define P_R_ENGAGE ga_P_R_ENGAGE
#define P_R_RECALLSHOP ga_P_R_RECALLSHOP
#define P_O_FLEE ga_P_O_FLEE
#define P_O_NEARRECALL ga_P_O_NEARRECALL
#define P_O_FM ga_P_O_FM
#define P_O_KITE ga_P_O_KITE
#define P_O_FRONT ga_P_O_FRONT
#define P_O_AVOIDLOW ga_P_O_AVOIDLOW
#define P_O_AVOID ga_P_O_AVOID
#define P_O_ENGAGE ga_P_O_ENGAGE
#define P_O_RECALLSHOP ga_P_O_RECALLSHOP
#define P_O_WALKHOME ga_P_O_WALKHOME
#define P_GP0_ON ga_P_GP0_ON
#define P_GP1_ON ga_P_GP1_ON
#define P_NN_ON ga_P_NN_ON
#define P_GOLD_W_EARLY ga_P_GOLD_W_EARLY
#define P_GOLD_W_LATE ga_P_GOLD_W_LATE
#define P_GA_GOLD_ROUND ga_P_GA_GOLD_ROUND
#define P_NOGOLD ga_P_NOGOLD
#define P_MAX_SHARE ga_P_MAX_SHARE
#define P_SHAREEXP ga_P_SHAREEXP
#define P_STACK_HP ga_P_STACK_HP
#define P_PAIR ga_P_PAIR
#define P_RESERVE_PCT ga_P_RESERVE_PCT
#define P_HALF ga_P_HALF
#define P_GA_HALF_D ga_P_GA_HALF_D
#define P_GA_DOOR ga_P_GA_DOOR
#define P_GA_DOOR_D ga_P_GA_DOOR_D
#define P_STICK ga_P_STICK
#define P_RESPAWN ga_P_RESPAWN
#define P_GA_NEEDCO ga_P_GA_NEEDCO
#define P_GA_SOLO ga_P_GA_SOLO
#define P_GA_CYCLE ga_P_GA_CYCLE
#define P_GA_OVERHEAD ga_P_GA_OVERHEAD
#define P_BANKW ga_P_BANKW
#define P_R34_BANKCOST ga_P_R34_BANKCOST
#define P_HOLD ga_P_HOLD
#define P_HOLD_R ga_P_HOLD_R
#define P_E_RETARGET ga_P_E_RETARGET
#define P_ONE_CAP ga_P_ONE_CAP
#define P_TRIBUTE_GEMS ga_P_TRIBUTE_GEMS
#define P_TRIBUTE_NEAR ga_P_TRIBUTE_NEAR
#define P_GA_NEAR_GEMS ga_P_GA_NEAR_GEMS
#define P_CHAIN ga_P_CHAIN
#define P_CHAIN_R ga_P_CHAIN_R
#define P_BAG ga_P_BAG
#define P_BAG_QUIET ga_P_BAG_QUIET
#define P_LATE_ROUND ga_P_LATE_ROUND
#define P_OWN_ALTAR ga_P_OWN_ALTAR
#define P_TELE ga_P_TELE
#define P_GA_TRIB_RC_GEMS ga_P_GA_TRIB_RC_GEMS
#define P_GA_TRIB_RC_D ga_P_GA_TRIB_RC_D
#define P_CAPRECALL ga_P_CAPRECALL
#define P_CAPRECALL_DELAY ga_P_CAPRECALL_DELAY
#define P_GA_CR_HEAL ga_P_GA_CR_HEAL
#define P_GA_CR_GOLD ga_P_GA_CR_GOLD
#define P_SHOP_GOLD ga_P_SHOP_GOLD
#define P_GA_SHOP_HP ga_P_GA_SHOP_HP
#define P_SHOP_RECALL ga_P_SHOP_RECALL
#define P_SHOP_PLAN ga_P_SHOP_PLAN
#define P_SHOPUNI ga_P_SHOPUNI
#define P_NE_POWER_OPEN ga_P_NE_POWER_OPEN
#define P_UNI_PATH ga_P_UNI_PATH
#define P_SAFE_RECALL ga_P_SAFE_RECALL
#define P_PATHD ga_P_PATHD
#define P_LEAN_RADIUS ga_P_LEAN_RADIUS
#define P_DRAFTUNI ga_P_DRAFTUNI
#define P_SWEEP ga_P_SWEEP
#define P_AOE ga_P_AOE
#define P_U34_RESET_LIVE ga_P_U34_RESET_LIVE
#define P_MONO ga_P_MONO
#define P_UNSTICK ga_P_UNSTICK
#define P_GA_SS_ALLY ga_P_GA_SS_ALLY
#define P_GA_SS_HOME ga_P_GA_SS_HOME
#define P_PAIR_N ga_P_PAIR_N
#define P_PAIR_FOE ga_P_PAIR_FOE
#define P_PAIR_STICK ga_P_PAIR_STICK
#define P_PAIR_ENGAGE ga_P_PAIR_ENGAGE
#define P_PAIR_LOWHP ga_P_PAIR_LOWHP
#define P_IM_PAIRED ga_P_IM_PAIRED
#define P_IM_PAIR_R ga_P_IM_PAIR_R
#define P_UNI_FLEE_P ga_P_UNI_FLEE_P
#define P_LOWHP_P ga_P_LOWHP_P
#define P_GA_AVOID_HP_P ga_P_GA_AVOID_HP_P
#define P_AVOID_DIST_P ga_P_AVOID_DIST_P
#define GA_GP0 ((const volatile int*)(ga_s + 130))
#define GA_GP1 ((const volatile int*)(ga_s + 178))
#define GA_NN ((const volatile int*)(ga_s + 226))

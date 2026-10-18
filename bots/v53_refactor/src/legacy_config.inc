// ---------------------------------------------------------------------------
// Tunables. The draft bot writes these into draft memory; champions read them.
// ---------------------------------------------------------------------------
// Local tuning: an optional params.h next to main.cpp overrides the P_* macros
// (used by the arena to compile parameter variants; the uploaded bot has none).
#if __has_include("params.h")
#include "params.h"
#endif
#ifndef P_TRIBUTE_GEMS
#define P_TRIBUTE_GEMS 20
#endif
#ifndef P_TRIBUTE_NEAR
#define P_TRIBUTE_NEAR 8      // bank 10+ gems when an altar is this close
#endif
#ifndef P_SHOP_GOLD
#define P_SHOP_GOLD 300       // recall to shop (when below half health) from this much gold
#endif
#ifndef P_LEAN_CAMPS
#define P_LEAN_CAMPS 1
#endif
#ifndef P_LEAN_RADIUS
#define P_LEAN_RADIUS 12
#endif
#ifndef P_ENGAGE2
#define P_ENGAGE2 0
#endif
#ifndef P_LOWHP
#define P_LOWHP 0
#endif
#ifndef P_ALLYDUTY
#define P_ALLYDUTY 0
#endif
#ifndef P_NODASHIN
#define P_NODASHIN 0
#endif
#ifndef P_CARRY
#define P_CARRY 0
#endif
#ifndef P_UNSTICK
#define P_UNSTICK 0
#endif
#ifndef P_PAIR
#define P_PAIR 0
#endif
#ifndef P_NOGOLD
#define P_NOGOLD 0
#endif
#ifndef P_MONO
#define P_MONO 1  // maps whose only gems are monoliths (contest): farm gold, then the whole team on the monolith
#endif
#ifndef P_STEPOFF
#define P_STEPOFF 0
#endif
#ifndef P_POT
#define P_POT 0
#endif
#ifndef P_CHAIN_R
#define P_CHAIN_R 8
#endif
#ifndef P_CASSI_HP
#define P_CASSI_HP 0
#endif
#ifndef P_PACKOPEN
#define P_PACKOPEN 0
#endif
#ifndef P_ALTAR_SAFE
#define P_ALTAR_SAFE 0
#endif
#ifndef P_DBGT_ALL
#define P_DBGT_ALL 0
#endif
#ifndef P_FRONT
#define P_FRONT 0
#endif
#ifndef P_FRONT_ZONE
#define P_FRONT_ZONE 3      // a foe this close means we are in the fight
#endif
#ifndef P_FRONT_OUT
#define P_FRONT_OUT 160     // their hp above this % of ours near the fight: not our fight
#endif
#ifndef P_SAVECC
#define P_SAVECC 0
#endif
// P_SWEEP 1: at the end of every turn, a ready damage/stun spell goes on an enemy champion within spell range
// (online vs the top 4 our casters had a spell ready in 52-70% of the rounds an enemy stood within 4; theirs 17-22%).
// 2 = the same, only in a fight. Tavi's, Ryth's and Cassi's spells cannot be cast after a step (engine error 126),
// so 1/2 rarely fire: 3 = cast before the turn's move, always; 4 = before the move, only when we were hit in the
// last 3 rounds, a foe can reach us, or the foe is hurt / channeling; 5 = before the move, but a spell that roots
// us for the round (exclusive_with_movement) only when standing is safe, then shoot; the rest again after the move.
#ifndef P_SWEEP
#define P_SWEEP 0
#endif
// P_CASTSAFE N (2026-10-15 fix list): before the turn's move, a spell that roots us for the round
// (exclusive_with_movement) is not cast when this turn should escape: we are below the flee threshold (the turn
// will run or recall), or the enemy's ready damage on our tile next round reaches N% of our health and a
// neighbouring tile is clearly safer. A cast that kills its target is still made.
#ifndef P_CASTSAFE
#define P_CASTSAFE 0
#endif
// P_AOE 1: ground area spells (Stellar's 1.4 x focus, radius 1) aim at the tile that covers the intended target
// and the most other enemy champions; 2: also cast the area spell before a single-target damage spell when it
// covers 2+ enemy champions (1.4 x 2 > 2.0).
#ifndef P_AOE
#define P_AOE 0
#endif
// P_GROUP T: "pelea en grupo" (user, 2026-10-14 09:48). For T rounds after we (or an ally, via the danger byte)
// saw an enemy pack (P_DANGER+ champions within 4), the team farms and moves as one ball like P_BALL with weight
// P_GROUP_W, so the pack meets all of us together. Needs P_DANGER. Nothing here depends on the map.
#ifndef P_GROUP
#define P_GROUP 0
#endif
// P_FM 1: complete fight mode (user's choice 2026-10-14 10:12, "Rehacer la pelea"), fight.h fight_mode().
// With an enemy champion within P_FM_R it replaces the old fight rules: weigh the local fight, engage or
// retreat with hysteresis (P_FM_ENTER / P_FM_STAY, % of their hp x dps), one focus for all of us, ranged
// stand and cast when no melee can dive them, melee peel and hit the focus, retreat towards allies.
#ifndef P_FM
#define P_FM 0
#endif
#ifndef P_FM_R
#define P_FM_R 6
#endif
#ifndef P_FM_ENTER
#define P_FM_ENTER 110
#endif
#ifndef P_FM_STAY
#define P_FM_STAY 75
#endif
#ifndef P_FM_LOWHP
#define P_FM_LOWHP 35
#endif
// P_FM 2: volley model (fight.h threat_of / danger_at). P_FM_VOL = % of our hp a tile's ready enemy
// damage must reach to count as lethal; P_FM_VR 1 trades the ready volleys before the force ratio;
// P_FM_HOLD = rounds a ranged champion waits outside their range before going back to the old rules.
#ifndef P_FM_VOL
#define P_FM_VOL 70
#endif
// P_VOLLEY N: volley-aware movement in every non-fight mode (farm, tribute, avoid, flee, shop...): a tile
// where the enemy's ready damage next round (danger_at) reaches N% of our health is a wall for pathing,
// and standing on one we first step to the neighbour with the least ready damage. 0 = off.
#ifndef P_VOLLEY
#define P_VOLLEY 0
#endif
// P_CAPRECALL 1: when a recall is wanted and our target's reward is waiting, step on the capture tiles first
// and start the recall there (after P_CAPRECALL_DELAY turns on the tiles; capture and recall both take 5).
#ifndef P_CAPRECALL
#define P_CAPRECALL 0
#endif
// Keep a safely claimable camp reward before a normal/nearby heal or shop recall.
// Enabled in params.h for an isolated A/B test; off reproduces prior behavior.
#ifndef P_CAPTURE_RECALL_FIX
#define P_CAPTURE_RECALL_FIX 0
#endif
// P_PATHD 1: camp choice uses walking distances (distance fields) instead of straight-line distance;
// P_BANKW %: add the bag's round trip to the nearest altar, shared by the squad, to a camp's cost.
#ifndef P_PATHD
#define P_PATHD 0
#endif
#ifndef P_SHOPFIX
#define P_SHOPFIX 0           // 1: finish the shop list on later turns when init ran out of fuel; no shop trips that cannot buy
#endif
#ifndef P_TELE
#define P_TELE 0              // >0: recall instead of walking to an altar when recall + spawn->altar walk is shorter by this margin
#endif
#ifndef P_BANKW
#define P_BANKW 0
#endif
#ifndef P_CAPRECALL_DELAY
#define P_CAPRECALL_DELAY 1
#endif
#ifndef P_VOLLEY_R  // how far around us the lethal tiles are marked for pathing
#define P_VOLLEY_R 1
#endif
#ifndef P_FM_VR
#define P_FM_VR 1
#endif
#ifndef P_FM_HOLD
#define P_FM_HOLD 8
#endif
#ifndef P_FM_RET  // P_FM 2 retreat: step by the volley map instead of safe_step
#define P_FM_RET 1
#endif
#ifndef P_GROUP_W
#define P_GROUP_W 5
#endif
#ifndef P_GROUP_R
#define P_GROUP_R 0   // > 0: in group mode followers walk back to within this of the leader, and the leader waits
#endif                // while a follower within 15 is farther than 2x this
#ifndef P_SW5_OUT
#define P_SW5_OUT 1   // P_SWEEP 5: stand and cast only with foes within 5 <= allies within 4 (me included) + this
#endif
#ifndef P_SW5_ALLY
#define P_SW5_ALLY 1  // P_SWEEP 5: and at least this many of us within 4 (me included)
#endif
#ifndef P_FRONT_CAST
#define P_FRONT_CAST 0
#endif
// P_HOLD N: hold the contested centre (top-10 caster teams camp the centre altar on corners, collision and
// interlock and kill whoever comes to bank there). The hold point is a reachable altar about as far from both
// spawns with 2+ gem camp groups within P_HOLD_R. Camps there score x N/100 and ignore danger spots, and the
// altar ignores danger when we bank.
#ifndef P_HOLD
#define P_HOLD 0
#endif
#ifndef P_HOLD_R
#define P_HOLD_R 6
#endif
// P_BALL W: the team moves as one ball like VeryGood: the first living ally in draft order leads and
// farms as usual; the others take the leader's claimed camp (score x W, no share cap) and avoid camps more
// than 8 tiles from the leader.
#ifndef P_BALL
#define P_BALL 0
#endif
// P_CASTGATE 1: P_KITE, P_BALL and P_HOLD only run when our team has 3+ ranged champions (the caster ball);
// with P_DRAFTMAP 2 that is corners, collision, interlock and packs.
// P_NOCHASE 1 (the user, 2026-10-14 08:42: "we chase forever; a fight is over when they retreat or die,
// then go back to farming"): a foe that moved away from us since last round and is out of our attack range
// is not a target unless it carries P_CHASE_GEMS+ gems; nobody steps toward it.
#ifndef P_NOCHASE
#define P_NOCHASE 0
#endif
#ifndef P_CASTGATE
#define P_CASTGATE 0
#endif
#ifndef P_DRAFTCAST
#define P_DRAFTCAST 0
#endif
#ifndef P_DRAFTMAP
#define P_DRAFTMAP 0
#endif
// P_DRAFTUNI: the #1 team's (Univardisty, 2026-10-14) fight drafts by team size: 3 = Cassi&Issac, Ren, Stellar;
// 4 = + Tavi; 5 = Ryth, Stellar, Prism, Ren, Tavi. 1 = always; 2 = only when the spawn-to-spawn path is at most
// P_UNI_PATH (known fight maps 26-41, farm maps 49-85). P_SHOPUNI: Ren, Prism and Stellar buy power-f + durability-h.
// P_RECALL_NEAR N: recall (hurt or shopping) with the nearest foe N+ tiles away when we were not hit since our last
// turn; damage interrupts a recall, so the #1 recalls at 4-6 tiles out of a fight and 87% of its recalls finish.
#ifndef P_DRAFTUNI
#define P_DRAFTUNI 0
#endif
#ifndef P_SQUISHY
#define P_SQUISHY 0
#endif
#ifndef P_DRAFTDIVE
#define P_DRAFTDIVE 0
#endif
// P_DRAFT5 1: with 5 champions the caster draft is Cassi&Issac, Stellar, Varg, Tavi, Ren (what the top 10 won with on
// the 2026-10-16 maps), instead of Ryth, Stellar, Prism, Ren, Tavi.
// P_JACKPOT R: a group holding half the map's gems or more that is about as far from both spawns (stampede's centre)
// is left alone before round R, and gold clusters are farmed even with P_NOGOLD: the top teams buy ~9000 gold of
// items first and take it by force from r350-475; we walked in at r50 and died 27 times a game.
#ifndef P_JACKPOT
#define P_JACKPOT 0
#endif
#ifndef P_DRAFT5
#define P_DRAFT5 0
#endif
// P_JACKGO R: from round R the jackpot (P_JACKPOT) is a whole-team job, like P_MONO's monolith: P_JACKN champions
// commit to it (no "too strong" bail), wait at it while it respawns, and value it P_JACKW times. Online at 13:50 the
// top teams took it at r305-650 with 2-6 champions while we had 0-1 there (stampede 0-10).
#ifndef P_JACKGO
#define P_JACKGO 0
#endif
#ifndef P_JACKN
#define P_JACKN 5
#endif
#ifndef P_JACKW
#define P_JACKW 10
#endif
#ifndef P_UNI_PATH
#define P_UNI_PATH 45
#endif
#ifndef P_SHOPUNI
#define P_SHOPUNI 0
#endif
#ifndef P_RECALL_NEAR
#define P_RECALL_NEAR 0
#endif
#ifndef P_UNI_STAND
#define P_UNI_STAND 0
#endif
#ifndef P_UNI_STAND_HP
#define P_UNI_STAND_HP 40
#endif
#ifndef P_UNI_RENKITE
#define P_UNI_RENKITE 0
#endif
#ifndef P_UNI_FLEE
#define P_UNI_FLEE 0
#endif
#ifndef P_UNI_RN
#define P_UNI_RN 0
#endif
#ifndef P_FRONT_LOCAL
#define P_FRONT_LOCAL 0
#endif
#ifndef P_CHASE_GEMS
#define P_CHASE_GEMS 150
#endif
#ifndef P_BAG
#define P_BAG 0
#endif
#ifndef P_BAG_QUIET
#define P_BAG_QUIET 40
#endif
#ifndef P_CAPCLAIM
#define P_CAPCLAIM 1
#endif
#ifndef P_GANG
#define P_GANG 0
#endif
// P_DANGER N: N+ enemy champions within 4 of each other mark a danger spot for P_DANGER_T rounds;
// camps within P_DANGER_R of it are skipped and altars near it cost 60 extra tiles (corners: a
// team camping the centre). Shared through byte 7 as the nearest altar when P_CALLHELP is off.
#ifndef P_DANGER
#define P_DANGER 0
#endif
#ifndef P_CALLHELP
#define P_CALLHELP 0
#endif
#ifndef P_DANGER_T
#define P_DANGER_T 40
#endif
#ifndef P_DANGER_R
#define P_DANGER_R 6
#endif
#ifndef P_SHOOT
#define P_SHOOT 0
#endif
#ifndef P_CASSI_PCT
#define P_CASSI_PCT 0
#endif
#ifndef P_ALTAR_REACH
#define P_ALTAR_REACH 0
#endif
#ifndef P_UNJAM
#define P_UNJAM 0
#endif
#ifndef P_WALKHOME
#define P_WALKHOME 0
#endif
#ifndef P_CAPDPS
#define P_CAPDPS 0
#endif
#ifndef P_ONE_CAP
#define P_ONE_CAP 0
#endif
#ifndef P_SHOP_PLAN
#define P_SHOP_PLAN 0
#endif
#ifndef P_SHOP_RECALL
#define P_SHOP_RECALL 0
#endif
#ifndef P_SAFE_RECALL
#define P_SAFE_RECALL 0
#endif
#ifndef P_OWN_ALTAR
#define P_OWN_ALTAR 0
#endif
#ifndef P_STICK
#define P_STICK 125           // score bonus in % for the current target (hysteresis)
#endif
#ifndef P_DBGT_LEN
#define P_DBGT_LEN 60
#endif
#ifndef P_RESPAWN
#define P_RESPAWN 0
#endif
#ifndef P_CHAIN
#define P_CHAIN 0
#endif
#ifndef P_HALF
#define P_HALF 0
#endif
#ifndef P_MAX_SHARE
#define P_MAX_SHARE 2         // champions allowed on one monster group
#endif
#ifndef P_STACK_HP
#define P_STACK_HP 0          // camps with at least this much hp use P_SHAREEXP (big camps: stack, small: spread)
#endif
#ifndef P_SHAREEXP
#define P_SHAREEXP 100        // a joiner values a big camp at gems / team^(P_SHAREEXP/100); 100 = even split
#endif
#ifndef P_GOLD_W_EARLY
#define P_GOLD_W_EARLY 35     // gold weight in % of a gem before round 600
#endif
#ifndef P_GOLD_W_LATE
#define P_GOLD_W_LATE 12
#endif
#ifndef P_RESERVE_PCT
#define P_RESERVE_PCT 20      // never start a camp that would leave less than this % health
#endif
#ifndef P_RETREAT
#define P_RETREAT 0           // 1: step away from enemies when avoiding; 0: head for spawn
#endif
#ifndef P_AVOID_DIST
#define P_AVOID_DIST 5        // back away from a stronger enemy group this close
#endif
#ifndef P_BAIL_PCT
#define P_BAIL_PCT 18         // abandon a camp fight below this % health
#endif
#ifndef P_RECALL_PCT
#define P_RECALL_PCT 40
#endif
#ifndef P_FLEE_PCT
#define P_FLEE_PCT 25
#endif
#ifndef P_LATE_ROUND
#define P_LATE_ROUND 1850
#endif
#ifndef STATUS_EVERY
#define STATUS_EVERY 25
#endif

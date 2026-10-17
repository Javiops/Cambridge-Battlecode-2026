// CAMBC (cambc2026a) bot - single-file C++ bot using only the documented SDK API.
//
// Strategy in one paragraph:
//   Draft tanky melee farmers first (Varg, Ryth, Vendetta), then Vesper Vale /
//   Marcella / Cassi & Issac and so on, by name, writing the plan into draft
//   memory before every pick. In game, every champion runs the same priority list:
//   shop on spawn (emblem build per champion), heal on spawn, flee or recall
//   when hurt, fight enemy champions only when the local fight looks even or
//   better, tribute at the nearest altar when the bag is big (or late in the
//   game), otherwise farm the best camp group it can clear safely (gem/gold
//   clusters first, then wolves, elk...), capture it and move on. Allies spread
//   over different camps through an 8-byte "claim" table in shared memory.
//
// NOTE: this was written from the API reference only and could not be compiled
// against the real SDK. Names the reference does not spell out (header name,
// enum values) are avoided: champions, items and passives are found by
// iterating enum values and matching to_string() names.

// The SDK header name is not in the API reference, so try the likely ones.
// If none match, replace this block with the #include from a `cambc new` template.
#if defined(CAMBC_LOCAL_STUB)
#include "cambc_stub.hpp"  // offline syntax check only
#elif __has_include(<cambc.hpp>)
#include <cambc.hpp>
#elif __has_include(<cambc/cambc.hpp>)
#include <cambc/cambc.hpp>
#elif __has_include(<cambc.h>)
#include <cambc.h>
#elif __has_include(<cambc/cambc.h>)
#include <cambc/cambc.h>
#elif __has_include(<cambc/sdk.hpp>)
#include <cambc/sdk.hpp>
#elif __has_include(<cambc/bot.hpp>)
#include <cambc/bot.hpp>
#elif __has_include(<cambc/all.hpp>)
#include <cambc/all.hpp>
#elif __has_include(<cambc/api.hpp>)
#include <cambc/api.hpp>
#elif __has_include(<cambc_sdk.hpp>)
#include <cambc_sdk.hpp>
#elif __has_include(<cambc/cambc.hh>)
#include <cambc/cambc.hh>
#elif __has_include(<sdk.hpp>)
#include <sdk.hpp>
#elif __has_include(<bot.hpp>)
#include <bot.hpp>
#elif __has_include(<bc.hpp>)
#include <bc.hpp>
#elif __has_include(<battlecode.hpp>)
#include <battlecode.hpp>
#else
#error "CAMBC SDK header not found: copy the #include line from a `cambc new` template here"
#endif

#include <algorithm>
#include <cmath>
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <vector>
#include <variant>
#include <cstdio>
#include <exception>
#include "channel_safety.h"

namespace bc = cambc;
using bc::vec2;

namespace {

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
#ifndef P_DP_CHANNEL_FIX
#define P_DP_CHANNEL_FIX 1
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
#ifndef P_PVCOMMIT
#define P_PVCOMMIT 0  // >0 (tiles): with P_PV 2, a "fight" verdict sends us at the weakest foe within this many tiles
#endif
#ifndef P_PVKITE
#define P_PVKITE 0  // fight.h: kite and call for help on a leave verdict
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
struct Params {
    int tribute_gems = P_TRIBUTE_GEMS;   // walk to an altar once carrying this many gems
    int recall_pct = P_RECALL_PCT;       // recall below this % health when safe
    int flee_pct = P_FLEE_PCT;           // run for spawn below this % health
    int late_round = P_LATE_ROUND;       // after this round, tribute any gems at all
};
Params P;

constexpr std::uint64_t FUEL_RESERVE = 6000;
constexpr int SPELL_RANGE = 4;   // every targeted/ground spell in the roster is range 4
constexpr int CAMP_RANGE = 3;    // all monsters attack at range 3
constexpr int MAX_GROUPS = 250;  // claim bytes store group index + 1

inline int X(vec2 v) { return static_cast<int>(v.dot(vec2(1, 0))); }
inline int Y(vec2 v) { return static_cast<int>(v.dot(vec2(0, 1))); }
inline int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }
inline bool fuel_ok(std::uint64_t need) { return bc::fuel_remaining() > need + FUEL_RESERVE; }

// Every SDK action can throw (cambc::error, out_of_range, ...). An uncaught
// exception restarts the C++ guest and loses all state, so wrap everything.
// Diagnostics go to stdout, which the runner saves as team-x.stdout.
int g_errors = 0;
const char* g_mode = "start";
const char* g_farm = "-";
// P_TRACE: one line per turn for behaviour studies (trace builds only; off in every bot we upload).
#ifndef P_TRACE
#define P_TRACE 0
#endif
int g_nf = 99, g_nfoes = 0, g_nal = 0, g_rew = 0, g_tlive = -1;

// 2026-10-16 behaviour fixes (thread "fix teammate behaviours"). Each is a switch; 0 = the teammate's bot as sent.
// P_CAPHOME N: a reward of our camp is waiting within N steps and we want to go home (hurt / asked to heal):
//   step onto it and recall there, so the 5-round capture and the recall run together, instead of recalling or
//   walking away and leaving the loot (also: no tribute walk while that reward waits for us).
#ifndef P_CAPHOME
#define P_CAPHOME 0
#endif
#ifndef P_CAPHOME_RSAFE   // 1: only when a recall would start anyway (nobody near enough to interrupt it)
#define P_CAPHOME_RSAFE 0
#endif
#ifndef P_CAPHOME_TRIB    // 1: no tribute walk while our reward waits within 2; 2: only that part (no cap-home recall)
#define P_CAPHOME_TRIB 1
#endif
// P_CAMPFOE N: an enemy champion within 3 (or within N after it hit us in the last 2 rounds) means a fight: hit
//   it if the fight is favourable and it is in reach, else back off; never spend the turn on a camp.
#ifndef P_CAMPFOE
#define P_CAMPFOE 0
#endif
// P_NOCHASE2 1: a low-health or channelling foe is only engaged within attack range + 1 (no walking after it),
//   unless it carries P_CHASE_GEMS+ gems (the user's doctrine: chase only a big bag).
#ifndef P_NOCHASE2
#define P_NOCHASE2 0
#endif
// P_NEEDHEAL R: waiting for a squad (rally) or for health that no recall will bring (need-heal with 80%+ health or
//   no safe recall) lasts at most R rounds: the camp is dropped for a while and another one is chosen.
#ifndef P_NEEDHEAL
#define P_NEEDHEAL 0
#endif
// P_KITEALLY R: kiting steps toward the nearest ally within R tiles (60 a tile past 2), not only toward allies
//   already within 6.
#ifndef P_KITEALLY
#define P_KITEALLY 0
#endif
// P_BACKHOME M: right after a tribute at a contested altar (distances to both spawns within M), recall home if
//   there is no camp to take or the next camp is contested too and (we saw a foe in the last 20 rounds or are
//   below 80% health); walk home if a recall is not safe.
#ifndef P_BACKHOME
#define P_BACKHOME 0
#endif
// P_CAPPRIO R: who stays on a reward (the gold and gems go to whoever stands on it): Stellar first (if she claims it
//   within R tiles or stands next to it), then the other casters, then Ren, the tanks last; ties by distance, then
//   roster index. A lower-priority champion keeps the capture going until the higher one is on the tiles, then steps off.
#ifndef P_CAPPRIO
#define P_CAPPRIO 0
#endif
// P_TWINFARM R: Issac farms Cassi's camp (they share one life; online-like local games: 33 of 82 pair deaths came
//   with Issac alone 9+ tiles from Cassi). With no camp claimed by Cassi he walks back to within R of her.
// P_NOLEAVE N (the user, 2026-10-16 17:17): a reward of our camp waiting within N tiles is never left behind, except
//   when staying kills us (the foes' ready damage on our tile, three rounds of it, reaches our health, or we are under
//   15%) or an ally with more right to the gold takes it (P_ONE_CAP / P_CAPPRIO). We step on, shoot whoever is in
//   range without moving, and recall on the tiles when we wanted to go home (capture and recall together).
#ifndef P_NOLEAVE
#define P_NOLEAVE 0
#endif
// P_CACHE 1 (with P_NOLEAVE): a tank that sees a waiting reward posts it in shared bytes 5-6 (group + 1, then 251 +
//   (round / 16) & 3) instead of taking it; casters and Ren read it as a free reward for 32 rounds and go for it.
#ifndef P_CACHE
#define P_CACHE 0
#endif
// P_OUTNUM R (the user, 2026-10-16 17:20: corners, Tavi 4 tiles from 3 foes with her allies far away walks toward
//   them and dies): outnumbered by 2+ within R (allies that are recalling do not count), we back off instead of
//   kiting, farming or walking on, unless the foe in reach dies to our next hit.
#ifndef P_OUTNUM
#define P_OUTNUM 0
#endif
// P_DPSFARM 1 (the user, 2026-10-16 17:56: "farming is meant for the DPS to collect and nobody else"): only the DPS
//   (casters and Ren) capture camps. A tank never chooses its own camp while a DPS has one claimed: it goes to the
//   DPS's camp nearest to it (Issac to Cassi's), helps kill it and steps off the reward; a reward a tank is left
//   with is posted in the cache (P_CACHE bytes) for the DPS. DPS do not count tank claims when choosing.
#ifndef P_DPSFARM
#define P_DPSFARM 0
#endif
#ifndef P_TWINFARM
#define P_TWINFARM 0
#endif
// P_AVOIDFIRST 1 (GA genome b672ef97f6, the user 18:11 idea 6): decide to back off before taking the front line.
#ifndef P_AVOIDFIRST
#define P_AVOIDFIRST 0
#endif
#include "profile.h"

void note_error(const char* what) {
    ++g_errors;
    if (g_errors <= 8 || g_errors % 500 == 0) {
        std::printf("[err #%d] %s\n", g_errors, what);
        std::fflush(stdout);
    }
}

template <class F>
bool attempt(F&& f) {
    try {
        return f();
    } catch (const std::exception& e) {
        note_error(e.what());
        return false;
    } catch (...) {
        note_error("unknown exception");
        return false;
    }
}

// P_FUELPROF: fuel used per section of the turn, and which section was running when a turn ran out of fuel (the
// bot is then suspended and resumes in the next round, so the round number changes between two marks).
// Profiling builds only: printed from debug_block, so run them without --release.
#ifndef P_FUELPROF
#define P_FUELPROF 0
#endif
// P_FUELGUARD 1: stop turns running out of fuel. A turn that runs out is suspended and the rest of it plays in the
// champion's next turn, on last round's data, so a champion loses one or two rounds each time (online: ~10 a game,
// 60+ on lanes). With unlimited fuel the decisions are the same as without it (154 of 154 map sides identical):
//  - cheaper, same result: one search instead of one per altar at start-up; walking distances to the camp groups
//    kept while we stand still (capturing); allies out of vision skipped before position() throws in
//    other_captures; the reward-evacuation check reads the camps near us instead of every visible camp;
//  - when the turn cannot pay for it: start-up finishes over the first turns (the champion waits on its spawn), an
//    optional camp re-choice waits for a later turn, log lines are skipped, and the low-fuel fallback step is a
//    plain greedy step instead of one more path search.
#ifndef P_FUELGUARD
#define P_FUELGUARD 0
#endif
#if P_FUELPROF
struct FuelSec { const char* name = "?"; unsigned long long sum = 0, n = 0, mx = 0, over = 0; };
FuelSec g_fp[32];
int g_fp_sec = 0, g_fp_round = -1;
unsigned long long g_fp_last = 0;
bool g_fp_over = false;
unsigned long long g_fp_turn[32];
int g_fp_where = -1;
void fp_mark(int next, const char* name) {
    int r = static_cast<int>(bc::round_number());
    unsigned long long f = bc::fuel_remaining();
    FuelSec& c = g_fp[g_fp_sec];
    if (!g_fp_over && r != g_fp_round) { ++c.over; g_fp_over = true; g_fp_where = g_fp_sec; }
    if (!g_fp_over && g_fp_last >= f) { c.sum += g_fp_last - f; ++c.n; c.mx = std::max(c.mx, g_fp_last - f); g_fp_turn[g_fp_sec] += g_fp_last - f; }
    g_fp_sec = next; g_fp[next].name = name; g_fp_last = f;
}
void fp_begin() {
    g_fp_round = static_cast<int>(bc::round_number()); g_fp_over = false; g_fp_where = -1;
    for (auto& t : g_fp_turn) t = 0;
    g_fp_sec = 0; g_fp[0].name = "pre-sweep"; g_fp_last = bc::fuel_remaining();
}
#define FP(i, name) fp_mark(i, name)
struct FpScope {  // a function's own section; the caller's section resumes when it returns
    int prev; const char* pname;
    FpScope(int i, const char* name) : prev(g_fp_sec), pname(g_fp[g_fp_sec].name) { fp_mark(i, name); }
    ~FpScope() { fp_mark(prev, pname); }
};
#define FP_SCOPE(i, name) FpScope fp_scope_{i, name}
#else
#define FP(i, name) ((void)0)
#define FP_SCOPE(i, name) ((void)0)
#endif

std::string norm(const std::string& s) {
    std::string o;
    for (char c : s) {
        if (c >= 'A' && c <= 'Z') o += static_cast<char>(c - 'A' + 'a');
        else if (c >= 'a' && c <= 'z') o += c;
    }
    return o;
}

bool starts_with(const std::string& s, const std::string& p) { return s.rfind(p, 0) == 0; }

#include "de_rules.h"
int g_de_map = 0;  // Public geometry family, transported in draft-memory byte28.
#include "draft_plan.h"

// Base monster stats from the rules (health, strength).
void monster_stats(const bc::camp& c, double& hp, double& str) {
    if (c.is_wolf()) { hp = 1350; str = 20; }
    else if (c.is_elk()) { hp = 2400; str = 60; }
    else if (c.is_monolith()) { hp = 20000; str = 200; }
    else { hp = 500; str = 0; }  // gem / gold cluster
}

// ---------------------------------------------------------------------------
// Draft
// ---------------------------------------------------------------------------
const char* const PREFS[] = {"vendetta", "varg",  "cassi",   "ryth",  "tavi",  "vesper",
                             "marcella", "ren",   "stellar", "prism", "willow"};

void write_plan(const std::vector<std::uint8_t>& roster) {
    std::array<std::byte, draftplan::SIZE> buf{};
    buf[0] = std::byte{'C'};
    buf[1] = std::byte{'M'};
    buf[2] = std::byte{'B'};
    buf[3] = std::byte{'1'};
    std::size_t n = std::min<std::size_t>(roster.size(), 16);
    buf[4] = static_cast<std::byte>(n);
    for (std::size_t i = 0; i < n; ++i) buf[5 + i] = static_cast<std::byte>(roster[i]);
    if (P_D34_FAMILY) buf[28] = static_cast<std::byte>(g_de_map);
    buf[24] = static_cast<std::byte>(P.tribute_gems);
    buf[25] = static_cast<std::byte>(P.recall_pct);
    buf[26] = static_cast<std::byte>(P.flee_pct);
    buf[27] = static_cast<std::byte>(P.late_round / 10);
    draftplan::copy_to(buf);
#if P_DP_MEMORY_FIX
    draftplan::submit_plan(buf);
#else
    attempt([&] {
        bc::draft_memory_buffer dm;
        dm = std::span<const std::byte>(buf.data(), buf.size());
        return true;
    });
#endif
}

#include "mapplan.h"

[[noreturn]] void run_draft() {
    struct Opt {
        std::string name;
        bc::champion_draft value;
        std::uint8_t raw;
    };
    std::vector<Opt> all;
    for (std::uint32_t i = 0; i < 48; ++i) {
        attempt([&] {
            auto c = static_cast<bc::champion_draft>(i);
            std::string n = norm(bc::to_string(c));
            if (n.empty() || n == "none" || n == "unknown" || n == "count") return false;
            for (auto& o : all)
                if (o.name == n) return false;
            all.push_back({n, c, static_cast<std::uint8_t>(i)});
            return true;
        });
    }

    std::vector<Opt> order;
    auto has = [&](const std::string& n) {
        for (auto& o : order)
            if (o.name == n) return true;
        return false;
    };
    // P_DRAFTMAP: on the fight maps (corners, interlock, elkring, packs, collision) draft the caster team
    // the two best top-10 teams use there; the map is told apart by team size, altars and walls,
    // which the draft can read (camp groups throw during the draft).
#ifdef P_MAPFEAT
    attempt([&] {  // draft-time map features: size, team size, walls, altars, spawn-to-spawn path length
        int W = bc::map::width(), H = bc::map::height();
        int ts = static_cast<int>(bc::draft::team_size());
        bc::bitboard block = bc::map::walls() | bc::map::holes() | bc::map::altars();
        const bc::bitboard& ra = bc::map::spawn_region(bc::team::ally);
        const bc::bitboard& rb = bc::map::spawn_region(bc::team::enemy);
        bc::distance_field da, db;
        bc::bitboard va, vb;
        da.compute(block, ra, va);
        db.compute(block, rb, vb);
        int ab = 1 << 30;
        for (auto p : rb.positions()) if (va.is_set(p)) ab = std::min(ab, static_cast<int>(da.get(p)));
        int open = static_cast<int>(va.positions().size());
        auto alts = bc::map::altars().positions();
        int mid = 0, near_mid = 1 << 30;
        for (auto a : alts) {
            int ma = 1 << 30, mb = 1 << 30;
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    vec2 t = a + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t)) continue;
                    if (va.is_set(t)) ma = std::min(ma, static_cast<int>(da.get(t)));
                    if (vb.is_set(t)) mb = std::min(mb, static_cast<int>(db.get(t)));
                }
            if (ma < (1 << 30) && mb < (1 << 30) && std::abs(ma - mb) <= 4) { ++mid; near_mid = std::min(near_mid, ma); }
        }
        std::printf("[mapfeat] W=%d H=%d ts=%d walls=%zu altars=%zu spawn_path=%d open=%d mid_altars=%d mid_dist=%d\n", W, H, ts,
                    bc::map::walls().positions().size(), alts.size(), ab, open, mid, near_mid == (1 << 30) ? -1 : near_mid);
        std::fflush(stdout);
        return true;
    });
#endif
    draftplan::prepare();
    std::vector<const char*> prefs(std::begin(PREFS), std::end(PREFS));
    if (P_DRAFTCAST) {  // the sparring caster team: VeryGood's draft on every map
        prefs = {"stellar", "tavi", "cassi", "willow", "prism"};
        for (const char* p : PREFS) prefs.push_back(p);
    } else if (P_DRAFTDIVE) {  // sparring melee team: Shawn's draft (beat v27 online 226-1022 on interlock)
        prefs = {"varg", "ryth", "vendetta", "ren", "marcella"};
        for (const char* p : PREFS) prefs.push_back(p);
    } else if (P_DRAFTMAP == 2) {  // VeryGood's caster ball on corners, collision, interlock and packs
        int ts = 0;
        std::size_t alt = 0, walls = 0;
        attempt([&] { ts = static_cast<int>(bc::draft::team_size()); return true; });
        attempt([&] { alt = bc::map::altars().positions().size(); return true; });
        attempt([&] { walls = bc::map::walls().positions().size(); return true; });
        bool ball_map = (ts == 5 && alt == 5 && walls == 44) ||   // corners
                        (ts == 4 && alt == 4 && walls == 76) ||   // interlock
                        (ts == 3 && alt == 6 && walls == 0) ||    // packs
                        (ts == 3 && alt == 2 && walls == 84);     // collision
        std::printf("[draft] map ts=%d altars=%zu walls=%zu ball=%d\n", ts, alt, walls, ball_map ? 1 : 0);
        if (ball_map) {
            prefs = {"stellar", "tavi", "cassi", "willow", "prism"};
            for (const char* p : PREFS) prefs.push_back(p);
        }
    } else if (P_DRAFTMAP) {
        int ts = 0;
        std::size_t alt = 0, walls = 0;
        attempt([&] { ts = static_cast<int>(bc::draft::team_size()); return true; });
        attempt([&] { alt = bc::map::altars().positions().size(); return true; });
        attempt([&] { walls = bc::map::walls().positions().size(); return true; });
        bool fight_map = (ts == 5 && alt == 5 && walls == 44) ||   // corners
                         (ts == 4 && alt == 4 && walls == 76) ||   // interlock
                         (ts == 5 && alt == 2 && walls == 0) ||    // elkring
                         (ts == 3 && alt == 6 && walls == 0) ||    // packs
                         (ts == 3 && alt == 2 && walls == 84);     // collision
        std::printf("[draft] map ts=%d altars=%zu walls=%zu fight=%d\n", ts, alt, walls, fight_map ? 1 : 0);
        if (fight_map) {
            if (ts <= 3) prefs = {"stellar", "tavi", "cassi"};
            else if (ts == 4) prefs = {"ren", "stellar", "tavi", "cassi"};
            else prefs = {"varg", "ren", "stellar", "tavi", "cassi"};
            for (const char* p : PREFS) prefs.push_back(p);  // fallbacks
        }
    } else if (P_DRAFTUNI) {
        int ts = 0, sp = -1;
        attempt([&] { ts = static_cast<int>(bc::draft::team_size()); return true; });
        if (P_DRAFTUNI == 2)
            attempt([&] {  // path length between the spawn regions (native distance field; a manual BFS runs out of draft fuel)
                bc::bitboard block = bc::map::walls() | bc::map::holes() | bc::map::altars();
                bc::distance_field da;
                bc::bitboard va;
                da.compute(block, bc::map::spawn_region(bc::team::ally), va);
                int ab = 1 << 30;
                for (auto p : bc::map::spawn_region(bc::team::enemy).positions())
                    if (va.is_set(p)) ab = std::min(ab, static_cast<int>(da.get(p)));
                if (ab < (1 << 30)) sp = ab;
                return true;
            });
        bool fight_map = P_DRAFTUNI == 1 || (sp >= 0 && sp <= P_UNI_PATH);
        std::printf("[draft] uni ts=%d spawn_path=%d fight=%d\n", ts, sp, fight_map ? 1 : 0);
        if (fight_map) {
            if (ts <= 3) prefs = {"cassi", "ren", "stellar"};
            else if (ts == 4) prefs = {"cassi", "ren", "stellar", "tavi"};
            else if (P_DRAFT5) prefs = {"cassi", "stellar", "varg", "tavi", "ren"};  // top-10 winners' 5-champion draft on the new maps
            else prefs = {"ryth", "stellar", "prism", "ren", "tavi"};
            for (const char* p : PREFS) prefs.push_back(p);  // fallbacks
        }
    }
    if (P_MAPPLAN) {  // mapplan.h: the draft read from map features
        MpDraftFeat f = mp_draft_features();
        auto chosen = mp_draft(f);
        std::printf("[mapplan] ts=%d altars=%d walls=%d %dx%d path=%d open=%d far_fight=%d\n", f.ts, f.altars, f.walls, f.w, f.h, f.path, f.open,
                    mp_far_fight(f) ? 1 : 0);
        if (!chosen.empty()) {
            prefs = std::move(chosen);
            for (const char* p : PREFS) prefs.push_back(p);  // fallbacks
        }
    }
    if (P_D34_FAMILY && fuel_ok(12000)) g_de_map = v34de::probe();
    if (P_D34_FAMILY) {
        auto chosen = v34de::recipe(g_de_map);
        if (!chosen.empty()) {
            prefs = std::move(chosen);
            for (const char* fallback : PREFS) prefs.push_back(fallback);
        }
    }
    for (const char* p : prefs)
        for (auto& o : all)
            if ((o.name == p || starts_with(o.name, p)) && !has(o.name)) order.push_back(o);
    for (auto& o : all)
        if (!has(o.name)) order.push_back(o);  // anything we did not list, as a fallback

    std::printf("[draft] %zu champions found:", all.size());
    for (auto& o : all) std::printf(" %s", o.name.c_str());
    std::printf("\n");
    std::fflush(stdout);
    std::vector<std::uint8_t> mine;
    std::vector<bool> tried(order.size(), false);
    for (;;) {
        for (std::size_t k = 0; k < order.size(); ++k) {
            if (tried[k]) continue;
            if (!fuel_ok(3000)) break;
            auto plan = mine;
            plan.push_back(order[k].raw);
            write_plan(plan);  // plan must be in draft memory before the final pick
            bool ok = attempt([&] {
                bc::draft::pick(order[k].value);
                return true;
            });
            tried[k] = true;  // accepted, or rejected because we already own it
            std::printf("[draft] pick %s -> %s\n", order[k].name.c_str(), ok ? "ok" : "rejected");
            std::fflush(stdout);
            if (ok) {
                mine.push_back(order[k].raw);
                break;
            }
        }
        bc::end_turn();
    }
}

// ---------------------------------------------------------------------------
// Gameplay state
// ---------------------------------------------------------------------------
enum class Slot { None, Reset, Dash, Targeted, Ground, Heal, Shield };

struct Group {
    std::vector<vec2> tiles;
    bc::bitboard mask;
    vec2 center;
    int gems = 0, gold = 0, respawn = 60;
    double hp = 0, str = 0;
    int members = 0;
    bool monolith = false;
    int next_ok = 0;       // believed to be on respawn cooldown until this round
    int bad_until = 0;     // we gave up on it; skip until this round
    int reward_seen = -1;  // round in which we last saw its reward available
    std::optional<bc::map::camp_group> obj;  // live handle for state() queries
    int spawn_pd = -1, altar_pd = -1;        // P_PATHD: walking distance from our spawn / from the nearest altar
    bool jackpot = false;                    // P_JACKPOT: most of the map's gems, about as far from both spawns
};

struct Shard {
    bc::item_type shard;
    bc::item_type emblem;
    char stat;  // 'h', 's', 'f'
    std::string family;
};

struct Step {
    const char* family;
    char stat;
    int want;  // how many of that emblem we want
};

struct Threat {
    vec2 p;
    double xd = 0;  // best ready spell that needs the caster to stand, and its range
    int xr = -9;
    double fd = 0;  // best ready spell that can follow a step
    int fr = -9;
    int sr = -9;  // range of a ready free stun
    double atk = 0;
    int ar = 1;      // basic attack reach next round
    double ready = 0;  // the biggest ready spell
};

// Static spell data per champion type (kind, modifier, range, exclusive), read once: info() is costly.
struct SpellInfo {
    int kind = 0;  // 1 attack reset, 2 damage, 3 cc with damage, 4 free pure stun, 0 nothing that hurts
    double mod = 0;
    int range = 0;
    bool excl = false;
};
struct ChampSpells {
    int type = -1;
    SpellInfo k[2];
};
inline const ChampSpells& spells_of(const bc::champion& c) {
    static std::vector<ChampSpells> cache;
    int type = -2;
    attempt([&] {
        type = static_cast<int>(c.champion_name());
        return true;
    });
    for (auto& cs : cache)
        if (cs.type == type) return cs;
    ChampSpells cs;
    cs.type = type;
    attempt([&] {
        auto abs = c.abilities();
        for (int k = 0; k < 2; ++k) {
            try {
                auto inf = abs[k].info();
                if (!inf) continue;
                std::visit([&](auto& x) {
                    using T = std::decay_t<decltype(x)>;
                    SpellInfo& si = cs.k[k];
                    if constexpr (T::kind == bc::ability_kind::attack_reset) {
                        si.kind = 1;
                    } else if constexpr (T::kind == bc::ability_kind::damage || T::kind == bc::ability_kind::aoe_damage ||
                                         T::kind == bc::ability_kind::cc) {
                        si.mod = x.modifier;
                        si.range = static_cast<int>(x.range);
                        if constexpr (requires { x.radius; }) si.range += static_cast<int>(x.radius);
                        si.excl = x.exclusive_with_movement;
                        if (x.modifier > 0) si.kind = 2;
                        else if (T::kind == bc::ability_kind::cc && !x.exclusive_with_movement) si.kind = 4;
                    }
                }, *inf);
            } catch (...) {
            }
        }
        return true;
    });
    if (type == -2) {  // unknown type: do not cache
        static ChampSpells tmp;
        tmp = cs;
        return tmp;
    }
    cache.push_back(cs);
    return cache.back();
}

inline Threat threat_of(bc::champion c, vec2 p, int atk_reach) {
    Threat t;
    t.p = p;
    t.ar = atk_reach;
    double foc = 0, str = 0;
    attempt([&] {
        foc = c.focus();
        str = c.strength();
        return true;
    });
    t.atk = str;
    const ChampSpells& cs = spells_of(c);
    if (!cs.k[0].kind && !cs.k[1].kind) return t;
    attempt([&] {
        auto abs = c.abilities();
        for (int k = 0; k < 2; ++k) {
            const SpellInfo& si = cs.k[k];
            if (!si.kind) continue;
            try {
                if (abs[k].cooldown() > 0) continue;
            } catch (...) {
                continue;
            }
            if (si.kind == 1) {
                t.atk += str;
            } else if (si.kind == 4) {
                t.sr = std::max(t.sr, si.range);
            } else {
                double d = si.mod * foc;
                t.ready = std::max(t.ready, d);
                if (si.excl) {
                    t.xd = std::max(t.xd, d);
                    t.xr = std::max(t.xr, si.range);
                } else {
                    t.fd = std::max(t.fd, d);
                    t.fr = std::max(t.fr, si.range);
                }
            }
        }
        return true;
    });
    return t;
}

// Damage we can take next round on tile t: one spell and one basic attack per foe.
inline double danger_at(const std::vector<Threat>& th, vec2 t) {
    double sum = 0;
    bool stun = false;
    for (auto& x : th) {
        int d = dist(t, x.p);
        double sp = 0;
        if (d <= x.xr) sp = x.xd;
        if (d <= x.fr + 1) sp = std::max(sp, x.fd);
        sum += sp + (d <= x.ar ? x.atk : 0.0);
        if (d <= x.sr + 1) stun = true;
    }
    if (stun)  // stunned for a round: the ready casters one step out get to stand and cast after
        for (auto& x : th) {
            int d = dist(t, x.p);
            if (d > x.xr && d <= x.xr + 1) sum += 0.5 * x.xd;
        }
    return sum;
}

struct Foe {
    bc::champion c;
    vec2 p;
    float hp;
    int d;
    int gems;
    bool channeling;
    bool away = false;  // moved farther from us since last round (P_NOCHASE)
};
struct Seen {
    bc::champion c;
    vec2 p;
    int away_until;
};

struct State {
    bc::bitboard mp_dashholes, mp_hvis, mp_hole_all;  // mapplan_game.h rule 5: hole tiles a dash crosses, and its field
    bc::distance_field mp_hdf;
    int mp_bank_d = -1, mp_home_d = -1, mp_last_g = -1, mp_last_r = -1000;
    vec2 self_pos;  // mapplan_game.h: median walk from a gem group to its altar / to our spawn
    bool ready = false;

    unsigned cf_reach = 0, cf_focus_wait = 0, cf_focus_exit = 0, cf_focus_hit = 0, cf_evac = 0;
    unsigned cf_reward_gain_observed = 0, cf_death_after_camp = 0;
    int cf_recent_camp = -1000, cf_log_round = -1000;
    bool cf_was_alive = false;
    std::optional<bc::team> my, en;
    bc::bitboard static_block, my_spawn, en_spawn;
    std::vector<vec2> altars, spawn_tiles;
    vec2 spawn_center, en_center;
    std::vector<Group> groups;
    bool mono_only = false;  // P_MONO: every gem on the map sits in a monolith group
    bool jackpot_map = false;  // P_JACKPOT: a jackpot group exists, so gold clusters are worth farming before it
    std::vector<Shard> shards;
    std::vector<bc::item_type> fallback_items;
    std::vector<Step> plan;
    std::array<Slot, 2> slots{Slot::None, Slot::None};
    int dash_slot = -1, reset_slot = -1;
    bool melee = true;
    std::string name;
    int ally_idx = -1;

    int target = -1;
    int target_round = 0;
    int cap_start = -1;
    int last_gems = 0, last_gold = 0;

    bc::bitboard blocked, visited, dest, vis;
    bc::distance_field df;
    std::vector<int> lock_until;
    std::vector<vec2> pots;          // altars with 3+ gem groups next to them (corners centre)
    std::vector<char> pot_group;     // per group: one of those gem groups
    bool casters = true;             // P_CASTGATE: our team has 3+ ranged champions
    int sweep = P_SWEEP;             // P_DRAFTUNI: cast-first (3) only with the caster draft, else 2
    bool renkite = false;            // P_UNI_RENKITE: Ren kites like a caster in the caster draft
    int rnear = P_RECALL_NEAR;       // P_DRAFTUNI: recall near foes only with the caster draft (P_UNI_RN 1)
    int hold = -1;                   // P_HOLD: index of the centre altar we hold, -1 if none
    std::vector<char> hold_group;    // per group: a gem camp within P_HOLD_R of the hold altar
    std::vector<char> altar_ok;  // altar has a tile next to it that is reachable from our spawn  // per altar: round until which we believe it enemy-locked
    int probe_fail = 0;
    int roster = 1;        // champions per team on this map
    int need_heal = -1000; // round in which farm() asked for a recall
    float last_hp = -1.0f;  // health at the start of our previous turn
    int hit_round = -1000;  // last round in which we lost health
    vec2 danger_p{0, 0};
    int danger_r = -1000;   // last round an enemy pack was seen at danger_p
    int foe_r = -1000;      // last round this champion saw an enemy champion
    int nf_d = 99, nf_r = -1000;  // P_CAMPHOLD: nearest enemy champion this round and the round it was measured
    std::vector<Seen> seen; // P_NOCHASE: enemy positions last round
    int seen_r = -10;
    vec2 seen_me{0, 0};     // our own tile last round
    int shop_recall = -1000; // last round we recalled to go shopping
    std::size_t shop_next = 0;    // P_SHOPFIX: next item index build_shop has to look at
    bool shop_done = false;       // P_SHOPFIX: every item type looked at
    int shop_fail = -1000;        // P_SHOPFIX: last round shopping on spawn bought nothing
    int still_x = -1, still_y = -1, still_n = 0;  // turns spent on the same tile
    signed char excl[2] = {-1, -1};  // P_SWEEP 5: slot k can't be cast in a round we move (1), can (0), unknown (-1)
    int rooted_r = -1;               // P_SWEEP 5: round we cast a move-exclusive spell before moving
    int fm = 0, fm_r = -10;          // P_FM: 1 engaged / 2 retreating, and the last round of that state
    int fm_hold = 0;                 // P_FM 2: rounds waiting at the edge of their range
    std::vector<Threat> thr;         // P_VOLLEY: ready enemy damage around us this round
    bc::distance_field pdf;          // P_PATHD: walking distances from where we stand
    bc::distance_field tele_fa;      // P_TELE: walking distance to the nearest usable altar
    bc::bitboard tele_va;
    int tele_sa = -1;                // P_TELE: walking distance spawn -> nearest altar
    bc::bitboard pdv;
    vec2 pd_pos{-1, -1};             // P_FUELGUARD: where pd_gd was measured (walls never change, so it holds there)
    std::vector<int> pd_gd;          // P_FUELGUARD: walking distance to each camp group from pd_pos (-1 unreached)
    std::uint64_t ct_cost = 20000;   // P_FUELGUARD: the dearest choose_target so far
    int init_stage = 0;              // start-up parts done (init)
    int thr_r = -1;
    int ch_round = -1;
    vec2 ch_pos{-1,-1};
    bool ch_complete = false;
    bool ch_camps_complete = false;
    std::vector<vec2> ch_foes;
    std::vector<bc::camp> ch_camps;
    // Capture-recall optional economy policy. Static return-trip distances.
    bc::distance_field cr_home_df;
    bc::bitboard cr_home_seen;
    bool cr_home_ready = false;
    int cr_home_retry = -1;
    int cr_seen = 0, cr_skipped = 0, cr_tavi_skipped = 0;
    int cr_path_unavailable = 0, cr_started = 0, cr_log_round = -1;
    int de_map = 0;
    bool ranged_me = false;  // P_CACHE: attack range > 1
    int tank_bits = -1;      // P_DPSFARM: bit k = ally k is a tank (-1 not known yet)
    bool sub_prev = false;   // P_BACKHOME: we were channelling a tribute last turn
    int trib_end = -1000;    // P_BACKHOME: round our last tribute finished
    int wait_start = -1000, wait_group = -1;  // P_NEEDHEAL: first round of the current rally / need-heal wait
    // BR_BANKING_ROUTING: private per-champion, one plan per round/position.
    int br_round = -1, br_choice = -1, br_reason = 0;
    vec2 br_pos{0, 0};
    bool br_safe_route = false;
    std::vector<int> br_lengths;
    bc::bitboard br_risk_block;
    int br_decisions = 0, br_fallbacks = 0, br_routes = 0, br_stops = 0;
    int br_log_round = -1;
    std::vector<bc::champion> roster_my, roster_en;  // P_ROSTER: the champion handles, read once
    int oc_round = -1, oc_group = -1, oc_x = -1, oc_y = -1;  // P_OCMEMO: other_captures' answer this turn
    bool oc_other = false, oc_on = false;

};

// P_ROSTER (2026-10-16 fuel profile): bc::champions(team) cost 3k-23k fuel a call and the handles never change, so
// read each roster once. P_OCMEMO: other_captures ran up to 4 times a turn (~15k each, the most expensive thing in
// the turns that ran out of fuel on monolith, stampede, lanes and corners); within one turn its answer only depends
// on the group and our tile, so it is computed once per (round, group, tile). Same decisions with unlimited fuel.
#ifndef P_ROSTER
#define P_ROSTER 0
#endif
#ifndef P_OCMEMO
#define P_OCMEMO 0
#endif
inline std::vector<bc::champion> my_roster(State& s) {
    if (!P_ROSTER) return bc::champions(*s.my);
    if (s.roster_my.empty()) s.roster_my = bc::champions(*s.my);
    return s.roster_my;
}
inline std::vector<bc::champion> en_roster(State& s) {
    if (!P_ROSTER) return bc::champions(*s.en);
    if (s.roster_en.empty()) s.roster_en = bc::champions(*s.en);
    return s.roster_en;
}

Slot classify(const bc::ability& a) {
    if (!a.info().has_value()) return Slot::None;
    if (a.is_dash()) return Slot::Dash;
    if (a.is_attack_reset()) return Slot::Reset;
    if (a.is_heal()) return Slot::Heal;
    if (a.is_shield()) return Slot::Shield;
    if (a.can_target_ground() && (a.is_aoe_damage() || a.is_cc() || a.is_damage())) return Slot::Ground;
    if (a.is_damage() || a.is_cc()) return Slot::Targeted;
    return Slot::None;
}

#include "opening_replace.h"

void build_shop(State& s, bc::champion& me) {
    std::size_t n = 0;
    attempt([&] {
        n = me.item_count().size();
        return true;
    });
    std::size_t i0 = P_SHOPFIX ? s.shop_next : 0;
    for (std::size_t i = i0; i < n && (P_DBGT_ALL || fuel_ok(20000)); ++i) {
        s.shop_next = i + 1;
        if (s.shop_next >= n) s.shop_done = true;
        attempt([&] {
            bc::item_type t(static_cast<std::uint32_t>(i));
            if (!t.is_purchasable()) return false;
            auto r = t.result();
            if (!r) return false;
            char stat = t.health_points() > 0 ? 'h' : (t.strength_points() > 0 ? 's' : 'f');
            if (stat == 'h') s.fallback_items.push_back(t);
            std::string fam;
            auto pas = r->passive();
            if (pas) fam = norm(bc::to_string(*pas));
            if (fam.empty() || fam == "none") {
                bool spread = r->health_points() > 0 && r->strength_points() > 0 && r->focus_points() > 0;
                fam = spread ? "bruiser" : "power";
            }
            s.shards.push_back({t, *r, stat, fam});
#ifdef P_DBGT
            if (s.ally_idx <= 0) std::printf("[item] %zu stat=%c fam=%s h=%d s=%d f=%d -> h=%d s=%d f=%d\n", i, stat, fam.c_str(), (int)t.health_points(), (int)t.strength_points(), (int)t.focus_points(), (int)r->health_points(), (int)r->strength_points(), (int)r->focus_points());
#endif
            return true;
        });
    }
    // Emblem build per champion. Families are matched by name prefix.
    if (starts_with(s.name, "ryth")) {
        s.plan = {{"jungle", 'h', 1}, {"durab", 'h', 1}, {"monster", 'h', 1}, {"power", 'h', 99}};
    } else if (starts_with(s.name, "vesper")) {
        s.plan = {{"monster", 's', 1}, {"treasure", 's', 1}, {"jungle", 'h', 1}, {"power", 's', 99}};
    } else if (s.melee) {
        s.plan = {{"jungle", 'h', 1}, {"monster", 's', 1}, {"durab", 'h', 1}, {"power", 's', 99}};
    } else {
        s.plan = {{"monster", 's', 1}, {"jungle", 'h', 1}, {"power", 's', 99}};
    }
    if (P_SHOP_PLAN) {  // what the top teams buy: the monster emblem first, then power
        if (starts_with(s.name, "cassi") && P_CASSI_HP)  // her death also kills Issac: health first
            s.plan = {{"jungle", 'h', 1}, {"durab", 'h', 1}, {"monster", 'f', 1}, {"power", 'f', 99}};
        else if (starts_with(s.name, "cassi"))
            s.plan = {{"monster", 'f', 1}, {"power", 'f', 99}};
        else if (starts_with(s.name, "ryth"))
            s.plan = {{"monster", 's', 1}, {"power", 's', 2}, {"jungle", 'h', 1}, {"power", 's', 99}};
        else
            s.plan = {{"monster", 's', 1}, {"power", 's', 3}, {"jungle", 'h', 1}, {"power", 's', 99}};
        if (P_SHOP_PLAN >= 2 && !starts_with(s.name, "cassi"))  // Mite's tank build: survive camps solo, then raw power
            s.plan = {{"durab", 's', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 1}, {"power", 's', 99}};
        if (P_SHOP_PLAN == 3) {  // what the top-10 winners buy (2026-10-14 study of 169 games)
            if (starts_with(s.name, "issac"))      // their Issac: 11 power-s shards a game, ours 5.5
                s.plan = {{"power", 's', 2}, {"jungle", 's', 1}, {"power", 's', 99}};
            else if (starts_with(s.name, "tavi"))  // their Tavi buys focus; ours bought strength
                s.plan = {{"power", 'f', 1}, {"bruiser", 'f', 1}, {"power", 'f', 99}};
            else if (starts_with(s.name, "cassi")) // little gold on Cassi: power-f and one durability-h
                s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};
            else if (starts_with(s.name, "stellar"))  // top Stellar: power-f x10, durability-h
                s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};
            else if (starts_with(s.name, "ren"))      // top Ren: power-s, some power-f (retaliation is focus)
                s.plan = {{"power", 's', 1}, {"bruiser", 'h', 1}, {"power", 'f', 1}, {"power", 's', 99}};
        }
    }
    if (P_SHOPUNI && (starts_with(s.name, "ren") || starts_with(s.name, "prism") || starts_with(s.name, "stellar")))
        s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};  // the #1's casters: 8-13 power-f a game
#if defined(P_NE_POWER_OPEN) && P_NE_POWER_OPEN > 0
    // One offensive opening emblem, then the complete original melee core.
    // Preserve Jungle camp mitigation and Bruiser health for later farming.
    if (starts_with(s.name, "ryth") || starts_with(s.name, "varg") || starts_with(s.name, "vendetta"))
        s.plan = {{"power", 's', 1}, {"durab", 's', 1}, {"jungle", 's', 1},
                  {"bruiser", 'h', 1}, {"power", 's', 99}};
#endif
    // O36_REPLACE_HOOK: one quota replaces one quota; no extra150-gold step.
    opening36::replace(s.plan, s.de_map, s.name, ((s.de_map == v34de::Rows) ? P_O36_REPLACE : 0));
}

// Start-up runs in three parts (map and camp groups, fixed walking distances, roles and shop). P_FUELGUARD lets a
// part wait for the next turn when this one cannot pay for it; with enough fuel all three run in the first turn.
void init_map(State& s, bc::champion& me) {
    FP_SCOPE(27, "init-start");
#ifdef P_CONSTPROBE
    std::printf("[const] capture=%d sleep=%d respawn=%d recall=%d submit_mult=%.3f base=%d min=%d range=%d\n", static_cast<int>(bc::constants::capture_time),
                static_cast<int>(bc::constants::camp_sleep_time), static_cast<int>(bc::constants::respawn_time),
                static_cast<int>(bc::constants::recall_time), static_cast<double>(bc::constants::submit_gem_duration_multiplier),
                static_cast<int>(bc::constants::submit_gem_base_duration), static_cast<int>(bc::constants::submit_gem_minimum_duration),
                static_cast<int>(bc::constants::submit_gems_range));
#endif
    s.my = me.team();
    s.en = bc::opponent(*s.my);
    s.my_spawn = bc::map::spawn_region(*s.my);
    s.en_spawn = bc::map::spawn_region(*s.en);
    s.static_block = bc::map::walls() | bc::map::holes() | bc::map::altars() | s.en_spawn;
    s.altars = bc::map::altars().positions();
    s.lock_until.assign(s.altars.size(), 0);
    s.altar_ok.assign(s.altars.size(), 1);
    FP(29, "init-altars");
    if (P_ALTAR_REACH && P_FUELGUARD)
        attempt([&] {  // one search from where we start; an altar is usable when a tile next to it is reached
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | bc::map::altars();
            bc::bitboard roots, seen;
            roots.set(me.position());
            bc::distance_field df;
            df.compute(wall, roots, seen);
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                bc::bitboard ring;
                ring.draw_chebyshev(s.altars[i], 1.0f);
                s.altar_ok[i] = (ring & ~wall & seen).is_empty() ? 0 : 1;
            }
            return true;
        });
    else if (P_ALTAR_REACH)
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | bc::map::altars();
            vec2 home = me.position();
            bc::distance_field df;
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                bc::bitboard ring, dest, seen;
                ring.draw_chebyshev(s.altars[i], 1.0f);
                dest.set(home);
                df.compute_to(wall, ring & ~wall, dest, seen);
                s.altar_ok[i] = seen.is_set(home) ? 1 : 0;
            }
            return true;
        });
    FP(28, "init-spawn");
    s.spawn_tiles = s.my_spawn.positions();

    auto centre = [](const std::vector<vec2>& v, vec2 fallback) {
        if (v.empty()) return fallback;
        long sx = 0, sy = 0;
        for (auto p : v) { sx += X(p); sy += Y(p); }
        vec2 m(static_cast<std::int32_t>(sx / static_cast<long>(v.size())),
               static_cast<std::int32_t>(sy / static_cast<long>(v.size())));
        vec2 best = v[0];
        for (auto p : v)
            if (dist(p, m) < dist(best, m)) best = p;
        return best;
    };
    s.spawn_center = centre(s.spawn_tiles, me.position());
    attempt([&] {
        s.en_center = centre(s.en_spawn.positions(), vec2(0, 0));
        return true;
    });

    FP(21, "init-groups");
    std::vector<bc::map::camp_group> raw_groups;
    attempt([&] {
        raw_groups = bc::map::camp_groups();
        return true;
    });
    if (P_FUELGUARD) s.groups.reserve(std::min<std::size_t>(raw_groups.size(), MAX_GROUPS));
    for (auto& g : raw_groups) {
        if (s.groups.size() >= MAX_GROUPS) break;
        attempt([&] {
        Group G;
        G.mask = g.spawn_tiles();
        G.tiles = G.mask.positions();
        if (G.tiles.empty()) return false;
        G.center = centre(G.tiles, G.tiles[0]);
        G.gems = static_cast<int>(g.gem_value());
        G.gold = static_cast<int>(g.gold_value());
        G.respawn = g.max_respawn_timer();
        for (auto& c : g.camps()) {
            double h = 0, st = 0;
            monster_stats(c, h, st);
            G.hp += h;
            G.str += st;
            G.monolith = G.monolith || c.is_monolith();
            ++G.members;
        }
        G.obj = g;
        s.groups.push_back(std::move(G));
        return true;
        });
    }
    if (P_MONO) {
        bool other_gems = false, mono = false;
        for (auto& g : s.groups) {
            if (g.monolith) mono = mono || g.gems > 0;
            else other_gems = other_gems || g.gems > 0;
        }
        s.mono_only = mono && !other_gems;
    }

}

void init_paths(State& s) {
    FP_SCOPE(22, "init-dist");
    if (P_PATHD)  // walking distances that never change: our spawn and the altars to every camp group
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn;
            bc::distance_field fs, fa;
            bc::bitboard vs, va, ar;
            fs.compute(wall, s.my_spawn & ~wall, vs);
            for (std::size_t i = 0; i < s.altars.size(); ++i)
                if (s.altar_ok[i]) ar.set(s.altars[i]);
            fa.compute(wall, ar, va);
            for (auto& g : s.groups) {
                int bs = 1 << 20, ba = 1 << 20;
                for (auto t : g.tiles) {
                    if (vs.is_set(t)) bs = std::min(bs, static_cast<int>(fs.get(t)));
                    if (va.is_set(t)) ba = std::min(ba, static_cast<int>(fa.get(t)));
                }
                g.spawn_pd = bs < (1 << 20) ? bs : -1;
                g.altar_pd = ba < (1 << 20) ? ba : -1;
            }
            return true;
        });
    if (P_JACKPOT)  // a jackpot: one group with half the map's gems or more, contested (as far from both spawns)
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.my_spawn;
            bc::distance_field fe;
            bc::bitboard ve;
            fe.compute(wall, s.en_spawn & ~wall, ve);
            int total = 0;
            for (auto& g : s.groups) total += g.gems;
            for (auto& g : s.groups) {
                if (g.monolith || g.gems * 2 < total || g.spawn_pd < 0) continue;
                int be = 1 << 20;
                for (auto t : g.tiles)
                    if (ve.is_set(t)) be = std::min(be, static_cast<int>(fe.get(t)));
                g.jackpot = be < (1 << 20) && std::abs(be - g.spawn_pd) <= 6;
                if (g.jackpot) s.jackpot_map = true;
                if (g.jackpot) std::printf("[jackpot] gems=%d of %d, from us %d, from them %d\n", g.gems, total, g.spawn_pd, be);
            }
            return true;
        });
    if (P_TELE)  // walking distance to the altars from everywhere, and from our spawn
        attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn, ar;
            for (std::size_t i = 0; i < s.altars.size(); ++i)
                if (s.altar_ok[i]) ar.set(s.altars[i]);
            s.tele_fa.compute(wall, ar, s.tele_va);
            int b = 1 << 20;
            for (auto t : s.spawn_tiles)
                if (s.tele_va.is_set(t)) b = std::min(b, static_cast<int>(s.tele_fa.get(t)));
            s.tele_sa = b < (1 << 20) ? b : -1;
            return true;
        });
}

void init_roles(State& s, bc::champion& me) {
    FP_SCOPE(25, "init-misc");
    if (P_DRAFTUNI)  // kite/hold only with the #1's caster draft (it always has Stellar; Ren counts as melee)
        attempt([&] {
            bool st = false;
            for (auto& a : my_roster(s))
                if (starts_with(norm(bc::to_string(a.champion_name())), "stellar")) st = true;
            s.casters = st;
            if (!st && P_SWEEP >= 3) s.sweep = 2;
            if (!st && P_UNI_RN) s.rnear = 0;
            if (st && P_UNI_RENKITE && starts_with(norm(bc::to_string(me.champion_name())), "ren")) s.renkite = true;
            return true;
        });
    s.pot_group.assign(s.groups.size(), 0);
    if (P_POT)
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (!s.altar_ok[i]) continue;
            int n = 0;
            for (auto& g : s.groups)
                if (g.gems > 0 && g.str <= 0 && dist(g.center, s.altars[i]) <= 4) ++n;
            if (n < 3) continue;
            s.pots.push_back(s.altars[i]);
            for (std::size_t k = 0; k < s.groups.size(); ++k)
                if (s.groups[k].gems > 0 && s.groups[k].str <= 0 && dist(s.groups[k].center, s.altars[i]) <= 4) s.pot_group[k] = 1;
        }
    if (P_CASTGATE) {
        int ranged = 0;  // the caster ball has 3+ ranged bodies; v19's melee draft has 2 (Cassi, Tavi)
        attempt([&] {
            for (auto& a : my_roster(s))
                try {
                    if (a.attack_range() > 1) ++ranged;
                } catch (...) {
                }
            return true;
        });
        s.casters = ranged >= 3;
    }
    s.hold_group.assign(s.groups.size(), 0);
    if (P_HOLD && s.casters) {
        int bd = 1 << 30;
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (!s.altar_ok[i]) continue;
            int dm = dist(s.altars[i], s.spawn_center), de = dist(s.altars[i], s.en_center);
            if (std::abs(dm - de) > 4) continue;
            int n = 0;
            for (auto& g : s.groups)
                if (g.gems > 0 && dist(g.center, s.altars[i]) <= P_HOLD_R) ++n;
            if (n >= 2 && dm < bd) { bd = dm; s.hold = static_cast<int>(i); }
        }
        if (s.hold >= 0)
            for (std::size_t k = 0; k < s.groups.size(); ++k)
                s.hold_group[k] = s.groups[k].gems > 0 && dist(s.groups[k].center, s.altars[s.hold]) <= P_HOLD_R;
    }
    s.melee = me.attack_range() <= 1;
    s.ranged_me = !s.melee;
    attempt([&] {
        s.name = norm(bc::to_string(me.champion_name()));
        return true;
    });
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        attempt([&] {
            s.slots[k] = classify(abs[k]);
            return true;
        });
        if (s.slots[k] == Slot::Dash) s.dash_slot = k;
        if (s.slots[k] == Slot::Reset) s.reset_slot = k;
    }

    attempt([&] {
        auto allies = my_roster(s);
        s.roster = static_cast<int>(allies.size());
        for (std::size_t i = 0; i < allies.size(); ++i)
            if (allies[i] == me) s.ally_idx = static_cast<int>(i);
        return true;
    });

    attempt([&] {
        bc::draft_memory_buffer dm;
#if P_DP_MEMORY_FIX
        // Optional cache errors must not suppress the independent legacy settings.
        attempt([&] { draftplan::load(dm); return true; });
        const auto legacy=draftplan::read_legacy_settings(dm);
        if (P_D34_FAMILY && legacy.family>=v34de::Unknown && legacy.family<=v34de::Rows) s.de_map=legacy.family;
        if (legacy.tribute>=0) P.tribute_gems=legacy.tribute;
        if (legacy.recall>=0) P.recall_pct=legacy.recall;
        if (legacy.flee>=0) P.flee_pct=legacy.flee;
        if (legacy.late>=0) P.late_round=legacy.late;
#else
        draftplan::load(dm);
        if (dm.size() >= 28 && dm[0] == std::byte{'C'} && dm[1] == std::byte{'M'} &&
            dm[2] == std::byte{'B'} && dm[3] == std::byte{'1'}) {
            if (P_D34_FAMILY && dm.size() > 28) {
                int family = std::to_integer<int>(dm[28]);
                if (family >= v34de::Unknown && family <= v34de::Rows) s.de_map = family;
            }
            int tg = std::to_integer<int>(dm[24]), rc = std::to_integer<int>(dm[25]);
            int fl = std::to_integer<int>(dm[26]), lr = std::to_integer<int>(dm[27]) * 10;
            if (tg >= 5 && tg <= 200) P.tribute_gems = tg;
            if (rc >= 10 && rc <= 90) P.recall_pct = rc;
            if (fl >= 5 && fl <= 80) P.flee_pct = fl;
            if (lr >= 500 && lr <= 2000) P.late_round = lr;
        }
#endif
        return true;
    });

    FP(23, "init-shop");
    attempt([&] {
        build_shop(s, me);
        return true;
    });
    s.last_gems = static_cast<int>(me.gem_count());
    s.last_gold = static_cast<int>(me.gold_count());

    // the game plan for this map (profile.h)
    MapFeatures mf;
    mf.camps = static_cast<int>(s.groups.size());
    mf.altars = static_cast<int>(s.altars.size());
    mf.spawn_dist = dist(s.spawn_center, s.en_center);
    attempt([&] { mf.team_size = static_cast<int>(bc::draft::team_size()); return true; });
    attempt([&] { mf.area = static_cast<int>(bc::map::width() * bc::map::height()); return true; });
    apply_profile(mf);
}

#include "mapplan_game.h"

// true once start-up is complete. A part that throws is not retried (its stage is counted before it runs).
bool init(State& s, bc::champion& me) {
    if (s.init_stage == 0) { s.init_stage = 1; init_map(s, me); }
    if (s.init_stage == 1) {
        if (P_FUELGUARD && !fuel_ok(35000)) return false;
        s.init_stage = 2;
        init_paths(s);
        if (P_MAPPLAN && (P_MP_FARHOME || P_MP_FOCUS_FAR || P_MP_SPREAD || P_MP_COMPANY || P_MP_CHAINPLAN)) mp_game_plan(s);  // only the rules that need it: off = v52 games
    }
    if (s.init_stage == 2) {
        if (P_FUELGUARD && !fuel_ok(50000)) return false;
        s.init_stage = 3;
        init_roles(s, me);
        if (P_MAPPLAN && P_MP_DASHHOLE && s.dash_slot >= 0) mp_find_dashholes(s);  // mapplan_game.h rule 5
    }
    return true;
}

// ---------------------------------------------------------------------------
// Shopping
// ---------------------------------------------------------------------------
void shop(State& s, bc::champion& me) {
    for (int it = 0; it < 12 && fuel_ok(10000); ++it) {
        if (me.gold_count() < 30) return;
        auto counts = me.item_count();
        const Shard* pick = nullptr;
        for (auto& st : s.plan) {
            const Shard* sh = nullptr;
            for (auto& x : s.shards)
                if (x.stat == st.stat && starts_with(x.family, st.family)) { sh = &x; break; }
            if (!sh) continue;
            if (static_cast<int>(counts[sh->emblem]) >= st.want) continue;
            pick = sh;
            break;
        }
        bool ok = false;
        if (pick) {
            ok = attempt([&] {
                if (!me.can_buy(pick->shard, 1)) return false;
                me.buy(pick->shard, 1);
                return true;
            });
        } else {
            for (auto& t : s.fallback_items) {
                ok = attempt([&] {
                    if (!me.can_buy(t, 1)) return false;
                    me.buy(t, 1);
                    return true;
                });
                if (ok) break;
            }
        }
        if (!ok) {
#ifdef P_DBGT
            int tot = 0;
            attempt([&] { for (auto c : me.item_count()) tot += static_cast<int>(c); return true; });
            std::printf("[shopfail] %s gold=%d plan=%zu shards=%zu fb=%zu pick=%s/%c items=%d\n", s.name.c_str(), static_cast<int>(me.gold_count()), s.plan.size(), s.shards.size(), s.fallback_items.size(),
                        pick ? pick->family.c_str() : "-", pick ? pick->stat : '-', tot);
#endif
            return;
        }
    }
}

// ---------------------------------------------------------------------------
// Movement
// ---------------------------------------------------------------------------
// Step (and dash, if allowed) towards any tile of `goals_in`. Returns true if we moved.
// P_VOLLEY: modes that commit to a fight walk in on purpose; every other mode respects the volley map.
// P_VOLLEY_FIGHT 1: ranged champions respect it in fights too (melee still walk in); 2: everybody does.
#ifndef P_VOLLEY_FIGHT
#define P_VOLLEY_FIGHT 0
#endif
// P_VOLLEY_FARM 0: farming ignores it too (online v25 gave up camps on expanse/lanes with no deaths to save).
#ifndef P_VOLLEY_FARM
#define P_VOLLEY_FARM 1
#endif
bool volley_mode(bc::champion& me) {
    if (!P_VOLLEY_FARM && (std::strcmp(g_mode, "farm") == 0 || std::strcmp(g_mode, "channel") == 0)) return false;
    if (P_VOLLEY_FIGHT >= 2 || (P_VOLLEY_FIGHT == 1 && me.attack_range() > 1)) return true;
    static const char* fights[] = {"fight", "front", "kite", "fm-engage", "twin"};
    for (auto* f : fights)
        if (std::strcmp(g_mode, f) == 0) return false;
    return true;
}

// P_FUELGUARD: one step to the free neighbour closest to `to` (straight line), no path search: the turn still moves
// when it has no fuel left for a search.
bool greedy_step(State& s, bc::champion& me, vec2 to) {
    if (!me.can_move()) return false;
    vec2 pos = me.position();
    int here = dist(pos, to), bd = here;
    std::optional<vec2> best;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 t = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
            int d = dist(t, to);
            if (d < bd) { bd = d; best = t; }
        }
    return best && attempt([&] { return me.move_absolute(*best); });
}

// P_DASHCALM (2026-10-17, swirl vs Nameless: Ren dashed to the centre at r4 and met all five; 32 of our 66 dashes
// ended closer to an enemy): while farming, no dash toward a camp in the first P_DASHCALM_OPEN rounds or within
// P_DASHCALM rounds of seeing an enemy champion. Fleeing and fights keep their dash.
#ifndef P_DASHCALM
#define P_DASHCALM 0
#endif
#ifndef P_DASHCALM_OPEN
#define P_DASHCALM_OPEN 40
#endif
inline bool g_farm_nodash = false;
bc::bitboard mp_awake_camp_zone(State& s, vec2 pos);
int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos);
bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {
    FP_SCOPE(16, "step_towards");
    if (g_farm_nodash) use_dash = false;
    vec2 pos = me.position();
    bc::bitboard goals = goals_in & ~s.blocked;
    if (goals.is_empty() || goals.is_set(pos)) return false;
    if (!me.can_move() && !(use_dash && s.dash_slot >= 0)) return false;

    bc::bitboard vblock = s.blocked;  // P_VOLLEY: blocked plus lethal tiles
    bool vol_on = false;
    if (P_VOLLEY && !s.thr.empty() && s.thr_r == static_cast<int>(bc::round_number()) && volley_mode(me)) {
        double lim = me.health() * P_VOLLEY / 100.0;
        double here = danger_at(s.thr, pos);
        if (here >= lim) {  // standing in a ready volley: first get out, toward the goal on ties
            if (me.can_move()) {
                bool field = attempt([&] {
                    s.dest.clear();
                    s.dest.set(pos);
                    s.df.compute_to(s.blocked, goals, s.dest, s.visited);
                    return true;
                });
                std::vector<std::pair<double, vec2>> c;
                for (int dx = -1; dx <= 1; ++dx)
                    for (int dy = -1; dy <= 1; ++dy) {
                        if (!dx && !dy) continue;
                        vec2 t = pos + vec2(dx, dy);
                        if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                        double dg = danger_at(s.thr, t);
                        if (dg >= here) continue;
                        double g = field && s.visited.is_set(t) ? s.df.get(t) : 999;
                        c.push_back({dg + 0.5 * g, t});
                    }
                std::sort(c.begin(), c.end(), [](auto& a, auto& b) { return a.first < b.first; });
                for (auto& [sc, t] : c)
                    if (attempt([&] { return me.move_absolute(t); })) return true;
            }
        } else {  // the ring around us is enough: next turn looks again
            for (int dx = -P_VOLLEY_R; dx <= P_VOLLEY_R; ++dx)
                for (int dy = -P_VOLLEY_R; dy <= P_VOLLEY_R; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if ((dx || dy) && bc::map::is_in_bounds(t) && !s.blocked.is_set(t) && danger_at(s.thr, t) >= lim) {
                        vblock.set(t);
                        vol_on = true;
                    }
                }
        }
    }

    if (!fuel_ok(25000)) {
        auto ps = goals.positions();
        if (ps.empty()) return false;
        vec2 best = ps[0];
        for (auto p : ps)
            if (dist(p, pos) < dist(best, pos)) best = p;
        if (P_FUELGUARD && !fuel_ok(14000)) return greedy_step(s, me, best);  // move_towards is one more path search
        return attempt([&] { return me.move_towards(best); });
    }

    s.dest.clear();
    s.dest.set(pos);
    auto fallback = [&] {
        auto ps = goals.positions();
        if (ps.empty() || !me.can_move()) return false;
        vec2 best = ps[0];
        for (auto p : ps)
            if (dist(p, pos) < dist(best, pos)) best = p;
        return attempt([&] { return me.move_towards(best); });
    };
    bool ok_field = false;
    if (P_MAPPLAN && P_MP_CAMPAVOID && fuel_ok(30000)) {  // mapplan_game.h rule 3: walk around awake camps we do not fight
        bc::bitboard avoid = mp_awake_camp_zone(s, pos);
        if (!avoid.is_empty())
            ok_field = attempt([&] {
                s.df.compute_to(vblock | (avoid & ~goals), goals, s.dest, s.visited);
                return s.visited.is_set(pos);
            });
    }
    if (!ok_field)
        ok_field = attempt([&] {
            s.df.compute_to(vblock, goals, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    if (!ok_field && vol_on) return false;  // every way runs through a ready volley: wait
    if (!ok_field && P_UNJAM) {  // corridor jammed by champions: plan through them
        ok_field = attempt([&] {
            bc::bitboard b2 = s.static_block | bc::vision::camp_tiles();
            b2.set(pos, false);
            s.df.compute_to(b2, goals_in & ~s.static_block, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    }
    if (!ok_field) return fallback();

    if (P_MAPPLAN && P_MP_DASHHOLE && use_dash && s.dash_slot >= 0 && !s.mp_dashholes.is_empty() && fuel_ok(40000)) {
        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash
        if (r) return r > 0;
    }
    bool moved = false;
    if (use_dash && s.dash_slot >= 0 && me.can_cast()) {
        auto ab = me.abilities()[s.dash_slot];
        int here = s.df.get(pos);
        if (here >= 3 && ab.is_ready()) {
            std::optional<vec2> best;
            int bestd = here - 1;  // only dash if it beats a plain step
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    int d = s.df.get(t);
                    if (d < bestd) { bestd = d; best = t; }
                }
            if (best && attempt([&] { return ab.use(*best); })) {
                moved = true;
                pos = *best;
            }
        }
    }
    if (me.can_move()) {
        std::vector<vec2> steps;
        attempt([&] {
            steps = s.df.next_moves_from(pos);
            return true;
        });
        for (auto d : steps)
            if (attempt([&] { return me.move(d); })) { moved = true; break; }
        if (!moved && !steps.empty()) moved = fallback();
        if (steps.empty() && !moved) moved = fallback();
        if (P_UNJAM && !moved && me.can_move()) {  // still stuck: any free tile that is not farther
            int here = s.df.get(pos);
            for (int dx = -1; dx <= 1 && !moved; ++dx)
                for (int dy = -1; dy <= 1 && !moved; ++dy) {
                    if (!dx && !dy) continue;
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    if (s.df.get(t) > here + 1) continue;
                    moved = attempt([&] { return me.move_absolute(t); });
                }
        }
    }
    return moved;
}

bool flee(State& s, bc::champion& me) { return step_towards(s, me, s.my_spawn, true); }

// ---------------------------------------------------------------------------
// Combat helpers
// ---------------------------------------------------------------------------
// U34_UNDERLYING_HOOKS: fresh SDK visibility after our own actions.
// A visible handle collected earlier can become hidden or die after a cast,
// attack, knockback or our move. A dead record may remain visible, so health
// must also be positive. is_visible handles hidden/not-found normally.
template <class U>
bool u34_target_visible(const U& target) {
    return attempt([&] { return target.is_visible() && target.health() > 0; });
}

vec2 aoe_centre(State& s, bc::champion& me, int k, vec2 tp, int* hits = nullptr);  // P_AOE, defined below

// P_CAMPHOLD (2026-10-17, user: no spells on a camp while an enemy champion is in reach): with an enemy champion
// within P_CAMPHOLD tiles this round, damage spells and the attack reset are kept for champions. 10 v53 games
// online: 114 of 808 spells on camps were cast with a foe within 6; Stellar emptied three on a camp at
// pilgrimage r481-491 with Ren and Varg at 6 tiles.
#ifndef P_CAMPHOLD
#define P_CAMPHOLD 0
#endif
#ifndef P_TRIBSAFE
#define P_TRIBSAFE 0
#endif
inline bool camp_hold(const State& s, bool champ) {
    return P_CAMPHOLD && !champ && s.nf_r == static_cast<int>(bc::round_number()) && s.nf_d <= P_CAMPHOLD;
}

template <class U>
bool cast_offense(State& s, bc::champion& me, const U& tgt, vec2 tpos, bool champ) {
    if (!me.can_cast() || dist(me.position(), tpos) > SPELL_RANGE) return false;
    if (camp_hold(s, champ)) return false;
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        auto& ab = abs[k];
        // P_SAVECC: keep stuns for champions while enemies were seen in the last P_SAVECC rounds.
        if (P_SAVECC && !champ && s.foe_r > -1000 && static_cast<int>(bc::round_number()) - s.foe_r <= P_SAVECC &&
            attempt([&] { return ab.is_cc(); }))
            continue;
        if (s.slots[k] == Slot::Targeted) {
            if (!(champ ? ab.can_target_enemies() : ab.can_target_camps())) continue;
            if (ab.is_ready() && attempt([&] { return ab.use(tgt); })) return true;
        } else if (s.slots[k] == Slot::Ground) {
            if (!ab.is_ready()) continue;
            vec2 c = tpos;
            if (P_AOE && champ) c = aoe_centre(s, me, k, tpos);
            if (attempt([&] { return ab.use(c); })) return true;
        }
    }
    return false;
}

template <class U>
bool basic_attack(State& s, bc::champion& me, const U& tgt, vec2 tpos) {
    if (dist(me.position(), tpos) > me.attack_range() || !me.can_attack()) return false;
    if (P_U34_ATTACK_LIVE && !u34_target_visible(tgt)) return false;
    bool hit = attempt([&] {
        me.attack(tgt);
        return true;
    });
    // Preserve a reset cooldown when its only selected target disappeared.
    if (hit && s.reset_slot >= 0 && me.can_cast() && !camp_hold(s, std::is_same_v<U, bc::champion>) &&
        // P_U34_RESET_LIVE 1: only on corners/interlock, spend the reset only if the target is still alive and
        // visible after the first hit; 2: the same check on every map (a dead target wastes the reset).
        (!(P_U34_RESET_LIVE >= 2 || (P_U34_RESET_LIVE && (s.de_map == v34de::Corners || s.de_map == v34de::Interlock))) ||
         u34_target_visible(tgt))) {
        auto ab = me.abilities()[s.reset_slot];
        if (ab.is_ready() && attempt([&] { return ab.use(); }))
            attempt([&] {
                me.attack(tgt);
                return true;
            });
    }
    return hit;
}

bool g_ally_near_tgt = false;
// Full engage on one target: spell, attack, close distance, attack again.
template <class U>
bool engage(State& s, bc::champion& me, const U& tgt, vec2 tpos, bool champ, bool dash) {
    FP_SCOPE(17, "engage");
    int d = dist(me.position(), tpos);
    int range = me.attack_range();
    bool acted = false;
    // Keep the exact action order; report whether any action really succeeded.
    if (d <= (s.melee ? range + 1 : 3)) acted = cast_offense(s, me, tgt, tpos, champ);
    if (basic_attack(s, me, tgt, tpos)) return true;
    if (dist(me.position(), tpos) > range) {
        bc::bitboard ring;
        ring.draw_chebyshev(tpos, static_cast<float>(range));
        acted = step_towards(s, me, ring, dash && (!P_NODASHIN || d <= 3 || g_ally_near_tgt)) || acted;
        acted = basic_attack(s, me, tgt, tpos) || acted;
    }
    return acted;
}

void support_spells(State& s, bc::champion& me, bool in_combat) {
    if (!me.can_cast()) return;
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        auto& ab = abs[k];
        if (s.slots[k] == Slot::Shield && in_combat && me.health() < 0.85f * me.max_health()) {
            if (ab.is_ready() && attempt([&] { return ab.use(); })) return;
        }
        if (s.slots[k] == Slot::Heal && ab.is_ready()) {
            for (auto& a : bc::vision::champions(*s.my)) {
                if (a == me) continue;
                bool done = attempt([&] {
                    if (!a.is_alive() || dist(a.position(), me.position()) > SPELL_RANGE) return false;
                    if (ab.heal_amount(a) < 0.5f * ab.heal_amount()) return false;
                    return ab.use(a);
                });
                if (done) return;
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Objectives
// ---------------------------------------------------------------------------
// Shared memory (8 bytes): bytes 0..4 = claim per ally index (group+1, 0 = none);
// bytes 5/6 = "group (byte5-1) respawns at round byte6*8", written by whoever saw it.
constexpr int SM_CLAIMS = 5;
constexpr int SM_BC_GROUP = 5, SM_BC_READY = 6;

#ifndef P_D5_PACKED_CLAIMS
#define P_D5_PACKED_CLAIMS 0
#endif

inline bool packed_claims(const State& s) {
    return P_D5_PACKED_CLAIMS && s.roster == 6 && s.groups.size() <= 63;
}
inline int claim_slots(const State& s) { return packed_claims(s) ? 6 : SM_CLAIMS; }

// Encoded claim value:0=none,1..63=group+1. No cooldown/danger byte is read.
inline std::uint8_t claim_value(const State& s, const std::array<std::uint8_t, 8>& sm, int body) {
    if (body < 0 || body >= claim_slots(s)) return 0;
    if (!packed_claims(s)) return sm[body];
    const int bit = body * 6, byte = bit / 8, shift = bit % 8;
    const unsigned word = static_cast<unsigned>(sm[byte]) | (static_cast<unsigned>(sm[byte + 1]) << 8);
    return static_cast<std::uint8_t>((word >> shift) & 63u);
}

std::array<std::uint8_t, 8> read_sm() {
    std::array<std::byte, 8> raw{};
    attempt([&] {
        bc::shared_memory.read(0, std::span<std::byte>(raw.data(), raw.size()));
        return true;
    });
    std::array<std::uint8_t, 8> out{};
    for (int i = 0; i < 8; ++i) out[i] = std::to_integer<std::uint8_t>(raw[i]);
    return out;
}

void write_sm(std::size_t off, std::uint8_t v) {
    std::byte b = static_cast<std::byte>(v);
    attempt([&] {
        bc::shared_memory.write(off, std::span<const std::byte>(&b, 1));
        return true;
    });
}

void write_claim(State& s, int group) {
    if (s.ally_idx < 0 || s.ally_idx >= claim_slots(s)) return;
    if (!packed_claims(s)) {
        write_sm(static_cast<std::size_t>(s.ally_idx), static_cast<std::uint8_t>(group + 1));
        return;
    }
    if (group < -1 || group >= static_cast<int>(s.groups.size())) return;
    // Complete this short read/modify/write before the existing fuel reserve.
    // One5-byte host write preserves the other claims and every byte5..7.
    if (!fuel_ok(2000)) return;
    std::array<std::byte, 5> raw{};
    if (!attempt([&] {
            bc::shared_memory.read(0, std::span<std::byte>(raw.data(), raw.size()));
            return true;
        })) return;
    std::uint64_t word = 0;
    for (int i = 0; i < 5; ++i)
        word |= static_cast<std::uint64_t>(std::to_integer<std::uint8_t>(raw[i])) << (i * 8);
    const int shift = s.ally_idx * 6;
    const std::uint64_t mask = std::uint64_t{63} << shift;
    word = (word & ~mask) | (static_cast<std::uint64_t>(group + 1) << shift);
    for (int i = 0; i < 5; ++i) raw[i] = static_cast<std::byte>((word >> (i * 8)) & 255u);
    attempt([&] {
        bc::shared_memory.write(0, std::span<const std::byte>(raw.data(), raw.size()));
        return true;
    });
}

int count_claimers(const State& s, const std::array<std::uint8_t, 8>& sm, int group) {
    int n = 0;
    for (int k = 0; k < claim_slots(s); ++k)
        if (k != s.ally_idx && claim_value(s, sm, k) == group + 1) ++n;
    return n;
}

// P_DPSFARM: which allies are tanks (anyone but Stellar, the casters and Ren), learned once.
inline int cap_rank(const std::string& n, bool ranged);
int tank_bits(State& s) {
    if (s.tank_bits >= 0) return s.tank_bits;
    int bits = 0;
    bool ok = attempt([&] {
        auto allies = my_roster(s);
        for (int k = 0; k < static_cast<int>(allies.size()) && k < 16; ++k) {
            std::string n = norm(bc::to_string(allies[k].champion_name()));
            bool ranged = !(starts_with(n, "issac") || starts_with(n, "vend") || starts_with(n, "varg") ||
                            starts_with(n, "ren") || starts_with(n, "marcella") || starts_with(n, "vesper"));
            if (cap_rank(n, ranged) == 3) bits |= 1 << k;
        }
        return true;
    });
    if (ok) s.tank_bits = bits;
    return bits;
}
inline bool i_am_tank(State& s) { return PR.dpsfarm && s.ally_idx >= 0 && ((tank_bits(s) >> s.ally_idx) & 1); }

void broadcast_cooldown(int group, int ready_round) {
    if (group < 0 || group > 250) return;
    write_sm(SM_BC_GROUP, static_cast<std::uint8_t>(group + 1));
    write_sm(SM_BC_READY, static_cast<std::uint8_t>(std::clamp(ready_round / 8 + 1, 1, 250)));
}

// Learn what allies broadcast and what we can see of each group's lifecycle
// (alive / reward available / respawning with a timer).
// Camps of the live groups around us, through the group handles (cheap) instead of the
// vision scan (very expensive). Only camps whose spawn area is in view are returned, so the
// callers' health() queries do not throw.
std::vector<bc::camp> near_camps(State& s, vec2 pos, bool* complete = nullptr) {
    if (complete) *complete=true;
    // Cheap replacement for bc::vision::camps(): only groups near us, and only camps the
    // engine says are in vision (is_visible() reports hidden camps without throwing).
    std::vector<bc::camp> out;
    bc::bitboard tv;  // the engine's own "effective vision", the one state() checks
    if (!attempt([&] { bc::vision::visible_tiles_into(tv); return true; })) {
        if (complete) *complete=false;
        return out;
    }
    for (auto& g : s.groups) {
        if (!g.obj || dist(g.center, pos) > P_LEAN_RADIUS) continue;
        bool seen = false;  // the engine refuses group queries when no camp spawn tile is in vision
        for (auto& c : g.obj->camps())
            if (tv.is_set(c.spawn_position())) { seen = true; break; }
        if (!seen) continue;
        if (g.next_ok > 0 && g.reward_seen < 0) {  // refresh_groups saw it respawning this turn
            bool resp = false;
            attempt([&] {
                resp = std::holds_alternative<bc::map::camp_group_respawning>(g.obj->state());
                return true;
            });
            if (resp) continue;
        }
        const bool known=attempt([&] {
            for (auto& c : g.obj->camps())
                if (c.is_visible()) out.push_back(c);
            return true;
        });
        if (!known && complete) *complete=false;
    }
    return out;
}

// P_CAPPRIO: capture priority by champion (lower first): Stellar, casters, Ren, tanks.
inline int cap_rank(const std::string& n, bool ranged) {
    if (starts_with(n, "stellar")) return 0;
    if (ranged) return 1;
    if (starts_with(n, "ren")) return 2;
    return 3;
}
void refresh_groups(State& s, int round) {
    auto sm = read_sm();
    int bg = static_cast<int>(sm[SM_BC_GROUP]) - 1;
    if (PR.cache && bg >= 0 && bg < static_cast<int>(s.groups.size()) && sm[SM_BC_READY] >= 251) {
        int stamp = sm[SM_BC_READY] - 251, now = (round / 16) & 3;
        Group& g = s.groups[bg];
        if ((stamp == now || stamp == ((now + 3) & 3)) && g.reward_seen < round - 1 && g.next_ok <= round &&
            cap_rank(s.name, s.ranged_me) <= 2) {
            g.reward_seen = round - 1;  // a free reward for choose_target (posted by a tank)
            g.next_ok = 0;
        }
        bg = -1;
    }
    if (bg >= 0 && bg < static_cast<int>(s.groups.size())) {
        int ready = static_cast<int>(sm[SM_BC_READY]) * 8;
        if (ready > round) s.groups[bg].next_ok = std::max(s.groups[bg].next_ok, ready);
    }
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (!g.obj) continue;
        bool visible = false;
        for (auto t : g.tiles)
            if (s.vis.is_set(t)) { visible = true; break; }
        if (!visible) continue;
        attempt([&] {
            auto st = g.obj->state();
            if (std::holds_alternative<bc::map::camp_group_respawning>(st)) {
                int timer = std::get<bc::map::camp_group_respawning>(st).timer;
                int ready = round + std::max(1, timer) + 1;
                if (P_MAPPLAN && P_MP_CHAINPLAN && g.reward_seen >= round - 3 && g.gems > 0 && dist(s.self_pos, g.center) <= 6) { s.mp_last_g = i; s.mp_last_r = round; }  // rule 9: captured next to us
                if (ready > g.next_ok + 4) broadcast_cooldown(i, ready);
                g.next_ok = std::max(g.next_ok, ready);
                g.reward_seen = -1;
            } else if (std::holds_alternative<bc::map::camp_group_reward_available>(st)) {
                g.next_ok = 0;
                g.reward_seen = round;
            } else {
                g.next_ok = 0;
                g.reward_seen = -1;
            }
            return true;
        });
    }
}

double my_dps(State& s, bc::champion& me) {
    double d = me.strength() * (s.reset_slot >= 0 ? 1.125 : 1.0);
    if (s.slots[0] == Slot::Targeted || s.slots[0] == Slot::Ground || s.slots[1] == Slot::Targeted ||
        s.slots[1] == Slot::Ground)
        d += me.focus() * 1.5 / 8.0;
    if (starts_with(s.name, "varg")) d *= 1.5;  // splash
    return std::max(d, 10.0);
}

// Smallest squad that can clear `hp_g` health of `str_g` total strength when each
// member deals `dps` and can afford to lose `afford` health: with n members the
// fight lasts hp_g/(dps*n) rounds and each takes str_g/n per round.
// P_MP_FOCUS S (mapplan, rule 4): camps with strength S+ (elks) focus one champion, so it takes the whole fight's damage:
// hp*str/(dps*n) must fit in one body, not hp*str/(dps*n*n). 0 = the old model everywhere.
#ifndef P_MP_FOCUS
#define P_MP_FOCUS 0
#endif
int squad_needed(double hp_g, double str_g, double dps, double afford) {
    if (str_g <= 0) return 1;
    const bool focus = P_MAPPLAN && P_MP_FOCUS && str_g >= P_MP_FOCUS && (!P_MP_FOCUS_FAR || g_mp_far);
    for (int n = 1; n <= 5; ++n)
        if (hp_g * str_g / (dps * n * (focus ? 1 : n)) <= afford) return n;
    return 6;
}

int allies_near(State& s, bc::champion& me, vec2 at, int radius) {
    int n = 0;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my))
            if (!(a == me) && a.is_alive() && dist(a.position(), at) <= radius) ++n;
        return true;
    });
    return n;
}

// Score every group by gems per round of champion time, counting the health it
// costs us as the recall trip needed to get that health back.
// Hit back while running: after the move, attack the weakest enemy champion still in reach.
void shoot_back(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    if (!P_SHOOT) return;
    vec2 pos = me.position();
    const Foe* best = nullptr;
    for (auto& f : foes) {
        if (f.hp <= 0 || dist(pos, f.p) > me.attack_range()) continue;
        if (!best || f.hp < best->hp) best = &f;
    }
    if (!best) return;
    if (P_SHOOT >= 2) cast_offense(s, me, best->c, best->p, true);
    basic_attack(s, me, best->c, best->p);
}

// Danger spot: an enemy pack (P_DANGER+ champions within 4 of each other) seen this turn, or
// one an ally reported in byte 7 (nearest altar index + 1, then round / 8, mod 32).
void update_danger(State& s, const std::vector<Foe>& foes, int round) {
    for (auto& f : foes) {
        if (s.en_spawn.is_set(f.p)) continue;
        int n = 0;
        for (auto& o : foes)
            if (dist(o.p, f.p) <= 4) ++n;
        if (n >= P_DANGER) {
            s.danger_p = f.p;
            s.danger_r = round;
            break;
        }
    }
    if (P_CALLHELP || P_PVKITE) return;  // byte 7 belongs to the help call then
    if (s.danger_r == round) {
        int ai = -1, ad = P_DANGER_R + 1;
        for (std::size_t i = 0; i < s.altars.size() && i < 7; ++i)
            if (dist(s.altars[i], s.danger_p) < ad) { ad = dist(s.altars[i], s.danger_p); ai = static_cast<int>(i); }
        if (ai >= 0) write_sm(7, static_cast<std::uint8_t>((ai + 1) | (((round / 8) & 31) << 3)));
        return;
    }
    int b = read_sm()[7];
    int ai = (b & 7) - 1, age = ((round / 8) - (b >> 3)) & 31;
    if (ai < 0 || ai >= static_cast<int>(s.altars.size()) || age * 8 > P_DANGER_T) return;
    int r = round - age * 8;
    if (r > s.danger_r) {
        s.danger_p = s.altars[ai];
        s.danger_r = r;
    }
}

bool grouped(const State& s, int round) { return P_GROUP && P_DANGER && s.danger_r > -1000 && round - s.danger_r <= P_GROUP; }
bool ball_on(const State& s, int round) { return (P_BALL && s.casters) || grouped(s, round); }

int choose_target_impl(State& s, bc::champion& me, int round);
// P_FUELGUARD: the dearest choose_target seen so far (it grows with the number of camp groups and with walls),
// so a caller can skip an optional re-choice when the turn could not pay for it plus a step afterwards.
int choose_target(State& s, bc::champion& me, int round) {
    if (!P_FUELGUARD) return choose_target_impl(s, me, round);
    std::uint64_t f0 = bc::fuel_remaining();
    int t = choose_target_impl(s, me, round);
    std::uint64_t f1 = bc::fuel_remaining();
    if (f0 > f1) s.ct_cost = std::max<std::uint64_t>(s.ct_cost, f0 - f1);
    return t;
}
bool can_choose(const State& s) { return !P_FUELGUARD || fuel_ok(s.ct_cost + 12000); }

int choose_target_impl(State& s, bc::champion& me, int round) {
    FP_SCOPE(15, "choose_target");
    auto sm = read_sm();
    vec2 pos = me.position();
    double hp = me.health();
    double mhp = std::max(1.0, static_cast<double>(me.max_health()));
    double dps = my_dps(s, me);
    double gold_w = (round < 600 ? P_GOLD_W_EARLY : P_GOLD_W_LATE) / 100.0;
    int best = -1;
    double best_score = 0;
    int lead_group = -1;
    std::optional<vec2> lead_p;
    if (ball_on(s, round) && s.ally_idx > 0)
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < s.ally_idx && k < static_cast<int>(allies.size()); ++k) {
                if (!allies[k].is_alive()) continue;
                if (k < claim_slots(s)) {
                    const int claim = claim_value(s, sm, k);
                    if (claim > 0) lead_group = claim - 1;
                }
                try { lead_p = allies[k].position(); } catch (...) {}
                break;
            }
            return true;
        });
    bool cached = P_FUELGUARD && P_PATHD && s.pd_pos == pos && s.pd_gd.size() == s.groups.size();
    bool have_pd = cached || (P_PATHD && attempt([&] {  // walking distance from here to every camp group
        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;
    }));
    if (P_FUELGUARD && P_PATHD && have_pd && !cached) {  // the walking distance to each group, read once per tile
        s.pd_gd.assign(s.groups.size(), -1);
        attempt([&] {
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 1 << 20;
                for (auto t : s.groups[i].tiles)
                    if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
                s.pd_gd[i] = b < (1 << 20) ? b : -1;
            }
            s.pd_pos = pos;
            return true;
        });
    }
    auto walk = [&](const Group& g) {
        int d = dist(pos, g.center);
        if (!have_pd) return d;
        if (P_FUELGUARD && s.pd_pos == pos && s.pd_gd.size() == s.groups.size()) {
            int b = s.pd_gd[static_cast<std::size_t>(&g - s.groups.data())];
            return b >= 0 ? b : d * 3 / 2;
        }
        int b = 1 << 20;
        for (auto t : g.tiles)
            if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
        return b < (1 << 20) ? b : d * 3 / 2;
    };
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;
        bool held = P_HOLD && s.hold_group[i];
        if (!held && P_DANGER && round - s.danger_r <= P_DANGER_T && dist(g.center, s.danger_p) <= P_DANGER_R) continue;
        int wait = g.next_ok - round;  // > 0: respawning
        int gd = walk(g);
        const bool jack_go = P_JACKGO && g.jackpot && round >= P_JACKGO;
        if (wait > 0 && !(jack_go && wait <= gd + 40) && (!P_RESPAWN || g.monolith || wait > gd + P_RESPAWN)) continue;
        if (g.gems + g.gold <= 0) continue;
        if (P_JACKPOT && g.jackpot && round < P_JACKPOT) continue;  // farm gold and buy first, as the top teams do (stampede: first visit r350-475)
        if (P_NOGOLD && g.gems <= 0 && !s.mono_only && !s.jackpot_map) continue;  // gold-only clusters give no gems (but gold is the tiebreak where only monoliths give gems)
        int claimers = count_claimers(s, sm, i);
        if (PR.dpsfarm && !i_am_tank(s))
            for (int k = 0; k < claim_slots(s); ++k)
                if (k != s.ally_idx && ((tank_bits(s) >> k) & 1) && claim_value(s, sm, k) == i + 1) --claimers;
        bool free_reward = g.reward_seen >= 0 && round - g.reward_seen < 30;
        double afford = std::max(1.0, mhp * (1.0 - P_RESERVE_PCT / 100.0));
        int needed = free_reward ? 1 : squad_needed(g.hp, g.str, dps, afford);
        bool mono_go = s.mono_only && g.monolith;  // its damage stays, so the team wears it down over several trips
        if (mono_go) needed = std::min(needed, s.roster);
        const int jack_n = std::max(1, std::min(P_JACKN, s.roster));
        if (jack_go) needed = std::min(needed, jack_n);
        if (needed > s.roster) continue;  // not with this team, not with these stats
        int cap = g.str > 0 ? std::max(needed, P_MAX_SHARE) : 1;
        if (g.str > 0 && mp_spread(s)) cap = needed;  // mapplan_game.h rule 7: no stacking past what the camp needs
        if (mono_go) cap = free_reward ? 1 : s.roster;
        if (jack_go) cap = jack_n;
        if (P_PAIR && g.str <= 0 && g.gems > 0) cap = P_PAIR;  // gem clusters: a pair kills twice as fast
        bool pot = P_POT && i < static_cast<int>(s.pot_group.size()) && s.pot_group[i];
        if (pot) cap = std::max(cap, 2);
        if (P_R34_SHARE && (s.de_map == v34de::Monolith) && !free_reward) cap = std::min(cap, std::max(needed, P_R34_SHARE));
        if (P_ONE_CAP && free_reward) cap = 1;
        if (P_PACKOPEN && round < P_PACKOPEN) cap = std::max(cap, s.roster);
        if (claimers >= cap && i != s.target && !lead) continue;
        int team = std::max(1 + claimers, needed);
        double t_clear = free_reward ? 0.0 : g.hp / (dps * team);
        double incoming = g.str * t_clear / team;
        double travel = std::max(gd, wait);
        double cycle = 8.0 + (P_PATHD && g.spawn_pd >= 0 ? g.spawn_pd : dist(s.spawn_center, g.center));  // recall + heal + walk back
        double rounds = travel + t_clear + 6.0 + (incoming / mhp) * cycle;
        if (P_BANKW && g.gems > 0 && g.altar_pd >= 0) rounds += P_BANKW / 100.0 * 2.0 * g.altar_pd / team;  // the bag's trip to an altar
        if (P_R34_BANKCOST && (s.de_map == v34de::Expanse || s.de_map == v34de::Monolith) && g.gems > 0 && g.altar_pd >= 0)
            rounds += ((s.de_map == v34de::Monolith ? 100 : P_R34_BANKCOST) / 100.0) * 2.0 * std::max(0, g.altar_pd - 1) / team;
        bool pack = P_PACKOPEN && round < P_PACKOPEN;  // opening: everybody on the best camp together
        double value = (g.gems + gold_w * g.gold) / (pack ? 1.0 : std::pow(static_cast<double>(team), ((g.monolith || g.hp < P_STACK_HP || mp_spread(s)) ? 100 : P_SHAREEXP) / 100.0));  // big camps (P_STACK_HP+): a joiner keeps more of the value, so champions stack there
        double score = value / std::max(1.0, rounds);
        if (needed > 1 + claimers) score *= (mp_far_trip(s, gd) && P_MP_COMPANY) ? P_MP_COMPANY / 100.0 : 0.7;  // still needs company (rule 8)
        if (claimers > 0 && g.str == 0 && !(P_PAIR && g.gems > 0 && claimers < P_PAIR) && !(pot && claimers < 2)) score *= pack ? 1.0 : 0.3;  // clusters are a solo job
        if (pot) score *= P_POT / 100.0;  // the centre pot pays 48 a pair next to the altar
        if (dist(g.center, s.en_center) < 8) score *= 0.6;    // stay off their doorstep
        if (P_HALF && !(mp_spread(s) && P_MP_HALFOFF) && dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6) score *= P_HALF / 100.0;
        if (held) score *= P_HOLD / 100.0;
        if (lead) score *= (P_BALL && s.casters) ? P_BALL : P_GROUP_W;
        else if (lead_p && dist(g.center, *lead_p) > 8) score *= 0.3;
        if (mp_chain_next(s, me, g, i, round)) score *= P_MP_CHAINPLAN / 100.0;  // rule 9: the squad moves on to the next camp
        if (i == s.target) score *= (P_MAPPLAN && P_MP_STICK && gd >= P_MP_STICK_D) ? P_MP_STICK / 100.0 : P_STICK / 100.0;  // hysteresis (mapplan_game.h rule 6)
        if (jack_go) score *= P_JACKW;
#ifdef P_DBGT
        if (round >= P_DBGT && round < P_DBGT + P_DBGT_LEN) std::printf("[dbgt] r%d %s g%d gems=%d gold=%d d=%d need=%d cl=%d wait=%d score=%.3f\n", round, s.name.c_str(), i, g.gems, g.gold, dist(pos, g.center), needed, claimers, wait, score);
#endif
        if (score > best_score) { best_score = score; best = i; }
    }
    return best;
}

std::optional<vec2> br_legacy_best_altar(State& s, vec2 pos, int round) {
    std::optional<vec2> best;
    int bestd = 1 << 30;
    for (std::size_t i = 0; i < s.altars.size(); ++i) {
        vec2 a = s.altars[i];
        if (!s.altar_ok[i]) continue;
        if (s.vis.is_set(a)) {  // refresh what we know about enemy locks
            bool locked = attempt([&] {
                return bc::vision::has_altar_lock(a) && bc::vision::altar_lock_at(a).is_enemy();
            });
            s.lock_until[i] = locked ? round + 40 : 0;
        }
        int d = dist(a, pos);
        if (s.lock_until[i] > round) d += 40;
        if (P_ALTAR_SAFE && s.vis.is_set(a))  // an enemy champion next to the altar: prefer another one
            attempt([&] {
                for (auto& e : bc::vision::champions(*s.en))
                    if (e.is_alive() && dist(e.position(), a) <= 3) { d += P_ALTAR_SAFE; break; }
                return true;
            });
        if (P_OWN_ALTAR && static_cast<int>(i) != s.hold && dist(a, s.spawn_center) - dist(a, s.en_center) > 3) d += P_OWN_ALTAR;
        if (P_DANGER && static_cast<int>(i) != s.hold && round - s.danger_r <= P_DANGER_T && dist(a, s.danger_p) <= P_DANGER_R) d += 60;
        if (d < bestd) { bestd = d; best = a; }
    }
    return best;
}
// BR_BANKING_ROUTING: native walking-to-approach distance, not line distance.
constexpr int br_policy = 1;

int br_ring_distance(const bc::distance_field& field, const bc::bitboard& reached,
                     const bc::bitboard& block, vec2 altar) {
    int best = 1 << 30;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 p = altar + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || block.is_set(p) || !reached.is_set(p)) continue;
            best = std::min(best, static_cast<int>(field.get(p)));
        }
    // +1 preserves the old altar-centre distance thresholds on an open map.
    return best < (1 << 30) ? best + 1 : -1;
}

int br_altar_penalty(State& s, vec2 a, int i, int round) {
    int cost = s.lock_until[i] > round ? 40 : 0;
    cost += draftplan::altar_penalty(a);
    if (P_ALTAR_SAFE && s.vis.is_set(a))
        attempt([&] {
            for (auto& e : bc::vision::champions(*s.en))
                if (e.is_alive() && dist(e.position(), a) <= 3) { cost += P_ALTAR_SAFE; break; }
            return true;
        });
    if (P_OWN_ALTAR && i != s.hold && dist(a, s.spawn_center) - dist(a, s.en_center) > 3) cost += P_OWN_ALTAR;
    if (P_DANGER && i != s.hold && round - s.danger_r <= P_DANGER_T && dist(a, s.danger_p) <= P_DANGER_R) cost += 60;
    return cost;
}

bool br_better(bool safe, int cost, int home, int index,
               bool old_safe, int old_cost, int old_home, int old_index) {
    if (old_index < 0) return true;
    if (br_policy == 2 && safe != old_safe) return safe;
    if (cost != old_cost) return cost < old_cost;
    if (home != old_home) return home < old_home;
    return index < old_index;
}

bool br_threat_block(State& s, vec2 pos, int round, bc::bitboard& block) {
    block = s.blocked;
    auto enemies = bc::vision::champions(*s.en);
    if (enemies.size() > 16) return false;
    for (auto& enemy : enemies) {
        if (!fuel_ok(26000)) return false;
        bool ok = attempt([&] {
            if (!enemy.is_alive()) return true;
            vec2 p = enemy.position();
            int radius = std::max(3, static_cast<int>(enemy.attack_range()) + 1);
            bool fresh = false;
            if (s.thr_r == round)
                for (const auto& threat : s.thr)
                    if (threat.p == p) {
                        radius = std::max(radius, std::max(threat.ar, std::max(threat.xr, std::max(threat.fr + 1, threat.sr + 1))));
                        fresh = true;
                        break;
                    }
            // Outside the existing fresh snapshot, reserve the generic spell
            // envelope; do not query hidden units or assume walls stop spells.
            if (!fresh) radius = std::max(radius, SPELL_RANGE + 1);
            bc::bitboard danger;
            danger.draw_chebyshev(p, static_cast<float>(radius));
            block |= danger;
            return true;
        });
        if (!ok) return false;
    }
    // A champion already in danger may escape; an adjacent altar can still be
    // used immediately. This does not mark its other threatened tiles safe.
    block.set(pos, false);
    return true;
}

bool br_plan(State& s, vec2 pos, int round) {
    if (!fuel_ok(50000) || s.altars.size() > 64) { s.br_reason = 1; return false; }
    return attempt([&] {
        bc::bitboard block = s.blocked, roots, reached;
        block.set(pos, false);
        roots.set(pos);
        bc::distance_field field;
        field.compute(block, roots, reached, 400);
        std::vector<int> ordinary(s.altars.size(), -1), safe(s.altars.size(), -1);
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (!fuel_ok(22000)) { s.br_reason = 1; return false; }
            if (s.altar_ok[i]) ordinary[i] = br_ring_distance(field, reached, block, s.altars[i]);
        }
        if (br_policy == 2) {
            if (!br_threat_block(s, pos, round, s.br_risk_block)) { s.br_reason = 2; return false; }
            bc::distance_field safe_field;
            bc::bitboard safe_reached;
            safe_field.compute(s.br_risk_block, roots, safe_reached, 400);
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                if (!fuel_ok(22000)) { s.br_reason = 1; return false; }
                if (ordinary[i] >= 0) safe[i] = br_ring_distance(safe_field, safe_reached, s.br_risk_block, s.altars[i]);
            }
        }
        int best = -1, best_cost = 1 << 30, best_home = 1 << 30;
        bool best_safe = false;
        s.br_lengths = ordinary;
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (ordinary[i] < 0) continue;
            const bool route_safe = br_policy == 2 && safe[i] >= 0;
            const int length = route_safe ? safe[i] : ordinary[i];
            const int cost = length + br_altar_penalty(s, s.altars[i], static_cast<int>(i), round);
            const int home = dist(s.altars[i], s.spawn_center);
            if (br_better(route_safe, cost, home, static_cast<int>(i), best_safe, best_cost, best_home, best)) {
                best = static_cast<int>(i); best_cost = cost; best_home = home; best_safe = route_safe;
            }
            if (route_safe) s.br_lengths[i] = safe[i];
        }
        if (best < 0) { s.br_reason = 3; return false; }
        s.br_choice = best;
        s.br_safe_route = best_safe;
        s.br_reason = br_policy == 2 && !best_safe ? 4 : 0;
        return true;
    });
}

std::optional<vec2> best_altar(State& s, vec2 pos, int round) {
    FP_SCOPE(18, "best_altar");
    if (s.br_round != round || !(s.br_pos == pos)) {
        s.br_round = round; s.br_pos = pos; s.br_choice = -1;
        s.br_safe_route = false; s.br_reason = 0;
        s.br_lengths.assign(s.altars.size(), -1);
        auto fallback = br_legacy_best_altar(s, pos, round); // preserves lock refresh
        if (!br_plan(s, pos, round)) {
            if (!s.br_reason) s.br_reason = 2; // SDK failure, not a safety claim
            s.br_lengths.assign(s.altars.size(), -1);
            if (fallback)
                for (std::size_t i = 0; i < s.altars.size(); ++i)
                    if (s.altars[i] == *fallback) { s.br_choice = static_cast<int>(i); break; }
        }
    }
    if (s.br_choice < 0) return std::nullopt;
    return s.altars[s.br_choice];
}

int br_altar_distance(State& s, vec2 altar, vec2 pos, int round) {
    FP_SCOPE(19, "br_altar_dist");
    best_altar(s, pos, round);
    for (std::size_t i = 0; i < s.altars.size(); ++i)
        if (s.altars[i] == altar && s.br_lengths[i] >= 0) return s.br_lengths[i];
    return dist(altar, pos); // explicit legacy/fuel fallback
}

bool br_safe_move(State& s, bc::champion& me, vec2 altar) {
    vec2 pos = me.position();
    bc::bitboard goals, dest, reached;
    goals.draw_chebyshev(altar, 1.0f);
    goals &= ~s.br_risk_block;
    if (goals.is_empty()) return false;
    dest.set(pos);
    bc::distance_field field;
    bool valid = attempt([&] {
        field.compute_to(s.br_risk_block, goals, dest, reached, 400);
        return reached.is_set(pos);
    });
    if (!valid) return false; // do not silently discard the risk walls
    bool moved = false;
    if (s.dash_slot >= 0 && me.can_cast()) {
        auto ability = me.abilities()[s.dash_slot];
        const int here = field.get(pos);
        if (here >= 3 && ability.is_ready()) {
            std::optional<vec2> best;
            int bestd = here - 1;
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 p = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(p) || s.br_risk_block.is_set(p) || !reached.is_set(p)) continue;
                    int distance = field.get(p);
                    if (distance < bestd) { best = p; bestd = distance; }
                }
            if (best && attempt([&] { return ability.use(*best); })) { moved = true; pos = me.position(); }
        }
    }
    if (me.can_move())
        for (auto direction : field.next_moves_from(pos))
            if (attempt([&] { return me.move(direction); })) { moved = true; break; }
    return moved;
}

void br_note(State& s, int round, int length, bool used_safe) {
    ++s.br_decisions;
    if (s.br_reason) ++s.br_fallbacks;
    if (used_safe) ++s.br_routes;
    if ((s.br_decisions <= 8 || round % 50 == 0) && s.br_log_round != round) {
        s.br_log_round = round;
        std::printf("[econ] who=%d r=%d br_decisions=%d br_fallbacks=%d br_routes=%d br_stops=%d altar=%d path=%d fallback=%d\n",
                    s.ally_idx, round, s.br_decisions, s.br_fallbacks, s.br_routes, s.br_stops, s.br_choice, length, s.br_reason);
    }
}


// Local channel guard: baseline recall policy plus currently observed exposure.
// It does not project a hypothetical stationary fight over the entire channel.
bool channel_eligible(State& s, bc::champion& me, int round, bool recall) {
    if (!P_DP_CHANNEL_FIX) return true;
    if (static_cast<int>(bc::round_number())!=round || s.ch_round!=round || !s.ch_complete ||
        (recall && !s.ch_camps_complete)) return false;
    const vec2 p=me.position();
    int nearest=99;
    for (auto fp:s.ch_foes) nearest=std::min(nearest,dist(p,fp));
    std::vector<bc::camp> moved_camps;
    const auto* camps=&s.ch_camps;
    bool unknown_near=false;
    if (!(p==s.ch_pos)) {
        // A move may reveal bodies absent from the pre-move snapshot. Only read
        // positions here; never build another ability/stat observer.
        if (!fuel_ok(7000)) return false;
        if (!attempt([&] {
            for (auto c:bc::vision::champions(*s.en)) {
                if (!c.is_alive()) continue;
                const vec2 cp=c.position();
                nearest=std::min(nearest,dist(p,cp));
                bool known=false;
                for (auto fp:s.ch_foes) if (fp==cp) { known=true; break; }
                if (!known && dist(p,cp)<=8) unknown_near=true;
            }
            return true;
        })) return false;
        if (recall) {
            bool complete=true;
            moved_camps=near_camps(s,p,&complete);
            if (!complete) return false;
            camps=&moved_camps;
        }
    }
    if (!recall && P_TRIBSAFE && nearest<=P_TRIBSAFE) return false;
    bool camp_near=false;
    if (recall) for (auto c:*camps) {
        if ((!c.is_wolf() && !c.is_elk() && !c.is_monolith()) || dist(c.spawn_position(),p)>CAMP_RANGE+1) continue;
        if (!fuel_ok(5000)) return false;
        if (!attempt([&] {
            const int range=c.attack_range();
            if (range<=0 || !c.is_awake()) return true;
            const int d=dist(c.position(),p);
            camp_near|=d<=range+1;
            return true;
        })) return false;
    }
    double enemy_damage=0;
    bool control=false;
    if (!s.ch_foes.empty()) {
        if (s.thr_r!=round) return false;
        enemy_damage=danger_at(s.thr,p);
        for (const auto& t:s.thr) if (t.sr>=0 && dist(p,t.p)<=t.sr+1) control=true;
    }
    bool safe=nearest>7;
    if (P_SAFE_RECALL) safe=safe && nearest>8 && round-s.hit_round>2;
    const bool near_safe=s.rnear && nearest>=s.rnear && round-s.hit_round>=1;
    const bool capture=s.target>=0 && s.target<static_cast<int>(s.groups.size()) &&
        s.groups[s.target].reward_seen==round && s.groups[s.target].mask.is_set(p) && nearest>8;
    const bool allowed=channel_safety::local_allowed(recall,safe||near_safe||capture,
        camp_near,enemy_damage,me.health(),control,unknown_near);
    return allowed && static_cast<int>(bc::round_number())==round;
}
bool start_recall(State& s, bc::champion& me, int round) {
    if (P_DP_CHANNEL_FIX && !attempt([&] { return channel_eligible(s,me,round,true); })) return false;
    return attempt([&] {
        if (P_DP_CHANNEL_FIX && static_cast<int>(bc::round_number())!=round) return false;
        const bool was_outside = P_DP_CHANNEL_FIX && !s.my_spawn.is_set(me.position());
        me.recall();
        return !P_DP_CHANNEL_FIX || me.is_recalling() || (was_outside && s.my_spawn.is_set(me.position()));
    });
}
bool start_submission(State& s, bc::champion& me, vec2 altar, int round) {
    if (P_DP_CHANNEL_FIX && !attempt([&] { return channel_eligible(s,me,round,false); })) return false;
    return attempt([&] {
        if (P_DP_CHANNEL_FIX && static_cast<int>(bc::round_number())!=round) return false;
        const auto before = P_DP_CHANNEL_FIX ? me.gem_count() : 0;
        me.submit_gems(altar);
        return !P_DP_CHANNEL_FIX || me.is_submitting_gems() || me.gem_count()<before;
    });
}

bool go_tribute(State& s, bc::champion& me, int round) {
    FP_SCOPE(20, "go_tribute");
    vec2 pos = me.position();
    auto a = best_altar(s, pos, round);
    if (!a) return false;
    const int length = br_altar_distance(s, *a, pos, round);
    // P_TRIBSAFE (2026-10-17, monolith r110-125 vs Nameless: Varg tributed 5 rounds with their Ryth hitting him,
    // 900 -> 420 hp, then lost the trade and died): no tribute starts with an enemy champion within P_TRIBSAFE.
    if (P_TRIBSAFE && dist(pos, *a) <= 1 && s.nf_r == round && s.nf_d <= P_TRIBSAFE) return false;
    if (dist(pos, *a) <= 1) {
        bool acted = start_submission(s, me, *a, round);
        br_note(s, round, length, false);
        return acted;
    }
    bool moved = false, used_safe = false;
    if (br_policy == 2 && s.br_safe_route && fuel_ok(26000)) {
        used_safe = true;
        moved = br_safe_move(s, me, *a);
        if (!moved) ++s.br_stops;
    } else {
        if (br_policy == 2 && s.br_safe_route) s.br_reason = 1;
        bc::bitboard ring;
        ring.draw_chebyshev(*a, 1.0f);
        moved = step_towards(s, me, ring, true);
    }
    bool submitted = false;
    if (dist(me.position(), *a) <= 1 && !(P_TRIBSAFE && s.nf_r == round && s.nf_d <= P_TRIBSAFE))
        submitted = start_submission(s, me, *a, round);
    br_note(s, round, length, used_safe);
    return moved || (P_DP_CHANNEL_FIX && submitted);
}

// Step (and dash) to the reachable neighbour that is farthest from the enemies,
// preferring tiles that also bring us closer to home.
bool retreat(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    vec2 pos = me.position();
    auto score_tile = [&](vec2 t) {
        int nearest = 99;
        for (auto& f : foes) nearest = std::min(nearest, dist(t, f.p));
        return nearest * 10 - dist(t, s.spawn_center);
    };
    bool moved = false;
    if (s.dash_slot >= 0 && me.can_cast()) {
        auto ab = me.abilities()[s.dash_slot];
        if (ab.is_ready()) {
            std::optional<vec2> best;
            int bests = score_tile(pos);
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                    int sc = score_tile(t);
                    if (sc > bests) { bests = sc; best = t; }
                }
            if (best && attempt([&] { return ab.use(*best); })) {
                moved = true;
                pos = me.position();
            }
        }
    }
    if (me.can_move()) {
        std::optional<vec2> best;
        int bests = score_tile(pos);
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                int sc = score_tile(t);
                if (sc > bests) { bests = sc; best = t; }
            }
        if (best && attempt([&] { return me.move_absolute(*best); })) moved = true;
    }
    return moved || flee(s, me);
}

bool slot_exclusive(State& s, bc::champion& me, int k) {
    if (s.excl[k] < 0) {
        s.excl[k] = 0;
        attempt([&] {
            auto inf = me.abilities()[k].info();
            if (!inf) return false;
            std::visit([&](auto& x) {
                if constexpr (requires { x.exclusive_with_movement; }) s.excl[k] = x.exclusive_with_movement ? 1 : 0;
            }, *inf);
            return true;
        });
    }
    return s.excl[k] == 1;
}

// P_AOE: radius, range and damage of our ground area spell in slot k (radius 0 = not an area spell).
struct AoeSlot {
    int radius = -1, range = 0;
    double mod = 0;
};
AoeSlot& aoe_slot(bc::champion& me, int k) {
    static AoeSlot cache[2];
    if (cache[k].radius < 0) {
        cache[k].radius = 0;
        attempt([&] {
            auto inf = me.abilities()[k].info();
            if (!inf) return false;
            std::visit([&](auto& x) {
                using T = std::decay_t<decltype(x)>;
                if constexpr (std::is_same_v<T, bc::ability_aoe_damage>) {
                    cache[k].radius = std::max(1, static_cast<int>(x.radius));
                    cache[k].range = static_cast<int>(x.range);
                    cache[k].mod = x.modifier;
                }
            }, *inf);
            return true;
        });
    }
    return cache[k];
}

// The centre for our area spell in slot k: within its cast range, covering `tp` (the intended target) when
// possible, and the most enemy champion health (a kill counts extra). hits = enemy champions under it.
vec2 aoe_centre(State& s, bc::champion& me, int k, vec2 tp, int* hits) {
    if (hits) *hits = 0;
    AoeSlot& a = aoe_slot(me, k);
    if (a.radius <= 0) return tp;
    double dmg = a.mod;
    attempt([&] {
        dmg = a.mod * me.focus();
        return true;
    });
    std::vector<std::pair<vec2, double>> en;
    attempt([&] {
        for (auto& c : bc::vision::champions(*s.en))
            try {
                if (!c.is_alive() || s.en_spawn.is_set(c.position())) continue;
                en.push_back({c.position(), c.health()});
            } catch (...) {
            }
        return true;
    });
    vec2 pos = me.position();
    int rng = a.range > 0 ? a.range : SPELL_RANGE;
    vec2 best = tp;
    double bs = -1;
    int bh = 0;
    for (int dx = -a.radius; dx <= a.radius; ++dx)
        for (int dy = -a.radius; dy <= a.radius; ++dy) {
            vec2 c = tp + vec2(dx, dy);
            if (!bc::map::is_in_bounds(c) || dist(pos, c) > rng) continue;
            double sc = 0;
            int h = 0;
            for (auto& e : en)
                if (dist(c, e.first) <= a.radius) {
                    ++h;
                    sc += std::min(dmg, e.second) + (dmg >= e.second ? 200.0 : 0.0);
                }
            if (dx == 0 && dy == 0) sc += 0.5;  // ties: the target itself
            if (sc > bs) { bs = sc; best = c; bh = h; }
        }
    if (hits) *hits = bh;
#ifdef P_FXLOG
    std::printf("[aoe] r=%d hits=%d moved=%d\n", static_cast<int>(bc::round_number()), bh, best == tp ? 0 : 1);
#endif
    return best;
}

#include "track.h"
#include "fight.h"
#include "verdict.h"


// ---------------------------------------------------------------------------
// Proven safe match closure: when the missing score is already carried or the
// team is within P_DP_FINISH_NEAR of 1000, carriers prioritise a safe tribute.
// ---------------------------------------------------------------------------
bool dp_finish_bank(State& s, bc::champion& me, const std::vector<Foe>& foes,
                    int round, int gems, float hpr, bool on_spawn) {
    if (!P_DP_FINISH || !s.my || gems <= 0) return false;
    std::uint32_t submitted = 0;
    if (!attempt([&] { submitted = bc::global_submitted_gems(*s.my); return true; })) return false;
    if (submitted >= 1000) return false;
    const int need = 1000 - static_cast<int>(submitted);

    int known_bags = gems;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            if (a == me || !a.is_alive()) continue;
            known_bags += static_cast<int>(a.gem_count());
        }
        return true;
    });
    if (need > P_DP_FINISH_NEAR && known_bags < need && gems < need) return false;

    int nearest = 99;
    for (auto& f : foes) nearest = std::min(nearest, f.d);
    if (on_spawn && hpr < 0.90f) { g_mode = "finish-heal"; return true; }

    if (!on_spawn && hpr * 100 < P_DP_FINISH_RECALL_HP && nearest > 8) {
        g_mode = "finish-recall";
        if (start_recall(s, me, round)) return true;
    }

    const vec2 pos = me.position();
    bc::bitboard risk;
    bool risk_ok = br_threat_block(s, pos, round, risk);
    if (!risk_ok) risk = s.blocked;
    risk.set(pos, false);
    if (P_DANGER && round - s.danger_r <= P_DANGER_T) {
        bc::bitboard old_pack;
        old_pack.draw_chebyshev(s.danger_p, static_cast<float>(P_DANGER_R + 1));
        risk |= old_pack;
        risk.set(pos, false);
    }

    bc::bitboard roots, reached;
    roots.set(pos);
    bc::distance_field field;
    bool path_ok = attempt([&] { field.compute(risk, roots, reached, 400); return true; });
    int best = -1, best_cost = 1 << 29;
    if (path_ok) {
        for (int i = 0; i < static_cast<int>(s.altars.size()); ++i) {
            if (i < static_cast<int>(s.altar_ok.size()) && !s.altar_ok[i]) continue;
            int len = br_ring_distance(field, reached, risk, s.altars[i]);
            if (len < 0) continue;
            int cost = len + draftplan::altar_penalty(s.altars[i]);
            cost += std::max(0, 10 - dist(s.altars[i], s.en_center)) * 6;
            if (P_DANGER && round - s.danger_r <= P_DANGER_T &&
                dist(s.altars[i], s.danger_p) <= P_DANGER_R + 2) cost += 80;
            if (cost < best_cost) { best_cost = cost; best = i; }
        }
    }

    if (best >= 0) {
        const vec2 altar = s.altars[best];
        if (dist(pos, altar) <= 1 && nearest >= 5) {
            g_mode = "finish-submit";
            return start_submission(s, me, altar, round);
        }
        s.br_risk_block = risk;
        g_mode = "finish-safe";
        if (br_safe_move(s, me, altar)) {
            if (dist(me.position(), altar) <= 1) {
                int now_near = 99;
                for (auto& f : foes) now_near = std::min(now_near, dist(me.position(), f.p));
                if (now_near >= 5)
                    start_submission(s, me, altar, round);
            }
            return true;
        }
    }

    if (!foes.empty() && nearest <= 8) {
        g_mode = "finish-avoid";
        fight::back_off(s, me, foes, round);
        return true;
    }
    g_mode = "finish-fallback";
    return go_tribute(s, me, round);
}

bool g_cap_other_on = false;  // P_CAPPRIO: the ally that takes the reward already stands on it

// One capturer per reward: among the allies on the reward or claiming it within 4 tiles,
// the nearest one (lowest index on ties) captures; everybody else leaves.
bool other_captures_impl(State& s, bc::champion& me, const Group& g, int gi);
bool other_captures(State& s, bc::champion& me, const Group& g, int gi) {
    if (!P_OCMEMO) return other_captures_impl(s, me, g, gi);
    const int round = static_cast<int>(bc::round_number());
    vec2 p = me.position();
    if (s.oc_round == round && s.oc_group == gi && s.oc_x == X(p) && s.oc_y == Y(p)) {
        g_cap_other_on = s.oc_on;
        return s.oc_other;
    }
    bool o = other_captures_impl(s, me, g, gi);
    s.oc_round = round; s.oc_group = gi; s.oc_x = X(p); s.oc_y = Y(p);
    s.oc_other = o; s.oc_on = g_cap_other_on;
    return o;
}
bool other_captures_impl(State& s, bc::champion& me, const Group& g, int gi) {
    FP_SCOPE(24, "other_captures");
    auto mask_dist = [&](vec2 p) {
        int d = 99;
        for (auto t : g.tiles) d = std::min(d, dist(p, t));
        return d;
    };
    int mine = mask_dist(me.position());
    auto sm = read_sm();
    bool other = false;
    g_cap_other_on = false;
    if (i_am_tank(s)) return true;  // P_DPSFARM: a tank never takes a reward
    const int my_rank = PR.capprio ? cap_rank(s.name, me.attack_range() > 1) : 0;
    std::vector<bc::champion> seen;  // P_FUELGUARD: allies in vision (position() of any other one throws)
    if (P_FUELGUARD) attempt([&] { seen = bc::vision::champions(*s.my); return true; });
    attempt([&] {
    auto allies = my_roster(s);
    for (std::size_t k = 0; k < allies.size() && !other; ++k) {
        auto& a = allies[k];
        if (P_FUELGUARD && std::find(seen.begin(), seen.end(), a) == seen.end()) continue;
        // One ally per attempt: an ally out of our vision throws on position(), and with a
        // single attempt around the loop that aborted it, so nobody ever left the reward.
        try {
            if (a == me || !a.is_alive()) continue;
            if (PR.dpsfarm && ((tank_bits(s) >> k) & 1)) continue;  // tanks step off, they never capture
            int d = mask_dist(a.position());
            bool claims = k < static_cast<std::size_t>(claim_slots(s)) && claim_value(s, sm, static_cast<int>(k)) == gi + 1;
            if (PR.capprio) {
                if (a.is_recalling() || a.is_teleporting()) continue;
                int ar = cap_rank(norm(bc::to_string(a.champion_name())), a.attack_range() > 1);
                bool counts = ar == 0 && my_rank > 0 ? ((claims && d <= PR.capprio) || d <= 1) : ((claims && d <= 4) || d == 0);
                if (!counts) continue;
                if (ar < my_rank || (ar == my_rank && (d < mine || (d == mine && static_cast<int>(k) < s.ally_idx)))) {
                    other = true;
                    g_cap_other_on = d == 0;
                }
                continue;
            }
            // P_CAPCLAIM: only allies still claiming the group count. Allies that already chose to
            // leave stand on the tiles for one more turn, and counting them made everybody leave.
            if (P_CAPCLAIM ? !(claims && d <= 4) : !(d == 0 || (claims && d <= 4))) continue;
            if (P_CAPDPS) {  // the capture's gold goes to a ranged damage dealer first (top 4: Ryth/Stellar/Cassi earn it)
                int ka = (a.attack_range() > 1 ? 0 : 100) + d, km = (me.attack_range() > 1 ? 0 : 100) + mine;
                if (ka < km || (ka == km && static_cast<int>(k) < s.ally_idx)) other = true;
                continue;
            }
            if (d < mine || (d == mine && static_cast<int>(k) < s.ally_idx)) other = true;
        } catch (...) {
        }
    }
    return true;
    });
    return other;
}

void drop_target(State& s) {
    s.target = -1;
    s.cap_start = -1;
    write_claim(s, -1);
}


// Local-only diagnostics: these do not use the eight shared bytes.
// A death after a recent camp action is temporal evidence, not kill attribution.
void cf_observe(State& s, bc::champion& me, int round) {
    const bool alive = me.is_alive();
    if (!alive && s.cf_was_alive && round - s.cf_recent_camp <= 2) ++s.cf_death_after_camp;
    s.cf_was_alive = alive;
    if (round % 50 == 0 && s.cf_log_round != round) {
        s.cf_log_round = round;
        std::printf("[econ] who=%d r=%d cf_reach=%u cf_focus_wait=%u cf_focus_exit=%u cf_focus_hit=%u cf_evac=%u cf_reward_gain_observed=%u cf_death_after_camp=%u\n",
                    s.ally_idx, round, s.cf_reach, s.cf_focus_wait, s.cf_focus_exit, s.cf_focus_hit, s.cf_evac,
                    s.cf_reward_gain_observed, s.cf_death_after_camp);
    }
}

// True only for actual visible, healthy allies who can plausibly remain here.
// No claimed-but-absent champion contributes damage to the focus model.
bool cf_available(const bc::champion& a) {
    return a.is_visible() && a.is_alive() && a.health() > 0 &&
           a.health() >= 0.35 * a.max_health() && !a.is_recalling() &&
           !a.is_teleporting() && !a.is_submitting_gems();
}


// Leave only for an ally ALREADY occupying the reward. Merely approaching or
// claiming allies never justify emptying the region and resetting capture.
bool cf_evac_reward(State& s, bc::champion& me, Group& g, int round, const std::vector<bc::camp>* near = nullptr) {
    FP_SCOPE(26, "evac");
    const vec2 pos = me.position();
    if (!g.mask.is_set(pos) || !me.can_move() || !fuel_ok(28000)) return false;
    bool present = false;
    for (auto& a : bc::vision::champions(*s.my)) {
        attempt([&] {
            if (a == me || !cf_available(a) || !g.mask.is_set(a.position())) return false;
            // In particular do not rely on a recalling/teleporting ally remaining.
            present = true;
            return true;
        });
        if (present) break;
    }
    if (!present) return false;
    std::vector<std::pair<vec2, int>> monsters;
    // P_FUELGUARD: the camps within 12 (play_turn's list) are the only ones that can reach a tile next to us.
    for (const auto& c : (P_FUELGUARD && near) ? *near : bc::vision::camps()) {
        if (!fuel_ok(16000)) return false;
        bool observed = attempt([&] {
            // Camp wake/aggro is not exposed: avoid every visible damaging
            // monster's range, including an untouched member of an awake group.
            if (c.health() > 0 && c.strength() > 0)
                monsters.push_back({c.position(), c.attack_range()});
            return true;
        });
        if (!observed) return false; // An unknown visible hazard cannot authorize departure.
    }
    // Temporarily remove this target from scoring, without broadcasting a claim
    // or changing lifecycle memory. Failed/no-benefit moves restore all fields.
    const int old_target = s.target, old_bad = g.bad_until;
    g.bad_until = round + 1;
    int alternate = -1;
    if (can_choose(s)) attempt([&] { alternate = choose_target(s, me, round); return true; });
    g.bad_until = old_bad;
    if (!fuel_ok(16000)) return false;
    if (alternate < 0 || alternate == old_target) return false;
    const auto& next = s.groups[alternate];
    const int old_distance = dist(pos, next.center);
    const double current_danger = danger_at(s.thr, pos);
    std::optional<vec2> best;
    int best_distance = old_distance;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 p = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p) || g.mask.is_set(p)) continue;
            if (danger_at(s.thr, p) > current_danger) continue;
            bool monster_safe = true;
            for (const auto& c : monsters) {
                if (dist(p, c.first) <= c.second) monster_safe = false;
                if (!monster_safe) break;
            }
            if (!monster_safe) continue;
            const int d = dist(p, next.center);
            if (d < best_distance) { best = p; best_distance = d; }
        }
    if (!best || !attempt([&] { return me.move_absolute(*best); })) return false;
    ++s.cf_evac;
    s.target = alternate;
    s.target_round = round;
    s.cap_start = -1;
    write_claim(s, alternate);
    g_farm = "reward-evac";
    return true;
}

void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {
    struct NoDash {
        ~NoDash() { g_farm_nodash = false; }
    } nodash_reset;
    g_farm_nodash = P_DASHCALM && (round < P_DASHCALM_OPEN || round - s.foe_r <= P_DASHCALM);
    vec2 pos = me.position();
    double hp = me.health();
    double mhp = std::max(1.0, static_cast<double>(me.max_health()));
    if (i_am_tank(s)) {  // P_DPSFARM: go where a DPS farms
        auto sm = read_sm();
        int best = -1, bd = 1 << 30, tb = tank_bits(s);
        bool issac = starts_with(s.name, "issac");
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < claim_slots(s) && k < static_cast<int>(allies.size()); ++k) {
                if (k == s.ally_idx || ((tb >> k) & 1) || !allies[k].is_alive()) continue;
                int c = static_cast<int>(claim_value(s, sm, k)) - 1;
                if (c < 0 || c >= static_cast<int>(s.groups.size()) || s.groups[c].bad_until > round) continue;
                int d = dist(pos, s.groups[c].center);
                if (issac && starts_with(norm(bc::to_string(allies[k].champion_name())), "cassi")) d -= 1000;
                if (d < bd) { bd = d; best = c; }
            }
            return true;
        });
        if (best >= 0 && best != s.target) {
            s.target = best;
            s.target_round = round;
            s.cap_start = -1;
            write_claim(s, best);
        }
        if (s.target >= 0 && s.groups[s.target].reward_seen == round) {  // the camp is dead: leave the loot to the DPS
            Group& g = s.groups[s.target];
            g_farm = "tank-off";
            write_sm(SM_BC_GROUP, static_cast<std::uint8_t>(s.target + 1));
            write_sm(SM_BC_READY, static_cast<std::uint8_t>(251 + ((round / 16) & 3)));
            g.bad_until = round + 10;
            drop_target(s);
            if (g.mask.is_set(pos)) {
                bc::bitboard r2;
                for (auto t : g.tiles) r2.draw_chebyshev(t, 2.0f);
                step_towards(s, me, r2 & ~g.mask, false);
            }
            return;
        }
        if (best >= 0) s.target_round = round;  // keep following: no periodic re-choice of our own
    }
    if (PR.twinfarm && starts_with(s.name, "issac")) {
        int ck = -1;
        std::optional<vec2> cp;
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < static_cast<int>(allies.size()); ++k) {
                if (!starts_with(norm(bc::to_string(allies[k].champion_name())), "cassi") || !allies[k].is_alive()) continue;
                ck = k;
                try { cp = allies[k].position(); } catch (...) {}
            }
            return true;
        });
        if (ck >= 0) {
            int claim = static_cast<int>(claim_value(s, read_sm(), ck)) - 1;
            if (claim >= 0 && claim < static_cast<int>(s.groups.size())) {
                if (claim != s.target) {
                    s.target = claim;
                    s.target_round = round;
                    s.cap_start = -1;
                    write_claim(s, claim);
                }
            } else if (cp && dist(*cp, pos) > PR.twinfarm && !s.my_spawn.is_set(*cp)) {
                g_farm = "twin-join";
                drop_target(s);
                bc::bitboard ring;
                ring.draw_chebyshev(*cp, 2.0f);
                step_towards(s, me, ring, false);
                return;
            }
        }
    }

    // Committed = a camp of our group is already damaged, or we are capturing.
    bool committed = false;
    if (s.target >= 0) {
        Group& g = s.groups[s.target];
        if (s.cap_start >= 0 && g.mask.is_set(pos)) committed = true;
        // A cleared camp awaiting capture is also committed. Otherwise the
        // retarget timer can redirect us between the final kill and the loot.
        if (P_CAPTURE_RECALL_FIX && g.reward_seen == round) committed = true;
        for (auto& c : camps)
            if (g.mask.is_set(c.spawn_position()) &&
                attempt([&] { return c.health() > 0 && c.health() < c.max_health(); }))
                committed = true;
    }
    bool expired = s.target >= 0 && (s.groups[s.target].bad_until > round ||
                                     s.groups[s.target].next_ok > round + (P_RESPAWN ? dist(pos, s.groups[s.target].center) + P_RESPAWN : 0));
    int target_refresh = 20;
#if defined(P_E_RETARGET) && P_E_RETARGET > 0
    target_refresh = P_E_RETARGET;
#endif
    // A damaged camp or active capture remains committed. Only travel plans
    // are reconsidered sooner when a more productive group becomes available.
    bool refresh = !committed && round - s.target_round >= (ball_on(s, round) ? 3 : target_refresh);
    if (P_FUELGUARD && (s.target < 0 || expired || refresh) && !can_choose(s)) {
        // Not enough fuel to choose and still act: a periodic re-choice waits for a later turn (we keep farming the
        // current target); with no usable target the turn ends here, cleanly, instead of being cut off half way
        // and finished one round late.
        if (s.target < 0 || expired) { g_farm = "fuel-wait"; return; }
        refresh = false;
    }
    if (s.target < 0 || expired || refresh) {
        int t = choose_target(s, me, round);
        if (t != s.target) s.cap_start = -1;
        s.target = t;
        s.target_round = round;
        write_claim(s, t);
    }
    g_farm = "travel";
    if (s.target < 0) {
        // Everything is on cooldown or claimed: wait out of reach of the respawning
        // group that frees up first (monsters hit at range 3; wait at 5).
        int wi = -1, wbest = 1 << 30;
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            Group& g = s.groups[i];
            if (g.gems + g.gold <= 0 || g.monolith || g.next_ok <= round || g.bad_until > round) continue;
            int w = g.next_ok - round + dist(pos, g.center) / 2;
            if (w < wbest) { wbest = w; wi = i; }
        }
        if (wi >= 0 && wbest < 120 && hp >= 0.6 * mhp) {
            g_farm = "wait";
            Group& g = s.groups[wi];
            bc::bitboard r5, r4;
            for (auto t : g.tiles) {
                r5.draw_chebyshev(t, 5.0f);
                r4.draw_chebyshev(t, 4.0f);
            }
            step_towards(s, me, r5 & ~r4, true);
            return;
        }
        g_farm = "no-target";
        if (!s.my_spawn.is_set(pos)) {
            if (hp < 0.9 * mhp && dist(pos, s.spawn_center) > 8) s.need_heal = round;
            else flee(s, me);
        }
        return;
    }
    Group& g = s.groups[s.target];
    attempt([&] {  // replay overlay: yellow line to the camp we are farming
        bc::debug::draw_line(pos, g.center, 0xFFD700);
        return true;
    });

    std::vector<const bc::camp*> live;
    for (auto& c : camps)
        if (g.mask.is_set(c.spawn_position()) && attempt([&] { return c.health() > 0; })) live.push_back(&c);

    if (!live.empty()) {
        s.cap_start = -1;
        s.probe_fail = 0;
        double rem = 0, str = 0;
        bool engaged = false;
        for (auto* c : live) {
            attempt([&] {
                rem += c->health();
                str += c->strength();
                if (c->health() < c->max_health()) engaged = true;
                return true;
            });
        }
        double dps = my_dps(s, me);
        double afford = std::max(1.0, hp - mhp * P_RESERVE_PCT / 100.0);
        int needed = squad_needed(rem, str, dps, afford);
        int here = 1 + allies_near(s, me, g.center, 7);
        int coming = 1 + count_claimers(s, read_sm(), s.target);
        const bool mono_go = (s.mono_only && g.monolith) || (P_JACKGO && g.jackpot && round >= P_JACKGO);
        if (mono_go) needed = std::min(needed, std::max(1, std::min(g.monolith ? s.roster : P_JACKN, s.roster)));
        if (!engaged && needed > here) {
            if (needed > std::max(coming, s.roster) || (!mono_go && needed > squad_needed(rem, str, dps, mhp * 0.75))) {
                g_farm = "too-strong";  // not even a full-health squad would do it
                g.bad_until = round + 60;
                drop_target(s);
                return;
            }
            if (PR.needheal) {  // a wait that no recall or ally will end: take another camp
                if (s.wait_group != s.target) { s.wait_group = s.target; s.wait_start = round; }
                bool recall_next = needed > coming && hp < 0.8 * mhp && dist(pos, s.spawn_center) > 6;
                if ((needed > coming && !recall_next) || round - s.wait_start > PR.needheal) {
                    g_farm = "wait-drop";
                    g.bad_until = round + 30;
                    s.wait_group = -1;
                    drop_target(s);
                    return;
                }
            }
            if (needed > coming) {
                g_farm = "need-heal";   // affordable with full health, not with this much
                s.need_heal = round;
                return;
            }
            g_farm = "rally";           // wait out of reach until the squad is here
            bc::bitboard r5, r4;
            for (auto* c : live) {
                r5.draw_chebyshev(c->position(), 5.0f);
                r4.draw_chebyshev(c->position(), 4.0f);
            }
            step_towards(s, me, r5 & ~r4, true);
            return;
        }
        g_farm = "fight-camp";
        s.wait_group = -1;
        if (hp < mhp * P_BAIL_PCT / 100.0) {
            g_farm = "bail";
            g.bad_until = round + 30;
            drop_target(s);
            bool awake_near = false;
            for (auto* c : live)
                if (dist(c->position(), pos) <= CAMP_RANGE && c->health() < c->max_health()) awake_near = true;
            if (awake_near) flee(s, me);
            return;
        }
        const bc::camp* tgt = live[0];
        for (auto* c : live)
            if (c->health() < tgt->health()) tgt = c;
        // Prefer a living camp already in basic range over walking to another
        // member of this same group. Keep the old choice if none is in range.
        if (P_U34_FARM_REACH && me.can_attack() && fuel_ok(12000)) {
            const int ar = static_cast<int>(me.attack_range());
            const bc::camp* local = nullptr;
            float lowest = 1e30f;
            int checked = 0;
            for (auto* c : live) {
                if (++checked > 8 || !fuel_ok(7000)) break;
                attempt([&] {
                    float health = c->health();
                    if (health > 0 && health < lowest && dist(pos, c->position()) <= ar) {
                        local = c;
                        lowest = health;
                    }
                    return true;
                });
            }
            if (local) { if (local != tgt) ++s.cf_reach; tgt = local; }
        }
        s.cf_recent_camp = round;
        engage(s, me, *tgt, tgt->position(), false, true);
        return;
    }

    // Nothing of this group is visible alive.
    if (g.reward_seen == round) {  // the engine says the reward is waiting: stand on it
        g_farm = "capture";
        if (P_ONE_CAP && other_captures(s, me, g, s.target)) {
            if (PR.capprio && g.mask.is_set(pos)) {
                if (!g_cap_other_on) return;  // keep the capture going until the champion that takes it arrives
                g_farm = "cap-handoff";
                g.bad_until = round + 12;
                drop_target(s);
                bc::bitboard r2;
                for (auto t : g.tiles) r2.draw_chebyshev(t, 2.0f);
                step_towards(s, me, r2 & ~g.mask, false);
                return;
            }
            if (cf_evac_reward(s, me, g, round, &camps)) return;
            if (g.mask.is_set(pos)) return; // retain capture if no safe purposeful step exists
            g_farm = "leave-reward";
            g.bad_until = round + 12;
            drop_target(s);
            if (P_STEPOFF && g.mask.is_set(pos)) {  // standing on the tiles would split the reward
                bc::bitboard r2;
                for (auto t : g.tiles) r2.draw_chebyshev(t, 2.0f);
                step_towards(s, me, r2 & ~g.mask, false);
            }
            return;
        }
        if (g.mask.is_set(pos)) {
            if (s.cap_start < 0) s.cap_start = round;
            if (round - s.cap_start > 12) {  // nothing came: someone else holds it
                g.next_ok = round + 20;
                drop_target(s);
            }
            return;
        }
        step_towards(s, me, g.mask, true);
        return;
    }
    if (g.next_ok > round) {  // refresh_groups saw it respawning
        if (P_RESPAWN && g.next_ok <= round + dist(pos, g.center) + P_RESPAWN) {
            g_farm = "wait-respawn";  // stand 2-3 tiles off its spawn tiles until it is back
            bc::bitboard r3, r1;
            for (auto t : g.tiles) {
                r3.draw_chebyshev(t, 3.0f);
                r1.draw_chebyshev(t, 1.0f);
            }
            bc::bitboard ring = r3 & ~r1;
            if (!ring.is_set(pos)) step_towards(s, me, ring, false);
            return;
        }
        drop_target(s);
        return;
    }
    // Alive but nothing visible: the monsters are hidden (bushes) or out of view.
    // Walk onto its spawn tiles; stepping into a hidden unit reveals it.
    g_farm = "approach";
    s.cap_start = -1;
    bc::bitboard goals = g.mask;
    if (g.mask.is_set(pos)) goals.set(pos, false);
    bool moved = step_towards(s, me, goals, true);
    if (!moved) {
        if (++s.probe_fail > 3) {
            g.bad_until = round + 25;
            drop_target(s);
            s.probe_fail = 0;
        }
    } else {
        s.probe_fail = 0;
    }
}

// ---------------------------------------------------------------------------
// One turn
// ---------------------------------------------------------------------------

// An AoE with cast range four and radius one can hit a visible champion five
// tiles away by aiming at a legal nearer centre. Ordinary targeted casts keep
// their existing scan/range; this is only a fallback when they did not cast.
bool cm_edge_aoe(State& s, bc::champion& me, bool allow_exclusive, bool track_root,
                 bool free_only = false, bool escape = false) {
    if (s.sweep < 3 || !me.can_cast() || !fuel_ok(16000)) return false;
    const vec2 pos = me.position();
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        if (s.slots[k] != Slot::Ground || !abs[k].is_ready()) continue;
        const AoeSlot a = aoe_slot(me, k);
        if (a.radius <= 0) continue;
        const bool exclusive = slot_exclusive(s, me, k);
        if (exclusive && (!allow_exclusive || free_only || escape)) continue;
        std::optional<vec2> best;
        double best_score = -1e30;
        for (auto& c : bc::vision::champions(*s.en)) {
            if (!fuel_ok(8000)) return false;
            attempt([&] {
                if (!c.is_visible() || !c.is_alive() || c.health() <= 0) return false;
                const vec2 p = c.position();
                const int d = dist(pos, p);
                if (s.en_spawn.is_set(p) || d <= SPELL_RANGE || d > a.range + a.radius) return false;
                int hits = 0;
                vec2 centre = aoe_centre(s, me, k, p, &hits);
                if (hits <= 0 || dist(pos, centre) > a.range || dist(centre, p) > a.radius) return false;
                const double score = hits * 1000.0 - c.health();
                if (score > best_score) { best = centre; best_score = score; }
                return true;
            });
        }
        if (best && attempt([&] { return abs[k].use(*best); })) {
            if (track_root && exclusive) s.rooted_r = static_cast<int>(bc::round_number());
            return true;
        }
    }
    return false;
}

// Heuristic benefit threshold for an OPTIONAL trip, not an emergency-heal veto.
// Longer return walks require a larger heal or a larger gold budget. Tavi shops
// in the field, so gold alone never justifies this optional return.
bool cr_optional_value(float hpr, int gold, bool tavi, bool shop_ok,
                       int return_walk, bool travel_policy) {
    if (!travel_policy) return hpr < 0.9f || (!tavi && gold >= 90);
    if (return_walk < 0) return false;
    const float heal_cutoff = std::clamp(0.9f - 0.006f * return_walk, 0.65f, 0.9f);
    const int gold_cutoff = 90 + 3 * std::min(return_walk, 50);
    return hpr < heal_cutoff || (!tavi && shop_ok && gold >= gold_cutoff);
}

void cr_trace(State& s, int round) {
    if (s.cr_log_round == round) return;
    if (s.cr_seen + s.cr_started > 8 && round % 50 != 0) return;
    s.cr_log_round = round;
    std::printf("[econ] who=%d r=%d cr_opportunity=%d cr_skipped=%d cr_tavi_skipped=%d cr_path_unavailable=%d cr_started=%d\n",
                s.ally_idx, round, s.cr_seen, s.cr_skipped, s.cr_tavi_skipped,
                s.cr_path_unavailable, s.cr_started);
}

int cr_return_walk(State& s, vec2 pos, int round) {
    if (!s.cr_home_ready && round >= s.cr_home_retry) {
        s.cr_home_retry = round + 16;
        if (fuel_ok(22000)) {
            s.cr_home_ready = attempt([&] {
                bc::bitboard roots = s.my_spawn & ~s.static_block;
                s.cr_home_df.compute(s.static_block, roots, s.cr_home_seen, 200);
                return true;
            });
        }
    }
    if (!s.cr_home_ready || !s.cr_home_seen.is_set(pos)) return -1;
    return static_cast<int>(s.cr_home_df.get(pos));
}

bool cr_capture_extra(State& s, bc::champion& me, float hpr, int gold, int round) {
    const bool tavi = starts_with(s.name, "tavi");
    const bool old_optional = hpr < 0.9f || gold >= 90;
    const bool eligible_reward = s.target >= 0 && s.target < static_cast<int>(s.groups.size()) &&
        s.groups[s.target].reward_seen == round && s.groups[s.target].mask.is_set(me.position());
    const bool shop_ok = (!P_SHOPFIX || round - s.shop_fail > 150) && round - s.shop_recall > 40;
    const int walk = true ? cr_return_walk(s, me.position(), round) : 0;
    const bool result = cr_optional_value(hpr, gold, tavi, shop_ok, walk, true);
    if (old_optional && eligible_reward) {
        ++s.cr_seen;
        if (!result) ++s.cr_skipped;
        if (tavi && hpr >= 0.9f && gold >= 90 && !result) ++s.cr_tavi_skipped;
        if (true && walk < 0) ++s.cr_path_unavailable;
        cr_trace(s, round);
    }
    return result;
}

void play_turn(State& s) {
    bc::champion& me = bc::self();
    FP(1, "init");
    if (!s.ready) {
        // P_FUELGUARD: start-up can eat most of the first turn's double budget on big maps; the turn then ends
        // cleanly on the spawn (start-up finishes next turn) rather than run out half way and play the rest late.
        if (!init(s, me)) {
            g_mode = "init-fuel";
            return;
        }
        s.ready = true;  // never retry a failing init every turn
        if (P_FUELGUARD && !fuel_ok(40000)) {
            g_mode = "init-fuel";
            return;
        }
    }
    const int round = static_cast<int>(bc::round_number());
    cf_observe(s, me, round);

    if (!me.is_alive()) {
        g_mode = "dead";
#if P_TRACK_LOG
        track::on_dead(round);
#endif
        shop(s, me);  // dead champions can still shop
        drop_target(s);
        return;
    }

    vec2 pos = me.position();
    const float mhp = me.max_health();
    int gems = static_cast<int>(me.gem_count());
    int gold = static_cast<int>(me.gold_count());
    bool on_spawn = s.my_spawn.is_set(pos);

    // Capture reward arrived while standing on our target's spawn tiles.
    if (s.target >= 0 && (gems > s.last_gems || gold > s.last_gold) && s.groups[s.target].mask.is_set(pos)) {
        Group& g = s.groups[s.target];
        ++s.cf_reward_gain_observed;
        g.next_ok = round + g.respawn - (P_RESPAWN ? 6 : 0);
        g.reward_seen = -1;
        broadcast_cooldown(s.target, g.next_ok);
        drop_target(s);
    }
    s.last_gems = gems;

    FP(2, "shop");
    if (P_SHOPFIX && !s.shop_done && fuel_ok(40000)) build_shop(s, me);  // init ran out of fuel before the item list was done
    if (gold >= 30) {
        shop(s, me);  // only succeeds on spawn / dead (or anywhere for Tavi)
        if (P_SHOPFIX && on_spawn && me.gold_count() >= 30 && static_cast<int>(me.gold_count()) == gold) s.shop_fail = round;
    }
    s.last_gold = static_cast<int>(me.gold_count());
    float hp = me.health();
    float hpr = hp / mhp;
    if (s.last_hp >= 0 && hp < s.last_hp - 1.0f) s.hit_round = round;
    s.last_hp = hp;

    if (PR.backhome) {
        bool sub = me.is_submitting_gems();
        if (s.sub_prev && !sub) s.trib_end = round;
        s.sub_prev = sub;
    }
    if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) {
        g_mode = "channel";
        return;
    }
    if (!fuel_ok(15000)) {
        g_mode = "low-fuel";
        return;
    }

    FP(3, "vision");
    if (X(pos) == s.still_x && Y(pos) == s.still_y) ++s.still_n;
    else { s.still_x = X(pos); s.still_y = Y(pos); s.still_n = 0; }
    s.blocked = s.static_block | bc::vision::champion_tiles() | bc::vision::camp_tiles();
    s.blocked.set(pos, false);
    attempt([&] {
        s.vis = me.visible_tiles();
        return true;
    });
    FP(4, "groups");
    if (P_MAPPLAN && P_MP_CHAINPLAN) s.self_pos = pos;
    refresh_groups(s, round);
    FP(5, "foes");

    std::vector<Foe> foes;
    bool channel_foes_complete=true;
    for (auto& c : bc::vision::champions(*s.en)) {
        bool inspected=false;
        attempt([&] {
            if (!c.is_alive()) { inspected=true; return false; }
            Foe f{c, c.position(), c.health(), 0, 0, false};
            f.d = dist(f.p, pos);
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                return true;
            });
            attempt([&] {
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            foes.push_back(f);
            inspected=true;
            return true;
        });
        if (!inspected) channel_foes_complete=false;
    }
    if (P_NOCHASE) {
        // Away: it stepped farther from where we stood, or toward its spawn without coming closer to us;
        // it stays "away" for 3 rounds unless it comes back within 2 of us.
        std::vector<Seen> now;
        for (auto& f : foes) {
            int until = -1;
            if (s.seen_r == round - 1)
                for (auto& o : s.seen)
                    if (o.c == f.c) {
                        until = o.away_until;
                        bool moved = !(o.p == f.p);
                        bool off = dist(f.p, s.seen_me) > dist(o.p, s.seen_me);
                        bool home = dist(f.p, s.en_center) < dist(o.p, s.en_center) && dist(f.p, pos) >= dist(o.p, pos);
                        if (moved && (off || home)) until = round + 3;
                        break;
                    }
            if (f.d <= 2) until = -1;
            f.away = until >= round;
            now.push_back({f.c, f.p, until});
        }
        s.seen = std::move(now);
        s.seen_r = round;
        s.seen_me = pos;
    }
    if (P_TRACK) track::update(s, me, foes, pos, round);
    if (P_DANGER) update_danger(s, foes, round);
    if (P_VOLLEY || P_FM >= 2) {  // the volley map of this round (step_towards reads it)
        s.thr.clear();
        for (auto& f : foes) {
            if (f.d > 10) continue;
            int ar = 1;
            attempt([&] {
                ar = static_cast<int>(f.c.attack_range());
                return true;
            });
            s.thr.push_back(threat_of(f.c, f.p, ar <= 1 ? 2 : ar + 1));
        }
        s.thr_r = round;
    }
    if (!foes.empty()) s.foe_r = round;
    FP(6, "camps");
    bool channel_camps_complete=true;
    std::vector<bc::camp> camps = P_LEAN_CAMPS ? near_camps(s,pos,P_DP_CHANNEL_FIX?&channel_camps_complete:nullptr) : bc::vision::camps();

    bool awake_camp_near = false;
    for (auto& c : camps)
        attempt([&] {
            if (dist(c.position(), pos) <= CAMP_RANGE + 1 && c.health() < c.max_health()) awake_camp_near = true;
            return true;
        });
    int nearest_foe = 99;
    for (auto& f : foes) nearest_foe = std::min(nearest_foe, f.d);
    s.nf_d = nearest_foe;
    s.nf_r = static_cast<int>(bc::round_number());
    if (P_TRACE) {
        g_nf = nearest_foe; g_nfoes = 0; g_nal = 0;
        for (auto& f : foes) if (f.d <= 8) ++g_nfoes;
        attempt([&] { for (auto& a : bc::vision::champions(*s.my)) if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 6) ++g_nal; return true; });
        g_rew = (s.target >= 0 && s.target < static_cast<int>(s.groups.size()) && s.groups[s.target].reward_seen == round) ? 1 : 0;
    }
    bool in_combat = nearest_foe <= 4 || awake_camp_near;
    bool safe = nearest_foe > 7 && !awake_camp_near;
    if (P_SAFE_RECALL) safe = safe && nearest_foe > 8 && round - s.hit_round > 2;
    // P_RECALL_NEAR: a recall only needs nobody to hit us while it channels, not an empty screen
    bool rsafe = safe || (s.rnear && nearest_foe >= s.rnear && round - s.hit_round >= 1 && !awake_camp_near);
    if (P_DP_CHANNEL_FIX) {
        s.ch_round=round; s.ch_pos=pos;
        s.ch_complete=channel_foes_complete;
        s.ch_camps_complete=channel_camps_complete;
        s.ch_foes.clear();
        for (const auto& f:foes) s.ch_foes.push_back(f.p);
        s.ch_camps=camps;
    }

    if (P_DP_FINISH && dp_finish_bank(s, me, foes, round, gems, hpr, on_spawn)) return;

    // Preserve a nearby cleared camp's loot, even if we were hit by its last
    // surviving monster on a recent turn. The recent-hit check in `safe` is
    // over-conservative after that monster has died. Only delay non-emergency
    // recalls, and only when we are the designated capturer, no enemies are
    // within 8 tiles, and no fighting camp is nearby. Very low HP still flees.
    bool capture_before_recall = false;
    if (P_CAPTURE_RECALL_FIX && hpr >= 0.20f && nearest_foe > 8 &&
        !awake_camp_near && s.target >= 0 &&
        s.target < static_cast<int>(s.groups.size()) && fuel_ok(18000)) {
        const Group& reward = s.groups[s.target];
        if (reward.reward_seen == round) {
            int nearest_tile = 99;
            for (auto tile : reward.tiles) nearest_tile = std::min(nearest_tile, dist(pos, tile));
            if (nearest_tile <= 2 && (!P_ONE_CAP || !other_captures(s, me, reward, s.target)))
                capture_before_recall = true;
        }
    }

    // P_CAPHOME: the reward of our camp waits within reach and we are its capturer.
    bool cap_home = false, cap_pend = false;
    if (PR.caphome && s.target >= 0 && s.target < static_cast<int>(s.groups.size()) && !awake_camp_near &&
        s.groups[s.target].reward_seen == round && fuel_ok(18000)) {
        const Group& rg = s.groups[s.target];
        int nt = 99;
        for (auto tile : rg.tiles) nt = std::min(nt, dist(pos, tile));
        if (nt <= PR.caphome && (!P_ONE_CAP || !other_captures(s, me, rg, s.target))) {
            cap_pend = PR.caphome_trib && nt <= 2;
            cap_home = PR.caphome_trib != 2 && hpr >= 0.1f && nearest_foe > (hpr * 100 < P.flee_pct ? 5 : 3) &&
                       (!PR.caphome_rsafe || rsafe);
        }
    }

    FP(7, "support");
    support_spells(s, me, in_combat);
    FP(8, "decide/flee");

    // Best enemy target: low health, channeling, or carrying gems; never on their spawn.
    Foe* tgt = nullptr;
    double tgt_score = 1e18;
    auto gone = [&](const Foe& f) {  // P_NOCHASE: walking away and out of reach: the fight with it is over
        return P_NOCHASE && f.away && f.d > me.attack_range() && f.gems < P_CHASE_GEMS && !f.channeling;
    };
    for (auto& f : foes) {
        if (f.d > 6 || s.en_spawn.is_set(f.p) || gone(f)) continue;
        double sc = f.hp - (f.channeling ? 300 : 0) - 5.0 * f.gems + 40.0 * f.d;
        if (sc < tgt_score) { tgt_score = sc; tgt = &f; }
    }

    // Stuck: same tile for many turns with nothing to hit. Bank or go home, give the target up.
    if (P_UNSTICK && s.still_n >= P_UNSTICK && !on_spawn && nearest_foe > 4 && !awake_camp_near &&
        (s.cap_start < 0 || round - s.cap_start > 10)) {
        g_mode = "unstick";
        if (s.target >= 0) {
            s.groups[s.target].bad_until = round + 30;
            drop_target(s);
        }
        if (gems > 0 && go_tribute(s, me, round)) return;
        if (hpr < 0.9f) {
            if (safe && start_recall(s, me, round))
                return;
            if (flee(s, me)) return;
        }
        s.still_n = 0;
    }

    if (PR.noleave && !awake_camp_near && hpr >= 0.15f && fuel_ok(25000)) {
        const bool carry = cap_rank(s.name, me.attack_range() > 1) <= 2;
        auto sm = read_sm();
        int gi = -1, gd = 99;
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            const Group& g = s.groups[i];
            if (g.reward_seen != round || g.monolith) continue;
            int d = 99;
            for (auto tile : g.tiles) d = std::min(d, dist(pos, tile));
            if (d > PR.noleave || d >= gd) continue;
            if (i != s.target && count_claimers(s, sm, i) > 0) continue;  // another ally already went for it
            gi = i;
            gd = d;
        }
        bool skip = gi < 0;
        if (!skip && PR.cache && !carry) {  // tanks leave it to a carry: post it in the cache and move on
            bool carry_alive = false, carry_near = false;
            attempt([&] {
                for (auto& a : my_roster(s)) {
                    if (a == me || !a.is_alive()) continue;
                    bool ar = false;
                    try { ar = a.attack_range() > 1; } catch (...) {}
                    if (cap_rank(norm(bc::to_string(a.champion_name())), ar) > 2) continue;
                    carry_alive = true;
                    try { if (dist(a.position(), pos) <= 6) carry_near = true; } catch (...) {}
                }
                return true;
            });
            if (carry_alive && !(gd <= 1 && !carry_near)) {
                write_sm(SM_BC_GROUP, static_cast<std::uint8_t>(gi + 1));
                write_sm(SM_BC_READY, static_cast<std::uint8_t>(251 + ((round / 16) & 3)));
                if (s.target == gi) {
                    s.groups[gi].bad_until = round + 15;
                    drop_target(s);
                }
                skip = true;
            }
        }
        if (!skip) {
            Group& g = s.groups[gi];
            double dmg = s.thr_r == round ? danger_at(s.thr, pos) : 0.0;
            if (dmg * 3 < hp && (!P_ONE_CAP || !other_captures(s, me, g, gi))) {
                g_mode = "no-leave";
                if (s.target != gi) {
                    s.target = gi;
                    s.target_round = round;
                    s.cap_start = -1;
                    write_claim(s, gi);
                }
                if (!g.mask.is_set(pos)) step_towards(s, me, g.mask, true);
                if (g.mask.is_set(me.position())) {
                    if (s.cap_start < 0) s.cap_start = round;
                    bool want_home = hpr * 100 < P.recall_pct || (round - s.need_heal <= 2 && hpr < 0.8f);
                    if (want_home && rsafe && round - s.cap_start >= P_CAPRECALL_DELAY)
                        start_recall(s, me, round);
                }
                if (!me.is_recalling()) shoot_back(s, me, foes);
                return;
            }
        }
    }

    // 1. Healing on spawn.
    g_mode = "heal-spawn";
    if (on_spawn && hpr * 100 < P_GA_SPAWN_HEAL) {
        if (tgt) basic_attack(s, me, tgt->c, tgt->p);
        return;
    }

    if (cap_home && (hpr * 100 < P.recall_pct || (round - s.need_heal <= 2 && hpr < 0.8f))) {
        Group& g = s.groups[s.target];
        g_mode = "cap-home";  // capture and recall run together on the reward tiles
        if (!g.mask.is_set(pos)) step_towards(s, me, g.mask, true);
        if (g.mask.is_set(me.position())) {
            if (s.cap_start < 0) s.cap_start = round;
            if (start_recall(s, me, round)) return;
        }
        if (!P_DP_CHANNEL_FIX) return;
    }

    // 2. Badly hurt: run, or recall if nobody can interrupt.
    g_mode = "flee/recall";
    // P_UNI_FLEE: with the caster draft, leave the fight earlier (the #1 walks away 58% of contact rounds below 30%
    // hp and 40% below 50%; v27 died in 20% of its contact rounds below 30%)
    if (!capture_before_recall &&
        hpr * 100 < ((P_UNI_FLEE && P_DRAFTUNI && s.casters) ? P_UNI_FLEE : P.flee_pct)) {
        if (gems > 0 && nearest_foe > 3) {
            auto a = best_altar(s, pos, round);
            if (a && dist(*a, pos) <= 1) {  // tribute is not interrupted by damage
                bool acted = go_tribute(s, me, round);
                if (acted || !(P_U34_FAILED_CHANNELS || P_DP_CHANNEL_FIX)) return;
            }
        }
        bool recalled = false;
        if (rsafe) recalled = start_recall(s, me, round);
        if (!rsafe || ((P_U34_FAILED_CHANNELS || P_DP_CHANNEL_FIX) && !recalled)) {
            bool hit = P_HITFIRST && fight::hit_now(s, me, foes);
            flee(s, me);
            if (!hit) shoot_back(s, me, foes);
        }
        return;
    }

    if (!capture_before_recall && s.rnear && !safe && rsafe && !on_spawn &&
        dist(pos, s.spawn_center) > 6 && hpr * 100 < P.recall_pct) {
        g_mode = "near-recall";  // the #1: hurt, out of the fight by 4-6 tiles: recall now, come back whole
        if (start_recall(s, me, round))
            return;
    }

    bool fight_fav = false;  // P_CAMPFOE: step 3's verdict on the fight
    // 3. Enemy champions: back away from a stronger group, fight an even or weaker one.
    FP(9, "fight");
    g_mode = "fight";
    std::vector<vec2> allies;
    for (auto& a : bc::vision::champions(*s.my))
        attempt([&] {
            if (!(a == me) && a.is_alive()) allies.push_back(a.position());
            return true;
        });
    // Ally duty: a foe near an ally of ours (within 8 of us) becomes our target.
    if (P_ALLYDUTY && !tgt) {
        for (auto& f : foes) {
            if (f.d > 8 || s.en_spawn.is_set(f.p) || gone(f)) continue;
            for (auto& ap : allies)
                if (dist(ap, f.p) <= 3 && dist(ap, pos) <= 8) {
                    if (!tgt || f.hp < tgt->hp) tgt = &f;
                    break;
                }
        }
    }
    bool pv_fight = false;  // P_PV: the first-contact verdict, held for the engagement (verdict.h)
    if (P_PV) {
        int v = pv::verdict(s, me, foes, round, on_spawn);
        bool keep = false;
        if (P_PV_KEEPCAP && s.cap_start >= 0) {
            keep = true;
            for (auto& f : foes)
                if (f.d <= 3) keep = false;
        }
        if (v == 2 && !on_spawn && !foes.empty() && !keep) {
            if (P_PVKITE) {  // user 2026-10-17: kite while asking for help instead of running home
                g_mode = "pv-kite";
                fight::call_help(s, foes, round);
                fight::pv_kite(s, me, foes, round);
                return;
            }
            g_mode = "pv-leave";
            if (P_PVOUT) fight::pv_out(s, me, foes, round);
            else fight::back_off(s, me, foes, round);
            return;
        }
        pv_fight = v == 1;
    }
    if (P_FM && !foes.empty() && !on_spawn && fight::fight_mode(s, me, foes, round)) {
        g_mode = s.fm == 1 ? "fm-engage" : "fm-retreat";
        return;
    }
    if (P_KITEFRONT == 1 && P_FRONT && !foes.empty() && !on_spawn && fight::front_line(s, me, foes, round)) {
        g_mode = "front";
        return;
    }
    if (P_KITE && s.casters && !foes.empty() && !on_spawn && (!s.melee || s.renkite) && fight::kite(s, me, foes, round)) {
        g_mode = "kite";
        return;
    }
    if (P_KITEFRONT != 1 && P_FRONT && !P_AVOIDFIRST && !foes.empty() && !on_spawn && fight::front_line(s, me, foes, round)) {
        g_mode = "front";
        return;
    }
    if (!foes.empty()) {
        if (P_CALLHELP && round - s.hit_round <= 1) fight::call_help(s, foes, round);
        if (PR.twin && !on_spawn && (s.cap_start < 0 || round - s.cap_start > 10) && fight::twin_guard(s, me, foes)) {
            g_mode = "twin";
            return;
        }
        double ours = hp, theirs = 0;
        for (auto& a : bc::vision::champions(*s.my))
            attempt([&] {
                if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 6) ours += a.health();
                return true;
            });
        for (auto& f : foes)
            if (f.d <= 8) theirs += f.hp;
        bool favourable = ours * 100.0 >= P_GA_FAV * theirs;
        if (P_ENGAGE2 && tgt) {
            int nb = 1, eb = 0;
            double oh = hp, eh = 0;
            for (auto& ap : allies)
                if (dist(ap, tgt->p) <= 8) ++nb;
            attempt([&] {
                for (auto& a : bc::vision::champions(*s.my))
                    if (!(a == me) && a.is_alive() && dist(a.position(), tgt->p) <= 8) oh += a.health();
                return true;
            });
            for (auto& f : foes)
                if (dist(f.p, tgt->p) <= 8) { ++eb; eh += f.hp; }
            favourable = nb >= eb && oh * 100.0 >= P_ENGAGE2 * eh;
        }
        if (P_TRACK && P_TRACK_FAV && tgt) favourable = track::favourable(me, tgt->p, round);
        bool helping = false;
        if ((P_CALLHELP || P_PVKITE) && hpr > 0.4f) {  // an ally named the foe hitting it: go and hit that one
            Foe* h = fight::help_target(s, foes, round);
            if (h && h->d <= P_HELP_R && !s.en_spawn.is_set(h->p) && !gone(*h)) {
                int nb = 1, eb = 0;
                for (auto& ap : allies) if (dist(ap, h->p) <= 6) ++nb;
                for (auto& f : foes) if (dist(f.p, h->p) <= 6) ++eb;
                if (nb >= eb) { tgt = h; favourable = true; helping = true; }
            }
        }
        // Top-10 habit: gang up on a lone foe that is hurt (< 65% hp) or carrying gems, with
        // P_GANG of us (me included) within 8 of it; never chase further than 8 tiles.
        if (P_GANG && !helping && hpr > 0.5f) {
            Foe* best = nullptr;
            for (auto& f : foes) {
                if (f.d > 8 || s.en_spawn.is_set(f.p) || gone(f)) continue;
                bool lone = true;
                for (auto& o : foes)
                    if (&o != &f && dist(o.p, f.p) <= 4) lone = false;
                if (!lone) continue;
                float mh = 0;
                attempt([&] {
                    mh = f.c.max_health();
                    return true;
                });
                if (!(f.channeling || f.gems >= 20 || (mh > 0 && f.hp < 0.65f * mh))) continue;
                int nb = 1;
                for (auto& ap : allies) if (dist(ap, f.p) <= 8) ++nb;
                if (nb < P_GANG) continue;
                if (!best || f.hp < best->hp) best = &f;
            }
            if (best) { tgt = best; favourable = true; helping = true; }
        }
        if (P_TRACK && P_TRACK_ISO && !helping && hpr > 0.4f) {  // a lone enemy the allies near it kill fast
            Foe* iso = track::isolated(s, me, foes, round, gone);
            if (iso) { tgt = iso; favourable = true; helping = true; }
        }
        bool pot_hold = false;
        if (P_POT && hpr > 0.3f)
            for (auto pa : s.pots)
                if (dist(pa, pos) <= 5) {
                    int nb6 = 1, eb6 = 0;
                    for (auto& ap : allies) if (dist(ap, pos) <= 6) ++nb6;
                    for (auto& f : foes) if (f.d <= 6) ++eb6;
                    if (eb6 < nb6 + 2) pot_hold = true;
                }
        if (pot_hold) favourable = true;
        if (pv_fight) favourable = true;
        bool commit = false;  // P_PVCOMMIT: a clearly won verdict (P_PV 2, ratio >= P_PV_FIGHT): all of us on the weakest foe
        if (P_PVCOMMIT && pv_fight && !helping && hpr > 0.25f) {
            Foe* best = nullptr;
            for (auto& f : foes) {
                if (f.d > P_PVCOMMIT || s.en_spawn.is_set(f.p) || gone(f)) continue;
                if (!best || f.hp < best->hp) best = &f;
            }
            if (best) { tgt = best; commit = true; }
        }
        g_ally_near_tgt = false;
        if (tgt)
            for (auto& ap : allies)
                if (dist(ap, tgt->p) <= 2) g_ally_near_tgt = true;
        fight_fav = favourable;
        bool killable = tgt && tgt->hp <= me.strength() * (P_GA_KILL_X / 10.0f);
        bool reachable = tgt && tgt->d <= me.attack_range() + 1;
        bool carrying = P_CARRY && gems >= P_CARRY;
        int low_pct = (P_CASSI_PCT && starts_with(s.name, "cassi")) ? P_CASSI_PCT : P_LOWHP;
        if (!killable && !commit && !on_spawn && !pot_hold && ((low_pct && hpr * 100 < low_pct && nearest_foe <= 6) ||
                                       (carrying && !favourable && nearest_foe <= 6))) {
            g_mode = "avoid";
            if (carrying) {
                auto a = best_altar(s, pos, round);
                if (a && dist(*a, pos) <= 1 && nearest_foe > 3) {
                    bool acted = go_tribute(s, me, round);
                    if (acted || !(P_U34_FAILED_CHANNELS || P_DP_CHANNEL_FIX)) return;
                }
            }
            fight::back_off(s, me, foes, round);
            return;
        }
        if (PR.outnum && !commit && !on_spawn && !(killable && reachable) && nearest_foe <= PR.outnum) {
            int nb = 1, eb = 0;
            attempt([&] {
                for (auto& a : bc::vision::champions(*s.my))
                    if (!(a == me) && a.is_alive() && !a.is_recalling() && dist(a.position(), pos) <= PR.outnum) ++nb;
                return true;
            });
            for (auto& f : foes)
                if (f.d <= PR.outnum && !s.en_spawn.is_set(f.p)) ++eb;
            if (eb >= nb + 2) {
                g_mode = "outnumbered";
                fight::back_off(s, me, foes, round);
                return;
            }
        }
        if (!favourable && !killable && (hpr * 100 < P_GA_AVOID_HP || nearest_foe <= P_AVOID_DIST) && !on_spawn) {
            g_mode = "avoid";
            fight::back_off(s, me, foes, round);
            return;
        }
        // P_AVOIDFIRST: the front line is taken only once the back-off checks above said stay
        if (P_AVOIDFIRST && P_KITEFRONT != 1 && P_FRONT && !on_spawn && fight::front_line(s, me, foes, round)) {
            g_mode = "front";
            return;
        }
        if (tgt && carrying && !commit && !killable && !tgt->channeling) tgt = nullptr;
        // P_NOCHASE2: a low or channelling foe is no reason to walk after it, unless it carries a big bag
        const bool close_enough = !PR.nochase2 || (tgt && (tgt->d <= me.attack_range() + 1 || tgt->gems >= P_CHASE_GEMS));
        if (tgt && (((killable || tgt->channeling) && close_enough) || (reachable && favourable) || helping || commit ||
                    (P_ALLYDUTY && favourable && tgt->d <= 8 && g_ally_near_tgt))) {
            bool acted = engage(s, me, tgt->c, tgt->p, true, true);
            if (acted || !P_U34_ENGAGE_FALLBACK) return;
        }
    }

    // 4. Recall to heal / spend gold when safe; bank the bag first if an altar is close.
    FP(10, "recall/tribute");
    g_mode = "recall-shop";
    int home = dist(pos, s.spawn_center);
    bool want_recall = hpr * 100 < P.recall_pct || (gold >= P_SHOP_GOLD && hpr < 0.5f) ||
                       (round - s.need_heal <= 2 && hpr < 0.8f);
    bool shop_trip = P_SHOP_RECALL && gold >= P_SHOP_RECALL && !starts_with(s.name, "tavi") &&
                     (!P_SHOPFIX || round - s.shop_fail > 150) &&
                     s.cap_start < 0 && round - s.shop_recall > 40;
    want_recall = want_recall || shop_trip;
    // P_CAPRECALL: capture first and recall on the capture tiles, so the 5-round recall overlaps the 5-round
    // capture (procless on rows: it captures and arrives home healed in the same turn).
    // P_CAPRECALL 2: also take the free trip home whenever it heals or shops something (hp < 90%, 90+ gold).
    // Preserve normal healing/shop recalls. Only the extra capture opportunity
    // weighs the cost of returning to productive territory.
    bool cap_want = want_recall || (((s.de_map == v34de::Lanes) ? 1 : P_CAPRECALL) >= 2 &&
                                   cr_capture_extra(s, me, hpr, gold, round));
    if (((s.de_map == v34de::Lanes) ? 1 : P_CAPRECALL) && cap_want &&
        (safe || capture_before_recall) && s.target >= 0 && s.target < static_cast<int>(s.groups.size())) {
        Group& g = s.groups[s.target];
        if (g.reward_seen == round && !other_captures(s, me, g, s.target)) {
            if (g.mask.is_set(pos) && (P_CAPRECALL_DELAY == 0 || (s.cap_start >= 0 && round - s.cap_start >= P_CAPRECALL_DELAY))) {
                g_mode = "cap-recall";
                const bool recalled = start_recall(s, me, round);
                if (recalled) {
                    ++s.cr_started;
                    cr_trace(s, round);
                    if (shop_trip) s.shop_recall = round;
                }
                if (recalled || !P_DP_CHANNEL_FIX) return;
            }
            want_recall = false;  // step on the tiles first
        }
    }
    if (PR.backhome && round - s.trib_end <= 2 && gems == 0 && home > 6) {
        s.trib_end = -1000;
        auto contested = [&](vec2 p) { return dist(p, s.spawn_center) - dist(p, s.en_center) >= -PR.backhome; };
        if (contested(pos)) {
            int t = s.target;
            if (can_choose(s)) t = choose_target(s, me, round);
            bool go = t < 0 || (contested(s.groups[t].center) && (round - s.foe_r <= 20 || hpr < 0.8f));
            if (go) {
                g_mode = "back-home";
                drop_target(s);
                if (rsafe && start_recall(s, me, round))
                    return;
                if (flee(s, me)) return;
            } else if (t != s.target) {
                s.target = t;
                s.target_round = round;
                s.cap_start = -1;
                write_claim(s, t);
            }
        }
    }
    if (!capture_before_recall && rsafe && home > 6 && want_recall) {
        if (gems >= 10) {
            auto a = best_altar(s, pos, round);
            if (a && br_altar_distance(s, *a, pos, round) <= std::min(home, 12)) {
                g_mode = "tribute";
                bool acted = go_tribute(s, me, round);
                if (acted || !(P_U34_FAILED_CHANNELS || P_DP_CHANNEL_FIX)) return;
            }
        }
        bool recalled = start_recall(s, me, round);
        if (recalled && shop_trip) s.shop_recall = round;
        if (recalled || !(P_U34_FAILED_CHANNELS || P_DP_CHANNEL_FIX)) return;
    }

    if (P_WALKHOME && !safe && home > 6 && hpr * 100 < P.recall_pct && nearest_foe > 2) {
        g_mode = "walk-home";
        if (gems >= 10) {
            auto a = best_altar(s, pos, round);
            if (a && br_altar_distance(s, *a, pos, round) <= std::min(home, 8) && go_tribute(s, me, round)) return;
        }
        if (flee(s, me)) return;
    }

    // 5. Bank gems.
    g_mode = "tribute";
    bool late = round >= P.late_round;
    if (gems > 0 && !(cap_pend && !late)) {
        auto a = best_altar(s, pos, round);
        int ad = a ? br_altar_distance(s, *a, pos, round) : 99;
        bool chain = false;
        const int chain_gems = mp_far_home(s) ? std::max(P_MP_CHAIN, (s.de_map == v34de::Rows) ? 60 : P_CHAIN) : ((s.de_map == v34de::Rows) ? 60 : P_CHAIN);
        if (chain_gems && gems < chain_gems && !late && ad > 2) {
            auto sm = read_sm();
            int gi = -1, gd = 99;
            for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
                Group& g = s.groups[i];
                if (g.gems <= 0 || g.monolith || g.next_ok > round || g.bad_until > round) continue;
                int d = dist(pos, g.center);
                if (d > (mp_far_home(s) ? P_MP_CHAIN_R : P_CHAIN_R) || d >= ad || d >= gd) continue;
                if (count_claimers(s, sm, i) > 0 && i != s.target) continue;
                if (squad_needed(g.hp, g.str, my_dps(s, me), std::max(1.0f, hp - mhp * 0.3f)) > 1) continue;
                gi = i;
                gd = d;
            }
            if (gi >= 0) {
                chain = true;
                if (s.target != gi) {
                    s.target = gi;
                    s.target_round = round;
                    s.cap_start = -1;
                    write_claim(s, gi);
                }
            }
        }
        // P_BAG: with no enemy seen for P_BAG_QUIET rounds, carry up to P_BAG gems before the trip
        // (rows winners bank 81 gems a trip; we banked 39).
        const int bag_q = mp_far_home(s) ? std::max(P_MP_BAG, (s.de_map == v34de::Rows) ? 48 : P_BAG) : ((s.de_map == v34de::Rows) ? 48 : P_BAG);
        int bag = (bag_q && round - s.foe_r > P_BAG_QUIET) ? std::max(P.tribute_gems, bag_q) : P.tribute_gems;
        if (P_DP_BANK && draftplan::R.valid && round - s.foe_r > P_DP_BANK_QUIET)
            bag = std::max(bag, draftplan::quiet_bag());
        if (!chain && (gems >= bag || late || (gems >= 10 && ad <= (s.de_map == v34de::Rows ? 4 : P_TRIBUTE_NEAR)) || (gems >= 5 && ad <= 2))) {
            // P_TELE: the walk to the altar is longer than recalling and walking from home: recall (heals and shops too).
            if (P_TELE && safe && s.tele_sa >= 0 && s.tele_va.is_set(pos) && !s.my_spawn.is_set(pos) &&
                static_cast<int>(s.tele_fa.get(pos)) > 5 + s.tele_sa + P_TELE) {
                g_mode = "tele-bank";
                const bool recalled = start_recall(s, me, round);
                if (recalled) s.shop_recall = round;
                if (recalled || !P_DP_CHANNEL_FIX) return;
            }
            bool acted = go_tribute(s, me, round);
            if (acted || !(P_U34_FAILED_CHANNELS || P_DP_CHANNEL_FIX)) return;
        }
    }

    // P_GROUP_R: keep the ball together. The leader is the first ally in draft order that is alive and not
    // channelling; followers come back to it, the leader waits for a straggler (ignoring anyone 15+ away).
    if (P_GROUP_R && grouped(s, round) && !awake_camp_near && s.cap_start < 0) {
        int li = -1, far = 0;
        vec2 lp{0, 0};
        std::vector<vec2> fol;
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < static_cast<int>(allies.size()); ++k) {
                auto& a = allies[k];
                try {
                    if (!a.is_alive() || a.is_recalling() || a.is_teleporting()) continue;
                    vec2 ap = a.position();
                    if (s.my_spawn.is_set(ap) && !(a == me)) continue;
                    if (li < 0) { li = k; lp = ap; continue; }
                    if (!(a == me)) fol.push_back(ap);
                } catch (...) {
                }
            }
            return true;
        });
        if (li >= 0 && li != s.ally_idx && dist(pos, lp) > P_GROUP_R) {
            g_mode = "group";
            bc::bitboard ring;
            ring.draw_chebyshev(lp, 2.0f);
            if (step_towards(s, me, ring, false)) {
                if (tgt && me.can_attack()) basic_attack(s, me, tgt->c, tgt->p);
                return;
            }
        }
        if (li == s.ally_idx)
            for (auto& f : fol) {
                int d = dist(f, pos);
                if (d <= 15) far = std::max(far, d);
            }
        if (li == s.ally_idx && far > 2 * P_GROUP_R) {
            g_mode = "group-wait";
            if (tgt && me.can_attack()) basic_attack(s, me, tgt->c, tgt->p);
            return;
        }
    }

    if (PR.campfoe && !on_spawn && !foes.empty()) {
        int live = 99;
        for (auto& f : foes)
            if (!s.en_spawn.is_set(f.p) && !gone(f)) live = std::min(live, f.d);
        bool capturing = s.target >= 0 && s.target < static_cast<int>(s.groups.size()) &&
                         s.groups[s.target].reward_seen == round && s.groups[s.target].mask.is_set(pos);
        if (!capturing && (live <= 3 || (live <= PR.campfoe && round - s.hit_round <= 2))) {
            g_mode = "campfoe";  // a fight: hit the rival or leave, never the camp
            if (tgt && fight_fav && tgt->d <= me.attack_range() + 1 && engage(s, me, tgt->c, tgt->p, true, false)) return;
            fight::back_off(s, me, foes, round);
            return;
        }
    }

    // 6. Farm camps.
    FP(11, "farm");
    g_mode = "farm";
    farm(s, me, round, camps);

    // Free hit on any enemy that ended up in reach.
    if (tgt && me.can_attack()) basic_attack(s, me, tgt->c, tgt->p);
}

const char* slot_name(Slot k) {
    switch (k) {
        case Slot::Reset: return "reset";
        case Slot::Dash: return "dash";
        case Slot::Targeted: return "target";
        case Slot::Ground: return "ground";
        case Slot::Heal: return "heal";
        case Slot::Shield: return "shield";
        default: return "none";
    }
}

void log_init(State& s) {
    std::printf("[init] %s melee=%d ally=%d groups=%zu altars=%zu spawn=%zu shards=%zu slots=%s/%s pots=%zu sm=%zu\n",
                s.name.c_str(), s.melee ? 1 : 0, s.ally_idx, s.groups.size(), s.altars.size(),
                s.spawn_tiles.size(), s.shards.size(), slot_name(s.slots[0]), slot_name(s.slots[1]), s.pots.size(),
                bc::shared_memory.size());
#ifdef P_RANGES
    attempt([&] {
        bc::champion& me = bc::self();
        auto abs = me.abilities();
        for (int k = 0; k < 2; ++k) {
            auto inf = abs[k].info();
            if (!inf) continue;
            std::visit([&](auto& x) {
                using T = std::decay_t<decltype(x)>;
                float r = -1, rad = -1, mod = -1; int dur = -1;
                if constexpr (requires { x.range; }) r = x.range;
                if constexpr (requires { x.radius; }) rad = x.radius;
                if constexpr (requires { x.modifier; }) mod = x.modifier;
                if constexpr (requires { x.duration; }) dur = x.duration;
                std::printf("[range] %s slot%d %s range=%.1f radius=%.1f mod=%.2f dur=%d cd=%d atk_range=%.1f\n", s.name.c_str(), k,
                            slot_name(s.slots[k]), r, rad, mod, dur, x.max_cooldown, static_cast<float>(me.attack_range()));
                (void)sizeof(T);
            }, *inf);
        }
        return true;
    });
#endif
    if (s.hold >= 0 && s.ally_idx <= 0) {
        int n = 0;
        for (char h : s.hold_group) n += h;
        std::printf("[hold] altar %d,%d groups %d\n", X(s.altars[s.hold]), Y(s.altars[s.hold]), n);
    }
#ifdef P_MAPDUMP
    if (s.ally_idx <= 0) {
        static char grid[64][65];
        for (auto& r : grid) { std::memset(r, '.', 64); r[64] = 0; }
        int W = 0, H = 0;
        auto put = [&](const std::vector<vec2>& v, char c) {
            for (auto t : v) if (X(t) >= 0 && X(t) < 64 && Y(t) >= 0 && Y(t) < 64) { grid[Y(t)][X(t)] = c; W = std::max(W, X(t) + 1); H = std::max(H, Y(t) + 1); }
        };
        put(bc::map::walls().positions(), '#');
        put(bc::map::holes().positions(), 'o');
        put(bc::map::altars().positions(), 'A');
        put(s.my_spawn.positions(), 'S');
        put(s.en_spawn.positions(), 'E');
        for (std::size_t i = 0; i < s.groups.size(); ++i) put(s.groups[i].tiles, static_cast<char>(i < 26 ? 'a' + i : 'A' + i - 26));
        for (int y = 0; y < H; ++y) { grid[y][W] = 0; std::printf("[map] %s\n", grid[y]); }
    }
#endif
#ifdef P_DBGT
    if (s.ally_idx <= 0) {
        namespace K = bc::constants;
        std::printf("[const] capture=%d sleep=%d respawn=%d recall=%d submit_mult=%.3f submit_base=%d submit_min=%d submit_range=%d passive_gold=%u\n",
                    (int)K::capture_time, (int)K::camp_sleep_time, (int)K::respawn_time, (int)K::recall_time,
                    K::submit_gem_duration_multiplier, (int)K::submit_gem_base_duration, (int)K::submit_gem_minimum_duration,
                    (int)K::submit_gems_range, (unsigned)K::passive_gold);
        for (std::size_t i = 0; i < s.groups.size(); ++i) {
            auto& g = s.groups[i];
            std::printf("[group] g%zu at (%d,%d) gems=%d gold=%d hp=%.0f str=%.0f members=%d mono=%d respawn=%d dmine=%d den=%d\n", i,
                        X(g.center), Y(g.center), g.gems, g.gold, g.hp, g.str, g.members, g.monolith ? 1 : 0, (int)g.respawn,
                        dist(g.center, s.spawn_center), dist(g.center, s.en_center));
        }
    }
#endif
    std::fflush(stdout);
}

void log_status(State& s) {
    attempt([&] {
        int round = static_cast<int>(bc::round_number());
#ifdef P_DBGT
        bool every = round >= P_DBGT && round < P_DBGT + P_DBGT_LEN;
#else
        bool every = false;
#endif
        if (P_TRACE) {
            bc::champion& me = bc::self();
            vec2 p = me.is_alive() ? me.position() : vec2(-1, -1);
            int rw = 0;  // groups with a waiting reward within 3 tiles of us
            if (me.is_alive())
                for (auto& g : s.groups)
                    if (g.reward_seen == round) { int d = 99; for (auto t : g.tiles) d = std::min(d, dist(p, t)); if (d <= 3) ++rw; }
            std::printf("T %d %d %d %d %d %.0f %u %u %s %s %d %d %d %d %d %d %d\n", round, s.ally_idx, X(p), Y(p),
                        me.is_alive() ? 1 : 0, me.is_alive() ? 100.0 * me.health() / me.max_health() : 0.0,
                        me.gem_count(), me.gold_count(), g_mode, g_farm, s.target, g_rew, rw, g_nf, g_nfoes, g_nal,
                        (me.is_recalling() ? 1 : 0) | (me.is_submitting_gems() ? 2 : 0));
            std::fflush(stdout);
            g_nf = 99; g_nfoes = 0; g_nal = 0; g_rew = 0;
            return true;
        }
        if (round % STATUS_EVERY != 0 && round > 3 && !every) return false;
        if (P_FUELGUARD && !fuel_ok(12000)) return false;  // a log line is not worth a turn cut short
        bc::champion& me = bc::self();
        vec2 p = me.position();
        std::printf("[r%d] %s pos=(%d,%d) hp=%.0f/%.0f gems=%u gold=%u mode=%s farm=%s target=%d errs=%d fuel=%llu\n",
                    round, s.name.c_str(), X(p), Y(p), me.health(), me.max_health(), me.gem_count(),
                    me.gold_count(), g_mode, g_farm, s.target, g_errors,
                    static_cast<unsigned long long>(bc::fuel_remaining()));
        std::fflush(stdout);
        return true;
    });
}

// P_SWEEP: stun the closest foe that can reach us next round, else damage the weakest foe in range, else stun it.
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
int g_sw[6];  // turns with a foe within 4: total, can't cast, channel, gate skip, no ready spell, cast
void sweep_dbg(State& s) {
    bc::champion& me = bc::self();
    if (!s.ready || !me.is_alive()) return;
    bool near = false;
    attempt([&] {
        for (auto& c : bc::vision::champions(*s.en))
            if (c.is_alive() && dist(c.position(), me.position()) <= SPELL_RANGE && !s.en_spawn.is_set(c.position())) near = true;
        return true;
    });
    if (!near) return;
    ++g_sw[0];
    if (!me.can_cast()) ++g_sw[1];
    else if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) ++g_sw[2];
    else {
        bool ready = false;
        auto abs = me.abilities();
        for (int k = 0; k < 2; ++k)
            if ((s.slots[k] == Slot::Targeted || s.slots[k] == Slot::Ground) && abs[k].is_ready()) ready = true;
        if (!ready) ++g_sw[4];
    }
    int r = static_cast<int>(bc::round_number());
    if (r % 50 == 0) std::printf("[swdbg] r=%d %s near=%d cantcast=%d channel=%d gate=%d noready=%d cast=%d mode=%s\n", r, s.name.c_str(), g_sw[0], g_sw[1], g_sw[2], g_sw[3], g_sw[4], g_sw[5], g_mode);
}
#endif

// pre = before the turn's move (P_SWEEP >= 3). P_SWEEP 5: a spell that roots us for the round is cast before
// moving only when standing is safe (hp >= 50%, no foe within 2, not outnumbered within 5); other spells always.
void spell_sweep(State& s, bool pre = false, bool free_only = false) {
    bc::champion& me = bc::self();
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
    sweep_dbg(s);
#endif
    if (!s.ready || !me.is_alive() || !me.can_cast()) return;
    if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) return;
    if (!fuel_ok(6000)) return;
    vec2 pos = me.position();
    std::vector<Foe> foes;
    for (auto& c : bc::vision::champions(*s.en))
        attempt([&] {
            if (!c.is_alive()) return false;
            Foe f{c, c.position(), c.health(), 0, 0, false};
            f.d = dist(f.p, pos);
            if (f.d > SPELL_RANGE || s.en_spawn.is_set(f.p)) return false;
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            foes.push_back(f);
            return true;
        });
    if (foes.empty()) {
        const bool roots_allowed = !P_CASTSAFE && !P_UNI_STAND && P_SWEEP != 5;
        if (cm_edge_aoe(s, me, roots_allowed, false, free_only)) g_mode = "sweep";
        return;
    }
    bool stand_ok = true;
    if (P_SWEEP == 5 && pre) {
        int nf = 0, na = 1;
        attempt([&] {
            for (auto& c : bc::vision::champions(*s.en))
                if (c.is_alive() && dist(c.position(), pos) <= 5) ++nf;
            for (auto& a : bc::vision::champions(*s.my))
                if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 4) ++na;
            return true;
        });
        for (auto& f : foes)
            if (f.d <= 2) stand_ok = false;
        if (me.health() < 0.5f * me.max_health() || nf > na + P_SW5_OUT || na < P_SW5_ALLY) stand_ok = false;
    }
    // P_UNI_STAND: with the caster draft, a spell that roots us is cast before moving only when no melee foe can
    // reach us next round and we have P_UNI_STAND_HP% hp; else we step first (v27's Stellar died from 60%+ hp in
    // 50 of 83 deaths, rooted by its own casts while melee closed from 4 to 1 tiles; the #1's Stellar holds 4-5)
    bool guard = pre && (P_SWEEP == 5 || (P_UNI_STAND && s.casters));
    if (P_UNI_STAND && s.casters && pre) {
        if (me.health() < P_UNI_STAND_HP / 100.0f * me.max_health()) stand_ok = false;
        for (auto& c : bc::vision::champions(*s.en))
            attempt([&] {
                if (!c.is_alive() || s.en_spawn.is_set(c.position())) return false;
                Foe f{c, c.position(), c.health(), dist(c.position(), pos), 0, false};
                if (f.d <= 2 || (c.attack_range() <= 1 && f.d <= fight::reach(f))) stand_ok = false;
                return true;
            });
    }
    // P_CASTSAFE: should this turn escape instead of standing to cast a spell that roots us?
    bool escape = false;
    if (P_CASTSAFE && pre) {
        float hpr = me.health() / std::max(1.0f, me.max_health());
        if (hpr * 100 < ((P_UNI_FLEE && P_DRAFTUNI && s.casters) ? P_UNI_FLEE : P.flee_pct)) {
            escape = true;  // play_turn will run or recall this round: a rooting cast would cancel the step
        } else {
            std::vector<Threat> th;
            attempt([&] {
                for (auto& c : bc::vision::champions(*s.en)) {
                    if (!c.is_alive() || s.en_spawn.is_set(c.position())) continue;
                    int ar = static_cast<int>(c.attack_range());
                    th.push_back(threat_of(c, c.position(), ar <= 1 ? 2 : ar + 1));
                }
                return true;
            });
            double here = danger_at(th, pos), lim = me.health() * P_CASTSAFE / 100.0;
            if (here >= lim) {
                for (int dx = -1; dx <= 1 && !escape; ++dx)
                    for (int dy = -1; dy <= 1 && !escape; ++dy) {
                        vec2 t = pos + vec2(dx, dy);
                        if ((!dx && !dy) || !bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                        if (danger_at(th, t) < std::min(lim, 0.7 * here)) escape = true;
                    }
            }
        }
    }
    auto kills = [&](int k, const Foe& t) {
        const SpellInfo& si = spells_of(me).k[k];
        double foc = 0;
        attempt([&] {
            foc = me.focus();
            return true;
        });
        return (si.kind == 2 || si.kind == 3) && si.mod * foc >= t.hp;
    };
    Foe* threat = nullptr;
    Foe* weak = nullptr;
    for (auto& f : foes) {
        if (f.d <= fight::reach(f) && (!threat || f.d < threat->d)) threat = &f;
        auto wsc = [&](const Foe& x) {  // P_SQUISHY: sparring only, prefer ranged targets (real caster teams hit our Stellar more)
            double v = x.hp - (x.channeling ? 300 : 0) - 5.0 * x.gems;
            if (P_SQUISHY) attempt([&] { if (x.c.attack_range() > 1) v -= P_SQUISHY; return true; });
            return v;
        };
        if (!weak || wsc(f) < wsc(*weak)) weak = &f;
    }
    if (P_SWEEP == 4) {  // before the turn: only when we were hit lately, a foe can reach us, or the foe is hurt / channeling
        const int round = static_cast<int>(bc::round_number());
        bool fighting = round - s.hit_round <= 3 || weak->channeling || threat;
        float mh = 0;
        attempt([&] {
            mh = weak->c.max_health();
            return true;
        });
        if (mh > 0 && weak->hp < 0.6f * mh) fighting = true;
        if (!fighting) return;
    }
    if (s.sweep == 2) {  // only in a fight: we were hit, we are in a fight mode, or the foe is hurt / channeling
        const int round = static_cast<int>(bc::round_number());
        std::string m = g_mode;
        bool fighting = round - s.hit_round <= 3 || weak->channeling ||
                        !(m == "farm" || m == "tribute" || m == "recall-shop" || m == "walk-home" || m == "unstick");
        float mh = 0;
        attempt([&] {
            mh = weak->c.max_health();
            return true;
        });
        if (mh > 0 && weak->hp < 0.6f * mh) fighting = true;
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
        if (!fighting) ++g_sw[3];
#endif
        if (!fighting) return;
    }
    auto abs = me.abilities();
    bool cast = false;
    auto try_use = [&](bool want_cc, Foe* t) {
        for (int k = 0; k < 2 && !cast; ++k) {
            auto& ab = abs[k];
            if (s.slots[k] != Slot::Targeted && s.slots[k] != Slot::Ground) continue;
            bool cc = attempt([&] { return ab.is_cc(); });
            if (cc != want_cc || !ab.is_ready()) continue;
            if (free_only && slot_exclusive(s, me, k)) continue;
            bool ex = guard && slot_exclusive(s, me, k);
            if (ex && pre && !stand_ok) continue;
            if (escape && slot_exclusive(s, me, k) && !kills(k, *t)) {
#ifdef P_FXLOG
                std::printf("[cs] r=%d %s skip slot%d hp=%.0f\n", static_cast<int>(bc::round_number()), s.name.c_str(), k, me.health());
#endif
                continue;
            }
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 3
            try {
                bool ok = s.slots[k] == Slot::Targeted ? ab.use(t->c) : ab.use(t->p);
                if (!ok) std::printf("[swfail] r=%d %s slot%d returned false d=%d\n", static_cast<int>(bc::round_number()), s.name.c_str(), k, t->d);
                cast = ok;
            } catch (const std::exception& e) {
                std::printf("[swfail] r=%d %s slot%d d=%d: %s\n", static_cast<int>(bc::round_number()), s.name.c_str(), k, t->d, e.what());
            }
            continue;
#endif
            if (s.slots[k] == Slot::Targeted) {
                if (!attempt([&] { return ab.can_target_enemies(); })) continue;
                cast = attempt([&] { return ab.use(t->c); });
            } else {
                vec2 c = P_AOE ? aoe_centre(s, me, k, t->p) : t->p;
                cast = attempt([&] { return ab.use(c); });
            }
            if (cast && ex && pre) s.rooted_r = static_cast<int>(bc::round_number());
        }
    };
    if (threat) try_use(true, threat);
    if (!cast && P_AOE >= 2) {  // an area spell that covers 2+ foes beats a single-target one
        for (int k = 0; k < 2 && !cast; ++k) {
            if (s.slots[k] != Slot::Ground || aoe_slot(me, k).radius <= 0 || !abs[k].is_ready()) continue;
            if (free_only && slot_exclusive(s, me, k)) continue;
            bool ex = guard && slot_exclusive(s, me, k);
            if (ex && pre && !stand_ok) continue;
            if (escape && slot_exclusive(s, me, k) && !kills(k, *weak)) continue;
            int hits = 0;
            vec2 c = aoe_centre(s, me, k, weak->p, &hits);
            if (hits < 2) continue;
            cast = attempt([&] { return abs[k].use(c); });
            if (cast && ex && pre) s.rooted_r = static_cast<int>(bc::round_number());
        }
    }
    if (!cast) try_use(false, weak);
    if (!cast) try_use(true, weak);
    if (!cast) cast = cm_edge_aoe(s, me, !guard || stand_ok, guard && pre, free_only, escape);
#ifdef P_SWEEP_LOG
    if (cast) std::printf("[sweep] r=%d %s mode=%s hit=%d tgt_d=%d canmove=%d canatk=%d\n", static_cast<int>(bc::round_number()), s.name.c_str(), g_mode,
                          static_cast<int>(bc::round_number()) - s.hit_round, weak->d, me.can_move() ? 1 : 0, me.can_attack() ? 1 : 0);
#endif
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
    if (cast) ++g_sw[5];
#endif
    if (cast) g_mode = "sweep";
}

// P_SWEEP 5: we cast a rooting spell this round, so the turn's steps failed: shoot the weakest foe in reach.
void shoot_rooted(State& s) {
    bc::champion& me = bc::self();
    if (!me.is_alive() || !me.can_attack()) return;
    vec2 pos = me.position();
    std::vector<Foe> foes;
    for (auto& c : bc::vision::champions(*s.en))
        attempt([&] {
            if (!c.is_alive() || s.en_spawn.is_set(c.position())) return false;
            foes.push_back(Foe{c, c.position(), c.health(), dist(c.position(), pos), 0, false});
            return true;
        });
    shoot_back(s, me, foes);
}

#include "utility.h"

[[noreturn]] void run_game() {
    State s;
    bool logged_init = false;
    for (;;) {
        g_mode = "?";
        g_farm = "-";
        try {
#if P_FUELPROF
            fp_begin();
#endif
            if (s.sweep >= 3) spell_sweep(s, true);  // before moving: most targeted spells cannot be cast after a step
#ifdef P_DZLOG
            double dz0 = -1;
            auto dz_now = [&]() -> double {  // ready enemy damage on our tile next round (fight.h volley model)
                double out = -1;
                attempt([&] {
                    bc::champion& me = bc::self();
                    if (!s.ready || !me.is_alive()) return false;
                    std::vector<Threat> th;
                    for (auto& c : bc::vision::champions(*s.en)) {
                        if (!c.is_alive() || s.en_spawn.is_set(c.position())) continue;
                        int ar = static_cast<int>(c.attack_range());
                        th.push_back(threat_of(c, c.position(), ar <= 1 ? 2 : ar + 1));
                    }
                    out = danger_at(th, me.position());
                    return true;
                });
                return out;
            };
            dz0 = dz_now();
#endif
            play_turn(s);
            FP(12, "post-sweep");
#ifdef P_DZLOG
            {
                double dz1 = dz_now();
                attempt([&] {
                    bc::champion& me = bc::self();
                    if (dz1 > 0 || dz0 > 0)
                        std::printf("[dz] %d %s %s %.0f %.0f %.0f\n", static_cast<int>(bc::round_number()), s.name.c_str(), g_mode, me.health(), dz0, dz1);
                    return true;
                });
            }
#endif
            if (s.sweep && s.sweep < 3) spell_sweep(s);
#ifdef P_CDPROBE
            attempt([&] {  // can we read enemy spell cooldowns?
                bc::champion& me = bc::self();
                if (!s.ready || !me.is_alive()) return false;
                for (auto& c : bc::vision::champions(*s.en)) {
                    if (!c.is_alive()) continue;
                    auto abs = c.abilities();
                    for (int k = 0; k < 2; ++k) {
                        int cd = -9;
                        std::string err;
                        try { cd = abs[k].cooldown(); } catch (const std::exception& e) { err = e.what(); }
                        float mod = -1, rg = -1;
                        int kind = -1;
                        try {
                            auto inf = abs[k].info();
                            if (inf) std::visit([&](auto& x) {
                                using T = std::decay_t<decltype(x)>;
                                kind = static_cast<int>(T::kind);
                                if constexpr (requires { x.modifier; }) { mod = x.modifier; rg = x.range; }
                                if constexpr (requires { x.exclusive_with_movement; }) { if (x.exclusive_with_movement) kind += 100; }
                                if constexpr (requires { x.duration; }) { kind += 1000 * x.duration; }
                                if constexpr (requires { x.radius; }) { rg += 100 * x.radius; }
                            }, *inf);
                        } catch (...) {}
                        std::printf("[cd] r=%d %s sees enemy %s slot%d cd=%d kind=%d mod=%.2f rg=%.1f foc=%.0f str=%.0f hp=%.0f %s\n", static_cast<int>(bc::round_number()), s.name.c_str(),
                                    bc::to_string(c.champion_name()).c_str(), k, cd, kind, mod, rg, c.focus(), c.strength(), c.health(), err.c_str());
                    }
                }
                return true;
            });
#endif
#ifdef P_MODELOG
            attempt([&] {  // mode of every turn with an enemy champion within 4 (not on its spawn)
                bc::champion& me = bc::self();
                if (!s.ready || !me.is_alive()) return false;
                int nd = 99;
                for (auto& c : bc::vision::champions(*s.en))
                    if (c.is_alive() && !s.en_spawn.is_set(c.position())) nd = std::min(nd, dist(c.position(), me.position()));
                if (nd <= 4) std::printf("[cm] %s %s %d\n", s.name.c_str(), g_mode, nd);
                return true;
            });
#endif
            if (s.sweep == 5) {
                if (s.rooted_r == static_cast<int>(bc::round_number())) shoot_rooted(s);
                spell_sweep(s);  // spells that still work after our step
            }
            // Newly revealed targets after moving were not in the pre-sweep.
            // This optional extra pass only uses movement-compatible spells.
            if (P_U34_POST_FREE && s.sweep >= 3 && s.sweep != 5 && fuel_ok(12000))
                spell_sweep(s, false, true);
            if (P_R5_LOCK) r5_altar_lock(s);
            if (P_R5_WARD) r5_personal_ward(s);
        } catch (const std::exception& e) {
            note_error(e.what());
        } catch (...) {
            note_error("unknown exception in turn");
        }
        FP(13, "log");
        if (s.ready && !logged_init && (!P_FUELGUARD || fuel_ok(20000))) {
            logged_init = true;
            log_init(s);
        }
#if P_FUELPROF
        FP(14, "end");
        debug_block({
            int r = static_cast<int>(bc::round_number());
            unsigned long long tot = 0;
            for (auto t : g_fp_turn) tot += t;
            if (g_fp_over || tot > 70000) {
                std::printf("[heavy] r=%d %s mode=%s farm=%s over=%s total=%llu", g_fp_round, s.name.c_str(), g_mode, g_farm,
                            g_fp_where >= 0 ? g_fp[g_fp_where].name : "-", tot);
                for (int i = 0; i < 32; ++i)
                    if (g_fp_turn[i] > 3000) std::printf(" %s=%llu", g_fp[i].name, g_fp_turn[i]);
                std::printf("\n");
            }
            if (r % 100 == 0 || r == 1) {
                std::printf("[fuel] r=%d %s", r, s.name.c_str());
                for (auto& c : g_fp)
                    if (c.n || c.over) std::printf(" | %s n=%llu avg=%llu max=%llu over=%llu", c.name, c.n, c.n ? c.sum / c.n : 0, c.mx, c.over);
                std::printf("\n");
            }
        });
#endif
        log_status(s);
        bc::end_turn();
    }
}

}  // namespace

int main() {
    if (bc::is_draft()) run_draft();
    run_game();
}

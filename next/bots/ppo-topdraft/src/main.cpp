// ppo-topdraft-v3: assemble around one reachable rally tile, then latch the team assault; expect objective captures.
// team-fight-v1 (design: analysis/claude-api-2026-10-18/team_fight_design_1019.md): recall-api-v1 + P_TEAM_FIGHT (finish layer,
// below) + P_HP_SHOP (hp shards at the top teams' hp share on the v72 power path).
// Finish layer: the no-chase doctrine lifted for hurt rivals. The bot let hurt rivals go by
// design (P_NOCHASE: a rival walking away is a finished fight; P_NOCHASE2: a low or channelling rival is never walked
// after) while the rivals finish ours: same damage traded, their hurt champion near us dies within 8 rounds 17%, ours 41%
// (death_root_cause_1019.md 9a). Now the team finishes the weakest hurt or recalling rival: a champion with half hp or
// more goes after it when it is within 4, or within 7 while one of our champions is already within 3 of it, and keeps
// after it 4 rounds. Everybody picks the same target (lowest hp share in the shared vision).
// chase-v1 (folded in): recall-api-v1 + P_CHASE (death_root_cause_1019.md section 9a): a healthy champion goes after a hurt or
// recalling rival within 4 and keeps after it for up to 4 rounds. Their hurt champion near ours: we kill it within 8 rounds
// 17% of the time, they kill ours 41% (W 32%); we step away 30% vs 18%. Unlike kill-api-v1b (hit a <=40% rival in reach,
// step in only when not outnumbered), chase-v1 triggers from 50% or on a recall, ignores the fight verdict/kite/farm modes
// that walked away from it, and follows the same target for 4 rounds.
// recall-api-v1: bank-v1b-clean (site v65) + rule 3 of analysis/claude-api-2026-10-18/data/findings_20261019-015018.md:
// no recall within P_RC_QUIET rounds of a hit or of seeing a rival within 6 (rivals step out of bushes and interrupt it).
// bank-v1b-clean: base-v53-clean + BK1 (a bank trip keeps its altar) with the real visible wait (a rival lock counts one full deposit).
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

#include <cambc.h>
#include "ppo-adapter.h"

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

namespace bc = cambc;
using bc::vec2;

namespace {

// ---------------------------------------------------------------------------
// Tunables. The draft bot writes these into draft memory; champions read them.
// ---------------------------------------------------------------------------
// Every switch and parameter (base-v53 cleanup: they all live in params.h).
#include "params.h"
// P_SWEEP 1: at the end of every turn, a ready damage/stun spell goes on an enemy champion within spell range
// (online vs the top 4 our casters had a spell ready in 52-70% of the rounds an enemy stood within 4; theirs 17-22%).
// 2 = the same, only in a fight. Tavi's, Ryth's and Cassi's spells cannot be cast after a step (engine error 126),
// so 1/2 rarely fire: 3 = cast before the turn's move, always; 4 = before the move, only when we were hit in the
// last 3 rounds, a foe can reach us, or the foe is hurt / channeling; 5 = before the move, but a spell that roots
// us for the round (exclusive_with_movement) only when standing is safe, then shoot; the rest again after the move.
// P_CASTSAFE N (2026-10-15 fix list): before the turn's move, a spell that roots us for the round
// (exclusive_with_movement) is not cast when this turn should escape: we are below the flee threshold (the turn
// will run or recall), or the enemy's ready damage on our tile next round reaches N% of our health and a
// neighbouring tile is clearly safer. A cast that kills its target is still made.
// P_AOE 1: ground area spells (Stellar's 1.4 x focus, radius 1) aim at the tile that covers the intended target
// and the most other enemy champions; 2: also cast the area spell before a single-target damage spell when it
// covers 2+ enemy champions (1.4 x 2 > 2.0).
// P_GROUP_W, so the pack meets all of us together. Needs P_DANGER. Nothing here depends on the map.
// P_FM_HOLD = rounds a ranged champion waits outside their range before going back to the old rules.
// P_VOLLEY N: volley-aware movement in every non-fight mode (farm, tribute, avoid, flee, shop...): a tile
// where the enemy's ready damage next round (danger_at) reaches N% of our health is a wall for pathing,
// and standing on one we first step to the neighbour with the least ready damage. 0 = off.
// P_CAPRECALL 1: when a recall is wanted and our target's reward is waiting, step on the capture tiles first
// and start the recall there (after P_CAPRECALL_DELAY turns on the tiles; capture and recall both take 5).
// Keep a safely claimable camp reward before a normal/nearby heal or shop recall.
// Enabled in params.h for an isolated A/B test; off reproduces prior behavior.
// P_PATHD 1: camp choice uses walking distances (distance fields) instead of straight-line distance;
// P_HOLD N: hold the contested centre (top-10 caster teams camp the centre altar on corners, collision and
// interlock and kill whoever comes to bank there). The hold point is a reachable altar about as far from both
// spawns with 2+ gem camp groups within P_HOLD_R. Camps there score x N/100 and ignore danger spots, and the
// altar ignores danger when we bank.
// P_NOCHASE 1 (the user, 2026-10-14 08:42: "we chase forever; a fight is over when they retreat or die,
// then go back to farming"): a foe that moved away from us since last round and is out of our attack range
// is not a target unless it carries P_CHASE_GEMS+ gems; nobody steps toward it.
// P_DRAFTUNI: the #1 team's (Univardisty, 2026-10-14) fight drafts by team size: 3 = Cassi&Issac, Ren, Stellar;
// 4 = + Tavi; 5 = Ryth, Stellar, Prism, Ren, Tavi. 1 = always; 2 = only when the spawn-to-spawn path is at most
// P_UNI_PATH (known fight maps 26-41, farm maps 49-85). P_SHOPUNI: Ren, Prism and Stellar buy power-f + durability-h.
// P_RECALL_NEAR N: recall (hurt or shopping) with the nearest foe N+ tiles away when we were not hit since our last
// turn; damage interrupts a recall, so the #1 recalls at 4-6 tiles out of a fight and 87% of its recalls finish.
// P_JACKPOT R: a group holding half the map's gems or more that is about as far from both spawns (stampede's centre)
// is left alone before round R, and gold clusters are farmed even with P_NOGOLD: the top teams buy ~9000 gold of
// items first and take it by force from r350-475; we walked in at r50 and died 27 times a game.
// P_JACKGO R: from round R the jackpot (P_JACKPOT) is a whole-team job, like P_MONO's monolith: P_JACKN champions
// commit to it (no "too strong" bail), wait at it while it respawns, and value it P_JACKW times. Online at 13:50 the
// top teams took it at r305-650 with 2-6 champions while we had 0-1 there (stampede 0-10).
// P_DANGER N: N+ enemy champions within 4 of each other mark a danger spot for P_DANGER_T rounds;
// camps within P_DANGER_R of it are skipped and altars near it cost 60 extra tiles (corners: a
// team camping the centre). Shared through byte 7 as the nearest altar when P_CALLHELP is off.
struct Params {
    int tribute_gems = P_TRIBUTE_GEMS;   // walk to an altar once carrying this many gems
    int recall_pct = P_RECALL_PCT;       // recall below this % health when safe
    int flee_pct = P_FLEE_PCT;           // run for spawn below this % health
    int late_round = P_LATE_ROUND;       // after this round, tribute any gems at all
};
Params P;

inline bool stage7_budget_active=false,stage7_budget_yielding=false;
inline unsigned stage7_yields=0;
struct Stage7TurnBudget {};
__attribute__((noinline)) void stage7_budget_checkpoint() {
    if(stage7_budget_active && bc::fuel_remaining()<30000) {stage7_budget_yielding=true;throw Stage7TurnBudget{};}
}
constexpr std::uint64_t FUEL_RESERVE = 16000;
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
int g_nf = 99, g_nfoes = 0, g_nal = 0, g_rew = 0, g_tlive = -1;

// 2026-10-16 behaviour fixes (thread "fix teammate behaviours"). Each is a switch; 0 = the teammate's bot as sent.
// P_CAPHOME N: a reward of our camp is waiting within N steps and we want to go home (hurt / asked to heal):
//   step onto it and recall there, so the 5-round capture and the recall run together, instead of recalling or
//   walking away and leaving the loot (also: no tribute walk while that reward waits for us).
// P_CAMPFOE N: an enemy champion within 3 (or within N after it hit us in the last 2 rounds) means a fight: hit
//   it if the fight is favourable and it is in reach, else back off; never spend the turn on a camp.
// P_NOCHASE2 1: a low-health or channelling foe is only engaged within attack range + 1 (no walking after it),
//   unless it carries P_CHASE_GEMS+ gems (the user's doctrine: chase only a big bag).
// P_NEEDHEAL R: waiting for a squad (rally) or for health that no recall will bring (need-heal with 80%+ health or
//   no safe recall) lasts at most R rounds: the camp is dropped for a while and another one is chosen.
// P_KITEALLY R: kiting steps toward the nearest ally within R tiles (60 a tile past 2), not only toward allies
//   already within 6.
// P_BACKHOME M: right after a tribute at a contested altar (distances to both spawns within M), recall home if
//   there is no camp to take or the next camp is contested too and (we saw a foe in the last 20 rounds or are
//   below 80% health); walk home if a recall is not safe.
// P_CAPPRIO R: who stays on a reward (the gold and gems go to whoever stands on it): Stellar first (if she claims it
//   within R tiles or stands next to it), then the other casters, then Ren, the tanks last; ties by distance, then
//   roster index. A lower-priority champion keeps the capture going until the higher one is on the tiles, then steps off.
// P_TWINFARM R: Issac farms Cassi's camp (they share one life; online-like local games: 33 of 82 pair deaths came
//   with Issac alone 9+ tiles from Cassi). With no camp claimed by Cassi he walks back to within R of her.
// P_NOLEAVE N (the user, 2026-10-16 17:17): a reward of our camp waiting within N tiles is never left behind, except
//   when staying kills us (the foes' ready damage on our tile, three rounds of it, reaches our health, or we are under
//   15%) or an ally with more right to the gold takes it (P_ONE_CAP / P_CAPPRIO). We step on, shoot whoever is in
//   range without moving, and recall on the tiles when we wanted to go home (capture and recall together).
// P_CACHE 1 (with P_NOLEAVE): a tank that sees a waiting reward posts it in shared bytes 5-6 (group + 1, then 251 +
//   (round / 16) & 3) instead of taking it; casters and Ren read it as a free reward for 32 rounds and go for it.
// P_OUTNUM R (the user, 2026-10-16 17:20: corners, Tavi 4 tiles from 3 foes with her allies far away walks toward
//   them and dies): outnumbered by 2+ within R (allies that are recalling do not count), we back off instead of
//   kiting, farming or walking on, unless the foe in reach dies to our next hit.
// P_DPSFARM 1 (the user, 2026-10-16 17:56: "farming is meant for the DPS to collect and nobody else"): only the DPS
//   (casters and Ren) capture camps. A tank never chooses its own camp while a DPS has one claimed: it goes to the
//   DPS's camp nearest to it (Issac to Cassi's), helps kill it and steps off the reward; a reward a tank is left
//   with is posted in the cache (P_CACHE bytes) for the DPS. DPS do not count tank claims when choosing.
// P_AVOIDFIRST 1 (GA genome b672ef97f6, the user 18:11 idea 6): decide to back off before taking the front line.
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
    } catch (const std::exception& e) { if(stage7_budget_yielding)throw; 
        note_error(e.what());
        return false;
    } catch (...) { if(stage7_budget_yielding)throw; 
        note_error("unknown exception");
        return false;
    }
}

// P_FUELGUARD 1: stop turns running out of fuel. A turn that runs out is suspended and the rest of it plays in the
// champion's next turn, on last round's data, so a champion loses one or two rounds each time (online: ~10 a game,
// 60+ on lanes). With unlimited fuel the decisions are the same as without it (154 of 154 map sides identical):
//  - cheaper, same result: one search instead of one per altar at start-up; walking distances to the camp groups
//    kept while we stand still (capturing); allies out of vision skipped before position() throws in
//    other_captures; the reward-evacuation check reads the camps near us instead of every visible camp;
//  - when the turn cannot pay for it: start-up finishes over the first turns (the champion waits on its spawn), an
//    optional camp re-choice waits for a later turn, log lines are skipped, and the low-fuel fallback step is a
//    plain greedy step instead of one more path search.
#define FP(i, name) ((void)0)
#define FP_SCOPE(i, name) ((void)0)

std::string norm(const std::string& s) {
    std::string o;
    for (char c : s) { stage7_budget_checkpoint(); 
        if (c >= 'A' && c <= 'Z') o += static_cast<char>(c - 'A' + 'a');
        else if (c >= 'a' && c <= 'z') o += c;
    }
    return o;
}

bool starts_with(const std::string& s, const std::string& p) { return s.rfind(p, 0) == 0; }

#include "de_rules.h"
int g_de_map = 0;  // Public geometry family, transported in draft-memory byte28.

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
    std::array<std::byte, 32> buf{};
    buf[0] = std::byte{'C'};
    buf[1] = std::byte{'M'};
    buf[2] = std::byte{'B'};
    buf[3] = std::byte{'1'};
    std::size_t n = std::min<std::size_t>(roster.size(), 16);
    buf[4] = static_cast<std::byte>(n);
    for (std::size_t i = 0; i < n; ++i) buf[5 + i] = static_cast<std::byte>(roster[i]);
    buf[28] = static_cast<std::byte>(g_de_map);
    buf[24] = static_cast<std::byte>(P.tribute_gems);
    buf[25] = static_cast<std::byte>(P.recall_pct);
    buf[26] = static_cast<std::byte>(P.flee_pct);
    buf[27] = static_cast<std::byte>(P.late_round / 10);
    attempt([&] {
        bc::draft_memory_buffer dm;
        dm = std::span<const std::byte>(buf.data(), buf.size());
        return true;
    });
}

#include "mapplan.h"

[[noreturn]] void run_draft() {
    struct Opt {
        std::string name;
        bc::champion_draft value;
        std::uint8_t raw;
    };
    std::vector<Opt> all;
    for (std::uint32_t i = 0; i < 48; ++i) { stage7_budget_checkpoint(); 
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
    std::vector<const char*> prefs(std::begin(PREFS), std::end(PREFS));
    {
        int ts = 0, sp = -1;
        attempt([&] { ts = static_cast<int>(bc::draft::team_size()); return true; });
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
        bool fight_map = (sp >= 0 && sp <= P_UNI_PATH);
        std::printf("[draft] uni ts=%d spawn_path=%d fight=%d\n", ts, sp, fight_map ? 1 : 0);
        if (fight_map) {
            if (ts <= 3) prefs = {"cassi", "ren", "stellar"};
            else if (ts == 4) prefs = {"cassi", "ren", "stellar", "tavi"};
            else prefs = {"ryth", "stellar", "prism", "ren", "tavi"};
            for (const char* p : PREFS) prefs.push_back(p);  // fallbacks
        }
    }
    {  // mapplan.h: the draft read from map features
        MpDraftFeat f = mp_draft_features();
        auto chosen = mp_draft(f);
        std::printf("[mapplan] ts=%d altars=%d walls=%d %dx%d path=%d open=%d far_fight=%d\n", f.ts, f.altars, f.walls, f.w, f.h, f.path, f.open,
                    mp_far_fight(f) ? 1 : 0);
        if (!chosen.empty()) {
            prefs = std::move(chosen);
            for (const char* p : PREFS) prefs.push_back(p);  // fallbacks
        }
    }
    if (fuel_ok(12000)) g_de_map = v34de::probe();
    {
        auto chosen = v34de::recipe(g_de_map);
        if (!chosen.empty()) {
            prefs = std::move(chosen);
            for (const char* fallback : PREFS) prefs.push_back(fallback);
        }
    }
    // Observed on Patch 1.0.1 in five Intercontinental Fish games (rank #1):
    // 3 picks: Stellar, Heart of Ruin, Ren. 5 picks: + Cassi & Issac, Ryth.
    // Four picks use that priority's prefix; no four-pick leader game was observed.
    // Keep map probing above: gameplay still consumes g_de_map via draft memory.
    prefs = {"stellar", "heart", "ren", "cassi", "ryth"};
    for (const char* fallback : PREFS) prefs.push_back(fallback);
    std::printf("[draft] topdraft-v1: stellar heart ren cassi ryth (Fish, patch 1.0.1)\n");
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
    for (;;) { stage7_budget_checkpoint(); 
        for (std::size_t k = 0; k < order.size(); ++k) { stage7_budget_checkpoint(); 
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
        for (int k = 0; k < 2; ++k) { stage7_budget_checkpoint(); 
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
            } catch (...) { if(stage7_budget_yielding)throw; 
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
        for (int k = 0; k < 2; ++k) { stage7_budget_checkpoint(); 
            const SpellInfo& si = cs.k[k];
            if (!si.kind) continue;
            try {
                if (abs[k].cooldown() > 0) continue;
            } catch (...) { if(stage7_budget_yielding)throw; 
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
    for (auto& x : th) { stage7_budget_checkpoint(); 
        int d = dist(t, x.p);
        double sp = 0;
        if (d <= x.xr) sp = x.xd;
        if (d <= x.fr + 1) sp = std::max(sp, x.fd);
        sum += sp + (d <= x.ar ? x.atk : 0.0);
        if (d <= x.sr + 1) stun = true;
    }
    if (stun)  // stunned for a round: the ready casters one step out get to stand and cast after
        for (auto& x : th) { stage7_budget_checkpoint(); 
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
    // BK1: the altar this bank trip keeps (index), the last round the trip banked, its walk when it started
    int bt_altar = -1, bt_last = -1000, bt_start_len = -1;
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
    std::optional<vec2> objective_stage;
    int objective_release_cycle = -1;
    int sole_gem_group = -1;  // public map geometry: exactly one gem-paying camp group
    bool mono_only = false;  // P_MONO: every gem on the map sits in a monolith group
    bool jackpot_map = false;  // P_JACKPOT: a jackpot group exists, so gold clusters are worth farming before it
    std::vector<Shard> shards;
    std::vector<bc::item_type> fallback_items;
    std::optional<bc::champion> chase;  // P_CHASE: the rival we are after
    int chase_until = -1;
    int close_r = -1000;  // P_RC_QUIET: last round a rival champion was seen within 6
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
    // Unused since the cleanup, kept on purpose: removing them changes how much fuel building a State costs, and v53's
    // choices depend on the fuel left (fuel_ok), so the games would change (base-v53-clean check).
    int fm_hold = 0;
    std::vector<Threat> thr;         // P_VOLLEY: ready enemy damage around us this round
    bc::distance_field pdf;          // P_PATHD: walking distances from where we stand
    bc::distance_field tele_fa;      // unused, kept (see fm_hold)
    bc::bitboard tele_va;            // unused, kept (see fm_hold)
    int tele_sa = -1;                // unused, kept (see fm_hold)
    bc::bitboard pdv;
    vec2 pd_pos{-1, -1};             // P_FUELGUARD: where pd_gd was measured (walls never change, so it holds there)
    std::vector<int> pd_gd;          // P_FUELGUARD: walking distance to each camp group from pd_pos (-1 unreached)
    std::uint64_t ct_cost = 20000;   // P_FUELGUARD: the dearest choose_target so far
    int init_stage = 0;              // start-up parts done (init)
    int thr_r = -1;
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
inline std::vector<bc::champion> my_roster(State& s) {
    if (s.roster_my.empty()) s.roster_my = bc::champions(*s.my);
    return s.roster_my;
}
inline std::vector<bc::champion> en_roster(State& s) {
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
    std::size_t i0 = s.shop_next;
    for (std::size_t i = i0; i < n && fuel_ok(20000); ++i) { stage7_budget_checkpoint(); 
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
    // what the top teams buy: the monster emblem first, then power
    if (starts_with(s.name, "cassi"))
        s.plan = {{"monster", 'f', 1}, {"power", 'f', 99}};
    else if (starts_with(s.name, "ryth"))
        s.plan = {{"monster", 's', 1}, {"power", 's', 2}, {"jungle", 'h', 1}, {"power", 's', 99}};
    else
        s.plan = {{"monster", 's', 1}, {"power", 's', 3}, {"jungle", 'h', 1}, {"power", 's', 99}};
    if (!starts_with(s.name, "cassi"))  // Mite's tank build: survive camps solo, then raw power
        s.plan = {{"durab", 's', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 1}, {"power", 's', 99}};
    // what the top-10 winners buy (2026-10-14 study of 169 games)
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


    if ((starts_with(s.name, "ren") || starts_with(s.name, "prism") || starts_with(s.name, "stellar")))
        s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};  // the #1's casters: 8-13 power-f a game
    // One offensive opening emblem, then the complete original melee core.
    // Preserve Jungle camp mitigation and Bruiser health for later farming.
    if (starts_with(s.name, "ryth") || starts_with(s.name, "varg") || starts_with(s.name, "vendetta"))
        s.plan = {{"power", 's', 1}, {"durab", 's', 1}, {"jungle", 's', 1},
                  {"bruiser", 'h', 1}, {"power", 's', 99}};
    // O36_REPLACE_HOOK: one quota replaces one quota; no extra150-gold step.
    opening36::replace(s.plan, s.de_map, s.name, ((s.de_map == v34de::Rows) ? P_O36_REPLACE : 0));
}

// Start-up runs in three parts (map and camp groups, fixed walking distances, roles and shop). P_FUELGUARD lets a
// part wait for the next turn when this one cannot pay for it; with enough fuel all three run in the first turn.
void init_map(State& s, bc::champion& me) {
    FP_SCOPE(27, "init-start");
    s.my = me.team();
    s.en = bc::opponent(*s.my);
    s.my_spawn = bc::map::spawn_region(*s.my);
    s.en_spawn = bc::map::spawn_region(*s.en);
    s.static_block = bc::map::walls() | bc::map::holes() | bc::map::altars() | s.en_spawn;
    s.altars = bc::map::altars().positions();
    s.lock_until.assign(s.altars.size(), 0);
    s.altar_ok.assign(s.altars.size(), 1);
    FP(29, "init-altars");
    if (true)
        attempt([&] {  // one search from where we start; an altar is usable when a tile next to it is reached
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | bc::map::altars();
            bc::bitboard roots, seen;
            roots.set(me.position());
            bc::distance_field df;
            df.compute(wall, roots, seen);
            for (std::size_t i = 0; i < s.altars.size(); ++i) { stage7_budget_checkpoint(); 
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
            for (std::size_t i = 0; i < s.altars.size(); ++i) { stage7_budget_checkpoint(); 
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
        for (auto p : v) { stage7_budget_checkpoint();  sx += X(p); sy += Y(p); }
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
    s.groups.reserve(std::min<std::size_t>(raw_groups.size(), MAX_GROUPS));
    for (auto& g : raw_groups) { stage7_budget_checkpoint(); 
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
        for (auto& c : g.camps()) { stage7_budget_checkpoint(); 
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
    {
        bool other_gems = false, mono = false;
        for (auto& g : s.groups) { stage7_budget_checkpoint(); 
            if (g.monolith) mono = mono || g.gems > 0;
            else other_gems = other_gems || g.gems > 0;
        }
        s.mono_only = mono && !other_gems;
        int gem_groups = 0;
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            stage7_budget_checkpoint();
            if (s.groups[i].gems > 0) { ++gem_groups; s.sole_gem_group = i; }
        }
        if (gem_groups != 1) s.sole_gem_group = -1;
    }

}

void init_paths(State& s) {
    FP_SCOPE(22, "init-dist");
    attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn;
            bc::distance_field fs, fa;
            bc::bitboard vs, va, ar;
            fs.compute(wall, s.my_spawn & ~wall, vs);
            for (std::size_t i = 0; i < s.altars.size(); ++i)
                if (s.altar_ok[i]) ar.set(s.altars[i]);
            fa.compute(wall, ar, va);
            for (auto& g : s.groups) { stage7_budget_checkpoint(); 
                int bs = 1 << 20, ba = 1 << 20;
                for (auto t : g.tiles) { stage7_budget_checkpoint(); 
                    if (vs.is_set(t)) bs = std::min(bs, static_cast<int>(fs.get(t)));
                    if (va.is_set(t)) ba = std::min(ba, static_cast<int>(fa.get(t)));
                }
                g.spawn_pd = bs < (1 << 20) ? bs : -1;
                g.altar_pd = ba < (1 << 20) ? ba : -1;
            }
            return true;
        });
    attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.my_spawn;
            bc::distance_field fe;
            bc::bitboard ve;
            fe.compute(wall, s.en_spawn & ~wall, ve);
            int total = 0;
            for (auto& g : s.groups) total += g.gems;
            for (auto& g : s.groups) { stage7_budget_checkpoint(); 
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
}

void init_roles(State& s, bc::champion& me) {
    FP_SCOPE(25, "init-misc");
    attempt([&] {
            bool st = false;
            for (auto& a : my_roster(s))
                if (starts_with(norm(bc::to_string(a.champion_name())), "stellar")) st = true;
            s.casters = st;
            if (!st) s.sweep = 2;
            if (!st) s.rnear = 0;
            return true;
        });
    s.pot_group.assign(s.groups.size(), 0);
    s.hold_group.assign(s.groups.size(), 0);
    if (s.casters) {
        int bd = 1 << 30;
        for (std::size_t i = 0; i < s.altars.size(); ++i) { stage7_budget_checkpoint(); 
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
    for (int k = 0; k < 2; ++k) { stage7_budget_checkpoint(); 
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
        if (dm.size() >= 28 && dm[0] == std::byte{'C'} && dm[1] == std::byte{'M'} &&
            dm[2] == std::byte{'B'} && dm[3] == std::byte{'1'}) {
            if (dm.size() > 28) {
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
        if (!fuel_ok(35000)) return false;
        s.init_stage = 2;
        init_paths(s);
        if (false) mp_game_plan(s);  // only the rules that need it: off = v52 games
    }
    if (s.init_stage == 2) {
        if (!fuel_ok(50000)) return false;
        s.init_stage = 3;
        init_roles(s, me);
        if (s.dash_slot >= 0) mp_find_dashholes(s);  // mapplan_game.h rule 5
    }
    return true;
}

// ---------------------------------------------------------------------------
// Shopping
// ---------------------------------------------------------------------------
// P_HP_SHOP: hp shards at the top-10 winners' hp share of all shards (micro_top_shop.md: Issac durability-h 4.2 +
// bruiser-h 1.1 of ~33 shards, Varg 4.2 of 34, Ryth 8.3 of 24, Ren 9.5 of 38, Tavi 1.6 of 29); the rest follows the
// v72 plan. Our hp gained by r150-299 is Issac 0 vs 181, Varg 5 vs 237, Ryth 85 vs 460, Ren 240 vs 511.
template <class C>
const Shard* hp_pick(State& s, const C& counts) {
    float share = 0;
    const char* fam = "durab";
    if (starts_with(s.name, "issac")) share = 0.16f;
    else if (starts_with(s.name, "varg")) share = 0.12f;
    else if (starts_with(s.name, "ryth")) { share = 0.34f; fam = "bruiser"; }
    else if (starts_with(s.name, "ren")) { share = 0.25f; fam = "bruiser"; }
    else if (starts_with(s.name, "tavi")) share = 0.06f;
    if (share <= 0) return nullptr;
    float all = 0, hp = 0;
    const Shard* want = nullptr;
    for (auto& x : s.shards) { stage7_budget_checkpoint(); 
        float n = 0;
        attempt([&] { n = static_cast<float>(counts[x.shard] + 5 * counts[x.emblem]); return true; });
        all += n;
        if (x.stat == 'h') hp += n;
        if (!want && x.stat == 'h' && starts_with(x.family, fam)) want = &x;
    }
    if (!want || hp + 1 > share * (all + 1)) return nullptr;
    return want;
}

void shop(State& s, bc::champion& me) {
    for (int it = 0; it < 12 && fuel_ok(10000); ++it) { stage7_budget_checkpoint(); 
        if (me.gold_count() < 30) return;
        auto counts = me.item_count();
        const Shard* pick = nullptr;
        if (P_HP_SHOP) pick = hp_pick(s, counts);
        if (!pick) for (auto& st : s.plan) { stage7_budget_checkpoint(); 
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
            for (auto& t : s.fallback_items) { stage7_budget_checkpoint(); 
                ok = attempt([&] {
                    if (!me.can_buy(t, 1)) return false;
                    me.buy(t, 1);
                    return true;
                });
                if (ok) break;
            }
        }
        if (!ok) {
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
// P_VOLLEY_FARM 0: farming ignores it too (online v25 gave up camps on expanse/lanes with no deaths to save).
bool volley_mode(bc::champion& me) {
    if ((P_VOLLEY_FIGHT == 1 && me.attack_range() > 1)) return true;
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
        for (int dy = -1; dy <= 1; ++dy) { stage7_budget_checkpoint(); 
            if (!dx && !dy) continue;
            vec2 t = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
            int d = dist(t, to);
            if (d < bd) { bd = d; best = t; }
        }
    return best && attempt([&] { return me.move_absolute(*best); });
}

bc::bitboard mp_awake_camp_zone(State& s, vec2 pos);
int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos);
bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {
    FP_SCOPE(16, "step_towards");
    vec2 pos = me.position();
    bc::bitboard goals = goals_in & ~s.blocked;
    if (goals.is_empty() || goals.is_set(pos)) return false;
    if (!me.can_move() && !(use_dash && s.dash_slot >= 0)) return false;

    bc::bitboard vblock = s.blocked;  // P_VOLLEY: blocked plus lethal tiles
    bool vol_on = false;
    if (!s.thr.empty() && s.thr_r == static_cast<int>(bc::round_number()) && volley_mode(me)) {
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
                    for (int dy = -1; dy <= 1; ++dy) { stage7_budget_checkpoint(); 
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
                for (int dy = -P_VOLLEY_R; dy <= P_VOLLEY_R; ++dy) { stage7_budget_checkpoint(); 
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
        if (!fuel_ok(14000)) return greedy_step(s, me, best);  // move_towards is one more path search
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
    if (false) {  // mapplan_game.h rule 3: walk around awake camps we do not fight
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
    if (!ok_field) {  // corridor jammed by champions: plan through them
        ok_field = attempt([&] {
            bc::bitboard b2 = s.static_block | bc::vision::camp_tiles();
            b2.set(pos, false);
            s.df.compute_to(b2, goals_in & ~s.static_block, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    }
    if (!ok_field) return fallback();

    if (use_dash && s.dash_slot >= 0 && !s.mp_dashholes.is_empty() && fuel_ok(40000)) {
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
                for (int dy = -2; dy <= 2; ++dy) { stage7_budget_checkpoint(); 
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
        if (!moved && me.can_move()) {  // still stuck: any free tile that is not farther
            int here = s.df.get(pos);
            for (int dx = -1; dx <= 1 && !moved; ++dx)
                for (int dy = -1; dy <= 1 && !moved; ++dy) { stage7_budget_checkpoint(); 
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

template <class U>
bool cast_offense(State& s, bc::champion& me, const U& tgt, vec2 tpos, bool champ) {
    if (!me.can_cast() || dist(me.position(), tpos) > SPELL_RANGE) return false;
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) { stage7_budget_checkpoint(); 
        auto& ab = abs[k];
        if (s.slots[k] == Slot::Targeted) {
            if (!(champ ? ab.can_target_enemies() : ab.can_target_camps())) continue;
            if (ab.is_ready() && attempt([&] { return ab.use(tgt); })) return true;
        } else if (s.slots[k] == Slot::Ground) {
            if (!ab.is_ready()) continue;
            vec2 c = tpos;
            if (champ) c = aoe_centre(s, me, k, tpos);
            if (attempt([&] { return ab.use(c); })) return true;
        }
    }
    return false;
}

template <class U>
bool basic_attack(State& s, bc::champion& me, const U& requested, vec2 tpos) {
    U tgt=requested;if(me.can_attack()&&dist(me.position(),tpos)<=me.attack_range())tgt=ppo_target(requested);
    if (dist(me.position(), tpos) > me.attack_range() || !me.can_attack()) return false;
    if (false) return false;
    bool hit = attempt([&] {
        me.attack(tgt);
        return true;
    });
    // Preserve a reset cooldown when its only selected target disappeared.
    if (hit && s.reset_slot >= 0 && me.can_cast() &&
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
        acted = step_towards(s, me, ring, dash && true) || acted;
        acted = basic_attack(s, me, tgt, tpos) || acted;
    }
    return acted;
}

void support_spells(State& s, bc::champion& me, bool in_combat) {
    if (!me.can_cast()) return;
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) { stage7_budget_checkpoint(); 
        auto& ab = abs[k];
        if (s.slots[k] == Slot::Shield && in_combat && me.health() < 0.85f * me.max_health()) {
            if (ab.is_ready() && attempt([&] { return ab.use(); })) return;
        }
        if (s.slots[k] == Slot::Heal && ab.is_ready()) {
            for (auto& a : bc::vision::champions(*s.my)) { stage7_budget_checkpoint(); 
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


inline bool packed_claims(const State& s) {
    return s.roster == 6 && s.groups.size() <= 63;
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
        for (int k = 0; k < static_cast<int>(allies.size()) && k < 16; ++k) { stage7_budget_checkpoint(); 
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
std::vector<bc::camp> near_camps(State& s, vec2 pos) {
    // Cheap replacement for bc::vision::camps(): only groups near us, and only camps the
    // engine says are in vision (is_visible() reports hidden camps without throwing).
    std::vector<bc::camp> out;
    bc::bitboard tv;  // the engine's own "effective vision", the one state() checks
    if (!attempt([&] { bc::vision::visible_tiles_into(tv); return true; })) return out;
    for (auto& g : s.groups) { stage7_budget_checkpoint(); 
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
        attempt([&] {
            for (auto& c : g.obj->camps())
                if (c.is_visible()) out.push_back(c);
            return true;
        });
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
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) { stage7_budget_checkpoint(); 
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
                if (false) { s.mp_last_g = i; s.mp_last_r = round; }  // rule 9: captured next to us
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
int squad_needed(double hp_g, double str_g, double dps, double afford) {
    if (str_g <= 0) return 1;
    const bool focus = false;
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
    vec2 pos = me.position();
    const Foe* best = nullptr;
    for (auto& f : foes) { stage7_budget_checkpoint(); 
        if (f.hp <= 0 || dist(pos, f.p) > me.attack_range()) continue;
        if (!best || f.hp < best->hp) best = &f;
    }
    if (!best) return;
    basic_attack(s, me, best->c, best->p);
}

// Danger spot: an enemy pack (P_DANGER+ champions within 4 of each other) seen this turn, or
// one an ally reported in byte 7 (nearest altar index + 1, then round / 8, mod 32).
void update_danger(State& s, const std::vector<Foe>& foes, int round) {
    for (auto& f : foes) { stage7_budget_checkpoint(); 
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
      // byte 7 belongs to the help call then
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

bool grouped(const State& s, int round) { return false; }
bool ball_on(const State& s, int round) { return grouped(s, round); }

// A shared round clock gives every champion the same objective window without
// using the claim bytes (which already have owners). Gold farming and shopping
// remain available between pushes; healing and banking retain their priorities.
bool objective_window(const State& s, int round) {
    return s.sole_gem_group >= 0 && round >= P_OBJECTIVE_START &&
        (round - P_OBJECTIVE_START) % P_OBJECTIVE_PERIOD < P_OBJECTIVE_WINDOW;
}
int objective_target(State& s, bc::champion& me, int round) {
    if (!objective_window(s, round) || me.health() < 0.65f * me.max_health()) return -1;
    const auto& g = s.groups[s.sole_gem_group];
    if (g.spawn_pd < 0 || g.next_ok > round + 40) return -1;
    return s.sole_gem_group;
}

int choose_target_impl(State& s, bc::champion& me, int round);
// Assemble at one reachable home-side staging tile, not around the camp's
// bounding perimeter: a large grouped camp can extend far beyond its centre.
bool objective_assemble(State& s, bc::champion& me, int round) {
    if (objective_target(s, me, round) < 0) return false;
    const int cycle = (round - P_OBJECTIVE_START) / P_OBJECTIVE_PERIOD;
    if (s.objective_release_cycle == cycle) return false;
    const auto& g = s.groups[s.sole_gem_group];
    if (!s.objective_stage) {
        bc::bitboard outer, inner;
        for (auto t : g.tiles) { stage7_budget_checkpoint(); outer.draw_chebyshev(t, 7.0f); inner.draw_chebyshev(t, 4.0f); }
        bc::distance_field from_home;
        bc::bitboard reachable;
        from_home.compute(s.static_block, s.my_spawn & ~s.static_block, reachable, 200);
        int best = 1 << 20;
        for (auto t : (outer & ~inner & ~s.static_block & reachable).positions()) {
            stage7_budget_checkpoint();
            int d = static_cast<int>(from_home.get(t));
            if (d < best) { best = d; s.objective_stage = t; }
        }
        if (!s.objective_stage) return false;
    }
    int ready = 0;
    attempt([&] {
        for (auto& a : my_roster(s)) {
            stage7_budget_checkpoint();
            if (a.is_alive() && !a.is_recalling() && a.health() >= 0.5f * a.max_health() &&
                dist(a.position(), *s.objective_stage) <= 5) ++ready;
        }
        return true;
    });
    const int quorum = std::min(s.roster, std::max(2, (4 * s.roster + 4) / 5));
    if (ready >= quorum) {
        s.objective_release_cycle = cycle;
        std::printf("OBJ r=%d unit=%d group=%d ready=%d quorum=%d phase=assault\n", round, s.ally_idx, s.sole_gem_group, ready, quorum);
        return false;
    }
    if (round % 40 == 0) std::printf("OBJ r=%d unit=%d group=%d ready=%d quorum=%d phase=rally\n", round, s.ally_idx, s.sole_gem_group, ready, quorum);
    g_mode = "objective-rally";
    g_farm = "objective-rally";
    bc::bitboard goals;
    goals.draw_chebyshev(*s.objective_stage, 3.0f);
    step_towards(s, me, goals & ~s.static_block, true);
    return true;
}

// P_FUELGUARD: the dearest choose_target seen so far (it grows with the number of camp groups and with walls),
// so a caller can skip an optional re-choice when the turn could not pay for it plus a step afterwards.
int choose_target(State& s, bc::champion& me, int round) {
    if (int objective = objective_target(s, me, round); objective >= 0) return objective;
    if(!fuel_ok(s.ct_cost+12000)) {
        auto position=me.position();const auto sm=read_sm();int best=-1;double best_score=0;
        const auto strength=std::max(1.f,me.strength());const auto health=me.health();
        for(std::size_t j=0;j<s.groups.size()&&bc::fuel_remaining()>33000;j++) {
            const auto i=(j+std::size_t(round+s.ally_idx*13))%s.groups.size();const auto& g=s.groups[i];
            if(g.next_ok>round||g.bad_until>round)continue;
            if(g.str>0&&g.hp/strength*g.str>health*.65)continue;
            bool claimed=false;for(int k=0;k<claim_slots(s);k++)if(k!=s.ally_idx&&claim_value(s,sm,k)==int(i)+1)claimed=true;
            if(claimed)continue;
            const double score=(g.gems+g.gold*.25+1)/(dist(position,g.center)+5+g.hp/strength);
            if(score>best_score){best_score=score;best=int(i);}
        }
        return best;
    }
    std::uint64_t f0 = bc::fuel_remaining();
    int t = choose_target_impl(s, me, round);
    std::uint64_t f1 = bc::fuel_remaining();
    if (f0 > f1) s.ct_cost = std::max<std::uint64_t>(s.ct_cost, f0 - f1);
    return t;
}
bool can_choose(const State& s) { return fuel_ok(18000); }

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
            for (int k = 0; k < s.ally_idx && k < static_cast<int>(allies.size()); ++k) { stage7_budget_checkpoint(); 
                if (!allies[k].is_alive()) continue;
                if (k < claim_slots(s)) {
                    const int claim = claim_value(s, sm, k);
                    if (claim > 0) lead_group = claim - 1;
                }
                try { lead_p = allies[k].position(); } catch (...) { if(stage7_budget_yielding)throw; }
                break;
            }
            return true;
        });
    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();
    bool have_pd = cached || (P_PATHD && attempt([&] {  // walking distance from here to every camp group
        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;
    }));
    if (have_pd && !cached) {  // the walking distance to each group, read once per tile
        s.pd_gd.assign(s.groups.size(), -1);
        attempt([&] {
            for (std::size_t i = 0; i < s.groups.size(); ++i) { stage7_budget_checkpoint(); 
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
        if (s.pd_pos == pos && s.pd_gd.size() == s.groups.size()) {
            int b = s.pd_gd[static_cast<std::size_t>(&g - s.groups.data())];
            return b >= 0 ? b : d * 3 / 2;
        }
        int b = 1 << 20;
        for (auto t : g.tiles)
            if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
        return b < (1 << 20) ? b : d * 3 / 2;
    };
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) { stage7_budget_checkpoint(); 
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;
        bool held = s.hold_group[i];
        if (!held && round - s.danger_r <= P_DANGER_T && dist(g.center, s.danger_p) <= P_DANGER_R) continue;
        int wait = g.next_ok - round;  // > 0: respawning
        int gd = walk(g);
        const bool jack_go = g.jackpot && round >= P_JACKGO;
        if (wait > 0 && !(jack_go && wait <= gd + 40) && (g.monolith || wait > gd + P_RESPAWN)) continue;
        if (g.gems + g.gold <= 0) continue;
        if (g.jackpot && round < P_JACKPOT) continue;  // farm gold and buy first, as the top teams do (stampede: first visit r350-475)
        if (g.gems <= 0 && !s.mono_only && !s.jackpot_map) continue;  // gold-only clusters give no gems (but gold is the tiebreak where only monoliths give gems)
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
        if (mono_go) cap = free_reward ? 1 : s.roster;
        if (jack_go) cap = jack_n;
        if (g.str <= 0 && g.gems > 0) cap = P_PAIR;  // gem clusters: a pair kills twice as fast
        bool pot = false;
        if (pot) cap = std::max(cap, 2);
        if ((s.de_map == v34de::Monolith) && !free_reward) cap = std::min(cap, std::max(needed, P_R34_SHARE));
        if (free_reward) cap = 1;
        if (false) cap = std::max(cap, s.roster);
        if (claimers >= cap && i != s.target && !lead) continue;
        int team = std::max(1 + claimers, needed);
        double t_clear = free_reward ? 0.0 : g.hp / (dps * team);
        double incoming = g.str * t_clear / team;
        double travel = std::max(gd, wait);
        double cycle = 8.0 + (P_PATHD && g.spawn_pd >= 0 ? g.spawn_pd : dist(s.spawn_center, g.center));  // recall + heal + walk back
        double rounds = travel + t_clear + 6.0 + (incoming / mhp) * cycle;
        if ((s.de_map == v34de::Expanse || s.de_map == v34de::Monolith) && g.gems > 0 && g.altar_pd >= 0)
            rounds += ((s.de_map == v34de::Monolith ? 100 : P_R34_BANKCOST) / 100.0) * 2.0 * std::max(0, g.altar_pd - 1) / team;
        bool pack = false;  // opening: everybody on the best camp together
        double value = (g.gems + gold_w * g.gold) / (pack ? 1.0 : std::pow(static_cast<double>(team), ((g.monolith || g.hp < P_STACK_HP || false) ? 100 : P_SHAREEXP) / 100.0));  // big camps (P_STACK_HP+): a joiner keeps more of the value, so champions stack there
        double score = value / std::max(1.0, rounds);
        if (needed > 1 + claimers) score *= (false && P_MP_COMPANY) ? P_MP_COMPANY / 100.0 : 0.7;  // still needs company (rule 8)
        if (claimers > 0 && g.str == 0 && !(g.gems > 0 && claimers < P_PAIR) && !(pot && claimers < 2)) score *= pack ? 1.0 : 0.3;  // clusters are a solo job
        if (pot) score *= P_POT / 100.0;  // the centre pot pays 48 a pair next to the altar
        if (dist(g.center, s.en_center) < 8) score *= 0.6;    // stay off their doorstep
        if (dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6) score *= P_HALF / 100.0;
        if (held) score *= P_HOLD / 100.0;
        if (lead) score *= P_GROUP_W;
        else if (lead_p && dist(g.center, *lead_p) > 8) score *= 0.3;
        if (mp_chain_next(s, me, g, i, round)) score *= P_MP_CHAINPLAN / 100.0;  // rule 9: the squad moves on to the next camp
        if (i == s.target) score *= (P_MAPPLAN && P_MP_STICK && gd >= P_MP_STICK_D) ? P_MP_STICK / 100.0 : P_STICK / 100.0;  // hysteresis (mapplan_game.h rule 6)
        if (jack_go) score *= P_JACKW;
        if (score > best_score) { best_score = score; best = i; }
    }
    return best;
}

// BK1's visible wait for an altar a rival lock blocks (bank-v1b). A lock shows only its hits left, not its time, so
// it counts as one full deposit, ceil(multiplier x the gems we carry) rounds (at least the minimum), not v53's fixed
// 40. A rival's deposit does not block the altar (no such engine error), so it adds no wait.
int deposit_rounds() {
    int gems = 0;
    attempt([&] {
        gems = static_cast<int>(bc::self().gem_count());
        return true;
    });
    const int d = static_cast<int>(std::ceil(bc::constants::submit_gem_duration_multiplier * gems));
    return std::max(static_cast<int>(bc::constants::submit_gem_minimum_duration), d);
}

std::optional<vec2> br_legacy_best_altar(State& s, vec2 pos, int round) {
    std::optional<vec2> best;
    int bestd = 1 << 30;
    for (std::size_t i = 0; i < s.altars.size(); ++i) { stage7_budget_checkpoint(); 
        vec2 a = s.altars[i];
        if (!s.altar_ok[i]) continue;
        if (s.vis.is_set(a)) {  // refresh what we know about enemy locks
            bool locked = attempt([&] {
                return bc::vision::has_altar_lock(a) && bc::vision::altar_lock_at(a).is_enemy();
            });
            s.lock_until[i] = locked ? round + deposit_rounds() : 0;  // BK1: the visible wait (bank-v1b)
        }
        int d = dist(a, pos);
        if (s.lock_until[i] > round) d += s.lock_until[i] - round;
        if (false)  // an enemy champion next to the altar: prefer another one
            attempt([&] {
                for (auto& e : bc::vision::champions(*s.en))
                    if (e.is_alive() && dist(e.position(), a) <= 3) { d += P_ALTAR_SAFE; break; }
                return true;
            });
        if (static_cast<int>(i) != s.hold && dist(a, s.spawn_center) - dist(a, s.en_center) > 3) d += P_OWN_ALTAR;
        if (static_cast<int>(i) != s.hold && round - s.danger_r <= P_DANGER_T && dist(a, s.danger_p) <= P_DANGER_R) d += 60;
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
        for (int dy = -1; dy <= 1; ++dy) { stage7_budget_checkpoint(); 
            if (!dx && !dy) continue;
            vec2 p = altar + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || block.is_set(p) || !reached.is_set(p)) continue;
            best = std::min(best, static_cast<int>(field.get(p)));
        }
    // +1 preserves the old altar-centre distance thresholds on an open map.
    return best < (1 << 30) ? best + 1 : -1;
}

int br_altar_penalty(State& s, vec2 a, int i, int round) {
    int cost = std::max(0, s.lock_until[i] - round);
    if (false)
        attempt([&] {
            for (auto& e : bc::vision::champions(*s.en))
                if (e.is_alive() && dist(e.position(), a) <= 3) { cost += P_ALTAR_SAFE; break; }
            return true;
        });
    if (i != s.hold && dist(a, s.spawn_center) - dist(a, s.en_center) > 3) cost += P_OWN_ALTAR;
    if (i != s.hold && round - s.danger_r <= P_DANGER_T && dist(a, s.danger_p) <= P_DANGER_R) cost += 60;
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
    for (auto& enemy : enemies) { stage7_budget_checkpoint(); 
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
        for (std::size_t i = 0; i < s.altars.size(); ++i) { stage7_budget_checkpoint(); 
            if (!fuel_ok(22000)) { s.br_reason = 1; return false; }
            if (s.altar_ok[i]) ordinary[i] = br_ring_distance(field, reached, block, s.altars[i]);
        }
        if (br_policy == 2) {
            if (!br_threat_block(s, pos, round, s.br_risk_block)) { s.br_reason = 2; return false; }
            bc::distance_field safe_field;
            bc::bitboard safe_reached;
            safe_field.compute(s.br_risk_block, roots, safe_reached, 400);
            for (std::size_t i = 0; i < s.altars.size(); ++i) { stage7_budget_checkpoint(); 
                if (!fuel_ok(22000)) { s.br_reason = 1; return false; }
                if (ordinary[i] >= 0) safe[i] = br_ring_distance(safe_field, safe_reached, s.br_risk_block, s.altars[i]);
            }
        }
        int best = -1, best_cost = 1 << 30, best_home = 1 << 30;
        bool best_safe = false;
        s.br_lengths = ordinary;
        for (std::size_t i = 0; i < s.altars.size(); ++i) { stage7_budget_checkpoint(); 
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
                for (int dy = -2; dy <= 2; ++dy) { stage7_budget_checkpoint(); 
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


bool go_tribute(State& s, bc::champion& me, int round) {
    FP_SCOPE(20, "go_tribute");
    vec2 pos = me.position();
    auto a = best_altar(s, pos, round);
    if (!a) return false;
    // BK1: the trip keeps the altar it picked when it started (lowest walk + visible wait, the costs above). It
    // switches only if the other altar costs less by more than the walk already made towards the kept one.
    {
        const int cand = s.br_choice;
        const bool on_trip = s.bt_altar >= 0 && s.bt_altar < static_cast<int>(s.altars.size()) && round - s.bt_last <= 1;
        if (!on_trip) {
            s.bt_altar = cand;
            s.bt_start_len = cand >= 0 && cand < static_cast<int>(s.br_lengths.size()) ? s.br_lengths[cand] : -1;
        } else if (cand >= 0 && cand != s.bt_altar) {
            const int kept_len = s.bt_altar < static_cast<int>(s.br_lengths.size()) ? s.br_lengths[s.bt_altar] : -1;
            const int cand_len = cand < static_cast<int>(s.br_lengths.size()) ? s.br_lengths[cand] : -1;
            if (kept_len < 0 || cand_len < 0) {
                s.bt_altar = cand;  // the kept altar cannot be reached now (or no walk known): take the new choice
                s.bt_start_len = cand_len;
            } else {
                const int kept = kept_len + br_altar_penalty(s, s.altars[s.bt_altar], s.bt_altar, round);
                const int other = cand_len + br_altar_penalty(s, s.altars[cand], cand, round);
                const int walked = std::max(0, s.bt_start_len - kept_len);
                if (kept - other > walked) {
                    s.bt_altar = cand;
                    s.bt_start_len = cand_len;
                }
            }
        }
        s.bt_last = round;
        if (s.bt_altar >= 0) a = s.altars[s.bt_altar];
    }
    const int length = br_altar_distance(s, *a, pos, round);
    if (dist(pos, *a) <= 1) {
        bool acted = attempt([&] { me.submit_gems(*a); return true; });
        br_note(s, round, length, false);
        if (acted) s.bt_altar = -1;  // the trip ends with the deposit
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
    if (dist(me.position(), *a) <= 1 && attempt([&] { me.submit_gems(*a); return true; })) s.bt_altar = -1;
    br_note(s, round, length, used_safe);
    return moved;
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
            } catch (...) { if(stage7_budget_yielding)throw; 
            }
        return true;
    });
    vec2 pos = me.position();
    int rng = a.range > 0 ? a.range : SPELL_RANGE;
    vec2 best = tp;
    double bs = -1;
    int bh = 0;
    for (int dx = -a.radius; dx <= a.radius; ++dx)
        for (int dy = -a.radius; dy <= a.radius; ++dy) { stage7_budget_checkpoint(); 
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
    return best;
}

#include "track.h"
#include "fight.h"
#include "verdict.h"

bool g_cap_other_on = false;  // P_CAPPRIO: the ally that takes the reward already stands on it

// One capturer per reward: among the allies on the reward or claiming it within 4 tiles,
// the nearest one (lowest index on ties) captures; everybody else leaves.
bool other_captures_impl(State& s, bc::champion& me, const Group& g, int gi);
bool other_captures(State& s, bc::champion& me, const Group& g, int gi) {
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
    attempt([&] { seen = bc::vision::champions(*s.my); return true; });
    attempt([&] {
    auto allies = my_roster(s);
    for (std::size_t k = 0; k < allies.size() && !other; ++k) { stage7_budget_checkpoint(); 
        auto& a = allies[k];
        if (std::find(seen.begin(), seen.end(), a) == seen.end()) continue;
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
            if (!(claims && d <= 4)) continue;
            if (d < mine || (d == mine && static_cast<int>(k) < s.ally_idx)) other = true;
        } catch (...) { if(stage7_budget_yielding)throw; 
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
    for (auto& a : bc::vision::champions(*s.my)) { stage7_budget_checkpoint(); 
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
    for (const auto& c : (P_FUELGUARD && near) ? *near : bc::vision::camps()) { stage7_budget_checkpoint(); 
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
        for (int dy = -1; dy <= 1; ++dy) { stage7_budget_checkpoint(); 
            if (!dx && !dy) continue;
            vec2 p = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p) || g.mask.is_set(p)) continue;
            if (danger_at(s.thr, p) > current_danger) continue;
            bool monster_safe = true;
            for (const auto& c : monsters) { stage7_budget_checkpoint(); 
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
    vec2 pos = me.position();
    double hp = me.health();
    double mhp = std::max(1.0, static_cast<double>(me.max_health()));
    if (i_am_tank(s)) {  // P_DPSFARM: go where a DPS farms
        auto sm = read_sm();
        int best = -1, bd = 1 << 30, tb = tank_bits(s);
        bool issac = starts_with(s.name, "issac");
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < claim_slots(s) && k < static_cast<int>(allies.size()); ++k) { stage7_budget_checkpoint(); 
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
            for (int k = 0; k < static_cast<int>(allies.size()); ++k) { stage7_budget_checkpoint(); 
                if (!starts_with(norm(bc::to_string(allies[k].champion_name())), "cassi") || !allies[k].is_alive()) continue;
                ck = k;
                try { cp = allies[k].position(); } catch (...) { if(stage7_budget_yielding)throw; }
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

    // Healthy champions switch away from scattered gold camps together. Do not
    // interrupt an active capture; ordinary healing/shopping/banking run first.
    const int objective = objective_target(s, me, round);
    if (objective >= 0 && s.target != objective && s.cap_start < 0) {
        s.target = objective;
        s.target_round = round;
        s.cap_start = -1;
        write_claim(s, objective);
    }
    // Committed = a camp of our group is already damaged, or we are capturing.
    bool committed = false;
    if (s.target >= 0) {
        Group& g = s.groups[s.target];
        if (s.cap_start >= 0 && g.mask.is_set(pos)) committed = true;
        // A cleared camp awaiting capture is also committed. Otherwise the
        // retarget timer can redirect us between the final kill and the loot.
        if (g.reward_seen == round) committed = true;
        for (auto& c : camps)
            if (g.mask.is_set(c.spawn_position()) &&
                attempt([&] { return c.health() > 0 && c.health() < c.max_health(); }))
                committed = true;
    }
    bool expired = s.target >= 0 && (s.groups[s.target].bad_until > round ||
                                     s.groups[s.target].next_ok > round + (dist(pos, s.groups[s.target].center) + P_RESPAWN));
    int target_refresh = 20;
    target_refresh = P_E_RETARGET;
    // A damaged camp or active capture remains committed. Only travel plans
    // are reconsidered sooner when a more productive group becomes available.
    bool refresh = !committed && round - s.target_round >= (ball_on(s, round) ? 3 : target_refresh);
    if ((s.target < 0 || expired || refresh) && !can_choose(s)) {
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
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) { stage7_budget_checkpoint(); 
            Group& g = s.groups[i];
            if (g.gems + g.gold <= 0 || g.monolith || g.next_ok <= round || g.bad_until > round) continue;
            int w = g.next_ok - round + dist(pos, g.center) / 2;
            if (w < wbest) { wbest = w; wi = i; }
        }
        if (wi >= 0 && wbest < 120 && hp >= 0.6 * mhp) {
            g_farm = "wait";
            Group& g = s.groups[wi];
            bc::bitboard r5, r4;
            for (auto t : g.tiles) { stage7_budget_checkpoint(); 
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
        for (auto* c : live) { stage7_budget_checkpoint(); 
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
        const bool objective_go = s.target == s.sole_gem_group && objective_window(s, round);
        const bool mono_go = objective_go || (s.mono_only && g.monolith) || (g.jackpot && round >= P_JACKGO);
        if (mono_go) needed = std::min(needed, std::max(1, std::min(g.monolith ? s.roster : P_JACKN, s.roster)));
        if (!engaged && needed > here) {
            if (needed > std::max(coming, s.roster) || (!mono_go && needed > squad_needed(rem, str, dps, mhp * 0.75))) {
                g_farm = "too-strong";  // not even a full-health squad would do it
                g.bad_until = round + 60;
                drop_target(s);
                return;
            }
            if (PR.needheal && !objective_go) {  // objective rally has its own bounded team window
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
            for (auto* c : live) { stage7_budget_checkpoint(); 
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
        if (me.can_attack() && fuel_ok(12000)) {
            const int ar = static_cast<int>(me.attack_range());
            const bc::camp* local = nullptr;
            float lowest = 1e30f;
            int checked = 0;
            for (auto* c : live) { stage7_budget_checkpoint(); 
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
        if (other_captures(s, me, g, s.target)) {
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
            if (false) {  // standing on the tiles would split the reward
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
        if (g.next_ok <= round + dist(pos, g.center) + P_RESPAWN) {
            g_farm = "wait-respawn";  // stand 2-3 tiles off its spawn tiles until it is back
            bc::bitboard r3, r1;
            for (auto t : g.tiles) { stage7_budget_checkpoint(); 
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
    for (int k = 0; k < 2; ++k) { stage7_budget_checkpoint(); 
        if (s.slots[k] != Slot::Ground || !abs[k].is_ready()) continue;
        const AoeSlot a = aoe_slot(me, k);
        if (a.radius <= 0) continue;
        const bool exclusive = slot_exclusive(s, me, k);
        if (exclusive && (!allow_exclusive || free_only || escape)) continue;
        std::optional<vec2> best;
        double best_score = -1e30;
        for (auto& c : bc::vision::champions(*s.en)) { stage7_budget_checkpoint(); 
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
    const bool shop_ok = (round - s.shop_fail > 150) && round - s.shop_recall > 40;
    const int walk = cr_return_walk(s, me.position(), round);
    const bool result = cr_optional_value(hpr, gold, tavi, shop_ok, walk, true);
    if (old_optional && eligible_reward) {
        ++s.cr_seen;
        if (!result) ++s.cr_skipped;
        if (tavi && hpr >= 0.9f && gold >= 90 && !result) ++s.cr_tavi_skipped;
        if (walk < 0) ++s.cr_path_unavailable;
        cr_trace(s, round);
    }
    return result;
}

// P_TEAM_FIGHT: Cassi and Issac die together, so each commits only while its partner also has half hp or more.
bool tf_pair_ok(State& s, bc::champion& me) {
    if (!starts_with(s.name, "cassi") && !starts_with(s.name, "issac")) return true;
    bool ok = true;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my))
            attempt([&] {
                if (a == me || !a.is_alive()) return false;
                std::string n = norm(bc::to_string(a.champion_name()));
                if ((starts_with(n, "cassi") || starts_with(n, "issac")) && a.health() < 0.5f * a.max_health()) ok = false;
                return true;
            });
        return true;
    });
    return ok;
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
        if (!fuel_ok(40000)) {
            g_mode = "init-fuel";
            return;
        }
    }
    const int round = static_cast<int>(bc::round_number());
    cf_observe(s, me, round);

    if (!me.is_alive()) {
        g_mode = "dead";
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
        g.next_ok = round + g.respawn - (6);
        g.reward_seen = -1;
        broadcast_cooldown(s.target, g.next_ok);
        drop_target(s);
    }
    s.last_gems = gems;

    FP(2, "shop");
    if (!s.shop_done && fuel_ok(40000)) build_shop(s, me);  // init ran out of fuel before the item list was done
    if (gold >= 30) {
        shop(s, me);  // only succeeds on spawn / dead (or anywhere for Tavi)
        if (on_spawn && me.gold_count() >= 30 && static_cast<int>(me.gold_count()) == gold) s.shop_fail = round;
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
    if (false) s.self_pos = pos;
    refresh_groups(s, round);
    FP(5, "foes");

    std::vector<Foe> foes;
    for (auto& c : bc::vision::champions(*s.en)) { stage7_budget_checkpoint(); 
        attempt([&] {
            if (!c.is_alive()) return false;
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
            return true;
        });
    }
    {
        // Away: it stepped farther from where we stood, or toward its spawn without coming closer to us;
        // it stays "away" for 3 rounds unless it comes back within 2 of us.
        std::vector<Seen> now;
        for (auto& f : foes) { stage7_budget_checkpoint(); 
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
    track::update(s, me, foes, pos, round);
    update_danger(s, foes, round);
    if (true) {  // the volley map of this round (step_towards reads it)
        s.thr.clear();
        for (auto& f : foes) { stage7_budget_checkpoint(); 
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
    std::vector<bc::camp> camps = near_camps(s, pos);

    bool awake_camp_near = false;
    for (auto& c : camps)
        attempt([&] {
            if (dist(c.position(), pos) <= CAMP_RANGE + 1 && c.health() < c.max_health()) awake_camp_near = true;
            return true;
        });
    int nearest_foe = 99;
    for (auto& f : foes) nearest_foe = std::min(nearest_foe, f.d);
    bool in_combat = nearest_foe <= 4 || awake_camp_near;
    bool safe = nearest_foe > 7 && !awake_camp_near;
    safe = safe && nearest_foe > 8 && round - s.hit_round > 2;
    // P_RECALL_NEAR: a recall only needs nobody to hit us while it channels, not an empty screen
    bool rsafe = safe || (s.rnear && nearest_foe >= s.rnear && round - s.hit_round >= 1 && !awake_camp_near);
    // P_RC_QUIET: our recalls started with a rival within 5 (true positions) die within 10 rounds 35% of the time, the
    // teams that beat us 3%; top-10 winners 13%, losers 25%. Wait until no hit and no rival within 6 for a few rounds.
    if (nearest_foe <= 6) s.close_r = round;
    if (P_RC_QUIET && (round - s.close_r < P_RC_QUIET || round - s.hit_round < P_RC_QUIET)) rsafe = false;

    // Preserve a nearby cleared camp's loot, even if we were hit by its last
    // surviving monster on a recent turn. The recent-hit check in `safe` is
    // over-conservative after that monster has died. Only delay non-emergency
    // recalls, and only when we are the designated capturer, no enemies are
    // within 8 tiles, and no fighting camp is nearby. Very low HP still flees.
    bool capture_before_recall = false;
    if (hpr >= 0.20f && nearest_foe > 8 && !awake_camp_near && s.target >= 0 && s.target < static_cast<int>(s.groups.size()) && fuel_ok(18000)) {
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
        if (P_TEAM_FIGHT && P_TF_GLOBAL && f.hp < 0.5f * std::max(1.0f, [&] { float m = 1; attempt([&] { m = f.c.max_health(); return true; }); return m; }())) return false;
        return f.away && f.d > me.attack_range() && f.gems < P_CHASE_GEMS && !f.channeling;
    };
    for (auto& f : foes) { stage7_budget_checkpoint(); 
        if (f.d > 6 || s.en_spawn.is_set(f.p) || gone(f)) continue;
        double sc = f.hp - (f.channeling ? 300 : 0) - 5.0 * f.gems + 40.0 * f.d;
        if (sc < tgt_score) { tgt_score = sc; tgt = &f; }
    }

    // Stuck: same tile for many turns with nothing to hit. Bank or go home, give the target up.
    if (s.still_n >= P_UNSTICK && !on_spawn && nearest_foe > 4 && !awake_camp_near && (s.cap_start < 0 || round - s.cap_start > 10)) {
        g_mode = "unstick";
        if (s.target >= 0) {
            s.groups[s.target].bad_until = round + 30;
            drop_target(s);
        }
        if (gems > 0 && go_tribute(s, me, round)) return;
        if (hpr < 0.9f) {
            if (safe && attempt([&] {
                    me.recall();
                    return true;
                }))
                return;
            if (flee(s, me)) return;
        }
        s.still_n = 0;
    }

    if (PR.noleave && !awake_camp_near && hpr >= 0.15f && fuel_ok(25000)) {
        const bool carry = cap_rank(s.name, me.attack_range() > 1) <= 2;
        auto sm = read_sm();
        int gi = -1, gd = 99;
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) { stage7_budget_checkpoint(); 
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
                for (auto& a : my_roster(s)) { stage7_budget_checkpoint(); 
                    if (a == me || !a.is_alive()) continue;
                    bool ar = false;
                    try { ar = a.attack_range() > 1; } catch (...) { if(stage7_budget_yielding)throw; }
                    if (cap_rank(norm(bc::to_string(a.champion_name())), ar) > 2) continue;
                    carry_alive = true;
                    try { if (dist(a.position(), pos) <= 6) carry_near = true; } catch (...) { if(stage7_budget_yielding)throw; }
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
                        attempt([&] {
                            me.recall();
                            return true;
                        });
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
            attempt([&] {
                me.recall();
                return true;
            });
        }
        return;
    }

    // 2. Badly hurt: run, or recall if nobody can interrupt.
    g_mode = "flee/recall";
    // P_UNI_FLEE: with the caster draft, leave the fight earlier (the #1 walks away 58% of contact rounds below 30%
    // hp and 40% below 50%; v27 died in 20% of its contact rounds below 30%)
    if (!capture_before_recall &&
        hpr * 100 < ((s.casters) ? P_UNI_FLEE : P.flee_pct)) {
        if (gems > 0 && nearest_foe > 3) {
            auto a = best_altar(s, pos, round);
            if (a && dist(*a, pos) <= 1) {  // tribute is not interrupted by damage
                bool acted = go_tribute(s, me, round);
                if (true) return;
            }
        }
        bool recalled = false;
        if (rsafe) recalled = attempt([&] {
            me.recall();
            return true;
        });
        if (!rsafe) {
            bool hit = fight::hit_now(s, me, foes);
            flee(s, me);
            if (!hit) shoot_back(s, me, foes);
        }
        return;
    }

    if (!capture_before_recall && s.rnear && !safe && rsafe && !on_spawn &&
        dist(pos, s.spawn_center) > 6 && hpr * 100 < P.recall_pct) {
        g_mode = "near-recall";  // the #1: hurt, out of the fight by 4-6 tiles: recall now, come back whole
        if (attempt([&] {
                me.recall();
                return true;
            }))
            return;
    }

    bool fight_fav = false;  // P_CAMPFOE: step 3's verdict on the fight
    // Healthy, empty-handed champions assemble before choosing solo gold or
    // applying the generic danger skip. Keep urgent self-defence and shop trips.
    if (objective_window(s, round) && gems == 0 && hpr >= 0.65f && nearest_foe > 2 &&
        gold < P_SHOP_RECALL && fuel_ok(22000) && objective_assemble(s, me, round)) return;

    // 3. Enemy champions: back away from a stronger group, fight an even or weaker one.
    FP(9, "fight");
    g_mode = "fight";
    // P_CHASE: go after a hurt (<50%) or recalling rival within 4 (followed up to 4 rounds, out to 6 tiles).
    if (P_TEAM_FIGHT && hpr >= 0.5f && tf_pair_ok(s, me) && !on_spawn && !awake_camp_near && !foes.empty() && fuel_ok(12000)) {
        auto hurt = [&](const Foe& f) {
            bool rc = false;
            float mh = 1;
            attempt([&] { rc = f.c.is_recalling(); mh = f.c.max_health(); return true; });
            return rc || f.hp < 0.5f * mh;
        };
        const Foe* k = nullptr;
        if (s.chase && round <= s.chase_until)
            for (auto& f : foes)
                if (f.c == *s.chase && f.d <= 6 && hurt(f)) k = &f;
        if (!k) {
            std::vector<vec2> mates;
            for (auto& a : bc::vision::champions(*s.my))
                attempt([&] {
                    if (!(a == me) && a.is_alive()) mates.push_back(a.position());
                    return true;
                });
            float kp = 2;
            for (auto& f : foes) { stage7_budget_checkpoint(); 
                if (f.d > 7 || !hurt(f)) continue;
                bool near = f.d <= 4;
                for (auto& m : mates)
                    if (dist(m, f.p) <= 3) near = true;
                if (!near) continue;
                float mh = 1;
                attempt([&] { mh = std::max(1.0f, f.c.max_health()); return true; });
                float pc = f.hp / mh;
                if (!k || pc < kp || (pc == kp && (f.p.x < k->p.x || (f.p.x == k->p.x && f.p.y < k->p.y)))) { k = &f; kp = pc; }
            }
        }
        if (!k && P_TF_GUARD) {  // a rival on one of our hurt champions (within 3 of it) is the next target
            std::vector<vec2> hurt_mates;
            for (auto& a : bc::vision::champions(*s.my))
                attempt([&] {
                    if (!(a == me) && a.is_alive() && a.health() < 0.5f * a.max_health()) hurt_mates.push_back(a.position());
                    return true;
                });
            for (auto& f : foes) { stage7_budget_checkpoint(); 
                if (f.d > 6) continue;
                bool on = false;
                for (auto& m : hurt_mates)
                    if (dist(m, f.p) <= 3) on = true;
                if (on && (!k || f.hp < k->hp)) k = &f;
            }
        }
        if (k && s.en_spawn.is_set(k->p)) k = nullptr;
        if (k) {
            int others = 0, cover = 0;
            for (auto& o : foes) { stage7_budget_checkpoint(); 
                if (&o == k) continue;
                if (dist(o.p, pos) <= 4) ++others;
                float omh = 1;
                attempt([&] { omh = std::max(1.0f, o.c.max_health()); return true; });
                if (dist(o.p, k->p) <= 3 && o.hp >= 0.5f * omh) ++cover;  // bait: it backs into its healthy group
            }
            if (others > 1 || cover >= 2) k = nullptr;
        }
        // a champion carrying a tribute-sized bag only hits a target already in reach; it does not follow
        bool bag = static_cast<int>(me.gem_count()) >= P.tribute_gems;
        if (k && bag && k->d > (s.melee ? 1 : static_cast<int>(me.attack_range()))) k = nullptr;
        if (k) {
            if (!s.chase || !(*s.chase == k->c)) { s.chase = k->c; s.chase_until = round + 4; }
            g_mode = "chase";
            vec2 p0 = me.position();
            bool cast = cast_offense(s, me, k->c, k->p, true);
            bool hit = basic_attack(s, me, k->c, k->p);
            if (!bag && dist(me.position(), k->p) > (s.melee ? 1 : me.attack_range()) && me.can_move()) {
                bc::bitboard goal;
                goal.draw_chebyshev(k->p, static_cast<float>(s.melee ? 1 : me.attack_range()));
                goal &= ~s.en_spawn;
                if (!step_towards(s, me, goal, s.melee)) attempt([&] { return me.move_towards(k->p); });
                if (!hit) hit = basic_attack(s, me, k->c, k->p);
            }
            if (cast || hit || !(me.position() == p0)) return;
        } else if (s.chase && round > s.chase_until) {
            s.chase.reset();
        }
    }
    std::vector<vec2> allies;
    for (auto& a : bc::vision::champions(*s.my))
        attempt([&] {
            if (!(a == me) && a.is_alive()) allies.push_back(a.position());
            return true;
        });
    // Ally duty: a foe near an ally of ours (within 8 of us) becomes our target.
    if (!tgt) {
        for (auto& f : foes) { stage7_budget_checkpoint(); 
            if (f.d > 8 || s.en_spawn.is_set(f.p) || gone(f)) continue;
            for (auto& ap : allies)
                if (dist(ap, f.p) <= 3 && dist(ap, pos) <= 8) {
                    if (!tgt || f.hp < tgt->hp) tgt = &f;
                    break;
                }
        }
    }
    bool pv_fight = false;  // P_PV: the first-contact verdict, held for the engagement (verdict.h)
    {
        int v = pv::verdict(s, me, foes, round, on_spawn);
        bool keep = false;
        if (false) {
            keep = true;
            for (auto& f : foes)
                if (f.d <= 3) keep = false;
        }
        if (v == 2 && !on_spawn && !foes.empty() && !keep) {
            g_mode = "pv-leave";
            fight::back_off(s, me, foes, round);
            return;
        }
        pv_fight = v == 1;
    }
    if (false) {
        g_mode = s.fm == 1 ? "fm-engage" : "fm-retreat";
        return;
    }
    if (false) {
        g_mode = "front";
        return;
    }
    if (s.casters && !foes.empty() && !on_spawn && (!s.melee || s.renkite) && fight::kite(s, me, foes, round)) {
        g_mode = "kite";
        return;
    }
    if (false) {
        g_mode = "front";
        return;
    }
    if (!foes.empty()) {
        if (false) fight::call_help(s, foes, round);
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
        if (tgt) {
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
        if (false) favourable = track::favourable(me, tgt->p, round);
        bool helping = false;
        if (false) {  // an ally named the foe hitting it: go and hit that one
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
        if (false) {
            Foe* best = nullptr;
            for (auto& f : foes) { stage7_budget_checkpoint(); 
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
        if (false) {  // a lone enemy the allies near it kill fast
            Foe* iso = track::isolated(s, me, foes, round, gone);
            if (iso) { tgt = iso; favourable = true; helping = true; }
        }
        bool pot_hold = false;
        if (false)
            for (auto pa : s.pots)
                if (dist(pa, pos) <= 5) {
                    int nb6 = 1, eb6 = 0;
                    for (auto& ap : allies) if (dist(ap, pos) <= 6) ++nb6;
                    for (auto& f : foes) if (f.d <= 6) ++eb6;
                    if (eb6 < nb6 + 2) pot_hold = true;
                }
        if (pot_hold) favourable = true;
        if (pv_fight) favourable = true;
        g_ally_near_tgt = false;
        if (tgt)
            for (auto& ap : allies)
                if (dist(ap, tgt->p) <= 2) g_ally_near_tgt = true;
        fight_fav = favourable;
        bool killable = tgt && tgt->hp <= me.strength() * (P_GA_KILL_X / 10.0f);
        bool reachable = tgt && tgt->d <= me.attack_range() + 1;
        bool carrying = false;
        int low_pct = P_LOWHP;
        if (!killable && !on_spawn && !pot_hold && ((low_pct && hpr * 100 < low_pct && nearest_foe <= 6) ||
                                       (carrying && !favourable && nearest_foe <= 6))) {
            g_mode = "avoid";
            if (carrying) {
                auto a = best_altar(s, pos, round);
                if (a && dist(*a, pos) <= 1 && nearest_foe > 3) {
                    bool acted = go_tribute(s, me, round);
                    if (true) return;
                }
            }
            fight::back_off(s, me, foes, round);
            return;
        }
        if (PR.outnum && !on_spawn && !(killable && reachable) && nearest_foe <= PR.outnum) {
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
        if (!on_spawn && fight::front_line(s, me, foes, round)) {
            g_mode = "front";
            return;
        }
        if (tgt && carrying && !killable && !tgt->channeling) tgt = nullptr;
        // P_NOCHASE2: a low or channelling foe is no reason to walk after it, unless it carries a big bag
        const bool close_enough = !PR.nochase2 || (tgt && (tgt->d <= me.attack_range() + 1 || tgt->gems >= P_CHASE_GEMS));
        if (tgt && (((killable || tgt->channeling) && close_enough) || (reachable && favourable) || helping ||
                    (favourable && tgt->d <= 8 && g_ally_near_tgt))) {
            bool acted = engage(s, me, tgt->c, tgt->p, true, true);
            if (true) return;
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
                if (attempt([&] {
                        me.recall();
                        return true;
                    })) {
                    ++s.cr_started;
                    cr_trace(s, round);
                    if (shop_trip) s.shop_recall = round;
                }
                return;
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
                if (rsafe && attempt([&] {
                        me.recall();
                        return true;
                    }))
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
                if (true) return;
            }
        }
        bool recalled = attempt([&] {
            me.recall();
            return true;
        });
        if (recalled && shop_trip) s.shop_recall = round;
        if (true) return;
    }

    if (false) {
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
        const int chain_gems = (s.de_map == v34de::Rows) ? 60 : P_CHAIN;
        if (chain_gems && gems < chain_gems && !late && ad > 2) {
            auto sm = read_sm();
            int gi = -1, gd = 99;
            for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) { stage7_budget_checkpoint(); 
                Group& g = s.groups[i];
                if (g.gems <= 0 || g.monolith || g.next_ok > round || g.bad_until > round) continue;
                int d = dist(pos, g.center);
                if (d > P_CHAIN_R || d >= ad || d >= gd) continue;
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
        const int bag_q = (s.de_map == v34de::Rows) ? 48 : P_BAG;
        int bag = (bag_q && round - s.foe_r > P_BAG_QUIET) ? std::max(P.tribute_gems, bag_q) : P.tribute_gems;
        if (!chain && (gems >= bag || late || (gems >= 10 && ad <= (s.de_map == v34de::Rows ? 4 : P_TRIBUTE_NEAR)) || (gems >= 5 && ad <= 2))) {
            if (false) {
                g_mode = "tele-bank";
                if (attempt([&] {
                        me.recall();
                        return true;
                    }))
                    s.shop_recall = round;
                return;
            }
            bool acted = go_tribute(s, me, round);
            if (true) return;
        }
    }

    // P_GROUP_R: keep the ball together. The leader is the first ally in draft order that is alive and not
    // channelling; followers come back to it, the leader waits for a straggler (ignoring anyone 15+ away).
    if (false) {
        int li = -1, far = 0;
        vec2 lp{0, 0};
        std::vector<vec2> fol;
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < static_cast<int>(allies.size()); ++k) { stage7_budget_checkpoint(); 
                auto& a = allies[k];
                try {
                    if (!a.is_alive() || a.is_recalling() || a.is_teleporting()) continue;
                    vec2 ap = a.position();
                    if (s.my_spawn.is_set(ap) && !(a == me)) continue;
                    if (li < 0) { li = k; lp = ap; continue; }
                    if (!(a == me)) fol.push_back(ap);
                } catch (...) { if(stage7_budget_yielding)throw; 
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
            for (auto& f : fol) { stage7_budget_checkpoint(); 
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
    if (s.hold >= 0 && s.ally_idx <= 0) {
        int n = 0;
        for (char h : s.hold_group) n += h;
        std::printf("[hold] altar %d,%d groups %d\n", X(s.altars[s.hold]), Y(s.altars[s.hold]), n);
    }
    std::fflush(stdout);
}

void log_status(State& s) {
    attempt([&] {
        int round = static_cast<int>(bc::round_number());
        bool every = false;
        if (round % STATUS_EVERY != 0 && round > 3 && !every) return false;
        if (!fuel_ok(12000)) return false;  // a log line is not worth a turn cut short
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

// pre = before the turn's move (P_SWEEP >= 3). P_SWEEP 5: a spell that roots us for the round is cast before
// moving only when standing is safe (hp >= 50%, no foe within 2, not outnumbered within 5); other spells always.
void spell_sweep(State& s, bool pre = false, bool free_only = false) {
    bc::champion& me = bc::self();
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
        const bool roots_allowed = true;
        if (cm_edge_aoe(s, me, roots_allowed, false, free_only)) g_mode = "sweep";
        return;
    }
    bool stand_ok = true;
    if (false) {
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
    bool guard = false;
    if (false) {
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
    if (false) {
        float hpr = me.health() / std::max(1.0f, me.max_health());
        if (hpr * 100 < ((s.casters) ? P_UNI_FLEE : P.flee_pct)) {
            escape = true;  // play_turn will run or recall this round: a rooting cast would cancel the step
        } else {
            std::vector<Threat> th;
            attempt([&] {
                for (auto& c : bc::vision::champions(*s.en)) { stage7_budget_checkpoint(); 
                    if (!c.is_alive() || s.en_spawn.is_set(c.position())) continue;
                    int ar = static_cast<int>(c.attack_range());
                    th.push_back(threat_of(c, c.position(), ar <= 1 ? 2 : ar + 1));
                }
                return true;
            });
            double here = danger_at(th, pos), lim = me.health() * P_CASTSAFE / 100.0;
            if (here >= lim) {
                for (int dx = -1; dx <= 1 && !escape; ++dx)
                    for (int dy = -1; dy <= 1 && !escape; ++dy) { stage7_budget_checkpoint(); 
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
    for (auto& f : foes) { stage7_budget_checkpoint(); 
        if (f.d <= fight::reach(f) && (!threat || f.d < threat->d)) threat = &f;
        auto wsc = [&](const Foe& x) {  // P_SQUISHY: sparring only, prefer ranged targets (real caster teams hit our Stellar more)
            double v = x.hp - (x.channeling ? 300 : 0) - 5.0 * x.gems;
            return v;
        };
        if (!weak || wsc(f) < wsc(*weak)) weak = &f;
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
        if (!fighting) return;
    }
    auto abs = me.abilities();
    bool cast = false;
    auto try_use = [&](bool want_cc, Foe* t) {
        for (int k = 0; k < 2 && !cast; ++k) { stage7_budget_checkpoint(); 
            auto& ab = abs[k];
            if (s.slots[k] != Slot::Targeted && s.slots[k] != Slot::Ground) continue;
            bool cc = attempt([&] { return ab.is_cc(); });
            if (cc != want_cc || !ab.is_ready()) continue;
            if (free_only && slot_exclusive(s, me, k)) continue;
            bool ex = guard && slot_exclusive(s, me, k);
            if (ex && pre && !stand_ok) continue;
            if (escape && slot_exclusive(s, me, k) && !kills(k, *t)) {
                continue;
            }
            if (s.slots[k] == Slot::Targeted) {
                if (!attempt([&] { return ab.can_target_enemies(); })) continue;
                cast = attempt([&] { return ab.use(t->c); });
            } else {
                vec2 c = aoe_centre(s, me, k, t->p);
                cast = attempt([&] { return ab.use(c); });
            }
            if (cast && ex && pre) s.rooted_r = static_cast<int>(bc::round_number());
        }
    };
    if (threat) try_use(true, threat);
    if (!cast) {  // an area spell that covers 2+ foes beats a single-target one
        for (int k = 0; k < 2 && !cast; ++k) { stage7_budget_checkpoint(); 
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
    for (;;) { stage7_budget_checkpoint(); 
        stage7_budget_active=true;
        g_mode = "?";
        g_farm = "-";
        try {
            if (s.sweep >= 3) spell_sweep(s, true);  // before moving: most targeted spells cannot be cast after a step
            play_turn(s);
            FP(12, "post-sweep");
            if (s.sweep && s.sweep < 3) spell_sweep(s);
            if (s.sweep == 5) {
                if (s.rooted_r == static_cast<int>(bc::round_number())) shoot_rooted(s);
                spell_sweep(s);  // spells that still work after our step
            }
            // Newly revealed targets after moving were not in the pre-sweep.
            // This optional extra pass only uses movement-compatible spells.
            if (false)
                spell_sweep(s, false, true);
            r5_altar_lock(s);
        } catch (const Stage7TurnBudget&) {
            stage7_budget_yielding=false;++stage7_yields;g_mode="fuel-yield";
        } catch (const std::exception& e) { if(stage7_budget_yielding)throw; 
            note_error(e.what());
        } catch (...) { if(stage7_budget_yielding)throw; 
            note_error("unknown exception in turn");
        }
        stage7_budget_active=false;
        FP(13, "log");
        if (s.ready && !logged_init && (!P_FUELGUARD || fuel_ok(20000))) {
            logged_init = true;
            log_init(s);
        }
        log_status(s);
        if(bc::round_number()%100==0 && bc::fuel_remaining()>3000)std::printf("S7P %u %u %u %u %u\n",bc::round_number(),unit_id(bc::self()),ppo_calls,ppo_changes,ppo_choices);
        bc::end_turn();
    }
}

}  // namespace

int main() {
    if (bc::is_draft()) run_draft();
    run_game();
}

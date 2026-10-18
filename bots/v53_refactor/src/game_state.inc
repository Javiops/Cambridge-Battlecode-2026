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


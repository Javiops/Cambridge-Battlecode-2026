// mite_scratch: a CAMBC 2026 bot written from scratch to imitate the ladder #1 team "Mite",
// rule by rule, as measured from its replays (see $S/reports/README.md and the six reports).
//
// Every section is tagged with the Mite rule it implements:
//   [DRAFT]  fixed draft per champions-per-team (draft_shop.md 1)
//   [SHOP]   jungle -> durability -> bruiser health -> power, spend everything, alive on spawn only, altar locks (draft_shop.md 2)
//   [OPEN]   whole team on the nearest camp, same monster, ranged from 3, one capturer, fan out 1-3 per camp (opening.md)
//   [MAP]    own-half camps only, no monoliths, mostly no gold-only clusters, enemy half only while chasing (map_control.md)
//   [TRIB]   tribute on every altar pass, start on the capture tile when an altar is adjacent, locks before tributing (recall_survival.md 5)
//   [RECALL] hp < 50% -> recall from 7+ tiles (walk home until then); shop recall at ~180 gold; recall as a teleport (recall_survival.md)
//   [FIGHT]  open with a spell at 4, isolated targets, no chasing, leave under fire at low hp (fights.md)
//   [TARGET] killable > nearest > lowest hp%, keep target, everyone on one victim (targeting_spells.md)
//   [SPELL]  never saved, exclusive spells only on turns without a walk, Stellar single/area, camp spells on awake monsters (targeting_spells.md)
//
// Engine facts relied on: monsters never move or chase; only champions on the group's spawn tiles share the capture;
// allies out of vision throw on position(); turn order in a team = draft order; a ranged champion that attacks cannot
// move that turn; exclusive spells cannot be cast after a step; 8 bytes of shared memory.

#include <cambc.h>

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <span>
#include <string>
#include <variant>
#include <vector>

namespace bc = cambc;
using bc::vec2;

namespace {

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------
constexpr std::uint64_t FUEL_RESERVE = 5000;
inline bool fuel_ok(std::uint64_t need) { return bc::fuel_remaining() > need + FUEL_RESERVE; }
inline int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }

// Every SDK call can throw (cambc::error); an uncaught exception restarts the guest and loses
// all state, so every action goes through attempt().
int g_errors = 0;
template <class F>
bool attempt(F&& f) {
    try {
        return f();
    } catch (const std::exception& e) {
        if (++g_errors <= 5) std::printf("[err] %s\n", e.what());
        return false;
    } catch (...) {
        ++g_errors;
        return false;
    }
}

// Tunables (all derived from the measured Mite thresholds).
constexpr int RECALL_PCT = 50;      // [RECALL] heal recall strictly below 50% hp
constexpr int RECALL_SAFE = 7;      // [RECALL] start the recall with the nearest enemy >= 7 tiles away
constexpr int SHOP_GOLD = 180;      // [RECALL] shop recall once ~180 gold is carried (6 shards)
constexpr int SHOP_GOLD_LOW = 90;   // [RECALL] ... or 90 gold when the next camp is far anyway
constexpr int TRIB_DETOUR = 12;     // [TRIB] with 40+ gems walk to the altar when it is this close (walking)
constexpr int BIG_BAG = 70;         // [TRIB] always go and bank a bag this big
constexpr int ENGAGE_RANGE = 6;     // [FIGHT] a visible enemy this close is engaged (walk in to cast at 4)
constexpr int CHASE_MAX = 10;       // [MAP] enemy half only while chasing, at most ~10 rounds
constexpr int OPEN_ROUNDS = 30;     // [OPEN] no per-camp cap in the opening: everyone stacks the first camp
constexpr int MAX_GROUPS = 250;

// ---------------------------------------------------------------------------
// Draft memory layout (written in the draft, read by every champion)
// ---------------------------------------------------------------------------
constexpr std::size_t DM_MAGIC = 0;   // 'M','S'
constexpr std::size_t DM_TEAM = 2;    // picks per team
constexpr std::size_t DM_PATH = 3;    // spawn-to-spawn walking distance (capped 255)
constexpr std::size_t DM_FOCUS = 4;   // 1 = Ryth/Ren take focus (5-pick maps)

// ---------------------------------------------------------------------------
// [DRAFT] Mite's fixed draft, keyed by champions per team (draft_shop.md):
//   3 picks: Varg, Ryth, Cassi&Issac when the spawn-to-spawn path is short (collision 34), else Ren, Stellar, C&I (packs 26?,
//            expanse 85). Packs has a short path but Mite drafts Ren/Stellar there too; the report's own rule is "<= 45 -> melee";
//            the measured table is ambiguous for packs, we follow the task statement.
//   4 picks: Varg, Ryth, C&I, Ren.
//   5 picks: Varg, Stellar, C&I, Ryth, Ren; Tavi instead of Ryth on very long maps with many altars (lanes: path 81, 18 altars).
// Pick order = act order (Varg/Ren first, C&I third).
// ---------------------------------------------------------------------------
int spawn_path_length() {
    int best = -1;
    attempt([&] {
        bc::bitboard block = bc::map::walls() | bc::map::holes() | bc::map::altars();
        bc::distance_field df;
        bc::bitboard visited;
        df.compute(block, bc::map::spawn_region(bc::team::ally), visited);
        int b = 1 << 30;
        for (auto p : bc::map::spawn_region(bc::team::enemy).positions())
            if (visited.is_set(p)) b = std::min(b, static_cast<int>(df.get(p)));
        if (b < (1 << 30)) best = b;
        return true;
    });
    return best;
}

[[noreturn]] void run_draft() {
    using D = bc::champion_draft;
    int ts = 3;
    attempt([&] { ts = static_cast<int>(bc::draft::team_size()); return true; });
    int path = spawn_path_length();
    std::size_t altars = 0;
    attempt([&] { altars = bc::map::altars().positions().size(); return true; });

    std::vector<D> plan;
    if (ts <= 3) {
        if (path >= 0 && path <= 45) plan = {D::varg, D::ryth, D::cassi_and_issac};
        else plan = {D::ren, D::stellar, D::cassi_and_issac};
    } else if (ts == 4) {
        plan = {D::varg, D::ryth, D::cassi_and_issac, D::ren};
    } else {
        bool lanes_like = path > 70 && altars >= 10;
        plan = {D::varg, D::stellar, D::cassi_and_issac, lanes_like ? D::tavi : D::ryth, D::ren};
    }
    // Fallbacks in case a pick is refused (never happens: rosters are independent).
    for (D d : {D::varg, D::ryth, D::cassi_and_issac, D::ren, D::stellar, D::tavi, D::vendetta, D::marcella, D::prism, D::willow, D::vesper_vale})
        if (std::find(plan.begin(), plan.end(), d) == plan.end()) plan.push_back(d);

    std::array<std::byte, 8> dm{};
    dm[DM_MAGIC] = std::byte{'M'};
    dm[DM_MAGIC + 1] = std::byte{'S'};
    dm[DM_TEAM] = static_cast<std::byte>(ts);
    dm[DM_PATH] = static_cast<std::byte>(std::clamp(path, 0, 255));
    dm[DM_FOCUS] = static_cast<std::byte>(ts >= 5 ? 1 : 0);
    attempt([&] {
        bc::draft_memory_buffer buf;
        buf = std::span<const std::byte>(dm.data(), dm.size());
        return true;
    });

    for (;;) {
        std::vector<D> mine;
        attempt([&] { mine = bc::draft::current_draft(bc::team::ally); return true; });
        for (D d : plan) {
            if (std::find(mine.begin(), mine.end(), d) != mine.end()) continue;
            if (attempt([&] { bc::draft::pick(d); return true; })) break;
        }
        bc::end_turn();
    }
}

// ---------------------------------------------------------------------------
// Gameplay state
// ---------------------------------------------------------------------------
struct Group {
    bc::bitboard mask;            // spawn tiles of the group
    std::vector<vec2> tiles;
    vec2 center{0, 0};
    int gems = 0, gold = 0, respawn = 60;
    double hp = 0;                // total base monster health
    double str = 0;               // total base monster strength (damage per round when focused)
    bool monolith = false, has_elk = false;
    int d_own = -1, d_en = -1;    // walking distance from our / their spawn
    int next_ok = 0;              // believed respawning until this round
    int bad_until = 0;            // skipped until this round (could not reach / clear it)
    int reward_seen = -1;         // round in which we last saw its reward waiting
    std::optional<bc::map::camp_group> obj;
};

enum class Kind { None, Reset, Dash, Damage, Cc, Aoe, Shield, Heal };
struct Slot {
    Kind kind = Kind::None;
    int range = 0;
    bool excl = false;   // exclusive with movement
    bool camps = false, enemies = false, ground = false;
};

struct Foe {
    bc::champion c;
    vec2 p;
    float hp = 0, mhp = 1;
    int d = 99;
    bool retreating = false;  // moved away from us since last round
    bool isolated = true;     // no enemy ally within 4
};

struct State {
    bool ready = false;
    bc::team my = bc::team::ally, en = bc::team::enemy;
    bc::bitboard static_block, my_spawn, en_spawn;
    std::vector<vec2> altars;
    std::vector<int> altar_d_own, altar_d_en;
    vec2 spawn_center{0, 0};
    std::vector<Group> groups;
    std::vector<std::uint16_t> f_own;   // walking distance from our spawn, linear buffer
    int W = 0, H = 0;

    // champion identity
    std::string name;
    bc::champion_type type = bc::champion_type::ryth;
    bool melee = true;
    bool is_varg = false, is_ryth = false, is_ren = false, is_cassi = false, is_issac = false, is_stellar = false, is_tavi = false;
    int ally_idx = 0, roster = 1;
    int team_size = 3;
    bool focus_main = false;
    std::array<Slot, 2> slot;
    int dash_slot = -1, reset_slot = -1, shield_slot = -1;

    // per-turn scratch
    bc::bitboard blocked, vis, dest, visited;
    bc::distance_field df;
    std::vector<std::uint16_t> f_me;  // walking distance from where we stand (refreshed on demand)
    int f_me_round = -100;
    vec2 f_me_pos{-1, -1};

    // objectives
    int target = -1;
    int target_round = -1000;
    int cap_start = -1;
    int last_gems = 0, last_gold = 0;
    float last_hp = -1;
    int hit_round = -1000;
    int shop_trips = 0;
    int spawn_arrive = -1000;
    int chase_rounds = 0;
    int recall_fail = 0;
    std::vector<std::pair<bc::champion, vec2>> seen;  // enemy positions last round
    int seen_round = -10;
    std::optional<bc::champion> fight_target;
    int fight_round = -10;
    int idle_check = -100;
    vec2 danger_p{0, 0};       // where we last saw an enemy pack that outnumbered us
    int danger_r = -1000;
};

// ---------------------------------------------------------------------------
// Shared memory (8 bytes): bytes 0..5 = claim per ally index (group+1, 0 = none),
// byte 6 = group+1 whose respawn was seen, byte 7 = ready round / 8 + 1.
// ---------------------------------------------------------------------------
constexpr int SM_CLAIMS = 6;
constexpr std::size_t SM_BC_GROUP = 6, SM_BC_READY = 7;

std::array<std::uint8_t, 8> read_sm() {
    std::array<std::byte, 8> raw{};
    attempt([&] { bc::shared_memory.read(0, std::span<std::byte>(raw.data(), raw.size())); return true; });
    std::array<std::uint8_t, 8> out{};
    for (int i = 0; i < 8; ++i) out[i] = std::to_integer<std::uint8_t>(raw[i]);
    return out;
}
void write_sm(std::size_t off, std::uint8_t v) {
    std::byte b = static_cast<std::byte>(v);
    attempt([&] { bc::shared_memory.write(off, std::span<const std::byte>(&b, 1)); return true; });
}
void write_claim(const State& s, int group) {
    if (s.ally_idx < 0 || s.ally_idx >= SM_CLAIMS) return;
    write_sm(static_cast<std::size_t>(s.ally_idx), static_cast<std::uint8_t>(group + 1));
}
int claimers(const State& s, const std::array<std::uint8_t, 8>& sm, int group) {
    int n = 0;
    for (int k = 0; k < std::min(SM_CLAIMS, s.roster); ++k)
        if (k != s.ally_idx && sm[k] == group + 1) ++n;
    return n;
}
void broadcast_cooldown(int group, int ready_round) {
    if (group < 0 || group >= MAX_GROUPS) return;
    write_sm(SM_BC_GROUP, static_cast<std::uint8_t>(group + 1));
    write_sm(SM_BC_READY, static_cast<std::uint8_t>(std::clamp(ready_round / 8 + 1, 1, 250)));
}

// ---------------------------------------------------------------------------
// Initialisation (first turn, 200k fuel)
// ---------------------------------------------------------------------------
vec2 centre_of(const std::vector<vec2>& v, vec2 fallback) {
    if (v.empty()) return fallback;
    long sx = 0, sy = 0;
    for (auto p : v) { sx += p.x; sy += p.y; }
    vec2 m(static_cast<std::int32_t>(sx / static_cast<long>(v.size())), static_cast<std::int32_t>(sy / static_cast<long>(v.size())));
    vec2 best = v[0];
    for (auto p : v) if (dist(p, m) < dist(best, m)) best = p;
    return best;
}

Slot classify(const bc::ability& a) {
    Slot s;
    auto inf = a.info();
    if (!inf) return s;
    std::visit([&](auto& x) {
        using T = std::decay_t<decltype(x)>;
        s.excl = x.exclusive_with_movement;
        if constexpr (T::kind == bc::ability_kind::attack_reset) s.kind = Kind::Reset;
        else if constexpr (T::kind == bc::ability_kind::dash) { s.kind = Kind::Dash; s.range = static_cast<int>(x.range); }
        else if constexpr (T::kind == bc::ability_kind::shield) s.kind = Kind::Shield;
        else if constexpr (T::kind == bc::ability_kind::heal) { s.kind = Kind::Heal; s.range = static_cast<int>(x.range); }
        else if constexpr (T::kind == bc::ability_kind::damage) { s.kind = Kind::Damage; s.range = static_cast<int>(x.range); }
        else if constexpr (T::kind == bc::ability_kind::cc) { s.kind = Kind::Cc; s.range = static_cast<int>(x.range); }
        else if constexpr (T::kind == bc::ability_kind::aoe_damage) { s.kind = Kind::Aoe; s.range = static_cast<int>(x.range); }
    }, *inf);
    s.camps = a.can_target_camps();
    s.enemies = a.can_target_enemies();
    s.ground = a.can_target_ground();
    return s;
}

int field_at(const std::vector<std::uint16_t>& f, int W, vec2 p) {
    if (f.empty() || p.x < 0 || p.y < 0 || p.x >= W) return -1;
    std::size_t i = static_cast<std::size_t>(p.y) * static_cast<std::size_t>(W) + static_cast<std::size_t>(p.x);
    if (i >= f.size()) return -1;
    std::uint16_t v = f[i];
    return v == bc::distance_field::unreachable ? -1 : static_cast<int>(v);
}
int group_dist(const std::vector<std::uint16_t>& f, int W, const Group& g) {
    int b = -1;
    for (auto t : g.tiles) {
        int d = field_at(f, W, t);
        if (d >= 0 && (b < 0 || d < b)) b = d;
    }
    return b;
}

void init(State& s, bc::champion& me) {
    s.W = bc::map::width();
    s.H = bc::map::height();
    s.my_spawn = bc::map::spawn_region(bc::team::ally);
    s.en_spawn = bc::map::spawn_region(bc::team::enemy);
    s.static_block = bc::map::walls() | bc::map::holes() | bc::map::altars() | s.en_spawn;
    s.altars = bc::map::altars().positions();
    s.spawn_center = centre_of(s.my_spawn.positions(), me.position());

    attempt([&] {
        s.type = me.champion_name();
        s.name = bc::to_string(s.type);
        return true;
    });
    s.melee = me.attack_range() <= 1;
    using CT = bc::champion_type;
    s.is_varg = s.type == CT::varg;
    s.is_ryth = s.type == CT::ryth;
    s.is_ren = s.type == CT::ren;
    s.is_cassi = s.type == CT::cassi;
    s.is_issac = s.type == CT::issac;
    s.is_stellar = s.type == CT::stellar;
    s.is_tavi = s.type == CT::tavi;

    attempt([&] {
        bc::draft_memory_buffer dm;
        if (dm.size() >= 5 && dm[0] == std::byte{'M'} && dm[1] == std::byte{'S'}) {
            s.team_size = std::to_integer<int>(dm[DM_TEAM]);
            s.focus_main = std::to_integer<int>(dm[DM_FOCUS]) == 1;
        }
        return true;
    });

    attempt([&] {
        auto allies = bc::champions(bc::team::ally);
        s.roster = static_cast<int>(allies.size());
        for (std::size_t i = 0; i < allies.size(); ++i)
            if (allies[i] == me) s.ally_idx = static_cast<int>(i);
        return true;
    });

    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        attempt([&] { s.slot[k] = classify(abs[k]); return true; });
        if (s.slot[k].kind == Kind::Dash) s.dash_slot = k;
        if (s.slot[k].kind == Kind::Reset) s.reset_slot = k;
        if (s.slot[k].kind == Kind::Shield) s.shield_slot = k;
    }

    // Camp groups.
    std::vector<bc::map::camp_group> raw;
    attempt([&] { raw = bc::map::camp_groups(); return true; });
    for (auto& g : raw) {
        if (s.groups.size() >= MAX_GROUPS) break;
        attempt([&] {
            Group G;
            G.mask = g.spawn_tiles();
            G.tiles = G.mask.positions();
            if (G.tiles.empty()) return false;
            G.center = centre_of(G.tiles, G.tiles[0]);
            G.gems = static_cast<int>(g.gem_value());
            G.gold = static_cast<int>(g.gold_value());
            G.respawn = g.max_respawn_timer();
            for (auto& c : g.camps()) {
                if (c.is_wolf()) { G.hp += 1350; G.str += 20; }
                else if (c.is_elk()) { G.hp += 2400; G.str += 60; G.has_elk = true; }
                else if (c.is_monolith()) { G.hp += 20000; G.str += 200; G.monolith = true; }
                else G.hp += 500;
            }
            G.obj = g;
            s.groups.push_back(std::move(G));
            return true;
        });
    }

    // [MAP] Walking distances from both spawns: own half = closer to our spawn than theirs.
    attempt([&] {
        bc::bitboard wall = bc::map::walls() | bc::map::holes();
        bc::distance_field fo, fe;
        bc::bitboard vo, ve;
        fo.compute(wall, s.my_spawn, vo);
        fe.compute(wall, s.en_spawn, ve);
        s.f_own = fo.export_linear_buffer();
        std::vector<std::uint16_t> f_en = fe.export_linear_buffer();
        for (auto& g : s.groups) {
            g.d_own = group_dist(s.f_own, s.W, g);
            g.d_en = group_dist(f_en, s.W, g);
        }
        for (auto a : s.altars) {
            int bo = -1, be = -1;
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    vec2 t = a + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t)) continue;
                    int d1 = field_at(s.f_own, s.W, t), d2 = field_at(f_en, s.W, t);
                    if (d1 >= 0 && (bo < 0 || d1 < bo)) bo = d1;
                    if (d2 >= 0 && (be < 0 || d2 < be)) be = d2;
                }
            s.altar_d_own.push_back(bo);
            s.altar_d_en.push_back(be);
        }
        return true;
    });
    if (s.altar_d_own.size() != s.altars.size()) {
        s.altar_d_own.assign(s.altars.size(), 0);
        s.altar_d_en.assign(s.altars.size(), 0);
    }
    s.last_gems = static_cast<int>(me.gem_count());
    s.last_gold = static_cast<int>(me.gold_count());
}

// Walking distances from where we stand (one BFS over static walls, exported once).
void refresh_f_me(State& s, vec2 pos, int round) {
    if (s.f_me_round == round && s.f_me_pos == pos) return;
    if (!fuel_ok(20000)) return;
    attempt([&] {
        bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn;
        bc::bitboard roots, visited;
        roots.set(pos);
        s.df.compute(wall, roots, visited);
        s.f_me = s.df.export_linear_buffer();
        s.f_me_round = round;
        s.f_me_pos = pos;
        return true;
    });
}

// ---------------------------------------------------------------------------
// [SHOP] Mite's build: jungle(main) x5 -> durability(main) x5 -> bruiser health x5 -> power(main) forever.
// Main stat: strength for Varg/Issac, focus for Cassi/Stellar/Tavi, Ryth/Ren focus on 5-pick maps else strength.
// Spend everything on every visit (alive, on spawn; Tavi anywhere). One altar lock about every other trip.
// ---------------------------------------------------------------------------
void shop(State& s, bc::champion& me, bool on_spawn) {
    using I = bc::item_type;
    bool focus = s.is_cassi || s.is_stellar || s.is_tavi || ((s.is_ryth || s.is_ren) && s.focus_main);
    struct Step { I shard; I emblem; bool unlimited; };
    std::vector<Step> plan;
    if (focus) {
        plan = {{I::jungle_shard_of_focus, I::jungle_emblem_of_focus, false},
                {I::durability_shard_of_focus, I::durability_emblem_of_focus, false},
                {I::bruiser_shard_of_health, I::bruiser_emblem_of_health, false},
                {I::power_shard_of_focus, I::power_emblem_of_focus, true}};
    } else {
        plan = {{I::jungle_shard_of_strength, I::jungle_emblem_of_strength, false},
                {I::durability_shard_of_strength, I::durability_emblem_of_strength, false},
                {I::bruiser_shard_of_health, I::bruiser_emblem_of_health, false},
                {I::power_shard_of_strength, I::power_emblem_of_strength, true}};
    }
    // [SHOP] altar lock: 10 gold, about every other trip, bought before the shards so the gold is reserved.
    if (on_spawn && (s.shop_trips % 2 == 0)) {
        attempt([&] {
            auto kind = bc::consumable_type::altar_lock;
            if (me.consumables()[kind].count() == 0 && me.gold_count() >= 10 && me.can_buy(kind)) me.buy(kind);
            return true;
        });
    }
    for (int it = 0; it < 6 && fuel_ok(8000); ++it) {
        int gold = static_cast<int>(me.gold_count());
        if (gold < 30) break;
        bool bought = false;
        attempt([&] {
            auto counts = me.item_count();
            for (auto& st : plan) {
                int emb = static_cast<int>(counts[st.emblem]);
                int sh = static_cast<int>(counts[st.shard]);
                if (!st.unlimited && emb >= 1) continue;
                unsigned n = static_cast<unsigned>(gold / 30);
                if (!st.unlimited) n = std::min<unsigned>(n, static_cast<unsigned>(std::max(1, 5 - sh)));
                if (n == 0) return false;
                if (!me.can_buy(st.shard, n)) {
                    n = 1;
                    if (!me.can_buy(st.shard, 1)) return false;
                }
                me.buy(st.shard, n);
                bought = true;
                return true;
            }
            return false;
        });
        if (!bought) break;
    }
}

// ---------------------------------------------------------------------------
// Movement: one step (and a travel dash) towards any tile of `goals`.
// ---------------------------------------------------------------------------
bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {
    vec2 pos = me.position();
    bc::bitboard goals = goals_in & ~s.blocked;
    if (goals.is_empty() || goals.is_set(pos)) return false;
    bool can_dash = use_dash && s.dash_slot >= 0 && me.can_cast();
    if (!me.can_move() && !can_dash) return false;

    auto fallback = [&] {  // no field: straight line to the nearest goal tile
        auto ps = goals.positions();
        if (ps.empty() || !me.can_move()) return false;
        vec2 best = ps[0];
        for (auto p : ps) if (dist(p, pos) < dist(best, pos)) best = p;
        return attempt([&] { return me.move_towards(best); });
    };
    if (!fuel_ok(15000)) return fallback();

    s.dest.clear();
    s.dest.set(pos);
    bool ok = attempt([&] {
        s.df.compute_to(s.blocked, goals, s.dest, s.visited);
        return s.visited.is_set(pos);
    });
    if (!ok) {  // jammed by champions: plan through them and let the step fail if still occupied
        ok = attempt([&] {
            bc::bitboard b2 = s.static_block | bc::vision::camp_tiles();
            b2.set(pos, false);
            s.df.compute_to(b2, goals_in & ~s.static_block, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
        if (!ok) return fallback();
    }
    bool moved = false;
    int here = s.df.get(pos);
    // [SPELL] dashes travel with the walk: dash when it beats a plain step.
    if (can_dash && here >= 3) {
        auto ab = me.abilities()[s.dash_slot];
        if (ab.is_ready()) {
            std::optional<vec2> best;
            int bestd = here - 1;
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    int d = s.df.get(t);
                    if (d < bestd) { bestd = d; best = t; }
                }
            if (best && attempt([&] { return ab.use(*best); })) {
                moved = true;
                pos = me.position();
            }
        }
    }
    if (me.can_move()) {
        std::vector<vec2> steps;
        attempt([&] { steps = s.df.next_moves_from(pos); return true; });
        bool stepped = false;
        for (auto d : steps)
            if (attempt([&] { return me.move(d); })) { stepped = true; break; }
        if (!stepped) {  // blocked: any neighbour that does not lose ground
            int h = s.df.get(pos);
            for (int dx = -1; dx <= 1 && !stepped; ++dx)
                for (int dy = -1; dy <= 1 && !stepped; ++dy) {
                    if (!dx && !dy) continue;
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    if (s.df.get(t) > h) continue;
                    stepped = attempt([&] { return me.move_absolute(t); });
                }
        }
        moved = moved || stepped;
    }
    return moved;
}

bool go_home(State& s, bc::champion& me) { return step_towards(s, me, s.my_spawn, true); }

bc::bitboard ring(vec2 c, int r) {
    bc::bitboard b;
    b.draw_chebyshev(c, static_cast<float>(r));
    if (r > 0) {
        bc::bitboard inner;
        inner.draw_chebyshev(c, static_cast<float>(r - 1));
        b = b & ~inner;
    }
    return b;
}

// ---------------------------------------------------------------------------
// Camps: what we can see of our target group, awake monsters near us.
// ---------------------------------------------------------------------------
struct Mon {
    bc::camp c;
    vec2 p;
    float hp, mhp;
    bool awake;
};

std::vector<Mon> group_monsters(State& s, const Group& g) {
    std::vector<Mon> out;
    if (!g.obj) return out;
    bool seen = false;
    for (auto t : g.tiles) if (s.vis.is_set(t)) { seen = true; break; }
    if (!seen) return out;
    attempt([&] {
        for (auto& c : g.obj->camps()) {
            if (!c.is_visible()) continue;
            float hp = c.health();
            if (hp <= 0) continue;
            float mhp = c.max_health();
            out.push_back({c, c.spawn_position(), hp, mhp, hp < mhp});
        }
        return true;
    });
    return out;
}

// Learn the lifecycle of every group whose tiles are in view, and what allies broadcast.
void refresh_groups(State& s, int round) {
    auto sm = read_sm();
    int bg = static_cast<int>(sm[SM_BC_GROUP]) - 1;
    if (bg >= 0 && bg < static_cast<int>(s.groups.size())) {
        int ready = static_cast<int>(sm[SM_BC_READY]) * 8;
        if (ready > round) s.groups[bg].next_ok = std::max(s.groups[bg].next_ok, ready);
    }
    for (int i = 0; i < static_cast<int>(s.groups.size()) && fuel_ok(12000); ++i) {
        Group& g = s.groups[i];
        if (!g.obj) continue;
        bool visible = false;
        for (auto t : g.tiles) if (s.vis.is_set(t)) { visible = true; break; }
        if (!visible) continue;
        attempt([&] {
            auto st = g.obj->state();
            if (std::holds_alternative<bc::map::camp_group_respawning>(st)) {
                int timer = std::get<bc::map::camp_group_respawning>(st).timer;
                int ready = round + std::max(1, timer) + 1;
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

// [OPEN]/[MAP] per-camp cap after the opening: 1-3 champions per camp, more on big groups.
int group_cap(const Group& g, int round) {
    if (round < OPEN_ROUNDS) return 9;
    int cap = static_cast<int>(g.hp / 900.0 + 0.5);
    return std::clamp(cap, 2, 4);
}

bool group_usable(const State& s, const Group& g) {
    if (g.monolith) return false;                 // [MAP] never monoliths
    if (g.gems <= 0) return false;                // [MAP] mostly skip gold-only clusters
    if (g.d_own < 0) return false;                // unreachable
    if (g.d_en >= 0 && g.d_own > g.d_en + 3) return false;  // [MAP] own half (or the middle) only
    return true;
}

// [OPEN] nearest camp group that is up (or about to be), by walking distance from here.
// Rough damage per round of this champion against a monster (basic + reset double hit + spell share).
double my_dps(const State& s, bc::champion& me) {
    double d = me.strength() * (s.reset_slot >= 0 ? 2.0 : 1.0);
    if (s.is_varg) d *= 1.3;
    for (auto& sl : s.slot)
        if (sl.kind == Kind::Damage || sl.kind == Kind::Aoe) d += me.focus() * 1.6 / 8.0;
        else if (sl.kind == Kind::Cc && sl.camps && !s.is_cassi) d += me.focus() * 1.2 / 8.0;
    return std::max(d, 20.0);
}

int choose_group(State& s, bc::champion& me, int round) {
    vec2 pos = me.position();
    refresh_f_me(s, pos, round);
    auto sm = read_sm();
    int best = -1;
    double bestc = 1e18;
    double dps = my_dps(s, me);
    double hp = me.health();
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        const Group& g = s.groups[i];
        if (!group_usable(s, g) || g.bad_until > round) continue;
        int d = s.f_me.empty() ? dist(pos, g.center) : group_dist(s.f_me, s.W, g);
        if (d < 0) continue;
        int wait = g.next_ok - round;
        if (wait > d + 10) continue;              // not about to be up
        int cl = claimers(s, sm, i);
        if (cl >= group_cap(g, round)) continue;
        if (round - s.danger_r <= 40 && dist(g.center, s.danger_p) <= 7) continue;  // an enemy pack sits there
        // Solo check (not a Mite rule, but it removes Mite's "lone caster hits an elk for 30 rounds" leak):
        // the damage the monsters deal while we kill them alone must fit in our health; melee tanks may lead
        // anything that fits into 90% of their health, a ranged champion joins a claimed group or farms what it
        // can clear safely (gem clusters, a wolf with health to spare).
        if (cl == 0 && g.has_elk && !s.melee && round >= OPEN_ROUNDS && hp < 0.9 * me.max_health()) continue;
        (void)dps;
        // Nearest first (Mite), with a small value term so a 48-gem cluster pair beats a wolf a few tiles closer.
        double cost = std::max(d, wait) + g.hp / 100.0 - 0.25 * g.gems;
        if (g.d_en >= 0 && g.d_own > g.d_en - 3) cost += 8;  // [MAP] middle camps only once the own half is done
        if (cost < bestc) { bestc = cost; best = i; }
    }
    return best;
}

// ---------------------------------------------------------------------------
// Spells and attacks
// ---------------------------------------------------------------------------
// Basic attack on a unit in range, with the attack reset for a second hit ([SPELL] attack resets = farming tool,
// also used on champions).
template <class U>
bool basic_attack(State& s, bc::champion& me, const U& tgt, vec2 tpos, bool use_reset) {
    if (!me.can_attack() || dist(me.position(), tpos) > me.attack_range()) return false;
    bool hit = attempt([&] { me.attack(tgt); return true; });
    if (hit && use_reset && s.reset_slot >= 0 && me.can_cast()) {
        auto ab = me.abilities()[s.reset_slot];
        if (ab.is_ready() && attempt([&] { return ab.use(); }))
            attempt([&] { if (tgt.is_visible() && tgt.health() > 0) me.attack(tgt); return true; });
    }
    return hit;
}

// Count enemies within radius 1 of tile t.
int foes_around(const std::vector<Foe>& foes, vec2 t) {
    int n = 0;
    for (auto& f : foes) if (dist(f.p, t) <= 1) ++n;
    return n;
}

// [SPELL]/[FIGHT] Offensive spell on champions: cast whenever an enemy is within 4 and the slot is ready.
// `can_root`: an exclusive spell may be cast (we will not walk this turn). Returns true if a spell was cast.
bool cast_on_foes(State& s, bc::champion& me, const std::vector<Foe>& foes, const Foe* primary, bool can_root) {
    if (!me.can_cast() || foes.empty()) return false;
    vec2 pos = me.position();
    auto abs = me.abilities();
    // Order: damage first, then cc (Cassi: damage slot 0 then stun; Stellar: single 0 / area 1 chosen below).
    for (int k = 0; k < 2; ++k) {
        const Slot& sl = s.slot[k];
        if (sl.kind != Kind::Damage && sl.kind != Kind::Cc && sl.kind != Kind::Aoe) continue;
        if (sl.excl && !can_root) continue;
        auto& ab = abs[k];
        bool ready = false;
        attempt([&] { ready = ab.is_ready(); return true; });
        if (!ready) continue;
        int range = sl.range > 0 ? sl.range : 4;
        if (sl.ground) {
            // Area: the tile (around an enemy) that covers the most enemies; Stellar area only for 2+ ([SPELL] rule 6).
            vec2 best{0, 0};
            int bestn = 0;
            for (auto& f : foes) {
                for (int dx = -1; dx <= 1; ++dx)
                    for (int dy = -1; dy <= 1; ++dy) {
                        vec2 t = f.p + vec2(dx, dy);
                        if (!bc::map::is_in_bounds(t) || dist(t, pos) > range) continue;
                        int n = foes_around(foes, t);
                        if (n > bestn || (n == bestn && n > 0 && primary && dist(t, primary->p) <= 1 && dist(best, primary->p) > 1)) { bestn = n; best = t; }
                    }
            }
            int need = s.is_stellar ? 2 : 1;
            if (bestn >= need && attempt([&] { return ab.use(best); })) return true;
        } else if (sl.enemies) {
            const Foe* t = nullptr;
            if (primary && primary->d <= range) t = primary;
            else for (auto& f : foes) if (f.d <= range && (!t || f.d < t->d)) t = &f;
            if (t && attempt([&] { return ab.use(t->c); })) return true;
        }
    }
    return false;
}

// [SPELL] Spells on camps: Cassi/Tavi/Stellar damage spells on cooldown on any monster (exclusive: only when we do not
// walk); Ren/Ryth stun only on an awake monster; Cassi stun on an awake elk; Varg shield while an awake monster is near.
void cast_on_camp(State& s, bc::champion& me, const Mon& m, bool can_root, bool elk) {
    if (!me.can_cast()) return;
    vec2 pos = me.position();
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        const Slot& sl = s.slot[k];
        if (sl.excl && !can_root) continue;
        auto& ab = abs[k];
        bool ready = false;
        attempt([&] { ready = ab.is_ready(); return true; });
        if (!ready) continue;
        int range = sl.range > 0 ? sl.range : 4;
        if (sl.kind == Kind::Shield) {
            if (s.is_varg && m.awake && dist(pos, m.p) <= 3 && attempt([&] { return ab.use(); })) return;
            continue;
        }
        if (dist(pos, m.p) > range) continue;
        if (sl.kind == Kind::Damage && sl.camps) {
            if (attempt([&] { return ab.use(m.c); })) return;
        } else if (sl.kind == Kind::Aoe && sl.ground) {
            if (attempt([&] { return ab.use(m.p); })) return;
        } else if (sl.kind == Kind::Cc) {
            bool want = false;
            if (s.is_cassi) want = m.awake && elk;
            else if (s.is_tavi) want = true;
            else want = m.awake;  // Ren, Ryth
            if (!want) continue;
            if (sl.ground) { if (attempt([&] { return ab.use(m.p); })) return; }
            else if (sl.camps && attempt([&] { return ab.use(m.c); })) return;
        }
    }
}

// ---------------------------------------------------------------------------
// [TRIB] Tribute: on every altar pass, instantly; lock the altar first when we carry a lock and the altar is contested.
// ---------------------------------------------------------------------------
int nearest_altar(const State& s, vec2 pos, int* out_d) {
    int bi = -1, bd = 1 << 30;
    for (int pass = 0; pass < 2 && bi < 0; ++pass)
    for (std::size_t i = 0; i < s.altars.size(); ++i) {
        if (s.altar_d_own[i] < 0) continue;  // not reachable from our side
        // An altar held by an enemy pack is skipped (first pass) unless it is the only one.
        if (pass == 0 && s.danger_r > -1000 && dist(s.altars[i], s.danger_p) <= 6) continue;
        int d = s.f_me.empty() ? dist(pos, s.altars[i]) : [&] {
            int b = -1;
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    vec2 t = s.altars[i] + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t)) continue;
                    int v = field_at(s.f_me, s.W, t);
                    if (v >= 0 && (b < 0 || v < b)) b = v;
                }
            return b < 0 ? dist(pos, s.altars[i]) + 50 : b;
        }();
        bool enemy_locked = false;
        if (s.vis.is_set(s.altars[i]))
            attempt([&] { enemy_locked = bc::vision::has_altar_lock(s.altars[i]) && bc::vision::altar_lock_at(s.altars[i]).is_enemy(); return true; });
        if (enemy_locked) d += 6;  // three hits to break it
        if (d < bd) { bd = d; bi = static_cast<int>(i); }
    }
    if (out_d) *out_d = bd;
    return bi;
}

void maybe_place_lock(State& s, bc::champion& me, vec2 altar, int ai) {
    attempt([&] {
        auto kind = bc::consumable_type::altar_lock;
        const auto& lock = me.consumables()[kind];
        if (lock.count() == 0) return false;
        if (dist(me.position(), altar) > 2) return false;
        if (bc::vision::has_altar_lock(altar) && bc::vision::altar_lock_at(altar).is_ally()) return false;
        // Only contested altars (not clearly on our side): the lock protects the tribute from the enemy.
        if (s.altar_d_en[ai] >= 0 && s.altar_d_en[ai] - s.altar_d_own[ai] > 8) return false;
        return lock.use(altar);
    });
}

// Submit at an adjacent altar (converted to attacks on an enemy lock by the engine). Returns true if we acted.
bool tribute_here(State& s, bc::champion& me) {
    vec2 pos = me.position();
    if (me.gem_count() == 0) return false;
    for (std::size_t i = 0; i < s.altars.size(); ++i) {
        if (dist(pos, s.altars[i]) > 1) continue;
        maybe_place_lock(s, me, s.altars[i], static_cast<int>(i));
        if (attempt([&] { me.submit_gems(s.altars[i]); return true; })) return true;
    }
    return false;
}

bool go_tribute(State& s, bc::champion& me, int ai) {
    if (ai < 0) return false;
    if (tribute_here(s, me)) return true;
    bool moved = step_towards(s, me, ring(s.altars[ai], 1), true);
    if (dist(me.position(), s.altars[ai]) <= 1 && tribute_here(s, me)) return true;
    return moved;
}

// ---------------------------------------------------------------------------
// Capture: exactly one champion stays on the tiles ([OPEN] rule 3). The lowest ally index standing on the tiles
// captures; otherwise the nearest claiming ally (lowest index on ties). Everyone else leaves at once.
// ---------------------------------------------------------------------------
bool other_captures(State& s, bc::champion& me, const Group& g, int gi) {
    auto mask_d = [&](vec2 p) {
        int d = 99;
        for (auto t : g.tiles) d = std::min(d, dist(p, t));
        return d;
    };
    int mine = mask_d(me.position());
    auto sm = read_sm();
    bool other = false;
    attempt([&] {
        auto allies = bc::champions(bc::team::ally);
        for (std::size_t k = 0; k < allies.size() && !other; ++k) {
            auto& a = allies[k];
            try {
                if (a == me || !a.is_alive() || !a.is_visible()) continue;
                int d = mask_d(a.position());
                bool claims = k < SM_CLAIMS && sm[k] == gi + 1;
                if (d == 0) { if (mine > 0 || static_cast<int>(k) < s.ally_idx) other = true; continue; }
                if (mine == 0) continue;
                if (claims && d <= 4 && (d < mine || (d == mine && static_cast<int>(k) < s.ally_idx))) other = true;
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

// ---------------------------------------------------------------------------
// [OPEN]/[SPELL] Farming the target group: everyone on the same monster (elk / biggest first, then the most damaged),
// ranged from exactly 3 tiles, melee adjacent; attack resets for double hits; spells per the camp rules.
// Returns true when we did something with the camp.
// ---------------------------------------------------------------------------
bool farm(State& s, bc::champion& me, int round) {
    vec2 pos = me.position();
    if (s.target < 0 || s.target >= static_cast<int>(s.groups.size())) return false;
    Group& g = s.groups[s.target];
    auto mons = group_monsters(s, g);

    if (!mons.empty()) {
        s.cap_start = -1;
        // Same monster for everybody: biggest max health, then the most damaged, then position.
        const Mon* t = &mons[0];
        for (auto& m : mons) {
            if (m.mhp > t->mhp + 1) t = &m;
            else if (std::abs(m.mhp - t->mhp) <= 1 && (m.hp < t->hp - 1 || (std::abs(m.hp - t->hp) <= 1 && (m.p.y < t->p.y || (m.p.y == t->p.y && m.p.x < t->p.x))))) t = &m;
        }
        bool elk = false;
        attempt([&] { elk = t->c.is_elk(); return true; });
        int d = dist(pos, t->p);
        int want = s.melee ? 1 : 3;
        // [OPEN] the melee tank takes the aggro: a ranged champion does not wake a sleeping monster while a melee
        // ally of this group is on its way (first hitter is melee in 76-81% of Mite's mixed groups).
        if (!s.melee && !t->awake && fuel_ok(25000)) {
            bool melee_coming = false;
            auto sm = read_sm();
            attempt([&] {
                auto allies = bc::champions(bc::team::ally);
                for (std::size_t k = 0; k < allies.size() && !melee_coming; ++k) {
                    try {
                        if (static_cast<int>(k) == s.ally_idx || k >= SM_CLAIMS || sm[k] != s.target + 1) continue;
                        if (!allies[k].is_alive() || !allies[k].is_visible() || allies[k].attack_range() > 1) continue;
                        if (dist(allies[k].position(), t->p) <= 8) melee_coming = true;
                    } catch (...) {
                    }
                }
                return true;
            });
            if (melee_coming) {
                if (d > 3) step_towards(s, me, ring(t->p, 3), false);
                return true;
            }
        }
        if (d <= (s.melee ? 1 : 3)) {
            // In range: no walk this turn, so exclusive spells are allowed.
            cast_on_camp(s, me, *t, true, elk);
            basic_attack(s, me, t->c, t->p, true);
            return true;
        }
        // Walk in (melee: hit after the step); only walk-compatible spells.
        cast_on_camp(s, me, *t, false, elk);
        bc::bitboard goal = ring(t->p, want);
        if (!s.melee) {  // [OPEN] ranged stand at exactly 3, on the side we come from: tiles within 3 of us first
            bc::bitboard near = goal;
            bc::bitboard around;
            around.draw_chebyshev(pos, 4.0f);
            near = near & around & ~s.blocked;
            if (!near.is_empty()) goal = near;
        }
        if (!step_towards(s, me, goal, s.melee)) {
            // Cannot get closer (walled in / crowded): hit it if the step put us in range anyway.
        }
        if (s.melee) basic_attack(s, me, t->c, t->p, true);
        else if (dist(me.position(), t->p) <= 3) basic_attack(s, me, t->c, t->p, true);
        return true;
    }

    // Nothing alive visible.
    if (g.reward_seen == round) {
        // [OPEN] exactly one capturer: everybody else leaves this round.
        if (other_captures(s, me, g, s.target)) {
            g.bad_until = round + 10;
            drop_target(s);
            return false;
        }
        if (g.mask.is_set(pos)) {
            if (s.cap_start < 0) s.cap_start = round;
            if (round - s.cap_start > 12) {  // someone else holds it or an enemy contests: move on
                g.next_ok = round + 20;
                drop_target(s);
                return false;
            }
            // [TRIB] start the tribute on the capture tile when an altar is adjacent.
            if (me.gem_count() > 0) tribute_here(s, me);
            return true;
        }
        step_towards(s, me, g.mask, true);
        return true;
    }
    if (g.next_ok > round) {  // respawning: wait 2-3 tiles off when it is about to be back, else move on
        if (g.next_ok <= round + 6) {
            bc::bitboard r3, r1;
            for (auto t : g.tiles) { r3.draw_chebyshev(t, 3.0f); r1.draw_chebyshev(t, 1.0f); }
            bc::bitboard wait = r3 & ~r1;
            if (!wait.is_set(pos)) step_towards(s, me, wait, false);
            return true;
        }
        drop_target(s);
        return false;
    }
    // Alive but not in view (hidden by bushes or far): walk onto its tiles.
    bc::bitboard goals = g.mask;
    if (g.mask.is_set(pos)) goals.set(pos, false);
    if (!step_towards(s, me, goals, true)) {
        if (++s.recall_fail > 4) {  // reuse as a stuck counter for this group
            g.bad_until = round + 25;
            drop_target(s);
            s.recall_fail = 0;
        }
    } else {
        s.recall_fail = 0;
    }
    return true;
}

// ---------------------------------------------------------------------------
// [FIGHT]/[TARGET] Fighting champions.
// ---------------------------------------------------------------------------
struct FightPlan {
    const Foe* target = nullptr;   // the victim: killable > nearest > lowest hp%, keep the current one in range
};

const Foe* choose_victim(State& s, bc::champion& me, const std::vector<Foe>& foes, int reach) {
    const Foe* best = nullptr;
    float str = me.strength();
    auto better = [&](const Foe& a, const Foe& b) {
        bool ka = a.hp <= str, kb = b.hp <= str;      // dies to this hit
        if (ka != kb) return ka;
        bool ca = s.fight_target && a.c == *s.fight_target, cb = s.fight_target && b.c == *s.fight_target;
        if (ca != cb) return ca;                       // keep the current target while in range
        if (a.d != b.d) return a.d < b.d;              // nearest
        return a.hp / a.mhp < b.hp / b.mhp;            // lowest hp%
    };
    for (auto& f : foes) {
        if (f.d > reach) continue;
        if (!best || better(f, *best)) best = &f;
    }
    return best;
}

// Engage a victim: cast (at 4), walk into range (dash to close), hit (with the reset). Returns true if we acted.
bool engage(State& s, bc::champion& me, const std::vector<Foe>& foes, const Foe& v, bool may_approach) {
    int range = me.attack_range();
    vec2 pos = me.position();
    bool acted = false;
    if (v.d <= range) {
        // Stand and hit: exclusive spells allowed, then the basic attack (casters hit from 3 and do not kite).
        acted = cast_on_foes(s, me, foes, &v, true);
        acted = basic_attack(s, me, v.c, v.p, true) || acted;
        return acted;
    }
    if (v.d <= 4) {
        // [FIGHT] the opener: a spell at 4; an exclusive cast roots us this turn (melee still cannot reach).
        if (cast_on_foes(s, me, foes, &v, true)) {
            if (!me.can_move()) return true;
            // a walk-compatible spell was cast: we may still walk in
        }
    }
    if (!may_approach) return acted;
    // [MAP] never enter the enemy half except while chasing (at most CHASE_MAX rounds).
    bool chase_ok = s.chase_rounds < CHASE_MAX;
    bc::bitboard goal = ring(v.p, range);
    if (!chase_ok) {
        bc::bitboard own;
        for (auto t : goal.positions())
            if (field_at(s.f_own, s.W, t) >= 0) own.set(t);
        goal = own;  // (approximation: tiles reachable from our spawn; the enemy-half test is in may_approach)
    }
    bool moved = step_towards(s, me, goal, true);
    if (moved) {
        acted = true;
        if (s.melee && dist(me.position(), v.p) <= range) basic_attack(s, me, v.c, v.p, true);
        else if (!s.melee && me.can_attack() && dist(me.position(), v.p) <= range) basic_attack(s, me, v.c, v.p, true);
    }
    return acted;
}

// ---------------------------------------------------------------------------
// One turn
// ---------------------------------------------------------------------------
void play_turn(State& s) {
    bc::champion& me = bc::self();
    if (!s.ready) {
        s.ready = true;
        init(s, me);
    }
    const int round = static_cast<int>(bc::round_number());

    if (!me.is_alive()) {  // [SHOP] Mite never buys while dead
        drop_target(s);
        s.last_hp = -1;
        return;
    }
    vec2 pos = me.position();
    const float mhp = std::max(1.0f, me.max_health());
    float hp = me.health();
    int gems = static_cast<int>(me.gem_count());
    int gold = static_cast<int>(me.gold_count());
    bool on_spawn = s.my_spawn.is_set(pos);
    if (s.last_hp >= 0 && hp < s.last_hp - 1.0f) s.hit_round = round;
    s.last_hp = hp;

    // Capture reward landed while standing on our target's tiles: the group respawns in `respawn` rounds.
    if (s.target >= 0 && (gems > s.last_gems || gold > s.last_gold) && s.groups[s.target].mask.is_set(pos)) {
        Group& g = s.groups[s.target];
        g.next_ok = round + g.respawn;
        g.reward_seen = -1;
        broadcast_cooldown(s.target, g.next_ok);
        drop_target(s);
    }
    s.last_gems = gems;

    if (me.is_recalling() || me.is_submitting_gems() || me.is_teleporting()) {
        s.last_gold = static_cast<int>(me.gold_count());
        return;
    }
    if (!fuel_ok(20000)) return;

    // [SHOP] on spawn: spend everything (also Tavi in the field), then stay one round to heal to full.
    if (on_spawn || s.is_tavi) {
        if (gold >= 10) shop(s, me, on_spawn);
        gold = static_cast<int>(me.gold_count());
    }
    s.last_gold = gold;
    if (on_spawn) {
        if (s.spawn_arrive < round - 1) { s.spawn_arrive = round; ++s.shop_trips; }
        if (me.health() < me.max_health() - 0.5f) return;  // [RECALL] stay until full
    }

    s.blocked = s.static_block | bc::vision::champion_tiles() | bc::vision::camp_tiles();
    s.blocked.set(pos, false);
    attempt([&] { me.visible_tiles_into(s.vis); return true; });
    refresh_groups(s, round);
    hp = me.health();
    float hpr = hp / mhp;

    // Enemies in vision (never the ones on their spawn).
    std::vector<Foe> foes;
    for (auto& c : bc::vision::champions(bc::team::enemy)) {
        attempt([&] {
            if (!c.is_alive()) return false;
            Foe f{c, c.position(), c.health(), std::max(1.0f, c.max_health()), 0, false, true};
            if (s.en_spawn.is_set(f.p)) return false;
            f.d = dist(f.p, pos);
            foes.push_back(f);
            return true;
        });
    }
    for (auto& f : foes) {
        for (auto& o : foes) if (!(o.c == f.c) && dist(o.p, f.p) <= 4) f.isolated = false;
        if (s.seen_round == round - 1)
            for (auto& [c, p] : s.seen)
                if (c == f.c && !(p == f.p) && dist(f.p, pos) > dist(p, pos)) f.retreating = true;
    }
    s.seen.clear();
    for (auto& f : foes) s.seen.push_back({f.c, f.p});
    s.seen_round = round;
    int nearest_foe = 99;
    for (auto& f : foes) nearest_foe = std::min(nearest_foe, f.d);
    bool in_enemy_half = field_at(s.f_own, s.W, pos) >= 0 && [&] {
        // enemy half = closer to their spawn by more than 3 (using straight distance as a cheap proxy for their field)
        int dm = field_at(s.f_own, s.W, pos);
        int de = dist(pos, centre_of(s.en_spawn.positions(), pos));
        return de + 3 < dm;
    }();
    if (nearest_foe <= ENGAGE_RANGE) ++s.chase_rounds; else s.chase_rounds = 0;
    // Local numbers (deviation from pure Mite, which walks into any fight): visible enemies within 8 vs visible allies
    // within 6 of us (us included). Outnumbered by 2+ = an enemy pack; remember where it is for 40 rounds.
    int allies_near = 1, foes_near = 0;
    attempt([&] {
        for (auto& a : bc::vision::champions(bc::team::ally))
            if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 6) ++allies_near;
        return true;
    });
    for (auto& f : foes) if (f.d <= 8) ++foes_near;
    bool outnumbered = foes_near > allies_near + 1;
    if (outnumbered) {
        long sx = 0, sy = 0;
        for (auto& f : foes) { sx += f.p.x; sy += f.p.y; }
        s.danger_p = vec2(static_cast<std::int32_t>(sx / foes.size()), static_cast<std::int32_t>(sy / foes.size()));
        s.danger_r = round;
    }
    if (round - s.danger_r > 40) s.danger_r = -1000;

    // Awake monsters within reach of us (range 3) hitting somebody: a recall next to them is interrupted.
    bool awake_near = false;
    for (auto& g : s.groups) {
        if (dist(g.center, pos) > 6) continue;
        for (auto& m : group_monsters(s, g))
            if (m.awake && dist(m.p, pos) <= 3) awake_near = true;
    }
    bool safe = nearest_foe >= RECALL_SAFE && !awake_near;

    // ---- [RECALL] hp < 50%: recall when the nearest enemy is 7+ tiles away, else walk home (no fighting back).
    if (hpr * 100 < RECALL_PCT && !on_spawn) {
        // A bag next to an altar is banked first (damage does not interrupt a tribute) when nobody is adjacent.
        if (gems > 0 && nearest_foe > 3 && tribute_here(s, me)) return;
        if (safe && attempt([&] { me.recall(); return true; })) return;
        if (awake_near && nearest_foe >= RECALL_SAFE) {
            // Out of the monster's range (3) first, then recall next turn (Mite retries under camp fire: a bug we skip).
            bc::bitboard away;
            for (auto& g : s.groups) {
                if (dist(g.center, pos) > 6) continue;
                for (auto& m : group_monsters(s, g)) if (m.awake) away |= ring(m.p, 4) | ring(m.p, 5);
            }
            if (!away.is_empty() && step_towards(s, me, away, true)) return;
        }
        go_home(s, me);
        return;
    }

    // ---- [TRIB] an altar right here with a bag: bank even with enemies around (damage does not interrupt it).
    if (gems >= 20 && nearest_foe > 2) {
        for (auto a : s.altars)
            if (dist(pos, a) <= 1 && tribute_here(s, me)) return;
    }

    // ---- [FIGHT] enemy champions.
    if (!foes.empty()) {
        // Spells never saved: a ready damage/stun spell goes on an enemy within 4 before anything else.
        // Victim: killable > current > nearest > lowest hp%, within reach this turn (range + 1 step; +2 with a dash).
        int reach = me.attack_range() + 1 + (s.dash_slot >= 0 ? 2 : 0);
        const Foe* v = choose_victim(s, me, foes, std::max(reach, ENGAGE_RANGE));
        if (v) {
            // [FIGHT] no chasing: a victim walking away out of our range is not followed; isolated targets preferred
            // by the engage decision (we do not wait for a numbers or hp edge).
            bool may_approach = !v->retreating && !in_enemy_half;
            if (in_enemy_half && s.chase_rounds < CHASE_MAX) may_approach = !v->retreating;
            // Local numbers at the point of contact (deviation from pure Mite, which walks into any fight):
            // we walk in only when our bodies within 6 of us are at least theirs within 6 of the victim minus one.
            int foes_at_victim = 0;
            for (auto& f : foes) if (dist(f.p, v->p) <= 6) ++foes_at_victim;
            bool killable = v->d <= me.attack_range() && v->hp <= me.strength();
            if (allies_near + 1 < foes_at_victim && !killable) {
                if (s.target >= 0 && dist(s.groups[s.target].center, v->p) <= 7) {
                    s.groups[s.target].bad_until = round + 30;
                    drop_target(s);
                }
                if (v->d <= 4) cast_on_foes(s, me, foes, v, nearest_foe > me.attack_range());
                if (nearest_foe <= 5 || outnumbered) {
                    // Back off toward the allies behind us (or spawn), keeping the pack together.
                    vec2 goal = s.spawn_center;
                    attempt([&] {
                        int bd = 99;
                        for (auto& a : bc::vision::champions(bc::team::ally)) {
                            if (a == me || !a.is_alive()) continue;
                            vec2 ap = a.position();
                            int dd = dist(ap, pos);
                            if (dd >= 3 && dd < bd && dist(ap, v->p) > v->d) { bd = dd; goal = ap; }
                        }
                        return true;
                    });
                    if (!me.can_move()) return;
                    bc::bitboard g2;
                    g2.draw_chebyshev(goal, 1.0f);
                    if (!step_towards(s, me, g2, true)) go_home(s, me);
                    return;
                }
                may_approach = false;
            }
            // Ranged bodies stay behind the melee: approach only when an ally is as close to the victim as we are.
            if (!s.melee && v->d > me.attack_range()) {
                bool ally_front = false;
                attempt([&] {
                    for (auto& a : bc::vision::champions(bc::team::ally))
                        if (!(a == me) && a.is_alive() && dist(a.position(), v->p) <= v->d) ally_front = true;
                    return true;
                });
                if (!ally_front) may_approach = false;
            }
            bool engaged_now = v->d <= me.attack_range() || v->d <= 4 || may_approach;
            if (engaged_now) {
                bool acted = engage(s, me, foes, *v, may_approach);
                if (acted) {
                    s.fight_target = v->c;
                    s.fight_round = round;
                    return;
                }
                if (v->d <= 4) return;  // rooted by the cast or nothing to do: stay with the fight
            }
        }
        // keep the current job otherwise (57% keep hitting the camp)
    }
    if (s.fight_round < round - 3) s.fight_target.reset();

    // ---- [TRIB] bank: instantly at an adjacent altar; after a capture walk to a close altar; big bags always.
    refresh_f_me(s, pos, round);
    int ad = 99;
    int ai = gems > 0 ? nearest_altar(s, pos, &ad) : -1;
    if (gems > 0 && ai >= 0) {
        if (ad <= 1 && tribute_here(s, me)) return;
        // "On every pass" = the altar is right there (<= 3); a detour only for a bigger bag; any bag late in the game.
        bool want = ad <= 3 || (gems >= 20 && ad <= 6) || (gems >= 40 && ad <= TRIB_DETOUR) || gems >= BIG_BAG || round >= 1900;
        if (want && s.cap_start < 0) {
            // [RECALL] recall as a teleport when 5 + spawn->altar is shorter than the walk (bank recalls on rows/lanes).
            int sa = s.altar_d_own[ai];
            if (safe && !on_spawn && sa >= 0 && ad > 5 + sa + 3 && attempt([&] { me.recall(); return true; })) return;
            if (go_tribute(s, me, ai)) return;
        }
    }

    // ---- [RECALL] shop recall: ~180 gold carried (or 90 and hurt), when safe, not in the middle of a capture.
    if (!on_spawn && safe && s.cap_start < 0 && (gold >= SHOP_GOLD || (gold >= SHOP_GOLD_LOW && hpr < 0.75f)) &&
        dist(pos, s.spawn_center) > 4) {
        if (gems >= 10 && ai >= 0 && ad <= 8 && go_tribute(s, me, ai)) return;  // bank first if an altar is right here
        if (attempt([&] { me.recall(); return true; })) return;
    }

    // ---- [OPEN]/[MAP] farm: nearest camp group that is up (or about to be), claimed through shared memory.
    bool expired = s.target >= 0 && (s.groups[s.target].bad_until > round || !group_usable(s, s.groups[s.target]));
    if (s.target < 0 || expired) {
        int t = choose_group(s, me, round);
        if (t != s.target) s.cap_start = -1;
        s.target = t;
        s.target_round = round;
        write_claim(s, t);
    }
    if (s.target >= 0) {
        Group& g = s.groups[s.target];
        // [RECALL] recall as a teleport: 5 + spawn->camp shorter than walking there.
        int dm = s.f_me.empty() ? dist(pos, g.center) : group_dist(s.f_me, s.W, g);
        if (safe && !on_spawn && g.d_own >= 0 && dm > 5 + g.d_own + 3 && s.cap_start < 0 && gems < 20 &&
            attempt([&] { me.recall(); return true; }))
            return;
        if (farm(s, me, round)) return;
        // farm() dropped the target (capturer elsewhere / respawning): pick again right away.
        if (s.target < 0 && fuel_ok(30000)) {
            int t = choose_group(s, me, round);
            s.target = t;
            s.target_round = round;
            write_claim(s, t);
            if (t >= 0 && farm(s, me, round)) return;
        }
    }
    // Nothing to farm: wait near the group that comes back first, out of monster range.
    if (s.target < 0) {
        int wi = -1, wbest = 1 << 30;
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            const Group& g = s.groups[i];
            if (!group_usable(s, g) || g.next_ok <= round) continue;
            int w = (g.next_ok - round) + dist(pos, g.center) / 2;
            if (w < wbest) { wbest = w; wi = i; }
        }
        if (wi >= 0 && wbest < 150) {
            const Group& g = s.groups[wi];
            bc::bitboard r5, r4;
            for (auto t : g.tiles) { r5.draw_chebyshev(t, 5.0f); r4.draw_chebyshev(t, 4.0f); }
            step_towards(s, me, r5 & ~r4, true);
        } else if (!on_spawn && gems > 0 && ai >= 0) {
            go_tribute(s, me, ai);
        }
    }
}

[[noreturn]] void run_game() {
    State s;
    for (;;) {
        try {
            play_turn(s);
        } catch (const std::exception& e) {
            if (++g_errors <= 5) std::printf("[turn err] %s\n", e.what());
        } catch (...) {
            ++g_errors;
        }
        bc::end_turn();
    }
}

}  // namespace

int main() {
    if (bc::is_draft()) run_draft();
    run_game();
}

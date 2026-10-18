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
    if (P_D34_FAMILY) buf[28] = static_cast<std::byte>(g_de_map);
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

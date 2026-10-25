# fuelfit o07 (changes the start-up schedule, not the play): no decision reads the fuel. fuel_ok() is always true;
# start-up runs on a fixed schedule by group count (turn 1: boards, altars, spawn and up to 30 camp groups; next turns:
# the rest in chunks of 30; then walking fields, roles, shop and the dash-hole scan; the champion plays from the turn
# after). The status line only every STATUS_EVERY rounds (rounds 1-3 printed it too: 19k each).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b,must=True):
    global s
    n=s.count(a)
    if n!=1:
        assert not must,(a[:70],n); return
    s=s.replace(a,b)
rep("inline bool fuel_ok(std::uint64_t need) { return bc::fuel_remaining() > need + FUEL_RESERVE; }",
    "inline bool fuel_ok(std::uint64_t) { return true; }  // fuelfit o07: no decision reads the fuel; every pass is bounded instead", must=False)
rep("    int dh_stage = 0;","    int dh_stage = 0;\n    std::vector<bc::map::camp_group> raw_groups;  // fuelfit o07: start-up groups still to read\n    std::size_t init_gi = 0;")
rep("""    FP(21, "init-groups");
    std::vector<bc::map::camp_group> raw_groups;
    attempt([&] {
        raw_groups = bc::map::camp_groups();
        return true;
    });
    s.groups.reserve(std::min<std::size_t>(raw_groups.size(), MAX_GROUPS));
    for (auto& g : raw_groups) {
        if (s.groups.size() >= MAX_GROUPS) break;
        attempt([&] {""","""    FP(21, "init-groups");
    attempt([&] {
        s.raw_groups = bc::map::camp_groups();
        return true;
    });
    s.groups.reserve(std::min<std::size_t>(s.raw_groups.size(), MAX_GROUPS));
}

// fuelfit o07: up to `quota` camp groups per call (about 3k fuel each); true once all are read.
bool init_groups(State& s, std::size_t quota) {
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
    std::size_t done = 0;
    for (; s.init_gi < s.raw_groups.size() && done < quota; ++s.init_gi, ++done) {
        auto& g = s.raw_groups[s.init_gi];
        if (s.groups.size() >= MAX_GROUPS) break;
        attempt([&] {""")
rep("""        G.obj = std::move(g);  // fuelfit o06: raw_groups is not read again
        s.groups.push_back(std::move(G));
        return true;
        });
    }
    {""","""        G.obj = std::move(g);  // fuelfit o06: raw_groups is not read again
        s.groups.push_back(std::move(G));
        return true;
        });
    }
    if (s.init_gi < s.raw_groups.size() && s.groups.size() < MAX_GROUPS) return false;
    s.raw_groups.clear();
    s.raw_groups.shrink_to_fit();
    {""")
rep("""bool init(State& s, bc::champion& me) {
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
        if (s.dash_slot >= 0 && !P_DHFUEL) mp_find_dashholes(s);  // mapplan_game.h rule 5 (P_DHFUEL: scanned in play_turn)
    }
    return true;
}""","""// fuelfit o07: a fixed schedule (the first turn has a double budget, ~200k): turn 1 reads the boards, the altars, the
// spawn and up to 30 groups (~100k on a 30-group map); a map with more groups reads the rest on the next turns, 30 a
// turn; the fields, roles, shop and dash-hole scan (~60k) follow, on turn 1 when the map has at most 20 groups.
constexpr std::size_t INIT_GROUPS_TURN = 30, INIT_SMALL_MAP = 20;
bool init(State& s, bc::champion& me) {
    if (s.init_stage == 0) {
        s.init_stage = 1;
        init_map(s, me);
        if (!init_groups(s, INIT_GROUPS_TURN)) return false;
        s.init_stage = 2;
        if (s.groups.size() > INIT_SMALL_MAP) return false;
    }
    if (s.init_stage == 1) {
        if (!init_groups(s, INIT_GROUPS_TURN)) return false;
        s.init_stage = 2;
        return false;
    }
    if (s.init_stage == 2) {
        s.init_stage = 3;
        init_paths(s);
        if (false) mp_game_plan(s);  // only the rules that need it: off = v52 games
        init_roles(s, me);
        if (s.dash_slot >= 0) mp_find_dashholes(s);  // mapplan_game.h rule 5 (o06: one bitboard pass)
    }
    return true;
}""")
rep("""        if (!init(s, me)) {
            g_mode = "init-fuel";
            return;
        }
        s.ready = true;  // never retry a failing init every turn
        if (!fuel_ok(40000)) {
            g_mode = "init-fuel";
            return;
        }""","""        if (!init(s, me)) {
            g_mode = "init";
            return;
        }
        s.ready = true;  // never retry a failing init every turn
        g_mode = "init-done";  // fuelfit o07: the champion plays from the next turn (fixed, whatever the map)
        return;""")
rep("        if (round % STATUS_EVERY != 0 && round > 3 && !every) return false;","        if (round % STATUS_EVERY != 0 && !every) return false;  // fuelfit o07: no extra lines on rounds 1-3 (19k each)")
rep("""        s.mono_guard = s.mono_guard && !s.mono_only && !s.mono_farm;
    }

}""","""        s.mono_guard = s.mono_guard && !s.mono_only && !s.mono_farm;
    }
    return true;  // fuelfit o07 (a bool function without it falls off the end: wasm trap, champion restarted)
}""")
open(p,'w',newline='').write(s)

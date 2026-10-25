# fuelfit o58 (after o57): the idle rounds of big maps (init_wait) also build the altar fields (br_static_step work),
# and the play-turn altar schedule starts at round play_from + 3 instead of 3, so the first playing turns on 100x100
# maps (already 97-160k: first choose_target forward field + path searches) do not carry a 24k altar field too.
# init_wait budget 70k -> 60k (it measured 80-83k on road_of_riches). Exact as long as nobody has gems before the
# fields are done (same argument as o32/o35).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""    long left = 70000;
    while (left >= price && s.pd_rf_done < s.groups.size()) {
        const std::size_t before = s.pd_rf_done;
        farm_pd_ready(s);
        left -= price;
        if (s.pd_rf_done == before) break;
    }
}""","""    long left = 60000;  // fuelfit o58: 70k measured 80-83k on road_of_riches
    while (left >= price && s.pd_rf_done < s.groups.size()) {
        const std::size_t before = s.pd_rf_done;
        farm_pd_ready(s);
        left -= price;
        if (s.pd_rf_done == before) break;
    }
    // fuelfit o58: altar fields (cap 400, ~24k on 100x100) in the idle rounds too, while they fit
    const long aprice = 1200 + (static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height()) * 5) / 2;
    while (left >= aprice && br_static_one(s)) left -= aprice;
}""")
rep("void br_static_step(State& s, int round) {\n    if (!P_BRCACHE || round < P_BRC_R0 || s.altars.size() > 64) return;",
"""// fuelfit o58: one altar field; true if one was built (false when done or not applicable)
bool br_static_one(State& s) {
    if (!P_BRCACHE || s.altars.size() > 64) return false;
    if (!g_brs.init) {
        g_brs.init = true;
        g_brs.f.resize(s.altars.size());
        g_brs.reached.resize(s.altars.size());
    }
    if (g_brs.built >= static_cast<int>(s.altars.size())) return false;
    const int i = g_brs.built++;
    attempt([&] {
        bc::bitboard roots;
        vec2 a = s.altars[i];
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 p = a + vec2(dx, dy);
                if (bc::map::is_in_bounds(p) && !s.static_block.is_set(p)) roots.set(p);
            }
        g_brs.f[i].compute(s.static_block, roots, g_brs.reached[i], 400);
        return true;
    });
    return true;
}
void br_static_step(State& s, int round) {
    if (!P_BRCACHE || round < P_BRC_R0 || round < s.play_from + 3 || s.altars.size() > 64) return;  // fuelfit o58""")
rep("bool farm_pd_ready(State& s);  // fuelfit o45, defined with choose_target","bool farm_pd_ready(State& s);  // fuelfit o45, defined with choose_target\nbool br_static_one(State& s);  // fuelfit o58, defined with br_static_step")
open(p,'w',newline='').write(s)

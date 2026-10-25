# fuelfit o06 (exact): start-up cheaper. (a) camp_group moved into the Group, not copied (500 fuel a group);
# (b) each camp's kind flags read once per camp (monster_stats took them again); (c) the dash-hole scan as bitboard
# shifts (16 shifts for the whole map) instead of 16 tile tests per hole (2.6k a hole, 875k on starfish).
import sys
d=sys.argv[1]
p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b,s_=None):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""        for (auto& c : g.camps()) {
            double h = 0, st = 0;
            monster_stats(c, h, st);
            G.hp += h;
            G.str += st;
            G.monolith = G.monolith || c.is_monolith();
            G.gem_cluster = G.gem_cluster || c.is_gem_cluster();
            G.cluster = G.cluster || c.is_gem_cluster() || c.is_gold_cluster();
#if P_E2 == 1
            G.wolf_only = G.wolf_only && c.is_wolf();
#endif
            ++G.members;
        }
        G.obj = g;""","""        for (auto& c : g.camps()) {
            const bool cw = c.is_wolf(), ce = c.is_elk(), cm = c.is_monolith(), cgem = c.is_gem_cluster(), cgold = c.is_gold_cluster();
            double h = 0, st = 0;
            monster_stats_k(c, cw, ce, cm, cgem, cgold, h, st);
            G.hp += h;
            G.str += st;
            G.monolith = G.monolith || cm;
            G.gem_cluster = G.gem_cluster || cgem;
            G.cluster = G.cluster || cgem || cgold;
#if P_E2 == 1
            G.wolf_only = G.wolf_only && cw;
#endif
            ++G.members;
        }
        G.obj = std::move(g);  // fuelfit o06: raw_groups is not read again""")
rep("""void monster_stats(const bc::camp& c, double& hp, double& str) {
    if (c.is_wolf()) { hp = 1350; str = 20; }
    else if (c.is_elk()) { hp = 2400; str = 60; }
    else if (c.is_monolith()) { hp = 20000; str = 200; }
    else { hp = 500; str = 0; }  // gem / gold cluster
#if P_E3
    // SDK-compatible fallback: Golem was introduced after older camp headers.
    // Prefer the engine-provided base_stats() below, which is authoritative.
    if (c.is_gem_cluster() || c.is_gold_cluster()) { hp = 120; str = 0; }
    else if (!c.is_wolf() && !c.is_elk() && !c.is_monolith()) { hp = 5000; str = 120; }""","""void monster_stats_k(const bc::camp& c, bool cw, bool ce, bool cm, bool cgem, bool cgold, double& hp, double& str) {
    if (cw) { hp = 1350; str = 20; }
    else if (ce) { hp = 2400; str = 60; }
    else if (cm) { hp = 20000; str = 200; }
    else { hp = 500; str = 0; }  // gem / gold cluster
#if P_E3
    // SDK-compatible fallback: Golem was introduced after older camp headers.
    // Prefer the engine-provided base_stats() below, which is authoritative.
    if (cgem || cgold) { hp = 120; str = 0; }
    else if (!cw && !ce && !cm) { hp = 5000; str = 120; }""")
# the tail of monster_stats_k is the old tail; re-add the old monster_stats as a wrapper
rep("""#if P_E3
// econ3 E3: a camp's attack range""","""void monster_stats(const bc::camp& c, double& hp, double& str) {
    monster_stats_k(c, c.is_wolf(), c.is_elk(), c.is_monolith(), c.is_gem_cluster(), c.is_gold_cluster(), hp, str);
}
#if P_E3
// econ3 E3: a camp's attack range""")
open(p,'w',newline='').write(s)
p=d+'/mapplan_game.h'; s=open(p,newline='').read()
rep("""    if (s.dh_stage == 0) {
        s.mp_hole_all = bc::map::holes();
        s.dh_bad = bc::map::walls() | s.mp_hole_all | bc::map::altars();
        attempt([&] { for (auto h : s.mp_hole_all.positions()) s.dh_list.push_back(h); return true; });
        s.dh_stage = 1;
    }
    while (s.dh_stage == 1) {""","""    if (s.dh_stage == 0) {
        s.mp_hole_all = bc::map::holes();
        s.dh_bad = bc::map::walls() | s.mp_hole_all | bc::map::altars();
        // fuelfit o06: a hole is crossable when, for some direction d, the tiles h-d and h+d are both in bounds and
        // free: free shifted by -d AND free shifted by +d, over the holes, for the four axes (16 shifts for the map).
        attempt([&] {
            const bc::bitboard free = ~s.dh_bad;
            const int dirs[4][2] = {{1, 0}, {0, 1}, {1, 1}, {1, -1}};
            for (auto& dd : dirs) {
                const bc::bitboard plus = free.shift_right(-dd[0]).shift_up(-dd[1]);
                const bc::bitboard minus = free.shift_right(dd[0]).shift_up(dd[1]);
                s.mp_dashholes |= s.mp_hole_all & plus & minus;
            }
            return true;
        });
        s.dh_stage = 2;
    }
    while (s.dh_stage == 1) {""")
open(p,'w',newline='').write(s)

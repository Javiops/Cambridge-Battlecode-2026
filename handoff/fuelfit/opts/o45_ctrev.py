# fuelfit o45 (farm section): choose_target without its per-call engine search, and a leaner scoring loop.
# (A) Reverse fields. The walking distance from here to each camp group used to come from ONE forward BFS per call
#     (distance_field::compute from pos over static walls, 3.4k fuel on 41x41 .. 30k on 100x100, every retarget turn)
#     plus a min over the group's tiles. The grid is undirected and the walls never change, so the same number is the
#     multi-source field of the GROUP's tiles read at pos: one compute per group ONCE per game (42k on corridors/12 groups
#     .. 551k on big_world/24 groups, bench b6), then is_set + get per group per call (1.2k-3.3k). Exact: verified
#     identical to the forward min on 6 maps, 287 champion positions, 0 mismatches. The forward BFS clears pos from the
#     walls, so when pos itself is a static-block tile (enemy spawn, altar) the original path is kept. While the fields
#     are not all computed yet, the original path runs: the decision is the same either way, only the fuel schedule
#     differs. P_FARM_PD_PER_TURN (default: all) lets the integrator spread the precompute over turns.
# (B) Scoring loop, pure C++ (12k fuel mean on heavy turns before): claimers counted in ONE pass over the claim slots
#     instead of one pass per group; the per-group distances to the spawn and the enemy spawn, and the recall cycle
#     term, computed once per game (centres and spawn_pd are set in init); walk() computes the straight-line distance
#     only when it is used; the danger window test hoisted. Identical integers/booleans and the same double expressions
#     in the same order, so identical scores. Requires o41 (anchors). No fuel_ok, fixed bounds, no new output.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)

rep("""    std::vector<int> pd_gd;          // P_FUELGUARD: walking distance to each camp group from pd_pos (-1 unreached)
""","""    std::vector<int> pd_gd;          // P_FUELGUARD: walking distance to each camp group from pd_pos (-1 unreached)
    std::vector<bc::distance_field> pd_rf;  // fuelfit o45: per-group field from the group's tiles over static walls
    std::vector<bc::bitboard> pd_rv;        // fuelfit o45: its reached mask
    std::size_t pd_rf_done = 0;             // fuelfit o45: groups whose field is computed (in index order)
""")

rep("""int choose_target_impl(State& s, bc::champion& me, int round) {
    FP_SCOPE(15, "choose_target");""","""#ifndef P_FARM_PD_PER_TURN
#define P_FARM_PD_PER_TURN 1000000  // fuelfit o45: reverse fields computed per call of farm_pd_ready (default: all at once)
#endif
// fuelfit o45: compute up to P_FARM_PD_PER_TURN missing per-group fields; true when every group has one.
bool farm_pd_ready(State& s) {
    if (s.pd_rf.size() != s.groups.size()) {
        s.pd_rf.resize(s.groups.size());
        s.pd_rv.resize(s.groups.size());
        s.pd_rf_done = 0;
    }
    for (int k = 0; k < P_FARM_PD_PER_TURN && s.pd_rf_done < s.groups.size(); ++k) {
        const std::size_t i = s.pd_rf_done;
        if (!attempt([&] {
                bc::bitboard roots;
                for (auto t : s.groups[i].tiles) roots.set(t);
                s.pd_rf[i].compute(s.static_block, roots & ~s.static_block, s.pd_rv[i], 200);
                return true;
            }))
            return false;
        ++s.pd_rf_done;
    }
    return s.pd_rf_done == s.groups.size();
}
int choose_target_impl(State& s, bc::champion& me, int round) {
    FP_SCOPE(15, "choose_target");""")

rep("""    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();
    bool have_pd = cached || (P_PATHD && !g_nopd && attempt([&] {  // walking distance from here to every camp group
        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;
    }));
    if (have_pd && !cached) {  // the walking distance to each group, read once per tile""","""    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();
    bool have_pd = cached;
    if (!cached && P_PATHD && !g_nopd && farm_pd_ready(s) && !s.static_block.is_set(pos)) {
        // fuelfit o45 (A): the group fields read at pos give the same walking distances as the forward search
        s.pd_gd.assign(s.groups.size(), -1);
        if (attempt([&] {
                for (std::size_t i = 0; i < s.groups.size(); ++i)
                    s.pd_gd[i] = s.pd_rv[i].is_set(pos) ? static_cast<int>(s.pd_rf[i].get(pos)) : -1;
                return true;
            })) {
            s.pd_pos = pos;
            cached = have_pd = true;
        }
    }
    have_pd = have_pd || (P_PATHD && !g_nopd && attempt([&] {  // walking distance from here to every camp group
        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;
    }));
    if (have_pd && !cached) {  // the walking distance to each group, read once per tile""")

rep("""    auto walk = [&](const Group& g) {
        int d = dist(pos, g.center);
        if (!have_pd) return d;
        if (s.pd_pos == pos && s.pd_gd.size() == s.groups.size()) {
            int b = s.pd_gd[static_cast<std::size_t>(&g - s.groups.data())];
            return b >= 0 ? b : unreach(d);
        }
        int b = 1 << 20;
        for (auto t : g.tiles)
            if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
        return b < (1 << 20) ? b : unreach(d);
    };
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;
        bool held = s.hold_group[i];
        if (!held && round - s.danger_r <= P_DANGER_T && dist(g.center, s.danger_p) <= P_DANGER_R) continue;""","""    auto walk = [&](const Group& g) {  // fuelfit o45 (B): the straight-line distance only when it is used
        if (!have_pd) return dist(pos, g.center);
        if (s.pd_pos == pos && s.pd_gd.size() == s.groups.size()) {
            int b = s.pd_gd[static_cast<std::size_t>(&g - s.groups.data())];
            return b >= 0 ? b : unreach(dist(pos, g.center));
        }
        int b = 1 << 20;
        for (auto t : g.tiles)
            if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
        return b < (1 << 20) ? b : unreach(dist(pos, g.center));
    };
    // fuelfit o45 (B): per-game constants of each group (centres and spawn_pd are fixed after init) and one pass over
    // the claim slots for every group's claimer counts (count_claimers did one pass per group).
    struct GroupConst { bool near_en, half; double cycle; };
    static std::vector<GroupConst> gc;
    if (gc.size() != s.groups.size()) {
        gc.resize(s.groups.size());
        for (std::size_t i = 0; i < s.groups.size(); ++i) {
            const Group& g = s.groups[i];
            gc[i].near_en = dist(g.center, s.en_center) < 8;
            gc[i].half = dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6;
            gc[i].cycle = 8.0 + (P_PATHD && g.spawn_pd >= 0 ? g.spawn_pd : dist(s.spawn_center, g.center));
        }
    }
    static std::vector<int> claimers_of, tank_claims_of;
    claimers_of.assign(s.groups.size(), 0);
    tank_claims_of.assign(s.groups.size(), 0);
    {
        const bool dps_adj = PR.dpsfarm && !i_am_tank(s);
        const int tb = dps_adj ? tank_bits(s) : 0;
        for (int k = 0; k < claim_slots(s); ++k) {
            if (k == s.ally_idx) continue;
            const int v = claim_value(s, sm, k);
            if (v <= 0 || v - 1 >= static_cast<int>(s.groups.size())) continue;
            ++claimers_of[v - 1];
            if (dps_adj && ((tb >> k) & 1)) ++tank_claims_of[v - 1];
        }
    }
    const bool danger_on = round - s.danger_r <= P_DANGER_T;
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;
        bool held = s.hold_group[i];
        if (!held && danger_on && dist(g.center, s.danger_p) <= P_DANGER_R) continue;""")

rep("""        int claimers = count_claimers(s, sm, i);
        if (PR.dpsfarm && !i_am_tank(s))
            for (int k = 0; k < claim_slots(s); ++k)
                if (k != s.ally_idx && ((tank_bits(s) >> k) & 1) && claim_value(s, sm, k) == i + 1) --claimers;""",
"""        int claimers = claimers_of[i] - tank_claims_of[i];  // fuelfit o45 (B): counted once above""")

rep("""        double cycle = 8.0 + (P_PATHD && g.spawn_pd >= 0 ? g.spawn_pd : dist(s.spawn_center, g.center));  // recall + heal + walk back""",
"""        double cycle = gc[i].cycle;  // recall + heal + walk back (fuelfit o45: per game)""")

rep("""        if (dist(g.center, s.en_center) < 8) score *= 0.6;    // stay off their doorstep
        if (dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6) score *= P_HALF / 100.0;""",
"""        if (gc[i].near_en) score *= 0.6;    // stay off their doorstep
        if (gc[i].half) score *= P_HALF / 100.0;""")
open(p,'w',newline='').write(s)
print("o45 ok")

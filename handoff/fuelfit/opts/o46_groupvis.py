# (re-anchored on b3: o31 near_camps keeps the camp list in gcs)
# fuelfit o46 (farm section, "groups" + camps lookups): refresh_groups and near_camps test tile visibility on ONE
# exported copy of the vision board instead of bitboard.is_set (47 fuel) per tile.
#   refresh_groups: for every group, `any tile of the group visible` scanned all tiles of every invisible group
#   (12-46 groups x 4-8 tiles = 100-300 imports every turn, 2.7k mean). Now: s.vis exported once (190, packed bits
#   LSB-first, index y*w+x, verified) and the groups' tile indices computed once per game (groups fixed after init).
#   near_camps: the engine's effective-vision board `tv` is exported once instead of one is_set per camp spawn tile.
# Exact: the same bits are read after the board was written (s.vis is assigned once per turn before refresh_groups;
# tv is filled in near_camps itself); `any` over the same tiles is order-independent. Static buffers (fuel is instruction
# metering: no per-call allocation). Uses BitSnap from o42 (apply after it). No fuel_ok, fixed bounds, no new output.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    bc::bitboard rg_tv{ bc::uninitialized };
    bool rg_tv_ok = false;
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (!g.obj) continue;
        bool visible = false;
        for (auto t : g.tiles)
            if (s.vis.is_set(t)) { visible = true; break; }
        if (!visible) continue;""","""    bc::bitboard rg_tv{ bc::uninitialized };
    bool rg_tv_ok = false;
    // fuelfit o46: one export of our vision board and the groups' tile indices (computed once) replace is_set per tile
    static BitSnap vis_s;
    static std::vector<std::vector<int>> gtiles;
    if (gtiles.size() != s.groups.size()) {
        const int w = bc::map::width();
        gtiles.assign(s.groups.size(), {});
        for (std::size_t i = 0; i < s.groups.size(); ++i)
            for (auto t : s.groups[i].tiles) gtiles[i].push_back(t.y * w + t.x);
    }
    if (!attempt([&] { vis_s.load(s.vis); return true; })) return;
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (!g.obj) continue;
        bool visible = false;
        for (int k : gtiles[i])
            if ((vis_s.b[k >> 3] >> (k & 7)) & 1) { visible = true; break; }
        if (!visible) continue;""")
rep("""    bc::bitboard tv;  // the engine's own "effective vision", the one state() checks
    if (!attempt([&] { bc::vision::visible_tiles_into(tv); return true; })) return out;
    for (auto& g : s.groups) {
        if (!g.obj || dist(g.center, pos) > P_LEAN_RADIUS) continue;
        bool seen = false;  // the engine refuses group queries when no camp spawn tile is in vision
        auto gcs = g.obj->camps();  // fuelfit o21: one list per group, reused for the push below
        for (auto& c : gcs)
            if (tv.is_set(c.spawn_position())) { seen = true; break; }
        if (!seen) continue;""","""    bc::bitboard tv;  // the engine's own "effective vision", the one state() checks
    if (!attempt([&] { bc::vision::visible_tiles_into(tv); return true; })) return out;
    static BitSnap tv_s;  // fuelfit o46: one export instead of is_set per camp spawn tile
    if (!attempt([&] { tv_s.load(tv); return true; })) return out;
    for (auto& g : s.groups) {
        if (!g.obj || dist(g.center, pos) > P_LEAN_RADIUS) continue;
        bool seen = false;  // the engine refuses group queries when no camp spawn tile is in vision
        auto gcs = g.obj->camps();  // fuelfit o21: one list per group, reused for the push below
        for (auto& c : gcs)
            if (tv_s.is_set(c.spawn_position())) { seen = true; break; }
        if (!seen) continue;""")
open(p,'w',newline='').write(s)
print("o46 ok")

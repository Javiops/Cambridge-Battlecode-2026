# o56_islecache.py SRCDIR (fuelfit, farm thread; EXACT, after o55). isle_escape off the mainland cost 66k mean (max 93k)
# on the 12 far games profiled: the goal field (exhaustive, 26-30k on 100x100) plus a C++ loop over up to 80 pocket
# tiles x 24 landings x a wall check (~30k) plus exports. The pocket (static component of our tile) is the same island
# every time, so its landing candidates (static filters: bounds, static block, mainland, no wall between) are built
# once per island and kept with the pocket; later calls walk the list in the same order (ties identical) and only
# read the dynamic parts (refused landings, the two fields). The pocket field (cheap) is computed before the goal
# field so an island over P_ISLE_MAX tiles returns before paying the exhaustive search (no side effects skipped).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    bc::bitboard reach, pocket;
    bc::distance_field gf, pf;
    bool ok = attempt([&] {
        bc::bitboard b2 = s.static_block, roots;
        b2.set(pos, false);
        bc::bitboard dest;
        dest.set(pos);
        gf.compute_to(b2, goals & ~s.static_block, dest, reach);
        roots.set(pos);
        pf.compute(b2, roots, pocket);
        return true;
    });
    if (!ok) return false;
    auto tiles = pocket.positions();  // kept: its order decides ties below
    if (tiles.size() > P_ISLE_MAX) return false;
    std::optional<vec2> from, to;
    int bestd = 1 << 30;
    // fuelfit o42: up to P_ISLE_MAX x 24 tiles x ~8 imports (190k fuel on ambush) -> 4 bitboard + 2 field exports.
    // walls, static_block and mainland never change in a game; g_isle_bad, reach, pf, gf are read after their last write.
    static BitSnap walls_s, sblock_s, mainland_s;
    static bool statics_ok = false;
    if (!statics_ok) {
        walls_s.load(bc::map::walls());
        sblock_s.load(s.static_block);
        mainland_s.load(mainland);
        statics_ok = true;
    }
    static BitSnap bad_s, reach_s;
    static DistSnap pf_s, gf_s;
    bad_s.load(g_isle_bad);
    reach_s.load(reach);
    pf_s.load(pf);
    gf_s.load(gf);
    for (auto p : tiles)
        for (int dx = -2; dx <= 2; ++dx)
            for (int dy = -2; dy <= 2; ++dy) {
                vec2 q = p + vec2(dx, dy);
                if ((!dx && !dy) || !bc::map::is_in_bounds(q) || sblock_s.is_set(q) || !mainland_s.is_set(q) || bad_s.is_set(q)) continue;
                bool wall_between = false;  // a dash goes over holes, not walls (ambush: 20 refused dashes through the room's wall)
                for (int ix = std::min(0, dx); ix <= std::max(0, dx); ++ix)
                    for (int iy = std::min(0, dy); iy <= std::max(0, dy); ++iy)
                        if ((ix || iy) && (ix != dx || iy != dy) && walls_s.is_set(p + vec2(ix, iy))) wall_between = true;
                if (wall_between) continue;
                int d = 2 * pf_s.get(p) + (reach_s.is_set(q) ? gf_s.get(q) : 1000);
                if (d < bestd) { bestd = d; from = p; to = q; }
            }
""","""    bc::bitboard reach, pocket;
    bc::distance_field gf, pf;
    bc::bitboard b2 = s.static_block;
    b2.set(pos, false);
    bool ok = attempt([&] {
        bc::bitboard roots;
        roots.set(pos);
        pf.compute(b2, roots, pocket);
        return true;
    });
    if (!ok) return false;
    // fuelfit o56: the island we stand on and its landing candidates (static filters), built once per island
    struct IsleIsland { bc::bitboard pocket; std::size_t ntiles; std::vector<std::pair<vec2, vec2>> cands; };
    static std::vector<IsleIsland> isles;
    IsleIsland* isl = nullptr;
    for (auto& it : isles)
        if (it.pocket.is_set(pos)) { isl = &it; break; }
    // fuelfit o42: up to P_ISLE_MAX x 24 tiles x ~8 imports (190k fuel on ambush) -> 4 bitboard + 2 field exports.
    // walls, static_block and mainland never change in a game; g_isle_bad, reach, pf, gf are read after their last write.
    static BitSnap walls_s, sblock_s, mainland_s;
    static bool statics_ok = false;
    if (!isl) {
        auto tiles = pocket.positions();  // kept: its order decides ties below
        isles.push_back(IsleIsland{pocket, tiles.size(), {}});
        isl = &isles.back();
        if (tiles.size() <= P_ISLE_MAX) {
            if (!statics_ok) {
                walls_s.load(bc::map::walls());
                sblock_s.load(s.static_block);
                mainland_s.load(mainland);
                statics_ok = true;
            }
            for (auto p : tiles)
                for (int dx = -2; dx <= 2; ++dx)
                    for (int dy = -2; dy <= 2; ++dy) {
                        vec2 q = p + vec2(dx, dy);
                        if ((!dx && !dy) || !bc::map::is_in_bounds(q) || sblock_s.is_set(q) || !mainland_s.is_set(q)) continue;
                        bool wall_between = false;  // a dash goes over holes, not walls (ambush: 20 refused dashes through the room's wall)
                        for (int ix = std::min(0, dx); ix <= std::max(0, dx); ++ix)
                            for (int iy = std::min(0, dy); iy <= std::max(0, dy); ++iy)
                                if ((ix || iy) && (ix != dx || iy != dy) && walls_s.is_set(p + vec2(ix, iy))) wall_between = true;
                        if (wall_between) continue;
                        isl->cands.push_back({p, q});
                    }
        }
    }
    if (isl->ntiles > P_ISLE_MAX) return false;
    ok = attempt([&] {
        bc::bitboard dest;
        dest.set(pos);
        gf.compute_to(b2, goals & ~s.static_block, dest, reach);
        return true;
    });
    if (!ok) return false;
    std::optional<vec2> from, to;
    int bestd = 1 << 30;
    static BitSnap bad_s, reach_s;
    static DistSnap pf_s, gf_s;
    bad_s.load(g_isle_bad);
    reach_s.load(reach);
    pf_s.load(pf);
    gf_s.load(gf);
    for (const auto& [p, q] : isl->cands) {
        if (bad_s.is_set(q)) continue;
        int d = 2 * pf_s.get(p) + (reach_s.is_set(q) ? gf_s.get(q) : 1000);
        if (d < bestd) { bestd = d; from = p; to = q; }
    }
""")
open(p,'w',newline='').write(s); print('o56 ok')

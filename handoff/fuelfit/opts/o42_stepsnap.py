# fuelfit o42 (farm section): step_towards, mp_dash_hole_step and isle_escape read their tile scans from row-major
# snapshots instead of one SDK import per tile.
#   bitboard::export_linear_buffer  -> packed bits, LSB-first, index y*w+x   (~190 fuel; is_set is ~47 PER TILE)
#   distance_field::export_linear_buffer -> one uint16 per tile, row-major   (~460 fuel on 41x41 .. ~2500 on 100x100;
#                                                                            get is ~41 PER TILE)
# Both exports were checked tile by tile against is_set/get on big_world (0 mismatches of 10000, bench a1b).
# Exact because: every snapshot is taken after the last write to the field it copies and before the reads it serves;
# the loops keep their order, bounds, in-bounds checks and strict '<' tie-breaking, so the chosen tile is the same;
# isle_escape still iterates pocket.positions() (its order is not row-major and decides ties).
# Snapshots are taken lazily (only when a scan actually runs), so a turn that never scans costs nothing extra.
# Fuel is instruction metering (a 10k-iteration C++ loop costs fuel too, see RESULTS bench b5), so every snapshot
# buffer is a function-level static: allocated and zero-filled once per game, then only overwritten by the export.
# Static maps (walls, static_block, mainland) are exported once per game. No fuel_ok, fixed bounds, no new output.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)

# --- helpers, placed before isle_continue (the first user) ---
rep("""#include "mapplan_game.h"
""","""// fuelfit o42: row-major snapshots of a bitboard / distance field, one SDK export instead of one import per tile.
// Callers check bc::map::is_in_bounds first, exactly as the original code did before is_set/get.
struct BitSnap {
    std::vector<std::uint8_t> b;
    int w = 0;
    void load(const bc::bitboard& bb) {
        w = bc::map::width();
        b.resize(bc::bitboard::linear_buffer_size());
        bb.export_linear_buffer(std::span<std::uint8_t>(b.data(), b.size()));
    }
    bool is_set(vec2 p) const { const int k = p.y * w + p.x; return (b[k >> 3] >> (k & 7)) & 1; }
};
struct DistSnap {
    std::vector<std::uint16_t> d;
    int w = 0;
    void load(const bc::distance_field& df) {
        w = bc::map::width();
        d.resize(bc::distance_field::linear_buffer_size() / sizeof(std::uint16_t));
        df.export_linear_buffer(std::span<std::uint16_t>(d.data(), d.size()));
    }
    int get(vec2 p) const { return d[p.y * w + p.x]; }
};
#include "mapplan_game.h"
""")

# --- isle_escape: static maps once per game, per-call fields once per call ---
rep("""    auto tiles = pocket.positions();
    if (tiles.size() > P_ISLE_MAX) return false;
    std::optional<vec2> from, to;
    int bestd = 1 << 30;
    const bc::bitboard walls = bc::map::walls();
    for (auto p : tiles)
        for (int dx = -2; dx <= 2; ++dx)
            for (int dy = -2; dy <= 2; ++dy) {
                vec2 q = p + vec2(dx, dy);
                if ((!dx && !dy) || !bc::map::is_in_bounds(q) || s.static_block.is_set(q) || !mainland.is_set(q) || g_isle_bad.is_set(q)) continue;
                bool wall_between = false;  // a dash goes over holes, not walls (ambush: 20 refused dashes through the room's wall)
                for (int ix = std::min(0, dx); ix <= std::max(0, dx); ++ix)
                    for (int iy = std::min(0, dy); iy <= std::max(0, dy); ++iy)
                        if ((ix || iy) && (ix != dx || iy != dy) && walls.is_set(p + vec2(ix, iy))) wall_between = true;
                if (wall_between) continue;
                int d = 2 * pf.get(p) + (reach.is_set(q) ? static_cast<int>(gf.get(q)) : 1000);
                if (d < bestd) { bestd = d; from = p; to = q; }
            }""","""    auto tiles = pocket.positions();  // kept: its order decides ties below
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
            }""")

# --- step_towards: no vblock copy unless the volley ring writes to it; lazy snapshots for the three scans ---
rep("""    bc::bitboard vblock = s.blocked;  // P_VOLLEY: blocked plus lethal tiles
    bool vol_on = false;""","""    bc::bitboard vblock_own;  // fuelfit o42: P_VOLLEY ring; copied from s.blocked only when a lethal tile is added
    const bc::bitboard* vblock_p = &s.blocked;
    bool vol_on = false;""")
rep("""                    if ((dx || dy) && bc::map::is_in_bounds(t) && !s.blocked.is_set(t) && danger_at(s.thr, t) >= lim) {
                        vblock.set(t);
                        vol_on = true;
                    }
                }
        }
    }
""","""                    if ((dx || dy) && bc::map::is_in_bounds(t) && !s.blocked.is_set(t) && danger_at(s.thr, t) >= lim) {
                        if (!vol_on) { vblock_own = s.blocked; vblock_p = &vblock_own; }
                        vblock_own.set(t);
                        vol_on = true;
                    }
                }
        }
    }
    const bc::bitboard& vblock = *vblock_p;
    // fuelfit o42: s.blocked / s.visited / s.df snapshots for the tpc, dash and stuck scans, taken on first use
    // (after the compute_to that fills s.df and s.visited; nothing below writes to any of the three).
    static BitSnap blk_s, vis_s;
    static DistSnap df_s;
    bool snap_ok = false;
    auto snap = [&] {
        if (snap_ok) return;
        blk_s.load(s.blocked);
        vis_s.load(s.visited);
        df_s.load(s.df);
        snap_ok = true;
    };
""")
rep("""            std::optional<vec2> best;
            int bestd = here - P_TPC_GAIN - 3;
            for (int dx = -3; dx <= 3; ++dx)
                for (int dy = -3; dy <= 3; ++dy) {
                    if (dx * dx + dy * dy > 9) continue;
                    vec2 q = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(q) || s.blocked.is_set(q) || !s.visited.is_set(q)) continue;
                    int d = s.df.get(q);
                    if (d < bestd) { bestd = d; best = q; }
                }""","""            std::optional<vec2> best;
            int bestd = here - P_TPC_GAIN - 3;
            snap();
            for (int dx = -3; dx <= 3; ++dx)
                for (int dy = -3; dy <= 3; ++dy) {
                    if (dx * dx + dy * dy > 9) continue;
                    vec2 q = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(q) || blk_s.is_set(q) || !vis_s.is_set(q)) continue;
                    int d = df_s.get(q);
                    if (d < bestd) { bestd = d; best = q; }
                }""")
rep("""        if (here >= 3 && ab.is_ready()) {
            std::optional<vec2> best;
            int bestd = here - 1;  // only dash if it beats a plain step
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    int d = s.df.get(t);
                    if (d < bestd) { bestd = d; best = t; }
                }""","""        if (here >= 3 && ab.is_ready()) {
            std::optional<vec2> best;
            int bestd = here - 1;  // only dash if it beats a plain step
            snap();
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || blk_s.is_set(t) || !vis_s.is_set(t)) continue;
                    int d = df_s.get(t);
                    if (d < bestd) { bestd = d; best = t; }
                }""")
rep("""        if (!moved && me.can_move()) {  // still stuck: any free tile that is not farther
            int here = s.df.get(pos);
            for (int dx = -1; dx <= 1 && !moved; ++dx)
                for (int dy = -1; dy <= 1 && !moved; ++dy) {
                    if (!dx && !dy) continue;
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    if (s.df.get(t) > here + 1) continue;
                    moved = attempt([&] { return me.move_absolute(t); });
                }""","""        if (!moved && me.can_move()) {  // still stuck: any free tile that is not farther
            // fuelfit o42: 8 tiles only; the snapshot is used when a scan above already paid for it, else the imports
            int here = snap_ok ? df_s.get(pos) : static_cast<int>(s.df.get(pos));
            for (int dx = -1; dx <= 1 && !moved; ++dx)
                for (int dy = -1; dy <= 1 && !moved; ++dy) {
                    if (!dx && !dy) continue;
                    vec2 t = pos + vec2(dx, dy);
                    if (snap_ok) {
                        if (!bc::map::is_in_bounds(t) || blk_s.is_set(t) || !vis_s.is_set(t)) continue;
                        if (df_s.get(t) > here + 1) continue;
                    } else {
                        if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                        if (s.df.get(t) > here + 1) continue;
                    }
                    moved = attempt([&] { return me.move_absolute(t); });
                }""")
open(p,'w',newline='').write(s)

# --- mapplan_game.h: mp_dash_hole_step's 5x5 ring + 3x3 hole check from snapshots ---
p=d+'/mapplan_game.h'; s=open(p,newline='').read()
rep("""    if (cd <= 0 && me.can_cast()) {  // dash across a hole tile next to us toward the goal
        std::optional<vec2> best;
        int bestd = hh - 1;
        for (int dx = -2; dx <= 2; ++dx)
            for (int dy = -2; dy <= 2; ++dy) {
                if (std::max(std::abs(dx), std::abs(dy)) < 2) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.mp_hvis.is_set(t)) continue;
                int d = s.mp_hdf.get(t);
                if (d >= bestd) continue;
                bool over = false;  // a crossable hole on a tile adjacent to both ends
                for (int mx = -1; mx <= 1 && !over; ++mx)
                    for (int my = -1; my <= 1 && !over; ++my) {
                        vec2 m = pos + vec2(mx, my);
                        if (std::max(std::abs(m.x - t.x), std::abs(m.y - t.y)) <= 1 && bc::map::is_in_bounds(m) && s.mp_dashholes.is_set(m)) over = true;
                    }""","""    if (cd <= 0 && me.can_cast()) {  // dash across a hole tile next to us toward the goal
        std::optional<vec2> best;
        int bestd = hh - 1;
        // fuelfit o42: 16 ring tiles x 3 imports + 9 hole tests each -> 2 bitboard exports + 1 field export per call;
        // s.mp_dashholes only grows inside mp_find_dashholes, one hole per s.dh_next step: re-exported when that moved.
        static BitSnap holes_s;
        static long holes_key = -1;
        const long key = static_cast<long>(s.dh_stage) * 1000000 + static_cast<long>(s.dh_next);
        if (holes_key != key) { holes_s.load(s.mp_dashholes); holes_key = key; }
        static BitSnap blk_s, hvis_s;
        static DistSnap hdf_s;
        blk_s.load(s.blocked);
        hvis_s.load(s.mp_hvis);
        hdf_s.load(s.mp_hdf);
        for (int dx = -2; dx <= 2; ++dx)
            for (int dy = -2; dy <= 2; ++dy) {
                if (std::max(std::abs(dx), std::abs(dy)) < 2) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || blk_s.is_set(t) || !hvis_s.is_set(t)) continue;
                int d = hdf_s.get(t);
                if (d >= bestd) continue;
                bool over = false;  // a crossable hole on a tile adjacent to both ends
                for (int mx = -1; mx <= 1 && !over; ++mx)
                    for (int my = -1; my <= 1 && !over; ++my) {
                        vec2 m = pos + vec2(mx, my);
                        if (std::max(std::abs(m.x - t.x), std::abs(m.y - t.y)) <= 1 && bc::map::is_in_bounds(m) && holes_s.is_set(m)) over = true;
                    }""")
open(p,'w',newline='').write(s)
print("o42 ok")

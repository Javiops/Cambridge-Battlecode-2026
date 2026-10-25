# o65_fieldreuse.py SRCDIR (fuelfit, farm thread; EXACT; over b15 + o59 + o63 + o64). step_towards computes the goal's
# walking field (roots = goal tiles, walls = s.blocked, search stopped at our tile) every turn of every champion, and
# mp_dash_hole_step a second one with the crossable holes open for dash champions: 14-17k and 14-20k per turn on ambush,
# 13-16k each on starvation, 6-8k on big_world (profile of e64; the two are ~60% of a walking turn on 100x100 maps).
# Both fields are kept, with the roots and walls they were computed with, and reused when the reads are provably the same:
#   A search stopped at our tile (distance D) holds the exact distance of every tile within D and reaches all of them.
#   With today's walls, the reads stay exact when (a) every tile that became a wall has cached distance >= D (it is on
#   no shortest path of a tile within D), and (b) every tile that stopped being a wall has all its neighbours at cached
#   distance >= D - 1 (a shorter route through a freed tile u reaches the tile before u at distance <= D - 3). Then every
#   tile within D keeps its distance and reach, and no tile beyond D comes within D - 1. The roots must be the same.
# The reads of step_towards are: our distance, tiles within 2-3 of us at distance < D - 1 (dash and crystal scans), the
# neighbours at D - 1 (next_moves_from), and whether the search reached us: all within D. The one read that depends on
# where the search stopped (the stuck scan: neighbours at D + 1, reached or not) gets a fresh search first.
# mp_dash_hole_step reads the same things of its own field, plus "reached within here - 4": the cached distance tells.
# Cost: one reached test + one get for our tile, a roots compare, and for the tiles that changed between the two wall
# sets (visible champions that moved, monsters that moved or died: 1-3 per turn) one get each, 8 for a freed tile: about
# 1-2.5k. Not tried when the cached distance is below P_FR_MIN (short searches cost less than the test).
# Measured over the 56 far games (x65n): the static rule holds on 63-80% of walking searches (hole field 61-77%) with
# 0 mismatches in 240k checks; the rule here also keeps a cache when a unit that stands still is nearer than us.
# No fuel read, no init work, no idle-round work, no new printf.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)

# --- State: the kept walking field and the roots/walls of both fields
rep("""    bc::distance_field mp_hdf;
    int mp_bank_d = -1, mp_home_d = -1, mp_last_g = -1, mp_last_r = -1000;""","""    bc::distance_field mp_hdf;
    bc::bitboard hf_roots, hf_walls;  // fuelfit o65: what mp_hdf / mp_hvis were computed with (reuse rule: field_reuse)
    bool hf_valid = false;
    bc::distance_field wf_df;  // fuelfit o65: step_towards' goal field, kept between turns with its roots and walls
    bc::bitboard wf_vis, wf_roots, wf_walls;
    bool wf_valid = false;
    int mp_bank_d = -1, mp_home_d = -1, mp_last_g = -1, mp_last_r = -1000;""")

# --- the rule (before mapplan_game.h, which uses it)
rep("""struct DistSnap {
    std::unique_ptr<std::uint16_t[]> d;""","""// fuelfit o65: a field computed by compute_to with (roots_c, walls_c), stopped at a destination at distance Dc, holds the
// exact distance of every tile within Dc and marks it reached (a layered search discovers all of layer k before any of
// k + 1). For a new search with the same roots and walls `walls`, stopped at `pos` (cached distance D <= Dc), every read
// within D is the same when: (a) each tile that became a wall has cached distance >= D (or is not reached: then >= Dc),
// so it lies on no shortest path of a tile within D; (b) each tile that stopped being a wall has every neighbour at
// cached distance >= D - 1: a route made shorter by a freed tile u reaches the tile before u at distance <= D - 3.
// With (a) and (b) every tile within D keeps its distance and its reach, and no other tile comes within D - 1.
// Returns D when the cached field can stand in for the new search, else -1 (also when D < dmin: not worth the test).
int field_reuse(const bc::distance_field& df, const bc::bitboard& vis, bool valid, const bc::bitboard& roots_c,
                const bc::bitboard& walls_c, const bc::bitboard& roots, const bc::bitboard& walls, vec2 pos, int dmin) {
    if (!valid || !vis.is_set(pos)) return -1;
    const int dpos = df.get(pos);
    if (dpos < dmin || dpos >= 60000) return -1;
    if (!(roots == roots_c)) return -1;
    for (auto t : (walls & ~walls_c).positions())
        if (vis.is_set(t) && static_cast<int>(df.get(t)) < dpos) return -1;
    for (auto u : (walls_c & ~walls).positions())
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                const vec2 n = u + vec2(dx, dy);
                if (bc::map::is_in_bounds(n) && vis.is_set(n) && static_cast<int>(df.get(n)) < dpos - 1) return -1;
            }
    return dpos;
}
struct DistSnap {
    std::unique_ptr<std::uint16_t[]> d;""")

# --- mp_dash_hole_step: reads the caller's field; its own field is kept and reused
rep("""int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos);""",
    """int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos,
                      const bc::distance_field& df, const bc::bitboard& vis);  // fuelfit o65: the caller's goal field""")
rep("""        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash""",
    """        int r = mp_dash_hole_step(s, me, goals, vblock, pos, *dfp, *visp);  // mapplan_game.h rule 5: plan across holes we can dash""")

# --- step_towards: the goal field lives in s.wf_*; reuse when the rule holds; s.df/s.visited stay for the other searches
rep("""    if (!ok_field && !sep)
        ok_field = attempt([&] {
            s.df.compute_to(vblock, goals, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    if (!ok_field && vol_on) return false;  // every way runs through a ready volley: wait
    if (!ok_field && !sep) {  // corridor jammed by champions: plan through them
        ok_field = attempt([&] {""","""    if (!ok_field && !sep) {
        if (field_reuse(s.wf_df, s.wf_vis, s.wf_valid, s.wf_roots, s.wf_walls, goals, vblock, pos, P_FR_MIN) >= 0) {
            ok_field = true;  // fuelfit o65: the kept field answers every read of this turn
            from_cache = true;
        } else {
            s.wf_valid = false;
            ok_field = attempt([&] {
                s.wf_df.compute_to(vblock, goals, s.dest, s.wf_vis);
                s.wf_roots = goals;
                s.wf_walls = vblock;
                s.wf_valid = true;
                return s.wf_vis.is_set(pos);
            });
        }
    }
    if (!ok_field && vol_on) return false;  // every way runs through a ready volley: wait
    if (!ok_field && !sep) {  // corridor jammed by champions: plan through them
        dfp = &s.df;
        visp = &s.visited;
        ok_field = attempt([&] {""")
rep("""    auto snap = [&] {
        if (snap_ok) return;
        blk_s.load(s.blocked);
        vis_s.load(s.visited);
        df_s.load(s.df);
        snap_ok = true;
    };""","""    auto snap = [&] {
        if (snap_ok) return;
        blk_s.load(s.blocked);
        vis_s.load(*visp);
        df_s.load(*dfp);
        snap_ok = true;
    };""")
rep("""    // fuelfit o42: s.blocked / s.visited / s.df snapshots for the tpc, dash and stuck scans, taken on first use
    // (after the compute_to that fills s.df and s.visited; nothing below writes to any of the three).
    static BitSnap blk_s, vis_s;""","""    // fuelfit o65: the field the reads below use: the kept goal field (reused or recomputed), or s.df after a search
    // through the jam. from_cache: no search this turn, so the stuck scan (reach at here + 1) must run one first.
    const bc::distance_field* dfp = &s.wf_df;
    const bc::bitboard* visp = &s.wf_vis;
    bool from_cache = false;
    // fuelfit o42: s.blocked / s.visited / s.df snapshots for the tpc, dash and stuck scans, taken on first use
    // (after the compute_to that fills s.df and s.visited; nothing below writes to any of the three).
    static BitSnap blk_s, vis_s;""")
rep("""    if (tpc_try) {
        int here = s.df.get(pos);""","""    if (tpc_try) {
        int here = dfp->get(pos);""")
rep("""        auto ab = me.abilities()[s.dash_slot];
        int here = s.df.get(pos);
        if (here >= 3 && ab.is_ready()) {""","""        auto ab = me.abilities()[s.dash_slot];
        int here = dfp->get(pos);
        if (here >= 3 && ab.is_ready()) {""")
rep("""        attempt([&] {
            steps = s.df.next_moves_from(pos);
            return true;
        });""","""        attempt([&] {
            steps = dfp->next_moves_from(pos);
            return true;
        });""")
rep("""        if (!moved && me.can_move()) {  // still stuck: any free tile that is not farther
            // fuelfit o42: 8 tiles only; the snapshot is used when a scan above already paid for it, else the imports
            int here = snap_ok ? df_s.get(pos) : static_cast<int>(s.df.get(pos));""","""        if (!moved && me.can_move()) {  // still stuck: any free tile that is not farther
            if (from_cache) {  // fuelfit o65: this scan reads the reach at here + 1, which depends on where the search stopped
                s.wf_valid = false;
                if (attempt([&] {
                        s.wf_df.compute_to(vblock, goals, s.dest, s.wf_vis);
                        s.wf_roots = goals;
                        s.wf_walls = vblock;
                        s.wf_valid = true;
                        return true;
                    })) {
                    from_cache = false;
                    snap_ok = false;
                }
            }
            // fuelfit o42: 8 tiles only; the snapshot is used when a scan above already paid for it, else the imports
            int here = snap_ok ? df_s.get(pos) : static_cast<int>(dfp->get(pos));""")
rep("""                    } else {
                        if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                        if (s.df.get(t) > here + 1) continue;
                    }""","""                    } else {
                        if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !visp->is_set(t)) continue;
                        if (dfp->get(t) > here + 1) continue;
                    }""")
open(p,'w',newline='').write(s)

# --- mapplan_game.h: mp_dash_hole_step reads the caller's field and keeps its own
p=d+'/mapplan_game.h'; s=open(p,newline='').read()
rep("""inline int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos) {
    if (!s.visited.is_set(pos)) return 0;
    int here = s.df.get(pos);""","""inline int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos,
                             const bc::distance_field& df, const bc::bitboard& vis) {
    if (!vis.is_set(pos)) return 0;
    int here = df.get(pos);""")
rep("""    bool ok = attempt([&] {
        s.mp_hdf.compute_to(vblock & ~s.mp_dashholes, goals, s.dest, s.mp_hvis, hole_bound);
        return s.mp_hvis.is_set(pos);
    });
    if (!ok) return 0;""","""    // fuelfit o65: the field is kept with its roots and walls; when field_reuse says the reads within our cached distance
    // are the same today, that distance also tells whether a search bounded by hole_bound would reach us.
    const bc::bitboard hwalls = vblock & ~s.mp_dashholes;
    const int cached = field_reuse(s.mp_hdf, s.mp_hvis, s.hf_valid, s.hf_roots, s.hf_walls, goals, hwalls, pos, P_FR_MIN);
    bool ok;
    if (cached >= 0) {
        ok = cached <= static_cast<int>(hole_bound);
    } else {
        s.hf_valid = false;
        ok = attempt([&] {
            s.mp_hdf.compute_to(hwalls, goals, s.dest, s.mp_hvis, hole_bound);
            s.hf_roots = goals;
            s.hf_walls = hwalls;
            s.hf_valid = true;
            return s.mp_hvis.is_set(pos);
        });
    }
    if (!ok) return 0;""")
open(p,'w',newline='').write(s)

# --- params
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_FR_MIN
#define P_FR_MIN 20  // fuelfit o65: a kept goal field is reused only when our cached distance is at least this (the test costs ~1-2.5k)
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)

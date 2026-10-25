# NOT ADOPTED (10-25): exact and working (v6: ring and fixed goals keyed), but it never lands on the heavy turns; see NOTES.md "o65 ... closed".
# o65_fieldreuse.py SRCDIR (fuelfit, farm thread; EXACT; over b15 + o59 + o63 + o64). step_towards computes the goal's
# walking field (roots = goal tiles, walls = s.blocked, search stopped at our tile) every turn of every champion, and
# mp_dash_hole_step a second one with the crossable holes open for dash champions: 14-17k and 14-20k per turn on ambush,
# 13-16k each on starvation, 5-9k on big_world (profile of e64); on 100x100 maps even a 5-tile search costs 3k (the
# engine prices the whole buffer). Both fields are kept and reused when every read is provably the same:
#   A search stopped at our tile (distance D) holds the exact distance of every tile within D and reaches all of them
#   (a layered search discovers all of layer k before any of k + 1). With today's walls and the same roots the reads stay
#   exact when (a) every tile that became a wall has cached distance >= D (it is on no shortest path of a tile within D)
#   and (b) every tile that stopped being a wall has all its neighbours at cached distance >= D - 1 (a shorter route
#   through a freed tile u reaches the tile before u at distance <= D - 3). Then every tile within D keeps its distance
#   and reach, and no tile beyond D comes within D - 1.
#   A bounded search that did not reach its destination (the dash-hole field when no crossing pays) reached every tile
#   within its bound B: with the rule at D = B + 1, a new search bounded by B' <= B would not reach us either.
#   After a check that passed with changed walls, the kept walls become today's: a later check at a distance <= D then
#   covers the earlier changes too (they were verified at D), so the check never grows.
# The reads of step_towards: our distance, tiles within 2-3 of us at distance < D - 1 (dash and crystal scans), the
# neighbours at D - 1 (next_moves_from), whether the search reached us: all within D. The one read that depends on where
# the search stopped (the stuck scan: neighbours at D + 1, reached or not) gets a fresh search first. mp_dash_hole_step
# reads the same of its own field plus "reached within here - 4": the cached distance (or the exhausted bound) tells.
# Nothing is copied. The walls of a kept field are s.blocked of the turn it was computed (or last reused) in: s.blocked
# is now double-buffered (s.blocked_prev holds the previous turn's, by a swap: no cost) with a generation counter, so a
# field kept with generation g is comparable while s.blocked_prev carries g (a volley block, or the mono zone added to
# s.blocked after the search, makes it incomparable: no reuse). The roots are goals_in & ~s.blocked: goals_in must be
# the same object with the same content (a group's spawn mask or our spawn: fixed after init; a ring built on the stack
# is never kept), and no changed tile may lie inside it (a tile inside that became a wall was a root; one that was freed
# is a root now). The roots' bounding box (built once per object) lets changed tiles far from it skip the reads.
# Cost (measured SDK prices on 100x100: get 64, == 222, xor 394, count 215, positions 450 + 45/tile, a search 2.9k +
# ~3.4/tile): a hit with nothing changed in sight is one get and one ==, ~0.3k for both fields; a new target costs
# nothing (object mismatch); a turn with more than P_FR_CHANGED changed tiles in sight costs == + xor + count (~0.8k,
# shared by both fields) and searches as before; a pass with changes adds positions() and one get per changed tile
# near the roots (eight for a freed tile, at most P_FR_READS). No reuse below the map's minimum distance (a short
# search costs little) and nothing is kept on the first playing turn (its cost is the stall thread's target).
# Measured over the 56 far games (x65p): the rule holds on 60-72% of the checked walking searches (ambush 72%,
# starvation 61%, big_world 60%) and 63-75% of the hole searches; nothing in sight changed on more than half of them;
# 0 mismatches between the cached and the fresh distance in 240k checks (x65n).
# No fuel read, no init work, no idle-round work, no new printf.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)

# --- State
rep("""struct Foe {
    bc::champion c;""","""// fuelfit o65: what a kept distance field was computed with (its walls are s.blocked of generation `gen`), and what its
// reuse was last argued for (field_reuse).
struct GoalKey {  // fuelfit o65: what the goal mask was built from, so two turns' masks compare without touching a bitboard
    int kind = 0;        // 0 none (not reusable), 1 chebyshev ring of radius r around c (draw_chebyshev), 2 a fixed object (ptr)
    vec2 c{0, 0};
    int r = 0;
    const bc::bitboard* ptr = nullptr;
    bool operator==(const GoalKey& o) const { return kind == o.kind && (kind != 1 || (c == o.c && r == o.r)) && (kind != 2 || ptr == o.ptr); }
};
struct KeptField {
    GoalKey key;  // how the goals_in the roots were taken from was built
    int gen = -1;                       // s.blocked generation of the walls (the search's, or the last check that passed with changes)
    bool exhausted = false;             // the search did not reach its destination: every tile within `bound` is reached
    int bound = 65535;                  // max_distance of that search
    int d_last = 65535;                 // distance the last check with changed walls was argued for: later checks must stay <= it
    bool valid = false;
};
// fuelfit o65: bounding box of a fixed goal mask, built once: a tile's distance from roots inside it is at least its
// Chebyshev distance to the box.
struct GoalBox {
    GoalKey key;
    int x0 = 0, y0 = 0, x1 = -1, y1 = -1;
    void build(const GoalKey& k, const bc::bitboard& g) {
        key = k;
        if (k.kind == 1) { x0 = X(k.c) - k.r; x1 = X(k.c) + k.r; y0 = Y(k.c) - k.r; y1 = Y(k.c) + k.r; return; }
        x0 = y0 = 1 << 20; x1 = y1 = -1;
        for (auto q : g.positions()) { x0 = std::min(x0, X(q)); x1 = std::max(x1, X(q)); y0 = std::min(y0, Y(q)); y1 = std::max(y1, Y(q)); }
    }
    int cheb(vec2 t) const {
        if (x1 < 0) return 0;
        const int dx = X(t) < x0 ? x0 - X(t) : (X(t) > x1 ? X(t) - x1 : 0);
        const int dy = Y(t) < y0 ? y0 - Y(t) : (Y(t) > y1 ? Y(t) - y1 : 0);
        return std::max(dx, dy);
    }
};

struct Foe {
    bc::champion c;""")
rep("""    bc::distance_field mp_hdf;
    int mp_bank_d = -1, mp_home_d = -1, mp_last_g = -1, mp_last_r = -1000;""","""    bc::distance_field mp_hdf;
    KeptField hf_k;  // fuelfit o65: what mp_hdf / mp_hvis were computed with
    bc::distance_field wf_df;  // fuelfit o65: step_towards' goal field, kept between turns
    bc::bitboard wf_vis;
    KeptField wf_k;
    bc::bitboard blocked_prev;  // fuelfit o65: s.blocked of the previous turn (swapped in, not copied) and its generation
    int blocked_gen = 0, blocked_prev_gen = -1;
    GoalBox goal_box;
    GoalKey fr_pending;  // fuelfit o65: set by a caller right before step_towards to say how its goal mask was built
    int mp_bank_d = -1, mp_home_d = -1, mp_last_g = -1, mp_last_r = -1000;""")

# --- s.blocked: double buffer + generation
rep("""    s.blocked = s.static_block | bc::vision::champion_tiles() | bc::vision::camp_tiles();
    s.blocked.set(pos, false);
    attempt([&] {
        s.vis = me.visible_tiles();""","""    s.blocked_prev.swap(s.blocked);  // fuelfit o65: last turn's walls stay readable (see field_reuse)
    s.blocked_prev_gen = s.blocked_gen;
    s.blocked = s.static_block | bc::vision::champion_tiles() | bc::vision::camp_tiles();
    s.blocked.set(pos, false);
    ++s.blocked_gen;
    attempt([&] {
        s.vis = me.visible_tiles();""")
rep("""            s.blocked |= zone;
            s.blocked.set(pos, false);
        }
    }""","""            s.blocked |= zone;
            s.blocked.set(pos, false);
            ++s.blocked_gen;  // fuelfit o65: a field searched before this is not comparable with s.blocked any more
        }
    }""")

# --- the rule (before mapplan_game.h, which uses it)
rep("""struct DistSnap {
    std::unique_ptr<std::uint16_t[]> d;""","""// fuelfit o65. A field computed by compute_to with roots (key & ~walls_c) and walls_c, stopped at a destination at
// distance Dc, holds the exact distance of every tile within Dc and marks it reached (a layered search discovers all of
// layer j before any of j + 1); a search that exhausted its bound B holds every tile within B. For a new search with the
// same key and the walls `walls`, stopped at `pos`, let D be our cached distance (or B + 1 when the exhausted search did
// not reach us): every read within D is the same when (a) each tile that became a wall has cached distance >= D (or is
// not reached: then it is beyond every reached tile), so it lies on no shortest path of a tile within D; (b) each tile
// that stopped being a wall has every neighbour at cached distance >= D - 1: a route made shorter by a freed tile u
// reaches the tile before u at distance <= D - 3; (c) no changed tile lies inside the key (the roots would differ).
// With (a)-(c) every tile within D keeps its distance and its reach, and no other tile comes within D - 1; in the
// exhausted case we are therefore not reached within any bound <= B. A tile the search did not reach reads
// distance_field::unreachable (65535). A tile's distance is at least its Chebyshev distance to the roots' bounding box.
// When the check passes with changed walls, the kept walls become `walls` (k.gen = gen) and k.d_last = D: the changes it
// verified stay verified for any later D' <= D. walls_c is s.blocked_prev, comparable only while k.gen == prev_gen.
// Returns D when the kept field stands in for the new search, -2 when it proves the new search (bounded by bound_now)
// would not reach us, -1 otherwise (also when D < dmin, or the check would cost more than it is worth).
struct WallDiff {  // fuelfit o65: today's walls against last turn's, computed once per step_towards call
    int state = 0;  // 0 not computed, 1 same, 2 too many changes, 3 listed
    std::vector<vec2> tiles;
    void compute(const bc::bitboard& walls, const bc::bitboard& prev) {
        if (state) return;
        if (walls == prev) { state = 1; return; }
        const bc::bitboard changed = walls ^ prev;
        if (static_cast<int>(changed.count()) > P_FR_CHANGED) { state = 2; return; }
        tiles = changed.positions();
        state = 3;
    }
};
int field_reuse(const bc::distance_field& df, KeptField& k, State& s, const GoalKey& gk, const bc::bitboard& goals_in,
                const bc::bitboard& walls, WallDiff& diff, vec2 pos, int dmin, int bound_now) {
    if (!k.valid || !(k.key == gk) || k.gen != s.blocked_prev_gen) return -1;
    int dpos = df.get(pos);
    const bool reached = dpos < 60000;
    if (reached) {
        if (dpos < dmin) return -1;
    } else {
        if (!k.exhausted || bound_now > k.bound || bound_now < dmin) return -1;
        dpos = k.bound + 1;
    }
    if (dpos > k.d_last) return -1;
    diff.compute(walls, s.blocked_prev);
    if (diff.state == 2) return -1;
    if (diff.state == 3) {
        if (!(s.goal_box.key == gk)) s.goal_box.build(gk, goals_in);
        std::array<vec2, 32> freed;
        int nf = 0, reads = 0;
        for (auto t : diff.tiles) {
            if (goals_in.is_set(t)) return -1;  // (c) a root changed
            if (s.goal_box.cheb(t) >= dpos) continue;  // its distance (and its neighbours' + 1) is at least D
            if (walls.is_set(t)) {  // became a wall: read now, the usual reason to fail
                if (++reads > P_FR_READS) return -1;
                if (static_cast<int>(df.get(t)) < dpos) return -1;
            } else {  // stopped being a wall: its neighbours, after the cheap reads
                if (nf == 32) return -1;
                freed[nf++] = t;
            }
        }
        for (int i = 0; i < nf; ++i) {
            if ((reads += 8) > P_FR_READS) return -1;
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    if (!dx && !dy) continue;
                    const vec2 n = freed[i] + vec2(dx, dy);
                    if (bc::map::is_in_bounds(n) && static_cast<int>(df.get(n)) < dpos - 1) return -1;
                }
        }
        k.d_last = dpos;
    }
    k.gen = s.blocked_gen;  // the kept walls are today's s.blocked from here on
    return reached ? dpos : -2;
}
// fuelfit o65: goals_in objects whose content never changes after init (a group's spawn mask, our spawn region); a
// ring built on the stack may come back at the same address with other tiles, so only these are kept.
inline bool fr_fixed_goals(const State& s, const bc::bitboard& goals_in) {
    if (&goals_in == &s.my_spawn) return true;
    for (const auto& g : s.groups)
        if (&g.mask == &goals_in) return true;
    return false;
}
// fuelfit o65: a search on a 100x100 map costs ~3k even when short (the engine prices the whole buffer); on small
// maps a short search costs less than the check.
inline int fr_dmin() { return bc::map::width() * bc::map::height() >= P_FR_BIG_AREA ? P_FR_MIN_BIG : P_FR_MIN; }
struct DistSnap {
    std::unique_ptr<std::uint16_t[]> d;""")

# --- mp_dash_hole_step: reads the caller's field; its own field is kept and reused
rep("""int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos);""",
    """int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos,
                      const bc::distance_field& df, const bc::bitboard& vis, const GoalKey& gk, const bc::bitboard& goals_in,
                      bool keepable, WallDiff& diff);  // fuelfit o65: the caller's goal field and the reuse context""")
rep("""        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash""",
    """        int r = mp_dash_hole_step(s, me, goals, vblock, pos, *dfp, *visp, gk, goals_in, keepable, diff);  // mapplan_game.h rule 5: plan across holes we can dash""")

# --- step_towards: the goal field lives in s.wf_*; reused when the rule holds; s.df/s.visited stay for the other searches
rep("""    // fuelfit o42: s.blocked / s.visited / s.df snapshots for the tpc, dash and stuck scans, taken on first use
    // (after the compute_to that fills s.df and s.visited; nothing below writes to any of the three).
    static BitSnap blk_s, vis_s;""","""    // fuelfit o65: the field the reads below use: the kept goal field (reused or recomputed), or s.df after a search
    // through the jam. from_cache: no search this turn, so the stuck scan (reach at here + 1) must run one first.
    // keepable: the walls are s.blocked and goals_in is a fixed object, so the field can be compared next turn.
    const bc::distance_field* dfp = &s.wf_df;
    const bc::bitboard* visp = &s.wf_vis;
    bool from_cache = false;
    GoalKey gk = s.fr_pending;  // the caller said how goals_in was built (a chebyshev ring: same centre and radius = same mask)
    s.fr_pending = GoalKey{};
    if (gk.kind == 0 && fr_fixed_goals(s, goals_in)) { gk.kind = 2; gk.ptr = &goals_in; }
    const bool keepable = vblock_p == &s.blocked && static_cast<int>(bc::round_number()) != s.play_from && gk.kind != 0;
    WallDiff diff;
    auto wf_search = [&] {  // the goal search into the kept field
        s.wf_k.valid = false;
        bool reached = false, done = false;
        attempt([&] {
            s.wf_df.compute_to(vblock, goals, s.dest, s.wf_vis);
            done = true;
            reached = s.wf_vis.is_set(pos);
            return true;
        });
        if (done && reached && keepable) {
            s.wf_k.key = gk;
            s.wf_k.gen = s.blocked_gen;
            s.wf_k.exhausted = false;
            s.wf_k.bound = 65535;
            s.wf_k.d_last = 65535;
            s.wf_k.valid = true;
        }
        return done && reached;
    };
    // fuelfit o42: s.blocked / s.visited / s.df snapshots for the tpc, dash and stuck scans, taken on first use
    // (after the compute_to that fills s.df and s.visited; nothing below writes to any of the three).
    static BitSnap blk_s, vis_s;""")
rep("""    if (!ok_field && !sep)
        ok_field = attempt([&] {
            s.df.compute_to(vblock, goals, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    if (!ok_field && vol_on) return false;  // every way runs through a ready volley: wait
    if (!ok_field && !sep) {  // corridor jammed by champions: plan through them
        ok_field = attempt([&] {""","""    if (!ok_field && !sep) {
        if (keepable && field_reuse(s.wf_df, s.wf_k, s, gk, goals_in, vblock, diff, pos, fr_dmin(), 65535) >= 0) {
            ok_field = true;  // fuelfit o65: the kept field answers every read of this turn
            from_cache = true;
        } else {
            ok_field = wf_search();
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
            if (from_cache && wf_search()) {  // fuelfit o65: this scan reads the reach at here + 1, which depends on where the search stopped
                from_cache = false;
                snap_ok = false;
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
# --- callers whose goal mask is a pure chebyshev ring: say so (same centre and radius = same mask, compared for free)
rep("""        acted = step_towards(s, me, ring, dash && true) || acted;""","""        s.fr_pending = GoalKey{1, tpos, range, nullptr};  // fuelfit o65
        acted = step_towards(s, me, ring, dash && true) || acted;""")
rep("""        const bool st = step_towards(s, me, ring, true);
        s.cf_stepfail = !st;""","""        s.fr_pending = GoalKey{1, tpos, range, nullptr};  // fuelfit o65
        const bool st = step_towards(s, me, ring, true);
        s.cf_stepfail = !st;""")
rep("""        ring.draw_chebyshev(*a, 1.0f);
        moved = step_towards(s, me, ring, true);""","""        ring.draw_chebyshev(*a, 1.0f);
        s.fr_pending = GoalKey{1, *a, 1, nullptr};  // fuelfit o65
        moved = step_towards(s, me, ring, true);""")
rep("""            ring.draw_chebyshev(lp, 2.0f);
            if (step_towards(s, me, ring, false)) {""","""            ring.draw_chebyshev(lp, 2.0f);
            s.fr_pending = GoalKey{1, lp, 2, nullptr};  // fuelfit o65
            if (step_towards(s, me, ring, false)) {""")
open(p,'w',newline='').write(s)

p=d+'/fight.h'; s=open(p,newline='').read()
rep("""        ring.draw_chebyshev(focus->p, static_cast<float>(range));
        step_towards(s, me, ring, chase);""","""        ring.draw_chebyshev(focus->p, static_cast<float>(range));
        s.fr_pending = GoalKey{1, focus->p, range, nullptr};  // fuelfit o65
        step_towards(s, me, ring, chase);""")
open(p,'w',newline='').write(s)
p=d+'/cassi_issac.h'; s=open(p,newline='').read()
rep("""        ring.draw_chebyshev(goal, 1.0f);
        bool moved = step_towards(s, me, ring, true);""","""        ring.draw_chebyshev(goal, 1.0f);
        s.fr_pending = GoalKey{1, goal, 1, nullptr};  // fuelfit o65
        bool moved = step_towards(s, me, ring, true);""")
rep("""    ring.draw_chebyshev(*partner, 1.0f);
    bool moved = step_towards(s, me, ring, true);""","""    ring.draw_chebyshev(*partner, 1.0f);
    s.fr_pending = GoalKey{1, *partner, 1, nullptr};  // fuelfit o65
    bool moved = step_towards(s, me, ring, true);""")
rep("""            ring.draw_chebyshev(*cp, 2.0f);
            step_towards(s, me, ring, false);""","""            ring.draw_chebyshev(*cp, 2.0f);
            s.fr_pending = GoalKey{1, *cp, 2, nullptr};  // fuelfit o65
            step_towards(s, me, ring, false);""")
open(p,'w',newline='').write(s)

# --- mapplan_game.h: mp_dash_hole_step reads the caller's field and keeps its own
p=d+'/mapplan_game.h'; s=open(p,newline='').read()
rep("""inline int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos) {
    if (!s.visited.is_set(pos)) return 0;
    int here = s.df.get(pos);""","""inline int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos,
                             const bc::distance_field& df, const bc::bitboard& vis, const GoalKey& gk, const bc::bitboard& goals_in,
                             bool keepable, WallDiff& diff) {
    if (!vis.is_set(pos)) return 0;
    int here = df.get(pos);""")
rep("""    bool ok = attempt([&] {
        s.mp_hdf.compute_to(vblock & ~s.mp_dashholes, goals, s.dest, s.mp_hvis, hole_bound);
        return s.mp_hvis.is_set(pos);
    });
    if (!ok) return 0;""","""    // fuelfit o65: the field is kept; field_reuse says when today's reads are the same (its walls differ from the walking
    // field's only by the crossable holes, which never change: the same wall diff serves), and when the kept search,
    // exhausted within its bound, proves that one bounded by hole_bound would not reach us.
    const int cached = keepable ? field_reuse(s.mp_hdf, s.hf_k, s, gk, goals_in, vblock, diff, pos, fr_dmin(), hole_bound) : -1;
    bool ok = false;
    if (cached >= 0) {
        ok = cached <= static_cast<int>(hole_bound);
    } else if (cached == -1) {
        s.hf_k.valid = false;
        bool done = false;
        attempt([&] {
            s.mp_hdf.compute_to(vblock & ~s.mp_dashholes, goals, s.dest, s.mp_hvis, hole_bound);
            done = true;
            ok = s.mp_hvis.is_set(pos);
            return true;
        });
        if (done && keepable) {
            s.hf_k.key = gk;
            s.hf_k.gen = s.blocked_gen;
            s.hf_k.exhausted = !ok;
            s.hf_k.bound = hole_bound;
            s.hf_k.d_last = 65535;
            s.hf_k.valid = true;
        }
    }
    if (!ok) return 0;""")
open(p,'w',newline='').write(s)

# --- params
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_FR_MIN
#define P_FR_MIN 20  // fuelfit o65: a kept goal field is reused only from this distance on small maps (a short search is cheap)
#endif
#ifndef P_FR_MIN_BIG
#define P_FR_MIN_BIG 10  // fuelfit o65: the same on maps of P_FR_BIG_AREA tiles or more, where every search costs 3k+
#endif
#ifndef P_FR_BIG_AREA
#define P_FR_BIG_AREA 4096
#endif
#ifndef P_FR_READS
#define P_FR_READS 12  // fuelfit o65: most distance reads a check may spend on changed wall tiles before giving up
#endif
#ifndef P_FR_CHANGED
#define P_FR_CHANGED 8  // fuelfit o65: more changed wall tiles in sight than this and the kept fields are not tried
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)

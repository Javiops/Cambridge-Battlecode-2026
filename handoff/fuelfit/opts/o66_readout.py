# o66_readout.py SRCDIR (fuelfit, farm thread; EXACT; over b15 + o59 + o63 + o64). Two read paths priced on 100x100 maps:
# (a) choose_target's read-out of the forward field (o41) exports the reached mask and the distances, then tests the
#     reached bit of every group tile before taking its distance: 24-51 groups x ~30 tiles = 700-1500 iterations of
#     bit test + min (8-13k; scope 25). The engine exports 65535 for every tile the search did not reach (beyond the
#     200 bound or cut off), larger than any reached distance, so the min over a group's tiles is 65535 exactly when no
#     tile is reached: the mask export (190) and the bit tests go; the loop is one min() per tile.
# (b) step_towards' dash scan (25 tiles) and tp-crystal scan (29 tiles) load three snapshots first (o42: s.blocked,
#     s.visited, s.df; the field export alone is 2.5k on 100x100, ~460 on 41x41) and then read for free. On maps of
#     4096 tiles or more, 25 direct get() (64 each) cost 1.6k against 2.9k of snapshots: a tile the search did not
#     reach reads 65535 and can never beat bestd, so the reach test is implied, and the wall test is asked only of a
#     tile that would otherwise win (the conditions are pure: same candidates in the same order, same best). Smaller
#     maps keep the snapshots (cheaper there). The stuck scan is unchanged (it uses the snapshot only when a scan above
#     already paid for it).
# No fuel read, no init work, no new printf, fixed bounds.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)

rep("""            static BitSnap vb;
            static DistSnap db;
            vb.load(s.pdv);
            db.load(s.pdf);
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 1 << 20;
                for (int k : gidx[i])
                    if ((vb.b[k >> 3] >> (k & 7)) & 1) b = std::min(b, static_cast<int>(db.d[k]));
                s.pd_gd[i] = b < (1 << 20) ? b : -1;
            }""","""            static DistSnap db;
            db.load(s.pdf);
            // fuelfit o66: the export holds 65535 on every unreached tile (> any reached distance), so the reached mask
            // and its bit test are not needed: one min() per group tile.
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 65535;
                for (int k : gidx[i]) b = std::min(b, static_cast<int>(db.d[k]));
                s.pd_gd[i] = b < 65535 ? b : -1;
            }""")

# helper (before step_towards)
rep("""bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {""","""// fuelfit o66: on maps of 4096 tiles or more a field export costs 2.5k; a 25-tile scan reads directly instead.
inline bool o66_direct_scan() {
    static int big = -1;
    if (big < 0) big = bc::map::width() * bc::map::height() >= 4096 ? 1 : 0;
    return big == 1;
}
bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {""")

rep("""            int bestd = here - P_TPC_GAIN - 3;
            snap();
            for (int dx = -3; dx <= 3; ++dx)
                for (int dy = -3; dy <= 3; ++dy) {
                    if (dx * dx + dy * dy > 9) continue;
                    vec2 q = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(q) || blk_s.is_set(q) || !vis_s.is_set(q)) continue;
                    int d = df_s.get(q);
                    if (d < bestd) { bestd = d; best = q; }
                }""","""            int bestd = here - P_TPC_GAIN - 3;
            if (o66_direct_scan()) {  // fuelfit o66: direct reads; an unreached tile reads 65535 and never wins
                for (int dx = -3; dx <= 3; ++dx)
                    for (int dy = -3; dy <= 3; ++dy) {
                        if (dx * dx + dy * dy > 9) continue;
                        vec2 q = pos + vec2(dx, dy);
                        if (!bc::map::is_in_bounds(q)) continue;
                        int d = s.df.get(q);
                        if (d < bestd && !s.blocked.is_set(q)) { bestd = d; best = q; }
                    }
            } else {
                snap();
                for (int dx = -3; dx <= 3; ++dx)
                    for (int dy = -3; dy <= 3; ++dy) {
                        if (dx * dx + dy * dy > 9) continue;
                        vec2 q = pos + vec2(dx, dy);
                        if (!bc::map::is_in_bounds(q) || blk_s.is_set(q) || !vis_s.is_set(q)) continue;
                        int d = df_s.get(q);
                        if (d < bestd) { bestd = d; best = q; }
                    }
            }""")

rep("""            int bestd = here - 1;  // only dash if it beats a plain step
            snap();
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || blk_s.is_set(t) || !vis_s.is_set(t)) continue;
                    int d = df_s.get(t);
                    if (d < bestd) { bestd = d; best = t; }
                }""","""            int bestd = here - 1;  // only dash if it beats a plain step
            if (o66_direct_scan()) {  // fuelfit o66: direct reads; an unreached tile reads 65535 and never wins
                for (int dx = -2; dx <= 2; ++dx)
                    for (int dy = -2; dy <= 2; ++dy) {
                        vec2 t = pos + vec2(dx, dy);
                        if (!bc::map::is_in_bounds(t)) continue;
                        int d = s.df.get(t);
                        if (d < bestd && !s.blocked.is_set(t)) { bestd = d; best = t; }
                    }
            } else {
                snap();
                for (int dx = -2; dx <= 2; ++dx)
                    for (int dy = -2; dy <= 2; ++dy) {
                        vec2 t = pos + vec2(dx, dy);
                        if (!bc::map::is_in_bounds(t) || blk_s.is_set(t) || !vis_s.is_set(t)) continue;
                        int d = df_s.get(t);
                        if (d < bestd) { bestd = d; best = t; }
                    }
            }""")
open(p,'w',newline='').write(s)

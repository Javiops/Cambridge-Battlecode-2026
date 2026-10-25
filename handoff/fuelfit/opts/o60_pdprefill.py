# (re-anchored on b17: o58 sets the idle budget to 60k)
# o60_pdprefill.py SRCDIR (fuelfit, farm thread; EXACT). The first playing turn on 100x100 maps paid the forward walking
# field from the spawn (26-31k) plus its per-group read-out (3-6k) inside choose_target, on top of everything else
# (ambush r4 131-162k, big_world r5 155-171k with unlimited fuel). The idle round(s) before it (init_wait, o08 v3 / o57)
# have the same position and the same static walls, so the same field and the same pd_gd values are computed there and
# left in the per-position cache (s.pd_pos / s.pd_gd); choose_target finds `cached` true and skips both. The cache is
# keyed by the position, so a champion moved before its first turn simply misses it and pays as before. Order in
# init_wait: the prefill first (priced like one field + 6k), then the reverse fields (o47) with what is left of the 70k.
# The first playing turn is marked as having paid its forward field, so the o54 end-of-turn warm-up skips it (it is the
# heaviest turn of the game on 100x100 maps, not a cheap one).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""void init_wait(State& s) {
    const long price = 1200 + (static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height()) * 5) / 2;
    long left = 60000;  // fuelfit o58: 70k measured 80-83k on road_of_riches
""","""bool farm_pd_prefill(State& s, vec2 pos);  // fuelfit o60, defined with choose_target
void init_wait(State& s) {
    const long price = 1200 + (static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height()) * 5) / 2;
    long left = 60000;  // fuelfit o58: 70k measured 80-83k on road_of_riches
    {  // fuelfit o60: the first playing turn's forward field and group distances, from where we stand now
        const vec2 pos = bc::self().position();
        if (!(s.pd_pos == pos && s.pd_gd.size() == s.groups.size()) && farm_pd_prefill(s, pos)) {
            left -= price + 6000;
            s.pd_fwd_round = s.play_from;  // the first playing turn counts as having paid its field: no o54 warm-up there
        }
    }
""")
# the forward block of choose_target, factored so the prefill runs the very same code
rep("""    have_pd = have_pd || (P_PATHD && !g_nopd && attempt([&] {  // walking distance from here to every camp group
        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pd_fwd_round = round;  // fuelfit o54
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;
    }));
    if (have_pd && !cached) {  // the walking distance to each group, read once per tile
        s.pd_gd.assign(s.groups.size(), -1);
        attempt([&] {
            // fuelfit o41: one export of the reached mask and one of the distances, then plain C++ over the
            // groups' tile indices (fixed after init_groups, computed once) instead of is_set + get per tile.
            farm_warmup_now(s);  // fuelfit o48: shared tile index lists, buffers without zero-fill
            const std::vector<std::vector<int>>& gidx = s.fw_gidx;
            static BitSnap vb;
            static DistSnap db;
            vb.load(s.pdv);
            db.load(s.pdf);
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 1 << 20;
                for (int k : gidx[i])
                    if ((vb.b[k >> 3] >> (k & 7)) & 1) b = std::min(b, static_cast<int>(db.d[k]));
                s.pd_gd[i] = b < (1 << 20) ? b : -1;
            }
            s.pd_pos = pos;
            return true;
        });
    }""","""    if (!cached && P_PATHD && !g_nopd) {  // walking distance from here to every camp group (fuelfit o60: shared code)
        s.pd_fwd_round = round;  // fuelfit o54
        have_pd = farm_pd_forward(s, pos);
        if (have_pd) farm_pd_readout(s, pos);
    }""")
rep("""// fuelfit o54: true when every group has its reverse field (no computing here; see the warm-up in run_game)
inline bool farm_pd_done(State& s) { return s.pd_rf.size() == s.groups.size() && s.pd_rf_done == s.groups.size(); }""",
"""// fuelfit o54: true when every group has its reverse field (no computing here; see the warm-up in run_game)
inline bool farm_pd_done(State& s) { return s.pd_rf.size() == s.groups.size() && s.pd_rf_done == s.groups.size(); }
// fuelfit o60: the forward walking field from pos (as choose_target always computed it) and its per-group read-out
// (o41) into the per-position cache; also run by init_wait on the idle round for the first playing turn.
bool farm_pd_forward(State& s, vec2 pos) {
    return attempt([&] {
        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;
    });
}
void farm_pd_readout(State& s, vec2 pos) {  // the walking distance to each group, read once per tile
    s.pd_gd.assign(s.groups.size(), -1);
    attempt([&] {
        farm_warmup_now(s);  // fuelfit o48: shared tile index lists, buffers without zero-fill
        const std::vector<std::vector<int>>& gidx = s.fw_gidx;
        static BitSnap vb;
        static DistSnap db;
        vb.load(s.pdv);
        db.load(s.pdf);
        for (std::size_t i = 0; i < s.groups.size(); ++i) {
            int b = 1 << 20;
            for (int k : gidx[i])
                if ((vb.b[k >> 3] >> (k & 7)) & 1) b = std::min(b, static_cast<int>(db.d[k]));
            s.pd_gd[i] = b < (1 << 20) ? b : -1;
        }
        s.pd_pos = pos;
        return true;
    });
}
bool farm_pd_prefill(State& s, vec2 pos) {
    if (!P_PATHD || g_nopd || s.static_block.is_set(pos) || s.groups.empty()) return false;
    if (!farm_pd_forward(s, pos)) return false;
    farm_pd_readout(s, pos);
    return true;
}""")
open(p,'w',newline='').write(s); print('o60 ok')

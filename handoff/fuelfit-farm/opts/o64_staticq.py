# o64_staticq.py SRCDIR (fuelfit, farm thread; EXACT by construction, after o54/o55; same.py decides). The first playing
# turn of 100x100 maps paid three static engine fields: the forward farm field (needed for the first decision), the
# recall home field (cr_return_walk's first call, 26-31k on ambush/big_world/starvation) and an altar field (o22/o35 at
# the start of play_turn from round P_BRC_R0, 10-27k). The last two are not needed with no gems. Now:
# - the o54 end-of-turn slot is a fixed queue of static work, one engine field per turn that did not pay the forward
#   field and is not a tribute walk: home field > altar fields > mainland (o55) > reverse group fields (o45);
# - br_static_step leaves the start of play_turn (br_plan keeps both of its paths: cached when ready, else as before);
# - cr_return_walk keeps its lazy compute (same code, factored into cr_home_prepare) as the fallback, and
#   cr_capture_extra asks for the walk only when it can change the answer: cr_optional_value(travel) is false whenever
#   hp >= 90% and gold < 90 whatever the walk (heal_cutoff <= 0.9, gold_cutoff >= 90), which is exactly `old_optional`.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""int cr_return_walk(State& s, vec2 pos, int round) {
    if (!s.cr_home_ready && round >= s.cr_home_retry) {
        s.cr_home_retry = round + 16;
        s.cr_home_ready = attempt([&] {  // fuelfit o34: no fuel_ok(22000)
            bc::bitboard roots = s.my_spawn & ~s.static_block;
            s.cr_home_df.compute(s.static_block, roots, s.cr_home_seen, 200);
            return true;
        });
    }
    if (!s.cr_home_ready || !s.cr_home_seen.is_set(pos)) return -1;""","""// fuelfit o64: the home field, computed by the end-of-turn static queue (or on demand, as before, if asked first)
void cr_home_prepare(State& s, int round) {
    s.cr_home_retry = round + 16;
    s.cr_home_ready = attempt([&] {  // fuelfit o34: no fuel_ok(22000)
        bc::bitboard roots = s.my_spawn & ~s.static_block;
        s.cr_home_df.compute(s.static_block, roots, s.cr_home_seen, 200);
        return true;
    });
}
int cr_return_walk(State& s, vec2 pos, int round) {
    if (!s.cr_home_ready && round >= s.cr_home_retry) cr_home_prepare(s, round);
    if (!s.cr_home_ready || !s.cr_home_seen.is_set(pos)) return -1;""")
rep("""    const int walk = cr_return_walk(s, me.position(), round);
    const bool result = cr_optional_value(hpr, gold, tavi, shop_ok, walk, true);""",
"""    // fuelfit o64: the walk only when it can change the answer (cr_optional_value is false with hp >= 90% and gold < 90
    // whatever the walk: heal_cutoff <= 0.9, gold_cutoff >= 90); the counters below are under the same condition
    const int walk = old_optional ? cr_return_walk(s, me.position(), round) : -1;
    const bool result = cr_optional_value(hpr, gold, tavi, shop_ok, walk, true);""")
rep("""    cf_observe(s, me, round);
    br_static_step(s, round);  // fuelfit o22
""","""    cf_observe(s, me, round);
    // fuelfit o64: br_static_step runs from the end-of-turn static queue (run_game), not here
""")
rep("""        // fuelfit o54: warm-up of the reverse group fields (o45) on the turns that did not pay the forward field and
        // are not a tribute walk: one field per such turn, fixed rule, no fuel read (see o54_pdsched.py).
        if (s.ready && P_PATHD && !g_nopd && s.pd_rf_done < s.groups.size() && std::strncmp(g_mode, "init", 4) != 0 &&
            std::strcmp(g_mode, "tribute") != 0 && s.pd_fwd_round != static_cast<int>(bc::round_number())) {
            if (P_ISLE && !g_mainland_ok) mainland_ready(s);  // fuelfit o55
            else farm_pd_ready(s);
        }""","""        // fuelfit o54/o64: static work queue, one engine field per turn that did not pay the forward field and is not
        // a tribute walk (fixed rule, no fuel read): recall home field, altar fields (o22/o35), mainland (o55), reverse
        // group fields (o45). See o64_staticq.py.
        if (s.ready && std::strncmp(g_mode, "init", 4) != 0 && std::strcmp(g_mode, "tribute") != 0 &&
            s.pd_fwd_round != static_cast<int>(bc::round_number())) {
            const int qround = static_cast<int>(bc::round_number());
            if (!s.cr_home_ready && qround >= s.cr_home_retry) cr_home_prepare(s, qround);
            else if (P_BRCACHE && s.altars.size() <= 64 && qround >= P_BRC_R0 && !br_static_ready(s)) br_static_step(s, qround);
            else if (P_ISLE && !g_mainland_ok) mainland_ready(s);
            else if (P_PATHD && !g_nopd && s.pd_rf_done < s.groups.size()) farm_pd_ready(s);
        }""")
# declarations before run_game: cr_home_prepare and br_static_step/br_static_ready are defined earlier in the file (checked by compile)
open(p,'w',newline='').write(s); print('o64 ok')

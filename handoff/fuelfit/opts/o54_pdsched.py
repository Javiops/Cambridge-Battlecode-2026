# o54_pdsched.py SRCDIR (fuelfit, farm thread; EXACT). On far maps choose_target_impl runs only every few rounds per
# champion, so the per-group reverse fields of o45 (one per call, 26-30k each on 100x100) took 250-500 rounds to warm
# up, and every call in between paid the forward field (26k) AND one reverse field: ct:compute 30-35k from r11 to r300
# (profile of 12 far games). Now choose_target never computes a reverse field: it uses them only once all exist,
# otherwise the forward field as before (same values: o45). The warm-up runs at the end of each playing turn that did
# not pay the forward field and is not a tribute walk (tribute turns already cost ~40k): one field per such turn,
# fixed rule, no fuel read. The idle round of big maps (o47 init_wait) keeps computing them too.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    std::size_t pd_rf_done = 0;             // fuelfit o45: groups whose field is computed (in index order)
""","""    std::size_t pd_rf_done = 0;             // fuelfit o45: groups whose field is computed (in index order)
    int pd_fwd_round = -1;                  // fuelfit o54: round of the last forward field (no warm-up on that turn)
""")
rep("""    return s.pd_rf_done == s.groups.size();
}
int choose_target_impl(State& s, bc::champion& me, int round) {""","""    return s.pd_rf_done == s.groups.size();
}
// fuelfit o54: true when every group has its reverse field (no computing here; see the warm-up in run_game)
inline bool farm_pd_done(State& s) { return s.pd_rf.size() == s.groups.size() && s.pd_rf_done == s.groups.size(); }
int choose_target_impl(State& s, bc::champion& me, int round) {""")
rep("""    if (!cached && P_PATHD && !g_nopd && farm_pd_ready(s) && !s.static_block.is_set(pos)) {""",
    """    if (!cached && P_PATHD && !g_nopd && farm_pd_done(s) && !s.static_block.is_set(pos)) {""")
rep("""        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;""","""        bc::bitboard roots, wall = s.static_block;
        roots.set(pos);
        wall.set(pos, false);
        s.pd_fwd_round = round;  // fuelfit o54
        s.pdf.compute(wall, roots, s.pdv, 200);
        return true;""")
rep("""        log_status(s);
        bc::end_turn();
    }
}""","""        // fuelfit o54: warm-up of the reverse group fields (o45) on the turns that did not pay the forward field and
        // are not a tribute walk: one field per such turn, fixed rule, no fuel read (see o54_pdsched.py).
        if (s.ready && P_PATHD && !g_nopd && s.pd_rf_done < s.groups.size() && std::strncmp(g_mode, "init", 4) != 0 &&
            std::strcmp(g_mode, "tribute") != 0 && s.pd_fwd_round != static_cast<int>(bc::round_number()))
            farm_pd_ready(s);
        log_status(s);
        bc::end_turn();
    }
}""")
if '#include <cstring>' not in s: rep('#include <cstdio>\n','#include <cstdio>\n#include <cstring>\n')
open(p,'w',newline='').write(s); print('o54 ok')

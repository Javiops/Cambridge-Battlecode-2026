# fuelfit o49 (farm section): more once-per-game work into farm_warmup (o48), out of the first playing turn.
# Measured on b7 round-2 turns (integrator): choose_target_impl 20k of its own after the warm-up, farm_pd_ready 12k.
#  (a) share_pow (o05) filled its std::pow table lazily: 303 fuel per pow, up to 18 entries on the first calls.
#      The table is now global and filled by the warm-up (same std::pow calls, same doubles).
#  (b) tank_bits(s) (my_roster + champion names) and the roster handles (bc::champions) were learned on first use.
#  (c) farm_pd_ready's first call resized s.pd_rf / s.pd_rv: N bitboard constructors (251 each, an SDK zero call) plus
#      N distance_field constructors at once = 5k+ with 20 groups, inside the first choose_target. The warm-up allocates
#      them; farm_pd_ready finds them sized (pd_rf_done stays 0, nothing else changes).
#  (d) my_roster returned the vector BY VALUE on every call (a copy of 6 handles each time, also in vcarry_on and the
#      claim/lead code); it returns a const reference now (callers that copy still copy, callers that iterate do not).
# Exact: the same values computed earlier / not copied. No fuel reads, no new output. Over b6 + o48.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""inline std::vector<bc::champion> my_roster(State& s) {
    if (s.roster_my.empty()) s.roster_my = bc::champions(*s.my);
    return s.roster_my;
}""","""inline const std::vector<bc::champion>& my_roster(State& s) {  // fuelfit o49: no copy per call
    if (s.roster_my.empty()) s.roster_my = bc::champions(*s.my);
    return s.roster_my;
}""")
rep("""bool farm_warmup(State& s, int quota) {
    if (s.fw_gidx.size() != s.groups.size()) {
        s.fw_gidx.assign(s.groups.size(), {});
        s.fw_gc.assign(s.groups.size(), FarmGC{});
        s.fw_done = 0;
    }""","""int tank_bits(State& s);  // fuelfit o49 (defined with the farm code)
double g_share_tbl[2][9];  // fuelfit o49: share_pow's table (o05), filled by the warm-up
bool g_share_have[2][9];
bool farm_warmup(State& s, int quota) {
    if (s.fw_gidx.size() != s.groups.size()) {
        s.fw_gidx.assign(s.groups.size(), {});
        s.fw_gc.assign(s.groups.size(), FarmGC{});
        s.fw_done = 0;
        // fuelfit o49: the rest of the once-per-game work that the first choose_target used to pay
        for (int ei = 0; ei < 2; ++ei)
            for (int team = 0; team <= 8; ++team) {
                g_share_tbl[ei][team] = std::pow(static_cast<double>(team), (ei == 0 ? 100 : P_SHAREEXP) / 100.0);
                g_share_have[ei][team] = true;
            }
        attempt([&] { (void)my_roster(s); (void)tank_bits(s); return true; });
        if (s.pd_rf.size() != s.groups.size()) {  // the reverse fields' objects (farm_pd_ready fills them)
            attempt([&] { s.pd_rf.resize(s.groups.size()); s.pd_rv.resize(s.groups.size()); return true; });
            s.pd_rf_done = 0;
        }
    }""")
rep("""    auto share_pow = [](int team, int e100) {  // fuelfit o05: std::pow once per (team, exponent)
        static double tbl[2][9];
        static bool have[2][9];
        const int ei = e100 == 100 ? 0 : 1;
        if (team < 0 || team > 8 || (ei == 1 && e100 != P_SHAREEXP)) return std::pow(static_cast<double>(team), e100 / 100.0);
        if (!have[ei][team]) { tbl[ei][team] = std::pow(static_cast<double>(team), e100 / 100.0); have[ei][team] = true; }
        return tbl[ei][team];
    };""","""    auto share_pow = [](int team, int e100) {  // fuelfit o05: std::pow once per (team, exponent); o49: table from the warm-up
        const int ei = e100 == 100 ? 0 : 1;
        if (team < 0 || team > 8 || (ei == 1 && e100 != P_SHAREEXP)) return std::pow(static_cast<double>(team), e100 / 100.0);
        if (!g_share_have[ei][team]) { g_share_tbl[ei][team] = std::pow(static_cast<double>(team), e100 / 100.0); g_share_have[ei][team] = true; }
        return g_share_tbl[ei][team];
    };""")
open(p,'w',newline='').write(s)
print("o49 ok")

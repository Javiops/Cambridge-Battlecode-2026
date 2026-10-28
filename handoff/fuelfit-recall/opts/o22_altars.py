# fuelfit o22 (recall/altares/campamentos): no fuel reads in the altar and trip code.
# - brcache fields on a fixed schedule: P_BRC_PER altars per turn from round P_BRC_R0 (every champion, alive or
#   dead), never inside br_plan. Before, br_plan built them "while fuel_ok(45000)" on its first call, so the first
#   trip's cost and route depended on the fuel left. All callers need gems > 0, which no champion has before the
#   fields are done (r3 + altars/2), so with unlimited fuel the decisions are the same as a1.
# - br_plan's uncached path (more than 64 altars, or an SDK failure) runs without fuel_ok(50000/22000): one field
#   plus one ring read per altar, bounded by the altar count.
# - br_threat_block / br_safe_move gates (br_policy is 1: dead code), the isle escape (fuel_ok 12000), the monolith
#   step-out (fuel_ok 20000) and the pairfarm walk (fuel_ok 12000) run unconditionally: each is one bounded call.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a,s.count(a)); s=s.replace(a,b)
rep("""    while (g_brs.built < static_cast<int>(s.altars.size()) && fuel_ok(P_BRC_BUILD)) {
        const int i = g_brs.built++;""","""    return g_brs.built >= static_cast<int>(s.altars.size());
}
// fuelfit o22: the fields are built on fixed turns (play_turn), never on demand
void br_static_step(State& s, int round) {
    if (!P_BRCACHE || round < P_BRC_R0 || s.altars.size() > 64) return;
    if (!g_brs.init) {
        g_brs.init = true;
        g_brs.f.resize(s.altars.size());
        g_brs.reached.resize(s.altars.size());
    }
    for (int k = 0; k < P_BRC_PER && g_brs.built < static_cast<int>(s.altars.size()); ++k) {
        const int i = g_brs.built++;""")
rep("""            g_brs.f[i].compute(s.static_block, roots, g_brs.reached[i], 400);
            return true;
        });
    }
    return g_brs.built >= static_cast<int>(s.altars.size());
}""","""            g_brs.f[i].compute(s.static_block, roots, g_brs.reached[i], 400);
            return true;
        });
    }
}""")
rep("""bool br_static_ready(State& s) {
    if (!P_BRCACHE) return false;
    if (!g_brs.init) {
        g_brs.init = true;
        g_brs.f.resize(s.altars.size());
        g_brs.reached.resize(s.altars.size());
    }
""","""bool br_static_ready(State& s) {
    if (!P_BRCACHE || !g_brs.init) return false;
""")
rep("""    if (!fuel_ok(50000) || s.altars.size() > 64) { s.br_reason = 1; return false; }""","""    if (s.altars.size() > 64) { s.br_reason = 1; return false; }""")
rep("""            if (!fuel_ok(22000)) { s.br_reason = 1; return false; }
""","",2)
rep("""        if (!fuel_ok(26000)) return false;
        bool ok = attempt([&] {
            if (!enemy.is_alive()) return true;""","""        bool ok = attempt([&] {
            if (!enemy.is_alive()) return true;""")
rep("""    if (br_policy == 2 && s.br_safe_route && fuel_ok(26000)) {""","""    if (br_policy == 2 && s.br_safe_route) {""")
rep("""    if (!moved && still_n >= P_ISLE_STILL && fuel_ok(12000)) {""","""    if (!moved && still_n >= P_ISLE_STILL) {""")
rep("""            if (zone.is_set(pos) && me.can_move() && fuel_ok(20000)) {""","""            if (zone.is_set(pos) && me.can_move()) {""")
rep("""        me.can_move() && dist(pos, s.groups[s.target].center) >= 4 && fuel_ok(12000)) {
        static int pw_target = -1, pw_n = 0;""","""        me.can_move() && dist(pos, s.groups[s.target].center) >= 4) {
        static int pw_target = -1, pw_n = 0;""")
rep("""    const int round = static_cast<int>(bc::round_number());
    cf_observe(s, me, round);
""","""    const int round = static_cast<int>(bc::round_number());
    cf_observe(s, me, round);
    br_static_step(s, round);  // fuelfit o22
""")
open(p,'w',newline='').write(s)
q=d+'/params.h'; t=open(q,newline='').read()
a="""#ifndef P_BRC_BUILD"""
assert t.count(a)==1
t=t.replace(a,"""#ifndef P_BRC_R0
#define P_BRC_R0 3   // fuelfit o22: first round of the altar-field schedule
#endif
#ifndef P_BRC_PER
#define P_BRC_PER 2  // fuelfit o22: altar fields built per turn
#endif
#ifndef P_BRC_BUILD""")
open(q,'w',newline='').write(t)

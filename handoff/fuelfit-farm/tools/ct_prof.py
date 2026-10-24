# ct_prof.py SRCDIR : sub-scopes inside choose_target_impl and step_towards (profiling only, on top of prof_fp.py)
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    FP_SCOPE(15, "choose_target");
    auto sm = read_sm();
    vec2 pos = me.position();
    double hp = me.health();
    double mhp = std::max(1.0, static_cast<double>(me.max_health()));
    double dps = my_dps(s, me);
""","""    FP_SCOPE(15, "choose_target");
    std::optional<FpScope> fpx; fpx.emplace(28);
    auto sm = read_sm();
    vec2 pos = me.position();
    double hp = me.health();
    double mhp = std::max(1.0, static_cast<double>(me.max_health()));
    double dps = my_dps(s, me);
    fpx.reset(); fpx.emplace(21);
""")
rep("""    std::vector<vec2> pf_claims;
    if (pf_on(round) && s.ally_idx >= 0)""","""    fpx.reset(); fpx.emplace(22);
    std::vector<vec2> pf_claims;
    if (pf_on(round) && s.ally_idx >= 0)""")
rep("""    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();
    bool have_pd =""","""    fpx.reset(); fpx.emplace(23);
    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();
    bool have_pd =""")
rep("""    if (have_pd && !cached) {  // the walking distance to each group, read once per tile""","""    fpx.reset(); fpx.emplace(25);
    if (have_pd && !cached) {  // the walking distance to each group, read once per tile""")
rep("""    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;""","""    fpx.reset(); fpx.emplace(27);
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;""")
# step_towards
rep("""    vec2 pos = me.position();
    bc::bitboard goals = goals_in & ~s.blocked;
    if (goals.is_empty() || goals.is_set(pos)) return false;""","""    std::optional<FpScope> fpy; fpy.emplace(14);
    vec2 pos = me.position();
    bc::bitboard goals = goals_in & ~s.blocked;
    if (goals.is_empty() || goals.is_set(pos)) return false;""")
rep("""    s.dest.clear();
    s.dest.set(pos);
    auto fallback = [&] {""","""    fpy.reset(); fpy.emplace(36);
    s.dest.clear();
    s.dest.set(pos);
    auto fallback = [&] {""")
rep("""    if (!ok_field) return fallback();
""","""    if (!ok_field) return fallback();
    fpy.reset(); fpy.emplace(29);
""")
rep("""        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash""","""        fpy.reset(); fpy.emplace(38);
        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash
        fpy.reset(); fpy.emplace(37);""")
rep("""    bool moved = false;
    if (use_dash && s.dash_slot >= 0 && me.can_cast() && !heart_of_ruin::keeps_dash_for_attacks(s)) {""","""    fpy.reset(); fpy.emplace(37);
    bool moved = false;
    if (use_dash && s.dash_slot >= 0 && me.can_cast() && !heart_of_ruin::keeps_dash_for_attacks(s)) {""")
open(p,'w',newline='').write(s); print("ct_prof ok")

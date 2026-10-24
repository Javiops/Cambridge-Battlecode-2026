# fuelfit o05: lshop_pick's late mix and shard lookups resolved once per champion; ward candidates beyond the first
# P_WARD_TRY never evaluated, so the second positions() is skipped when the dark ones already fill the quota;
# choose_target's std::pow(team, share exponent) from a table (same call, same inputs, computed once).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    std::vector<LateFill> o;
    if (!champ::late_mix(s, o) || o.empty() || o.size() > 4) return base;
    auto find = [&](int k) -> const Shard* {
        for (auto& x : s.shards)
            if (x.stat == o[k].stat && starts_with(x.family, o[k].fam)) return &x;
        return nullptr;
    };""","""    static std::vector<LateFill> o;  // fuelfit o05: the late mix depends on the champion only; resolved once
    static int o_ok = -1;
    static const Shard* o_sh[4] = {nullptr, nullptr, nullptr, nullptr};
    if (o_ok < 0) {
        o_ok = champ::late_mix(s, o) && !o.empty() && o.size() <= 4;
        if (o_ok)
            for (int k = 0; k < static_cast<int>(o.size()); ++k)
                for (auto& x : s.shards)
                    if (x.stat == o[k].stat && starts_with(x.family, o[k].fam)) { o_sh[k] = &x; break; }
    }
    if (!o_ok) return base;
    auto find = [&](int k) -> const Shard* { return o_sh[k]; };""")
rep("""    std::vector<vec2> cand = (place & dark).positions();  // dark bush tiles in reach first, then the rest
    for (auto p : (place & ~dark).positions()) cand.push_back(p);""","""    std::vector<vec2> cand = (place & dark).positions();  // dark bush tiles in reach first, then the rest
    if (static_cast<int>(cand.size()) < P_WARD_TRY)  // fuelfit o05: only the first P_WARD_TRY are ever evaluated
        for (auto p : (place & ~dark).positions()) cand.push_back(p);""")
rep("""    auto walk = [&](const Group& g) {
        int d = dist(pos, g.center);""","""    auto share_pow = [](int team, int e100) {  // fuelfit o05: std::pow once per (team, exponent)
        static double tbl[2][9];
        static bool have[2][9];
        const int ei = e100 == 100 ? 0 : 1;
        if (team < 0 || team > 8 || (ei == 1 && e100 != P_SHAREEXP)) return std::pow(static_cast<double>(team), e100 / 100.0);
        if (!have[ei][team]) { tbl[ei][team] = std::pow(static_cast<double>(team), e100 / 100.0); have[ei][team] = true; }
        return tbl[ei][team];
    };
    auto walk = [&](const Group& g) {
        int d = dist(pos, g.center);""")
rep("std::pow(static_cast<double>(team), ((g.monolith || g.hp < P_STACK_HP || false) ? 100 : P_SHAREEXP) / 100.0)","share_pow(team, (g.monolith || g.hp < P_STACK_HP || false) ? 100 : P_SHAREEXP)")
open(p,'w',newline='').write(s)

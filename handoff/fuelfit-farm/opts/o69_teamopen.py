# o69_teamopen.py SRCDIR (farm thread; NOT EXACT: a decision change, judge by strength; over b29 = b28 + o66 + o67,
# also applies over b15 + o59 + o63 + o64). The top 10 open with the whole team: on 40 top-10 near-map games the first
# capture comes at r22 with 3 champions present (median; 55% of the first three captures have 3+ champions, 17% are
# solo), and the first group is an elk+gem (13/40), wolf+gem (11) or gold cluster (10) group. b29 on the same kind of
# panel (80 near games): first capture r25 with 2 champions, 31% of the first three captures with 3+, 45% solo, and
# the first group is a gold cluster in 47/80 games. From r50 on our elk+gem captures match the top 10; the gap is the
# opening (elk+gem captures by r50: 0.29/game vs 0.62; deaths <= r100 0.65 vs 0.35).
# Rule (teamopen-v1): until round P_TO_R the first alive ally in draft order leads: it values every group for the
# whole team (value not shared, clear time with the roster, no "needs company" discount: the dormant `pack` hook of
# choose_target); the others take the leader's claimed group (x P_GROUP_W, existing ball code) and discount groups
# more than 8 tiles from the leader (x 0.3), re-choosing every 3 rounds like the ball. After P_TO_R the usual choice
# resumes (hysteresis keeps a group under capture). P_TO_NEAR 1 limits it to near maps (spawn-to-spawn path <
# P_PF_MAX). P_TO_OWN 1 (v2): the team valuation applies to own-side groups only; with 0 the leader parked the team on the
# centre group (gemfight 78 gems, packs, gold_rush) and two champions died at r27-r45 in each of those games. No fuel read.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""int choose_target_impl(State& s, bc::champion& me, int round) {""",
"""// o69 teamopen-v1: the team opens together until round P_TO_R (near maps only with P_TO_NEAR).
inline bool teamopen_on(const State& s, int round) {
    if (!P_TO || round >= P_TO_R || s.roster < 2) return false;
    if (P_TO_NEAR) {
        const int sp = pf_spawn_path();
        if (sp < 0 || sp >= P_PF_MAX) return false;
    }
    return true;
}
int choose_target_impl(State& s, bc::champion& me, int round) {""")
rep("""    if (ball_on(s, round) && s.ally_idx > 0)
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < s.ally_idx && k < static_cast<int>(allies.size()); ++k) {
                if (!allies[k].is_alive()) continue;""",
"""    const bool to_on = teamopen_on(s, round);  // o69
    bool to_leader = to_on;                    // o69: no alive ally before me in draft order -> I lead
    if ((ball_on(s, round) || to_on) && s.ally_idx > 0)
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < s.ally_idx && k < static_cast<int>(allies.size()); ++k) {
                if (!allies[k].is_alive()) continue;
                to_leader = false;  // o69""")
rep("""        int team = std::max(1 + claimers, needed);""",
"""        int team = std::max(1 + claimers, needed);
        const bool pack = to_leader && (!P_TO_OWN || dist(g.center, s.spawn_center) + P_TO_OWN_D < dist(g.center, s.en_center));  // o69 teamopen-v1: the leader values the group for the whole team (P_TO_OWN: own-side groups only)
        if (pack) team = std::max(team, s.roster);""")
rep("""        bool pack = false;  // opening: everybody on the best camp together
""", "")
rep("""        if (needed > 1 + claimers) score *= (false && P_MP_COMPANY) ? P_MP_COMPANY / 100.0 : 0.7;  // still needs company (rule 8)""",
"""        if (needed > 1 + claimers && !pack) score *= (false && P_MP_COMPANY) ? P_MP_COMPANY / 100.0 : 0.7;  // still needs company (rule 8); o69: the team comes""")
rep("""    bool refresh = !committed && round - s.target_round >= (ball_on(s, round) ? 3 : target_refresh);""",
"""    bool refresh = !committed && round - s.target_round >= ((ball_on(s, round) || teamopen_on(s, round)) ? 3 : target_refresh);  // o69: followers re-choose every 3 rounds""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_TO
#define P_TO 1        // o69 teamopen-v1: the team opens together (first alive ally leads, the rest take its group x P_GROUP_W) until round P_TO_R
#define P_TO_R 40
#define P_TO_NEAR 0   // 1 = near maps only (spawn-to-spawn path < P_PF_MAX)
#define P_TO_OWN 1    // the leader values for the team only groups on our side (closer to our spawn by P_TO_OWN_D); v1 panel: with 0 the team walked into the centre groups (gemfight 78 gems, packs, gold_rush) and lost 2 champions at r27-45
#define P_TO_OWN_D 2
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)

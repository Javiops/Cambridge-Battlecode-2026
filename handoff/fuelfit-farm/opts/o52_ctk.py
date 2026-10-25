# fuelfit o52 (farm section, DECISION CHANGE, not exact): choose_target scores only the P_CT_K (12) camp groups nearest
# by walking distance (plus the current target and the leader's group). The scoring loop is pure C++ at ~500 fuel per
# group (12k on maps with 24-46 groups); groups 13+ by distance are chosen almost never (their score divides by rounds =
# travel + ...). The K-th distance is found with nth_element over the per-group distances (24-46 ints). Groups with no
# walking distance keep the old treatment. Effect to measure by strength (pair/vstat vs the base), never by fuel.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""#include <cambc.h>
""","""#include <cambc.h>
#ifndef P_CT_K
#define P_CT_K 12  // fuelfit o52: choose_target scores only the K nearest groups (0 = all)
#endif
""")
rep("""    const bool danger_on = round - s.danger_r <= P_DANGER_T;
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;
        bool held = s.hold_group[i];
        if (!held && danger_on && dist(g.center, s.danger_p) <= P_DANGER_R) continue;
        int wait = g.next_ok - round;  // > 0: respawning
        int gd = walk(g);
        if (gd < 0) continue;  // islefix-v1: no path and no dash""","""    const bool danger_on = round - s.danger_r <= P_DANGER_T;
    // fuelfit o52: the K-th nearest walking distance among the groups; farther groups are not scored
    int gd_cut = 1 << 30;
    if (P_CT_K > 0 && static_cast<int>(s.groups.size()) > P_CT_K) {
        static std::vector<int> gds;
        gds.clear();
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            const int gd = walk(s.groups[i]);
            gds.push_back(gd < 0 ? (1 << 29) : gd);
        }
        std::nth_element(gds.begin(), gds.begin() + (P_CT_K - 1), gds.end());
        gd_cut = gds[P_CT_K - 1];
    }
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;
        bool held = s.hold_group[i];
        if (!held && danger_on && dist(g.center, s.danger_p) <= P_DANGER_R) continue;
        int wait = g.next_ok - round;  // > 0: respawning
        int gd = walk(g);
        if (gd < 0) continue;  // islefix-v1: no path and no dash
        if (gd > gd_cut && i != s.target && !lead) continue;  // fuelfit o52: beyond the K nearest""")
open(p,'w',newline='').write(s)
print("o52 ok")

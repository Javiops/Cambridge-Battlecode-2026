# o63_gdonce.py SRCDIR (fuelfit, farm thread; EXACT, after o52). choose_target computed each group's walking distance
# twice per call: once in the o52 K-cut pass (walk() + vector push_back, ~59 fuel each) and again in the scoring loop.
# walk() has no side effects (o59 caches the one SDK query it may make), so the distances are computed once into a
# pre-sized static array and the scoring loop reads them. First-turn profile of b15 (14 far maps): the K-cut pass cost
# ~300 per group (7.6k on 24 groups), the scoring loop's walk() another ~130 per group.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    int gd_cut = 1 << 30;
    if (P_CT_K > 0 && static_cast<int>(s.groups.size()) > P_CT_K) {
        static std::vector<int> gds;
        gds.clear();
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            const int gd = walk(s.groups[i]);
            gds.push_back(gd < 0 ? (1 << 29) : gd);
        }
        std::nth_element(gds.begin(), gds.begin() + (P_CT_K - 1), gds.end());
        gd_cut = gds[P_CT_K - 1];
    }""","""    int gd_cut = 1 << 30;
    // fuelfit o63: every group's walking distance once (walk() has no side effects), reused by the scoring loop
    static std::vector<int> gds, gds_sorted;
    const int ngroups = static_cast<int>(s.groups.size());
    if (static_cast<int>(gds.size()) < ngroups) { gds.resize(ngroups); gds_sorted.resize(ngroups); }
    for (int i = 0; i < ngroups; ++i) gds[i] = walk(s.groups[i]);
    if (P_CT_K > 0 && ngroups > P_CT_K) {
        for (int i = 0; i < ngroups; ++i) gds_sorted[i] = gds[i] < 0 ? (1 << 29) : gds[i];
        std::nth_element(gds_sorted.begin(), gds_sorted.begin() + (P_CT_K - 1), gds_sorted.begin() + ngroups);
        gd_cut = gds_sorted[P_CT_K - 1];
    }""")
rep("""        int wait = g.next_ok - round;  // > 0: respawning
        int gd = walk(g);
        if (gd < 0) continue;  // islefix-v1: no path and no dash""","""        int wait = g.next_ok - round;  // > 0: respawning
        int gd = gds[i];  // fuelfit o63
        if (gd < 0) continue;  // islefix-v1: no path and no dash""")
open(p,'w',newline='').write(s); print('o63 ok')

# pk "manada" (superiority thread 10-27): fixed packs by roster index farm together from P_PK_FROM to P_PK_TO.
# t5b 2.0.0 replays r21-100: top 5 hit a camp with an ally on the same group 67% of camp rounds (we 45%), have an ally
# within 2 52% (we 36%); contacts start 2.7 vs 2.1 near; reinforcement after the start is ~0 for both.
import sys, re
p = sys.argv[1] + '/main.cpp'
s = open(p).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a, s.count(a))
    s = s.replace(a, b)
rep("bool grouped(const State& s, int round) { return false; }",
"""#ifndef P_PK
#define P_PK 1          // pk manada: packs {0,1} {2,3,4} (5 champions), {0,1} {2,3} (4), {0,1,2} (3); index = roster order
#endif
#ifndef P_PK_FROM
#define P_PK_FROM 40
#endif
#ifndef P_PK_TO
#define P_PK_TO 150
#endif
#ifndef P_PK_W
#define P_PK_W 5        // score x for the leader's claimed group
#endif
#ifndef P_PK_FAR
#define P_PK_FAR 30     // score % for a group farther than P_PK_R from the leader (when the leader is in vision)
#endif
#ifndef P_PK_R
#define P_PK_R 8
#endif
#ifndef P_PK_NEAR
#define P_PK_NEAR 0     // > 0: only maps whose spawn-to-spawn path is below this
#endif
int pk_lead(const State& s) {
    if (!P_PK || s.ally_idx <= 0) return -1;
    const int n = s.roster, i = s.ally_idx;
    if (n == 5) return i == 1 ? 0 : (i >= 3 ? 2 : -1);
    if (n == 4) return i == 1 ? 0 : (i == 3 ? 2 : -1);
    if (n == 3) return 0;
    return -1;
}
int pf_spawn_path();
bool grouped(const State& s, int round) {
    if (!P_PK || round < P_PK_FROM || round > P_PK_TO || pk_lead(s) < 0) return false;
    if (P_PK_NEAR) { const int sp = pf_spawn_path(); if (sp < 0 || sp >= P_PK_NEAR) return false; }
    return true;
}""")
rep("""inline int pf_spawn_path() {""", """int pf_spawn_path() {""")
# leader = the pack leader (alive), not the first alive ally
rep("""            for (int k = 0; k < s.ally_idx && k < static_cast<int>(allies.size()); ++k) {
                if (!allies[k].is_alive()) continue;""",
"""            for (int k = pk_lead(s); k >= 0 && k < s.ally_idx && k < static_cast<int>(allies.size()); ++k) {
                if (!allies[k].is_alive()) break;""")
rep("""        if (lead) score *= P_GROUP_W;
        else if (lead_p && dist(g.center, *lead_p) > 8) score *= 0.3;""",
"""        if (lead) score *= P_PK_W;
        else if (lead_p && dist(g.center, *lead_p) > P_PK_R) score *= P_PK_FAR / 100.0;""")
rep('''std::printf("[fuelfit] b35nohp o74 nohitpass det + farmeo c95go45e1 o100_incoming o125_holdlate o129_goldopen45\\n");''',
'''std::printf("[fuelfit] b35nohp o74 nohitpass det + farmeo c95go45e1 o100_incoming o125_holdlate o129_goldopen45 + sup pk%d r%d-%d w%d far%d\\n", P_PK, P_PK_FROM, P_PK_TO, P_PK_W, P_PK_FAR);''')
open(p, 'w').write(s)
print('ok pk')

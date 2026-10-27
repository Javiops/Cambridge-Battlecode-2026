# pkb: pk + the leader prices monster groups for its whole pack, followers only follow into monster groups / rich clusters
import sys, subprocess
d = sys.argv[1]
subprocess.check_call(['python3', '/tmp/claude-0/w/opts/pk.py', d])
p = d + '/main.cpp'
s = open(p).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a, s.count(a))
    s = s.replace(a, b)
rep("int pf_spawn_path();\nbool grouped(", """#ifndef P_PK_CLG
#define P_PK_CLG 10     // followers also follow into gem clusters with this many gems
#endif
int pk_followers(const State& s) {  // pack leader: how many followers price its groups
    if (!P_PK || s.ally_idx < 0) return 0;
    const int n = s.roster, i = s.ally_idx;
    if (n == 5) return i == 0 ? 1 : (i == 2 ? 2 : 0);
    if (n == 4) return (i == 0 || i == 2) ? 1 : 0;
    if (n == 3) return i == 0 ? 2 : 0;
    return 0;
}
int pf_spawn_path();
bool grouped(""")
rep("""    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group;""", """    const int pk_fn = (P_PK && round >= P_PK_FROM && round <= P_PK_TO) ? pk_followers(s) : 0;
    for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
        Group& g = s.groups[i];
        if (g.bad_until > round) continue;
        bool lead = i == lead_group && (g.str > 0 || g.gems >= P_PK_CLG);""")
rep("""        int team = std::max(1 + claimers, needed);""", """        int team = std::max(1 + claimers, needed);
        if (pk_fn > 0 && g.str > 0) team = std::max(team, 1 + pk_fn);  // pkb: the pack comes with the leader""")
open(p, 'w').write(s)
print('ok pkb')

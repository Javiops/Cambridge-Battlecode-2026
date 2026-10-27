# aa "ancla en aliado" (superiority thread 10-27, coordinator/user: build on the diagnosed faults).
# t5b 2.0.0: our wounded die 39% vs 12%, die after leaving 22% vs 7%, with 0.49 allies within 4 when leaving vs 0.83
# (we leave toward nobody: flee() walks to our spawn); r151-300 deaths 53% with no ally within 6, 76% in our half;
# top 5's nearest ally 10 rounds before a death is at 2-3, ours at 4-7.
#  (1) flee(): toward the nearest healthy visible ally within P_AA_R that is not nearer the closest rival than we are
#      (ring 1 around it), else home as before.
#  (2) choose_target: a group with a visible ally within P_AA_GR of its centre scores x P_AA_GW/100.
#  (3) optional awb early warning (P_AW) and pairfarm extended (P_PF_UNTIL / P_PF_MAX) via defines.
import sys, re
p = sys.argv[1] + '/main.cpp'
s = open(p).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)
rep("bool flee(State& s, bc::champion& me) { return step_towards(s, me, s.my_spawn, true); }",
"""#ifndef P_AA
#define P_AA 1
#endif
#ifndef P_AA_HOME
#define P_AA_HOME 2  // the ally must be this much nearer home than we are (0 = anywhere)
#endif
#ifndef P_AA_R
#define P_AA_R 10
#endif
#ifndef P_AA_GR
#define P_AA_GR 3
#endif
#ifndef P_AA_GW
#define P_AA_GW 150
#endif
int g_aa_flee = 0;
bool flee(State& s, bc::champion& me) {
    if (P_AA && s.seen_r == static_cast<int>(bc::round_number()) && !s.seen.empty()) {
        const vec2 pos = me.position();
        vec2 fp = s.seen.front().p;
        for (auto& o : s.seen) if (dist(o.p, pos) < dist(fp, pos)) fp = o.p;
        const int myd = dist(pos, fp);
        vec2 best{0, 0};
        int bd = 99;
        attempt([&] {
            for (auto& a : vis_champions(*s.my)) {
                if (a == me || !a.is_alive() || a.is_recalling() || a.health() < 0.4f * a.max_health()) continue;
                const vec2 q = a.position();
                const int d = dist(q, pos);
                if (d < 2 || d > P_AA_R || dist(q, fp) < myd || d >= bd) continue;
                if (P_AA_HOME && dist(q, s.spawn_center) > dist(pos, s.spawn_center) - P_AA_HOME) continue;  // on the way home
                bd = d; best = q;
            }
            return true;
        });
        if (bd < 99) {
            bc::bitboard ring;
            ring.draw_chebyshev(best, 1.0f);
            ring &= ~s.blocked;
            if (step_towards(s, me, ring, true)) { ++g_aa_flee; return true; }
        }
    }
    return step_towards(s, me, s.my_spawn, true);
}""")
rep("    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();",
"""    std::vector<vec2> aa_mates;  // aa (2): visible allies' tiles
    if (P_AA && P_AA_GW != 100)
        attempt([&] {
            for (auto& a : vis_champions(*s.my))
                if (!(a == me) && a.is_alive() && !a.is_recalling()) aa_mates.push_back(a.position());
            return true;
        });
    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();""")
rep("        if (score > best_score) { best_score = score; best = i; best_gd = gd; }",
"""        if (!aa_mates.empty()) {
            bool near = false;
            for (auto q : aa_mates) near |= dist(q, g.center) <= P_AA_GR;
            if (near) score *= P_AA_GW / 100.0;
        }
        if (score > best_score) { best_score = score; best = i; best_gd = gd; }""")
m = re.search(r'    std::printf\("\[fuelfit\][^\n]*\n', s)
s = s[:m.end()] + '    std::printf("[sup] aa%d H%d R%d GR%d GW%d\\n", P_AA, P_AA_HOME, P_AA_R, P_AA_GR, P_AA_GW);\n' + s[m.end():]
open(p, 'w').write(s)
print('ok aa')

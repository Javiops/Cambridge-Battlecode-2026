# cv "convocatoria" (superiority thread 10-27; farm data: 1.24 elk groups/game in our half untouched at r300, mostly
# 2+ elk; we come within 6 in 76% and do not go in; top 5 takes them with 3 champions in 58/84, 36-51 rounds).
#  (1) choose_target: a monster group an ally claims that still lacks company (needed > claimers) within P_CV_D walk
#      scores x P_CV_W/100 (the ally's call is answered);
#  (2) farm(): a champion whose target needs more company than it has (needed > 1 + claimers) holds within
#      P_CV_HOLD of the group, out of the camps' reach, up to P_CV_WAIT rounds before going in alone.
import sys, re
p = sys.argv[1] + '/main.cpp'
s = open(p).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)
rep("int choose_target_impl(State& s, bc::champion& me, int round) {\n", """#ifndef P_CV
#define P_CV 1
#endif
#ifndef P_CV_FROM
#define P_CV_FROM 40
#endif
#ifndef P_CV_W
#define P_CV_W 250
#endif
#ifndef P_CV_D
#define P_CV_D 20
#endif
#ifndef P_CV_HOLD
#define P_CV_HOLD 6
#endif
#ifndef P_CV_WAIT
#define P_CV_WAIT 15
#endif
int g_cv_call = 0, g_cv_wait = 0;
int choose_target_impl(State& s, bc::champion& me, int round) {
""")
rep("        if (needed > 1 + claimers) score *= (false && P_MP_COMPANY) ? P_MP_COMPANY / 100.0 : 0.7;  // still needs company (rule 8)",
"""        if (needed > 1 + claimers) score *= (false && P_MP_COMPANY) ? P_MP_COMPANY / 100.0 : 0.7;  // still needs company (rule 8)
        if (P_CV && round >= P_CV_FROM && g.str > 0 && claimers > 0 && needed > claimers && i != s.target && gd <= P_CV_D) {
            score *= P_CV_W / 100.0;  // cv (1): answer an ally's call
            ++g_cv_call;
        }""")
rep("""    g_farm = "travel";
    if (s.target < 0) {""", """    g_farm = "travel";
    if (P_CV && round >= P_CV_FROM && s.target >= 0 && !committed && s.target < static_cast<int>(s.groups.size())) {
        static int cv_g = -1, cv_t0 = -1;  // this champion's wait: group and first round
        Group& g = s.groups[s.target];
        bool hold = false;
        if (g.str > 0 && !g.monolith && dist(pos, g.center) <= P_CV_HOLD) {
            const double afford = std::max(1.0, static_cast<double>(me.max_health()) * (1.0 - P_RESERVE_PCT / 100.0));
            const int needed = squad_needed(g.hp, g.str, my_dps(s, me), afford);
            const int claimers = count_claimers(s, read_sm(), s.target);
            if (needed > 1 + claimers) {
                if (cv_g != s.target) { cv_g = s.target; cv_t0 = round; }
                hold = round - cv_t0 < P_CV_WAIT;
            }
        }
        if (hold) {
            g_farm = "cv-wait";
            ++g_cv_wait;
            bool safe_tile = true;
            for (auto& c : camps)
                if (g.mask.is_set(c.spawn_position()) && dist(c.position(), pos) <= camp_range(c) + 1) safe_tile = false;
            if (!safe_tile) {
                bc::bitboard out;
                out.draw_chebyshev(g.center, static_cast<float>(P_CV_HOLD));
                for (auto& c : camps)
                    if (g.mask.is_set(c.spawn_position())) { bc::bitboard k; k.draw_chebyshev(c.position(), static_cast<float>(camp_range(c) + 1)); out &= ~k; }
                step_towards(s, me, out & ~s.blocked, false);
            }
            return;
        }
    }
    if (s.target < 0) {""")
m = re.search(r'    std::printf\("\[fuelfit\][^\n]*\n', s)
s = s[:m.end()] + '    std::printf("[sup] cv%d r%d W%d D%d H%d T%d\\n", P_CV, P_CV_FROM, P_CV_W, P_CV_D, P_CV_HOLD, P_CV_WAIT);\n' + s[m.end():]
open(p, 'w').write(s)
print('ok cv')

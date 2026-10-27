#!/usr/bin/env python3
"""o106 elksquad: choose_target prices a strong camp group (str >= P_ESQ_STR, i.e. two elks or more) as a job for the squad that is
already around me (1 + living allies visible within P_ESQ_R, capped at P_ESQ_N) instead of a pair that never forms, and with the
incoming damage measured in the real games (P_ESQ_INC percent of str x clear time per champion, c34 games vs ranks 56-70:
2-elk groups taken with 3-4 champions in 12-30 rounds, 500-900 health lost by the whole squad, zero deaths; the model said 1760-2520
for a pair). The "still needs company" x0.7 is lifted when that squad is here. From round P_ESQ_R0.
Why: in the 33 c34 losses of e1foco the rival captures 0.7 strong groups per game (72 gems each) against our 0.3, with 3-4 champions
within 4 of the camp; ours are taken by 2-3. Both sides capture the same number of gold-only clusters (4.7 vs 4.8 per game, r151-300).
Usage: o106_elksquad.py SRCDIR [STR=120] [R=10] [N=3] [INC=28] [R0=0]"""
import sys, os
src = sys.argv[1]; args = sys.argv[2:] + ['120', '10', '3', '28', '0'][len(sys.argv) - 2:]
STR, R, N, INC, R0 = args[:5]
p = os.path.join(src, 'main.cpp'); s = open(p).read()
a = "    const bool danger_on = round - s.danger_r <= P_DANGER_T;\n"
assert s.count(a) == 1
s = s.replace(a, a + """    std::vector<vec2> esq_ally_pos;  // o106 elksquad: living allies visible this round
    if (round >= P_ESQ_R0)
        for (auto& ally : vis_champions(*s.my))
            attempt([&] {
                if (!(ally == me) && ally.is_alive() && ally.is_visible()) esq_ally_pos.push_back(ally.position());
                return true;
            });
""")
a = "        int team = std::max(1 + claimers, needed);\n"
assert s.count(a) == 1
s = s.replace(a, """        int esq_team = 0;  // o106 elksquad: a strong group is a job for the squad already around me
        if (g.str >= P_ESQ_STR && round >= P_ESQ_R0) {
            int near = 0;
            for (auto& ap : esq_ally_pos) if (dist(ap, pos) <= P_ESQ_R) ++near;
            esq_team = std::min(P_ESQ_N, 1 + near);
        }
        int team = std::max(1 + claimers, needed);
        if (esq_team > team) team = esq_team;
""")
a = "        double incoming = g.str * t_clear / team * (P_INC_PCT / 100.0);"
assert s.count(a) == 1
s = s.replace(a, "        double incoming = g.str * t_clear / team * ((esq_team >= 2 ? P_ESQ_INC : P_INC_PCT) / 100.0);  // o106 elksquad: measured for squads")
a = "        if (needed > 1 + claimers) score *= (false && P_MP_COMPANY)"
assert s.count(a) == 1
s = s.replace(a, "        if (needed > 1 + claimers && esq_team < needed) score *= (false && P_MP_COMPANY)")
m = 'o129_goldopen45'; assert s.count(m) == 1
s = s.replace(m, m + ' o106_elksquad')  # stdout marker on the [fuelfit] line
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_ESQ_STR\n#define P_ESQ_STR {STR}  // o106 elksquad: groups of this strength or more are priced for the squad around me\n#define P_ESQ_R {R}      // allies counted within this distance of me\n#define P_ESQ_N {N}      // squad size cap\n#define P_ESQ_INC {INC}   // incoming damage, percent of str x clear time per champion, when the squad is 2+ (measured 28)\n#define P_ESQ_R0 {R0}     // from this round\n#endif\n")
print("o106 applied to", src, "STR", STR, "R", R, "N", N, "INC", INC, "R0", R0)

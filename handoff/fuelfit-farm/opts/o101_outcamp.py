#!/usr/bin/env python3
"""o101 outcamp: choose_target skips a camp group when the enemy champions visible within P_OUTC_RE of it outnumber us there
(me + allies visible within P_OUTC_RA of the group, or the claimers already on it) by P_OUTC_SLACK or more, from round P_OUTC_R0.
Real 2.0.0 games vs the top 5 (118, r151-300): our champion arrives at a camp with 2+ enemies within 10 in 31% of the arrivals
and dies within 15 rounds in 19% of those (top 5: 28% and 4%); we arrive outnumbered in 41% of the contested arrivals (top 5: 17%),
and at equal numbers we still die 13% vs 3%. Until now only a pack of P_DANGER (4) enemies within 4 of each other marked a camp
as dangerous. Usage: o101_outcamp.py SRCDIR [SLACK=1] [RE=8] [RA=6] [R0=0]"""
import sys, os
src = sys.argv[1]; args = sys.argv[2:] + ['1', '8', '6', '0'][len(sys.argv) - 2:]
SLACK, RE, RA, R0 = args[:4]
p = os.path.join(src, 'main.cpp'); s = open(p).read()
a = "    std::vector<Threat> thr;         // P_VOLLEY: ready enemy damage around us this round\n"
assert s.count(a) == 1
s = s.replace(a, a + "    std::vector<vec2> foe_pos;       // o101 outcamp: every enemy champion visible this round (not only within 10 of us)\n")
a = "    if (!foes.empty()) s.foe_r = round;\n"
assert s.count(a) == 1
s = s.replace(a, a + "    s.foe_pos.clear();  // o101 outcamp\n    for (auto& f : foes) if (!s.en_spawn.is_set(f.p)) s.foe_pos.push_back(f.p);\n")
a = "        int claimers = claimers_of[i] - tank_claims_of[i];  // fuelfit o45 (B): counted once above\n"
assert s.count(a) == 1
s = s.replace(a, a + """        if (P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty()) {  // o101 outcamp: not into a camp where the visible enemies outnumber us
            int en = 0, al = 0;
            for (auto& fp : s.foe_pos) if (dist(fp, g.center) <= P_OUTC_RE) ++en;
            if (en > 0) {
                for (auto& ap : oc_ally_pos) if (dist(ap, g.center) <= P_OUTC_RA) ++al;
                const int ours = std::max(1 + al, 1 + claimers);
                if (en >= ours + P_OUTC_SLACK) continue;
            }
        }
""")
# ally positions once per call, before the group loop
a = "    const bool danger_on = round - s.danger_r <= P_DANGER_T;\n"
assert s.count(a) == 1
s = s.replace(a, a + """    std::vector<vec2> oc_ally_pos;  // o101 outcamp: visible living allies
    if (P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty())
        for (auto& ally : vis_champions(*s.my))
            attempt([&] {
                if (!(ally == me) && ally.is_alive() && ally.is_visible()) oc_ally_pos.push_back(ally.position());
                return true;
            });
""")
m = 'o129_goldopen45'; assert s.count(m) == 1
s = s.replace(m, m + ' o101_outcamp')  # stdout marker on the [fuelfit] line
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_OUTC_SLACK\n#define P_OUTC_SLACK {SLACK}  // o101 outcamp: skip a camp when visible enemies >= ours + SLACK (-1 = off)\n#define P_OUTC_RE {RE}      // enemies counted within this Chebyshev distance of the group centre\n#define P_OUTC_RA {RA}      // allies counted within this distance of the group centre\n#define P_OUTC_R0 {R0}      // from this round\n#endif\n")
print("o101 applied to", src, "SLACK", SLACK, "RE", RE, "RA", RA, "R0", R0)

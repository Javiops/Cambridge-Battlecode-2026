#!/usr/bin/env python3
"""o102 allynear (applied after o101_outcamp.py, uses its oc_ally_pos): in choose_target a gold-only group (no gems) with no visible
ally within P_OUTC_RA of it and no claimer scores x P_ALONE_W/100; a gem group (elk, gem cluster) with an ally within P_OUTC_RA
or a claimer scores x P_TOGETHER_W/100. Real 2.0.0 games vs the top 5 (118, r151-300): they capture 1.9 elk groups a game to our
1.1 and 2.8 gold-only clusters to our 3.7; our victim had its nearest ally 7+ tiles away at first sight of the enemy in 45% of
its deaths (top 5: 19%); our arrivals at a camp have 0 allies within 6 in 43% (top 5: 26%).
Usage: o102_allynear.py SRCDIR [ALONE_W=50] [TOGETHER_W=120] [R0=0]"""
import sys, os
src = sys.argv[1]; args = sys.argv[2:] + ['50', '120', '0'][len(sys.argv) - 2:]
AW, TW, R0 = args[:3]
p = os.path.join(src, 'main.cpp'); s = open(p).read()
a = "    if (P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty())\n        for (auto& ally : vis_champions(*s.my))\n"
assert s.count(a) == 1
s = s.replace(a, "    if ((P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty()) || round >= P_ALONE_R0)  // o102: allies also for allynear\n        for (auto& ally : vis_champions(*s.my))\n")
a = "        if (gc[i].near_en) score *= 0.6;    // stay off their doorstep\n"
assert s.count(a) == 1
s = s.replace(a, a + """        if (round >= P_ALONE_R0 && !mono_go && !jack_go) {  // o102 allynear: gems with company first, gold alone far from everyone last
            bool ally_near = claimers > 0;
            for (auto& ap : oc_ally_pos) if (!ally_near && dist(ap, g.center) <= P_OUTC_RA) ally_near = true;
            if (g.gems <= 0 && !ally_near) score *= P_ALONE_W / 100.0;
            else if (g.gems > 0 && ally_near) score *= P_TOGETHER_W / 100.0;
        }
""")
m = 'o101_outcamp'; assert s.count(m) >= 1
s = s.replace('o101_outcamp\\n")', 'o101_outcamp o102_allynear\\n")')  # stdout marker on the [fuelfit] line
assert 'o102_allynear' in s
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_ALONE_W\n#define P_ALONE_W {AW}      // o102 allynear: gold-only group with no ally within P_OUTC_RA and no claimer scores x this %\n#define P_TOGETHER_W {TW}  // gem group with an ally within P_OUTC_RA or a claimer scores x this %\n#define P_ALONE_R0 {R0}      // from this round\n#endif\n")
print("o102 applied to", src, "ALONE_W", AW, "TOGETHER_W", TW, "R0", R0)

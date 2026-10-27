#!/usr/bin/env python3
"""o103 cleartime: choose_target's modelled clear time of a monster group (t_clear = hp / (dps x team), and the incoming damage that
scales with it) is multiplied by P_TCLEAR_PCT/100. Real 2.0.0 games vs the top 5 (118, r<=300, gem/t5b_cleartime.py): a 2-elk group
(hp 5040, str 120) is cleared in a median 16-20 rounds by 2-3 champions, by us and by them alike; the model prices it at 84 rounds of
clearing plus ~50 rounds of recall cycles at r10 (dps 30), so it scores 0.53 against 0.82 for a small camp and 72% of the 2-elk groups
on our half are never touched by r300 (top 5 take 49% of the elks, we 39%). v2: the discount applies only from round R0 and, with PAIR=1, only when the group already has a claimer or an ally stands
within P_OUTC_RA of me (the pair is real; the plain discount sent lone champions into big camps: o1f camp deaths x2).
Usage: o103_cleartime.py SRCDIR [PCT=40] [R0=60] [PAIR=1]"""
import sys, os
src = sys.argv[1]; args = sys.argv[2:] + ['40', '60', '1'][len(sys.argv) - 2:]; PCT, R0, PAIR = args[:3]
p = os.path.join(src, 'main.cpp'); s = open(p).read()
a = "        double t_clear = free_reward ? 0.0 : g.hp / (dps * team);\n"
assert s.count(a) == 1
s = s.replace(a, """        bool tc_pair = claimers >= 1;  // o103 cleartime v2: the pair is real (a claimer, or an ally next to me)
        if (!tc_pair && P_TCLEAR_PAIR) for (auto& ap : oc_ally_pos) if (dist(ap, pos) <= P_OUTC_RA) { tc_pair = true; break; }
        const bool tc_on = P_TCLEAR_PCT < 100 && round >= P_TCLEAR_R0 && (!P_TCLEAR_PAIR || tc_pair);
        double t_clear = free_reward ? 0.0 : g.hp / (dps * team) * (tc_on ? P_TCLEAR_PCT / 100.0 : 1.0);  // o103 cleartime: measured clear times are a fraction of hp/dps
""")
m = 'o101_outcamp'; assert s.count(m) >= 1 and s.count('o101_outcamp\\n")') == 1
s = s.replace('o101_outcamp\\n")', 'o101_outcamp o103_cleartime\\n")')
b = "    if ((P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty()) || round >= P_ALONE_R0)  // o102: allies also for allynear\n"
c = "    if (P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty())\n        for (auto& ally : vis_champions(*s.my))\n"
if s.count(b) == 1: s = s.replace(b, "    if ((P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty()) || round >= P_ALONE_R0 || (P_TCLEAR_PAIR && round >= P_TCLEAR_R0))  // o102/o103: allies also needed\n")
else:
    assert s.count(c) == 1
    s = s.replace(c, "    if ((P_OUTC_SLACK >= 0 && round >= P_OUTC_R0 && !s.foe_pos.empty()) || (P_TCLEAR_PAIR && round >= P_TCLEAR_R0))  // o103: allies also for the pair test\n        for (auto& ally : vis_champions(*s.my))\n")
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_TCLEAR_PCT\n#define P_TCLEAR_PCT {PCT}  // o103 cleartime: modelled clear time (and incoming camp damage) x this % (100 = old model)\n#define P_TCLEAR_R0 {R0}   // from this round\n#define P_TCLEAR_PAIR {PAIR}  // 1: only when the group has a claimer or an ally is within P_OUTC_RA of me\n#endif\n")
print("o103 applied to", src, "PCT", PCT, "R0", R0, "PAIR", PAIR)

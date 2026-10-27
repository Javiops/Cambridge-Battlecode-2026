#!/usr/bin/env python3
"""o107 goldlate (o102-lite): from round P_GL_R0 the gold weight in choose_target is capped at P_GL_W percent of a gem (e1foco: 45 from
r150, 1.0 before r940 otherwise). The opening (o129 goldopen, 45 until r150) is untouched. Optional P_GL_WOLF: wolf-only groups score
x P_GL_WOLF/100 from the same round.
Why: top 10 vs top 10 (599 games of 10-27, r151-300) make the same number of captures as we do (9.0 vs our 8.5-10) but each is worth
16 gems against our 7-11: wolf camps 2.8, gold-only clusters 2.5, gem clusters 2.1, elk 1.56 per game; ours in losses vs ranks 56-70:
gold-only 4.7, wolf 1.9, gem 1.1, elk 0.8. Our model prices a gold cluster (40 gold x 0.45 = 18 in ~16 rounds) over a wolf camp
(12 gems + 60 gold in ~67 modelled rounds). The own-lineage bench cannot judge this (its rivals are our gold-farming bots): online does.
Usage: o107_goldlate.py SRCDIR [W=30] [R0=150] [WOLF=100]"""
import sys, os
src = sys.argv[1]; args = sys.argv[2:] + ['30', '150', '100'][len(sys.argv) - 2:]
W, R0, WOLF = args[:3]
p = os.path.join(src, 'main.cpp'); s = open(p).read()
a = "    if (round >= P_RC2_R) gold_w = std::min(gold_w, P_RC2_GW / 100.0);"
assert s.count(a) == 1
s = s.replace(a, a + "\n    if (round >= P_GL_R0) gold_w = std::min(gold_w, P_GL_W / 100.0);  // o107 goldlate: top 10 take wolves and elks over gold clusters from r150")
a = "        if (jack_go) score *= P_JACKW;\n"
assert s.count(a) == 1
s = s.replace(a, a + "        if (P_GL_WOLF != 100 && g.str > 0 && g.str == 20 * g.members && round >= P_GL_R0) score *= P_GL_WOLF / 100.0;  // o107 goldlate: wolf camps\n")
m = 'o129_goldopen45'; assert s.count(m) == 1
s = s.replace(m, m + ' o107_goldlate')  # stdout marker on the [fuelfit] line
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_GL_W\n#define P_GL_W {W}      // o107 goldlate: gold weight cap (percent of a gem) from P_GL_R0\n#define P_GL_R0 {R0}    // from this round (the o129 opening keeps its 45 until r150)\n#define P_GL_WOLF {WOLF}  // wolf-only groups score x this/100 from P_GL_R0 (100 = off)\n#endif\n")
print("o107 applied to", src, "W", W, "R0", R0, "WOLF", WOLF)

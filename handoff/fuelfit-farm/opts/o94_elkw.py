#!/usr/bin/env python3
"""o94 elkw: choose_target multiplies the score of gem-bearing monster groups that are not wolf-only (elk/golem groups)
by P_ELKW/100. Real 2.0.0 games vs the top 5 (375, both sides): they capture 1.54 elk+gem groups/game in r0-150 (48 gems)
vs our 1.07 (32); we take 3.7 gold-only clusters vs their 2.8. Usage: o94_elkw.py SRCDIR [PCT=130]"""
import sys, os
src = sys.argv[1]; pct = sys.argv[2] if len(sys.argv) > 2 else '130'
p = os.path.join(src, 'main.cpp'); s = open(p).read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
rep("    bool jackpot = false;", "    bool jackpot = false;\n    bool has_elk = false;                    // o94 elkw: an elk sits in the group")
rep("            G.cluster = G.cluster || cgem || cgold;\n", "            G.cluster = G.cluster || cgem || cgold;\n            G.has_elk = G.has_elk || ce;  // o94\n")
a = "        double score = value / std::max(1.0, rounds);\n"
rep(a, a + "        if (g.gems > 0 && g.has_elk && !g.monolith) score *= P_ELKW / 100.0;  // o94 elkw: elk gem groups\n")
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_ELKW\n#define P_ELKW {pct}   // o94 elkw: score multiplier for gem-bearing non-wolf monster groups (100 = off)\n#endif\n")
print("o94 applied to", src, "P_ELKW", pct)

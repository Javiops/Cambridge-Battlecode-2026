#!/usr/bin/env python3
"""o103 cleartime: choose_target's modelled clear time of a monster group (t_clear = hp / (dps x team), and the incoming damage that
scales with it) is multiplied by P_TCLEAR_PCT/100. Real 2.0.0 games vs the top 5 (118, r<=300, gem/t5b_cleartime.py): a 2-elk group
(hp 5040, str 120) is cleared in a median 16-20 rounds by 2-3 champions, by us and by them alike; the model prices it at 84 rounds of
clearing plus ~50 rounds of recall cycles at r10 (dps 30), so it scores 0.53 against 0.82 for a small camp and 72% of the 2-elk groups
on our half are never touched by r300 (top 5 take 49% of the elks, we 39%). Usage: o103_cleartime.py SRCDIR [PCT=40]"""
import sys, os
src = sys.argv[1]; PCT = sys.argv[2] if len(sys.argv) > 2 else '40'
p = os.path.join(src, 'main.cpp'); s = open(p).read()
a = "        double t_clear = free_reward ? 0.0 : g.hp / (dps * team);\n"
assert s.count(a) == 1
s = s.replace(a, "        double t_clear = free_reward ? 0.0 : g.hp / (dps * team) * (P_TCLEAR_PCT / 100.0);  // o103 cleartime: measured clear times are a fraction of hp/dps\n")
m = 'o101_outcamp'; assert s.count(m) >= 1 and s.count('o101_outcamp\\n")') == 1
s = s.replace('o101_outcamp\\n")', 'o101_outcamp o103_cleartime\\n")')
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_TCLEAR_PCT\n#define P_TCLEAR_PCT {PCT}  // o103 cleartime: modelled clear time (and incoming camp damage) x this % (100 = old model)\n#endif\n")
print("o103 applied to", src, "PCT", PCT)

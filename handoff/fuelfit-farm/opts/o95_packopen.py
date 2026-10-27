#!/usr/bin/env python3
"""o95 packopen: in the opening (round < P_PACK_R) on near maps (hp_far false: spawn walk < 60) choose_target does not split a
group's value by the team size and lets several champions take the same cluster, so the whole team converges on the best
camp. Real 2.0.0 games vs the top 5: their first capture is at r24 with 3.0 champions within 3 (3+ in 72/118 games), ours
at r28 with 1.9 (31/118); by r50 they have 23 gems from 1.9 captures, we 15 from 2.5. Usage: o95_packopen.py SRCDIR [R=40]"""
import sys, os
src = sys.argv[1]; R = sys.argv[2] if len(sys.argv) > 2 else '40'
p = os.path.join(src, 'main.cpp'); s = open(p).read()
a = "        bool pack = false;  // opening: everybody on the best camp together\n"
assert s.count(a) == 1
s = s.replace(a, "        bool pack = P_PACK_R > 0 && round < P_PACK_R && !s.hp_far;  // o95 packopen: opening on near maps, everybody on the best camp together\n")
open(p, 'w').write(s)
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write(f"#ifndef P_PACK_R\n#define P_PACK_R {R}   // o95 packopen: rounds of the opening in which the team packs on one camp (near maps); 0 = off\n#endif\n")
print("o95 applied to", src, "P_PACK_R", R)

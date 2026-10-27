#!/usr/bin/env python3
"""o92 farguard: on far maps (spawn walk >= P_HITLAST_FAR, the bot's existing hp_far flag) the two E1 opening pieces
o100 (incoming x0.5) and o129 (gold weight 0.45 in the opening) revert to the b35 values (100 / 100).
Bench 2.0.0 far set (14 maps x rTop1,rD x 2 sides): E1 42/56; E1 with incoming 100 49/56; E1 with gold opening 1.0 49/56;
b35 48/56. Near maps unchanged by construction (hp_far false). Usage: o92_farguard.py SRCDIR"""
import sys, os
src = sys.argv[1]
def patch(path, reps):
    s = open(path).read()
    for a, b in reps:
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    open(path, 'w').write(s)
patch(os.path.join(src, 'main.cpp'), [
    ("static int g_tpc_path = -1;",
     "static int g_tpc_path = -1;\nstatic int g_inc_pct = P_INC_PCT;  // o92 farguard: P_FAR_INC on far maps (set with hp_far)"),
    ("        s.hp_far = P_HITLAST_FAR > 0 && !(g_tpc_path >= 0 && g_tpc_path < P_HITLAST_FAR);",
     "        s.hp_far = P_HITLAST_FAR > 0 && !(g_tpc_path >= 0 && g_tpc_path < P_HITLAST_FAR);\n"
     "        g_inc_pct = s.hp_far ? P_FAR_INC : P_INC_PCT;  // o92 farguard"),
    ("        if (hp_g * str_g * (P_INC_PCT / 100.0) / (dps * n * (focus ? 1 : n)) <= afford)",
     "        if (hp_g * str_g * (g_inc_pct / 100.0) / (dps * n * (focus ? 1 : n)) <= afford)"),
    ("        double incoming = g.str * t_clear / team * (P_INC_PCT / 100.0);",
     "        double incoming = g.str * t_clear / team * (g_inc_pct / 100.0);"),
    ("    if (round < P_GWO_R) gold_w = std::min(gold_w, P_GWO / 100.0);  // o129",
     "    if (round < P_GWO_R) gold_w = std::min(gold_w, (s.hp_far ? P_FAR_GWO : P_GWO) / 100.0);  // o129; o92 farguard: far maps keep the b35 weight"),
    ("o125_holdlate o129_goldopen45\\n\");", "o125_holdlate o129_goldopen45 o92_farguard\\n\");  // stdout marker"),
])
with open(os.path.join(src, 'params.h'), 'a') as f:
    f.write("#ifndef P_FAR_INC\n#define P_FAR_INC 100   // o92 farguard: incoming % on far maps (hp_far), 100 = b35\n#endif\n"
            "#ifndef P_FAR_GWO\n#define P_FAR_GWO 100   // o92 farguard: opening gold weight % on far maps, 100 = b35\n#endif\n")
print("o92 applied to", src)

# heavy.py MAIN : print [heavy] r<round> <sec-at-80k?> used=<fuel> for every turn over 80k (run with unlimited fuel)
import sys
p=sys.argv[1]; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:50],s.count(a)); s=s.replace(a,b)
rep("        g_mode = \"?\";\n        g_farm = \"-\";\n","        g_mode = \"?\";\n        g_farm = \"-\";\n        const unsigned long long hv_f0 = bc::fuel_remaining();\n")
rep("        log_status(s);\n        bc::end_turn();","        log_status(s);\n        { const unsigned long long used = hv_f0 - bc::fuel_remaining(); if (used > 80000) std::printf(\"[heavy] r%d used=%llu mode=%s farm=%s ready=%d\\n\", (int)bc::round_number(), used, g_mode, g_farm, (int)s.ready); }\n        bc::end_turn();")
open(p,'w',newline='').write(s)

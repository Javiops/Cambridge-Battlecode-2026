# o82_farnochase.py SRCDIR (far-maps thread; NOT EXACT: a decision change on far maps before r400, judge by strength).
# Online far (V20, 40 games, r150-400) we walk 126 rounds per team that end in a champion fight, the rival 81, for the same
# number of fight rounds (25 vs 26): we go after fights from further away. The local bench does not reproduce it (b35 vs
# rTop1: 92 vs 101), so only the PC can judge it. On maps with spawn path >= 60 (g_tpc_path, draft byte 29), before
# P_FNC_R1, the team-fight chase layer (P_CHASE / P_TF_GUARD: go after a hurt or recalling rival within 7) is off.
# No fuel read, no printf, no start-up work.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    if (P_TEAM_FIGHT && hpr >= 0.5f && cassi_issac::pair_ok(s, me) && !on_spawn && !awake_camp_near && !foes.empty() && fuel_ok(12000)) {""",
"""    if (P_TEAM_FIGHT && hpr >= 0.5f && cassi_issac::pair_ok(s, me) && !on_spawn && !awake_camp_near && !foes.empty() && fuel_ok(12000) &&
        !(P_FNC_R1 && g_tpc_path >= 60 && round < P_FNC_R1)) {  // o82 farnochase""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
s+='\n// o82 farnochase (far-maps thread): no team-fight chase on far maps before this round (0 = off)\n#ifndef P_FNC_R1\n#define P_FNC_R1 400\n#endif\n'
open(p,'w',newline='').write(s)

# fuelfit c01 (pelea, CAMBIA decisiones): in the fight step (from FP(9) "fight" to FP(10)) at most P_FS_PATHS path
# searches (step_towards past its cheap early exits) per turn; a further call returns false as if no path were found
# (callers fall back as they already do). Heavy fight turns chained flee + engage + chase + front_line searches.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {\n","""int g_fs_paths = -1;  // fuelfit c01: path searches so far in this turn's fight step (-1 = not in the fight step)
bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {
""")
rep("""    if (!me.can_move() && !(use_dash && s.dash_slot >= 0)) return false;
""","""    if (!me.can_move() && !(use_dash && s.dash_slot >= 0)) return false;
    if (g_fs_paths >= 0 && g_fs_paths++ >= P_FS_PATHS) return false;  // fuelfit c01
""")
rep('    FP(9, "fight");\n','    FP(9, "fight");\n    g_fs_paths = 0;  // fuelfit c01\n')
rep('    FP(10, "recall/tribute");\n','    FP(10, "recall/tribute");\n    g_fs_paths = -1;  // fuelfit c01\n')
rep("            play_turn(s);\n","            play_turn(s);\n            g_fs_paths = -1;  // fuelfit c01: a return from the fight step ends it\n")
open(p,'w',newline='').write(s)
q=d+'/params.h'; t=open(q,newline='').read().rstrip('\n')+'\n#ifndef P_FS_PATHS\n#define P_FS_PATHS 1  // fuelfit c01: path searches allowed per turn in the fight step\n#endif\n'
open(q,'w',newline='').write(t)

# fuelfit o53 (farm section, DECISION CHANGE, not exact): off the mainland, isle_escape plans at most once every
# P_ISLE_EVERY (10) rounds. Each plan costs two field searches (one of them exhaustive, ~30k on 100x100) plus the landing
# scan; on ambush/islands a champion that cannot land re-planned every turn (6 consecutive turns of 160-216k in the
# profile). isle_continue (walking to the edge, waiting for the dash) is untouched. Effect to measure by strength.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""#include <cambc.h>
""","""#include <cambc.h>
#ifndef P_ISLE_EVERY
#define P_ISLE_EVERY 10  // fuelfit o53: rounds between two isle_escape plans
#endif
""")
rep("""    if (mainland.is_set(pos) || static_cast<int>(bc::round_number()) < g_isle_off) return false;""",
"""    if (mainland.is_set(pos) || static_cast<int>(bc::round_number()) < g_isle_off) return false;
    static int isle_last_plan = -1000;  // fuelfit o53: one plan every P_ISLE_EVERY rounds
    if (static_cast<int>(bc::round_number()) - isle_last_plan < P_ISLE_EVERY) return false;
    isle_last_plan = static_cast<int>(bc::round_number());""")
open(p,'w',newline='').write(s)
print("o53 ok")

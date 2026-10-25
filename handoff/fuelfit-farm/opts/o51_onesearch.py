# fuelfit o51 (farm section, DECISION CHANGE, not exact): one path search per turn in step_towards.
# When the first field (walls = blocked + volley ring, roots = goals, stop at pos) does not reach us, the code ran a
# second, full search through the champions ("corridor jammed", walls = static walls + camp tiles); when we are truly
# cut off that search is exhaustive (~30k fuel on 100x100) and then isle_escape adds two more. Now the second search is
# skipped: the turn falls through to isle_escape (o53 limits it) / fallback() exactly as it did when the second search
# also failed. Effect to measure by strength (pair/vstat vs the base on the same 80 games, then 240 more): a champion
# behind a wall of champions waits for the way to clear instead of planning through them.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    if (!ok_field) {  // corridor jammed by champions: plan through them
        ok_field = attempt([&] {""","""    if (!ok_field && !P_ONE_SEARCH) {  // corridor jammed by champions: plan through them (fuelfit o51: off)
        ok_field = attempt([&] {""")
rep("""#include <cambc.h>
""","""#include <cambc.h>
#ifndef P_ONE_SEARCH
#define P_ONE_SEARCH 1  // fuelfit o51: step_towards runs one field search per turn (no jammed-corridor re-search)
#endif
""")
open(p,'w',newline='').write(s)
print("o51 ok")

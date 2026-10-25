# o59_unreach.py SRCDIR (fuelfit, farm thread; EXACT). choose_target's walk() prices a group with no walking path by
# unreach(), which asked s.mp_dashholes.is_empty() (an SDK call, ~200 fuel) for EVERY unreachable group, twice per call
# (the o52 K-cut pass and the scoring pass): 11-17k per choose_target on islands (46 groups, most unreachable from the
# spawn), 7k on big_world (first-turn profile of b16). s.mp_dashholes only changes inside mp_find_dashholes, so one
# query per call gives the same answer.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    auto unreach = [&](int d) {
        if (s.dash_slot < 0 || s.mp_dashholes.is_empty()) return -1;
        return d * 2 + 10;
    };""","""    int dh_empty = -1;  // fuelfit o59: s.mp_dashholes.is_empty() asked once per call (it was one SDK call per unreachable group)
    auto unreach = [&](int d) {
        if (s.dash_slot < 0) return -1;
        if (dh_empty < 0) dh_empty = s.mp_dashholes.is_empty() ? 1 : 0;
        if (dh_empty) return -1;
        return d * 2 + 10;
    };""")
open(p,'w',newline='').write(s); print('o59 ok')

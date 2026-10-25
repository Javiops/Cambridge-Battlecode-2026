# o79_holdgems.py SRCDIR (farm thread; NOT EXACT: a decision change, judge by strength; over b35, independent of o70).
# choose_target doubles the score (P_HOLD 200) of every gem group within P_HOLD_R 6 of the "hold" altar (a middle altar,
# |dm - de| <= 4, with >= 2 gem groups around it), whatever the group is worth, and the current target keeps x1.25
# (P_STICK). Printed every candidate and pick of b35 + o70 on the_farm vs rD (e70dbg): in 32 of 67 decisions (r20-300)
# the pick was the 2-wolf group next to that altar (8 gems, 120 gold) and a single-elk group 11 tiles away (29 gems, 90
# gold) had a higher raw value / rounds; the x2.5 decided. The team farmed the 8-gem group all game and never approached
# the elk. Clean capture counts (cmpwin2.py): the top 10 take single-elk groups 1.4-1.9 times per game per 150-round
# window, we 0.5-0.8, and we spend 4.1-4.6 captures per game on gold-only clusters (top 10 2.0). The hold bonus is the
# territory idea (fight around the middle altar); o79 keeps it for groups worth holding: the x2 applies only when the
# group's gems >= P_HOLD_MIN (15: elk and wolf+gem groups; 4-8 gem groups go back to their plain value).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""        if (held) score *= P_HOLD / 100.0;""",
"""        if (held && g.gems >= P_HOLD_MIN) score *= P_HOLD / 100.0;  // o79: only groups worth holding (the 8-gem wolf pair next to the altar beat a 29-gem elk by this x2 alone)""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_HOLD_MIN
#define P_HOLD_MIN 15  // o79: the hold-altar x2 (P_HOLD) applies only to groups with at least this many gems
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)

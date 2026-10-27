# o78_feasible.py SRCDIR (farm thread; NOT EXACT: a decision change, judge by strength; companion of o70, apply after it
# over b35). choose_target PRICES an impossible fight instead of rejecting it: squad_needed caps "needed" at P_NEED_CAP
# (2) even when no team of 5 could afford the group, and the cost model only adds heal cycles for the hp lost. The base
# survived because the inflated incoming (o70's finding) kept such groups too expensive; with the calibrated incoming
# (P_INC_PCT 50) they come back into range. Measured on starvation (80x80, all gems in one 4-elk group of 240 strength
# plus two monoliths): b35 + o70 loses 3/4 (b35 4/4) with 15-29 deaths per game, 9-26 of them next to camps (b35: 0-3),
# 71 of them at that 4-elk group and its gem cluster. Monsters focus ONE champion (o70's measurement), so a group of
# strength S kills the focused champion in mhp / S rounds whatever the team size: v1 of this gate (grow the team until
# S / team is survivable) sent 4-5 champions to the same group from r75 and they died the same way (far 45/56 vs 48).
# v2: a group whose full strength would kill the focused member in less than P_TTD rounds is not an option unless the
# whole roster clears it before that; it comes back as max hp grows (shards). The top 10 never take a group of 180+
# strength before r300 (0.03 per game, 40 games) and nor do we; the groups both take are 60-120 (1-2 elks), which
# pass at mhp 1200 (20 / 10 rounds). Monolith trips (mono_only) and the jackpot team keep their own rules.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""        int needed = free_reward ? 1 : squad_needed(g.hp, g.str, dps, afford);
        bool mono_go = s.mono_only && g.monolith;  // its damage stays, so the team wears it down over several trips""",
"""        int needed = free_reward ? 1 : squad_needed(g.hp, g.str, dps, afford);
        bool mono_go = s.mono_only && g.monolith;  // its damage stays, so the team wears it down over several trips
        if (P_TTD > 0 && !free_reward && !mono_go && !jack_go && g.str > 0) {  // o78: monsters focus one champion; a group that kills him in < P_TTD rounds is no option unless the roster clears it first
            const double ttd = mhp * (P_FEAS_PCT / 100.0) / g.str;
            if (ttd < P_TTD && g.hp / (dps * s.roster) > ttd) continue;
        }""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_TTD
#define P_TTD 10  // o78: a camp group is an option only if its full strength leaves the focused champion this many rounds to live (0 = off)
#endif
#ifndef P_FEAS_PCT
#define P_FEAS_PCT 100  // o78: share of max hp the focused champion may lose in that time
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)

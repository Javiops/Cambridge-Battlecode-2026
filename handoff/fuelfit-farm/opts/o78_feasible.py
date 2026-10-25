# o78_feasible.py SRCDIR (farm thread; NOT EXACT: a decision change, judge by strength; companion of o70, apply after it
# over b35). choose_target PRICES an impossible fight instead of rejecting it: squad_needed caps "needed" at P_NEED_CAP
# (2) even when no team of 5 could afford the group, and the cost model only adds heal cycles for the hp lost. The
# base survived because the inflated incoming (o70's finding) made such groups too expensive; with the calibrated
# incoming (P_INC_PCT 50) they come back into range. Measured on starvation (80x80, all gems in one 4-elk group of
# 240 strength plus two monoliths): b35 + o70 loses 3/4 (b35 4/4) with 15-29 deaths per game, 9-26 of them next to
# camps (b35: 0-3), 71 of them at that 4-elk group and its gem cluster: two champions arrive, take 120 a round each
# and die in 10 rounds, before the retreat rules can act. The gate: with `team` champions a group is only an option
# if its FULL strength (every camp alive at the start) leaves each member at least P_TTD rounds to live
# (mhp x P_FEAS_PCT% / (str / team)), or the clear is over before that. Otherwise the team grows to the smallest size
# that passes; if the whole roster cannot, the group is skipped (needed > roster). Monolith trips (mono_only) and the
# jackpot team keep their own rules.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""        int needed = free_reward ? 1 : squad_needed(g.hp, g.str, dps, afford);
        bool mono_go = s.mono_only && g.monolith;  // its damage stays, so the team wears it down over several trips""",
"""        int needed = free_reward ? 1 : squad_needed(g.hp, g.str, dps, afford);
        bool mono_go = s.mono_only && g.monolith;  // its damage stays, so the team wears it down over several trips
        if (P_TTD > 0 && !free_reward && !mono_go && !jack_go && g.str > 0) {  // o78: the team must survive the group's full burst for P_TTD rounds (or clear it first); squad_needed's cap turned "impossible" into "a pair"
            const double hp_ok = mhp * (P_FEAS_PCT / 100.0);
            int t = std::max(1, needed);
            for (; t <= s.roster; ++t) {
                const double ttd = hp_ok / (g.str / t);            // rounds each member lasts under str / t a round
                if (ttd >= P_TTD || g.hp / (dps * t) <= ttd) break;  // long enough to retreat, or the group dies first
            }
            needed = t;  // > roster: skipped below
        }""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_TTD
#define P_TTD 20  // o78: a camp group is an option only if its full strength leaves each team member this many rounds to live (0 = off)
#endif
#ifndef P_FEAS_PCT
#define P_FEAS_PCT 100  // o78: share of max hp a member may lose in that time
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)

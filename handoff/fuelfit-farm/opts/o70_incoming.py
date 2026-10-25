# o70_incoming.py SRCDIR (farm thread; NOT EXACT: a decision change, judge by strength; over b35 = b32 + o74; the anchors
# are the same in b29/b32). The camp cost model of choose_target charges a group's FULL strength for the whole clear
# (incoming = str x t_clear / team, then (incoming / mhp) heal cycles); squad_needed does the same. Measured on 133 elk
# and 343 wolf episodes of b35 (near 80 panel, rounds <= 300, replay hp of every participant from first approach to
# capture): the hp actually lost is 0.46 (elk) / 0.63 (wolf) of str x duration (top 10: 0.34 / 0.47) because camps die
# one by one and monsters focus one champion; deaths 0.05 / 0.03 per episode. The inflated incoming hits the strong
# groups hardest (elk 60 strength per camp): the model charges a 2-elk group 4800 damage -> 4.8 heal cycles -> ~280
# rounds, so wolves and gem clusters outscore elk groups and we take 1.11 elk+gem groups per game in r150-300 where
# the top 10 take 2.27 (same total captures, 80 vs 106 group gems in that window; our elk episodes, when we go, are
# as fast and as safe as theirs). P_INC_PCT scales the modelled incoming damage (100 = old model).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""        double incoming = g.str * t_clear / team;""",
"""        double incoming = g.str * t_clear / team * (P_INC_PCT / 100.0);  // o70: camps die one by one, monsters focus one champion (measured 0.46-0.63 of str x duration)""")
rep("""        if (hp_g * str_g / (dps * n * (focus ? 1 : n)) <= afford) return std::min(n, P_NEED_CAP);""",
"""        if (hp_g * str_g * (P_INC_PCT / 100.0) / (dps * n * (focus ? 1 : n)) <= afford) return std::min(n, P_NEED_CAP);  // o70: same calibration""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_INC_PCT
#define P_INC_PCT 50  // o70: modelled incoming camp damage as % of strength x clear time (measured 46-63%; 100 = old model)
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)

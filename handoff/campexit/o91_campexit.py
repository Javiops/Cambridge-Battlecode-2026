# o91 campexit (main.cpp farm, fight-camp step). Why (10-25 fb35dbg, 312 local games): 90 of 660 deaths r20-300 (14%)
# have no rival within 5 tiles: the camp kills us. Once a group is damaged ("engaged") fight-camp skips the squad_needed
# admission, so a lone champion keeps hitting an elk group it cannot clear (boss_battle: HoR, then Marcella, each alone
# on 2 x 2400 hp elks, -120 hp a round). Observed x = (time to clear) / (time to die) at the first fight-camp round:
# x<0.5 dies 1%, 0.5-1 3%, 1-2 7%, 2-4 11%, 4+ 10%. Rule: alone at the camp (no ally within 3 of the group centre),
# measured over the last 2-3 rounds of this stay, if x >= P_CX/10: drop the group for P_CX_BAD rounds and step home.
# No fuel read; no loop beyond the existing live-camp list; one vis_champions call (allies_near) only when x qualifies.
import sys
d=sys.argv[1]; v=int(sys.argv[2]) if len(sys.argv)>2 else 10
hpv=int(sys.argv[3]) if len(sys.argv)>3 else 100  # only below this hp %
def edit(fn, pairs):
    p=d+'/'+fn; s=open(p,newline='').read()
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:60],s.count(a)); s=s.replace(a,b)
    open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read(); nl='\r\n' if '\r\n' in s else '\n'
s=s.rstrip('\r\n')+nl+nl.join(["","// o91 campexit: leave a damaged camp we cannot clear alone; threshold x10 (0 = off), drop rounds",
"#ifndef P_CX","#define P_CX %d"%v,"#endif","#ifndef P_CX_BAD","#define P_CX_BAD 40","#endif","#ifndef P_CX_HP","#define P_CX_HP %d"%hpv,"#endif"])+nl
open(p,'w',newline='').write(s)
edit('main.cpp',[
("""    int cf_noact = 0;  // islefix-v1: consecutive fight-camp turns with no step and no attack
""","""    int cf_noact = 0;  // islefix-v1: consecutive fight-camp turns with no step and no attack
    int cx_t = -1, cx_r = -1000;  // o91 campexit: target / round / my hp / group hp at the oldest kept fight-camp turn
    double cx_hp = 0, cx_rem = 0;
    int cx_t2 = -1, cx_r2 = -1000;  // ... and at the newest one
    double cx_hp2 = 0, cx_rem2 = 0;
"""),
("""        g_farm = "fight-camp";
        s.wait_group = -1;
""","""        g_farm = "fight-camp";
        s.wait_group = -1;
#if P_CX
        if (engaged && !mono_go) {
            if (s.cx_t == s.target && round - s.cx_r >= 2 && round - s.cx_r <= 4) {
                const double dr = round - s.cx_r, dH = (s.cx_hp - hp) / dr, dG = (s.cx_rem - rem) / dr;
                if (dH > 0 && hp > 0 && hp * 100.0 < P_CX_HP * mhp) {
                    const double t_die = hp / dH, t_clear = dG > 0 ? rem / dG : 1e9;
                    if (t_clear * 10.0 >= P_CX * t_die && allies_near(s, me, g.center, 3) == 0) {
                        g_farm = "lose-camp";
                        g.bad_until = round + P_CX_BAD;
                        s.cx_t = s.cx_t2 = -1;
                        drop_target(s);
                        if (me.can_move()) step_towards(s, me, s.my_spawn, true);
                        return;
                    }
                }
            }
            if (s.cx_t2 != s.target || round - s.cx_r2 > 2) { s.cx_t = s.target; s.cx_r = round; s.cx_hp = hp; s.cx_rem = rem; }
            else if (round - s.cx_r > 3) { s.cx_t = s.cx_t2; s.cx_r = s.cx_r2; s.cx_hp = s.cx_hp2; s.cx_rem = s.cx_rem2; }
            s.cx_t2 = s.target; s.cx_r2 = round; s.cx_hp2 = hp; s.cx_rem2 = rem;
        }
#endif
""")])

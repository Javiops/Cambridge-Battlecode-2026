# fuelfit o72 (changes the start, judged by strength): kvvl played from round 1 on small maps (init left >= 40k of the
# 186k first-turn budget) and from round 2 on most mid maps; b15-b27 play from round 2 (<= 14 groups) or 3 (more), one
# round later than kvvl on contest, fragment, hooks, eight, starfish, gold_rush, gemfight (online c19: near maps 37 ->
# 32/81 wins, -41 gems/game, worst on exactly these maps). Start-up and first-turn fuel measured with unlimited fuel
# (kidbg, 26 near maps): init 97k (fragment) .. 256k (boss_battle); first playing turn 33-90k.
# Rule of the map (groups, tiles), no fuel read:
#   A: groups <= 12 and tiles <= 1000 (fragment 97k+33k, packs 117k+36k, hooks 119k+38k, elkring 121k+59k <= 180k):
#      play in round 1 right after the start-up.
#   B: groups <= 19 and tiles <= 1000, not A (gold_rush 132k, gemfight 142k; reverse_spiral 138k, 14 groups): the idle
#      round's work (reverse fields, 28-43k) runs in turn 1 after the start-up (fits 186k) and play starts in round 2.
#   else as before: round 2 when <= 14 groups, round 3 otherwise.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:60],s.count(a)); s=s.replace(a,b)
rep("        s.play_from = s.groups.size() <= INIT_SMALL ? 2 : 3;\n",
"""        {
            const long tiles = static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height());
            const std::size_t ng = s.groups.size();
            if (ng <= 12 && tiles <= 1000) s.play_from = 1;  // fuelfit o72 class A
            else if (ng <= 19 && tiles <= 1000) { s.play_from = 2; s.wait_in_r1 = true; }  // class B
            else s.play_from = ng <= INIT_SMALL ? 2 : 3;
        }
""")
rep("    int play_from = 2;  // fuelfit o08 v3: first playing round (a rule of the map)\n",
    "    int play_from = 2;  // fuelfit o08 v3: first playing round (a rule of the map)\n    bool wait_in_r1 = false;  // fuelfit o72: the idle round's work runs in turn 1 (class B maps)\n")
rep("""        s.ready = true;  // never retry a failing init every turn
        g_mode = "init-done";  // fuelfit o07: the champion plays from the next turn (fixed, whatever the map)
        return;
    }
""","""        s.ready = true;  // never retry a failing init every turn
        if (s.play_from > 1) {  // fuelfit o72: class A maps play on in this turn
            if (s.wait_in_r1) init_wait(s);  // class B: the idle round's work, here
            g_mode = "init-done";  // fuelfit o07: the champion plays from the next turn (fixed, whatever the map)
            return;
        }
    }
""")
open(p,'w',newline='').write(s)

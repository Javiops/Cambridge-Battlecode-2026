# fuelfit o08 v2 (replaces o07's init(); v1 was a priced step machine that idled 3-5 rounds: a14 +0.64 -> +0.25).
# (measured with unlimited fuel over 52 games x 4 champions, rounded up): map 56k (boards, altars, spawn,
# camp_groups), one camp group 8k, walking fields 31k, dash-hole scan 14k, roles + shop 56k. A turn runs steps while
# they fit its budget: 176k on round 1 (the engine gives quantum*2 - 14k = 186k), 76k later (86k). The schedule thus
# depends only on the round and the group count, never on the fuel left. Also restart-safe: if the engine ever
# restarts the program mid-game (a turn over the fuel), start-up fits the 86k turns too. [boot] marks each program
# start (one per champion; more = a restart).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
i=s.index("constexpr std::size_t INIT_GROUPS_TURN = 30, INIT_SMALL_MAP = 20;")
j=s.index("    return true;\n}\n",i)+len("    return true;\n}\n")
s=s[:i]+"""// fuelfit o08 v3: the whole start-up runs on the first turn, at once. No action is issued while starting up, so if it does
// not fit the first turn's budget (186k) the engine finishes it in the next round and nothing can diverge. The first
// playing round is a fixed rule of the map: round 2 when the map has at most INIT_SMALL groups (start-up measured
// <= 143k there, unlimited fuel, 52 games), round 3 otherwise (up to 252k on 31 groups: it always ends inside round 2).
// Measured start-up: map 32k p50 / 56k max, groups ~5k each all included, paths 20k / 31k, roles + shop 50k / 56k,
// dash holes 7k / 13k. [boot] marks each program start (one per champion; more = a restart, see README).
constexpr std::size_t INIT_SMALL = 14;
bool init(State& s, bc::champion& me) {
    if (s.init_stage == 0) {
        init_map(s, me);
        init_groups(s, 1000000);
        init_paths(s);
        if (false) mp_game_plan(s);  // only the rules that need it: off = v52 games
        init_roles(s, me);
        if (s.dash_slot >= 0) mp_find_dashholes(s);  // mapplan_game.h rule 5 (o06: one bitboard pass)
        s.play_from = s.groups.size() <= INIT_SMALL ? 2 : 3;
        s.init_stage = 5;
    }
    return true;
}
"""+s[j:]
rep("    std::size_t init_gi = 0;\n","    std::size_t init_gi = 0;\n    int play_from = 2;  // fuelfit o08 v3: first playing round (a rule of the map)\n")
rep("""        s.ready = true;  // never retry a failing init every turn
        g_mode = "init-done";  // fuelfit o07: the champion plays from the next turn (fixed, whatever the map)
        return;
    }""","""        s.ready = true;  // never retry a failing init every turn
        g_mode = "init-done";  // fuelfit o07: the champion plays from the next turn (fixed, whatever the map)
        return;
    }
    if (static_cast<int>(bc::round_number()) < s.play_from) {  // fuelfit o08 v3: a fixed idle round on big maps
        g_mode = "init-wait";
        init_wait(s);
        return;
    }""")
rep("bool init(State& s, bc::champion& me) {","void init_wait(State& s);  // fuelfit o08 v3: optional work for the idle round (o47)\nbool init(State& s, bc::champion& me) {")

rep("[[noreturn]] void run_game() {\n    State s;\n","[[noreturn]] void run_game() {\n    std::printf(\"[boot] r%d\\n\", static_cast<int>(bc::round_number()));  // fuelfit o08: one per champion; a second one = restart\n    State s;\n")
open(p,'w',newline='').write(s)

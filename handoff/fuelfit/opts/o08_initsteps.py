# fuelfit o08 (start-up as a step machine, replaces o07's init()): every start-up step has a fixed worst-case price
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
s=s[:i]+"""constexpr long INIT_C_MAP = 56000, INIT_C_GROUP = 8000, INIT_C_PATHS = 31000, INIT_C_DASH = 14000, INIT_C_ROLES = 56000;
constexpr long INIT_BUDGET_R1 = 176000, INIT_BUDGET = 76000;
bool init(State& s, bc::champion& me) {
    long left = static_cast<int>(bc::round_number()) == 1 ? INIT_BUDGET_R1 : INIT_BUDGET;
    if (s.init_stage == 0) {  // boards, altars, spawn, the group list
        init_map(s, me);
        left -= INIT_C_MAP;
        s.init_stage = 1;
    }
    if (s.init_stage == 1) {  // camp groups, as many as fit
        const long n = left / INIT_C_GROUP;
        if (n <= 0) return false;
        const std::size_t before = s.init_gi;
        if (!init_groups(s, static_cast<std::size_t>(n))) return false;
        left -= static_cast<long>(s.init_gi - before) * INIT_C_GROUP;
        s.init_stage = 2;
    }
    if (s.init_stage == 2) {  // walking fields
        if (left < INIT_C_PATHS) return false;
        init_paths(s);
        if (false) mp_game_plan(s);  // only the rules that need it: off = v52 games
        left -= INIT_C_PATHS;
        s.init_stage = 3;
    }
    if (s.init_stage == 3) {  // roles and the shop plan (sets the dash slot)
        if (left < INIT_C_ROLES) return false;
        init_roles(s, me);
        left -= INIT_C_ROLES;
        s.init_stage = 4;
    }
    if (s.init_stage == 4) {  // dash holes (mapplan_game.h rule 5; o06: one bitboard pass)
        if (left < INIT_C_DASH) return false;
        if (s.dash_slot >= 0) mp_find_dashholes(s);
        s.init_stage = 5;
    }
    return true;
}
"""+s[j:]
rep("[[noreturn]] void run_game() {\n    State s;\n","[[noreturn]] void run_game() {\n    std::printf(\"[boot] r%d\\n\", static_cast<int>(bc::round_number()));  // fuelfit o08: one per champion; a second one = restart\n    State s;\n")
open(p,'w',newline='').write(s)

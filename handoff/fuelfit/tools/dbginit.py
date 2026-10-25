# dbginit.py MAIN : [dbgI] fuel per start-up step (run with unlimited fuel), [dbgG] per-group max/mean
import sys
p=sys.argv[1]; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:50],s.count(a)); s=s.replace(a,b)
rep("bool init(State& s, bc::champion& me) {\n","unsigned long long g_f0;\n#define DF(tag) { unsigned long long f_ = bc::fuel_remaining(); std::printf(\"[dbgI] r%d %s %llu\\n\", (int)bc::round_number(), tag, g_f0 - f_); g_f0 = bc::fuel_remaining(); }\nbool init(State& s, bc::champion& me) {\n    g_f0 = bc::fuel_remaining();\n")
rep("        init_map(s, me);\n        if (!init_groups(s, INIT_GROUPS_TURN)) return false;","        init_map(s, me);\n        DF(\"map\");\n        if (!init_groups(s, 1000)) return false;\n        DF(\"groups\");")
rep("        init_paths(s);\n        if (false) mp_game_plan(s);  // only the rules that need it: off = v52 games\n        init_roles(s, me);\n        if (s.dash_slot >= 0) mp_find_dashholes(s);","        init_paths(s);\n        DF(\"paths\");\n        if (false) mp_game_plan(s);  // only the rules that need it: off = v52 games\n        init_roles(s, me);\n        DF(\"roles+shop\");\n        if (s.dash_slot >= 0) mp_find_dashholes(s);\n        DF(\"dash\");")
rep("    std::size_t done = 0;\n    for (; s.init_gi < s.raw_groups.size() && done < quota; ++s.init_gi, ++done) {","    std::size_t done = 0;\n    unsigned long long gmax = 0, gsum = 0; int gn = 0;\n    for (; s.init_gi < s.raw_groups.size() && done < quota; ++s.init_gi, ++done) {\n        struct GE { unsigned long long f0, &mx, &sm; int &n; ~GE() { unsigned long long c = f0 - bc::fuel_remaining(); if (c > mx) mx = c; sm += c; ++n; } } ge{bc::fuel_remaining(), gmax, gsum, gn};")
rep("    if (s.init_gi < s.raw_groups.size() && s.groups.size() < MAX_GROUPS) return false;","    std::printf(\"[dbgG] n %d max %llu mean %llu raw %zu\\n\", gn, gmax, gn ? gsum / gn : 0ULL, s.raw_groups.size());\n    if (s.init_gi < s.raw_groups.size() && s.groups.size() < MAX_GROUPS) return false;")
rep("    attempt([&] {\n        s.raw_groups = bc::map::camp_groups();\n        return true;\n    });","    { unsigned long long cf0 = bc::fuel_remaining(); attempt([&] {\n        s.raw_groups = bc::map::camp_groups();\n        return true;\n    }); std::printf(\"[dbgC] camp_groups %llu\\n\", cf0 - bc::fuel_remaining()); }")
open(p,'w',newline='').write(s)

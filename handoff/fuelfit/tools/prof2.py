# prof2.py MAIN: turn/section fuel accounting for a kvvl-based main.cpp (prints [usec] [ush] [ut1] [ugh] like ungate.py)
import sys
p=sys.argv[1]; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:60],s.count(a)); s=s.replace(a,b)
rep("#define FP(i, name) ((void)0)","""std::uint64_t g_sf0 = 0, g_tf0 = 0; int g_sec = 0, g_turn = 0; double g_tsec[30]; double g_secS[30], g_secM[30], g_secB[30]; int g_hist[40]; int g_bigN = 0; int g_sh[14][40]; double g_t1[3][30];
inline void pf_mark(int i) { const std::uint64_t f = bc::fuel_remaining(); if (g_sec >= 0 && g_sec < 30) g_tsec[g_sec] += double(g_sf0) - double(f); g_sf0 = f; g_sec = i; }
inline void pf_turn_start() { ++g_turn; g_sec = 0; g_sf0 = g_tf0 = bc::fuel_remaining(); for (int k = 0; k < 30; ++k) g_tsec[k] = 0; }
inline void pf_turn_end() {
    pf_mark(14);
    const double used = double(g_tf0) - double(bc::fuel_remaining());
    int b = static_cast<int>(used / 5000); if (b < 0) b = 0; if (b > 39) b = 39; if (g_turn > 1) ++g_hist[b];
    for (int k = 0; k < 14; ++k) { g_secS[k] += g_tsec[k]; if (g_tsec[k] > g_secM[k]) g_secM[k] = g_tsec[k]; }
    if (g_turn >= 1 && g_turn <= 3) for (int k = 0; k < 30; ++k) g_t1[g_turn - 1][k] = g_tsec[k];
    if (g_turn > 1) for (int k = 0; k < 14; ++k) { int b_ = static_cast<int>(g_tsec[k] / 2500); if (b_ < 0) b_ = 0; if (b_ > 39) b_ = 39; ++g_sh[k][b_]; }
    if (used > 92000 && g_turn > 1) { ++g_bigN; for (int k = 0; k < 14; ++k) g_secB[k] += g_tsec[k]; }
    const int rr = static_cast<int>(bc::round_number());
    if (rr % 100 == 0) {
        std::printf("[usec] r%d %d %d", rr, g_turn, g_bigN); for (int k = 0; k < 14; ++k) std::printf(" %.0f:%.0f:%.0f", g_secS[k], g_secB[k], g_secM[k]); std::printf("\\n");
        for (int k = 0; k < 14; ++k) { std::printf("[ush] %d", k); for (int b_ = 0; b_ < 40; ++b_) std::printf(" %d", g_sh[k][b_]); std::printf("\\n"); }
        for (int t_ = 0; t_ < 3; ++t_) { std::printf("[ut1] %d", t_ + 1); for (int k = 0; k < 30; ++k) std::printf(" %.0f", g_t1[t_][k]); std::printf("\\n"); }
        std::printf("[ugh] r%d", rr); for (int k = 0; k < 40; ++k) std::printf(" %d", g_hist[k]); std::printf("\\n");
    }
}
#define FP(i, name) pf_mark(i)""")
rep("        g_mode = \"?\";\n        g_farm = \"-\";\n","        g_mode = \"?\";\n        g_farm = \"-\";\n        pf_turn_start();\n")
rep("        log_status(s);\n        bc::end_turn();","        log_status(s);\n        pf_turn_end();\n        bc::end_turn();")
open(p,'w',newline='').write(s)

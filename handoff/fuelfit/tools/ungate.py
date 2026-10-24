# ungate.py MAIN: fuel_ok always lets work through (real fuel guard 3000 only) + per-turn / per-site / per-section real costs
import sys
p=sys.argv[1]; s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
a=s.index("inline bool fuel_okc(std::uint64_t need, std::uint64_t charge) {"); b=s.index("inline bool fuel_ok(std::uint64_t need) { return fuel_okc(need, 0); }")
s=s[:a]+"""int g_pl = 0; std::uint64_t g_pf = 0; int g_pturn = -1; double g_pS[9000], g_pQ[9000], g_pM[9000]; int g_pN[9000];
inline void pp_point() {
    if (g_pl && g_pturn == g_dm_turn) { const double c = double(g_pf) - double(bc::fuel_remaining()); g_pS[g_pl] += c; g_pQ[g_pl] += c * c; if (c > g_pM[g_pl]) g_pM[g_pl] = c; ++g_pN[g_pl]; }
    g_pl = 0;
}
inline bool fuel_okc_at(std::uint64_t, std::uint64_t, int line) {
    pp_point();
    if (bc::fuel_remaining() <= 3000) { ++g_dm_emerg; return false; }
    if (line > 0 && line < 9000) { g_pl = line; g_pf = bc::fuel_remaining(); g_pturn = g_dm_turn; }
    return true;
}
#define fuel_okc(n, c) fuel_okc_at((n), (c), __LINE__ + (__builtin_strstr(__FILE__, "main.cpp") ? 0 : (__builtin_strstr(__FILE__, "heart_of_ruin") ? 6000 : __builtin_strstr(__FILE__, "utility") ? 7000 : 8000)))
#define fuel_ok(n) fuel_okc(n, 0)
"""+s[b+len("inline bool fuel_ok(std::uint64_t need) { return fuel_okc(need, 0); }"):]
rep("""inline void dm_mark(int i) {
    g_dm += dm_cost(g_dm_sec);
    g_dm_sec = i;
}""","""inline void pp_point();
std::uint64_t g_sf0 = 0, g_tf0 = 0; double g_tsec[30]; double g_secS[30], g_secM[30], g_secB[30]; int g_secN[30]; int g_hist[40]; int g_big = 0; int g_bigN = 0; int g_sh[14][40]; double g_t1[3][14];
inline void dm_mark(int i) {
    pp_point();
    g_dm += dm_cost(g_dm_sec);
    const std::uint64_t f = bc::fuel_remaining();
    if (g_dm_sec >= 0 && g_dm_sec < 30) { const double c = double(g_sf0) - double(f); g_tsec[g_dm_sec] += c; }
    g_sf0 = f;
    g_dm_sec = i;
}
inline void dm_turn_end() {
    dm_mark(14);
    double tot = 0; for (int k = 0; k < 14; ++k) { tot += g_tsec[k]; g_secS[k] += g_tsec[k]; if (g_tsec[k] > g_secM[k]) g_secM[k] = g_tsec[k]; ++g_secN[k]; }
    const double used = double(g_tf0) - double(bc::fuel_remaining());
    int b = static_cast<int>(used / 5000); if (b < 0) b = 0; if (b > 39) b = 39; if (g_dm_turn > 1) ++g_hist[b];
    if (g_dm_turn >= 1 && g_dm_turn <= 3) for (int k = 0; k < 14; ++k) g_t1[g_dm_turn - 1][k] = g_tsec[k];
    if (g_dm_turn > 1) for (int k = 0; k < 14; ++k) { int b_ = static_cast<int>(g_tsec[k] / 2500); if (b_ < 0) b_ = 0; if (b_ > 39) b_ = 39; ++g_sh[k][b_]; }
    if (used > 92000 && g_dm_turn > 1) { ++g_bigN; for (int k = 0; k < 14; ++k) g_secB[k] += g_tsec[k]; }
    if (used > 70000 && g_dm_turn > 1 && g_big < 40) { ++g_big; std::printf("[big] t%d used %.0f nf %d |", g_dm_turn, used, g_dm_nf); for (int k = 0; k < 14; ++k) std::printf(" %.0f", g_tsec[k]); std::printf("\\n"); }
    for (int k = 0; k < 30; ++k) g_tsec[k] = 0;
}""")
rep("inline void dm_turn_start() { g_dm = 0; g_dm_sec = 0; ++g_dm_turn; }","inline void dm_turn_start() { g_dm = 0; g_dm_sec = 0; ++g_dm_turn; g_sf0 = g_tf0 = bc::fuel_remaining(); }")
rep("        log_status(s);\n        bc::end_turn();","""        log_status(s);
        dm_turn_end();
        { const int rr = static_cast<int>(bc::round_number()); if (rr % 100 == 0) {
            std::printf("[usec] r%d %d %d", rr, g_dm_turn, g_bigN); for (int k = 0; k < 14; ++k) std::printf(" %.0f:%.0f:%.0f", g_secS[k], g_secB[k], g_secM[k]); std::printf("\\n");
            for (int k = 0; k < 14; ++k) { std::printf("[ush] %d", k); for (int b_ = 0; b_ < 40; ++b_) std::printf(" %d", g_sh[k][b_]); std::printf("\\n"); }
            for (int t_ = 0; t_ < 3; ++t_) { std::printf("[ut1] %d", t_ + 1); for (int k = 0; k < 14; ++k) std::printf(" %.0f", g_t1[t_][k]); std::printf("\\n"); }
            std::printf("[ugh] r%d", rr); for (int k = 0; k < 40; ++k) std::printf(" %d", g_hist[k]); std::printf("\\n");
            std::printf("[ugp] r%d", rr); for (int k = 0; k < 9000; ++k) if (g_pN[k]) std::printf(" %d:%d:%.0f:%.0f:%.0f", k, g_pN[k], g_pS[k], g_pQ[k], g_pM[k]); std::printf("\\n"); } }
        bc::end_turn();""")
open(p,'w').write(s)

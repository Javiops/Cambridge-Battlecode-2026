# prof.py SRCDIR : profiling build (not exact): per-turn fuel per FP section and per FP_SCOPE / added scope,
# histograms in 1k buckets, printed as [zp] lines every 100 rounds (cumulative).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a,s.count(a)); s=s.replace(a,b)
rep('#define FP(i, name) ((void)0)\n#define FP_SCOPE(i, name) ((void)0)\n','''double g_zT[64]; double g_zM[64]; int g_zH[64][201]; int g_zSec = 0; std::uint64_t g_zF = 0; int g_zTurns = 0;
inline void zp_mark(int i) { const std::uint64_t f = bc::fuel_remaining(); if (g_zSec > 0) g_zT[g_zSec] += double(g_zF) - double(f); g_zSec = i; g_zF = f; }
struct ZScope { int id; std::uint64_t f0; explicit ZScope(int i) : id(i), f0(bc::fuel_remaining()) {} ~ZScope() { g_zT[id] += double(f0) - double(bc::fuel_remaining()); } };
#define FP(i, name) zp_mark(i)
#define FP_SCOPE(i, name) ZScope zp_scope_{i}
inline void zp_turn_end(int round) {
    zp_mark(0);
    ++g_zTurns;
    if (g_zTurns > 1) for (int k = 0; k < 64; ++k) { if (g_zT[k] > g_zM[k]) g_zM[k] = g_zT[k]; int b = static_cast<int>(g_zT[k] / 1000); if (b < 0) b = 0; if (b > 200) b = 200; ++g_zH[k][b]; }
    for (int k = 0; k < 64; ++k) g_zT[k] = 0;
    if (round % 100 == 0) for (int k = 0; k < 64; ++k) { if (g_zM[k] <= 0) continue; std::printf("[zp] %d %d %.0f", round, k, g_zM[k]); for (int b = 0; b <= 200; ++b) if (g_zH[k][b]) std::printf(" %d:%d", b, g_zH[k][b]); std::printf("\\n"); }
}
''')
rep('std::vector<bc::camp> near_camps(State& s, vec2 pos) {\n','std::vector<bc::camp> near_camps(State& s, vec2 pos) {\n    FP_SCOPE(30, "near_camps");\n')
rep('bool br_plan(State& s, vec2 pos, int round) {\n','bool br_plan(State& s, vec2 pos, int round) {\n    FP_SCOPE(34, "br_plan");\n')
rep('std::optional<vec2> br_legacy_best_altar(State& s, vec2 pos, int round) {\n','std::optional<vec2> br_legacy_best_altar(State& s, vec2 pos, int round) {\n    FP_SCOPE(35, "br_legacy");\n')
rep('    if (P_MG && s.mono_guard) {  // monoguard-v1: see params.h\n','    if (P_MG && s.mono_guard) {  // monoguard-v1: see params.h\n        FP_SCOPE(31, "monoguard");\n')
rep('    bool awake_camp_near = false;\n','    bool awake_camp_near = false;\n    const std::uint64_t zp_a0 = bc::fuel_remaining();\n')
rep('    int nearest_foe = 99;\n    for (auto& f : foes) nearest_foe = std::min(nearest_foe, f.d);\n    bool in_combat','    g_zT[32] += double(zp_a0) - double(bc::fuel_remaining());\n    int nearest_foe = 99;\n    for (auto& f : foes) nearest_foe = std::min(nearest_foe, f.d);\n    bool in_combat')
rep('            r5_altar_lock(s);\n','            { FP_SCOPE(33, "altar_lock"); r5_altar_lock(s); }\n')
rep('''        log_status(s);
        bc::end_turn();''','''        log_status(s);
        zp_turn_end(static_cast<int>(bc::round_number()));
        bc::end_turn();''')
for i,a in [(44,'    if (PR.backhome && round - s.trib_end <= 2'),(45,'    if (!capture_before_recall && rsafe && home > 6 && want_recall) {'),(46,'    // 5. Bank gems.\n'),(47,'    // P_GROUP_R: keep the ball together.'),(48,'    if (PR.campfoe && !on_spawn && !foes.empty()) {')]:
    rep(a,'    FP(%d, "sub");\n'%i+a)
open(p,'w').write(s)

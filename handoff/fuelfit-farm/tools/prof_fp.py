# prof_fp.py SRCDIR: analysis build only. FP/FP_SCOPE record fuel per play_turn section (0 pre .. 13 log) and per
# function scope (15 choose_target .. 33 farm); every 50 rounds prints histograms ([fph] k b0..b39, 2.5k buckets) and
# prints one [fpt] line for every turn whose farm section >= 25k or total >= 90k. For --fuel-quantum 2000000 runs.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a,s.count(a)); s=s.replace(a,b)
rep('#define FP(i, name) ((void)0)\n#define FP_SCOPE(i, name) ((void)0)','''std::uint64_t g_fp_last = 0; int g_fp_sec = -1; double g_fp_cost[40]; int g_fp_hist[40][40]; double g_fp_tot = 0; int g_fp_turns = 0;
inline void fp_mark(int i) { const std::uint64_t f = bc::fuel_remaining(); if (g_fp_sec >= 0 && g_fp_last >= f) g_fp_cost[g_fp_sec] += double(g_fp_last - f); g_fp_sec = i; g_fp_last = f; }
struct FpScope { int id; std::uint64_t f0; explicit FpScope(int i) : id(i), f0(bc::fuel_remaining()) {} ~FpScope() { const std::uint64_t f = bc::fuel_remaining(); if (f0 >= f) g_fp_cost[id] += double(f0 - f); } };
#define FP(i, name) fp_mark(i)
#define FP_SCOPE(i, name) FpScope fp_scope_##i(i)
inline void fp_turn_begin() { for (int k = 0; k < 40; ++k) g_fp_cost[k] = 0; g_fp_sec = -1; g_fp_tot = double(bc::fuel_remaining()); fp_mark(0); }
inline void fp_turn_end(const char* name) {
    fp_mark(-1);
    const double tot = g_fp_tot - double(bc::fuel_remaining());
    const int round = static_cast<int>(bc::round_number());
    if (round > 1) {
        ++g_fp_turns;
        auto bk = [](double c) { int b = int(c / 2500.0); return b < 0 ? 0 : b > 39 ? 39 : b; };
        ++g_fp_hist[39][bk(tot)];
        for (int k = 0; k < 39; ++k) ++g_fp_hist[k][bk(g_fp_cost[k])];
        if (g_fp_cost[11] >= 25000 || tot >= 90000) {
            std::printf("[fpt] r%d %s tot=%.0f", round, name, tot);
            for (int k = 0; k < 39; ++k) if (g_fp_cost[k] >= 2500) std::printf(" %d=%.0f", k, g_fp_cost[k]);
            std::printf("\\n");
        }
    }
    if (round % 50 == 0 || round == 2) {
        std::printf("[fpn] %d\\n", g_fp_turns);
        for (int k = 0; k < 40; ++k) {
            bool any = false; for (int b = 1; b < 40; ++b) any |= g_fp_hist[k][b] > 0;
            if (!any && k != 39) continue;
            std::printf("[fph] %d", k); for (int b = 0; b < 40; ++b) std::printf(" %d", g_fp_hist[k][b]); std::printf("\\n");
        }
    }
}''')
rep('''        g_mode = "?";
        g_farm = "-";
        try {''','''        g_mode = "?";
        g_farm = "-";
        fp_turn_begin();
        try {''')
rep('        log_status(s);\n        bc::end_turn();','        log_status(s);\n        fp_turn_end(s.name.c_str());\n        bc::end_turn();')
rep('''bool engage_camp_e4(State& s, bc::champion& me, const bc::camp* tgt, const std::vector<const bc::camp*>& live, Group& g) {
    const int range = me.attack_range();''','''bool engage_camp_e4(State& s, bc::champion& me, const bc::camp* tgt, const std::vector<const bc::camp*>& live, Group& g) {
    FP_SCOPE(30, "engage_camp");
    const int range = me.attack_range();''')
rep('''void refresh_groups(State& s, int round) {
    auto sm = read_sm();''','''void refresh_groups(State& s, int round) {
    FP_SCOPE(31, "refresh_groups");
    auto sm = read_sm();''')
rep('''std::vector<bc::camp> near_camps(State& s, vec2 pos) {
    // Cheap replacement''','''std::vector<bc::camp> near_camps(State& s, vec2 pos) {
    FP_SCOPE(32, "near_camps");
    // Cheap replacement''')
rep('''void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {
    vec2 pos = me.position();''','''void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {
    FP_SCOPE(33, "farm");
    vec2 pos = me.position();''')
rep('''double my_dps(State& s, bc::champion& me) {''','''double my_dps(State& s, bc::champion& me) {
    FP_SCOPE(34, "my_dps");''')
rep('''int allies_near(State& s, bc::champion& me, vec2 at, int radius) {''','''int allies_near(State& s, bc::champion& me, vec2 at, int radius) {
    FP_SCOPE(35, "allies_near");''')
open(p,'w',newline='').write(s); print('prof ok')

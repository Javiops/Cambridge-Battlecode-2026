struct Params {
    int tribute_gems = P_TRIBUTE_GEMS;   // walk to an altar once carrying this many gems
    int recall_pct = P_RECALL_PCT;       // recall below this % health when safe
    int flee_pct = P_FLEE_PCT;           // run for spawn below this % health
    int late_round = P_LATE_ROUND;       // after this round, tribute any gems at all
};
Params P;

constexpr std::uint64_t FUEL_RESERVE = 6000;
constexpr int SPELL_RANGE = 4;   // every targeted/ground spell in the roster is range 4
constexpr int CAMP_RANGE = 3;    // all monsters attack at range 3
constexpr int MAX_GROUPS = 250;  // claim bytes store group index + 1

inline int X(vec2 v) { return static_cast<int>(v.dot(vec2(1, 0))); }
inline int Y(vec2 v) { return static_cast<int>(v.dot(vec2(0, 1))); }
inline int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }
inline bool fuel_ok(std::uint64_t need) { return bc::fuel_remaining() > need + FUEL_RESERVE; }

// Every SDK action can throw (cambc::error, out_of_range, ...). An uncaught
// exception restarts the C++ guest and loses all state, so wrap everything.
// Diagnostics go to stdout, which the runner saves as team-x.stdout.
int g_errors = 0;
const char* g_mode = "start";
const char* g_farm = "-";
// P_TRACE: one line per turn for behaviour studies (trace builds only; off in every bot we upload).
#ifndef P_TRACE
#define P_TRACE 0
#endif
int g_nf = 99, g_nfoes = 0, g_nal = 0, g_rew = 0, g_tlive = -1;

// 2026-10-16 behaviour fixes (thread "fix teammate behaviours"). Each is a switch; 0 = the teammate's bot as sent.
// P_CAPHOME N: a reward of our camp is waiting within N steps and we want to go home (hurt / asked to heal):
//   step onto it and recall there, so the 5-round capture and the recall run together, instead of recalling or
//   walking away and leaving the loot (also: no tribute walk while that reward waits for us).
#ifndef P_CAPHOME
#define P_CAPHOME 0
#endif
#ifndef P_CAPHOME_RSAFE   // 1: only when a recall would start anyway (nobody near enough to interrupt it)
#define P_CAPHOME_RSAFE 0
#endif
#ifndef P_CAPHOME_TRIB    // 1: no tribute walk while our reward waits within 2; 2: only that part (no cap-home recall)
#define P_CAPHOME_TRIB 1
#endif
// P_CAMPFOE N: an enemy champion within 3 (or within N after it hit us in the last 2 rounds) means a fight: hit
//   it if the fight is favourable and it is in reach, else back off; never spend the turn on a camp.
#ifndef P_CAMPFOE
#define P_CAMPFOE 0
#endif
// P_NOCHASE2 1: a low-health or channelling foe is only engaged within attack range + 1 (no walking after it),
//   unless it carries P_CHASE_GEMS+ gems (the user's doctrine: chase only a big bag).
#ifndef P_NOCHASE2
#define P_NOCHASE2 0
#endif
// P_NEEDHEAL R: waiting for a squad (rally) or for health that no recall will bring (need-heal with 80%+ health or
//   no safe recall) lasts at most R rounds: the camp is dropped for a while and another one is chosen.
#ifndef P_NEEDHEAL
#define P_NEEDHEAL 0
#endif
// P_KITEALLY R: kiting steps toward the nearest ally within R tiles (60 a tile past 2), not only toward allies
//   already within 6.
#ifndef P_KITEALLY
#define P_KITEALLY 0
#endif
// P_BACKHOME M: right after a tribute at a contested altar (distances to both spawns within M), recall home if
//   there is no camp to take or the next camp is contested too and (we saw a foe in the last 20 rounds or are
//   below 80% health); walk home if a recall is not safe.
#ifndef P_BACKHOME
#define P_BACKHOME 0
#endif
// P_CAPPRIO R: who stays on a reward (the gold and gems go to whoever stands on it): Stellar first (if she claims it
//   within R tiles or stands next to it), then the other casters, then Ren, the tanks last; ties by distance, then
//   roster index. A lower-priority champion keeps the capture going until the higher one is on the tiles, then steps off.
#ifndef P_CAPPRIO
#define P_CAPPRIO 0
#endif
// P_TWINFARM R: Issac farms Cassi's camp (they share one life; online-like local games: 33 of 82 pair deaths came
//   with Issac alone 9+ tiles from Cassi). With no camp claimed by Cassi he walks back to within R of her.
// P_NOLEAVE N (the user, 2026-10-16 17:17): a reward of our camp waiting within N tiles is never left behind, except
//   when staying kills us (the foes' ready damage on our tile, three rounds of it, reaches our health, or we are under
//   15%) or an ally with more right to the gold takes it (P_ONE_CAP / P_CAPPRIO). We step on, shoot whoever is in
//   range without moving, and recall on the tiles when we wanted to go home (capture and recall together).
#ifndef P_NOLEAVE
#define P_NOLEAVE 0
#endif
// P_CACHE 1 (with P_NOLEAVE): a tank that sees a waiting reward posts it in shared bytes 5-6 (group + 1, then 251 +
//   (round / 16) & 3) instead of taking it; casters and Ren read it as a free reward for 32 rounds and go for it.
#ifndef P_CACHE
#define P_CACHE 0
#endif
// P_OUTNUM R (the user, 2026-10-16 17:20: corners, Tavi 4 tiles from 3 foes with her allies far away walks toward
//   them and dies): outnumbered by 2+ within R (allies that are recalling do not count), we back off instead of
//   kiting, farming or walking on, unless the foe in reach dies to our next hit.
#ifndef P_OUTNUM
#define P_OUTNUM 0
#endif
// P_DPSFARM 1 (the user, 2026-10-16 17:56: "farming is meant for the DPS to collect and nobody else"): only the DPS
//   (casters and Ren) capture camps. A tank never chooses its own camp while a DPS has one claimed: it goes to the
//   DPS's camp nearest to it (Issac to Cassi's), helps kill it and steps off the reward; a reward a tank is left
//   with is posted in the cache (P_CACHE bytes) for the DPS. DPS do not count tank claims when choosing.
#ifndef P_DPSFARM
#define P_DPSFARM 0
#endif
#ifndef P_TWINFARM
#define P_TWINFARM 0
#endif
// P_AVOIDFIRST 1 (GA genome b672ef97f6, the user 18:11 idea 6): decide to back off before taking the front line.
#ifndef P_AVOIDFIRST
#define P_AVOIDFIRST 0
#endif
#include "profile.h"

void note_error(const char* what) {
    ++g_errors;
    if (g_errors <= 8 || g_errors % 500 == 0) {
        std::printf("[err #%d] %s\n", g_errors, what);
        std::fflush(stdout);
    }
}

template <class F>
bool attempt(F&& f) {
    try {
        return f();
    } catch (const std::exception& e) {
        note_error(e.what());
        return false;
    } catch (...) {
        note_error("unknown exception");
        return false;
    }
}

// P_FUELPROF: fuel used per section of the turn, and which section was running when a turn ran out of fuel (the
// bot is then suspended and resumes in the next round, so the round number changes between two marks).
// Profiling builds only: printed from debug_block, so run them without --release.
#ifndef P_FUELPROF
#define P_FUELPROF 0
#endif
// P_FUELGUARD 1: stop turns running out of fuel. A turn that runs out is suspended and the rest of it plays in the
// champion's next turn, on last round's data, so a champion loses one or two rounds each time (online: ~10 a game,
// 60+ on lanes). With unlimited fuel the decisions are the same as without it (154 of 154 map sides identical):
//  - cheaper, same result: one search instead of one per altar at start-up; walking distances to the camp groups
//    kept while we stand still (capturing); allies out of vision skipped before position() throws in
//    other_captures; the reward-evacuation check reads the camps near us instead of every visible camp;
//  - when the turn cannot pay for it: start-up finishes over the first turns (the champion waits on its spawn), an
//    optional camp re-choice waits for a later turn, log lines are skipped, and the low-fuel fallback step is a
//    plain greedy step instead of one more path search.
#ifndef P_FUELGUARD
#define P_FUELGUARD 0
#endif
#if P_FUELPROF
struct FuelSec { const char* name = "?"; unsigned long long sum = 0, n = 0, mx = 0, over = 0; };
FuelSec g_fp[32];
int g_fp_sec = 0, g_fp_round = -1;
unsigned long long g_fp_last = 0;
bool g_fp_over = false;
unsigned long long g_fp_turn[32];
int g_fp_where = -1;
void fp_mark(int next, const char* name) {
    int r = static_cast<int>(bc::round_number());
    unsigned long long f = bc::fuel_remaining();
    FuelSec& c = g_fp[g_fp_sec];
    if (!g_fp_over && r != g_fp_round) { ++c.over; g_fp_over = true; g_fp_where = g_fp_sec; }
    if (!g_fp_over && g_fp_last >= f) { c.sum += g_fp_last - f; ++c.n; c.mx = std::max(c.mx, g_fp_last - f); g_fp_turn[g_fp_sec] += g_fp_last - f; }
    g_fp_sec = next; g_fp[next].name = name; g_fp_last = f;
}
void fp_begin() {
    g_fp_round = static_cast<int>(bc::round_number()); g_fp_over = false; g_fp_where = -1;
    for (auto& t : g_fp_turn) t = 0;
    g_fp_sec = 0; g_fp[0].name = "pre-sweep"; g_fp_last = bc::fuel_remaining();
}
#define FP(i, name) fp_mark(i, name)
struct FpScope {  // a function's own section; the caller's section resumes when it returns
    int prev; const char* pname;
    FpScope(int i, const char* name) : prev(g_fp_sec), pname(g_fp[g_fp_sec].name) { fp_mark(i, name); }
    ~FpScope() { fp_mark(prev, pname); }
};
#define FP_SCOPE(i, name) FpScope fp_scope_{i, name}
#else
#define FP(i, name) ((void)0)
#define FP_SCOPE(i, name) ((void)0)
#endif

std::string norm(const std::string& s) {
    std::string o;
    for (char c : s) {
        if (c >= 'A' && c <= 'Z') o += static_cast<char>(c - 'A' + 'a');
        else if (c >= 'a' && c <= 'z') o += c;
    }
    return o;
}


// profile.h - the game plan in one place (2026-10-16, after the user's "strong, flexible architecture" note).
//
// Every behaviour switch the plan depends on (who captures, who escorts, how camps are dropped, when to fight)
// lives in one Profile. The compile-time P_* values are the default profile; with P_PROFILE 1 the bot reads the
// map's features once at start-up, picks a map family from them (never a map name) and applies that family's
// overrides from kFamilies. Adapting to the meta late in the competition = edit kFamilies / pick_family.
// Code reads PR.<field>, never the P_* macro.

#ifndef P_PROFILE
#define P_PROFILE 0   // 0: one profile for every map (the P_* values); 1: per-family overrides below
#endif
#ifndef P_PROF_RUSH
#define P_PROF_RUSH 22   // spawn centre to enemy spawn centre (tiles) at or under which a map is a rush map
#endif
#ifndef P_PROF_LONG
#define P_PROF_LONG 40   // at or over this a map is a long farm map
#endif
#ifndef P_TWIN
#define P_TWIN 0
#endif

struct Profile {
    // farming: who captures and how a waiting reward is handled
    int capprio;       // P_CAPPRIO
    int dpsfarm;       // P_DPSFARM
    int cache;         // P_CACHE
    int noleave;       // P_NOLEAVE
    int twinfarm;      // P_TWINFARM
    int caphome, caphome_rsafe, caphome_trib;  // P_CAPHOME*
    int needheal;      // P_NEEDHEAL
    int backhome;      // P_BACKHOME
    // fighting
    int campfoe;       // P_CAMPFOE
    int nochase2;      // P_NOCHASE2
    int kiteally;      // P_KITEALLY
    int outnum;        // P_OUTNUM
    int twin;          // P_TWIN
};

inline Profile default_profile() {
    return {P_CAPPRIO, P_DPSFARM, P_CACHE,    P_NOLEAVE,  P_TWINFARM, P_CAPHOME, P_CAPHOME_RSAFE, P_CAPHOME_TRIB,
            P_NEEDHEAL, P_BACKHOME, P_CAMPFOE, P_NOCHASE2, P_KITEALLY, P_OUTNUM,  P_TWIN};
}

inline Profile PR = default_profile();
inline const char* g_family = "default";

// What the plan is chosen from: measured on the map at start-up, so it works on maps we have never seen.
struct MapFeatures {
    int team_size = 0;
    int altars = 0;
    int camps = 0;        // camp groups
    int spawn_dist = 0;   // our spawn centre to theirs, in tiles
    int area = 0;
};

enum Family { FAM_RUSH, FAM_MID, FAM_LONG, FAM_COUNT };

// Per-family overrides: -1 keeps the default profile's value. All -1 today (one plan everywhere); fill a row
// when a switch is measured to help on that family only.
struct FamilyRow {
    const char* name;
    Profile over;
};
constexpr int K = -1;
inline const FamilyRow kFamilies[FAM_COUNT] = {
    {"rush", {K, K, K, K, K, K, K, K, K, K, K, K, K, K, K}},
    {"mid", {K, K, K, K, K, K, K, K, K, K, K, K, K, K, K}},
    {"long", {K, K, K, K, K, K, K, K, K, K, K, K, K, K, K}},
};

inline Family pick_family(const MapFeatures& f) {
    if (f.spawn_dist <= P_PROF_RUSH) return FAM_RUSH;
    if (f.spawn_dist >= P_PROF_LONG) return FAM_LONG;
    return FAM_MID;
}

inline void apply_profile(const MapFeatures& f) {
    Profile p = default_profile();
    Family fam = pick_family(f);
    if (P_PROFILE) {
        const int* o = reinterpret_cast<const int*>(&kFamilies[fam].over);
        int* d = reinterpret_cast<int*>(&p);
        for (std::size_t i = 0; i < sizeof(Profile) / sizeof(int); ++i)
            if (o[i] != K) d[i] = o[i];
    }
    PR = p;
    g_family = kFamilies[fam].name;
    std::printf("[profile] family=%s ts=%d altars=%d camps=%d spawn_dist=%d area=%d on=%d\n", g_family, f.team_size,
                f.altars, f.camps, f.spawn_dist, f.area, P_PROFILE);
}

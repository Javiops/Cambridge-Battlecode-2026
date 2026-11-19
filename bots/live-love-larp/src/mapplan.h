// mapplan.h - the map plan read from map features (new-maps thread, 2026-10-16).
//
// The eight maps the site added on 16 Oct fall outside de_rules.h (it knows the nine old maps by exact size, altars and
// walls), so they were played with the default plan. Here each rule is one P_MP_* field, chosen from features any map
// has (team size, altars, walls, size, spawn-to-spawn walking path), never from a map name, so it also covers maps we
// have never seen. P_MAPPLAN 0 = identical games to the base; each P_MP_* 0 turns its rule off.
#pragma once
#include <vector>

// Rule 1, draft. A map with 5 champions a side whose spawns are far apart (walking path > P_UNI_PATH) but whose gems can
// only be banked at a few altars (<= P_MP_ALTARS) is a fight map, not a farm map: both teams walk to the same altars, so
// they meet there (eight: 1 altar, stampede 2, pilgrimage and ambush 4; the old farm maps lanes 18 and monolith 6). The
// top 10 draft casters there (Cassi&Issac + Stellar in all 60 winning games); we drafted Vendetta, Varg, Cassi&Issac,
// Ryth, Tavi and won 1-84 on eight, 14-77 on pilgrimage, 24-67 on stampede, 25-65 on ambush online (16 Oct).
// 1 = the top-10 draft (Cassi&Issac, Stellar, Varg, Tavi, Ren); 2 = our fight-map draft (Ryth, Stellar, Prism, Ren, Tavi).
// Panel (5 specialists, both sides): site maps 125 -> 132 of 170 games (flips 10-3: stampede 5-2, pilgrimage 4-0, eight 1-0,
// ambush 0-1), sealed hold60 7-2, dev200 17-4; draft 2 was 9-2 on site maps but 5-10 on hold60.
// ...unless the map is so open that the teams need not meet (P_MP_OPEN: reachable tiles per champion on the map, both
// teams; ambush 756, the others it fires on 117-259). 0 = no cap.

struct MpDraftFeat {
    int ts = 0, altars = 0, walls = 0, w = 0, h = 0, path = -1, open = 0;
};

inline MpDraftFeat mp_draft_features() {
    MpDraftFeat f;
    attempt([&] { f.ts = static_cast<int>(bc::draft::team_size()); return true; });
    attempt([&] { f.altars = static_cast<int>(bc::map::altars().positions().size()); return true; });
    attempt([&] { f.walls = static_cast<int>(bc::map::walls().positions().size()); return true; });
    attempt([&] { f.w = static_cast<int>(bc::map::width()); f.h = static_cast<int>(bc::map::height()); return true; });
    attempt([&] {  // walking path between the spawn regions (native distance field: a manual BFS runs out of draft fuel)
        bc::bitboard block = bc::map::walls() | bc::map::holes() | bc::map::altars();
        bc::distance_field da;
        bc::bitboard va;
        da.compute(block, bc::map::spawn_region(bc::team::ally), va);
        int ab = 1 << 30;
        for (auto p : bc::map::spawn_region(bc::team::enemy).positions())
            if (va.is_set(p)) ab = std::min(ab, static_cast<int>(da.get(p)));
        if (ab < (1 << 30)) f.path = ab;
        f.open = static_cast<int>(va.positions().size());
        return true;
    });
    return f;
}

// far apart but few altars: the teams meet where they bank
inline bool mp_far_fight(const MpDraftFeat& f) {
    return f.ts >= P_MP_TS && f.path > P_UNI_PATH && f.altars <= P_MP_ALTARS;
}

inline std::vector<const char*> mp_draft(const MpDraftFeat& f) {
    if (!mp_far_fight(f)) return {};
    return {"cassi", "stellar", "varg", "tavi", "ren"};
    return {"ryth", "stellar", "prism", "ren", "tavi"};
}

inline bool g_mp_far = false;  // unused, kept: the same reason as State::fm_hold (main.cpp)

// mapplan_game.h - the in-game half of the map plan (mapplan.h): features that need the camp groups and the
// walking distances of init_paths (camp groups are not readable during the draft). Included after State.
#pragma once
#include <algorithm>
#include <vector>

inline int mp_median(std::vector<int> v) {
    if (v.empty()) return -1;
    std::sort(v.begin(), v.end());
    return v[v.size() / 2];
}

// Rule 2, far from home. Where the gem camps are a long walk from our spawn (median walking distance >= P_MP_FARHOME;
// ambush 73, rows 73, pilgrimage 82, expanse 64; the fight maps 14-42), every trip home costs a long walk back, so the
// top teams take a second camp before banking: on ambush they capture the 106-gem camp at r75 and the 72-gem camp next
// to it at r107, banking 106-120 a trip; we recalled after the first one, came back for it at r191 and banked 53 a trip.
// On those maps chain to a camp within P_MP_CHAIN_R while carrying fewer than P_MP_CHAIN gems, and carry up to
// P_MP_BAG with no enemy seen (rows already had chain 60 / bag 48 by name in de_rules; this is the same idea by feature).
#ifndef P_MP_FARHOME
#define P_MP_FARHOME 0
#endif
#ifndef P_MP_CHAIN
#define P_MP_CHAIN 60
#endif
#ifndef P_MP_CHAIN_R
#define P_MP_CHAIN_R 12
#endif
#ifndef P_MP_BAG
#define P_MP_BAG 48
#endif
inline bool mp_far_home(const State& s) { return P_MAPPLAN && P_MP_FARHOME && s.mp_home_d >= P_MP_FARHOME; }

// Rule 3, walk around awake camps. Monsters focus one champion, and an awake camp (an ally is fighting it) hits whoever
// walks within its range. On ambush the caster draft lost Cassi&Issac at r70 walking past the elks Stellar had woken, on
// the way to the gem cluster 5 tiles further: 48 camp deaths in 6 local games (34 before r300) vs 26 with the old draft.
// With P_MP_CAMPAVOID, a path to anything but that camp avoids the range of every damaged monster in sight (falls back
// to the plain path when that is blocked).
#ifndef P_MP_CAMPAVOID
#define P_MP_CAMPAVOID 0
#endif
inline bc::bitboard mp_awake_camp_zone(State& s, vec2 pos) {
    bc::bitboard z;
    attempt([&] {
        for (const auto& c : bc::vision::camps()) {
            if (c.health() <= 0 || c.strength() <= 0 || c.health() >= c.max_health()) continue;
            vec2 cp = c.position();
            if (dist(cp, pos) > 12) continue;
            if (s.target >= 0 && s.target < static_cast<int>(s.groups.size()) && s.groups[s.target].mask.is_set(cp)) continue;
            z.draw_chebyshev(cp, static_cast<float>(c.attack_range()) + 1.0f);
        }
        return true;
    });
    z.set(pos, false);
    return z;
}

// Called once, after init_paths. Fills s.mp_* from the map's features.
inline void mp_game_plan(State& s) {
    std::vector<int> bank, home;
    for (auto& g : s.groups) {
        if (g.gems <= 0 || g.monolith) continue;
        if (g.altar_pd >= 0) bank.push_back(g.altar_pd);
        if (g.spawn_pd >= 0) home.push_back(g.spawn_pd);
    }
    s.mp_bank_d = mp_median(bank);
    if (P_MP_FOCUS_FAR) {
        MpDraftFeat f = mp_draft_features();
        g_mp_far = mp_far_fight(f);
    }
    s.mp_home_d = mp_median(home);
#ifdef P_MPDEBUG
    std::printf("[mpgame] gem_groups=%zu bank_d=%d home_d=%d\n", bank.size(), s.mp_bank_d, s.mp_home_d);
#endif
}

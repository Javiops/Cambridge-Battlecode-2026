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

// Rule 5, dash over holes. A dash moves 2 tiles and may cross a hole (not a wall). Ambush has 1-tile hole lines inside
// its wall lines (row 37 x16-26 above the 106-gem camp, row 62, x72 ...): the walking field treats holes as walls, so
// Ren, Tavi, Issac and Vendetta walk around them (Varg and Ren went round via the bushes at x36-42, ~15 tiles more).
// With P_MP_DASHHOLE, a dash champion also plans with the crossable hole tiles open; when that route is at least
// P_MP_DASHHOLE tiles shorter than the walk and the dash cooldown is shorter than the saving, it walks that route,
// keeps the dash for the crossing and waits at the edge if the dash is not back yet.
#ifndef P_MP_DASHHOLE
#define P_MP_DASHHOLE 0
#endif
inline void mp_find_dashholes(State& s) {
    s.mp_hole_all = bc::map::holes();
    bc::bitboard bad = bc::map::walls() | s.mp_hole_all | bc::map::altars();
    attempt([&] {
        for (auto h : bc::map::holes().positions())
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    if (!dx && !dy) continue;
                    vec2 a = h - vec2(dx, dy), b = h + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(a) || !bc::map::is_in_bounds(b) || bad.is_set(a) || bad.is_set(b)) continue;
                    s.mp_dashholes.set(h);
                }
        return true;
    });
}
// 1 = moved (or dashed), -1 = wait at the hole edge for the dash, 0 = no gain: the caller walks as before.
inline int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos) {
    if (!s.visited.is_set(pos)) return 0;
    int here = s.df.get(pos);
    auto ab = me.abilities()[s.dash_slot];
    int cd = 99;
    attempt([&] { cd = ab.cooldown(); return true; });
    if (here - P_MP_DASHHOLE <= cd) return 0;  // the walk is as fast as waiting for the dash
    bool ok = attempt([&] {
        s.mp_hdf.compute_to(vblock & ~s.mp_dashholes, goals, s.dest, s.mp_hvis);
        return s.mp_hvis.is_set(pos);
    });
    if (!ok) return 0;
    int hh = s.mp_hdf.get(pos);
    if (hh > here - P_MP_DASHHOLE || hh <= cd) return 0;  // no crossing on the way, or it does not pay
    if (cd <= 0 && me.can_cast()) {  // dash across a hole tile next to us toward the goal
        std::optional<vec2> best;
        int bestd = hh - 1;
        for (int dx = -2; dx <= 2; ++dx)
            for (int dy = -2; dy <= 2; ++dy) {
                if (std::max(std::abs(dx), std::abs(dy)) < 2) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.mp_hvis.is_set(t)) continue;
                int d = s.mp_hdf.get(t);
                if (d >= bestd) continue;
                bool over = false;  // a crossable hole on a tile adjacent to both ends
                for (int mx = -1; mx <= 1 && !over; ++mx)
                    for (int my = -1; my <= 1 && !over; ++my) {
                        vec2 m = pos + vec2(mx, my);
                        if (std::max(std::abs(m.x - t.x), std::abs(m.y - t.y)) <= 1 && bc::map::is_in_bounds(m) && s.mp_dashholes.is_set(m)) over = true;
                    }
                if (over) { bestd = d; best = t; }
            }
        if (best && attempt([&] { return ab.use(*best); })) {
            pos = *best;
            if (me.can_move()) {
                std::vector<vec2> st;
                attempt([&] { st = s.mp_hdf.next_moves_from(pos); return true; });
                for (auto d : st)
                    if (!s.mp_hole_all.is_set(pos + d) && attempt([&] { return me.move(d); })) break;
            }
            return 1;
        }
    }
    if (!me.can_move()) return 0;
    std::vector<vec2> st;
    attempt([&] { st = s.mp_hdf.next_moves_from(pos); return true; });
    bool edge = false;
    for (auto d : st) {
        if (s.mp_hole_all.is_set(pos + d)) { edge = true; continue; }
        if (attempt([&] { return me.move(d); })) return 1;
    }
    return edge ? -1 : 0;
}

// Rule 6, keep the camp on a long walk. On ambush 3-4 camps score within 30% of each other (106-gem elks 0.38, 48-gem
// cluster 0.53 that drops to 0.16 once an ally claims it, 120-gem camp 0.29), and the target is re-chosen every 6 rounds
// with a 25% bonus for the current one, so as claims change a champion swaps camp mid-walk: Ren went 11 -> 8 -> 6 -> 1 ->
// 8 -> 11 and reached its first camp at r75 (r49 in a game where it kept camp 11). With P_MP_STICK, a target still
// P_MP_STICK_D or more tiles away keeps a P_MP_STICK % bonus instead.
#ifndef P_MP_STICK
#define P_MP_STICK 0
#endif
#ifndef P_MP_STICK_D
#define P_MP_STICK_D 15
#endif

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

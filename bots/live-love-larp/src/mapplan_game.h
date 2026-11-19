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

// Rule 3, walk around awake camps. Monsters focus one champion, and an awake camp (an ally is fighting it) hits whoever
// walks within its range. On ambush the caster draft lost Cassi&Issac at r70 walking past the elks Stellar had woken, on
// the way to the gem cluster 5 tiles further: 48 camp deaths in 6 local games (34 before r300) vs 26 with the old draft.
// With P_MP_CAMPAVOID, a path to anything but that camp avoids the range of every damaged monster in sight (falls back
// to the plain path when that is blocked).
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
inline void mp_find_dashholes(State& s) {
#if P_DHFUEL
    // t10draft-fx-v1: the scan cost ~2.6k fuel per hole with no fuel check; on hole-heavy maps (ambush, starfish,
    // islands, fracture, pilgrimage) every dash champion (HoR, Vesper, Vendetta) ran out of fuel in rounds 1-9 and the
    // whole start-up was retried each turn (local: 1.5 exhausted turns a game per dash champion, online mv-vesp 8.6 vs
    // 5.5). Now it is resumable: one hole at a time while fuel lasts, continued on later turns; a partial set only
    // means fewer planned crossings.
    if (s.dh_stage == 0) {
        s.mp_hole_all = bc::map::holes();
        s.dh_bad = bc::map::walls() | s.mp_hole_all | bc::map::altars();
        // fuelfit o06: a hole is crossable when, for some direction d, the tiles h-d and h+d are both in bounds and
        // free: free shifted by -d AND free shifted by +d, over the holes, for the four axes (16 shifts for the map).
        attempt([&] {
            const bc::bitboard free = ~s.dh_bad;
            const int dirs[4][2] = {{1, 0}, {0, 1}, {1, 1}, {1, -1}};
            for (auto& dd : dirs) {
                const bc::bitboard plus = free.shift_right(-dd[0]).shift_up(-dd[1]);
                const bc::bitboard minus = free.shift_right(dd[0]).shift_up(dd[1]);
                s.mp_dashholes |= s.mp_hole_all & plus & minus;
            }
            return true;
        });
        s.dh_stage = 2;
    }
    while (s.dh_stage == 1) {
        if (s.dh_next >= s.dh_list.size()) { s.dh_stage = 2; break; }
        if (!fuel_ok(P_DHFUEL_NEED)) return;
        vec2 h = s.dh_list[s.dh_next++];
        attempt([&] {
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    if (!dx && !dy) continue;
                    vec2 a = h - vec2(dx, dy), b = h + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(a) || !bc::map::is_in_bounds(b) || s.dh_bad.is_set(a) || s.dh_bad.is_set(b)) continue;
                    s.mp_dashholes.set(h);
                    return true;
                }
            return true;
        });
    }
#else
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
#endif
}
// 1 = moved (or dashed), -1 = wait at the hole edge for the dash, 0 = no gain: the caller walks as before.
inline int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos) {
    if (!s.visited.is_set(pos)) return 0;
    int here = s.df.get(pos);
    auto ab = me.abilities()[s.dash_slot];
    int cd = 99;
    attempt([&] { cd = ab.cooldown(); return true; });
    if (here - P_MP_DASHHOLE <= cd) return 0;  // the walk is as fast as waiting for the dash
    // fuelfit o43: the search stops at here - P_MP_DASHHOLE steps; farther means "no crossing on the way" below anyway
    const std::uint16_t hole_bound = static_cast<std::uint16_t>(here - P_MP_DASHHOLE);
    bool ok = attempt([&] {
        s.mp_hdf.compute_to(vblock & ~s.mp_dashholes, goals, s.dest, s.mp_hvis, hole_bound);
        return s.mp_hvis.is_set(pos);
    });
    if (!ok) return 0;
    int hh = s.mp_hdf.get(pos);
    if (hh > here - P_MP_DASHHOLE || hh <= cd) return 0;  // no crossing on the way, or it does not pay
#if P_HOLEFIX
    // holefix-v1: a hole route that makes no progress is dropped. The planned crossing is our own guess of the
    // engine's dash path rules; when the engine refuses it (Ren: "destination unreachable") or the dash does not
    // land across (Heart of Ruin), the champion walked to the hole edge and back for hundreds of rounds (fracture,
    // islands, starvation, yellow_brick_road: 43 stuck rounds a game over the site maps). If the hole-route
    // distance has not reached a new low for P_HOLEFIX rounds, plan by walking only for the next 150 rounds.
    {
        const int r = static_cast<int>(bc::round_number());
        if (r < s.hf_off_until) return 0;
        if (r - s.hf_last_r > 3 || hh < s.hf_best) {
            if (r - s.hf_last_r > 3 || hh < s.hf_best) s.hf_best_r = r;
            s.hf_best = hh;
        }
        s.hf_last_r = r;
        if (r - s.hf_best_r >= P_HOLEFIX) {
            s.hf_off_until = r + 150;
            return 0;
        }
    }
#endif
    if (cd <= 0 && me.can_cast()) {  // dash across a hole tile next to us toward the goal
        std::optional<vec2> best;
        int bestd = hh - 1;
        // fuelfit o42: 16 ring tiles x 3 imports + 9 hole tests each -> 2 bitboard exports + 1 field export per call;
        // s.mp_dashholes only grows inside mp_find_dashholes, one hole per s.dh_next step: re-exported when that moved.
        static BitSnap holes_s;
        static long holes_key = -1;
        const long key = static_cast<long>(s.dh_stage) * 1000000 + static_cast<long>(s.dh_next);
        if (holes_key != key) { holes_s.load(s.mp_dashholes); holes_key = key; }
        static BitSnap blk_s, hvis_s;
        static DistSnap hdf_s;
        blk_s.load(s.blocked);
        hvis_s.load(s.mp_hvis);
        hdf_s.load(s.mp_hdf);
        for (int dx = -2; dx <= 2; ++dx)
            for (int dy = -2; dy <= 2; ++dy) {
                if (std::max(std::abs(dx), std::abs(dy)) < 2) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || blk_s.is_set(t) || !hvis_s.is_set(t)) continue;
                int d = hdf_s.get(t);
                if (d >= bestd) continue;
                bool over = false;  // a crossable hole on a tile adjacent to both ends
                for (int mx = -1; mx <= 1 && !over; ++mx)
                    for (int my = -1; my <= 1 && !over; ++my) {
                        vec2 m = pos + vec2(mx, my);
                        if (std::max(std::abs(m.x - t.x), std::abs(m.y - t.y)) <= 1 && bc::map::is_in_bounds(m) && holes_s.is_set(m)) over = true;
                    }
                if (over) { bestd = d; best = t; }
            }
        if (best && attempt([&] { return dm_use(ab).use(*best); })) {
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

// Rule 9, the squad moves on to the next camp. The top teams on ambush capture the 106-gem camp at r73-77; the carrier
// goes home and the others walk 10 tiles to the 72-gem elks and take them at r96-111. v52 re-chooses alone every 6
// rounds and takes the 72 camp at r190-243. With P_MP_CHAINPLAN, on maps whose gem camps are P_MP_SPREAD_D+ from home,
// for P_MP_CHAIN_T rounds after a gem camp next to us was captured, a champion carrying no gems scores the gem camps
// within P_MP_CHAIN_N tiles of it at P_MP_CHAINPLAN % (all the non-carriers there see the same camp, so they go together).
inline bool mp_chain_next(const State& s, bc::champion& me, const Group& g, int i, int round) {
    if (true) return false;
    if (round - s.mp_last_r > P_MP_CHAIN_T || g.gems <= 0) return false;
    if (dist(g.center, s.groups[s.mp_last_g].center) > P_MP_CHAIN_N) return false;
    bool empty = false;
    attempt([&] { empty = me.gem_count() == 0; return true; });
    return empty;
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
    s.mp_home_d = mp_median(home);
}

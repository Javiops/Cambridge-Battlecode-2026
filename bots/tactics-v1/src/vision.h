#pragma once

#include "sdk_world.h"
#include <algorithm>
#include <array>
#include <optional>
#include <vector>

namespace tactics {

struct WardState {
    int attempt_round = -1, success_round = -1;
    std::vector<Pos> rejected;
};

inline cambc::vec2 ward_sdk(Pos p) {
    return {p.x, p.y};
}
inline Pos ward_pos(cambc::vec2 p) {
    return {p.x, p.y};
}
inline bool ward_blocked_phase(Phase p) {
    return p == Phase::Unassigned || p == Phase::Channel;
}
inline bool ward_local_bit(const std::vector<std::uint8_t> &bytes, int index) {
    return index >= 0 && index / 8 < static_cast<int>(bytes.size()) &&
           (bytes[index / 8] & (1u << (index % 8))) != 0;
}

inline Pos ward_future_waypoint(World &w, const Mission &mission) {
    const std::vector<std::uint16_t> *field = nullptr;
    if (mission.phase == Phase::Recover)
        field = &w.geo.home;
    else {
        for (std::size_t i = 0; i < w.geo.altars.size(); ++i)
            if (mission.target == w.geo.altars[i]) {
                field = &w.geo.altar_fields[i];
                break;
            }
        // A distance answer from a self-rooted cache does not establish this
        // target-rooted route. Geometry::walk owns that bounded cache entry.
        if (!field && !w.geo.blocked(mission.target) &&
            w.geo.walk(w.self.pos, mission.target) != unreachable) {
            const auto it = w.geo.route_cache.find(w.geo.index(mission.target));
            if (it != w.geo.route_cache.end())
                field = &it->second;
        }
    }
    Pos future = w.self.pos;
    if (!field || w.geo.at(*field, future) == unreachable)
        return future;
    const auto terrain = w.geo.static_blocked.export_linear_buffer();
    // A short static-route forecast; no per-neighbor host queries and no
    // assertion that future dynamic occupancy is already known to be empty.
    for (int step = 0; step < 6; ++step) {
        int best = w.geo.at(*field, future);
        Pos next = future;
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                Pos p{future.x + dx, future.y + dy};
                if (!w.geo.valid(p) || ward_local_bit(terrain, w.geo.index(p)))
                    continue;
                const int value = w.geo.at(*field, p);
                if (value < best) {
                    best = value;
                    next = p;
                }
            }
        if (next == future)
            break;
        future = next;
    }
    return future;
}

// The same actual engine masks evaluate retaining and replacing an observer.
// Natural sight excludes all wards, including this body's current remote one.
inline int ward_observer_score(const cambc::bitboard &mask, const cambc::bitboard &natural_now,
                               const cambc::bitboard &natural_future,
                               const cambc::bitboard &decision_tiles,
                               const cambc::bitboard &approach_tiles) {
    const int immediate = static_cast<int>((mask & ~natural_now & decision_tiles).count());
    const int persistent = static_cast<int>((mask & ~natural_future & decision_tiles).count());
    const int warning = static_cast<int>((mask & ~natural_future & approach_tiles).count());
    return 4 * immediate + 2 * persistent + warning;
}

// Four diverse legal anchors form an explicit bounded fallback. Geometry only
// proposes candidates; the actual shadowcast and retained old ward decide.
inline std::vector<Pos> ward_candidate_positions(const std::vector<Pos> &legal, Pos self,
                                                 Pos ahead) {
    int dx = (ahead.x > self.x) - (ahead.x < self.x), dy = (ahead.y > self.y) - (ahead.y < self.y);
    if (dx == 0 && dy == 0)
        dx = 1;
    const std::array<Pos, 4> offsets{{{dx, dy}, {-dy, dx}, {dy, -dx}, {-dx, -dy}}};
    std::vector<Pos> selected;
    for (auto offset : offsets) {
        const Pos desired{self.x + 2 * offset.x, self.y + 2 * offset.y};
        std::optional<Pos> best;
        int best_distance = 100000, best_axis = 100000;
        for (auto p : legal) {
            if (std::find(selected.begin(), selected.end(), p) != selected.end())
                continue;
            const int d = distance(p, desired),
                      axis = std::abs(p.x - desired.x) + std::abs(p.y - desired.y);
            if (!best || d < best_distance ||
                (d == best_distance &&
                 (axis < best_axis ||
                  (axis == best_axis && (p.y < best->y || (p.y == best->y && p.x < best->x)))))) {
                best = p;
                best_distance = d;
                best_axis = axis;
            }
        }
        if (best)
            selected.push_back(*best);
    }
    return selected;
}

inline std::optional<Action> ward_proposal(World &w, const Mission &mission, WardState &state) {
    const std::uint64_t start = cambc::fuel_remaining();
    if (!w.self.alive || w.self.stunned || w.self.channel != Channel::None ||
        ward_blocked_phase(mission.phase) || state.success_round == w.round || start < 45000 ||
        w.round != static_cast<int>(cambc::round_number()) ||
        w.me.restrictions().contains(cambc::buff_restrictions::ward) || w.me.ward_cooldown() > 0)
        return std::nullopt;
    // The arbiter admits this only after useful core actions are exhausted.
    // Setup itself costs fuel: budget it as well as the bounded native scores.
    const std::uint64_t floor = std::max<std::uint64_t>(16000, start - 40000);
    if (state.attempt_round != w.round) {
        state.attempt_round = w.round;
        state.rejected.clear();
    }
    const auto old_positions = w.me.ward_positions();
    if (old_positions.size() > 1)
        return std::nullopt; // Current rules: one ward/body.
    auto legal_mask = w.me.ward_placement_tiles();
    legal_mask &= ~(w.geo.static_blocked | cambc::vision::ward_tiles(cambc::team::ally));
    std::vector<Pos> legal;
    for (auto raw : legal_mask.positions()) {
        const Pos p = ward_pos(raw);
        if (std::find(state.rejected.begin(), state.rejected.end(), p) == state.rejected.end() &&
            std::find(old_positions.begin(), old_positions.end(), raw) == old_positions.end())
            legal.push_back(p);
    }
    if (legal.empty())
        return std::nullopt;
    const Pos future = ward_future_waypoint(w, mission);
    if (cambc::fuel_remaining() < floor)
        return std::nullopt;
    const bool departing = mission.phase == Phase::Recover || mission.phase == Phase::Escape;
    const Pos anchor = departing ? w.self.pos : future;
    cambc::bitboard decision_tiles, approach_tiles, inner;
    decision_tiles.draw_chebyshev(ward_sdk(w.self.pos), 3);
    decision_tiles.draw_chebyshev(ward_sdk(anchor), 4);
    approach_tiles.draw_chebyshev(ward_sdk(anchor), 6);
    inner.draw_chebyshev(ward_sdk(anchor), 2);
    approach_tiles &= ~inner;
    decision_tiles &= ~w.geo.static_blocked;
    approach_tiles &= ~w.geo.static_blocked;
    const auto natural_now = w.me.visible_tiles_from(ward_sdk(w.self.pos));
    const auto natural_future =
        future == w.self.pos ? natural_now : w.me.visible_tiles_from(ward_sdk(future));
    int retained = 0;
    for (auto p : old_positions) {
        if (cambc::fuel_remaining() < floor)
            return std::nullopt;
        retained =
            std::max(retained, ward_observer_score(cambc::ward::visible_tiles_from(p), natural_now,
                                                   natural_future, decision_tiles, approach_tiles));
    }
    Pos ahead = future;
    if (ahead == w.self.pos && w.geo.valid(mission.target))
        ahead = mission.target;
    const auto candidates = ward_candidate_positions(legal, w.self.pos, ahead);
    int best = retained;
    Pos placement{};
    for (auto p : candidates) {
        if (cambc::fuel_remaining() < floor)
            break;
        const int score =
            ward_observer_score(cambc::ward::visible_tiles_from(ward_sdk(p)), natural_now,
                                natural_future, decision_tiles, approach_tiles);
        if (score > best) {
            best = score;
            placement = p;
        }
    }
    if (placement.x < 0 || best <= retained + std::max(4, retained / 6))
        return std::nullopt;
    Action action;
    action.kind = Kind::Ward;
    action.at = placement;
    action.reason =
        departing ? "leave-persistent-mission-observer" : "improve-personal-mission-warning";
    return action;
}

inline void ward_after_action(const World &w, const Action &action, bool success,
                              WardState &state) {
    if (action.kind != Kind::Ward)
        return;
    if (state.attempt_round != w.round) {
        state.attempt_round = w.round;
        state.rejected.clear();
    }
    if (success)
        state.success_round = w.round;
    else if (std::find(state.rejected.begin(), state.rejected.end(), action.at) ==
             state.rejected.end())
        state.rejected.push_back(action.at);
}

} // namespace tactics

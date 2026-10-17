#pragma once

#include "sdk_world.h"
#include "strategic.h"
#include <algorithm>
#include <array>
#include <bit>
#include <optional>
#include <vector>

namespace tactics {

struct WardState {
    int attempt_round = -1, success_round = -1;
    std::vector<Pos> rejected;
    bool timing_known = false, terrain_timing_exact = false;
    int warning_slack = -1, holes = -1;
};
struct WardScoreByte {
    int index = 0;
    std::uint8_t decision = 0, approach = 0;
};
inline unsigned ward_interval_bits(int first, int last, int byte) {
    const int lo = std::max(first, byte * 8) - byte * 8;
    const int hi = std::min(last, byte * 8 + 7) - byte * 8;
    return lo <= hi ? ((0xffu << lo) & (0xffu >> (7 - hi))) : 0;
}
inline std::vector<WardScoreByte> ward_score_stencil(int width, int height, Pos self, Pos anchor,
                                                     const std::vector<std::uint8_t> &blocked) {
    std::vector<WardScoreByte> out;
    if (width <= 0 || height <= 0 || blocked.size() != unsigned((width * height + 7) / 8))
        return out;
    out.reserve(80);
    const int y0 = std::max(0, std::min(self.y - 3, anchor.y - 6));
    const int y1 = std::min(height - 1, std::max(self.y + 3, anchor.y + 6));
    const int x0 = std::max(0, std::min(self.x - 3, anchor.x - 6));
    const int x1 = std::min(width - 1, std::max(self.x + 3, anchor.x + 6));
    auto rectangle = [&](int y, int byte, Pos center, int radius) {
        if (std::abs(y - center.y) > radius)
            return 0u;
        const int first = y * width + std::max(0, center.x - radius);
        const int last = y * width + std::min(width - 1, center.x + radius);
        return ward_interval_bits(first, last, byte);
    };
    for (int y = y0; y <= y1; ++y)
        for (int byte = (y * width + x0) / 8; byte <= (y * width + x1) / 8; ++byte) {
            const unsigned legal = ~unsigned(blocked[byte]) & 0xffu;
            const unsigned decision =
                (rectangle(y, byte, self, 3) | rectangle(y, byte, anchor, 4)) & legal;
            const unsigned approach =
                rectangle(y, byte, anchor, 6) & ~rectangle(y, byte, anchor, 2) & legal;
            if (decision || approach)
                out.push_back({byte, static_cast<std::uint8_t>(decision),
                               static_cast<std::uint8_t>(approach)});
        }
    return out;
}
inline int ward_stencil_score(const std::vector<WardScoreByte> &stencil,
                              const std::vector<std::uint8_t> &mask,
                              const std::vector<std::uint8_t> &now,
                              const std::vector<std::uint8_t> &future) {
    if (mask.size() != now.size() || mask.size() != future.size())
        return 0;
    int score = 0;
    for (const auto &entry : stencil) {
        const auto seen = unsigned(mask[entry.index]);
        score += 4 * std::popcount(seen & ~unsigned(now[entry.index]) & entry.decision);
        score += 2 * std::popcount(seen & ~unsigned(future[entry.index]) & entry.decision);
        score += std::popcount(seen & ~unsigned(future[entry.index]) & entry.approach);
    }
    return score;
}
inline int ward_contact_range(const World &w) {
    // Pinned current kits: 4-tile control plus a possible earlier 2-tile dash.
    // Unknown kits retain that bound; observed metadata can enlarge it.
    int reach = 6;
    for (const auto &enemy : w.enemies)
        reach = std::max(reach, possible_contact_reach(enemy, 8));
    for (const auto &sight : w.sightings)
        reach = std::max(reach, possible_contact_reach(
                                    sight.actor, 8 + std::clamp(w.round - sight.round, 0, 8)));
    return reach;
}
inline bool ward_dash_uncertain(const World &w) {
    if (w.sightings.size() < w.enemy_handles.size())
        return true;
    for (const auto &sight : w.sightings)
        for (const auto &spell : sight.actor.spells)
            if (spell.kind == 6 &&
                (spell.cooldown < 0 || spell.cooldown <= 8 + w.round - sight.round))
                return true;
    return false;
}
inline int ward_finish_ticks(const World &w, const Mission &mission) {
    if (mission.phase == Phase::Collect) {
        const int elapsed = w.memory.hold_group == mission.group && w.memory.hold_since >= 0
                                ? w.round - w.memory.hold_since
                                : 0;
        return std::max(1, int(cambc::constants::capture_time) + 1 - elapsed);
    }
    if (mission.phase == Phase::Deliver)
        return mission.completion_cost > 0 ? int(std::ceil(mission.completion_cost)) : -1;
    if (mission.phase == Phase::Recover)
        return w.self.home ? 3 : cambc::constants::recall_time;
    if (mission.phase == Phase::Clear && mission.group >= 0 &&
        mission.group < int(w.groups.size())) {
        if (!w.groups[mission.group].fresh(w.round) || w.self.strength <= 0)
            return -1;
        double hp = 0;
        for (const auto &camp : w.groups[mission.group].camps)
            hp += camp.hp;
        // Solo basics are a bounded upper finish estimate. No unaccepted helper
        // or a second successful cast is invented to shorten the commitment.
        return std::max(1, int(std::ceil(hp / w.self.strength)) + (w.self.can_attack ? 0 : 1));
    }
    return 1; // The next reversible observation/movement decision.
}

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
    return packed_bit(bytes, index);
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
        // Only already available goal-rooted fields are inspected. Preparing a
        // ward never builds a route or consumes the primary move's path budget.
        if (!field && w.geo.valid(mission.target)) {
            const int key = w.geo.index(mission.target);
            for (const auto &[goal, cached] : w.geo.goal_cache)
                if (goal.first == key && (!field || goal.second == 0))
                    field = &cached;
            if (!field) {
                const auto it = w.geo.route_cache.find(key);
                if (it != w.geo.route_cache.end())
                    field = &it->second;
            }
        }
    }
    Pos future = w.self.pos;
    if (!field || w.geo.at(*field, future) == unreachable)
        return future;
    const auto &terrain = w.geo.terrain;
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
        // Distance zero is the unique optimum of the unchanged ranking. Avoid
        // scoring every legal tile when this exact anchor is already legal.
        if (std::find(legal.begin(), legal.end(), desired) != legal.end() &&
            std::find(selected.begin(), selected.end(), desired) == selected.end()) {
            selected.push_back(desired);
            continue;
        }
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

// Ward placement has its own action resource, but observer scoring also has a
// computation cost. Admit it before a planned ordinary move/assembly/collection
// or nonurgent recall; never postpone an attack, survival action or bank start.
inline bool ward_opportunity(const World &w, const Mission &mission, const Action &chosen) {
    if (!w.self.alive || w.self.stunned || w.self.channel != Channel::None ||
        ward_blocked_phase(mission.phase) || mission.phase == Phase::Escape ||
        (chosen.kind != Kind::Move && chosen.kind != Kind::Recall && chosen.kind != Kind::None))
        return false;
    if (chosen.kind == Kind::Recall && w.self.health_fraction() < .35)
        return false;
    for (const auto &e : w.enemies)
        if (distance(e.pos, w.self.pos) <= e.range + 1)
            return false;
    const Pos next = chosen.kind == Kind::Move ? chosen.at : mission.target;
    auto unseen = [&](Pos p) {
        return w.geo.valid(p) && !ward_local_bit(w.visible_bytes, w.geo.index(p));
    };
    const bool approaching =
        w.geo.valid(mission.target) && distance(w.self.pos, mission.target) <= 8;
    return (approaching && (unseen(mission.target) || unseen(next))) ||
           w.warning_near(w.self.pos, 4) ||
           (w.geo.valid(mission.target) && w.warning_near(mission.target, 4)) ||
           (chosen.kind == Kind::Recall && mission.group >= 0);
}

// Exact engine shadowcast masks are exported once each. Local arithmetic scores
// bounded objective/approach neighborhoods; there are no per-tile SDK queries.
inline int ward_buffer_score(const std::vector<std::uint8_t> &mask,
                             const std::vector<std::uint8_t> &now,
                             const std::vector<std::uint8_t> &future,
                             const std::vector<std::uint8_t> &blocked, int width, int height,
                             Pos self, Pos anchor) {
    if (width <= 0 || height <= 0 ||
        mask.size() != static_cast<unsigned>((width * height + 7) / 8) ||
        now.size() != mask.size() || future.size() != mask.size() || blocked.size() != mask.size())
        return 0;
    int immediate = 0, persistent = 0, warning = 0;
    const int x0 = std::max(0, std::min(self.x - 3, anchor.x - 6));
    const int x1 = std::min(width - 1, std::max(self.x + 3, anchor.x + 6));
    const int y0 = std::max(0, std::min(self.y - 3, anchor.y - 6));
    const int y1 = std::min(height - 1, std::max(self.y + 3, anchor.y + 6));
    for (int y = y0; y <= y1; ++y)
        for (int x = x0; x <= x1; ++x) {
            const int i = y * width + x;
            if (!ward_local_bit(mask, i) || ward_local_bit(blocked, i))
                continue;
            const Pos p{x, y};
            const int d = distance(p, anchor);
            const bool decision = distance(p, self) <= 3 || d <= 4;
            immediate += decision && !ward_local_bit(now, i);
            persistent += decision && !ward_local_bit(future, i);
            warning += d > 2 && d <= 6 && !ward_local_bit(future, i);
        }
    return 4 * immediate + 2 * persistent + warning;
}

inline std::optional<Action> ward_proposal(World &w, const Mission &mission, WardState &state) {
    const std::uint64_t start = cambc::fuel_remaining();
    if (!w.self.alive || w.self.stunned || w.self.channel != Channel::None ||
        ward_blocked_phase(mission.phase) || state.success_round == w.round ||
        state.attempt_round == w.round || start < 40000 ||
        w.round != static_cast<int>(cambc::round_number()) ||
        w.me.restrictions().contains(cambc::buff_restrictions::ward) || w.me.ward_cooldown() > 0)
        return std::nullopt;
    // Leave a primary action plus its fresh gateway check. At most two actual
    // candidate shadowcasts are scored, and at most one scan/owner/world round.
    const std::uint64_t floor = std::max<std::uint64_t>(32000, start - 25000);
    state.attempt_round = w.round;
    state.rejected.clear();
    const auto old_positions = w.me.ward_positions();
    if (old_positions.size() > 1)
        return std::nullopt;
    auto legal_mask = w.me.ward_placement_tiles();
    legal_mask &= ~(w.geo.static_blocked | cambc::vision::ward_tiles(cambc::team::ally));
    std::vector<Pos> legal;
    for (auto raw : legal_mask.positions()) {
        const Pos p = ward_pos(raw);
        if (std::find(old_positions.begin(), old_positions.end(), raw) == old_positions.end())
            legal.push_back(p);
    }
    if (legal.empty() || cambc::fuel_remaining() < floor)
        return std::nullopt;
    const Pos future = ward_future_waypoint(w, mission);
    const bool departing = mission.phase == Phase::Recover;
    const Pos anchor = departing ? w.self.pos : future;
    const auto natural_now = w.me.visible_tiles_from(ward_sdk(w.self.pos));
    const auto natural_future =
        future == w.self.pos ? natural_now : w.me.visible_tiles_from(ward_sdk(future));
    const auto now_bytes = natural_now.export_linear_buffer();
    const auto natural_bytes = natural_future.export_linear_buffer();
    const auto stencil =
        ward_score_stencil(w.geo.width, w.geo.height, w.self.pos, anchor, w.geo.terrain);
    if (cambc::fuel_remaining() < floor + 4000)
        return std::nullopt;
    // Use only a previously funded enemy-owned approach field. Its roots are
    // the entire plausible contact ring; subtracting range from a center-only
    // walk field can overstate warning around a wall.
    const int contact_range = ward_contact_range(w);
    const std::vector<std::uint16_t> *enemy_route = nullptr;
    if (w.geo.valid(mission.target)) {
        const auto found =
            w.geo.enemy_goal_cache.find({w.geo.index(mission.target), contact_range});
        if (found != w.geo.enemy_goal_cache.end())
            enemy_route = &found->second;
    }
    struct Approach {
        int index, eta;
    };
    std::vector<Approach> arrival;
    int outside_cutoff = 0, finish = ward_finish_ticks(w, mission), escape = unreachable;
    state.timing_known = false;
    state.terrain_timing_exact = false;
    state.warning_slack = -1;
    if (enemy_route && finish >= 0 && cambc::fuel_remaining() >= floor + 12000) {
        const auto exit = known_exit_prefix(w, anchor, false);
        if (exit.known) {
            escape = exit.owner_eta;
            int speed = 1;
            for (const auto &enemy : w.enemies)
                speed = std::max(speed, enemy.move_speed);
            for (const auto &sight : w.sightings)
                speed = std::max(speed, sight.actor.move_speed);
            if (state.holes < 0)
                state.holes = int(cambc::map::holes().count());
            const bool uncertain_shortcut = state.holes > 0 && ward_dash_uncertain(w);
            state.terrain_timing_exact = !uncertain_shortcut;
            // Outside this radius, even a straight approach cannot beat this
            // cutoff. It remains in the minimum; unscanned space is never empty.
            constexpr int radius = 10;
            outside_cutoff = std::clamp((radius + 1 - contact_range + speed - 1) / speed, 0, 8);
            arrival.reserve(64);
            state.timing_known = true;
            for (int y = std::max(0, mission.target.y - radius);
                 y <= std::min(w.geo.height - 1, mission.target.y + radius); ++y) {
                if (cambc::fuel_remaining() < floor + 7000) {
                    state.timing_known = false;
                    break; // Coverage scoring still has a funded fallback.
                }
                const int x0 = std::max(0, mission.target.x - radius);
                const int x1 = std::min(w.geo.width - 1, mission.target.x + radius);
                for (int byte = (y * w.geo.width + x0) / 8; byte <= (y * w.geo.width + x1) / 8;
                     ++byte) {
                    unsigned bits =
                        ward_interval_bits(y * w.geo.width + x0, y * w.geo.width + x1, byte) &
                        ~unsigned(natural_bytes[byte]) & ~unsigned(w.geo.enemy_terrain[byte]) &
                        0xffu;
                    while (bits) {
                        const int bit = std::countr_zero(bits), index = byte * 8 + bit;
                        bits &= bits - 1;
                        int path = (*enemy_route)[index];
                        if (uncertain_shortcut) {
                            const Pos p{index % w.geo.width, index / w.geo.width};
                            path = std::min(
                                path, std::max(0, distance(p, mission.target) - contact_range));
                        }
                        if (path == unreachable)
                            continue;
                        const int eta = (path + speed - 1) / speed;
                        if (eta >= outside_cutoff)
                            continue;
                        if (arrival.size() < 64)
                            arrival.push_back({index, eta});
                        else
                            outside_cutoff = std::min(outside_cutoff, eta);
                    }
                }
            }
        }
    }
    int last_slack = -1, selected_slack = -1;
    auto score_mask = [&](const std::vector<std::uint8_t> &mask) {
        int value = ward_stencil_score(stencil, mask, now_bytes, natural_bytes);
        if (state.timing_known) {
            int first = outside_cutoff;
            for (const auto &[index, eta] : arrival)
                if (!packed_bit(mask, index))
                    first = std::min(first, eta);
            // One owner read/reaction opportunity is reserved. It is not a
            // teammate's instant shared camera, nor a fabricated zero delay.
            const int slack = first - finish - escape - 1;
            last_slack = slack;
            value += 3 * std::clamp(slack, -12, 12);
        }
        return value;
    };
    auto score = [&](Pos p) {
        return score_mask(cambc::ward::visible_tiles_from(ward_sdk(p)).export_linear_buffer());
    };
    int retained = state.timing_known ? score_mask(std::vector<std::uint8_t>(now_bytes.size())) : 0;
    for (auto p : old_positions) {
        if (cambc::fuel_remaining() < floor)
            return std::nullopt;
        retained = std::max(retained, score(ward_pos(p)));
    }
    Pos ahead = future;
    if (ahead == w.self.pos && w.geo.valid(mission.target))
        ahead = mission.target;
    const auto candidates = ward_candidate_positions(legal, w.self.pos, ahead);
    int best = retained;
    Pos placement{};
    const unsigned side = w.self_index >= 0 && w.self_index % 2 ? 2 : 1;
    for (unsigned k = 0; k < 2 && k < candidates.size(); ++k) {
        if (cambc::fuel_remaining() < floor)
            break;
        const unsigned i = k == 0 || side >= candidates.size() ? k : side;
        const int value = score(candidates[i]);
        if (value > best) {
            best = value;
            placement = candidates[i];
            selected_slack = last_slack;
        }
    }
    if (placement.x < 0 || best <= retained + std::max(4, retained / 6))
        return std::nullopt;
    Action action;
    action.kind = Kind::Ward;
    action.at = placement;
    action.reason =
        departing ? "leave-persistent-mission-observer" : "prepare-personal-mission-warning";
    state.warning_slack = selected_slack;
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

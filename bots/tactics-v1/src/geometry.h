#pragma once
#include "types.h"
#include <cambc.h>
#include <map>
namespace tactics {
namespace bc = cambc;
inline const char *native_context = "turn";
inline bc::vec2 sdk(Pos p) {
    return {p.x, p.y};
}
inline Pos position(bc::vec2 p) {
    return {p.x, p.y};
}
inline bool fuel(int extra = 0) {
    return bc::fuel_remaining() > static_cast<unsigned>(Settings::fuel_reserve + extra);
}

// Only immutable public terrain/design lives here. No map-name strategy branches.
struct Geometry {
    int width = 0, height = 0, spawn_walk = unreachable;
    bc::bitboard static_blocked, own_spawn, enemy_spawn, enemy_blocked;
    std::vector<std::uint8_t> enemy_terrain;
    std::vector<std::uint8_t> terrain, spawn_terrain;
    std::vector<Pos> altars;
    std::vector<Group> groups;
    std::vector<bc::map::camp_group> handles;
    std::vector<std::uint16_t> home, enemy_home, nearest_altar;
    std::vector<std::vector<std::uint16_t>> altar_fields;
    std::map<int, std::vector<std::uint16_t>> route_cache;
    std::map<std::pair<int, int>, std::vector<std::uint16_t>> goal_cache, enemy_goal_cache;
    struct FieldWork {
        int key = -1;
        std::size_t scan = 0, head = 0;
        std::vector<std::uint16_t> values;
        std::vector<std::uint8_t> blocked;
        std::vector<int> frontier;
    } pending_field;
    Pos pending_goal{};
    int pending_range = 0;
    bool pending_enemy = false;
    bool initialized = false, monolith_only = false;
    bool valid(Pos p) const {
        return p.x >= 0 && p.y >= 0 && p.x < width && p.y < height;
    }
    int index(Pos p) const {
        return p.y * width + p.x;
    }
    bool blocked(Pos p) const {
        return !valid(p) ||
               (terrain.empty() ? static_blocked.is_set(sdk(p)) : packed_bit(terrain, index(p)));
    }
    int at(const std::vector<std::uint16_t> &field, Pos p) const {
        return valid(p) && field.size() == static_cast<unsigned>(width * height) ? field[index(p)]
                                                                                 : unreachable;
    }
    std::vector<std::uint16_t> field(const bc::bitboard &blockers,
                                     const bc::bitboard &roots) const {
        bc::distance_field distances;
        bc::bitboard reached;
        distances.compute(blockers, roots, reached);
        return distances.export_linear_buffer();
    }
    std::vector<std::uint16_t> field(const std::vector<Pos> &roots) const {
        bc::bitboard mask;
        for (auto p : roots)
            if (!blocked(p))
                mask.set(sdk(p));
        return field(static_blocked, mask);
    }
    std::optional<std::vector<std::uint16_t>> build_field(int key, const bc::bitboard &blockers,
                                                          const bc::bitboard &roots) {
        if (pending_field.key >= 0 && pending_field.key != key)
            return std::nullopt;
        if (pending_field.key < 0) {
            const int admission = std::min(95000, std::max(55000, 30000 + 5 * width * height));
            if (bc::fuel_remaining() < static_cast<unsigned>(admission))
                return std::nullopt;
            bc::distance_field distances;
            bc::bitboard reached;
            native_context = "geometry:bounded-field";
            // A winding new map must not turn one native BFS into an
            // unbounded host call. Continue its exact frontier in guest slices.
            const auto expanded =
                distances.compute_with_expansion_count(blockers, roots, reached, 128);
            if (expanded < 128)
                return distances.export_linear_buffer();
            pending_field.values = distances.export_linear_buffer();
            pending_field.blocked = blockers.export_linear_buffer();
            pending_field.key = key;
        }
        auto &work = pending_field;
        while (work.scan < work.values.size()) {
            if ((work.scan & 31) == 0 && bc::fuel_remaining() < 34000)
                return std::nullopt;
            if (work.values[work.scan] == 128)
                work.frontier.push_back(work.scan);
            ++work.scan;
        }
        while (work.head < work.frontier.size()) {
            if (bc::fuel_remaining() < 34000)
                return std::nullopt;
            const int cell = work.frontier[work.head++];
            const Pos p{cell % width, cell / width};
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    Pos next{p.x + dx, p.y + dy};
                    if (!valid(next))
                        continue;
                    const int i = index(next);
                    if (work.values[i] != unreachable || packed_bit(work.blocked, i))
                        continue;
                    work.values[i] = work.values[cell] + 1;
                    work.frontier.push_back(i);
                }
        }
        auto result = std::move(work.values);
        pending_field = {};
        // Only a completed search enters a route cache. A capped-unreached
        // tile is never exposed as a certified disconnected destination.
        return result;
    }
    int walk(Pos from, Pos to) {
        if (!valid(from) || !valid(to) || blocked(to))
            return unreachable;
        int key = index(to);
        auto it = route_cache.find(key);
        if (it == route_cache.end()) {
            if (!fuel(18000))
                return unreachable;
            if (route_cache.size() >= 12)
                route_cache.erase(route_cache.begin());
            it = route_cache.emplace(key, field(std::vector<Pos>{to})).first;
        }
        return at(it->second, from);
    }
    void ensure_route(Pos root) {
        if (blocked(root) || route_cache.contains(index(root)) || !fuel(18000))
            return;
        if (route_cache.size() >= 12)
            route_cache.erase(route_cache.begin());
        route_cache.emplace(index(root), field(std::vector<Pos>{root}));
    }
    // Shortlists use a lower bound until a selected route has an exact field.
    // Do not build a full map field for every actor position/candidate/action.
    int estimate(Pos from, Pos target, int range = 0) const {
        if (!valid(from) || !valid(target))
            return unreachable;
        auto it = goal_cache.find({index(target), range});
        if (it != goal_cache.end())
            return at(it->second, from);
        auto source = route_cache.find(index(from));
        if (source != route_cache.end()) {
            const int d = at(source->second, target);
            return d == unreachable ? unreachable : std::max(0, d - range);
        }
        return std::max(0, distance(from, target) - range);
    }
    std::optional<int> cached_steps(Pos from, Pos target, int range = 0) const {
        if (!valid(from) || !valid(target))
            return std::nullopt;
        if (auto it = goal_cache.find({index(target), range}); it != goal_cache.end())
            return at(it->second, from);
        if (range == 0) {
            if (auto it = route_cache.find(index(target)); it != route_cache.end())
                return at(it->second, from);
            if (auto it = route_cache.find(index(from)); it != route_cache.end())
                return at(it->second, target);
        }
        return std::nullopt;
    }
    void resume_goal() {
        if (pending_field.key < 100000 || !valid(pending_goal))
            return;
        const auto key = std::pair{index(pending_goal), pending_range};
        auto result = build_field(pending_field.key, pending_enemy ? enemy_blocked : static_blocked,
                                  bc::bitboard{});
        if (!result)
            return;
        auto &cache = pending_enemy ? enemy_goal_cache : goal_cache;
        if (cache.size() >= 20)
            cache.erase(cache.begin());
        cache.emplace(key, std::move(*result));
        pending_goal = {};
    }
    const std::vector<std::uint16_t> *goal_field(Pos target, int range, bool enemy = false) {
        if (!valid(target))
            return nullptr;
        auto &cache = enemy ? enemy_goal_cache : goal_cache;
        const auto key = std::pair{index(target), range};
        if (auto it = cache.find(key); it != cache.end())
            return &it->second;
        const int request = 100000 + index(target) * 32 + range + (enemy ? 2000000 : 0);
        if (pending_field.key >= 0) {
            resume_goal();
            if (auto it = cache.find(key); it != cache.end())
                return &it->second;
            if (pending_field.key >= 0)
                return nullptr;
        }
        // Measured release native field construction/export costs up to 28k.
        // Admission leaves a useful action and fresh legality check available.
        const unsigned admission = std::min(95000, std::max(55000, 30000 + 5 * width * height));
        if (bc::fuel_remaining() < admission + 3000)
            return nullptr;
        bc::bitboard roots;
        native_context = "geometry:goal-roots";
        roots.draw_chebyshev(sdk(target), range);
        roots &= ~(enemy ? enemy_blocked : static_blocked);
        if (roots.count() == 0) {
            if (cache.size() >= 20)
                cache.erase(cache.begin());
            return &cache.emplace(key, std::vector<std::uint16_t>(width * height, unreachable))
                        .first->second;
        }
        auto result = build_field(request, enemy ? enemy_blocked : static_blocked, roots);
        if (!result) {
            if (pending_field.key == request) {
                pending_goal = target;
                pending_range = range;
                pending_enemy = enemy;
            }
            return nullptr;
        }
        if (cache.size() >= 20)
            cache.erase(cache.begin());
        return &cache.emplace(key, std::move(*result)).first->second;
    }
    void initialize(bool draft_only = false) {
        if (initialized)
            return;
        if (width == 0) {
            width = bc::map::width();
            height = bc::map::height();
            own_spawn = bc::map::spawn_region(bc::team::ally);
            enemy_spawn = bc::map::spawn_region(bc::team::enemy);
            const auto walls = bc::map::walls(), holes = bc::map::holes(),
                       altar_mask = bc::map::altars();
            static_blocked = walls | holes | altar_mask | enemy_spawn;
            terrain = static_blocked.export_linear_buffer();
            spawn_terrain = own_spawn.export_linear_buffer();
            enemy_blocked = walls | holes | altar_mask | own_spawn;
            enemy_terrain = enemy_blocked.export_linear_buffer();
            for (auto p : altar_mask.positions())
                altars.push_back(position(p));
        }
        // Immutable preparation resumes explicitly between owner turns. A
        // field is admitted only with its measured worst-case construction
        // allowance; automatic fuel suspension is never the scheduler.
        auto admitted = [&] { return bc::fuel_remaining() >= 60000; };
        if (home.empty()) {
            if (!admitted())
                return;
            auto result = build_field(1, static_blocked, own_spawn);
            if (!result)
                return;
            home = std::move(*result);
        }
        if (draft_only) {
            for (auto p : enemy_spawn.positions())
                for (int dy = -1; dy <= 1; ++dy)
                    for (int dx = -1; dx <= 1; ++dx) {
                        Pos q{p.x + dx, p.y + dy};
                        if (!blocked(q))
                            spawn_walk = std::min(spawn_walk, at(home, q));
                    }
            return;
        }
        if (enemy_home.empty()) {
            if (!admitted())
                return;
            auto result = build_field(2, enemy_blocked, enemy_spawn);
            if (!result)
                return;
            enemy_home = std::move(*result);
        }
        auto ring_at = [&](Pos altar) {
            bc::bitboard ring;
            for (int y = altar.y - 1; y <= altar.y + 1; ++y)
                for (int x = altar.x - 1; x <= altar.x + 1; ++x)
                    if (!blocked({x, y}))
                        ring.set(sdk({x, y}));
            return ring;
        };
        while (altar_fields.size() < altars.size()) {
            if (!admitted())
                return;
            auto result = build_field(10 + altar_fields.size(), static_blocked,
                                      ring_at(altars[altar_fields.size()]));
            if (!result)
                return;
            altar_fields.push_back(std::move(*result));
        }
        if (nearest_altar.empty()) {
            if (!admitted())
                return;
            bc::bitboard rings;
            for (auto altar : altars)
                rings |= ring_at(altar);
            auto result = build_field(3, static_blocked, rings);
            if (!result)
                return;
            nearest_altar = std::move(*result);
        }
        if (handles.empty())
            handles = bc::map::camp_groups();
        while (groups.size() < handles.size()) {
            if (!admitted())
                return;
            const unsigned i = groups.size();
            const auto &h = handles[i];
            Group g;
            g.id = static_cast<unsigned>(static_cast<bc::handle_camp_group_t>(h));
            g.index = i;
            g.gold = h.gold_value();
            g.gems = h.gem_value();
            g.respawn = h.max_respawn_timer();
            for (const auto &c : h.camps()) {
                const auto stats = c.base_stats();
                g.spawns.push_back({static_cast<int>(static_cast<bc::handle_camp_t>(c)),
                                    static_cast<int>(c.kind()), position(c.spawn_position()),
                                    static_cast<double>(stats.base_health),
                                    static_cast<double>(stats.base_strength),
                                    static_cast<int>(stats.base_attack_range)});
                g.initial_hp += stats.base_health;
                g.initial_strength += stats.base_strength;
                g.monolith |= c.is_monolith();
            }
            groups.push_back(std::move(g));
        }
        for (auto p : enemy_spawn.positions())
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    Pos q{p.x + dx, p.y + dy};
                    if (!blocked(q))
                        spawn_walk = std::min(spawn_walk, at(home, q));
                }
        bool gem = false, ordinary = false;
        for (const auto &g : groups) {
            gem |= g.gems > 0;
            ordinary |= g.gems > 0 && !g.monolith;
        }
        monolith_only = gem && !ordinary;
        initialized = true;
    }
};
} // namespace tactics

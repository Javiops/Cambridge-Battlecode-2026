#pragma once
#include "types.h"
#include <cambc.h>
#include <map>
namespace tactics {
namespace bc = cambc;
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
    std::vector<Pos> altars;
    std::vector<Group> groups;
    std::vector<bc::map::camp_group> handles;
    std::vector<std::uint16_t> home, enemy_home, nearest_altar;
    std::vector<std::vector<std::uint16_t>> altar_fields;
    std::map<int, std::vector<std::uint16_t>> route_cache;
    bool initialized = false, monolith_only = false;
    bool valid(Pos p) const {
        return p.x >= 0 && p.y >= 0 && p.x < width && p.y < height;
    }
    int index(Pos p) const {
        return p.y * width + p.x;
    }
    bool blocked(Pos p) const {
        return !valid(p) || static_blocked.is_set(sdk(p));
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
    void initialize() {
        if (initialized)
            return;
        width = bc::map::width();
        height = bc::map::height();
        own_spawn = bc::map::spawn_region(bc::team::ally);
        enemy_spawn = bc::map::spawn_region(bc::team::enemy);
        static_blocked = bc::map::walls() | bc::map::holes() | bc::map::altars() | enemy_spawn;
        for (auto p : bc::map::altars().positions())
            altars.push_back(position(p));
        home = field(static_blocked, own_spawn);
        enemy_blocked = bc::map::walls() | bc::map::holes() | bc::map::altars() | own_spawn;
        enemy_terrain = enemy_blocked.export_linear_buffer();
        enemy_home = field(enemy_blocked, enemy_spawn);
        bc::bitboard all_rings;
        for (auto altar : altars) {
            bc::bitboard ring;
            for (int y = altar.y - 1; y <= altar.y + 1; ++y)
                for (int x = altar.x - 1; x <= altar.x + 1; ++x) {
                    Pos p{x, y};
                    if (!blocked(p)) {
                        ring.set(sdk(p));
                        all_rings.set(sdk(p));
                    }
                }
            altar_fields.push_back(field(static_blocked, ring));
        }
        nearest_altar = field(static_blocked, all_rings);
        // Boundary-to-boundary route is a coarse draft fallback, not a combat forecast.
        for (auto p : enemy_spawn.positions())
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    Pos q{p.x + dx, p.y + dy};
                    if (!blocked(q))
                        spawn_walk = std::min(spawn_walk, at(home, q));
                }
        handles = bc::map::camp_groups();
        bool gem = false, ordinary = false;
        for (unsigned i = 0; i < handles.size(); ++i) {
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
                                    static_cast<double>(stats.base_strength)});
                g.initial_hp += stats.base_health;
                g.initial_strength += stats.base_strength;
                g.monolith |= c.is_monolith();
            }
            gem |= g.gems > 0;
            ordinary |= g.gems > 0 && !g.monolith;
            groups.push_back(g);
        }
        monolith_only = gem && !ordinary;
        initialized = true;
    }
};
} // namespace tactics

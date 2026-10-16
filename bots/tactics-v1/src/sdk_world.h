#pragma once
#include "geometry.h"
#include "information.h"
#include <cambc.h>
#include <string>
namespace tactics {
inline int identity(const bc::champion &c) {
    return static_cast<unsigned>(static_cast<bc::handle_champion_t>(c));
}
inline int identity(const bc::camp &c) {
    return static_cast<unsigned>(static_cast<bc::handle_camp_t>(c));
}
// Host API adapter pinned to CAMBC SDK 2.2.2. These are the official imported
// records from that SDK's imports.h, not locally reconstructed ABI layouts.
// The validation runner pins cambc.h SHA-256 to 76664dc7c4ab764243a7530eb97be12d9
// c20518b7bd2601a962fb0669d1da4a4. A snapshot is local to one refresh; it never
// bypasses the host's personal-visibility check or survives an action/yield.
namespace sdk_222 {
inline std::optional<bc::detail::champion_info> visible_champion(const bc::champion &c) {
    native_context = "snapshot:champion-record";
    bc::detail::champion_info value{};
    const auto code = bc::detail::sdk_champion(static_cast<std::uint32_t>(identity(c)), &value);
    if (code == static_cast<std::int32_t>(bc::error_code::api_not_in_vision))
        return std::nullopt;
    bc::detail::check(code);
    if (value.x < 0 || value.y < 0)
        return std::nullopt;
    return value;
}
inline std::optional<bc::detail::camp_state> visible_camp(const bc::camp &c) {
    native_context = "snapshot:camp-record";
    bc::detail::camp_state value{};
    const auto code = bc::detail::sdk_camp(static_cast<std::uint32_t>(identity(c)), &value);
    if (code == static_cast<std::int32_t>(bc::error_code::api_not_in_vision) ||
        code == static_cast<std::int32_t>(bc::error_code::api_not_found))
        return std::nullopt;
    bc::detail::check(code);
    return value;
}
inline int visible_camp_identity(Pos p) {
    native_context = "snapshot:camp-at";
    std::uint32_t handle{};
    bc::detail::check(bc::detail::sdk_camp_at(p.x, p.y, &handle));
    return static_cast<int>(handle);
}
} // namespace sdk_222
inline Spell read_spell(const bc::ability &a, bool can_cast) {
    native_context = "snapshot:ability";
    Spell s;
    s.slot = a.slot();
    auto info = a.info();
    if (!info)
        return s;
    std::visit(
        [&](const auto &p) {
            s.kind = static_cast<int>(p.kind);
            s.recharge = p.max_cooldown;
            s.exclusive = p.exclusive_with_movement;
            s.camps = p.valid_targets.contains(bc::ability_target_mask::camps);
            s.enemies = p.valid_targets.contains(bc::ability_target_mask::enemies);
            s.allies = p.valid_targets.contains(bc::ability_target_mask::allies);
            s.self = p.valid_targets.contains(bc::ability_target_mask::self);
            s.ground = p.valid_targets.contains(bc::ability_target_mask::ground);
            if constexpr (requires { p.range; })
                s.range = static_cast<int>(p.range);
            if constexpr (requires { p.radius; })
                s.radius = static_cast<int>(p.radius);
            if constexpr (requires { p.duration; })
                s.duration = p.duration;
            if constexpr (requires { p.modifier; })
                s.scale = p.modifier;
        },
        *info);
    try {
        s.cooldown = a.cooldown();
        s.ready = can_cast && s.cooldown == 0;
    } catch (const bc::error &) {
        s.cooldown = -1;
    }
    if (s.kind == 2 || s.kind == 3 || s.kind == 4)
        s.amount = a.damage_amount();
    else if (s.kind == 5)
        s.amount = a.heal_amount();
    else if (s.kind == 7)
        s.amount = a.shield_amount();
    return s;
}
inline Actor read_actor(const bc::champion &c, const bc::detail::champion_info &snapshot) {
    native_context = "snapshot:actor";
    Actor a;
    a.id = identity(c);
    const auto state = bc::champion_state::from_bits_retain(snapshot.state);
    a.alive = state.contains(bc::champion_state::alive);
    if (!a.alive)
        return a;
    a.type = snapshot.type;
    a.pos = {snapshot.x, snapshot.y};
    a.hp = snapshot.health;
    a.max_hp = snapshot.max_health;
    a.strength = snapshot.strength;
    a.focus = snapshot.focus;
    a.range = snapshot.attack_range;
    a.gems = c.gem_count();
    a.can_move = state.contains(bc::champion_state::can_move);
    a.can_attack = state.contains(bc::champion_state::can_attack);
    a.can_cast = state.contains(bc::champion_state::can_cast);
    a.completed = state.contains(bc::champion_state::completed_turn);
    a.move_speed = snapshot.move_speed;
    a.priority = c.prev_priority();
    if (state.contains(bc::champion_state::recalling))
        a.channel = Channel::Recall;
    else if (state.contains(bc::champion_state::submitting_gems))
        a.channel = Channel::Tribute;
    else if (state.contains(bc::champion_state::teleporting))
        a.channel = Channel::Teleport;
    if (a.channel != Channel::None)
        a.channel_ticks = c.remaining_channel_time();
    const auto buffs = c.buffs();
    a.stunned = buffs.has_stun();
    if (a.stunned)
        a.stun_ticks = buffs.get<bc::buff_stun>().duration;
    a.enhanced = buffs.has_enhanced_attack();
    if (buffs.has_shield())
        a.shield = buffs.get<bc::buff_shield>().value;
    const auto inventory = c.item_count();
    static_assert(static_cast<unsigned>(bc::item_type::count) == 42);
    const auto has_emblem = [&](unsigned family) {
        for (unsigned stat = 0; stat < 3; ++stat)
            if (inventory[static_cast<bc::item_type>(6 * family + 2 * stat + 1)] > 0)
                return true;
        return false;
    };
    if (has_emblem(2))
        a.mitigation = .9;
    const bool jungle = has_emblem(4);
    a.home = has_emblem(5);
    a.monster = has_emblem(0);
    a.camp_mitigation = a.mitigation * (jungle ? .7 : 1.0);
    const auto abilities = c.abilities();
    for (int k = 0; k < 2; ++k)
        a.spells[k] = read_spell(abilities[k], a.can_cast);
    return a;
}
inline Actor read_actor(const bc::champion &c) {
    // In particular, self can shop while dead. Never ask for its live record,
    // type, inventory or ability amounts before this official life guard.
    if (!c.is_alive()) {
        Actor dead;
        dead.id = identity(c);
        return dead;
    }
    auto snapshot = sdk_222::visible_champion(c);
    if (!snapshot) {
        Actor hidden;
        hidden.id = identity(c);
        return hidden;
    }
    return read_actor(c, *snapshot);
}
struct Sighting {
    Actor actor{};
    int round = -1;
};
struct World {
    Geometry &geo;
    Memory &memory;
    bc::champion &me;
    Actor self{};
    int gold = 0, round = -1, serial = 0, own_score = 0, enemy_score = 0, self_type = -1;
    std::array<Spell, 2> spells{};
    std::vector<Actor> allies, enemies;
    std::vector<bc::champion> ally_handles, enemy_handles;
    std::vector<int> kit_ready;
    std::vector<bc::camp> camp_handles;
    struct CampMetadata {
        bc::camp handle;
        int group = -1, range = 0;
    };
    std::map<int, CampMetadata> camp_metadata;
    struct FarmGeometryScore {
        int distance = unreachable;
        double alive = 0, reward = 0, damage = 0;
    };
    std::vector<FarmGeometryScore> farm_geometry_scores;
    Pos farm_geometry_origin{};
    double farm_geometry_strength = -1, farm_geometry_mitigation = -1;
    bool prepare_farm_geometry_scores() {
        if (farm_geometry_origin != self.pos || farm_geometry_strength != self.strength ||
            farm_geometry_mitigation != self.camp_mitigation) {
            farm_geometry_scores.clear();
            farm_geometry_origin = self.pos;
            farm_geometry_strength = self.strength;
            farm_geometry_mitigation = self.camp_mitigation;
        }
        // Only immutable map geometry and current own power are cached. Fresh
        // lifecycle, HP reserve, failures and holder state are applied later.
        while (farm_geometry_scores.size() < geo.groups.size()) {
            if (bc::fuel_remaining() < 28000)
                return false;
            const auto &group = geo.groups[farm_geometry_scores.size()];
            FarmGeometryScore value;
            for (const auto &spawn : group.spawns)
                if (home_distance(spawn.pos) != unreachable)
                    value.distance = std::min(value.distance, distance(self.pos, spawn.pos));
            if (value.distance != unreachable) {
                const double ticks = std::ceil(group.initial_hp / std::max(1.0, self.strength));
                const double reward = group.gems + .25 * group.gold;
                value.alive = reward / (1 + value.distance +
                                        group.initial_hp / std::max(1.0, self.strength) + 6);
                value.reward = reward / (1 + value.distance + 6);
                value.damage = ticks * group.initial_strength * self.camp_mitigation + 1;
            }
            farm_geometry_scores.push_back(value);
        }
        return true;
    }
    std::vector<GroupView> groups;
    std::vector<Sighting> sightings;
    int combat_cache_serial = -1;
    std::map<std::pair<int, int>, std::vector<Pos>> combat_reach_cache;
    std::map<std::array<int, 5>, double> combat_damage_cache;
    bc::bitboard visible, occupied;
    std::vector<std::uint8_t> occupied_bytes, visible_bytes;
    std::array<std::uint8_t, 8> claims{};
    int self_index = -1, ally_count = 0;
    explicit World(Geometry &g, Memory &m)
        : geo(g), memory(m), me(bc::self()), groups(g.groups.size()) {
        // Physical identities and immutable kit metadata do not change after
        // drafting. Cache handles, never their live observed state.
        ally_handles = bc::champions(bc::team::ally);
        enemy_handles = bc::champions(bc::team::enemy);
        std::sort(ally_handles.begin(), ally_handles.end(),
                  [](const auto &a, const auto &b) { return identity(a) < identity(b); });
        ally_count = ally_handles.size();
        for (unsigned i = 0; i < ally_handles.size(); ++i)
            if (identity(ally_handles[i]) == identity(me))
                self_index = i;
        kit_ready.push_back(identity(me));
        // Public camp identities, groups and design ranges never change.
        // Visibility, position, HP and awake/dead state remain fresh queries.
        for (unsigned gi = 0; gi < geo.handles.size(); ++gi)
            for (const auto &camp : geo.handles[gi].camps()) {
                int range = -1;
                for (const auto &spawn : geo.groups[gi].spawns)
                    if (spawn.id == identity(camp)) {
                        range = spawn.range;
                        break;
                    }
                if (range >= 0)
                    camp_metadata.emplace(identity(camp), CampMetadata{camp, int(gi), range});
            }
    }
    void ensure_visible_kit(bc::champion &c, Pos observed_position) {
        const int id = identity(c);
        if (std::find(kit_ready.begin(), kit_ready.end(), id) != kit_ready.end())
            return;
        // SDK 2.2.2 caches ability metadata errors in handles constructed while
        // hidden. Rebind once from an actually visible tile before reading kit
        // information; this does not grant sight or legal hidden targeting.
        c = bc::vision::champion_at(sdk(observed_position));
        kit_ready.push_back(id);
    }
    bool in_spawn(Pos p) const {
        return geo.valid(p) &&
               (geo.spawn_terrain.empty() ? geo.own_spawn.is_set(sdk(p))
                                          : packed_bit(geo.spawn_terrain, geo.index(p)));
    }
    int home_distance(Pos p) const {
        return geo.at(geo.home, p);
    }
    int altar_distance(Pos p) const {
        return geo.at(geo.nearest_altar, p);
    }
    int walk(Pos a, Pos b) {
        if (a == self.pos) {
            auto it = geo.route_cache.find(geo.index(a));
            if (it != geo.route_cache.end())
                return geo.at(it->second, b);
        }
        return geo.walk(a, b);
    }
    bool free(Pos p) const {
        return !geo.blocked(p) &&
               (p == self.pos ||
                !(occupied_bytes.empty() ? occupied.is_set(sdk(p))
                                         : packed_bit(occupied_bytes, geo.index(p)))) &&
               !(memory.blocked_round == round && memory.blocked_tile == p);
    }
    // Exact immutable walking distance to a legal enemy approach ring. If its
    // field cannot be admitted, a geometric lower bound retains uncertainty.
    int enemy_steps(Pos from, Pos target, int range = 0) {
        if (auto field = geo.goal_field(target, range, true))
            return geo.at(*field, from);
        return std::max(0, distance(from, target) - range);
    }
    std::optional<bc::champion> champion(int id) const {
        if (id == self.id)
            return me;
        for (const auto &c : ally_handles)
            if (identity(c) == id && c.is_visible())
                return c;
        for (const auto &c : enemy_handles)
            if (identity(c) == id && c.is_visible())
                return c;
        return std::nullopt;
    }
    std::optional<bc::camp> camp(int id) const {
        for (const auto &c : camp_handles)
            if (identity(c) == id && c.is_visible() && c.is_alive())
                return c;
        return std::nullopt;
    }
    std::optional<bc::altar_lock> enemy_lock(Pos p) const {
        // altar_lock_at prefers our own lock when BOTH sides occupy an altar.
        for (const auto &lock : bc::vision::altar_locks(bc::team::enemy))
            if (position(lock.position()) == p)
                return lock;
        return std::nullopt;
    }
    bool on_group(int index, Pos p) const {
        if (index < 0 || index >= static_cast<int>(geo.groups.size()))
            return false;
        for (auto s : geo.groups[index].spawns)
            if (s.pos == p)
                return true;
        return false;
    }
    int group_index(int id) const {
        for (unsigned i = 0; i < geo.groups.size(); ++i)
            if (geo.groups[i].id == id)
                return i;
        return -1;
    }
    int claim_for(int roster_index) const {
        ClaimBytes bytes{};
        std::copy_n(claims.begin(), 5, bytes.begin());
        return decode_claim(bytes, roster_index, ally_count, geo.groups.size());
    }
    bool matching_claim(int actor_id, int group) const {
        for (unsigned i = 0; i < ally_handles.size(); ++i)
            if (identity(ally_handles[i]) == actor_id)
                return claim_for(i) == group;
        return false;
    }
    void publish_claim(int group) {
        if (self_index < 0 || !fuel(1000) || round != static_cast<int>(bc::round_number()))
            return;
        // Re-read immediately before bounded RMW; no stale byte buffer survives a yield.
        if (ally_count == 6 && geo.groups.size() <= 63) {
            if (!fuel(1000) || round != static_cast<int>(bc::round_number()))
                return;
            ClaimBytes bytes{};
            bc::shared_memory.read(0, std::span(bytes));
            auto next = encode_claim(bytes, self_index, ally_count, geo.groups.size(), group);
            if (next)
                bc::shared_memory.write(0, std::span(*next));
        } else if (self_index < 5)
            bc::shared_memory[self_index] =
                static_cast<std::uint8_t>(group >= 0 && group < 255 ? group + 1 : 0);
        // Unsupported sixth-body/large-layout case deliberately has no claim; it never overwrites
        // another slot.
    }
    void publish_warning() {
        if (self_index < 0 || self_index > 5 || enemies.empty() || !fuel(2500) ||
            round != static_cast<int>(bc::round_number()))
            return;
        const Actor *danger = &enemies.front();
        for (const auto &e : enemies)
            if (distance(e.pos, self.pos) < distance(danger->pos, self.pos))
                danger = &e;
        Warning next{std::min(15, danger->pos.x * 16 / geo.width),
                     std::min(15, danger->pos.y * 16 / geo.height), round,
                     enemies.size() >= 3   ? 3
                     : enemies.size() >= 2 ? 2
                                           : 1,
                     self_index};
        std::array<std::uint8_t, 3> bytes{};
        bc::shared_memory.read(5, std::span(bytes));
        const auto old = decode_warning(bytes);
        if (old.fresh(round) && old.round == round && old.severity > next.severity)
            return;
        // No unbounded calculation, action or yield between this epoch guard
        // and the three-byte write. Never rewrites the five claim bytes.
        if (round == static_cast<int>(bc::round_number()) && fuel(1500)) {
            bytes = encode_warning(next);
            bc::shared_memory.write(5, std::span(bytes));
            std::copy(bytes.begin(), bytes.end(), claims.begin() + 5);
        }
    }
    bool warning_near(Pos p, int radius = 2) const {
        const auto warning = decode_warning({claims[5], claims[6], claims[7]});
        if (!warning.fresh(round) || warning.writer == self_index)
            return false;
        const int x0 = (warning.x * geo.width + 15) / 16;
        const int x1 = std::min(geo.width - 1, ((warning.x + 1) * geo.width + 15) / 16 - 1);
        const int y0 = (warning.y * geo.height + 15) / 16;
        const int y1 = std::min(geo.height - 1, ((warning.y + 1) * geo.height + 15) / 16 - 1);
        bool all_visible = true;
        for (int y = y0; y <= y1 && all_visible; ++y)
            for (int x = x0; x <= x1; ++x)
                if (!packed_bit(visible_bytes, geo.index({x, y}))) {
                    all_visible = false;
                    break;
                }
        if (all_visible) {
            bool present = false;
            for (const auto &e : enemies)
                present |= e.pos.x >= x0 && e.pos.x <= x1 && e.pos.y >= y0 && e.pos.y <= y1;
            if (!present)
                return false; // Fresh personal absence outranks a report.
        }
        return distance(p, {std::clamp(p.x, x0, x1), std::clamp(p.y, y0, y1)}) <= radius;
    }
    double exposure(Pos p) const {
        double damage = 0;
        for (const auto &e : enemies)
            if (e.alive && !e.stunned) {
                double cast = 0;
                int d = distance(e.pos, p);
                if (d <= e.range + e.move_speed)
                    damage += e.strength;
                for (const auto &a : e.spells)
                    if (a.cooldown <= 1 && (a.kind == 2 || a.kind == 3 || a.kind == 4) &&
                        d <= a.range + a.radius + (a.exclusive ? 0 : e.move_speed))
                        cast = std::max(cast, a.amount);
                damage += cast;
            }
        return damage;
    }
    std::optional<Pos> toward(Pos target, int range = 0, bool retreat = false) {
        if (!self.can_move || !geo.valid(target) || distance(self.pos, target) <= range ||
            (memory.blocked_round == round && memory.blocked_tile == self.pos) ||
            !fuel(self.move_speed <= 1 ? 18000 : 24000))
            return std::nullopt;
        const std::vector<std::uint16_t> *field = nullptr;
        for (unsigned i = 0; i < geo.altars.size(); ++i)
            if (target == geo.altars[i] && range == 1)
                field = &geo.altar_fields[i];
        if (retreat && in_spawn(target))
            field = &geo.home;
        if (!field && !geo.blocked(target))
            field = geo.goal_field(target, 0);
        if (!field)
            field = geo.goal_field(target, range);
        if (!field)
            return std::nullopt;
        const int current = geo.at(*field, self.pos);
        if (current == 0 || current == unreachable)
            return std::nullopt;
        std::vector<bc::vec2> legal;
        if (self.move_speed <= 1) {
            // Exact one-step native reachable set. Export order follows 8x8
            // storage blocks, then rows inside each block; preserve that order
            // so equally valued legal steps retain the same deterministic tie.
            // Fresh packed blockers suffice; no map-sized host board/export.
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    const Pos p{self.pos.x + dx, self.pos.y + dy};
                    if (free(p))
                        legal.push_back(sdk(p));
                }
            const int stride = (geo.width + 7) / 8;
            const auto native_key = [&](const bc::vec2 &p) {
                return ((p.y / 8) * stride + p.x / 8) * 64 + (p.y % 8) * 8 + p.x % 8;
            };
            std::sort(legal.begin(), legal.end(), [&](const bc::vec2 &a, const bc::vec2 &b) {
                return native_key(a) < native_key(b);
            });
        } else {
            auto block = geo.static_blocked | occupied;
            block.set(sdk(self.pos), false);
            if (memory.blocked_round == round && geo.valid(memory.blocked_tile))
                block.set(sdk(memory.blocked_tile));
            native_context = "route:reachable-tiles";
            legal = block.reachable_tiles(sdk(self.pos), std::max(1, self.move_speed)).positions();
        }
        double best = std::numeric_limits<double>::infinity();
        std::optional<Pos> result;
        for (auto q : legal) {
            Pos p = position(q);
            if (p == self.pos || !free(p))
                continue;
            int d = distance(p, target) <= range ? 0 : geo.at(*field, p);
            if (d == unreachable)
                continue;
            double risk = exposure(p), current_risk = exposure(self.pos);
            if (!retreat && risk > self.hp + self.shield && risk >= current_risk)
                continue;
            double value = d + (retreat ? 10.0 : 2.0) * risk / std::max(1.0, self.hp + self.shield);
            if (d >= current && risk >= current_risk && !retreat) {
                // A local detour may step sideways around a body. Never keep
                // renewing an A-B-A loop under an unchanged mission.
                bool recent = false;
                for (int i = 0; i < std::min(4, memory.route_samples); ++i)
                    recent |= memory.route_history[i] == p;
                if (recent || d > current + 1)
                    continue;
                value += 2;
            }
            if (value < best) {
                best = value;
                result = p;
            }
        }
        return result;
    }
    void refresh(bool self_only = false) {
        native_context = "snapshot:refresh";
        const int previous_round = round;
        round = bc::round_number();
        ++serial;
        self = read_actor(me);
        if (self.alive)
            self_type = self.type;
        else
            self.type = self_type;
        // SDK is_ready checks casting/cooldown; movement exclusivity is enforced
        // separately. A ranged basic also consumes movement, so can_move alone
        // cannot tell these cases apart.
        if (memory.moved_round == round)
            for (auto &spell : self.spells)
                if (spell.exclusive)
                    spell.ready = false;
        gold = me.gold_count();
        spells = self.spells;
        own_score = bc::global_submitted_gems(bc::team::ally);
        enemy_score = bc::global_submitted_gems(bc::team::enemy);
        if (self_only && previous_round == round) {
            // Purchases and self-only casts do not change other units or sight.
            // If execution resumed in a new epoch, refresh everything instead.
            for (auto &ally : allies)
                if (ally.id == self.id)
                    ally = self;
            return;
        }
        allies.clear();
        enemies.clear();
        camp_handles.clear();
        for (unsigned i = 0; i < ally_handles.size(); ++i) {
            auto &c = ally_handles[i];
            if (identity(c) == self.id) {
                if (self.alive)
                    allies.push_back(self);
            } else if (auto snapshot = sdk_222::visible_champion(c)) {
                ensure_visible_kit(c, {snapshot->x, snapshot->y});
                auto a = read_actor(c, *snapshot);
                if (a.alive)
                    allies.push_back(a);
            }
        }
        for (auto &c : enemy_handles)
            if (auto snapshot = sdk_222::visible_champion(c)) {
                ensure_visible_kit(c, {snapshot->x, snapshot->y});
                auto a = read_actor(c, *snapshot);
                if (!a.alive) {
                    for (auto &sight : sightings)
                        if (sight.actor.id == a.id)
                            sight = {a, round};
                    continue;
                }
                enemies.push_back(a);
                auto it = std::find_if(sightings.begin(), sightings.end(),
                                       [&](const auto &t) { return t.actor.id == a.id; });
                if (it == sightings.end())
                    sightings.push_back({a, round});
                else
                    *it = {a, round};
            }
        bc::vision::visible_tiles_into(visible);
        native_context = "snapshot:occupancy";
        const auto visible_camps = bc::vision::camp_tiles();
        occupied = bc::vision::champion_tiles() | visible_camps;
        occupied_bytes = occupied.export_linear_buffer();
        visible_bytes = visible.export_linear_buffer();
        bc::shared_memory.read(0, std::span(claims));
        for (auto &v : groups) {
            v.camps.clear();
            v.known_dead.clear();
        }
        // A camp may walk into sight while all its original spawn tiles are
        // hidden. Combat visibility and group lifecycle visibility differ.
        for (const auto tile : visible_camps.positions()) {
            const int id = sdk_222::visible_camp_identity(position(tile));
            const auto metadata = camp_metadata.find(id);
            if (metadata == camp_metadata.end())
                throw std::runtime_error("visible camp absent from immutable public inventory");
            const auto &c = metadata->second.handle;
            if (auto snapshot = sdk_222::visible_camp(c)) {
                native_context = "snapshot:camp";
                const auto state = c.state();
                if (!state.is_alive())
                    continue;
                const int gi = metadata->second.group;
                Camp a;
                a.id = identity(c);
                a.group = gi;
                a.type = static_cast<int>(c.kind());
                a.pos = {snapshot->x, snapshot->y};
                a.hp = snapshot->health;
                a.max_hp = snapshot->max_health;
                a.strength = snapshot->strength;
                a.range = metadata->second.range;
                a.awake = state.is_awake();
                groups[gi].camps.push_back(a);
                camp_handles.push_back(c);
            }
        }
        for (unsigned i = 0; i < geo.groups.size() && fuel(6500); ++i) {
            auto &v = groups[i];
            bool seen = false;
            for (const auto &s : geo.groups[i].spawns)
                seen |= packed_bit(visible_bytes, geo.index(s.pos));
            if (!seen)
                continue;
            try {
                native_context = "snapshot:group-state";
                auto state = geo.handles[i].state();
                v.seen = round;
                if (std::holds_alternative<bc::map::camp_group_reward_available>(state))
                    v.state = Lifecycle::Reward;
                else if (auto *timer = std::get_if<bc::map::camp_group_respawning>(&state)) {
                    v.state = Lifecycle::Respawning;
                    v.respawn_ticks = timer->timer;
                } else
                    v.state = Lifecycle::Alive;
                for (const auto &camp : geo.handles[i].camps()) {
                    const int id = identity(camp);
                    if (std::any_of(v.camps.begin(), v.camps.end(),
                                    [&](const Camp &known) { return known.id == id; }))
                        continue; // This exact snapshot already observed it alive.
                    try {
                        if (camp.state() == bc::camp_state::dead)
                            v.known_dead.push_back(identity(camp));
                    } catch (const bc::error &e) {
                        if (e.code() != bc::error_code::api_not_in_vision)
                            throw;
                    }
                }
            } catch (const bc::error &e) {
                if (e.code() != bc::error_code::api_not_in_vision)
                    throw;
            }
        }
    }
    void refresh_local_effects(const Action &action) {
        const int epoch = round;
        refresh(true);
        if (round != epoch)
            return; // refresh() already replaced the entire new owner snapshot.
        if (!self.alive) {
            refresh();
            return;
        }
        // A stationary hit/cast cannot move observers. No opponent takes an
        // action between our commands, so refresh only units it can change.
        // Ground AoE, retaliation and Cassi/Issac links can affect several
        // currently observed actors; all of those records are re-read.
        for (auto &list : {&allies, &enemies})
            for (auto &actor : *list) {
                if (actor.id == self.id)
                    continue;
                const auto handle = champion(actor.id);
                if (handle) {
                    if (auto snapshot = sdk_222::visible_champion(*handle))
                        actor = read_actor(*handle, *snapshot);
                    else
                        actor.alive = false; // Drop a record no longer observed after the effect.
                } else
                    actor.alive = false;
            }
        for (const auto &actor : enemies)
            for (auto &sight : sightings)
                if (sight.actor.id == actor.id)
                    sight = {actor, round};
        for (auto &list : {&allies, &enemies})
            list->erase(
                std::remove_if(list->begin(), list->end(), [](const Actor &a) { return !a.alive; }),
                list->end());
        const bool camp_effect = action.kind == Kind::BasicCamp || action.kind == Kind::CastCamp ||
                                 (action.kind == Kind::BasicChampion && self.type == 10) ||
                                 action.kind == Kind::CastGround;
        if (camp_effect)
            for (unsigned gi = 0; gi < groups.size(); ++gi) {
                auto &view = groups[gi];
                bool changed = false;
                for (auto &camp : view.camps) {
                    for (const auto &handle : camp_handles)
                        if (identity(handle) == camp.id) {
                            const auto flags = handle.state();
                            if (!flags.is_alive()) {
                                camp.hp = 0;
                                view.known_dead.push_back(camp.id);
                                changed = true;
                                break;
                            }
                            if (auto state = sdk_222::visible_camp(handle)) {
                                camp.hp = state->health;
                                camp.awake = flags.is_awake();
                                changed = true;
                            }
                            break;
                        }
                }
                view.camps.erase(std::remove_if(view.camps.begin(), view.camps.end(),
                                                [](const Camp &c) { return c.hp <= 0; }),
                                 view.camps.end());
                if (changed && view.fresh(round)) {
                    const auto state = geo.handles[gi].state();
                    if (std::holds_alternative<bc::map::camp_group_reward_available>(state))
                        view.state = Lifecycle::Reward;
                    else if (auto *timer = std::get_if<bc::map::camp_group_respawning>(&state)) {
                        view.state = Lifecycle::Respawning;
                        view.respawn_ticks = timer->timer;
                    }
                }
            }
        occupied = bc::vision::champion_tiles() | bc::vision::camp_tiles();
        occupied_bytes = occupied.export_linear_buffer();
    }
};
} // namespace tactics

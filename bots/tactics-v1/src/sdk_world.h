#pragma once
#include "geometry.h"
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
    bc::detail::camp_state value{};
    const auto code = bc::detail::sdk_camp(static_cast<std::uint32_t>(identity(c)), &value);
    if (code == static_cast<std::int32_t>(bc::error_code::api_not_in_vision) ||
        code == static_cast<std::int32_t>(bc::error_code::api_not_found))
        return std::nullopt;
    bc::detail::check(code);
    return value;
}
} // namespace sdk_222
inline Spell read_spell(const bc::ability &a, bool can_cast) {
    Spell s;
    s.slot = a.slot();
    auto info = a.info();
    if (!info)
        return s;
    std::visit(
        [&](const auto &p) {
            s.kind = static_cast<int>(p.kind);
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
    std::vector<GroupView> groups;
    std::vector<Sighting> sightings;
    int combat_cache_serial = -1;
    std::map<std::pair<int, int>, std::vector<Pos>> combat_reach_cache;
    bc::bitboard visible, occupied;
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
        return geo.valid(p) && geo.own_spawn.is_set(sdk(p));
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
        return !geo.blocked(p) && (p == self.pos || !occupied.is_set(sdk(p))) &&
               !(memory.blocked_round == round && memory.blocked_tile == p);
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
        if (!self.can_move || !geo.valid(target) || !fuel(9000))
            return std::nullopt;
        auto block = geo.static_blocked | occupied;
        block.set(sdk(self.pos), false);
        if (memory.blocked_round == round && geo.valid(memory.blocked_tile))
            block.set(sdk(memory.blocked_tile));
        bc::bitboard roots;
        for (int y = target.y - range; y <= target.y + range; ++y)
            for (int x = target.x - range; x <= target.x + range; ++x) {
                Pos p{x, y};
                if (geo.valid(p) && !block.is_set(sdk(p)))
                    roots.set(sdk(p));
            }
        if (roots.count() == 0)
            return std::nullopt;
        bc::distance_field field;
        bc::bitboard reached;
        field.compute(block, roots, reached);
        const int current = field.get(sdk(self.pos));
        auto legal = block.reachable_tiles(sdk(self.pos), std::max(1, self.move_speed)).positions();
        double best = std::numeric_limits<double>::infinity();
        std::optional<Pos> result;
        for (auto q : legal) {
            Pos p = position(q);
            if (p == self.pos || !free(p))
                continue;
            int d = field.get(q);
            if (d == unreachable)
                continue;
            double risk = exposure(p), current_risk = exposure(self.pos);
            if (!retreat && risk > self.hp + self.shield && risk >= current_risk)
                continue;
            double value = d + (retreat ? 10.0 : 2.0) * risk / std::max(1.0, self.hp + self.shield);
            if (d >= current && risk >= current_risk && !retreat)
                continue;
            if (value < best) {
                best = value;
                result = p;
            }
        }
        return result;
    }
    void refresh(bool self_only = false) {
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
                if (!a.alive)
                    continue;
                enemies.push_back(a);
                auto it = std::find_if(sightings.begin(), sightings.end(),
                                       [&](const auto &t) { return t.actor.id == a.id; });
                if (it == sightings.end())
                    sightings.push_back({a, round});
                else
                    *it = {a, round};
            }
        bc::vision::visible_tiles_into(visible);
        occupied = bc::vision::champion_tiles() | bc::vision::camp_tiles();
        bc::shared_memory.read(0, std::span(claims));
        for (auto &v : groups) {
            v.seen = -1;
            v.camps.clear();
            v.known_dead.clear();
        }
        // A camp may walk into sight while all its original spawn tiles are
        // hidden. Combat visibility and group lifecycle visibility differ.
        for (const auto &c : bc::vision::camps())
            if (auto snapshot = sdk_222::visible_camp(c)) {
                const auto state = c.state();
                if (!state.is_alive())
                    continue;
                int gi = -1;
                for (unsigned i = 0; i < geo.groups.size() && gi < 0; ++i)
                    for (const auto &s : geo.groups[i].spawns)
                        if (s.id == identity(c)) {
                            gi = i;
                            break;
                        }
                if (gi < 0)
                    continue;
                Camp a;
                a.id = identity(c);
                a.group = gi;
                a.type = static_cast<int>(c.kind());
                a.pos = {snapshot->x, snapshot->y};
                a.hp = snapshot->health;
                a.max_hp = snapshot->max_health;
                a.strength = snapshot->strength;
                a.range = c.attack_range();
                a.awake = state.is_awake();
                groups[gi].camps.push_back(a);
                camp_handles.push_back(c);
            }
        for (unsigned i = 0; i < geo.groups.size() && fuel(6500); ++i) {
            auto &v = groups[i];
            bool seen = false;
            for (const auto &s : geo.groups[i].spawns)
                seen |= visible.is_set(sdk(s.pos));
            if (!seen)
                continue;
            try {
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
};
} // namespace tactics

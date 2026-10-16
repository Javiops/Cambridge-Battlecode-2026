#pragma once
#include "types.h"
#include <span>
#ifndef TACTICS_COMBAT_MODEL_ONLY
#include "sdk_world.h"
#endif

namespace tactics {
namespace combat_detail {
inline constexpr int ren_type = 9, marcella_type = 7, cassi_type = 3, issac_type = 4;

inline bool offensive(const Spell &s) {
    return s.kind == 2 || s.kind == 3 || s.kind == 4;
}
inline bool plausible_ready(const Spell &s, int horizon = 1) {
    // Visible completed-turn flags are not a promise of inactivity next round.
    return s.kind != 0 && (s.ready || s.cooldown < 0 || s.cooldown <= horizon);
}
inline double basic_hp_damage(const Actor &from, const Actor &target) {
    // No undocumented enhanced-attack damage multiplier is invented here.
    return std::min(target.hp, std::max(0.0, from.strength * target.mitigation - target.shield));
}
inline double returned_damage(const Actor &from, const Actor &target, bool primary = true) {
    // The optional false case is specifically a secondary Varg basic, whose
    // no-return boundary is confirmed in the pinned current engine.
    return primary && target.type == ren_type
               ? std::max(0.0, .2 * target.focus * from.mitigation - from.shield)
               : 0.0;
}
inline bool direct_hit_survives(const Actor &from, const Actor &target) {
    return from.hp > returned_damage(from, target);
}
inline constexpr int recent_sighting_horizon = 3; // Initial bounded setting, not an optimum.
inline bool recent_sighting(int age) {
    return age >= 1 && age <= recent_sighting_horizon;
}

// One successful cast is shared by all slots. A reset alternative cannot also
// add a damaging spell, and a ranged walk cannot also claim an ordinary basic.
// `move_distance` is the known walk distance, not center-line distance.
inline double reply_raw(const Actor &e, Pos victim, int move_distance, int horizon = 1) {
    if (!e.alive)
        return 0;
    const int d = distance(e.pos, victim), moves = std::max(0, horizon) * std::max(1, e.move_speed);
    const bool stationary_basic = d <= e.range;
    const bool moved_basic = e.range <= 1 && move_distance <= e.range + moves;
    double best = stationary_basic || moved_basic ? e.strength : 0.0;
    for (const auto &s : e.spells)
        if (plausible_ready(s, horizon)) {
            if (s.kind == 1) {
                double value = stationary_basic || moved_basic ? 2 * e.strength : 0.0;
                if (e.range > 1 && move_distance <= e.range + moves)
                    value = std::max(value, e.strength);
                best = std::max(best, value);
            } else if (offensive(s) && (s.enemies || s.ground)) {
                const int reach = s.range + (s.kind == 3 ? s.radius : 0);
                if (d <= reach)
                    best = std::max(best,
                                    std::max(0.0, s.amount) + (stationary_basic ? e.strength : 0));
                if (!s.exclusive && move_distance <= reach + moves)
                    best = std::max(best, std::max(0.0, s.amount) + (moved_basic ? e.strength : 0));
            } else if (s.kind == 6 && d <= s.range + e.range) {
                // A dash is a separate terrain transition. This conservative upper
                // estimate does not assert that its hidden landing will be legal.
                best = std::max(best, e.strength);
            }
        }
    return best;
}

// SDK-free uncertainty model helpers are shared by production and unit tests.
inline std::vector<Pos> expand_region(int width, int height,
                                      const std::vector<std::uint8_t> &terrain,
                                      const std::vector<Pos> &origins, int steps, int dash = 0) {
    auto valid = [&](Pos p) { return p.x >= 0 && p.y >= 0 && p.x < width && p.y < height; };
    auto blocked = [&](Pos p) {
        if (!valid(p))
            return true;
        int index = p.y * width + p.x;
        return index / 8 >= static_cast<int>(terrain.size()) ||
               (terrain[index / 8] & (1u << (index % 8))) != 0;
    };
    const int count = std::max(0, width * height);
    std::vector<std::uint64_t> marked((count + 63) / 64);
    std::vector<std::pair<Pos, int>> queue;
    auto add = [&](Pos p, int depth) {
        if (blocked(p))
            return;
        int i = p.y * width + p.x;
        auto bit = std::uint64_t(1) << (i % 64);
        if (marked[i / 64] & bit)
            return;
        marked[i / 64] |= bit;
        queue.emplace_back(p, depth);
    };
    for (auto p : origins)
        add(p, 0);
    if (dash > 0)
        for (auto p : origins)
            for (int dy = -dash; dy <= dash; ++dy)
                for (int dx = -dash; dx <= dash; ++dx)
                    add({p.x + dx, p.y + dy}, 0);
    const int bound = std::clamp(steps, 0, 8);
    for (std::size_t i = 0; i < queue.size(); ++i)
        if (queue[i].second < bound) {
            const auto [p, depth] = queue[i];
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx)
                    if (dx || dy)
                        add({p.x + dx, p.y + dy}, depth + 1);
        }
    std::vector<Pos> result;
    result.reserve(queue.size());
    for (const auto &q : queue)
        result.push_back(q.first);
    return result;
}
inline std::vector<Pos> remove_visible_absence(std::vector<Pos> origins, int width,
                                               const std::vector<std::uint8_t> &visible,
                                               const std::vector<Actor> &enemies, int id) {
    origins.erase(std::remove_if(origins.begin(), origins.end(),
                                 [&](Pos p) {
                                     int index = p.y * width + p.x;
                                     if (index < 0 ||
                                         index / 8 >= static_cast<int>(visible.size()) ||
                                         !(visible[index / 8] & (1u << (index % 8))))
                                         return false;
                                     for (const auto &e : enemies)
                                         if (e.id == id && e.pos == p)
                                             return false;
                                     return true;
                                 }),
                  origins.end());
    return origins;
}
inline double region_reply_span(const Actor &e, std::span<const Pos> current,
                                std::span<const Pos> future, Pos at, int horizon = 1) {
    if (!e.alive || current.empty())
        return 0;
    auto near = [&](const auto &region, int range) {
        for (auto p : region)
            if (distance(p, at) <= range)
                return true;
        return false;
    };
    const bool stationary_basic = near(current, e.range),
               moved_basic = e.range <= 1 && near(future, e.range);
    double best = stationary_basic || moved_basic ? e.strength : 0.0;
    for (const auto &s : e.spells)
        if (plausible_ready(s, horizon)) {
            if (s.kind == 1) {
                double value = stationary_basic || moved_basic ? 2 * e.strength : 0.0;
                if (e.range > 1 && near(future, e.range))
                    value = std::max(value, e.strength);
                best = std::max(best, value);
            } else if (offensive(s) && (s.enemies || s.ground)) {
                const int reach = s.range + (s.kind == 3 ? s.radius : 0);
                if (near(current, reach))
                    best = std::max(best,
                                    std::max(0.0, s.amount) + (stationary_basic ? e.strength : 0));
                if (!s.exclusive && near(future, reach))
                    best = std::max(best, std::max(0.0, s.amount) + (moved_basic ? e.strength : 0));
            } else if (s.kind == 6 && near(current, s.range + e.range))
                best = std::max(best, e.strength);
        }
    return best;
}
inline double region_reply_raw(const Actor &e, const std::vector<Pos> &current,
                               const std::vector<Pos> &future, Pos at, int horizon = 1) {
    return region_reply_span(e, current, future, at, horizon);
}
inline Pos geometric_approach(Pos from, Pos to, int steps) {
    const int dx = std::clamp(to.x - from.x, -steps, steps),
              dy = std::clamp(to.y - from.y, -steps, steps);
    return {from.x + dx, from.y + dy};
}
inline double long_window_reply_upper(const Actor &e, Pos from, Pos at, int horizon) {
    // Bounded native reach is limited to eight steps. Longer channel windows
    // use a deliberately conservative geometric approach, never a fabricated
    // reachable route. Earlier walking can precede a later exclusive cast or
    // stationary ranged basic; exclusivity is not a whole-channel restriction.
    const int speed = std::max(1, e.move_speed);
    const std::array<Pos, 1> before{geometric_approach(from, at, std::max(0, horizon - 1) * speed)};
    const std::array<Pos, 1> after{geometric_approach(from, at, horizon * speed)};
    return region_reply_span(e, before, after, at, horizon);
}
inline double coarse_remembered_reply(Actor e, int age, Pos at, int horizon) {
    // A low-budget risk envelope, never a targetable hidden location. It can
    // overestimate paths through terrain, but must not erase a missing threat.
    int past_dash = 0;
    for (auto &s : e.spells) {
        if (s.kind == 6 && (s.cooldown < 0 || s.cooldown <= age))
            past_dash = std::max(past_dash, s.range);
        if (s.cooldown >= 0)
            s.cooldown = std::max(0, s.cooldown - age);
    }
    const Pos origin = geometric_approach(e.pos, at, age * std::max(1, e.move_speed) + past_dash);
    return long_window_reply_upper(e, origin, at, horizon);
}
inline int plausible_dash(const Actor &e, int elapsed) {
    int dash = 0;
    for (const auto &s : e.spells)
        if (s.kind == 6 && (s.cooldown < 0 || s.cooldown <= elapsed))
            dash = std::max(dash, s.range);
    return dash;
}

#ifndef TACTICS_COMBAT_MODEL_ONLY
inline void ensure_reach_cache(World &w) {
    if (w.combat_cache_serial != w.serial) {
        w.combat_reach_cache.clear();
        w.combat_cache_serial = w.serial;
    }
}
inline const bc::bitboard &enemy_walking_blockers(World &w) {
    return w.geo.enemy_blocked;
}
inline const std::vector<Pos> &enemy_positions(World &w, const Actor &e, int horizon) {
    ensure_reach_cache(w);
    auto key = std::make_pair(e.id, std::clamp(horizon, 0, 8));
    auto found = w.combat_reach_cache.find(key);
    if (found != w.combat_reach_cache.end())
        return found->second;
    // Bounded native reach, not a fresh whole-map field for every micro tile.
    // Enemy walking may leave its own spawn, but cannot enter our spawn.
    const auto &block = enemy_walking_blockers(w);
    const int steps = std::clamp(horizon * std::max(1, e.move_speed), 0, 8);
    auto reachable = block.reachable_tiles(sdk(e.pos), steps).positions();
    std::vector<Pos> result;
    result.reserve(reachable.size() + 1);
    result.push_back(e.pos);
    for (auto p : reachable)
        if (position(p) != e.pos)
            result.push_back(position(p));
    return w.combat_reach_cache.emplace(key, std::move(result)).first->second;
}

// Expand a small multi-origin uncertainty region against packed public terrain.
// There are no host queries per BFS neighbor and no hidden entity inspection.
inline std::vector<Pos> expand_origins(World &w, const std::vector<Pos> &origins, int steps,
                                       int dash = 0) {
    return expand_region(w.geo.width, w.geo.height, w.geo.enemy_terrain, origins, steps, dash);
}
inline const std::vector<Pos> &remembered_positions(World &w, const Sighting &sight, int horizon,
                                                    bool future) {
    const int age = w.round - sight.round;
    ensure_reach_cache(w);
    // The current region does not depend on the requested future horizon.
    // Reuse it across farm, micro and channel checks in this world snapshot.
    const auto key = std::make_pair(sight.actor.id, (future ? 200 : 100) + age * 16 +
                                                        (future ? std::clamp(horizon, 0, 8) : 0));
    auto found = w.combat_reach_cache.find(key);
    if (found != w.combat_reach_cache.end())
        return found->second;
    if (future && remembered_positions(w, sight, 0, false).empty())
        return w.combat_reach_cache.emplace(key, std::vector<Pos>{}).first->second;
    const int elapsed = age + (future ? horizon : 0),
              steps = elapsed * std::max(1, sight.actor.move_speed),
              dash = plausible_dash(sight.actor, elapsed);
    std::vector<Pos> origins;
    if (!dash && steps <= 8)
        origins = enemy_positions(w, sight.actor, elapsed);
    else {
        // One bounded legal-landing square replaces multi-origin nested dash
        // expansions. It is a conservative possibility envelope; it does not
        // certify any particular hidden walking or dash trajectory.
        origins = expand_origins(w, {sight.actor.pos}, 0, steps + dash);
    }
    if (!future)
        origins =
            remove_visible_absence(std::move(origins), w.geo.width,
                                   w.visible.export_linear_buffer(), w.enemies, sight.actor.id);
    // Empty tiles now are valid future arrivals, so only prune the current set.
    return w.combat_reach_cache.emplace(key, std::move(origins)).first->second;
}
inline double remembered_raw(World &w, const Sighting &sight, Pos at, int horizon = 1) {
    const int age = w.round - sight.round;
    if (!recent_sighting(age) || !sight.actor.alive)
        return 0;
    for (const auto &e : w.enemies)
        if (e.id == sight.actor.id)
            return 0; // Count each enemy once.
    // Region construction has a larger bounded cost than a visible one-step
    // reply. Fall back before that optional work can consume the action budget.
    const int uncertainty_extent = (age + horizon) * std::max(1, sight.actor.move_speed) +
                                   plausible_dash(sight.actor, age + horizon);
    // Large hidden origin regions are not worth several owner opportunities.
    // Retain a conservative scalar possibility instead of expanding them.
    if (horizon > 8 || uncertainty_extent > 2 || !fuel(50000))
        return coarse_remembered_reply(sight.actor, age, at, horizon);
    Actor e = sight.actor;
    for (auto &s : e.spells)
        if (s.cooldown >= 0)
            s.cooldown = std::max(0, s.cooldown - age);
    const auto &current = remembered_positions(w, sight, horizon, false);
    if (current.empty())
        return 0;
    if (!fuel(24000))
        return coarse_remembered_reply(sight.actor, age, at, horizon);
    const auto &future = remembered_positions(w, sight, horizon, true);
    return region_reply_raw(e, current, future, at, horizon);
}

inline double enemy_raw(World &w, const Actor &e, Pos at, int horizon = 1) {
    if (!e.alive)
        return 0;
    // Preserve a legal action and refresh reserve. The coarse envelope may
    // overestimate contact through terrain, but never certifies a blind route
    // as safe merely because another native reach search cannot be afforded.
    if (bc::fuel_remaining() < 24000)
        return long_window_reply_upper(e, e.pos, at, horizon);
    if (horizon > 8 || horizon * std::max(1, e.move_speed) > 8)
        return long_window_reply_upper(e, e.pos, at, horizon);
    const int d = distance(e.pos, at),
              moves = std::clamp(horizon * std::max(1, e.move_speed), 0, 8);
    int maximum = e.range + moves;
    for (const auto &s : e.spells)
        if (plausible_ready(s, horizon))
            maximum = std::max(maximum,
                               s.range + s.radius +
                                   (s.exclusive ? std::max(0, horizon - 1) * e.move_speed : moves) +
                                   e.range * (s.kind == 6));
    if (d > maximum)
        return 0;
    if (horizon > 1)
        return region_reply_raw(e, enemy_positions(w, e, horizon - 1),
                                enemy_positions(w, e, horizon), at, horizon);
    const auto &positions = enemy_positions(w, e, horizon);
    int walk = unreachable;
    for (auto p : positions)
        if (distance(p, at) <= std::max(e.range, 1))
            walk = std::min(walk, distance(e.pos, p) + distance(p, at));
    // A compatible long-range cast may have a useful destination farther from
    // basic range. Check its actual reachable region instead of crossing walls.
    double value = reply_raw(e, at, walk, horizon);
    for (const auto &s : e.spells)
        if (plausible_ready(s, horizon) && offensive(s) && !s.exclusive &&
            (s.enemies || s.ground)) {
            const int reach = s.range + (s.kind == 3 ? s.radius : 0);
            for (auto p : positions)
                if (distance(p, at) <= reach) {
                    value = std::max(
                        value, std::max(0.0, s.amount) +
                                   (e.range <= 1 && distance(p, at) <= e.range ? e.strength : 0));
                    break;
                }
        }
    return value;
}

inline double incoming_for(World &w, const Actor &victim, Pos at, int horizon = 1,
                           bool include_camps = true, int waking_group = -1) {
    double enemy = 0, monster = 0;
    for (const auto &e : w.enemies)
        enemy += enemy_raw(w, e, at, horizon);
    for (const auto &sight : w.sightings)
        enemy += remembered_raw(w, sight, at, horizon);
    if (include_camps)
        for (unsigned g = 0; g < w.groups.size(); ++g)
            for (const auto &c : w.groups[g].camps)
                if (c.hp > 0 && (c.awake || static_cast<int>(g) == waking_group) &&
                    distance(c.pos, at) <= c.range + std::max(1, horizon))
                    monster += c.strength;
    // Longer channels have repeated exposure. This is deliberately a coarse
    // conservative bound, not a recovered opponent schedule/probability model.
    const double raw =
        (enemy * victim.mitigation + monster * victim.camp_mitigation) * std::max(1, horizon);
    return std::max(0.0, raw - victim.shield);
}

inline double spell_hp_damage(World &w, const Spell &s, const Actor &target) {
    if (!offensive(s))
        return 0;
    auto handle = w.champion(target.id);
    if (handle)
        try {
            return w.me.abilities()[s.slot].damage_amount(*handle);
        } catch (const bc::error &) {
        }
    return std::min(target.hp, std::max(0.0, s.amount * target.mitigation - target.shield));
}
inline bool can_cast_at(const World &w, const Spell &s, const Actor &target) {
    return w.self.can_cast && s.ready && s.enemies && distance(w.self.pos, target.pos) <= s.range;
}
inline double target_importance(const Actor &e) {
    return 1.0 + std::min(1.0, e.gems / 50.0) + (e.channel == Channel::Tribute ? 1.0 : 0.0);
}
inline double basic_splash_value(const World &w, const Actor &primary) {
    if (w.self.type != 10)
        return 0;
    double value = 0;
    for (const auto &other : w.enemies)
        if (other.id != primary.id && other.alive && distance(other.pos, primary.pos) <= 1) {
            // Secondary splash is not another selected direct target, and in this
            // engine it does not add Ren's direct-hit retaliation.
            const double hit = basic_hp_damage(w.self, other);
            value += hit + (hit >= other.hp - .001 ? 300 + other.gems * 2 : 0);
        }
    return value;
}
inline double linked_removal_value(const World &w, const Actor &target, double hit) {
    if (hit < target.hp - .001 || (target.type != cassi_type && target.type != issac_type))
        return 0;
    const int partner = target.type == cassi_type ? issac_type : cassi_type;
    for (const auto &other : w.enemies)
        if (other.alive && other.type == partner)
            return 300 + other.gems * 2;
    // A hidden partner's live HP/bag is not fabricated. Known link mechanics
    // still inform our self-survival; the bonus only uses observed recipients.
    return 0;
}
inline Proposal proposal(const Action &action, Phase phase, Priority priority, double value,
                         const Memory &memory, int round) {
    Proposal p;
    p.action = action;
    p.mission = memory.mission;
    p.mission.phase = phase;
    p.mission.expiry = round + Settings::job_lease;
    p.priority = priority;
    p.value = value;
    p.valid = true;
    return p;
}
inline Action cast_unit(const Spell &s, int target, const char *reason) {
    Action a;
    a.kind = Kind::CastChampion;
    a.target = target;
    a.slot = s.slot;
    a.reason = reason;
    return a;
}
inline Action cast_self(const Spell &s, const char *reason) {
    Action a;
    a.kind = Kind::CastSelf;
    a.slot = s.slot;
    a.reason = reason;
    return a;
}
inline Action move(Pos at, const char *reason) {
    Action a;
    a.kind = Kind::Move;
    a.at = at;
    a.reason = reason;
    return a;
}
}

inline double incoming_damage(World &w, Pos at, int horizon = 1, bool include_camps = true) {
    return combat_detail::incoming_for(w, w.self, at, std::max(1, horizon), include_camps);
}

inline bool farm_safe(World &w, int group) {
    if (!w.self.alive || w.self.channel != Channel::None || group < 0 ||
        group >= static_cast<int>(w.groups.size()))
        return false;
    const auto &v = w.groups[group];
    if (v.state == Lifecycle::Reward)
        return true; // Physical hold safety is checked separately.
    if (v.camps.empty())
        return false; // Missing observation is not an empty safe camp.
    const double reply = combat_detail::incoming_for(w, w.self, w.self.pos, 1, true, group);
    bool enemy_can_punish = false;
    for (const auto &e : w.enemies)
        enemy_can_punish |= combat_detail::enemy_raw(w, e, w.self.pos) > 0;
    for (const auto &s : w.sightings)
        enemy_can_punish |= combat_detail::remembered_raw(w, s, w.self.pos) > 0;
    const double floor = (enemy_can_punish ? .35 : .25) * w.self.max_hp;
    // This guard does not divide monster damage by geometric ally headcount.
    // It remains deliberately local; readiness/assembly is the mission gate.
    return w.self.hp - reply > floor;
}

inline std::optional<Action> escape_action(World &w) {
    using namespace combat_detail;
    if (!w.self.alive || w.self.channel != Channel::None)
        return std::nullopt;
    // Do not spend the farming opportunity evaluating an empty fight. This is
    // an eligibility test, not a zero-risk assumption about missing enemies.
    bool opportunity = !w.enemies.empty();
    for (const auto &sight : w.sightings)
        opportunity |= sight.actor.alive && recent_sighting(w.round - sight.round);
    for (const auto &group : w.groups)
        for (const auto &camp : group.camps)
            opportunity |=
                camp.hp > 0 && camp.awake && distance(camp.pos, w.self.pos) <= camp.range + 1;
    if (w.self.can_cast)
        for (const auto &spell : w.spells)
            if (spell.ready && spell.kind == 5 && spell.allies)
                for (const auto &ally : w.allies)
                    opportunity |= ally.id != w.self.id && ally.alive && ally.hp < ally.max_hp &&
                                   distance(w.self.pos, ally.pos) <= spell.range;
    if (!opportunity)
        return std::nullopt;
    const double current = incoming_damage(w, w.self.pos);
    double best = current;
    int best_home = w.home_distance(w.self.pos);
    std::optional<Action> result;
    if (w.self.can_move) {
        auto blocked = w.geo.static_blocked | w.occupied;
        blocked.set(sdk(w.self.pos), false);
        for (auto q :
             blocked.reachable_tiles(sdk(w.self.pos), std::max(1, w.self.move_speed)).positions()) {
            if (bc::fuel_remaining() < 24000)
                break;
            Pos p = position(q);
            if (p == w.self.pos || !w.free(p))
                continue;
            const double risk = incoming_damage(w, p);
            const int home = w.home_distance(p);
            if (risk < best - .01 || (risk <= best + .01 && home < best_home)) {
                best = risk;
                best_home = home;
                result = move(p, "escape-walk");
            }
        }
    }
    if (w.self.can_cast)
        for (const auto &s : w.spells)
            if (s.ready) {
                if (s.kind == 6 && s.ground) {
                    if (!fuel(24000))
                        continue;
                    // Native 0.0.2 permits bending around a wall and crossing
                    // holes and altars, but walls, units and enemy spawn block the
                    // traversal. valid_tiles() supplies RANGE ONLY; landing
                    // and the actual short dash path are separate checks.
                    auto path_blockers = bc::map::walls() | w.geo.enemy_spawn | w.occupied |
                                         bc::vision::teleport_tiles();
                    path_blockers.set(sdk(w.self.pos), false);
                    auto destinations = path_blockers.reachable_tiles(sdk(w.self.pos), s.range);
                    destinations &= w.me.abilities()[s.slot].valid_tiles();
                    destinations &= ~(w.geo.static_blocked | w.occupied);
                    for (auto raw : destinations.positions()) {
                        if (bc::fuel_remaining() < 24000)
                            break;
                        Pos p = position(raw);
                        if (p == w.self.pos || !w.free(p))
                            continue;
                        const double risk = incoming_damage(w, p);
                        const int home = w.home_distance(p);
                        if (risk < best - .01 || (risk <= best + .01 && home < best_home)) {
                            Action a;
                            a.kind = Kind::CastGround;
                            a.slot = s.slot;
                            a.at = p;
                            a.reason = "escape-dash";
                            result = a;
                            best = risk;
                            best_home = home;
                        }
                    }
                } else if (s.kind == 7 && s.self && s.amount > w.self.shield) {
                    const double after = std::max(0.0, current - (s.amount - w.self.shield));
                    if (after < best - .01) {
                        result = cast_self(s, "escape-shield");
                        best = after;
                    }
                } else if (s.kind == 4 && s.enemies) {
                    for (const auto &e : w.enemies)
                        if (e.alive && e.type != marcella_type && can_cast_at(w, s, e) &&
                            direct_hit_survives(w.self, e)) {
                            const double after = std::max(
                                0.0, current - enemy_raw(w, e, w.self.pos) * w.self.mitigation);
                            if (after < best - .01) {
                                result = cast_unit(s, e.id, "escape-control");
                                best = after;
                            }
                        }
                }
            }
    // A pointless side-step is not an escape. Homeward progress on a risk tie
    // remains useful, but no action is manufactured when nothing improves.
    return result;
}

inline std::optional<Proposal> combat_proposal(World &w, Memory &memory,
                                               bool farming_context = false) {
    using namespace combat_detail;
    if (!w.self.alive || w.self.channel != Channel::None)
        return std::nullopt;
    const double incoming = incoming_damage(w, w.self.pos);
    const bool endangered =
        incoming >= w.self.hp * .80 || (incoming > 0 && w.self.health_fraction() < .35);
    std::array<std::vector<std::pair<int, double>>, 2> damage_cache;
    auto spell_damage = [&](const Spell &s, const Actor &target) {
        if (s.slot < 0 || s.slot > 1)
            return 0.0;
        for (const auto &entry : damage_cache[s.slot])
            if (entry.first == target.id)
                return entry.second;
        double value =
            bc::fuel_remaining() < 24000
                ? std::min(target.hp, std::max(0.0, s.amount * target.mitigation - target.shield))
                : spell_hp_damage(w, s, target);
        damage_cache[s.slot].push_back({target.id, value});
        return value;
    };
    std::vector<std::pair<int, double>> ally_danger_cache;
    auto ally_danger = [&](const Actor &ally) {
        for (const auto &entry : ally_danger_cache)
            if (entry.first == ally.id)
                return entry.second;
        const double value = incoming_for(w, ally, ally.pos);
        ally_danger_cache.push_back({ally.id, value});
        return value;
    };

    // First compare verified removal of a lethal contributor with escape.
    // Target-aware spell health loss is used; returned damage is paid even for
    // a lethal or fully shielded direct hit on Ren.
    if (endangered)
        for (const auto &e : w.enemies)
            if (e.alive && direct_hit_survives(w.self, e)) {
                const double return_raw = e.type == ren_type ? .2 * e.focus * w.self.mitigation : 0;
                // incoming already charged the current shield once. Do not spend that
                // same shield a second time on retaliation in this combined reply.
                const double remaining = std::max(
                    0.0, incoming - enemy_raw(w, e, w.self.pos) * w.self.mitigation + return_raw);
                if (remaining >= w.self.hp)
                    continue;
                for (const auto &s : w.spells)
                    if (can_cast_at(w, s, e) && offensive(s) && spell_damage(s, e) >= e.hp - .001)
                        return proposal(cast_unit(s, e.id, "survival-remove-threat"), Phase::Fight,
                                        Priority::Survival, 10000 + e.gems, memory, w.round);
                if (w.self.can_attack && distance(w.self.pos, e.pos) <= w.self.range &&
                    basic_hp_damage(w.self, e) >= e.hp - .001) {
                    Action a;
                    a.kind = Kind::BasicChampion;
                    a.target = e.id;
                    a.reason = "survival-lethal-basic";
                    return proposal(a, Phase::Fight, Priority::Survival, 10000 + e.gems, memory,
                                    w.round);
                }
            }
    if (endangered)
        if (auto a = escape_action(w))
            return proposal(*a, Phase::Escape, Priority::Survival, 20000 + incoming, memory,
                            w.round);

    // Local protection is an actual useful cast on an observed ally, not a
    // geometric count of nominal helpers. No remote readiness is assumed.
    if (w.self.can_cast && incoming < w.self.hp && fuel(22000))
        for (const auto &s : w.spells)
            if (s.ready && s.kind == 5 && s.allies) {
                const Actor *selected = nullptr;
                double best = 0;
                for (const auto &ally : w.allies)
                    if (ally.id != w.self.id && ally.alive &&
                        distance(w.self.pos, ally.pos) <= s.range) {
                        const double heal =
                            std::min(s.amount, std::max(0.0, ally.max_hp - ally.hp));
                        if (heal <= 0)
                            continue;
                        if (!fuel(18000))
                            break;
                        const double danger = ally_danger(ally);
                        const bool saved = danger >= ally.hp && danger < ally.hp + heal;
                        double value = heal + (saved ? 10000.0 : 0) +
                                       (danger > 0 ? std::min(500, ally.gems * 5) : 0);
                        if (heal > 0 && value > best) {
                            best = value;
                            selected = &ally;
                        }
                    }
                if (selected && best >= 10000)
                    return proposal(cast_unit(s, selected->id, "protect-lethal-heal"),
                                    Phase::Protect, Priority::Survival, best, memory, w.round);
            }

    // A local peel is useful when it removes a real contributor before that
    // contributor's next response, not merely because an ally is nearby.
    if (w.self.can_cast && !w.enemies.empty() && incoming < w.self.hp && fuel(22000))
        for (const auto &s : w.spells)
            if (s.ready && s.kind == 4 && s.enemies && s.duration > 0) {
                for (const auto &ally : w.allies)
                    if (ally.id != w.self.id && ally.alive) {
                        if (!fuel(18000))
                            break;
                        const double danger = ally_danger(ally);
                        if (danger < ally.hp * .60 && !(ally.gems >= 10 && danger > 0))
                            continue;
                        for (const auto &e : w.enemies)
                            if (e.type != marcella_type && can_cast_at(w, s, e) &&
                                direct_hit_survives(w.self, e)) {
                                const double removed = enemy_raw(w, e, ally.pos) * ally.mitigation;
                                const double after = std::max(0.0, danger - removed);
                                if (removed > 0 && after < ally.hp && danger >= ally.hp)
                                    return proposal(cast_unit(s, e.id, "protect-lethal-peel"),
                                                    Phase::Protect, Priority::Survival,
                                                    10000 + ally.gems, memory, w.round);
                            }
                    }
            }

    std::optional<Proposal> best;
    int best_target = std::numeric_limits<int>::max();
    auto consider = [&](Action a, double value, const Actor &e, bool control = false) {
        if (value <= 0)
            return;
        const bool relevant = enemy_raw(w, e, w.self.pos) > 0;
        const bool deciding = e.channel == Channel::Tribute && w.enemy_score + e.gems >= 1000 &&
                              control && e.type != marcella_type;
        Priority priority =
            deciding ? Priority::Deciding : (relevant ? Priority::Incumbent : Priority::Routine);
        value *= target_importance(e);
        if (memory.focus == e.id && memory.focus_until >= w.round)
            value *= 1.10;
        if (!best || priority > best->priority ||
            (priority == best->priority &&
             (value > best->value ||
              (std::abs(value - best->value) < .001 && e.id < best_target)))) {
            best = proposal(a, deciding ? Phase::Protect : Phase::Fight, priority, value, memory,
                            w.round);
            best->mission.target = e.pos;
            best_target = e.id;
        }
    };
    for (const auto &e : w.enemies)
        if (e.alive && fuel(18000)) {
            const int d = distance(w.self.pos, e.pos);
            const double return_cost = returned_damage(w.self, e);
            if (!direct_hit_survives(w.self, e))
                continue;
            const double basic = basic_hp_damage(w.self, e);
            const double reply = enemy_raw(w, e, w.self.pos) * w.self.mitigation;
            const bool relevant = reply > 0;
            if (farming_context && !relevant && e.channel != Channel::Tribute)
                continue;
            if (w.self.can_attack && d <= w.self.range) {
                double continuation = 0;
                for (const auto &s : w.spells)
                    if (s.ready && s.kind == 1 && s.self && e.hp > basic)
                        continuation = std::max(continuation, std::min(e.hp - basic, basic));
                // Preserve ranged escape walking when this nonlethal basic would
                // spend it and the next reply would make the result unsustainable.
                if (!(w.self.range > 1 && w.self.can_move &&
                      incoming + return_cost >= w.self.hp * .80 && basic < e.hp)) {
                    Action a;
                    a.kind = Kind::BasicChampion;
                    a.target = e.id;
                    a.reason = "fight-basic";
                    const double lethal = basic >= e.hp - .001 ? 300 + e.gems * 2 : 0;
                    consider(a,
                             basic + continuation + lethal + basic_splash_value(w, e) +
                                 linked_removal_value(w, e, basic) - return_cost,
                             e, w.self.enhanced && w.self.type == marcella_type);
                }
            }
            if (w.self.can_cast)
                for (const auto &s : w.spells)
                    if (s.ready) {
                        if (s.kind == 1 && s.self && d <= w.self.range && basic > 0) {
                            const bool interrupt = w.self.type == marcella_type &&
                                                   e.channel != Channel::None &&
                                                   e.type != marcella_type;
                            if (!w.self.can_attack || interrupt)
                                consider(cast_self(s, "fight-reset-live-followup"),
                                         basic - return_cost + (interrupt ? 200 : 0), e, interrupt);
                        } else if (offensive(s) && can_cast_at(w, s, e)) {
                            const double damage = spell_damage(s, e);
                            const bool control = s.kind == 4 && e.type != marcella_type;
                            const double kill = (damage >= e.hp - .001 ? 300 + e.gems * 2 : 0) +
                                                linked_removal_value(w, e, damage);
                            const double follow =
                                w.self.can_attack && d <= w.self.range
                                    ? std::min(std::max(0.0, e.hp - damage), basic)
                                    : 0;
                            double value = damage + follow + kill - return_cost;
                            if (control && relevant)
                                value += std::min(200.0, reply);
                            if (control && e.channel != Channel::None)
                                value += 200;
                            if (s.kind == 3 && s.ground) {
                                // Centers within cast radius can affect a target outside
                                // unit-target range. This direct-center candidate is one
                                // of a bounded nine-point shortlist below.
                            } else
                                consider(cast_unit(s, e.id, "fight-useful-cast"), value, e,
                                         control);
                        }
                        if (s.kind == 3 && s.ground) {
                            // Nine centers around a target suffice for a bounded edge/AoE
                            // prototype; no full-map search or hidden coordinates.
                            for (int dy = -s.radius; dy <= s.radius; dy += std::max(1, s.radius))
                                for (int dx = -s.radius; dx <= s.radius;
                                     dx += std::max(1, s.radius)) {
                                    if (!fuel(22000))
                                        break;
                                    Pos center{e.pos.x + dx, e.pos.y + dy};
                                    if (!w.geo.valid(center) ||
                                        distance(w.self.pos, center) > s.range)
                                        continue;
                                    double gain = 0, retaliation = 0;
                                    int useful = 0;
                                    for (const auto &other : w.enemies)
                                        if (other.alive &&
                                            distance(other.pos, center) <= s.radius) {
                                            const double hit = spell_damage(s, other);
                                            gain +=
                                                hit +
                                                (hit >= other.hp - .001 ? 300 + other.gems * 2 : 0);
                                            if (hit > 0)
                                                ++useful;
                                            // Unknown area-return semantics do not justify a
                                            // lethal self-sacrifice. Varg secondary BASIC is
                                            // separately known not to trigger Ren retaliation.
                                            if (other.type == ren_type)
                                                retaliation += .2 * other.focus * w.self.mitigation;
                                        }
                                    retaliation = std::max(0.0, retaliation - w.self.shield);
                                    if (useful && retaliation < w.self.hp) {
                                        Action a;
                                        a.kind = Kind::CastGround;
                                        a.slot = s.slot;
                                        a.at = center;
                                        a.reason = "fight-useful-area";
                                        consider(a, gain - retaliation, e, false);
                                    }
                                }
                        }
                    }
        }
    if (best)
        return best;

    // Useful non-emergency healing is compared after urgent offense/protection,
    // with no overheal and no blind 50%-missing threshold.
    if (w.self.can_cast && incoming < w.self.hp)
        for (const auto &s : w.spells)
            if (s.ready && s.kind == 5 && s.allies) {
                const Actor *chosen = nullptr;
                double gain = 0;
                for (const auto &ally : w.allies)
                    if (ally.id != w.self.id && ally.alive &&
                        distance(w.self.pos, ally.pos) <= s.range) {
                        double heal = std::min(s.amount, std::max(0.0, ally.max_hp - ally.hp));
                        if (heal > gain) {
                            gain = heal;
                            chosen = &ally;
                        }
                    }
                if (chosen && gain > 0)
                    return proposal(cast_unit(s, chosen->id, "support-effective-heal"),
                                    Phase::Protect, Priority::Routine, gain, memory, w.round);
            }

    if (farming_context || !w.self.can_move || !fuel(22000))
        return std::nullopt;
    const Actor *target = nullptr;
    double merit = 0;
    for (const auto &e : w.enemies)
        if (e.alive) {
            int reach = w.self.range;
            for (const auto &s : w.spells)
                if (s.ready && !s.exclusive && offensive(s))
                    reach = std::max(reach, s.range + s.radius);
            if (distance(w.self.pos, e.pos) > reach + std::max(1, w.self.move_speed))
                continue;
            // A one-opportunity useful approach, not an indefinite center chase.
            const double v = target_importance(e) / (1 + e.hp / std::max(1.0, e.max_hp));
            if (v > merit) {
                merit = v;
                target = &e;
            }
        }
    if (target) {
        int reach = w.self.range;
        for (const auto &s : w.spells)
            if (s.ready && !s.exclusive && offensive(s))
                reach = std::max(reach, s.range + s.radius);
        if (auto step = w.toward(target->pos, reach)) {
            const double next = incoming_damage(w, *step);
            if (next < w.self.hp * .65) {
                // A ranged walk needs a compatible cast/reset afterward. Do
                // not value an ordinary ranged basic lost to that walk.
                bool action = w.self.range <= 1;
                for (const auto &s : w.spells)
                    if (s.ready && ((s.kind == 1 && distance(*step, target->pos) <= w.self.range) ||
                                    (!s.exclusive && offensive(s) &&
                                     distance(*step, target->pos) <= s.range + s.radius)))
                        action = true;
                if (action)
                    return proposal(move(*step, "fight-timely-approach"), Phase::Fight,
                                    Priority::Routine, merit * 20, memory, w.round);
            }
        }
    }
    return std::nullopt;
}
#else
} // namespace combat_detail
#endif
} // namespace tactics

#pragma once
#include "types.h"
#include <bit>
#include <span>
#ifndef TACTICS_COMBAT_MODEL_ONLY
#include "sdk_world.h"
#endif

namespace tactics {
namespace combat_detail {
inline constexpr int ren_type = 9, marcella_type = 7, cassi_type = 3, issac_type = 4;

// Both linked bodies die atomically when either is killed. Only currently
// observed living actors can contribute a removable reply source; control on
// one body alone never disables its partner.
inline bool linked_partners(const Actor &a, const Actor &b) {
    return a.alive && b.alive && a.id != b.id &&
           ((a.type == cassi_type && b.type == issac_type) ||
            (a.type == issac_type && b.type == cassi_type));
}
inline bool immediate_effect_removes(const Actor &target, const Actor &source, bool killed,
                                     bool controlled) {
    return target.alive && source.alive &&
           ((target.id == source.id && (killed || controlled)) ||
            (killed && linked_partners(target, source)));
}
struct ImmediateRemoval {
    const Actor *target = nullptr;
    bool killed = false, controlled = false;
};
inline bool source_removed_by(std::span<const ImmediateRemoval> effects, const Actor &source) {
    for (const auto &effect : effects)
        if (effect.target &&
            immediate_effect_removes(*effect.target, source, effect.killed, effect.controlled))
            return true;
    return false;
}
inline bool killed_directly_by(std::span<const ImmediateRemoval> effects, const Actor &source) {
    for (const auto &effect : effects)
        if (effect.target && effect.target->id == source.id && effect.killed)
            return true;
    return false;
}
inline bool killed_by_effects(std::span<const ImmediateRemoval> effects, const Actor &source) {
    for (const auto &effect : effects)
        if (effect.target && effect.killed &&
            immediate_effect_removes(*effect.target, source, true, false))
            return true;
    return false;
}
inline bool basic_splash_hits(const Actor &self, const Actor &primary, const Actor &other) {
    return self.type == 10 && other.alive && primary.id != other.id &&
           distance(primary.pos, other.pos) <= 1;
}
inline double linked_only_removal_value(std::span<const ImmediateRemoval> effects,
                                        const Actor &source) {
    if (killed_directly_by(effects, source))
        return 0;
    for (const auto &effect : effects)
        if (effect.target && effect.killed && linked_partners(*effect.target, source))
            return 300 + source.gems * 2;
    return 0;
}

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
struct HitEffect {
    double hp = 0, shield = 0;
};
inline HitEffect apply_hit(Actor &target, double raw) {
    const double effective = std::max(0.0, raw * target.mitigation);
    HitEffect hit;
    hit.shield = std::min(target.shield, effective);
    target.shield -= hit.shield;
    hit.hp = std::min(target.hp, effective - hit.shield);
    target.hp -= hit.hp;
    return hit;
}
inline int added_control_windows(const Actor &target, int duration) {
    if (target.type == marcella_type || duration <= 0)
        return 0;
    if (!target.stunned)
        return duration;
    // A visible zero timer is still an active buff now, but expires at its
    // owner's next start. Unknown remaining timing cannot certify an extension.
    return target.stun_ticks >= 0 ? std::max(0, duration - target.stun_ticks) : 0;
}
// Eligibility depends only on the observed caster, spell and enemy, not on
// which ally is threatened. Filter it once before expensive ally forecasts.
inline bool peel_target_eligible(const Actor &caster, const Spell &spell, const Actor &enemy) {
    return caster.can_cast && spell.ready && spell.enemies &&
           distance(caster.pos, enemy.pos) <= spell.range &&
           added_control_windows(enemy, spell.duration) > 0 && direct_hit_survives(caster, enemy);
}
inline bool applies_control(const Actor &caster, const Spell &spell) {
    // Ryth's native area-stun is exposed by the SDK as area damage, not kind4.
    // A generic lasting damage area is not assumed to stun its recipients.
    return spell.kind == 4 || (caster.type == 0 && spell.kind == 3 && spell.duration > 0);
}
struct Exchange {
    double hp_damage = 0, shield_damage = 0, returned = 0;
    bool lethal = false;
    int hits = 0;
};
inline Exchange sequence_exchange(const Actor &self, const Actor &target, double first_raw,
                                  double follow_raw = 0, double final_raw = 0) {
    Actor victim = target;
    Exchange result;
    double shield = self.shield;
    for (double raw : {first_raw, follow_raw, final_raw}) {
        if (raw <= 0 || victim.hp <= 0)
            continue;
        ++result.hits;
        const auto hit = apply_hit(victim, raw);
        result.hp_damage += hit.hp;
        result.shield_damage += hit.shield;
        // Each real direct hit can retaliate, even if fully shielded or lethal.
        const double returned = target.type == ren_type ? .2 * target.focus * self.mitigation : 0;
        const double absorbed = std::min(shield, returned);
        shield -= absorbed;
        result.returned += returned - absorbed;
    }
    result.lethal = victim.hp <= .001;
    return result;
}
struct ShortSequence {
    Action first{};
    Exchange exchange{};
    int actions = 1, control_windows = 0;
};
inline bool immediate_sequence_kill(const ShortSequence &sequence, bool movement_first) {
    return !movement_first && sequence.actions == 1 && sequence.exchange.lethal;
}
inline bool immediate_sequence_control(const Actor &self, const ShortSequence &sequence,
                                       bool movement_first) {
    if (movement_first || sequence.control_windows <= 0)
        return false;
    const auto kind = sequence.first.kind;
    return kind == Kind::CastChampion || kind == Kind::CastGround ||
           (kind == Kind::BasicChampion && self.type == marcella_type && self.enhanced);
}
inline std::vector<ShortSequence> stationary_sequences(const Actor &self, const Actor &target) {
    std::vector<ShortSequence> result;
    if (!self.alive || !target.alive || self.stunned || self.channel != Channel::None)
        return result;
    result.reserve(5);
    const int d = distance(self.pos, target.pos);
    const bool basic = self.can_attack && d <= self.range;
    const int enhanced_control =
        self.type == marcella_type && self.enhanced ? added_control_windows(target, 1) : 0;
    if (basic) {
        Action a;
        a.kind = Kind::BasicChampion;
        a.target = target.id;
        a.reason = "fight-basic";
        result.push_back({a, sequence_exchange(self, target, self.strength), 1, enhanced_control});
    }
    if (!self.can_cast)
        return result;
    for (const auto &spell : self.spells) {
        if (!spell.ready)
            continue;
        if (spell.kind == 1 && spell.self && d <= self.range) {
            Action a;
            a.kind = basic ? Kind::BasicChampion : Kind::CastSelf;
            a.target = target.id;
            a.slot = spell.slot;
            a.reason = basic ? "fight-basic-plan-reset" : "fight-reset-live-followup";
            const auto exchange =
                sequence_exchange(self, target, self.strength, basic ? self.strength : 0);
            // A reset is only part of the sequence if the first basic leaves a
            // living target. A kill instead releases the remaining cast budget.
            const bool first_kills = basic && sequence_exchange(self, target, self.strength).lethal;
            if (!first_kills)
                result.push_back(
                    {a, exchange, basic ? 3 : 2,
                     std::max(enhanced_control,
                              self.type == marcella_type ? added_control_windows(target, 1) : 0)});
        } else if (offensive(spell) && spell.enemies && d <= spell.range) {
            Action a;
            a.kind = Kind::CastChampion;
            a.slot = spell.slot;
            a.target = target.id;
            a.reason = basic ? "fight-cast-plan-basic" : "fight-useful-cast";
            auto exchange =
                sequence_exchange(self, target, spell.amount, basic ? self.strength : 0);
            const bool cast_kills = sequence_exchange(self, target, spell.amount).lethal;
            result.push_back(
                {a, exchange, basic && !cast_kills ? 2 : 1,
                 applies_control(self, spell) ? added_control_windows(target, spell.duration) : 0});
        }
    }
    return result;
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
    if (e.stunned && e.stun_ticks >= horizon)
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
            } else if (s.kind == 6 &&
                       (d <= s.range + e.range || (!s.exclusive && e.range <= 1 &&
                                                   move_distance <= s.range + e.range + moves))) {
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
// Exact bounded ordinary walking on the exported enemy-owned terrain mask.
// Nine-bit rows avoid both host board allocation/export and a heap/queue node
// for every neighbor. Paths may cut a diagonal corner, as native ReachableMask
// does; walls, holes, altars and our spawn remain blocked by the input mask.
inline std::vector<Pos>
ordinary_reachable_region(int width, int height, const std::vector<std::uint8_t> &terrain,
                          Pos origin, int steps,
                          const std::vector<std::uint8_t> *occupied = nullptr) {
    const int radius = std::clamp(steps, 0, 4), side = 2 * radius + 1;
    std::array<std::uint16_t, 9> allowed{}, reached{}, next{};
    if (origin.x < 0 || origin.y < 0 || origin.x >= width || origin.y >= height)
        return {};
    for (int row = 0; row < side; ++row) {
        const int y = origin.y + row - radius;
        if (y < 0 || y >= height)
            continue;
        for (int col = 0; col < side; ++col) {
            const int x = origin.x + col - radius;
            const int index = y * width + x;
            if (x >= 0 && x < width && index / 8 < static_cast<int>(terrain.size()) &&
                !packed_bit(terrain, index) && !(occupied && packed_bit(*occupied, index)))
                allowed[row] |= std::uint16_t(1) << col;
        }
    }
    // The observed source is retained even when a projected fixture places it
    // on a blocked origin, matching enemy_positions' previous explicit seed.
    reached[radius] = std::uint16_t(1) << radius;
    for (int tick = 0; tick < radius; ++tick) {
        for (int row = 0; row < side; ++row) {
            std::uint16_t adjacent = reached[row];
            if (row > 0)
                adjacent |= reached[row - 1];
            if (row + 1 < side)
                adjacent |= reached[row + 1];
            next[row] =
                reached[row] | ((adjacent | (adjacent << 1) | (adjacent >> 1)) & allowed[row]);
        }
        reached = next;
    }
    std::vector<Pos> result;
    result.reserve(side * side);
    for (int row = 0; row < side; ++row)
        for (auto bits = reached[row]; bits; bits &= bits - 1) {
            const int col = std::countr_zero(bits);
            result.push_back({origin.x + col - radius, origin.y + row - radius});
        }
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
    if (e.stunned && e.stun_ticks >= horizon)
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
            } else if (s.kind == 6 &&
                       (near(current, s.range + e.range) ||
                        (!s.exclusive && e.range <= 1 && near(future, s.range + e.range))))
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

inline double cumulative_reply_upper(const Actor &enemy, Pos from, Pos at, int horizon) {
    if (!enemy.alive || horizon <= 0)
        return 0;
    // At most 32 future owner opportunities are expanded. Longer forecasts use
    // a conservative tail rather than an unbounded search or a false zero.
    const int expanded = std::min(32, horizon), speed = std::max(1, enemy.move_speed);
    std::array<double, 2> bonus{};
    std::array<int, 2> earliest{expanded + 1, expanded + 1};
    double basics = 0;
    for (int tick = 1; tick <= expanded; ++tick) {
        if (enemy.stunned && enemy.stun_ticks >= tick)
            continue;
        const int earlier_dash = tick > 1 ? plausible_dash(enemy, tick - 1) : 0;
        const int before = std::max(0, distance(from, at) - (tick - 1) * speed - earlier_dash);
        const int after = std::max(0, distance(from, at) - tick * speed - earlier_dash);
        const bool stationary_basic = before <= enemy.range;
        const bool moved_basic = enemy.range <= 1 && after <= enemy.range;
        const double basic = stationary_basic || moved_basic ? enemy.strength : 0;
        basics += basic;
        for (int slot = 0; slot < 2; ++slot) {
            const auto &spell = enemy.spells[slot];
            if (!plausible_ready(spell, tick))
                continue;
            double reply = basic;
            if (spell.kind == 1) {
                double reset = stationary_basic || moved_basic ? 2 * enemy.strength : 0;
                if (enemy.range > 1 && after <= enemy.range)
                    reset = std::max(reset, enemy.strength);
                reply = std::max(reply, reset);
            } else if (offensive(spell) && (spell.enemies || spell.ground)) {
                const int reach = spell.range + (spell.kind == 3 ? spell.radius : 0);
                const double amount = std::max(0.0, spell.amount);
                if (before <= reach)
                    reply = std::max(reply, amount + (stationary_basic ? enemy.strength : 0));
                if (!spell.exclusive && after <= reach)
                    reply = std::max(reply, amount + (moved_basic ? enemy.strength : 0));
            } else if (spell.kind == 6 && (before <= spell.range + enemy.range ||
                                           (!spell.exclusive && enemy.range <= 1 &&
                                            after <= spell.range + enemy.range))) {
                reply = std::max(reply, enemy.strength);
            }
            const double extra = reply - basic;
            if (extra > 0) {
                earliest[slot] = std::min(earliest[slot], tick);
                bonus[slot] = std::max(bonus[slot], extra);
            }
        }
    }
    std::array<int, 2> casts{};
    for (int slot = 0; slot < 2; ++slot)
        if (earliest[slot] <= expanded) {
            const int recharge = std::max(1, enemy.spells[slot].recharge);
            casts[slot] = 1 + (expanded - earliest[slot]) / recharge;
        }
    // An upper schedule assigns at most one successful cast per opportunity.
    // Each slot receives its maximum useful bonus in this window; it never
    // charges an eight-turn spell on every turn or adds two simultaneous casts.
    const int first = bonus[1] > bonus[0] ? 1 : 0, second = 1 - first;
    const int n_first = std::min(expanded, casts[first]);
    const int n_second = std::min(expanded - n_first, casts[second]);
    double result = basics + n_first * bonus[first] + n_second * bonus[second];
    if (horizon > expanded)
        result += (horizon - expanded) * long_window_reply_upper(enemy, from, at, horizon);
    return result;
}

inline double possible_window_volley_upper(const Actor &enemy, Pos from, Pos at, int horizon) {
    if (!enemy.alive || horizon <= 0 || (enemy.stunned && enemy.stun_ticks >= horizon))
        return 0;
    double volley = std::max(0.0, enemy.strength);
    int reach = enemy.range, dash = 0;
    for (const auto &spell : enemy.spells)
        if (plausible_ready(spell, horizon)) {
            if (spell.kind == 1)
                volley = std::max(volley, 2 * enemy.strength);
            else if (offensive(spell) && (spell.enemies || spell.ground)) {
                volley = std::max(volley, enemy.strength + std::max(0.0, spell.amount));
                reach = std::max(reach, spell.range + (spell.kind == 3 ? spell.radius : 0));
            } else if (spell.kind == 6) {
                dash = std::max(dash, spell.range);
                // The bounded window model can combine a past access bonus
                // with its later basic upper schedule. Preserve that margin.
                volley = std::max(volley, 2 * enemy.strength);
            }
        }
    // This is only a risk envelope. It does not authorize a hidden target,
    // promise a path through terrain, or repeat two casts in one opportunity.
    // The exact conservative window model admits an earlier uncertain dash
    // and a final dash/basic alternative. Its envelope must retain both.
    if (distance(from, at) > reach + horizon * std::max(1, enemy.move_speed) + 2 * dash)
        return 0;
    return volley;
}
inline double possible_remembered_volley_upper(Actor enemy, int age, Pos at, int horizon) {
    const Pos from = geometric_approach(
        enemy.pos, at, age * std::max(1, enemy.move_speed) + plausible_dash(enemy, age));
    for (auto &spell : enemy.spells)
        if (spell.cooldown >= 0)
            spell.cooldown = std::max(0, spell.cooldown - age);
    return possible_window_volley_upper(enemy, from, at, horizon);
}
inline constexpr double unknown_reply_upper() {
    return std::numeric_limits<double>::max() / 1024;
}
inline bool known_reply(double value) {
    return std::isfinite(value) && value >= 0 && value < unknown_reply_upper();
}
// Ordinary aggression cannot turn a surviving hold into a lethal reply.
// Only an already deciding stop or a known lethal hold retains the existing
// desperate-trade policy. A budget/visibility unknown is not forced death.
inline bool combat_trade_allowed(double holding, double after, double hp, bool deciding = false) {
    if (!std::isfinite(hp) || hp <= 0 || !std::isfinite(after) || after < 0)
        return false;
    if (deciding || (known_reply(after) && after < hp))
        return true;
    return known_reply(holding) && holding >= hp;
}
inline double forecast_shield(const Actor &victim, int horizon) {
    // Current response keeps the actually present shield. Across several
    // phases it is only safe to subtract value which cannot expire before
    // the requested endpoint; later casts are never promised here.
    return std::isfinite(victim.shield) && victim.shield > 0 &&
                   (horizon <= 1 || victim.shield_ticks >= horizon)
               ? victim.shield
               : 0;
}
inline bool preserves_ready_walk(const Actor &self, const Action &first,
                                 bool movement_first = false) {
    if (movement_first || first.kind == Kind::Move)
        return false;
    if (!self.can_move)
        return true; // No unspent ordinary walk is lost by this action.
    if (first.kind == Kind::BasicChampion)
        return self.range <= 1;
    if (first.kind == Kind::CastSelf || first.kind == Kind::CastChampion ||
        first.kind == Kind::CastGround)
        return first.slot >= 0 && first.slot < 2 && !self.spells[first.slot].exclusive;
    return false;
}
inline double marginal_reply_cost(double after, double holding, bool preserves_walk,
                                  double escape_reply = 0, bool escape_known = false) {
    // Compare compatible actions at a common endpoint. Holding would receive
    // the same unavoidable reply; paying it only for attacking creates false
    // inactivity. A move-locking action instead pays the lost escape option.
    // An incomplete escape frontier supplies no optimistic baseline credit.
    // Unknown sentinels never cancel each other into a fictitious safe action.
    if (!known_reply(after) || !known_reply(holding))
        return .5 * after;
    const double baseline = preserves_walk ? holding
                            : escape_known && known_reply(escape_reply)
                                ? std::min(holding, escape_reply)
                                : 0;
    return .5 * (after - baseline);
}

inline constexpr int cumulative_forecast_allowance(int horizon) {
    // Actual pinned native measurements for six simultaneous sources cost
    // 9,177 fuel at H5 and 47,247 at H32. This deliberately larger per-source
    // allowance protects the mutation/core reserve before starting the loop.
    return 1200 + 500 * std::clamp(horizon, 1, 32);
}
inline constexpr int native_reach_allowance(int steps, int previous_steps) {
    const int current_side = 2 * std::clamp(steps, 0, 8) + 1;
    const int previous_side = 2 * std::clamp(previous_steps, 0, 8) + 1;
    return 6000 + 80 * (current_side * current_side + previous_side * previous_side);
}

#ifndef TACTICS_COMBAT_MODEL_ONLY
inline void ensure_reach_cache(World &w) {
    if (w.combat_cache_serial != w.serial) {
        w.combat_reach_cache.clear();
        w.combat_damage_cache.clear();
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
    // Bounded local reach, not a fresh native board/export for every micro tile.
    // Enemy walking may leave its own spawn, but cannot enter our spawn.
    const int steps = std::clamp(horizon * std::max(1, e.move_speed), 0, 4);
    auto result =
        ordinary_reachable_region(w.geo.width, w.geo.height, w.geo.enemy_terrain, e.pos, steps);
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
    if (!dash && steps <= 4)
        origins = enemy_positions(w, sight.actor, elapsed);
    else {
        // One bounded legal-landing square replaces multi-origin nested dash
        // expansions. It is a conservative possibility envelope; it does not
        // certify any particular hidden walking or dash trajectory.
        origins = expand_origins(w, {sight.actor.pos}, 0, steps + dash);
    }
    if (!future)
        origins = remove_visible_absence(std::move(origins), w.geo.width, w.visible_bytes,
                                         w.enemies, sight.actor.id);
    // Empty tiles now are valid future arrivals, so only prune the current set.
    return w.combat_reach_cache.emplace(key, std::move(origins)).first->second;
}
inline double remembered_uncached(World &w, const Sighting &sight, Pos at, int horizon = 1) {
    const int age = w.round - sight.round;
    if (!recent_sighting(age) || !sight.actor.alive)
        return 0;
    for (const auto &e : w.enemies)
        if (e.id == sight.actor.id)
            return 0; // Count each enemy once.
    if (horizon > 1) {
        return possible_remembered_volley_upper(sight.actor, age, at, horizon);
    }
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

inline double remembered_raw(World &w, const Sighting &sight, Pos at, int horizon = 1) {
    ensure_reach_cache(w);
    const std::array<int, 5> key{1, sight.actor.id, at.x, at.y, horizon};
    if (auto found = w.combat_damage_cache.find(key); found != w.combat_damage_cache.end())
        return found->second;
    const double result = remembered_uncached(w, sight, at, horizon);
    if (w.combat_damage_cache.size() < 128)
        w.combat_damage_cache.emplace(key, result);
    return result;
}
inline double enemy_uncached(World &w, const Actor &e, Pos at, int horizon = 1) {
    if (!e.alive)
        return 0;
    // Preserve a legal action and refresh reserve. The coarse envelope may
    // overestimate contact through terrain, but never certifies a blind route
    // as safe merely because another native reach search cannot be afforded.
    if (bc::fuel_remaining() < 24000)
        return horizon > 1 ? possible_window_volley_upper(e, e.pos, at, horizon)
                           : long_window_reply_upper(e, e.pos, at, horizon);
    if (horizon > 1 || std::max(1, e.move_speed) > 4)
        return possible_window_volley_upper(e, e.pos, at, horizon);
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
inline double enemy_raw(World &w, const Actor &e, Pos at, int horizon = 1) {
    ensure_reach_cache(w);
    const std::array<int, 5> key{0, e.id, at.x, at.y, horizon};
    if (auto found = w.combat_damage_cache.find(key); found != w.combat_damage_cache.end())
        return found->second;
    const double result = enemy_uncached(w, e, at, horizon);
    if (w.combat_damage_cache.size() < 128)
        w.combat_damage_cache.emplace(key, result);
    return result;
}

inline double incoming_for(World &w, const Actor &victim, Pos at, int horizon = 1,
                           bool include_camps = true, int waking_group = -1) {
    ensure_reach_cache(w);
    const std::array<int, 5> key{2000 + 2 * (waking_group + 1) + include_camps, victim.id, at.x,
                                 at.y, horizon};
    if (auto found = w.combat_damage_cache.find(key); found != w.combat_damage_cache.end())
        return found->second;
    const auto unknown = [&] {
        // A finite conservative unknown is not a measured damage estimate.
        // It prevents a late caller from spending the action reserve or
        // treating unvisited remaining sources as harmless.
        if (w.enemies.empty() && w.sightings.empty() && (!include_camps || w.groups.empty()))
            return 0.0;
        return unknown_reply_upper();
    };
    if (bc::fuel_remaining() < 12000)
        return unknown();
    double enemy = 0, monster = 0;
    auto window = [&](const Actor &actor, Pos from) {
        const double upper = possible_window_volley_upper(actor, from, at, horizon);
        if (upper == 0)
            return 0.0;
        if (static_cast<int>(bc::fuel_remaining()) < 20000 + cumulative_forecast_allowance(horizon))
            return horizon * upper;
        return cumulative_reply_upper(actor, from, at, horizon);
    };
    for (const auto &e : w.enemies) {
        const auto remaining = bc::fuel_remaining();
        if (remaining < 12000)
            return unknown();
        const double possible =
            remaining < 24000 ? (horizon > 1 ? possible_window_volley_upper(e, e.pos, at, horizon)
                                             : long_window_reply_upper(e, e.pos, at, horizon))
                              : enemy_raw(w, e, at, horizon);
        enemy += horizon <= 1 || possible == 0 ? possible : window(e, e.pos);
    }
    for (const auto &sight : w.sightings) {
        const int age = w.round - sight.round;
        if (!recent_sighting(age) || !sight.actor.alive)
            continue;
        bool visible = false;
        for (const auto &e : w.enemies)
            visible |= e.id == sight.actor.id;
        if (visible)
            continue;
        const auto remaining = bc::fuel_remaining();
        if (remaining < 12000)
            return unknown();
        const double possible =
            remaining < 24000
                ? (horizon > 1 ? possible_remembered_volley_upper(sight.actor, age, at, horizon)
                               : coarse_remembered_reply(sight.actor, age, at, horizon))
                : remembered_raw(w, sight, at, horizon);
        if (horizon <= 1 || possible == 0) {
            enemy += possible;
            continue;
        }
        Actor e = sight.actor;
        const Pos from =
            geometric_approach(e.pos, at, age * std::max(1, e.move_speed) + plausible_dash(e, age));
        for (auto &spell : e.spells)
            if (spell.cooldown >= 0)
                spell.cooldown = std::max(0, spell.cooldown - age);
        enemy += window(e, from);
    }
    if (include_camps) {
        if (bc::fuel_remaining() < 12000)
            return unknown();
        for (unsigned g = 0; g < w.groups.size(); ++g)
            for (const auto &c : w.groups[g].camps)
                if (c.hp > 0 && (c.awake || static_cast<int>(g) == waking_group) &&
                    distance(c.pos, at) <= c.range) {
                    bool closer = false;
                    // Camp actions occur before the next champion turns. A body
                    // which has completed this round cannot walk away first.
                    // Longer forecasts do not assume that ally stays as a tank.
                    if (horizon == 1)
                        for (const auto &ally : w.allies)
                            if (ally.id != victim.id && ally.alive && ally.completed &&
                                distance(c.pos, ally.pos) < distance(c.pos, at))
                                closer = true;
                    if (!closer)
                        monster += c.strength * std::max(1, horizon);
                }
    }
    const double raw = enemy * victim.mitigation + monster * victim.camp_mitigation;
    const double result = std::max(0.0, raw - forecast_shield(victim, horizon));
    if (w.combat_damage_cache.size() < 128)
        w.combat_damage_cache.emplace(key, result);
    return result;
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
inline double basic_splash_value(const World &w, const Actor &primary, bool primary_killed) {
    if (w.self.type != 10)
        return 0;
    double value = 0;
    for (const auto &other : w.enemies)
        if (basic_splash_hits(w.self, primary, other) &&
            !(primary_killed && linked_partners(primary, other))) {
            // Secondary splash is not another selected direct target, and in this
            // engine it does not add Ren's direct-hit retaliation.
            const double hit = basic_hp_damage(w.self, other);
            value += hit;
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
struct ReplyBaseline {
    double damage = 0;
    bool known = false;
};
inline ReplyBaseline walking_reply_baseline(World &w, const Memory &memory, double holding,
                                            int floor) {
    if (!known_reply(holding))
        return {};
    if (!w.self.can_move || holding == 0)
        return {holding, true};
    // Optional completeness matters: a partial list's minimum can overstate
    // the risk of an untested escape and wrongly justify spending the walk.
    if (w.self.move_speed > 4 || w.occupied_bytes.empty() || memory.blocked_round == w.round ||
        static_cast<int>(bc::fuel_remaining()) < std::max(32000, floor + 8000))
        return {};
    const auto positions =
        ordinary_reachable_region(w.geo.width, w.geo.height, w.geo.terrain, w.self.pos,
                                  std::max(1, w.self.move_speed), &w.occupied_bytes);
    double best = holding;
    for (const auto p : positions) {
        if (p == w.self.pos || !w.free(p))
            continue;
        if (memory.hold_group >= 0 && w.on_group(memory.hold_group, w.self.pos) &&
            !w.on_group(memory.hold_group, p))
            continue;
        if (static_cast<int>(bc::fuel_remaining()) <= floor ||
            w.round != static_cast<int>(bc::round_number()))
            return {};
        const double risk = incoming_for(w, w.self, p);
        if (!known_reply(risk))
            return {};
        best = std::min(best, risk);
        // Zero is a certified global minimum even if later legal endpoints
        // have not been evaluated, since modeled damage cannot be negative.
        if (best == 0)
            return {0, true};
    }
    return {best, true};
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

inline std::optional<Action> escape_action(World &w, int planning_floor = 0) {
    using namespace combat_detail;
    if (!w.self.alive || w.self.channel != Channel::None || bc::fuel_remaining() < 24000 ||
        w.round != static_cast<int>(bc::round_number()))
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
    const int start_fuel = static_cast<int>(bc::fuel_remaining());
    const bool ready_dash = std::any_of(w.spells.begin(), w.spells.end(), [](const Spell &s) {
        return s.ready && s.kind == 6 && s.ground;
    });
    const int floor = planning_floor > 0
                          ? std::clamp(planning_floor, 18000, std::max(18000, start_fuel - 4000))
                          : std::max(18000, start_fuel - (ready_dash ? 24000 : 10000));
    const auto funded = [&](int reserve = 0) {
        return w.round == static_cast<int>(bc::round_number()) &&
               static_cast<int>(bc::fuel_remaining()) >= std::max(floor, reserve);
    };
    const double current = incoming_damage(w, w.self.pos);
    if (w.round != static_cast<int>(bc::round_number()))
        return std::nullopt;
    double best = current;
    int best_home = w.home_distance(w.self.pos);
    std::optional<Action> result;
    if (w.self.can_move) {
        // A legal one-step stencil is sufficient for every current kit, whose
        // base speed is one, and remains a valid fallback for a faster kit.
        // No board construction or per-tile host query precedes this escape.
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                if ((!dx && !dy) || !funded())
                    continue;
                Pos p{w.self.pos.x + dx, w.self.pos.y + dy};
                if (!w.free(p))
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
            if (s.ready && funded()) {
                if (s.kind == 6 && s.ground) {
                    if (!funded(std::max(42000, floor + 6000)))
                        continue;
                    // Native 0.0.2 permits bending around a wall and crossing
                    // holes and altars, but walls, units and enemy spawn block the
                    // traversal. valid_tiles() supplies RANGE ONLY; landing
                    // and the actual short dash path are separate checks.
                    auto path_blockers = bc::map::walls() | w.geo.enemy_spawn | w.occupied |
                                         bc::vision::teleport_tiles();
                    path_blockers.set(sdk(w.self.pos), false);
                    auto destinations = path_blockers.reachable_tiles(sdk(w.self.pos), s.range);
                    // A native mask query may resume in another owner round.
                    // Never ask an old live ability for its range after that
                    // yield: the actual owner may now be dead at (-1,-1).
                    if (!funded(24000))
                        return w.round == static_cast<int>(bc::round_number()) ? result
                                                                               : std::nullopt;
                    native_context = "escape:dash-range";
                    destinations &= w.me.abilities()[s.slot].valid_tiles();
                    destinations &= ~(w.geo.static_blocked | w.occupied);
                    struct Landing {
                        Pos pos;
                        double exposure;
                        int home;
                    };
                    std::vector<Landing> shortlist;
                    for (auto raw : destinations.positions()) {
                        Pos p = position(raw);
                        if (p != w.self.pos && w.free(p))
                            shortlist.push_back({p, w.exposure(p), w.home_distance(p)});
                    }
                    std::sort(shortlist.begin(), shortlist.end(), [](const auto &a, const auto &b) {
                        if (a.exposure != b.exposure)
                            return a.exposure < b.exposure;
                        if (a.home != b.home)
                            return a.home < b.home;
                        return a.pos.y < b.pos.y || (a.pos.y == b.pos.y && a.pos.x < b.pos.x);
                    });
                    for (unsigned i = 0; i < std::min<std::size_t>(8, shortlist.size()); ++i) {
                        if (!funded(24000))
                            break;
                        Pos p = shortlist[i].pos;
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
                        if (e.alive && added_control_windows(e, s.duration) > 0 &&
                            can_cast_at(w, s, e) && direct_hit_survives(w.self, e)) {
                            const double returned =
                                e.type == ren_type ? .2 * e.focus * w.self.mitigation : 0;
                            const double after = std::max(
                                0.0, current - enemy_raw(w, e, w.self.pos) * w.self.mitigation +
                                         returned);
                            if (after < best - .01) {
                                result = cast_unit(s, e.id, "escape-control");
                                best = after;
                            }
                        }
                }
            }
    // A pointless side-step is not an escape. Homeward progress on a risk tie
    // remains useful, but no action is manufactured when nothing improves.
    return w.round == static_cast<int>(bc::round_number()) ? result : std::nullopt;
}

inline std::optional<Proposal>
combat_proposal(World &w, Memory &memory, bool farming_context = false, int planning_floor = 0) {
    using namespace combat_detail;
    if (!w.self.alive || w.self.stunned || w.self.channel != Channel::None ||
        bc::fuel_remaining() < 32000 || w.round != static_cast<int>(bc::round_number()))
        return std::nullopt;
    const int start_fuel = static_cast<int>(bc::fuel_remaining());
    const int floor =
        planning_floor > 0 ? std::max(20000, planning_floor) : std::max(40000, start_fuel - 18000);
    auto optional_work = [&]() {
        return static_cast<int>(bc::fuel_remaining()) > floor &&
               w.round == static_cast<int>(bc::round_number());
    };
    const double incoming = incoming_damage(w, w.self.pos);
    if (w.round != static_cast<int>(bc::round_number()))
        return std::nullopt;
    const bool endangered =
        incoming >= w.self.hp * .80 || (incoming > 0 && w.self.health_fraction() < .35);
    std::optional<ReplyBaseline> walk_baseline;
    auto reply_cost = [&](const Action &first, double after, bool movement_first = false) {
        const bool preserves_walk = preserves_ready_walk(w.self, first, movement_first);
        if (!preserves_walk && !walk_baseline)
            walk_baseline = walking_reply_baseline(w, memory, incoming, floor);
        return marginal_reply_cost(after, incoming, preserves_walk,
                                   walk_baseline ? walk_baseline->damage : 0,
                                   walk_baseline && walk_baseline->known);
    };
    std::optional<Proposal> best;
    int best_target = std::numeric_limits<int>::max();
    auto take = [&](Action action, Phase phase, Priority priority, double value,
                    const Actor *target = nullptr) {
        if (value <= 0 || !std::isfinite(value))
            return;
        const int id = target ? target->id : std::numeric_limits<int>::max();
        if (!best || priority > best->priority ||
            (priority == best->priority &&
             (value > best->value + .001 ||
              (std::abs(value - best->value) <= .001 && id < best_target)))) {
            best = proposal(action, phase, priority, value, memory, w.round);
            if (target)
                best->mission.target = target->pos;
            best_target = id;
        }
    };
    auto offer = [&](const ShortSequence &sequence, const Actor &target, Pos from, double reply,
                     const Action *first_override = nullptr) {
        auto effect = sequence.exchange;
        if (effect.returned >= w.self.hp)
            return;
        const Action action = first_override ? *first_override : sequence.first;
        const bool immediate_control =
            immediate_sequence_control(w.self, sequence, first_override != nullptr);
        bool immediate_kill = immediate_sequence_kill(sequence, first_override != nullptr);
        if (immediate_kill && action.kind == Kind::CastChampion &&
            (endangered || target.channel == Channel::Tribute)) {
            // Only a selected useful lethal needs the native target predictor;
            // broad candidate enumeration uses the observed scaling/shield model.
            immediate_kill = action.slot >= 0 && action.slot < 2 && bc::fuel_remaining() >= 24000 &&
                             spell_hp_damage(w, w.spells[action.slot], target) >= target.hp - .001;
        }
        std::vector<ImmediateRemoval> removals;
        removals.reserve(w.enemies.size() + 1);
        if (immediate_control || immediate_kill)
            removals.push_back({&target, immediate_kill, immediate_control});
        const bool splash_basic = action.kind == Kind::BasicChampion && w.self.type == 10;
        const bool primary_basic_killed =
            splash_basic && basic_hp_damage(w.self, target) >= target.hp - .001;
        if (splash_basic) {
            for (const auto &other : w.enemies)
                if (basic_splash_hits(w.self, target, other) &&
                    basic_hp_damage(w.self, other) >= other.hp - .001)
                    removals.push_back({&other, true, false});
            if (!immediate_kill && killed_by_effects(removals, target)) {
                // A linked secondary's death already ends the primary's life.
                // A planned reset cannot damage that dead primary again.
                effect = sequence_exchange(w.self, target, w.self.strength);
                immediate_kill = true;
            }
        }
        const double source = enemy_raw(w, target, from) * w.self.mitigation;
        const double raw_return =
            target.type == ren_type ? effect.hits * .2 * target.focus * w.self.mitigation : 0;
        double removed = 0;
        for (const auto &other : w.enemies)
            if (source_removed_by(removals, other))
                removed +=
                    other.id == target.id ? source : enemy_raw(w, other, from) * w.self.mitigation;
        const double after = std::max(0.0, reply - removed + raw_return);
        const bool deciding =
            target.channel == Channel::Tribute &&
            w.enemy_score + target.gems >= static_cast<int>(bc::constants::winning_gems) &&
            (immediate_control || immediate_kill);
        if (!combat_trade_allowed(incoming, after, w.self.hp, deciding))
            return;
        Priority priority = source > 0 ? Priority::Incumbent : Priority::Routine;
        if (endangered && (immediate_control || immediate_kill) && after < w.self.hp)
            priority = Priority::Survival;
        if (deciding)
            priority = Priority::Deciding;
        double value = effect.hp_damage + .5 * effect.shield_damage - effect.returned;
        for (const auto &other : w.enemies)
            if ((effect.lethal && immediate_effect_removes(target, other, true, false)) ||
                killed_by_effects(removals, other))
                value += 300 + other.gems * 2;
        if (sequence.control_windows > 0)
            value += std::min(200.0, source) + (target.channel != Channel::None ? 200 : 0);
        if (splash_basic)
            value += basic_splash_value(w, target, primary_basic_killed);
        // Unchanged holding pressure is paid by both alternatives. Only a
        // currently ready walk consumed by this first action loses an escape.
        value -= reply_cost(action, after, first_override != nullptr);
        value *= target_importance(target);
        if (memory.focus == target.id && memory.focus_until >= w.round)
            value *= 1.10;
        if (deciding || priority == Priority::Survival)
            value += 10000;
        take(action, deciding ? Phase::Protect : Phase::Fight, priority, value, &target);
    };

    // Cheap legal stationary sequences are always available before optional
    // geometry. Each uses at most one cast: basic/reset/basic, reset/basic, or
    // cast/basic. Shields and retaliation evolve across the actual hit order.
    std::vector<const Actor *> targets;
    for (const auto &enemy : w.enemies) {
        if (bc::fuel_remaining() < 24000 || w.round != static_cast<int>(bc::round_number()))
            break;
        if (!enemy.alive)
            continue;
        const double source = enemy_raw(w, enemy, w.self.pos);
        if (farming_context && source == 0 && enemy.channel == Channel::None)
            continue;
        targets.push_back(&enemy);
        for (const auto &sequence : stationary_sequences(w.self, enemy)) {
            if (bc::fuel_remaining() < 22000 || w.round != static_cast<int>(bc::round_number()))
                break;
            if (w.self.range > 1 && sequence.first.kind == Kind::BasicChampion && w.self.can_move &&
                endangered && !sequence.exchange.lethal)
                continue;
            offer(sequence, enemy, w.self.pos, incoming);
        }
    }

    // Ground centers are legal geometric candidates, not hidden unit targets.
    // Coarse scoring is local arithmetic; only the best eight distinct centers
    // per slot enter the exact candidate comparison.
    if (w.self.can_cast && optional_work())
        for (const auto &spell : w.spells)
            if (spell.ready && spell.kind == 3 && spell.ground) {
                struct Area {
                    Pos center;
                    double merit;
                };
                std::vector<Area> centers;
                for (const auto *enemy : targets)
                    for (int dy = -spell.radius; dy <= spell.radius;
                         dy += std::max(1, spell.radius))
                        for (int dx = -spell.radius; dx <= spell.radius;
                             dx += std::max(1, spell.radius)) {
                            if (!optional_work())
                                break;
                            Pos center{enemy->pos.x + dx, enemy->pos.y + dy};
                            if (!w.geo.valid(center) || distance(w.self.pos, center) > spell.range)
                                continue;
                            bool duplicate = false;
                            for (const auto &c : centers)
                                duplicate |= c.center == center;
                            if (duplicate)
                                continue;
                            double merit = 0;
                            for (const auto &recipient : w.enemies)
                                if (recipient.alive &&
                                    distance(recipient.pos, center) <= spell.radius) {
                                    const auto effect =
                                        sequence_exchange(w.self, recipient, spell.amount);
                                    merit += effect.hp_damage + .5 * effect.shield_damage +
                                             (effect.lethal ? 300 + recipient.gems * 2 : 0);
                                }
                            centers.push_back({center, merit});
                        }
                std::sort(centers.begin(), centers.end(), [](const auto &a, const auto &b) {
                    if (a.merit != b.merit)
                        return a.merit > b.merit;
                    return a.center.y < b.center.y ||
                           (a.center.y == b.center.y && a.center.x < b.center.x);
                });
                for (unsigned i = 0;
                     i < std::min<std::size_t>(8, centers.size()) && optional_work(); ++i) {
                    const auto center = centers[i].center;
                    const Actor *anchor = nullptr;
                    double gain = 0, raw_return = 0, removed = 0;
                    std::vector<ImmediateRemoval> removals;
                    removals.reserve(w.enemies.size());
                    bool deciding = false;
                    for (const auto &recipient : w.enemies)
                        if (recipient.alive && distance(recipient.pos, center) <= spell.radius) {
                            const auto effect = sequence_exchange(w.self, recipient, spell.amount);
                            const int control =
                                applies_control(w.self, spell)
                                    ? added_control_windows(recipient, spell.duration)
                                    : 0;
                            const double source =
                                enemy_raw(w, recipient, w.self.pos) * w.self.mitigation;
                            gain += effect.hp_damage + .5 * effect.shield_damage +
                                    (effect.lethal ? 300 + recipient.gems * 2 : 0);
                            if (control)
                                gain += std::min(200.0, source) +
                                        (recipient.channel != Channel::None ? 200 : 0);
                            if (effect.lethal || control)
                                removals.push_back({&recipient, effect.lethal, control > 0});
                            if (recipient.type == ren_type)
                                raw_return += .2 * recipient.focus * w.self.mitigation;
                            bool stops = recipient.channel == Channel::Tribute &&
                                         w.enemy_score + recipient.gems >=
                                             static_cast<int>(bc::constants::winning_gems) &&
                                         (effect.lethal || control);
                            if (!anchor || stops ||
                                target_importance(recipient) > target_importance(*anchor))
                                anchor = &recipient;
                            deciding |= stops;
                        }
                    // A linked body may die outside the area, or both may be
                    // direct recipients. Count each observed reply/value once.
                    for (const auto &other : w.enemies)
                        if (source_removed_by(removals, other)) {
                            removed += enemy_raw(w, other, w.self.pos) * w.self.mitigation;
                            gain += linked_only_removal_value(removals, other);
                        }
                    const double returned = std::max(0.0, raw_return - w.self.shield);
                    if (!anchor || returned >= w.self.hp)
                        continue;
                    const double after = std::max(0.0, incoming - removed + raw_return);
                    if (!combat_trade_allowed(incoming, after, w.self.hp, deciding))
                        continue;
                    Priority priority = removed > 0 ? Priority::Incumbent : Priority::Routine;
                    if (endangered && removed > 0 && after < w.self.hp)
                        priority = Priority::Survival;
                    if (deciding)
                        priority = Priority::Deciding;
                    Action action;
                    action.kind = Kind::CastGround;
                    action.slot = spell.slot;
                    action.at = center;
                    action.reason = "fight-useful-area";
                    double value = gain - returned - reply_cost(action, after);
                    if (priority >= Priority::Survival)
                        value += 10000;
                    take(action, deciding ? Phase::Protect : Phase::Fight, priority, value, anchor);
                }
            }

    // Protection competes for the same cast. A claimed save must change the
    // recipient's actual next response; decorative healing is an ordinary job.
    if (w.self.can_cast)
        for (const auto &spell : w.spells) {
            if (!spell.ready)
                continue;
            if (spell.kind == 7 && spell.self && incoming > 0 && spell.amount > w.self.shield) {
                const double saved = std::min(incoming, spell.amount - w.self.shield);
                const bool survives = incoming >= w.self.hp && incoming - saved < w.self.hp;
                take(cast_self(spell, "protect-useful-self-shield"), Phase::Protect,
                     survives ? Priority::Survival : Priority::Incumbent,
                     saved + (survives ? 10000 : 0));
            }
            if (spell.kind != 5 || !spell.allies || incoming >= w.self.hp)
                continue;
            for (const auto &ally : w.allies) {
                if (ally.id == w.self.id || !ally.alive ||
                    distance(w.self.pos, ally.pos) > spell.range)
                    continue;
                const double heal = std::min(spell.amount, std::max(0.0, ally.max_hp - ally.hp));
                if (heal <= 0)
                    continue;
                // The cheap upper bound remains useful if optional forecasting
                // is no longer funded; it does not manufacture a guaranteed save.
                const double danger = optional_work() ? incoming_for(w, ally, ally.pos) : -1;
                const bool saved = danger >= ally.hp && danger < ally.hp + heal;
                take(cast_unit(spell, ally.id,
                               saved ? "protect-lethal-heal" : "support-effective-heal"),
                     Phase::Protect, saved ? Priority::Survival : Priority::Routine,
                     heal + (saved ? 10000 + ally.gems : 0));
            }
        }
    if (w.self.can_cast && incoming < w.self.hp && optional_work())
        for (const auto &spell : w.spells)
            if (spell.ready && spell.kind == 4 && spell.enemies) {
                std::vector<const Actor *> eligible;
                for (const auto &enemy : w.enemies)
                    if (peel_target_eligible(w.self, spell, enemy))
                        eligible.push_back(&enemy);
                if (eligible.empty())
                    continue;
                for (const auto &ally : w.allies) {
                    if (!optional_work())
                        break;
                    if (ally.id == w.self.id || !ally.alive)
                        continue;
                    const double danger = incoming_for(w, ally, ally.pos);
                    if (danger < ally.hp)
                        continue;
                    for (const auto *enemy : eligible) {
                        const double removed = enemy_raw(w, *enemy, ally.pos) * ally.mitigation;
                        const double own_source =
                            enemy_raw(w, *enemy, w.self.pos) * w.self.mitigation;
                        const double returned =
                            enemy->type == ren_type ? .2 * enemy->focus * w.self.mitigation : 0;
                        const double own_after = std::max(0.0, incoming - own_source + returned);
                        if (removed > 0 && danger - removed < ally.hp &&
                            combat_trade_allowed(incoming, own_after, w.self.hp))
                            take(cast_unit(spell, enemy->id, "protect-lethal-peel"), Phase::Protect,
                                 Priority::Survival, 10000 + ally.gems + removed, enemy);
                    }
                }
            }
    if (best && best->priority >= Priority::Survival)
        return best;
    if (endangered) {
        if (auto escape = escape_action(w, floor))
            return proposal(*escape, Phase::Escape, Priority::Survival, 20000 + incoming, memory,
                            w.round);
        return best; // No safe exit: spend only a legal, useful remaining action.
    }

    // Compare holding with actual neighboring positions. A ranged walk removes
    // its ordinary basic, but a compatible spell/reset can still be useful.
    // Every projection consumes the same one-cast allowance as the stationary
    // sequence model, and no remote ally follow-up is added.
    std::sort(targets.begin(), targets.end(), [&](const auto *a, const auto *b) {
        const double av = target_importance(*a) / (1 + distance(w.self.pos, a->pos));
        const double bv = target_importance(*b) / (1 + distance(w.self.pos, b->pos));
        return av > bv || (av == bv && a->id < b->id);
    });
    auto compare_position = [&](Pos pos, const Action &movement, bool dash) {
        if (!w.free(pos))
            return;
        if (memory.hold_group >= 0 && w.on_group(memory.hold_group, w.self.pos) &&
            !w.on_group(memory.hold_group, pos))
            return;
        const double reply = incoming_damage(w, pos);
        if (reply >= w.self.hp * .80)
            return;
        Actor projected = w.self;
        projected.pos = pos;
        projected.can_move = false;
        if (dash) {
            projected.can_cast = false;
            for (auto &spell : projected.spells)
                spell.ready = false;
        } else {
            if (projected.range > 1)
                projected.can_attack = false;
            for (auto &spell : projected.spells)
                if (spell.exclusive)
                    spell.ready = false;
        }
        for (unsigned j = 0; j < std::min<std::size_t>(2, targets.size()); ++j)
            for (auto sequence : stationary_sequences(projected, *targets[j])) {
                ++sequence
                      .actions; // Movement precedes, rather than duplicates, the useful sequence.
                offer(sequence, *targets[j], pos, reply, &movement);
            }
    };
    if (w.self.can_move && !farming_context && optional_work())
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                if ((!dx && !dy) || !optional_work())
                    continue;
                Pos pos{w.self.pos.x + dx, w.self.pos.y + dy};
                compare_position(pos, move(pos, "fight-kite-compatible-sequence"), false);
            }
    if (w.self.can_cast && !farming_context && optional_work() &&
        static_cast<int>(bc::fuel_remaining()) > std::max(36000, floor + 6000))
        for (const auto &spell : w.spells)
            if (spell.ready && spell.kind == 6 && spell.ground && w.self.can_attack) {
                auto blocked = bc::map::walls() | w.geo.enemy_spawn | w.occupied |
                               bc::vision::teleport_tiles();
                blocked.set(sdk(w.self.pos), false);
                auto legal = blocked.reachable_tiles(sdk(w.self.pos), spell.range);
                if (!optional_work() || bc::fuel_remaining() < 24000)
                    return w.round == static_cast<int>(bc::round_number()) ? best : std::nullopt;
                native_context = "combat:dash-range";
                legal &= w.me.abilities()[spell.slot].valid_tiles();
                legal &= ~(w.geo.static_blocked | w.occupied);
                struct Landing {
                    Pos pos;
                    int distance;
                };
                std::vector<Landing> positions;
                for (auto raw : legal.positions()) {
                    const Pos pos = position(raw);
                    int nearest = unreachable;
                    for (const auto *target : targets)
                        nearest = std::min(nearest, distance(pos, target->pos));
                    if (nearest <= w.self.range && pos != w.self.pos)
                        positions.push_back({pos, nearest});
                }
                std::sort(positions.begin(), positions.end(), [](const auto &a, const auto &b) {
                    if (a.distance != b.distance)
                        return a.distance < b.distance;
                    return a.pos.y < b.pos.y || (a.pos.y == b.pos.y && a.pos.x < b.pos.x);
                });
                for (unsigned i = 0;
                     i < std::min<std::size_t>(8, positions.size()) && optional_work(); ++i) {
                    Action dash;
                    dash.kind = Kind::CastGround;
                    dash.slot = spell.slot;
                    dash.at = positions[i].pos;
                    dash.reason = "fight-dash-plan-basic";
                    compare_position(dash.at, dash, true);
                }
            }
    if (!best && incoming > 0 && optional_work())
        if (auto escape = escape_action(w, floor))
            return proposal(*escape, Phase::Escape, Priority::Incumbent, incoming, memory, w.round);
    return best;
}

#else
} // namespace combat_detail
#endif
} // namespace tactics

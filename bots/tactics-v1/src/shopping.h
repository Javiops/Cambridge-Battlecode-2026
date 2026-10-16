#pragma once

#include "camp_actions.h"
#include "sdk_world.h"
#include "solo.h"
#include <algorithm>
#include <array>
#include <optional>
#include <string_view>

namespace tactics {

enum class ShopFamily { Monster, Power, Durability, Treasure, Jungle, Home, Bruiser };
enum class ShopStat { Strength, Focus, Health };
static_assert(static_cast<int>(cambc::item_type::enum_type::count) == 42,
              "Review catalogue grouping when the SDK item catalogue changes");

inline int shop_raw(ShopFamily family, ShopStat stat, bool emblem = false) {
    return 6 * static_cast<int>(family) + 2 * static_cast<int>(stat) + (emblem ? 1 : 0);
}
inline cambc::item_type shop_item(int raw) {
    return cambc::item_type{static_cast<std::uint32_t>(raw)};
}
// Catalogue metadata is immutable for the pinned engine. Dynamic wallet,
// inventory and can_buy remain fresh; only these public definitions are cached.
inline const cambc::item_info &shop_info(int raw) {
    static std::array<std::optional<cambc::item_info>, 42> catalogue;
    auto &entry = catalogue.at(raw);
    if (!entry)
        entry = shop_item(raw).info();
    return *entry;
}
inline bool shop_unique_family(ShopFamily f) {
    return f != ShopFamily::Power && f != ShopFamily::Bruiser;
}

struct ShopInventory {
    std::array<int, 42> count{};
    std::array<bool, 7> active{};
    bool has(ShopFamily f) const {
        return active[static_cast<int>(f)];
    }
};
inline ShopInventory shop_inventory(const cambc::enum_map<cambc::item_type> &counts) {
    ShopInventory result;
    for (int i = 0; i < 42; ++i) {
        result.count[i] = static_cast<int>(counts[shop_item(i)]);
        if ((i & 1) && result.count[i] > 0)
            result.active[i / 6] = true;
    }
    return result;
}
inline ShopStat shop_role_stat(int physical_type) {
    // Ryth's bonus-Health Strength is considered by the survival alternative;
    // Ren uses the documented attack-heavy fallback unless a richer cast model
    // can demonstrate that Focus changes the next useful sequence.
    switch (physical_type) {
    case 3:
    case 5:
    case 6:
    case 8:
    case 11:
        return ShopStat::Focus;
    default:
        return ShopStat::Strength;
    }
}

// One finite acquisition receipt. Projected gold never enters World or inventory.
struct CashInvestment {
    int group = -1, item = -1, count = 0, before = 0, emblem_before = 0;
    int gold_before = 0, expected_gold = 0, created = -1, until = -1;
    Pos stage{}, capture{};
    Mission gem_mission{};
    double rate = 0, absence = 0;
    bool holding = false, started = false;
};

struct ShoppingState {
    CashInvestment cash{};
    int cached_cash_group = -1;
    Pos cached_cash_stage{};
    std::array<int, 2> cached_gem_group{-1, -1};
    std::array<Pos, 2> cached_gem_stage{};
    int cached_gem_next = 0;
    std::vector<Pos> own_spawn_positions; // Immutable public geometry; completed once.
    std::array<int, 2> gem_route_group{-1, -1};
    std::array<Pos, 2> gem_route_stage{};
    std::array<std::array<int, 4>, 2> gem_route_lengths{};
    int gem_route_next = 0;
    std::optional<cambc::champion_stats> own_growth;
    int goal = -1, goal_group = -2;
    Phase goal_phase = Phase::Unassigned;
    int failed_round = -1, last_round = -1, heals_this_round = 0;
    int planned_heal = -1, pending_heal = -1, heal_count = 0, heal_gold = 0;
    // Optional planner forecasts are deliberately zero unless the caller has
    // a named remaining income/return schedule. No fixed round payback rule.
    double expected_base_gold = 0;
    int expected_useful_recalls = 0;
    int reserve_consumable = -1;
    const char *reserve_reason = "no-consumable-mission";
    int forecast_group = -1;
    double forecast_cycles = 0;
    // Exact bundle behind an elective return; it survives the temporary
    // Recover/Channel mission instead of silently changing to a generic build.
    int investment_item = -1, investment_count = 0, investment_before = 0,
        investment_emblem_before = 0, investment_round = -1, investment_buy_gold = 0;
    double investment_gain = 0, investment_absence = 0;
    Mission investment_mission{}, investment_origin{};
    bool investment_gem_unlock = false;
};

struct UpgradeDelta {
    double health = 0, strength = 0, focus = 0;
    bool first_passive = false;
    ShopFamily family = ShopFamily::Power;
};
inline UpgradeDelta upgrade_delta(int raw, const ShopInventory &inv,
                                  const cambc::champion_stats &growth, int count = 1) {
    const auto &item = shop_info(raw);
    double hp = count * item.health_points, str = count * item.strength_points,
           focus = count * item.focus_points;
    const bool completes = inv.count[raw] + count == 5 && item.result.has_value();
    if (completes) {
        const auto &combined = shop_info(static_cast<int>(*item.result));
        hp = combined.health_points - inv.count[raw] * item.health_points;
        str = combined.strength_points - inv.count[raw] * item.strength_points;
        focus = combined.focus_points - inv.count[raw] * item.focus_points;
    }
    const auto family = static_cast<ShopFamily>(raw / 6);
    UpgradeDelta result{hp * growth.health_growth, str * growth.strength_growth,
                        focus * growth.focus_growth, completes && !inv.has(family), family};
    return result;
}
inline void forecast_investment(const World &w, const Mission &mission, ShoppingState &state) {
    state.expected_base_gold = 0;
    state.expected_useful_recalls = 0;
    state.forecast_cycles = 0;
    state.forecast_group = -1;
    if (mission.group < 0 || mission.group >= static_cast<int>(w.geo.groups.size()) ||
        !w.self.alive)
        return;
    const auto &group = w.geo.groups[mission.group];
    const int remaining = std::max(0, static_cast<int>(cambc::constants::max_rounds) - w.round);
    double damage = w.self.strength;
    for (const auto &spell : w.spells)
        if (camp_damage_ability(spell))
            damage = std::max(damage, w.self.strength + spell.amount / std::max(1, spell.recharge));
    if (w.self.monster)
        damage *= 1.1;
    const double clear = std::ceil(group.initial_hp / std::max(1.0, damage));
    const double route = w.geo.estimate(w.self.pos, mission.target);
    const double interval = std::max<double>(group.respawn, route + clear + 6);
    const int recipients = std::max(
        1, static_cast<int>(std::count_if(w.allies.begin(), w.allies.end(), [&](const Actor &a) {
            return a.alive && w.matching_claim(a.id, mission.group);
        })));
    // A named repeat route forecast, capped to eight cycles. It is an estimate,
    // not promised future income or a claim that every public camp stays ours.
    state.forecast_cycles =
        std::max(0.0, std::min(8.0, (remaining - route - clear - 6) / std::max(1.0, interval)));
    if (!w.enemies.empty() || w.warning_near(mission.target, 4))
        state.forecast_cycles = std::min(1.0, state.forecast_cycles);
    state.forecast_group = mission.group;
    state.expected_base_gold = state.forecast_cycles * group.gold / recipients;
    if (group.initial_strength > 0 &&
        clear * group.initial_strength * w.self.camp_mitigation > w.self.max_hp * .35)
        state.expected_useful_recalls = static_cast<int>(std::floor(state.forecast_cycles));
}
inline double upgrade_mission_value(const World &w, const Mission &mission,
                                    const UpgradeDelta &delta, const ShoppingState &state) {
    const bool farm = mission.group >= 0 && mission.group < static_cast<int>(w.geo.groups.size());
    double hp = 0, enemy_pressure = w.exposure(w.self.pos) * w.self.mitigation,
           monster_pressure = 0, value = 1;
    if (farm) {
        const auto &g = w.geo.groups[mission.group];
        hp = g.initial_hp;
        value = g.gems + .25 * g.gold;
        if (w.self.range <= 2)
            monster_pressure = g.initial_strength * w.self.camp_mitigation;
    } else
        for (const auto &enemy : w.enemies)
            hp = std::max(hp, enemy.hp + enemy.shield);
    double added_strength = delta.strength + (w.self.type == 0 ? .01 * delta.health : 0);
    double old_damage = w.self.strength, added_cast = 0;
    for (const auto &spell : w.spells)
        if ((farm ? camp_damage_ability(spell) : spell.enemies) &&
            (spell.kind == 2 || spell.kind == 3 || spell.kind == 4)) {
            old_damage =
                std::max(old_damage, w.self.strength + spell.amount / std::max(1, spell.recharge));
            added_cast =
                std::max(added_cast, delta.focus * spell.scale / std::max(1, spell.recharge));
        }
    double next_damage = old_damage + added_strength + added_cast;
    if (farm && w.self.monster)
        old_damage *= 1.1, next_damage *= 1.1;
    if (farm && !w.self.monster && delta.first_passive && delta.family == ShopFamily::Monster)
        next_damage *= 1.1;
    const double old_turns = std::ceil(hp / std::max(1.0, old_damage));
    const double new_turns = std::ceil(hp / std::max(1.0, next_damage));
    double score = std::max(0.0, old_turns - new_turns) * value;
    score += value * (next_damage - old_damage) / std::max(1.0, old_damage);
    const double pressure = std::max(0.0, enemy_pressure + monster_pressure - w.self.shield);
    double reduced_enemy = enemy_pressure, reduced_monster = monster_pressure;
    if (delta.first_passive && delta.family == ShopFamily::Durability)
        reduced_enemy *= .9, reduced_monster *= .9;
    if (farm && delta.first_passive && delta.family == ShopFamily::Jungle)
        reduced_monster *= .7;
    const double reduced = std::max(0.0, reduced_enemy + reduced_monster - w.self.shield);
    const double next_hp = w.self.hp + (w.in_spawn(w.self.pos) ? delta.health : 0);
    if (pressure >= w.self.hp && reduced < next_hp)
        score += 10000; // A concrete next-response survival breakpoint.
    score += value * std::max(0.0, pressure - reduced) / std::max(1.0, w.self.max_hp);
    score += value * delta.health / std::max(1.0, w.self.max_hp) * (pressure > 0 ? 1 : .05);
    for (const auto &spell : w.spells)
        if (spell.kind == 5 || spell.kind == 7) {
            double effective = 0;
            if (spell.kind == 5) {
                for (const auto &ally : w.allies)
                    if (distance(w.self.pos, ally.pos) <= spell.range)
                        effective =
                            std::max(effective, std::min(delta.focus * spell.scale,
                                                         std::max(0.0, ally.max_hp - ally.hp)));
            } else
                effective = std::min(pressure, delta.focus * spell.scale);
            score += value * effective / std::max(1.0, w.self.max_hp);
        }
    if (delta.first_passive && delta.family == ShopFamily::Treasure)
        score += .25 * .2 * state.expected_base_gold;
    if (delta.first_passive && delta.family == ShopFamily::Home)
        score += 2 * state.expected_useful_recalls * std::max(0.0, mission.rate);
    return score;
}

inline bool shop_farm_phase(const Mission &m) {
    return m.group >= 0 &&
           (m.phase == Phase::Travel || m.phase == Phase::Assemble || m.phase == Phase::Clear ||
            m.phase == Phase::Collect || m.phase == Phase::Reenter);
}
inline bool shop_family_useful(ShopFamily f, bool farm, bool damaging, bool pressure,
                               const ShoppingState &state, int remaining) {
    switch (f) {
    case ShopFamily::Monster:
        return farm;
    case ShopFamily::Jungle:
        return damaging;
    case ShopFamily::Durability:
        return damaging || pressure;
    case ShopFamily::Treasure:
        return state.expected_base_gold >= 750 && remaining > 0;
    case ShopFamily::Home:
        return state.expected_useful_recalls > 0 && remaining > 0;
    default:
        return true;
    }
}

// A bounded, auditable fallback selector: useful first passive, a relevant
// almost-complete item, then primary Power. It does not claim an optimal DPS or
// counterfactual survival model when those thresholds are unresolved.
inline int shop_choose_shard(const ShopInventory &inv, int type, const Mission &mission,
                             bool damaging, bool pressure, const ShoppingState &state,
                             int remaining) {
    const bool farm = shop_farm_phase(mission);
    const auto primary = shop_role_stat(type);
    ShopFamily fallback = ShopFamily::Power;
    ShopStat stat = primary;
    if (farm && !inv.has(ShopFamily::Monster))
        fallback = ShopFamily::Monster;
    if (damaging && !inv.has(ShopFamily::Jungle))
        fallback = ShopFamily::Jungle;
    if (pressure && !inv.has(ShopFamily::Durability))
        fallback = ShopFamily::Durability;
    // Health is for the next mission's durable frontline, not an assertion that
    // a field Health purchase heals Tavi's current HP.
    if (pressure && (type == 0 || type == 4 || type == 7 || type == 9 || type == 10))
        stat = ShopStat::Health;

    const int fallback_raw = shop_raw(fallback, stat);
    int partial = -1, partial_count = 0;
    for (int raw = 0; raw < 42; raw += 2) {
        const auto f = static_cast<ShopFamily>(raw / 6);
        const auto s = static_cast<ShopStat>((raw % 6) / 2);
        if ((s != primary && s != stat) || (shop_unique_family(f) && inv.has(f)) ||
            !shop_family_useful(f, farm, damaging, pressure, state, remaining))
            continue;
        if (inv.count[raw] > partial_count) {
            partial_count = inv.count[raw];
            partial = raw;
        }
    }
    // Completion is a real discrete event; four identical shards can activate a
    // still-useful first passive now. Three + two different stat shards cannot.
    if (partial >= 0 && partial_count >= 4)
        return partial;
    if (state.goal >= 0 && state.goal < 42 && !(state.goal & 1) &&
        state.goal_group == mission.group && state.goal_phase == mission.phase) {
        const auto f = static_cast<ShopFamily>(state.goal / 6);
        if ((!shop_unique_family(f) || !inv.has(f)) &&
            shop_family_useful(f, farm, damaging, pressure, state, remaining) &&
            !(pressure && f != ShopFamily::Durability && !inv.has(ShopFamily::Durability)))
            return state.goal;
    }
    return fallback_raw;
}

struct ShopBundle {
    int raw = -1, count = 0;
    UpgradeDelta delta{};
    double score = 0;
    bool affordable = false;
};
inline ShopBundle select_shop_bundle(World &w, const Mission &mission,
                                     const ShopInventory &inventory, const ShoppingState &state,
                                     int reserve = 0) {
    const bool farm = shop_farm_phase(mission);
    bool pressure = false;
    for (const auto &enemy : w.enemies)
        pressure |= enemy.alive && distance(w.self.pos, enemy.pos) <= 8;
    const bool damaging = farm && mission.group < static_cast<int>(w.geo.groups.size()) &&
                          w.geo.groups[mission.group].initial_strength > 0 && w.self.range <= 2;
    const int remaining = std::max(0, static_cast<int>(cambc::constants::max_rounds) - w.round);
    int raw =
        shop_choose_shard(inventory, w.self.type, mission, damaging, pressure, state, remaining);
    auto bundle_count = [&](int candidate) {
        const int cost = static_cast<int>(shop_info(candidate).cost);
        return cost > 0 ? std::max(0, std::min(5 - inventory.count[candidate],
                                               (w.gold - reserve) / cost))
                        : 0;
    };
    ShopBundle result;
    if (bundle_count(raw) <= 0)
        return result;
    result.raw = raw;
    result.count = bundle_count(raw);
    result.affordable = true;
    if (!w.self.alive || cambc::fuel_remaining() <= 25000)
        return result; // Explicit role-build fallback, never a priced return.
    const auto growth = w.me.base_stats();
    int completion = raw, most = 0;
    for (int item = 0; item < 42; item += 2) {
        const auto family = static_cast<ShopFamily>(item / 6);
        if (inventory.count[item] > most &&
            shop_family_useful(family, farm, damaging, pressure, state, remaining) &&
            (!shop_unique_family(family) || !inventory.has(family))) {
            most = inventory.count[item];
            completion = item;
        }
    }
    ShopFamily alternative = ShopFamily::Power;
    ShopStat stat = shop_role_stat(w.self.type);
    if (damaging && !inventory.has(ShopFamily::Jungle))
        alternative = ShopFamily::Jungle;
    else if (pressure && !inventory.has(ShopFamily::Durability)) {
        alternative = ShopFamily::Durability;
        stat = ShopStat::Health;
    } else if (state.expected_base_gold >= 750 && !inventory.has(ShopFamily::Treasure))
        alternative = ShopFamily::Treasure;
    else if (state.expected_useful_recalls > 1 && !inventory.has(ShopFamily::Home))
        alternative = ShopFamily::Home;
    else if (farm && !inventory.has(ShopFamily::Monster))
        alternative = ShopFamily::Monster;
    result.delta = upgrade_delta(raw, inventory, growth, result.count);
    result.score = upgrade_mission_value(w, mission, result.delta, state) / result.count;
    for (int candidate : {completion, shop_raw(alternative, stat)}) {
        const int count = bundle_count(candidate);
        if (count <= 0)
            continue;
        const auto delta = upgrade_delta(candidate, inventory, growth, count);
        const double score = upgrade_mission_value(w, mission, delta, state) / count;
        if (score > result.score * 1.1 + .001) {
            result.raw = candidate;
            result.count = count;
            result.delta = delta;
            result.score = score;
        }
    }
    return result;
}
struct ReturnPayoff {
    double saved_turns = 0, absence = 0, cycles = 0;
    bool known = false, worthwhile = false;
};
inline ReturnPayoff named_return_payoff(const Actor &body, const Group &group,
                                        const UpgradeDelta &delta, int remaining, int return_walk,
                                        int recall_ticks, double margin, int bank_walk = 0,
                                        int bank_ticks = 1) {
    ReturnPayoff out;
    // A gold-only route lacks a named completed-bank continuation in this
    // bounded model. It never manufactures one from equipment points.
    if (group.gems <= 0 || group.initial_hp <= 0 || return_walk < 0 || return_walk == unreachable ||
        bank_walk < 0 || bank_walk == unreachable || bank_ticks <= 0 || remaining <= 0 ||
        recall_ticks <= 0)
        return out;
    double old_damage = body.strength;
    const double strength =
        body.strength + delta.strength + (body.type == 0 ? .01 * delta.health : 0);
    double next_damage = strength;
    for (const auto &spell : body.spells)
        if (camp_damage_ability(spell)) {
            const double interval = std::max(1, spell.recharge);
            old_damage = std::max(old_damage, body.strength + spell.amount / interval);
            next_damage = std::max(
                next_damage, strength + (spell.amount + delta.focus * spell.scale) / interval);
        }
    if (body.monster)
        old_damage *= 1.1, next_damage *= 1.1;
    if (!body.monster && delta.first_passive && delta.family == ShopFamily::Monster)
        next_damage *= 1.1;
    const double old_clear = std::ceil(group.initial_hp / std::max(1.0, old_damage));
    const double new_clear = std::ceil(group.initial_hp / std::max(1.0, next_damage));
    const int bank_travel =
        (bank_walk + std::max(1, body.move_speed) - 1) / std::max(1, body.move_speed);
    // Every counted repetition includes a completed bank and the next resource
    // return leg. Counting a final extra return is conservative, not free income.
    const double interval =
        std::max<double>(group.respawn, old_clear + 6 + 2 * bank_travel + bank_ticks);
    out.absence = recall_ticks + 1 + std::ceil(double(return_walk) / std::max(1, body.move_speed));
    out.cycles = std::max(
        0.0, std::min(8.0, std::floor((remaining - out.absence) / std::max(1.0, interval))));
    const double injury = old_clear * group.initial_strength * body.camp_mitigation;
    if (injury > 0)
        out.cycles =
            std::min(out.cycles, std::max(0.0, std::floor((body.hp - .25 * body.max_hp) / injury)));
    out.saved_turns = std::max(0.0, old_clear - new_clear) * out.cycles;
    out.known = std::isfinite(out.saved_turns) && std::isfinite(out.absence) && out.cycles > 0;
    out.worthwhile = out.known && out.saved_turns > out.absence * margin;
    return out;
}
// The future schedule assumes the currently observed quiet sleeping resource
// remains available; actual arrival must revalidate it. This is a priced policy
// assumption, never a future-visibility or uncontested-ownership guarantee.
// One explicitly named completed gem cycle, not a conversion of gold or item
// points into imaginary score. Every length is a completed static walking field.
struct GemReturnLegs {
    int direct_walk = unreachable, spawn_walk = unreachable, capture_walk = unreachable,
        bank_walk = unreachable, home_walk = unreachable, capture_hold = 0, tribute = 0;
};
struct GemReturnPayoff {
    double next_ticks = 0, old_ticks = 0, absence = 0, saved_turns = 0;
    bool known = false, worthwhile = false, unlock = false;
};
inline Actor project_bundle_actor(Actor body, const UpgradeDelta &delta) {
    body.max_hp += delta.health;
    body.hp = body.max_hp; // Requires the explicitly priced spawn end/full heal.
    body.strength += delta.strength + (body.type == 0 ? .01 * delta.health : 0);
    body.focus += delta.focus;
    body.shield = 0;
    for (auto &spell : body.spells)
        if (spell.kind == 2 || spell.kind == 3 || spell.kind == 4 || spell.kind == 5 ||
            spell.kind == 7)
            spell.amount += delta.focus * spell.scale;
    if (delta.first_passive) {
        if (delta.family == ShopFamily::Jungle)
            body.camp_mitigation *= .7;
        if (delta.family == ShopFamily::Durability) {
            body.mitigation *= .9;
            body.camp_mitigation *= .9;
        }
        if (delta.family == ShopFamily::Home)
            body.home = true;
        if (delta.family == ShopFamily::Monster)
            body.monster = true; // The solo certificate applies camp damage once.
    }
    return body;
}
inline GemReturnPayoff completed_gem_return(const Actor &actual, const UpgradeDelta &delta,
                                            const Camp &camp, Pos stage, const GemReturnLegs &legs,
                                            int remaining, double margin) {
    GemReturnPayoff out;
    for (int length :
         {legs.direct_walk, legs.spawn_walk, legs.capture_walk, legs.bank_walk, legs.home_walk})
        if (length < 0 || length == unreachable)
            return out;
    if (!actual.alive || actual.gems != 0 || camp.awake || legs.capture_hold <= 0 ||
        legs.tribute <= 0 || remaining <= 0 || actual.channel != Channel::None)
        return out;
    const auto turns = [&](int distance) {
        return (distance + std::max(1, actual.move_speed) - 1) / std::max(1, actual.move_speed);
    };
    Actor old_full = actual;
    old_full.hp = old_full.max_hp;
    const Actor next = project_bundle_actor(actual, delta);
    const int returning = (actual.home ? 3 : 5) + 1 + turns(legs.spawn_walk);
    const auto before = certify_solo_clear(old_full, camp, stage, returning, false);
    const auto after = certify_solo_clear(next, camp, stage, returning, false);
    if (!before.known || !after.known || !after.feasible)
        return out;
    const auto completion = [&](const Actor &body, double clear) {
        // Both alternatives finish banked and recovered at spawn. Counting the
        // final heal even at high HP is a conservative complete-cycle bound.
        const int recovery = std::min(turns(legs.home_walk), body.home ? 3 : 5) + 1;
        return clear + turns(legs.capture_walk) + legs.capture_hold + turns(legs.bank_walk) +
               legs.tribute + recovery;
    };
    out.absence = returning;
    out.next_ticks = returning + completion(next, after.clear_ticks);
    if (!std::isfinite(out.next_ticks) || out.next_ticks >= remaining)
        return out;
    out.known = true;
    if (!before.feasible) {
        // Explicit first-version unlock policy: a proven infeasible same camp
        // becomes a real completed gem cycle. Continued origin gold farming is
        // a zero-gem alternative, not an exchange rate from gold into gems.
        out.unlock = out.worthwhile = true;
        return out;
    }
    out.old_ticks = returning + completion(old_full, before.clear_ticks);
    int direct_elapsed = turns(legs.direct_walk) + (actual.can_move ? 0 : 1);
    const bool ready_now =
        stage == actual.pos && !actual.completed && (actual.can_attack || actual.can_cast);
    if (!ready_now)
        direct_elapsed = std::max(1, direct_elapsed);
    const auto direct = certify_solo_clear(actual, camp, stage, direct_elapsed, ready_now);
    if (!direct.known)
        return GemReturnPayoff{}; // Unknown current alternative is never free.
    if (direct.feasible)
        out.old_ticks =
            std::min(out.old_ticks, direct_elapsed + completion(actual, direct.clear_ticks));
    out.saved_turns = std::max(0.0, out.old_ticks - out.next_ticks);
    out.worthwhile = out.saved_turns > out.absence * margin;
    return out;
}
struct CashGemLegs {
    int walk = unreachable, capture_walk = unreachable, hold = 0;
};
struct CashGemPayoff {
    double cash_ticks = 0, total_ticks = 0, absence = 0;
    bool known = false, worthwhile = false;
};
// A single real solo payout purchases one exact bundle, then completes the
// separately named gem cycle. Gold has no direct score or unbounded repetition.
inline CashGemPayoff completed_cash_gem(const Actor &actual, const Camp &cash, Pos cash_stage,
                                        Pos cash_capture, const CashGemLegs &cash_legs, int wallet,
                                        int sole_gold, int bundle_cost, const UpgradeDelta &delta,
                                        const Camp &gem, Pos gem_stage,
                                        const GemReturnLegs &gem_legs, int remaining,
                                        double margin) {
    CashGemPayoff out;
    if (wallet < 0 || sole_gold <= 0 || bundle_cost <= wallet || bundle_cost > wallet + sole_gold ||
        cash.awake || gem.awake || cash_legs.walk < 0 || cash_legs.walk == unreachable ||
        cash_legs.capture_walk < 0 || cash_legs.capture_walk == unreachable ||
        cash_legs.hold <= 0 || remaining <= 0)
        return out;
    const int speed = std::max(1, actual.move_speed);
    const auto turns = [&](int d) { return (d + speed - 1) / speed; };
    const bool now =
        actual.pos == cash_stage && !actual.completed && (actual.can_attack || actual.can_cast);
    const int elapsed = now ? 0 : std::max(1, turns(cash_legs.walk) + (actual.can_move ? 0 : 1));
    const auto clear = certify_solo_clear(actual, cash, cash_stage, elapsed, now);
    if (!clear.known || !clear.feasible)
        return out;
    out.cash_ticks = elapsed + clear.clear_ticks + turns(cash_legs.capture_walk) + cash_legs.hold;
    Actor after_cash = actual;
    after_cash.pos = cash_capture;
    after_cash.hp = clear.remaining_hp;
    after_cash.shield = 0;
    after_cash.completed = true;
    after_cash.can_move = after_cash.can_attack = after_cash.can_cast = false;
    // The clear may have spent any slot. Do not promise its original cooldown.
    for (auto &spell : after_cash.spells) {
        spell.ready = false;
        spell.cooldown = spell.recharge > 0 ? spell.recharge : unreachable;
    }
    const int left = remaining - static_cast<int>(std::ceil(out.cash_ticks));
    const auto continuation =
        completed_gem_return(after_cash, delta, gem, gem_stage, gem_legs, left, margin);
    if (!continuation.known || !continuation.unlock || !continuation.worthwhile)
        return CashGemPayoff{};
    out.total_ticks = out.cash_ticks + continuation.next_ticks;
    out.absence = continuation.absence;
    out.known = std::isfinite(out.total_ticks) && out.total_ticks < remaining;
    out.worthwhile = out.known;
    return out;
}
inline std::array<int, 2> gem_investment_groups(const World &w) {
    std::array<int, 2> result{-1, -1};
    std::array<int, 2> cost{unreachable, unreachable};
    for (unsigned gi = 0; gi < w.groups.size(); ++gi) {
        if (!assembly_detail::simple_sleeping(w, gi) || w.geo.groups[gi].gems <= 0 ||
            w.warning_near(w.groups[gi].camps.front().pos, 4))
            continue;
        bool occupied = false;
        for (const auto &ally : w.allies)
            occupied |= ally.alive && ally.id != w.self.id &&
                        (w.on_group(gi, ally.pos) || w.matching_claim(ally.id, gi));
        if (occupied)
            continue;
        const int d = distance(w.self.pos, w.groups[gi].camps.front().pos);
        if (d < cost[0]) {
            result[1] = result[0];
            cost[1] = cost[0];
            result[0] = gi;
            cost[0] = d;
        } else if (d < cost[1]) {
            result[1] = gi;
            cost[1] = d;
        }
    }
    return result;
}
inline std::optional<Pos> gem_investment_stage(const World &w, int gi,
                                               const ShoppingState *state = nullptr) {
    if (!assembly_detail::simple_sleeping(w, gi))
        return std::nullopt;
    const auto &camp = w.groups[gi].camps.front();
    if (state)
        for (int k = 0; k < 2; ++k) {
            const Pos chosen = state->gem_route_stage[k];
            if (state->gem_route_group[k] == gi && w.free(chosen) &&
                packed_bit(w.visible_bytes, w.geo.index(chosen)) &&
                distance(chosen, camp.pos) <= w.self.range)
                return chosen; // Keep a still-legal already priced named endpoint.
        }
    const int range = std::min(4, w.self.range);
    int best = unreachable;
    std::optional<Pos> result;
    for (int dy = -range; dy <= range; ++dy)
        for (int dx = -range; dx <= range; ++dx) {
            const Pos p{camp.pos.x + dx, camp.pos.y + dy};
            if (!w.free(p) || !packed_bit(w.visible_bytes, w.geo.index(p)) ||
                distance(p, camp.pos) > w.self.range)
                continue;
            const int d = w.home_distance(p);
            if (d < best) {
                best = d;
                result = p;
            }
        }
    return result;
}
inline std::optional<Pos> cached_gem_contribution_stage(const World &w, int gi,
                                                        ShoppingState &state) {
    if (!assembly_detail::simple_sleeping(w, gi))
        return std::nullopt;
    const auto &camp = w.groups[gi].camps.front();
    for (int k = 0; k < 2; ++k)
        if (state.cached_gem_group[k] == gi && w.free(state.cached_gem_stage[k]) &&
            packed_bit(w.visible_bytes, w.geo.index(state.cached_gem_stage[k])) &&
            distance(state.cached_gem_stage[k], camp.pos) <= w.self.range)
            return state.cached_gem_stage[k];
    auto chosen = gem_investment_stage(w, gi, &state);
    if (chosen) {
        const int slot = state.cached_gem_next++ % 2;
        state.cached_gem_group[slot] = gi;
        state.cached_gem_stage[slot] = *chosen;
    }
    return chosen;
}
inline bool cash_sole_holder(const World &w, int gi) {
    for (const auto &ally : w.allies)
        if (ally.id != w.self.id && ally.alive &&
            (w.on_group(gi, ally.pos) || w.matching_claim(ally.id, gi)))
            return false;
    return true;
}
inline int cash_investment_group(const World &w) {
    int best = -1, length = unreachable;
    for (unsigned gi = 0; gi < w.groups.size(); ++gi) {
        const auto &group = w.geo.groups[gi];
        if (group.gems != 0 || group.gold <= 0 || !assembly_detail::simple_sleeping(w, gi) ||
            !cash_sole_holder(w, gi) || w.warning_near(w.groups[gi].camps.front().pos, 4) ||
            (w.memory.failed_group == static_cast<int>(gi) && w.round < w.memory.failed_until))
            continue;
        const int d = distance(w.self.pos, w.groups[gi].camps.front().pos);
        if (d < length) {
            best = gi;
            length = d;
        }
    }
    return best;
}
inline std::optional<Pos> cash_contribution_stage(const World &w, int gi, ShoppingState &state) {
    if (!assembly_detail::simple_sleeping(w, gi))
        return std::nullopt;
    const auto &camp = w.groups[gi].camps.front();
    if (state.cached_cash_group == gi && w.free(state.cached_cash_stage) &&
        packed_bit(w.visible_bytes, w.geo.index(state.cached_cash_stage)) &&
        distance(state.cached_cash_stage, camp.pos) <= w.self.range)
        return state.cached_cash_stage;
    auto chosen = gem_investment_stage(w, gi, &state);
    if (chosen) {
        state.cached_cash_group = gi;
        state.cached_cash_stage = *chosen;
    }
    return chosen;
}
// Advisory for main's next fresh-budget immutable field preparation. It does
// not authorize the old observation, a clear, or a return on the next owner.
inline std::optional<Pos> shopping_gem_route_hint(const World &w, ShoppingState &state) {
    if (!w.self.alive || state.investment_item >= 0 || w.self.type == 11 || w.self.gems > 0 ||
        !w.enemies.empty())
        return std::nullopt;
    if (state.cash.group >= 0 && state.cash.group < static_cast<int>(w.geo.groups.size())) {
        // The finite prefix consumer certifies arrival using the actual cash
        // camp root, not the separately priced fixed contribution stage.
        const Pos target = state.cash.capture;
        if (!w.geo.goal_cache.contains({w.geo.index(target), 0}) &&
            !w.geo.route_cache.contains(w.geo.index(target)))
            return target;
    }
    if (w.gold < 30) {
        const int cash = cash_investment_group(w);
        if (cash < 0)
            return std::nullopt;
        if (auto stage = cash_contribution_stage(w, cash, state))
            if (!w.geo.goal_cache.contains({w.geo.index(*stage), 0}))
                return stage;
    } else if (w.memory.mission.group < 0 ||
               w.memory.mission.group >= static_cast<int>(w.geo.groups.size()) ||
               w.geo.groups[w.memory.mission.group].gems > 0)
        return std::nullopt;
    for (int gi : gem_investment_groups(w))
        if (gi >= 0)
            if (auto stage = cached_gem_contribution_stage(w, gi, state))
                if (!w.geo.goal_cache.contains({w.geo.index(*stage), 0}))
                    return stage;
    return std::nullopt;
}
inline std::optional<GemReturnLegs> gem_return_legs(const World &w, ShoppingState &state, int gi,
                                                    Pos stage, int floor = 40000) {
    const auto field = w.geo.goal_cache.find({w.geo.index(stage), 0});
    if (field == w.geo.goal_cache.end())
        return std::nullopt;
    GemReturnLegs legs;
    legs.direct_walk = w.geo.at(field->second, w.self.pos);
    int cached = -1;
    for (int k = 0; k < 2; ++k)
        if (state.gem_route_group[k] == gi && state.gem_route_stage[k] == stage)
            cached = k;
    if (cached >= 0) {
        const auto &v = state.gem_route_lengths[cached];
        legs.spawn_walk = v[0];
        legs.capture_walk = v[1];
        legs.bank_walk = v[2];
        legs.home_walk = v[3];
    } else {
        legs.spawn_walk = 0;
        if (state.own_spawn_positions.empty()) {
            const auto native_spawn = w.geo.own_spawn.positions();
            std::vector<Pos> complete;
            complete.reserve(native_spawn.size());
            for (const auto tile : native_spawn)
                complete.push_back(position(tile));
            state.own_spawn_positions = std::move(complete);
            return std::nullopt; // Immutable setup is one bounded advisory opportunity.
        }
        for (const auto tile : state.own_spawn_positions) {
            if (bc::fuel_remaining() < static_cast<unsigned>(floor + 2000))
                return std::nullopt;
            const int d = w.geo.at(field->second, tile);
            if (d == unreachable)
                return std::nullopt; // Every actual possible spawn, not only the nearest one.
            legs.spawn_walk = std::max(legs.spawn_walk, d);
        }
        const Pos capture = w.geo.groups[gi].spawns.front().pos;
        legs.capture_walk = w.geo.at(field->second, capture);
        legs.bank_walk = unreachable;
        for (const auto altar : w.geo.altars)
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    if (bc::fuel_remaining() < static_cast<unsigned>(floor + 2500))
                        return std::nullopt;
                    const Pos at{altar.x + dx, altar.y + dy};
                    const int back = w.home_distance(at);
                    const int forward = w.geo.at(field->second, at);
                    if (back == unreachable || forward == unreachable)
                        continue;
                    // The altar itself is impassable. Price a real legal adjacent
                    // bank tile via capture->certified stage->bank endpoint. This
                    // completed cached walk is an upper bound, never a straight line.
                    const int d = legs.capture_walk + forward;
                    if (d < legs.bank_walk) {
                        legs.bank_walk = d;
                        legs.home_walk = back;
                    }
                }
        if (legs.spawn_walk == unreachable || legs.capture_walk == unreachable ||
            legs.bank_walk == unreachable || legs.home_walk == unreachable)
            return std::nullopt;
        const int slot = state.gem_route_next++ % 2;
        state.gem_route_group[slot] = gi;
        state.gem_route_stage[slot] = stage;
        state.gem_route_lengths[slot] = {legs.spawn_walk, legs.capture_walk, legs.bank_walk,
                                         legs.home_walk};
        return std::nullopt; // Complete immutable quote legs are reused next owner.
    }
    legs.capture_hold = int(bc::constants::capture_time) + 1;
    legs.tribute = tribute_ticks(
        w.geo.groups[gi].gems, bc::constants::submit_gem_duration_multiplier,
        bc::constants::submit_gem_base_duration, bc::constants::submit_gem_minimum_duration);
    return legs;
}

inline void clear_investment(ShoppingState &state) {
    state.investment_item = -1;
    state.investment_count = 0;
    state.investment_gain = state.investment_absence = 0;
    state.investment_gem_unlock = false;
}
inline bool investment_plan_invalid(const ShoppingState &state, const Memory &memory, int round,
                                    int group_count, bool alive, bool opposition, bool warning) {
    const auto &job = state.investment_mission;
    return !alive || state.investment_round < 0 || round - state.investment_round > 40 ||
           (job.latest >= 0 && round >= job.latest) || job.group < 0 || job.group >= group_count ||
           (memory.failed_group == job.group && round < memory.failed_until) || opposition ||
           warning;
}
inline bool plan_gold_gem_return(World &w, Memory &memory, ShoppingState &state,
                                 const ShopInventory &inventory, int floor) {
    struct Candidate {
        int group = -1;
        Mission mission{};
        ShopBundle bundle{};
        GemReturnPayoff payoff{};
        double rate = 0;
    };
    Candidate best;
    double old_rate = 0;
    int quotes = 0;
    for (const auto &view : w.groups)
        for (const auto &camp : view.camps)
            if (camp.awake && camp.hp > 0)
                return false; // This quote does not model a walk through an active camp fight.
    for (int gi : gem_investment_groups(w)) {
        if (gi < 0 || bc::fuel_remaining() < static_cast<unsigned>(floor + 10000))
            continue;
        const auto stage = cached_gem_contribution_stage(w, gi, state);
        if (!stage)
            continue;
        const auto legs = gem_return_legs(w, state, gi, *stage, floor);
        if (!legs || bc::fuel_remaining() < static_cast<unsigned>(floor + 9000))
            continue;
        const auto &camp = w.groups[gi].camps.front();
        int collateral = w.self.type == 10 ? 1 : 0;
        for (const auto &spell : w.self.spells)
            if (spell.kind == 3 && spell.camps)
                collateral = std::max(collateral, spell.radius);
        bool splash = false;
        if (collateral > 0)
            for (unsigned other = 0; other < w.geo.groups.size(); ++other)
                if (other != static_cast<unsigned>(gi))
                    for (const auto &spawn : w.geo.groups[other].spawns)
                        splash |= distance(spawn.pos, camp.pos) <= collateral;
        if (splash)
            continue;
        Mission next;
        next.phase = Phase::Travel;
        next.intent = Intent::Farm;
        next.group = gi;
        next.target = camp.pos;
        next.start = next.last_progress = w.round;
        next.expiry = w.round + Settings::job_lease;
        if (!state.own_growth)
            state.own_growth = w.me.base_stats(); // Immutable actual personal design.
        const auto make_bundle = [&](int raw) {
            ShopBundle bundle;
            bundle.raw = raw;
            const int cost = int(shop_info(raw).cost);
            bundle.count =
                cost > 0 ? std::max(0, std::min(5 - inventory.count[raw], w.gold / cost)) : 0;
            bundle.affordable = bundle.count > 0;
            if (bundle.affordable)
                bundle.delta = upgrade_delta(raw, inventory, *state.own_growth, bundle.count);
            return bundle;
        };
        const ShopFamily defense =
            !inventory.has(ShopFamily::Jungle) ? ShopFamily::Jungle : ShopFamily::Durability;
        ShopBundle defensive;
        if (!inventory.has(defense))
            defensive = make_bundle(shop_raw(defense, ShopStat::Health));
        const ShopFamily offense = !inventory.has(ShopFamily::Jungle)    ? ShopFamily::Jungle
                                   : !inventory.has(ShopFamily::Monster) ? ShopFamily::Monster
                                                                         : ShopFamily::Power;
        const auto role_bundle = make_bundle(shop_raw(offense, shop_role_stat(w.self.type)));
        if (defensive.raw == role_bundle.raw)
            defensive.affordable = false;
        // A reserve unlock first needs a durable affordable kit. The normal
        // role bundle remains the second exact alternative when budget permits.
        for (const auto &bundle : {defensive, role_bundle}) {
            if (quotes >= 2 || !bundle.affordable || bundle.raw < 0 ||
                bc::fuel_remaining() < static_cast<unsigned>(floor + 6500))
                continue;
            ++quotes;
            const auto payoff = completed_gem_return(w.self, bundle.delta, camp, *stage, *legs,
                                                     int(bc::constants::max_rounds) - w.round,
                                                     Settings::switch_margin);
            if (w.round != int(bc::round_number()) ||
                bc::fuel_remaining() < static_cast<unsigned>(floor))
                return false;
            if (!payoff.known)
                continue;
            const int gems = w.geo.groups[gi].gems;
            if (payoff.old_ticks > 0)
                old_rate = std::max(old_rate, gems / payoff.old_ticks);
            const double rate = gems / std::max(1.0, payoff.next_ticks);
            if (payoff.worthwhile && rate > best.rate) {
                next.rate = rate;
                next.latest = int(bc::constants::max_rounds) -
                              int(std::ceil(payoff.next_ticks - payoff.absence));
                best = {gi, next, bundle, payoff, rate};
            }
            if (payoff.worthwhile)
                break; // Spend the other permitted quote on the next named alternative.
        }
    }
    if (best.group < 0 || old_rate >= best.rate)
        return false;
    state.investment_origin = memory.mission;
    state.investment_mission = best.mission;
    state.investment_item = best.bundle.raw;
    state.investment_count = best.bundle.count;
    state.investment_before = inventory.count[best.bundle.raw];
    state.investment_emblem_before = inventory.count[best.bundle.raw + 1];
    state.investment_round = w.round;
    state.investment_gem_unlock = memory.upgrade_gem_unlock = best.payoff.unlock;
    state.investment_gain = memory.upgrade_gain = best.payoff.saved_turns;
    state.investment_absence = memory.upgrade_absence = best.payoff.absence;
    return true;
}
inline bool cash_reward_paid(const CashInvestment &cash, int wallet, int bundle_cost, bool fresh,
                             Lifecycle lifecycle, bool on_capture) {
    return cash.holding && fresh && lifecycle == Lifecycle::Respawning && on_capture &&
           cash.expected_gold > 0 && bundle_cost > 0 &&
           wallet >= cash.gold_before + cash.expected_gold && wallet >= bundle_cost;
}
inline void publish_cash_investment(Memory &memory, const CashInvestment &cash) {
    memory.cash_investment_group = cash.group;
    memory.cash_investment_until = cash.until;
    memory.cash_investment_rate = cash.rate;
}
inline bool plan_cash_gem_investment(World &w, Memory &memory, ShoppingState &state,
                                     const ShopInventory &inventory, int floor) {
    auto &cash = state.cash;
    if (cash.group >= 0) {
        const int gi = cash.group, gem = cash.gem_mission.group;
        const bool indices = gi < static_cast<int>(w.groups.size()) && gem >= 0 &&
                             gem < static_cast<int>(w.groups.size());
        const bool unchanged = cash.item >= 0 && cash.item < 42 && !(cash.item & 1) &&
                               cash.count > 0 && cash.count <= 5 &&
                               inventory.count[cash.item] == cash.before &&
                               inventory.count[cash.item + 1] == cash.emblem_before;
        bool recent_hostile = false;
        for (const auto &sight : w.sightings)
            recent_hostile |=
                sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round);
        if (!indices || !w.self.alive || w.self.gems != 0 || !unchanged || w.round >= cash.until ||
            !w.enemies.empty() || recent_hostile || !cash_sole_holder(w, gi) ||
            !cash_sole_holder(w, gem) || w.warning_near(w.geo.groups[gi].spawns.front().pos, 4) ||
            w.warning_near(cash.gem_mission.target, 4) ||
            (memory.failed_group == gi && w.round < memory.failed_until) ||
            (memory.failed_group == gem && w.round < memory.failed_until)) {
            cash = {};
            return false;
        }
        const auto &view = w.groups[gi];
        const auto &future = w.groups[gem];
        if ((view.state != Lifecycle::Respawning && w.gold != cash.gold_before) ||
            (future.fresh(w.round) && future.state != Lifecycle::Alive)) {
            cash = {};
            return false;
        }
        if (view.fresh(w.round) && view.state == Lifecycle::Reward && w.on_group(gi, w.self.pos))
            cash.holding = true;
        if (view.fresh(w.round) && view.state == Lifecycle::Respawning) {
            const int cost = static_cast<int>(shop_info(cash.item).cost) * cash.count;
            if (!cash_reward_paid(cash, w.gold, cost, true, view.state,
                                  w.on_group(gi, w.self.pos))) {
                cash = {}; // A shared/changed payout never supplies projected money.
                return false;
            }
            state.investment_origin = memory.mission;
            state.investment_mission = cash.gem_mission;
            state.investment_item = cash.item;
            state.investment_count = cash.count;
            state.investment_before = cash.before;
            state.investment_emblem_before = cash.emblem_before;
            state.investment_round = w.round;
            state.investment_gem_unlock = memory.upgrade_gem_unlock = true;
            state.investment_gain = memory.upgrade_gain = 0;
            state.investment_absence = memory.upgrade_absence = cash.absence;
            cash = {};
            return true; // Only the actual wallet now authorizes the existing return.
        }
        if ((view.fresh(w.round) && view.state == Lifecycle::Respawning) ||
            (cash.started && memory.mission.group != gi)) {
            cash = {};
            return false;
        }
        cash.started |= memory.mission.group == gi;
        publish_cash_investment(memory, cash);
        return true;
    }
    if (state.investment_item >= 0 || w.gold >= 30 || w.self.gems != 0 || !w.self.alive ||
        w.self.type == 11 || w.self.channel != Channel::None || bc::fuel_remaining() < 60000 ||
        !w.enemies.empty())
        return false;
    for (const auto &sight : w.sightings)
        if (sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round))
            return false;
    for (const auto &view : w.groups)
        for (const auto &camp : view.camps)
            if (camp.awake && camp.hp > 0)
                return false;
    const int gi = cash_investment_group(w);
    if (gi < 0)
        return false;
    const auto stage = cash_contribution_stage(w, gi, state);
    if (!stage)
        return false;
    const auto field = w.geo.goal_cache.find({w.geo.index(*stage), 0});
    if (field == w.geo.goal_cache.end())
        return false;
    const auto &group = w.geo.groups[gi];
    const auto &camp = w.groups[gi].camps.front();
    const Pos capture = group.spawns.front().pos;
    CashGemLegs acquisition{w.geo.at(field->second, w.self.pos), w.geo.at(field->second, capture),
                            int(bc::constants::capture_time) + 1};
    if (!state.own_growth)
        state.own_growth = w.me.base_stats();
    const ShopFamily defense =
        !inventory.has(ShopFamily::Jungle) ? ShopFamily::Jungle : ShopFamily::Durability;
    const int raw = shop_raw(defense, ShopStat::Health);
    const int cost = int(shop_info(raw).cost);
    const int count =
        cost > 0 ? std::min(5 - inventory.count[raw], (w.gold + group.gold) / cost) : 0;
    if (count <= 0 || inventory.has(defense))
        return false;
    const auto delta = upgrade_delta(raw, inventory, *state.own_growth, count);
    CashInvestment best;
    for (int gem : gem_investment_groups(w)) {
        if (gem < 0 || bc::fuel_remaining() < static_cast<unsigned>(floor + 9000))
            continue;
        const auto gem_stage = cached_gem_contribution_stage(w, gem, state);
        if (!gem_stage)
            continue;
        auto legs = gem_return_legs(w, state, gem, *gem_stage, floor);
        if (!legs || bc::fuel_remaining() < static_cast<unsigned>(floor + 6500))
            continue;
        const auto payoff =
            completed_cash_gem(w.self, camp, *stage, capture, acquisition, w.gold, group.gold,
                               cost * count, delta, w.groups[gem].camps.front(), *gem_stage, *legs,
                               int(bc::constants::max_rounds) - w.round, Settings::switch_margin);
        if (w.round != int(bc::round_number()) ||
            bc::fuel_remaining() < static_cast<unsigned>(floor))
            return false;
        if (!payoff.known || !payoff.worthwhile)
            continue;
        const double rate = w.geo.groups[gem].gems / std::max(1.0, payoff.total_ticks);
        if (rate <= best.rate)
            continue;
        Mission named;
        named.group = gem;
        named.target = w.groups[gem].camps.front().pos;
        named.phase = Phase::Travel;
        named.intent = Intent::Farm;
        named.start = named.last_progress = w.round;
        named.expiry = w.round + Settings::job_lease;
        named.latest = int(bc::constants::max_rounds) -
                       int(std::ceil(payoff.total_ticks - payoff.cash_ticks - payoff.absence));
        named.rate = w.geo.groups[gem].gems / std::max(1.0, payoff.total_ticks - payoff.cash_ticks);
        best.group = gi;
        best.item = raw;
        best.count = count;
        best.before = inventory.count[raw];
        best.emblem_before = inventory.count[raw + 1];
        best.gold_before = w.gold;
        best.expected_gold = group.gold; // Conservative base reward, no bonus invented.
        best.created = w.round;
        best.until = std::min(named.latest, w.round + int(std::ceil(payoff.cash_ticks)) +
                                                2 * Settings::job_lease);
        best.stage = *stage;
        best.capture = capture;
        best.gem_mission = named;
        best.rate = rate;
        best.absence = payoff.absence;
    }
    if (best.group < 0)
        return false;
    cash = best;
    publish_cash_investment(memory, cash);
    return true;
}
inline void plan_upgrade_return(World &w, Memory &memory, ShoppingState &state) {
    const int planning_floor = std::max(40000, int(bc::fuel_remaining()) - 16000);
    memory.upgrade_gain = memory.upgrade_absence = 0;
    memory.upgrade_gem_unlock = false;
    memory.cash_investment_group = -1;
    memory.cash_investment_until = -1;
    memory.cash_investment_rate = 0;
    if ((!w.self.alive || w.self.gems > 0 || !w.enemies.empty()) && state.cash.group >= 0)
        state.cash = {};
    if (w.self.alive && w.self.type != 11 && w.self.channel == Channel::None &&
        bc::fuel_remaining() >= (state.cash.group >= 0 ? 45000u : 60000u)) {
        const auto inventory = shop_inventory(w.me.item_count());
        if (plan_cash_gem_investment(w, memory, state, inventory, planning_floor))
            return;
    }
    if (state.investment_item >= 0) {
        if (investment_plan_invalid(state, memory, w.round, w.geo.groups.size(), w.self.alive,
                                    !w.enemies.empty(),
                                    w.warning_near(state.investment_mission.target, 4))) {
            clear_investment(state);
            return;
        }
        if (w.in_spawn(w.self.pos))
            return; // Actual named bundle is installed by shopping_proposal first.
        if (memory.mission.phase == Phase::Recover || memory.mission.phase == Phase::Channel ||
            memory.prior_channel == Channel::Recall) {
            memory.upgrade_gem_unlock = state.investment_gem_unlock;
            memory.upgrade_gain = state.investment_gain;
            memory.upgrade_absence = state.investment_absence;
            return;
        }
        clear_investment(state); // An unrelated mission needs a fresh plan.
    }
    const auto &mission = memory.mission;
    if (!w.self.alive || w.self.type == 11 || w.in_spawn(w.self.pos) || w.gold < 30 ||
        w.self.channel != Channel::None || mission.group < 0 ||
        mission.group >= static_cast<int>(w.geo.groups.size()) || cambc::fuel_remaining() < 60000 ||
        !w.enemies.empty() || mission.bank_after_reward || mission.chain_used ||
        w.own_score + w.self.gems >= static_cast<int>(cambc::constants::winning_gems))
        return;
    if (w.warning_near(mission.target, 4))
        return;
    const int home = w.home_distance(mission.target);
    const int altar = w.altar_distance(mission.target);
    if (home == unreachable || altar == unreachable ||
        w.me.restrictions().contains(cambc::buff_restrictions::shop))
        return;
    const auto inventory = shop_inventory(w.me.item_count());
    if (w.geo.groups[mission.group].gems == 0) {
        for (const auto &sight : w.sightings)
            if (sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round))
                return;
        plan_gold_gem_return(w, memory, state, inventory, planning_floor);
        return;
    }
    forecast_investment(w, mission, state);
    const auto bundle = select_shop_bundle(w, mission, inventory, state);
    if (!bundle.affordable || bundle.raw < 0)
        return;
    const int remaining = std::max(0, static_cast<int>(cambc::constants::max_rounds) - w.round);
    const auto payoff = named_return_payoff(
        w.self, w.geo.groups[mission.group], bundle.delta, remaining, home,
        w.self.home ? 3 : cambc::constants::recall_time, Settings::switch_margin, altar,
        tribute_ticks(w.self.gems + w.geo.groups[mission.group].gems,
                      cambc::constants::submit_gem_duration_multiplier,
                      cambc::constants::submit_gem_base_duration,
                      cambc::constants::submit_gem_minimum_duration));
    if (!payoff.worthwhile)
        return;
    state.investment_item = bundle.raw;
    state.investment_count = bundle.count;
    state.investment_before = inventory.count[bundle.raw];
    state.investment_emblem_before = inventory.count[bundle.raw + 1];
    state.investment_round = w.round;
    state.investment_mission = state.investment_origin = mission;
    state.investment_gem_unlock = false;
    state.investment_gain = memory.upgrade_gain = payoff.saved_turns;
    state.investment_absence = memory.upgrade_absence = payoff.absence;
}

inline std::optional<Action> shopping_proposal(World &w, const Mission &mission,
                                               ShoppingState &state) {
    if (state.last_round != w.round) {
        state.last_round = w.round;
        state.heals_this_round = 0;
    }
    if (state.failed_round == w.round || cambc::fuel_remaining() < Settings::fuel_reserve + 4000 ||
        w.self.channel != Channel::None ||
        (w.self.alive && w.me.restrictions().contains(cambc::buff_restrictions::shop)))
        return std::nullopt;
    if (state.pending_heal < 0 && state.reserve_consumable < 0 &&
        (w.gold < 30 || (w.self.alive && !w.in_spawn(w.self.pos) && w.self.type != 11)))
        return std::nullopt;
    const auto inventory = shop_inventory(w.me.item_count());
    forecast_investment(w, mission, state);

    if (state.pending_heal >= 0) {
        const int raw = state.pending_heal;
        if (!w.self.alive || !w.in_spawn(w.self.pos) || !w.me.can_sell() ||
            inventory.count[raw] != state.heal_count + 1 || w.gold != state.heal_gold - 30) {
            state.pending_heal = -1; // A changed transaction is never sold blindly.
            state.failed_round = w.round;
            return std::nullopt;
        }
        Action result;
        result.kind = Kind::Sell;
        result.item = raw;
        result.reason = "tavi-restore-heal-transaction";
        return result;
    }

    if (state.investment_item >= 0 && w.self.alive && w.in_spawn(w.self.pos)) {
        const int raw = state.investment_item, count = state.investment_count;
        if (raw < 0 || raw >= 42 || (raw & 1) || count <= 0) {
            clear_investment(state);
            w.memory.upgrade_gain = w.memory.upgrade_absence = 0;
            w.memory.upgrade_gem_unlock = false;
            return std::nullopt;
        }
        const auto item = shop_item(raw);
        const bool unchanged = raw >= 0 && raw < 42 && !(raw & 1) && count > 0 &&
                               inventory.count[raw] == state.investment_before &&
                               inventory.count[raw + 1] == state.investment_emblem_before;
        if (!unchanged || w.gold < static_cast<int>(item.cost()) * count ||
            !w.me.can_buy(item, count)) {
            clear_investment(state);
            w.memory.upgrade_gain = w.memory.upgrade_absence = 0;
            w.memory.upgrade_gem_unlock = false;
            // No blind substitution: get ordinary spawn recovery/new arbitration.
            return std::nullopt;
        }
        state.investment_buy_gold = w.gold;
        Action result;
        result.kind = Kind::Buy;
        result.item = raw;
        result.count = count;
        result.reason = "install-priced-return-bundle";
        return result;
    }

    bool pressure = false;
    for (const auto &enemy : w.enemies)
        if (enemy.alive && distance(w.self.pos, enemy.pos) <= 8)
            pressure = true;
    bool damaging = false;
    if (shop_farm_phase(mission))
        for (const auto &group : w.geo.groups)
            if (group.index == mission.group && group.initial_strength > 0 && w.self.range <= 2)
                damaging = true;

    int reserve = 0;
    // The central mission planner may request a consumable for a named legal
    // use. Existing stock removes the reserve; Tavi field equipment permission
    // alone never opens the consumable shop.
    if (state.reserve_consumable >= 0 && state.reserve_consumable < 2) {
        const auto kind =
            cambc::consumable_type{static_cast<std::uint32_t>(state.reserve_consumable)};
        if (w.me.consumables()[kind].count() == 0 && w.me.can_buy(kind)) {
            reserve = static_cast<int>(kind.cost());
            Action result;
            result.kind = Kind::BuyConsumable;
            result.item = state.reserve_consumable;
            result.reason = state.reserve_reason;
            return result;
        }
    }

    // Optional same-turn Tavi spawn recovery is a checked two-action
    // transaction. It is useful only if a planned departure can happen now;
    // ordinary recovery can simply take the spawn's end-of-turn full heal.
    if (w.self.type == 11 && w.self.alive && w.in_spawn(w.self.pos) && w.self.can_move &&
        mission.phase != Phase::Recover && w.me.can_sell() && state.heals_this_round < 3 &&
        w.self.hp + 1 < w.self.max_hp && w.gold - reserve >= 30) {
        for (int family = 0; family < 7; ++family) {
            const int raw = shop_raw(static_cast<ShopFamily>(family), ShopStat::Health);
            if (inventory.count[raw] > 3 || !w.me.can_buy(shop_item(raw)))
                continue;
            state.planned_heal = raw;
            state.heal_count = inventory.count[raw];
            state.heal_gold = w.gold;
            Action result;
            result.kind = Kind::Buy;
            result.item = raw;
            result.reason = "tavi-bounded-spawn-heal";
            return result;
        }
    }
    state.planned_heal = -1;
    const auto bundle = select_shop_bundle(w, mission, inventory, state, reserve);
    if (!bundle.affordable || bundle.raw < 0 || !w.me.can_buy(shop_item(bundle.raw), bundle.count))
        return std::nullopt;
    const int raw = bundle.raw;
    state.goal = raw;
    state.goal_group = mission.group;
    state.goal_phase = mission.phase;
    Action result;
    result.kind = Kind::Buy;
    result.item = raw;
    result.count = bundle.count;
    result.reason = inventory.count[raw] == 4 ? "complete-useful-item-before-mission"
                                              : "useful-private-budget-component";
    return result;
}

inline void shopping_after_action(World &post, const Action &action, bool success,
                                  ShoppingState &state) {
    if (action.kind != Kind::Buy && action.kind != Kind::Sell && action.kind != Kind::BuyConsumable)
        return;
    if (!success) {
        state.failed_round = post.round;
        state.pending_heal = -1;
        if (std::string_view(action.reason) == "install-priced-return-bundle") {
            const Mission fallback = state.investment_origin;
            if (fallback.group >= 0 && fallback.group < static_cast<int>(post.geo.groups.size())) {
                post.memory.mission = fallback;
                post.memory.mission.phase = Phase::Reenter;
                post.memory.mission.start = post.round;
                post.memory.mission.expiry = post.round + Settings::job_lease;
            }
            clear_investment(state);
            post.memory.upgrade_gain = post.memory.upgrade_absence = 0;
            post.memory.upgrade_gem_unlock = false;
        }
        return;
    }
    if (std::string_view(action.reason) == "install-priced-return-bundle") {
        const auto inventory = shop_inventory(post.me.item_count());
        const int raw = state.investment_item, count = state.investment_count;
        const bool completes = state.investment_before + count == 5;
        const bool correct =
            raw >= 0 && raw < 42 && action.item == raw && action.count == count &&
            inventory.count[raw] == (completes ? 0 : state.investment_before + count) &&
            inventory.count[raw + 1] == state.investment_emblem_before + (completes ? 1 : 0) &&
            post.gold == state.investment_buy_gold - static_cast<int>(shop_info(raw).cost) * count;
        const Mission original = state.investment_mission, fallback = state.investment_origin;
        clear_investment(state);
        post.memory.upgrade_gain = post.memory.upgrade_absence = 0;
        post.memory.upgrade_gem_unlock = false;
        if (!correct) {
            state.failed_round = post.round;
            if (fallback.group >= 0 && fallback.group < static_cast<int>(post.geo.groups.size())) {
                post.memory.mission = fallback;
                post.memory.mission.phase = Phase::Reenter;
                post.memory.mission.start = post.round;
                post.memory.mission.expiry = post.round + Settings::job_lease;
            }
            return; // A partial/changed result never certifies the predicted power.
        }
        if (original.group >= 0 && original.group < static_cast<int>(post.geo.groups.size()) &&
            !(post.memory.failed_group == original.group &&
              post.round < post.memory.failed_until)) {
            post.memory.mission = original;
            post.memory.mission.phase = Phase::Reenter;
            post.memory.mission.start = post.round;
            post.memory.mission.expiry = post.round + Settings::job_lease;
            post.memory.mission.sortie_floor = 0;
        }
        return;
    }
    if (std::string_view(action.reason) == "tavi-bounded-spawn-heal") {
        const auto inv = shop_inventory(post.me.item_count());
        if (action.item == state.planned_heal && inv.count[action.item] == state.heal_count + 1 &&
            post.gold == state.heal_gold - 30)
            state.pending_heal = action.item;
        else {
            state.pending_heal = -1;
            state.failed_round = post.round;
        }
    } else if (std::string_view(action.reason) == "tavi-restore-heal-transaction") {
        const auto inv = shop_inventory(post.me.item_count());
        if (action.item != state.pending_heal || inv.count[action.item] != state.heal_count ||
            post.gold != state.heal_gold)
            state.failed_round = post.round;
        state.pending_heal = -1;
        ++state.heals_this_round;
    }
}

} // namespace tactics

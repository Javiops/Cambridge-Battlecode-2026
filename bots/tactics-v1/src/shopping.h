#pragma once

#include "sdk_world.h"
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

struct ShoppingState {
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
};

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
    const auto inventory = shop_inventory(w.me.item_count());

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
    const int remaining = std::max(0, static_cast<int>(cambc::constants::max_rounds) - w.round);
    const int raw =
        shop_choose_shard(inventory, w.self.type, mission, damaging, pressure, state, remaining);
    const auto item = shop_item(raw);
    if (w.gold - reserve < static_cast<int>(item.cost()) || !w.me.can_buy(item))
        return std::nullopt;
    state.goal = raw;
    state.goal_group = mission.group;
    state.goal_phase = mission.phase;
    Action result;
    result.kind = Kind::Buy;
    result.item = raw;
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

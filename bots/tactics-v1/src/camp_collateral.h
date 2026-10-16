#pragma once
#include "camp_actions.h"
#include <span>
namespace tactics {
// Optimistic enemy contact envelope across the entire proposed fixed clear.
// Repeated dashes are possible when their observed recharge fits the horizon;
// unknown recharge is conservatively one possible dash per world round.
inline int camp_enemy_contact(const Actor &enemy, int horizon) {
    horizon = std::max(0, horizon);
    int attack = enemy.range, dash = 0;
    for (const auto &spell : enemy.spells) {
        const int first = spell.ready || spell.cooldown < 0 ? 0 : spell.cooldown;
        if (first > horizon)
            continue;
        if (spell.kind == 6) {
            const int uses = 1 + (horizon - first) / std::max(1, spell.recharge);
            dash += uses * spell.range;
        } else if (spell.kind == 2 || spell.kind == 3 || spell.kind == 4)
            attack = std::max(attack, spell.range + spell.radius);
    }
    return attack + dash + horizon * std::max(1, enemy.move_speed);
}
// A selected-area clear cannot price a different sleeping group's response.
// Public original spawns remain possible future occupants even when presently
// empty; only an enlarged explicit forecast could safely remove this veto.
inline bool external_camp_collateral(const Actor &actor, std::span<const Camp> selected,
                                     std::span<const Group> groups, int own_group,
                                     std::span<const GroupView> views = {}, int round = -1) {
    int radius = actor.type == 10 ? 1 : 0;
    for (const auto &spell : actor.spells)
        if (spell.kind == 3 && camp_damage_ability(spell))
            radius = std::max(radius, spell.radius);
    if (radius <= 0)
        return false;
    for (unsigned gi = 0; gi < groups.size(); ++gi) {
        if (int(gi) == own_group)
            continue;
        for (const auto &spawn : groups[gi].spawns)
            for (const auto &primary : selected)
                if (primary.hp > 0 && distance(primary.pos, spawn.pos) <= radius)
                    return true;
        if (gi < views.size() && views[gi].fresh(round))
            for (const auto &camp : views[gi].camps)
                for (const auto &primary : selected)
                    if (camp.hp > 0 && primary.hp > 0 && distance(primary.pos, camp.pos) <= radius)
                        return true;
    }
    return false;
}
} // namespace tactics

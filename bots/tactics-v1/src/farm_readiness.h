#pragma once
#include "squads.h"
#include "types.h"
#include <span>

namespace tactics {
// A present contribution starts with a legal useful action at this body's
// actual position. A claim, future arrival or nominal Strength is insufficient.
inline Contributor current_camp_contribution(const Actor &actor, std::span<const Camp> camps,
                                             bool exclusive_allowed = true) {
    Contributor out{actor.id, 0, 1, false};
    if (!actor.alive || actor.completed || actor.stunned || actor.channel != Channel::None)
        return out;
    bool basic_range = false;
    double recurring_cast = 0;
    for (const auto &camp : camps) {
        if (camp.hp <= 0)
            continue;
        const bool in_basic = distance(actor.pos, camp.pos) <= actor.range;
        basic_range |= in_basic;
        out.ready |= actor.can_attack && in_basic && actor.strength > 0;
        for (const auto &spell : actor.spells) {
            if (spell.exclusive && !exclusive_allowed)
                continue;
            const bool reset = spell.kind == 1 && spell.self && in_basic && actor.strength > 0;
            // Ground areas use an actual camp position as their legal center.
            // Their radius never extends the cast center's permitted range.
            const bool damage =
                spell.amount > 0 &&
                ((spell.camps && (spell.kind == 2 || spell.kind == 3 || spell.kind == 4)) ||
                 (spell.kind == 3 && spell.ground)) &&
                distance(actor.pos, camp.pos) <= spell.range;
            out.ready |= actor.can_cast && spell.ready && (damage || (reset && !actor.can_attack));
            if (spell.recharge > 0)
                recurring_cast = std::max(recurring_cast, (reset    ? actor.strength
                                                           : damage ? spell.amount
                                                                    : 0) /
                                                              spell.recharge);
        }
    }
    if (out.ready)
        out.dps =
            ((basic_range ? actor.strength : 0) + recurring_cast) * (actor.monster ? 1.1 : 1.0);
    return out;
}

// Unnamed observation/assembly is reversible work. Unlike a certified solo or
// pair route, it has no permission to enter any monster's potential reply zone.
inline bool potential_camp_pressure(Pos at, std::span<const Group> groups,
                                    std::span<const GroupView> views, int round) {
    for (unsigned gi = 0; gi < groups.size(); ++gi) {
        const auto &group = groups[gi];
        const GroupView *view = gi < views.size() ? &views[gi] : nullptr;
        const bool fresh = view && view->fresh(round);
        if (fresh && (view->state == Lifecycle::Reward || view->state == Lifecycle::Respawning))
            continue;
        for (const auto &spawn : group.spawns) {
            if (fresh && std::find(view->known_dead.begin(), view->known_dead.end(), spawn.id) !=
                             view->known_dead.end())
                continue;
            const Camp *observed = nullptr;
            if (fresh)
                for (const auto &camp : view->camps)
                    if (camp.id == spawn.id) {
                        observed = &camp;
                        break;
                    }
            const double hp = observed ? observed->hp : spawn.hp;
            const double strength = observed ? observed->strength : spawn.strength;
            const Pos position = observed ? observed->pos : spawn.pos;
            const int range = observed ? observed->range : spawn.range;
            if (hp > 0 && strength > 0 && distance(at, position) <= range)
                return true;
        }
    }
    return false;
}
} // namespace tactics

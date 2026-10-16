#pragma once
#include "types.h"
#include <span>

namespace tactics {
// The stationary camp executor and its forecast share this action order. The
// selector never grants a future permission; callers supply actual allowances
// or an explicitly projected future owner opportunity.
inline const Camp *camp_action_target(std::span<const Camp> camps, int id) {
    for (const auto &camp : camps)
        if (camp.id == id)
            return &camp;
    return nullptr;
}
inline bool camp_damage_ability(const Spell &spell) {
    return spell.amount > 0 &&
           ((spell.camps && (spell.kind == 2 || spell.kind == 3 || spell.kind == 4)) ||
            (spell.kind == 3 && spell.ground));
}
inline double camp_action_damage(const Actor &actor, const Action &action,
                                 std::span<const Camp> camps, const Camp &victim) {
    if (victim.hp <= 0)
        return 0;
    double raw = 0;
    if (action.kind == Kind::BasicCamp) {
        const auto *primary = camp_action_target(camps, action.target);
        if (primary && (victim.id == primary->id ||
                        (actor.type == 10 && distance(primary->pos, victim.pos) <= 1)))
            raw = actor.strength; // Varg's primary is never splashed twice.
    } else if ((action.kind == Kind::CastCamp || action.kind == Kind::CastGround) &&
               action.slot >= 0 && action.slot < 2) {
        const auto &spell = actor.spells[action.slot];
        const auto *primary = camp_action_target(camps, action.target);
        const Pos center =
            action.kind == Kind::CastGround ? action.at : (primary ? primary->pos : Pos{});
        if (spell.kind == 3 && center.x >= 0 && distance(center, victim.pos) <= spell.radius)
            raw = spell.amount;
        else if (spell.kind != 3 && primary && victim.id == primary->id)
            raw = spell.amount;
    }
    return std::max(0.0, raw) * (actor.monster ? 1.1 : 1.0);
}
inline int camp_action_control(const Actor &actor, const Action &action,
                               std::span<const Camp> camps, const Camp &victim) {
    if (camp_action_damage(actor, action, camps, victim) <= 0)
        return 0;
    if (action.kind == Kind::BasicCamp)
        return actor.type == 7 && actor.enhanced && victim.id == action.target ? 1 : 0;
    if (action.slot < 0 || action.slot > 1)
        return 0;
    const auto &spell = actor.spells[action.slot];
    return spell.kind == 4 || (actor.type == 0 && spell.kind == 3) ? std::max(0, spell.duration)
                                                                   : 0;
}
struct CampActionBudget {
    bool operator()() const {
        return true;
    }
};
template <class Budget = CampActionBudget>
inline Action stationary_camp_support(const Actor &actor, std::span<const Actor> crew,
                                      std::span<const Camp> camps, bool exclusive_allowed = true,
                                      Budget funded = {}) {
    Action action;
    if (!actor.alive || actor.completed || actor.stunned || !actor.can_cast ||
        actor.channel != Channel::None)
        return action;
    double best = 0;
    for (int slot = 0; slot < 2; ++slot) {
        if (!funded())
            return {};
        const auto &spell = actor.spells[slot];
        if (!spell.ready || spell.amount <= 0 || (spell.kind != 5 && spell.kind != 7) ||
            (spell.kind == 7 && spell.duration <= 0) || (spell.exclusive && !exclusive_allowed))
            continue;
        for (const auto &body : crew) {
            if (!funded())
                return {};
            if (!body.alive || body.hp <= 0 ||
                (body.id == actor.id ? !spell.self : !spell.allies) ||
                distance(actor.pos, body.pos) > spell.range)
                continue;
            double worst_reply = 0;
            for (const auto &camp : camps) {
                if (!funded())
                    return {};
                if (camp.hp > 0)
                    worst_reply += camp.strength * body.camp_mitigation;
            }
            if (body.hp + body.shield > worst_reply + .25 * body.max_hp + 1)
                continue;
            double reply = 0;
            for (const auto &camp : camps) {
                if (!funded())
                    return {};
                if (camp.hp <= 0 || camp.strength <= 0)
                    continue;
                int nearest = unreachable;
                for (const auto &other : crew)
                    if (other.alive && other.hp > 0)
                        nearest = std::min(nearest, distance(other.pos, camp.pos));
                if (nearest <= camp.range && distance(body.pos, camp.pos) == nearest)
                    reply += camp.strength * body.camp_mitigation;
            }
            if (body.hp + body.shield > reply + .25 * body.max_hp + 1)
                continue;
            const double benefit =
                spell.kind == 5 ? std::min(spell.amount, std::max(0.0, body.max_hp - body.hp))
                                : std::max(0.0, spell.amount - body.shield);
            if (benefit > best) {
                best = benefit;
                action.kind = body.id == actor.id ? Kind::CastSelf : Kind::CastChampion;
                action.slot = slot;
                action.target = body.id;
                action.reason = "crew-paid-necessary-support";
            }
        }
    }
    return action;
}
template <class Budget = CampActionBudget>
inline Action stationary_camp_action(const Actor &actor, std::span<const Camp> camps,
                                     bool exclusive_allowed = true, Budget funded = {}) {
    Action action;
    if (!actor.alive || actor.completed || actor.stunned || actor.channel != Channel::None)
        return action;
    const Camp *basic = nullptr;
    double best_pressure_cost = 1e30;
    for (const auto &camp : camps) {
        if (!funded())
            return {};
        if (camp.hp <= 0 || distance(actor.pos, camp.pos) > actor.range)
            continue;
        const double cost = camp.hp / std::max(1.0, camp.strength);
        if (!basic || cost < best_pressure_cost ||
            (cost == best_pressure_cost && camp.id < basic->id)) {
            basic = &camp;
            best_pressure_cost = cost;
        }
    }
    if (actor.can_attack && basic) {
        action.kind = Kind::BasicCamp;
        action.target = basic->id;
        action.reason = "crew-paid-pressure-removing-basic";
        return action;
    }
    if (!actor.can_cast)
        return action;
    double best_damage = 0;
    for (int slot = 0; slot < 2; ++slot) {
        if (!funded())
            return {};
        const auto &spell = actor.spells[slot];
        if (!spell.ready || !camp_damage_ability(spell) || (spell.exclusive && !exclusive_allowed))
            continue;
        for (const auto &camp : camps) {
            if (!funded())
                return {};
            // A radius affects victims around a legal center, never cast reach.
            if (camp.hp <= 0 || distance(actor.pos, camp.pos) > spell.range)
                continue;
            Action candidate;
            candidate.kind = spell.ground && spell.kind == 3 ? Kind::CastGround : Kind::CastCamp;
            candidate.target = camp.id;
            candidate.at = camp.pos;
            candidate.slot = slot;
            candidate.reason = "crew-paid-useful-camp-cast";
            double damage = 0;
            for (const auto &victim : camps) {
                if (!funded())
                    return {};
                damage += std::min(victim.hp, camp_action_damage(actor, candidate, camps, victim));
            }
            if (damage > best_damage) {
                best_damage = damage;
                action = candidate;
            }
        }
    }
    if (best_damage > 0)
        return action;
    if (!actor.can_attack && basic)
        for (int slot = 0; slot < 2; ++slot) {
            const auto &spell = actor.spells[slot];
            if (spell.ready && spell.kind == 1 && spell.self &&
                (!spell.exclusive || exclusive_allowed)) {
                action.kind = Kind::CastSelf;
                action.slot = slot;
                action.target = basic->id;
                action.reason = "crew-paid-reset-with-basic";
                return action;
            }
        }
    return action;
}
// The cheap sufficient certificate promises ordinary basics only. Optional
// support or a ready reset must neither replace nor delay that guaranteed hit.
// Detailed forecasts keep their shared support-before-offense sequence.
inline Action certified_camp_first_action(const Actor &actor, std::span<const Actor> crew,
                                          std::span<const Camp> camps, ClearProofKind proof,
                                          bool exclusive_allowed = true) {
    if (proof == ClearProofKind::BasicOnly) {
        if (!actor.can_attack)
            return {};
        auto action = stationary_camp_action(actor, camps, exclusive_allowed);
        return action.kind == Kind::BasicCamp ? action : Action{};
    }
    if (proof != ClearProofKind::DetailedBundle)
        return {};
    auto action = stationary_camp_support(actor, crew, camps, exclusive_allowed);
    return action.kind != Kind::None ? action
                                     : stationary_camp_action(actor, camps, exclusive_allowed);
}
} // namespace tactics

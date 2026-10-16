#pragma once
#ifdef TACTICS_STRATEGIC_MODEL_ONLY
#include "types.h"
#else
#include "sdk_world.h"
#endif
namespace tactics {
struct RouteContext {
    bool exit_known = false, walkout = false, cutoff_known = false;
    int escape_steps = unreachable, enemy_arrival = unreachable;
    int exit_length = 0;
    Pos reversible_step{};
    double reinforcement_cost = 0;
    Intent intent = Intent::Farm;
};
struct ExitGradient {
    std::array<Pos, 6> path{};
    int length = 0, owner_eta = unreachable, earliest_contact = unreachable;
    bool known = false, viable = false;
};
inline int owner_movement_eta(int tiles, int speed, bool movement_ready) {
    speed = std::max(1, speed);
    return std::max(0, (tiles + speed - 1) / speed - (movement_ready ? 1 : 0));
}
inline int enemy_contact_eta(const Actor &enemy, Pos at, int age = 0, int horizon = 8) {
    if (!enemy.alive)
        return unreachable;
    const int speed = std::max(1, enemy.move_speed);
    const int reach = possible_contact_reach(enemy, horizon + std::max(0, age));
    const int remaining = distance(enemy.pos, at) - reach - std::max(0, age) * speed;
    return std::max(0, (remaining + speed - 1) / speed);
}
template <class HomeDistance, class Available, class Observed, class Contact>
inline ExitGradient trace_exit_gradient(Pos origin, int speed, bool movement_ready,
                                        HomeDistance home, Available available, Observed observed,
                                        Contact contact) {
    ExitGradient result;
    int remaining = home(origin);
    if (remaining == unreachable)
        return result;
    if (remaining == 0) {
        result.known = result.viable = true;
        result.owner_eta = 0;
        return result;
    }
    Pos current = origin;
    bool viable = true;
    for (int step = 0; step < 6; ++step) {
        Pos next{};
        int best = remaining;
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                Pos candidate{current.x + dx, current.y + dy};
                if ((!dx && !dy) || !available(candidate) || !observed(candidate))
                    continue;
                const int distance = home(candidate);
                if (distance < best ||
                    (distance == best && next.x >= 0 &&
                     (candidate.y < next.y || (candidate.y == next.y && candidate.x < next.x)))) {
                    best = distance;
                    next = candidate;
                }
            }
        if (next.x < 0)
            return result; // A missing/occluded continuation is not a safe exit.
        result.path[result.length++] = next;
        result.owner_eta = owner_movement_eta(result.length, speed, movement_ready);
        const int enemy_eta = contact(next);
        result.earliest_contact = std::min(result.earliest_contact, enemy_eta);
        viable &= enemy_eta > result.owner_eta;
        current = next;
        remaining = best;
        if (remaining == 0)
            break;
    }
    result.known = true; // Exactly this observed <=6-tile prefix, not all the way home.
    result.viable = viable;
    return result;
}
#ifndef TACTICS_STRATEGIC_MODEL_ONLY
inline int observed_contact_eta(const World &w, Pos at, int horizon = 8, bool reports = true) {
    int result = unreachable;
    for (const auto &enemy : w.enemies)
        result = std::min(result, enemy_contact_eta(enemy, at, 0, horizon));
    for (const auto &sight : w.sightings) {
        const int age = w.round - sight.round;
        if (age < 1 || age > 3 || !sight.actor.alive)
            continue;
        bool visible = false;
        for (const auto &enemy : w.enemies)
            visible |= enemy.id == sight.actor.id;
        if (!visible)
            result = std::min(result, enemy_contact_eta(sight.actor, at, age, horizon));
    }
    // A report has neither precise kit nor accepted response timing. It can
    // invalidate a claimed exit, never supply a target or a guarantee of safety.
    if (reports && w.warning_near(at, 3))
        result = 0;
    return result;
}
inline ExitGradient known_exit_prefix(const World &w, Pos origin, bool movement_ready) {
    if (origin != w.self.pos && !w.free(origin))
        return {};
    const bool warned = w.warning_near(origin, 6);
    return trace_exit_gradient(
        origin, w.self.move_speed, movement_ready, [&](Pos p) { return w.home_distance(p); },
        [&](Pos p) { return w.geo.valid(p) && w.free(p); },
        [&](Pos p) { return w.geo.valid(p) && packed_bit(w.visible_bytes, w.geo.index(p)); },
        [&](Pos p) { return warned ? 0 : observed_contact_eta(w, p, 8, false); });
}
inline RouteContext route_context(const World &w, Pos objective, int group = -1) {
    RouteContext out;
    const int own = w.home_distance(objective);
    const int enemy = w.geo.at(w.geo.enemy_home, objective);
    // Quiet farms do not need an interception trace. Missing sight remains
    // unknown, but alone is not evidence of a contest or a blanket farm veto.
    out.enemy_arrival = observed_contact_eta(w, objective, 8, false);
    bool credible = false;
    for (const auto &actor : w.enemies)
        credible |= actor.alive;
    for (const auto &sight : w.sightings)
        credible |= sight.actor.alive && w.round - sight.round >= 1 && w.round - sight.round <= 3;
    const bool warned = w.warning_near(objective, 3) || w.warning_near(w.self.pos, 6);
    credible |= warned;
    if (warned)
        out.enemy_arrival = 0; // An imprecise report cannot certify reaction slack.
    out.cutoff_known = credible;
    if (credible && bc::fuel_remaining() >= 30000) {
        const auto exit = known_exit_prefix(w, w.self.pos, w.self.can_move);
        out.escape_steps = exit.owner_eta;
        out.exit_length = exit.length;
        out.exit_known = exit.known;
        out.walkout = exit.known && exit.viable;
        if (exit.length > 0)
            out.reversible_step = exit.path.front();
    }
    int friendly = 0, hostile = 0;
    for (const auto &ally : w.allies)
        friendly +=
            ally.alive && ally.channel == Channel::None && distance(ally.pos, objective) <= 6;
    for (const auto &actor : w.enemies) {
        hostile += distance(actor.pos, objective) <= 6;
        if (group >= 0 && w.on_group(group, actor.pos))
            out.intent = Intent::Contest;
    }
    if (own != unreachable && enemy != unreachable && enemy < own) {
        out.reinforcement_cost =
            std::min(8.0, (own - enemy) / double(std::max(1, w.self.move_speed)));
        if (out.intent != Intent::Contest)
            out.intent = Intent::Invade;
        if (friendly > hostile + 1)
            out.reinforcement_cost *= .5;
    }
    if (w.warning_near(objective, 3))
        out.reinforcement_cost += 3;
    if (group >= 0 && w.groups[group].fresh(w.round) &&
        w.groups[group].state == Lifecycle::Reward && hostile > 0 && friendly > hostile)
        out.intent = Intent::Deny;
    return out;
}
#endif
} // namespace tactics

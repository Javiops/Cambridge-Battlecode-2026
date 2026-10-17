#pragma once
#include "types.h"

namespace tactics {
// A complete adjacent observation move, not an economic quote or a claim about
// any unvisited route. The already completed static field must strictly fall.
// All candidate cells are inspected before returning a winner; interrupted
// inspection stays Unknown rather than publishing a partial best.
struct ObservationDetour {
    bool known = false, feasible = false;
    Pos at{};
    int before = -1, after = -1, inspected = 0;
};
template <class Valid, class Distance, class Legal, class Pressure, class Funded>
inline ObservationDetour observation_detour_step(const Actor &actual, Valid valid, Distance field,
                                                 Legal legal, Pressure pressure, Funded funded,
                                                 int max_nodes = 9) {
    ObservationDetour out;
    if (!funded() || !actual.alive || actual.completed || actual.stunned ||
        actual.channel != Channel::None || !actual.can_move || actual.move_speed < 1 ||
        !valid(actual.pos) || max_nodes < 1 || max_nodes > 9)
        return out;
    const int before = field(actual.pos);
    if (before < 0 || before == unreachable)
        return out;
    out.before = before;
    out.inspected = 1;
    for (int dy = -1; dy <= 1; ++dy)
        for (int dx = -1; dx <= 1; ++dx) {
            if (!dx && !dy)
                continue;
            if (!funded() || out.inspected == max_nodes) {
                out.known = out.feasible = false;
                return out;
            }
            ++out.inspected;
            const Pos next{actual.pos.x + dx, actual.pos.y + dy};
            if (!valid(next) || !legal(next))
                continue;
            const int distance = field(next);
            if (distance < 0 || distance == unreachable || distance >= before || pressure(next))
                continue;
            if (!out.feasible || distance < out.after) {
                out.feasible = true;
                out.at = next;
                out.after = distance;
            }
        }
    if (!funded()) {
        out.known = out.feasible = false;
        return out;
    }
    out.known = true;
    return out;
}
} // namespace tactics

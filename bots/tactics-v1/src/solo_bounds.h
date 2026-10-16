#pragma once
#include "types.h"
namespace tactics {
struct SoloImpossibility {
    double volley_upper = 0, unavoidable_damage = 0;
    int earliest_kill = 0;
    bool impossible = false;
};
// Narrow lower bound for the fixed contribution-stage clear. Grant a basic
// PLUS the strongest direct cast/reset every round, ignoring cooldown and cast
// conflicts. If even this optimistic stationary plan dies before its earliest
// kill, a timely helper is necessary for that plan. No work cap implies failure.
inline SoloImpossibility optimistic_solo_impossibility(const Actor &a, const Camp &camp,
                                                       double observed_shield = 0) {
    SoloImpossibility out;
    if (!a.alive || a.type < 0 || a.type > 11 || a.type == 0 || a.type == 7 || a.type == 9 ||
        a.type == 11 || a.enhanced || camp.awake || camp.hp <= 0 || camp.strength <= 0 ||
        distance(a.pos, camp.pos) > camp.range || !std::isfinite(a.hp) || a.hp <= 0 ||
        !std::isfinite(a.strength) || a.strength <= 0 || !std::isfinite(a.camp_mitigation) ||
        a.camp_mitigation <= 0 || !std::isfinite(a.shield) || a.shield < 0 || a.range < 0 ||
        camp.range < 0 || !std::isfinite(camp.hp) || !std::isfinite(camp.strength) ||
        !std::isfinite(observed_shield) || observed_shield < 0)
        return out;
    // Ryth/Marcella's enhanced control, Ren's retaliation and Tavi's mid-trip
    // shopping are excluded by physical type. Actual SDK2.2.2 kind4 is control;
    // any unknown/control/heal/shield or delayed payload is left to fallback.
    double cast = 0;
    const int d = distance(a.pos, camp.pos);
    const double basic = d <= a.range ? a.strength : 0;
    for (const auto &spell : a.spells) {
        if (spell.kind < 1 || spell.kind > 7 || spell.kind == 4 || spell.kind == 5 ||
            spell.kind == 7 || spell.duration > 0 || spell.range < 0 || spell.radius < 0 ||
            !std::isfinite(spell.amount) || spell.amount < 0 ||
            (spell.kind == 6 && spell.amount > 0))
            return out;
        if (spell.kind == 1) {
            if (!spell.self)
                return out;
            cast = std::max(cast, basic);
        } else if ((spell.kind == 2 || spell.kind == 3) && spell.camps &&
                   d <= spell.range + (spell.kind == 3 ? spell.radius : 0))
            cast = std::max(cast, spell.amount);
    }
    out.volley_upper = (basic + cast) * (a.monster ? 1.1 : 1.0);
    if (!std::isfinite(out.volley_upper) || out.volley_upper <= 0)
        return out;
    const double turns = std::ceil(camp.hp / out.volley_upper);
    if (!std::isfinite(turns) || turns < 1 || turns > unreachable)
        return out;
    out.earliest_kill = static_cast<int>(turns);
    // A sleeping camp gets no invented pre-wake hit: K volleys require at
    // least K-1 intervening responses. The killing volley can precede response K.
    out.unavoidable_damage = (out.earliest_kill - 1) * camp.strength * a.camp_mitigation;
    const double shield = std::max(std::max(0.0, a.shield), observed_shield);
    out.impossible =
        std::isfinite(out.unavoidable_damage) && out.unavoidable_damage >= a.hp + shield;
    return out;
}
} // namespace tactics

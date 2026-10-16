#pragma once
#include "types.h"
#include <bit>
#include <span>

namespace tactics {
struct BasicCampBody {
    const Actor *actor = nullptr;
    double reserve = 0;
};
struct BasicCampMonster {
    const Camp *camp = nullptr;
    bool observed = false;
};
struct BasicCampCertificate {
    bool ready = false;
    int ticks = 0, count = 0;
    std::array<int, 6> selected_ids{};
    std::array<double, 6> remaining_hp{}, damage_taken{};
};
inline std::optional<double> camp_basic_f32_ulp(double value) {
    const float rounded = static_cast<float>(value);
    if (!std::isfinite(rounded) || rounded < 0)
        return std::nullopt;
    const auto bits = std::bit_cast<std::uint32_t>(rounded);
    const float next = std::bit_cast<float>(bits + 1);
    if (!std::isfinite(next))
        return std::nullopt;
    return double(next) - double(rounded);
}
// Sufficient only. Each body must retain an ordinary basic against EVERY
// living member, at its actual fixed tile. No cast, shield, heal, control,
// splash or retaliation is credited. Unknown never proves infeasibility.
struct CampBasicBudget {
    bool operator()() const {
        return true;
    }
};
template <class Budget = CampBasicBudget>
inline BasicCampCertificate sufficient_basic_clear(std::span<const BasicCampBody> crew,
                                                   std::span<const BasicCampMonster> monsters,
                                                   int self_id, Budget funded = {}) {
    BasicCampCertificate out;
    if (!funded() || self_id < 0 || crew.empty() || crew.size() > 6 || monsters.empty() ||
        monsters.size() > 8)
        return out;
    double hp = 0, future_dps = 0, first_dps = 0, largest = 0, hp_ulp = 0;
    int living = 0;
    bool self = false;
    for (const auto &view : monsters) {
        if (!view.camp || view.camp->id < 0 || view.camp->pos.x < 0 || view.camp->pos.y < 0 ||
            !std::isfinite(view.camp->hp) || view.camp->hp < 0 ||
            !std::isfinite(view.camp->strength) || view.camp->strength < 0 || view.camp->range < 0)
            return out;
        if (view.camp->hp <= 0)
            continue;
        if (!view.observed)
            return out;
        const auto ulp = camp_basic_f32_ulp(view.camp->hp);
        if (!ulp)
            return out;
        hp_ulp = std::max(hp_ulp, *ulp);
        hp += std::max(view.camp->hp, double(static_cast<float>(view.camp->hp)));
        ++living;
    }
    if (!living || !std::isfinite(hp))
        return out;
    for (unsigned i = 0; i < crew.size(); ++i) {
        if (!funded())
            return {};
        if (!crew[i].actor)
            return out;
        const auto &a = *crew[i].actor;
        if (a.id < 0 || a.pos.x < 0 || a.pos.y < 0 || !a.alive || a.stunned ||
            a.channel != Channel::None || a.type < 0 || a.type > 11 || !std::isfinite(a.hp) ||
            !std::isfinite(a.max_hp) || a.max_hp <= 0 || a.hp <= 0 || !std::isfinite(a.strength) ||
            a.strength <= 0 || a.range < 1 || !std::isfinite(a.camp_mitigation) ||
            a.camp_mitigation <= 0 || !std::isfinite(crew[i].reserve) || crew[i].reserve < 0)
            return out;
        for (unsigned j = 0; j < i; ++j)
            if (crew[j].actor->id == a.id)
                return out;
        for (const auto &view : monsters)
            if (view.camp->hp > 0 && distance(a.pos, view.camp->pos) > a.range)
                return out;
        const double ideal = a.strength * (a.monster ? 1.1 : 1.0);
        const float native_product = static_cast<float>(a.strength) * (a.monster ? 1.1f : 1.0f);
        const double raw = std::min(ideal, double(native_product));
        const auto product_ulp = camp_basic_f32_ulp(raw);
        if (!product_ulp)
            return out;
        // Allow for f32 HP/product rounding: a subtraction may remove less
        // than the advertised hit; product+maximum current-HP ULP is reserved
        // on EVERY credited hit. The same lower credit drives both DPS and
        // overkill. Extra actual damage can only finish a target earlier.
        const double basic = raw - hp_ulp - *product_ulp;
        if (!std::isfinite(basic) || basic <= 0)
            return out;
        future_dps += basic;
        if (a.can_attack && !a.completed)
            first_dps += basic;
        largest = std::max(largest, basic);
        self |= a.id == self_id;
        out.selected_ids[i] = a.id;
    }
    // At most M-1 earlier kills waste part of a credited basic. Ignoring
    // this term would wrongly clear3tiny camps with one huge attack in1turn.
    const double damage_budget = hp + (living - 1) * largest;
    if (!self || !std::isfinite(damage_budget) || !std::isfinite(future_dps) || future_dps <= 0)
        return BasicCampCertificate{};
    const double ticks = 1 + std::ceil(std::max(0.0, damage_budget - first_dps) / future_dps);
    if (!std::isfinite(ticks) || ticks < 1 || ticks > 128)
        return BasicCampCertificate{};
    std::array<double, 6> pressure{};
    for (const auto &view : monsters) {
        if (!funded())
            return {};
        const auto &camp = *view.camp;
        if (camp.hp <= 0 || camp.strength <= 0)
            continue;
        int nearest = unreachable;
        for (const auto &body : crew)
            nearest = std::min(nearest, distance(body.actor->pos, camp.pos));
        if (nearest > camp.range)
            continue;
        for (unsigned i = 0; i < crew.size(); ++i)
            if (distance(crew[i].actor->pos, camp.pos) == nearest) {
                const auto &a = *crew[i].actor;
                const double ideal = camp.strength * a.camp_mitigation;
                const double native = double(static_cast<float>(camp.strength) *
                                             static_cast<float>(a.camp_mitigation));
                const double raw = std::max(ideal, native);
                const auto product_ulp = camp_basic_f32_ulp(raw);
                const auto body_ulp = camp_basic_f32_ulp(std::max(a.hp, a.max_hp));
                if (!product_ulp || !body_ulp)
                    return BasicCampCertificate{};
                // Upper-bound product/order and HP subtraction rounding, once
                // for each actual possible hit; never divide nearest ties.
                pressure[i] += raw + 3 * *product_ulp + *body_ulp;
            }
    }
    for (unsigned i = 0; i < crew.size(); ++i) {
        if (!funded())
            return {};
        const auto &a = *crew[i].actor;
        const double damage = pressure[i] * (ticks - 1);
        const double remaining = a.hp - damage;
        if (!std::isfinite(remaining) || remaining <= crew[i].reserve + .25 * a.max_hp + 1)
            return BasicCampCertificate{};
        out.remaining_hp[i] = remaining;
        out.damage_taken[i] = damage;
    }
    out.ticks = static_cast<int>(ticks);
    out.count = crew.size();
    if (!funded())
        return {};
    out.ready = true;
    return out;
}
} // namespace tactics

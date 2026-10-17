#pragma once
#include "camp_basic.h"
#include "types.h"
#include <span>

namespace tactics {
// A fixed-position direct-cast schedule only. This is not a travel, capture,
// enemy-absence, snapshot-provenance or whole-cycle certificate. The caller
// supplies those independent proofs before using it as a farming proposal.
struct CastOnlyCertificate {
    bool known = false, feasible = false, ready_now = false;
    int actor = -1, camp = -1, slot = -1, shots = 0, first_delay = 0, clear_ticks = 0;
    Pos origin{}, stage{};
    double damage_per_shot = 0, remaining_hp = 0;
};

inline CastOnlyCertificate certify_cast_only_clear(const Actor &actual, const Camp &camp, Pos stage,
                                                   int elapsed,
                                                   std::span<const Camp> nearby_camps = {},
                                                   double enemy_reply = 0, int max_ticks = 2000,
                                                   bool exclusive_allowed = true,
                                                   int required_slot = -1) {
    CastOnlyCertificate best;
    if (required_slot < -1 || required_slot > 1 || actual.id < 0 || actual.type < 0 ||
        actual.type > 11 || camp.id < 0 || camp.pos.x < 0 || camp.pos.y < 0 || !actual.alive ||
        actual.stunned || actual.channel != Channel::None || actual.pos.x < 0 || actual.pos.y < 0 ||
        stage.x < 0 || stage.y < 0 || elapsed < 0 || (elapsed == 0 && stage != actual.pos) ||
        max_ticks < 1 || !std::isfinite(actual.hp) || actual.hp <= 0 ||
        !std::isfinite(actual.max_hp) || actual.max_hp <= 0 || !std::isfinite(camp.hp) ||
        camp.hp <= 0 || !std::isfinite(camp.strength) || camp.strength < 0 || camp.range < 0 ||
        !std::isfinite(enemy_reply) || enemy_reply < 0 || distance(stage, camp.pos) <= camp.range)
        return best;
    for (const auto &other : nearby_camps) {
        if (other.id == camp.id || !other.awake || other.hp <= 0)
            continue;
        if (!std::isfinite(other.hp) || !std::isfinite(other.strength) || other.strength < 0 ||
            other.range < 0 || (other.strength > 0 && distance(stage, other.pos) <= other.range))
            return best; // No unpriced active pressure or imaginary helper tank.
    }
    const auto hp_ulp = camp_basic_f32_ulp(camp.hp);
    if (!hp_ulp)
        return best;
    const double hp = std::max(camp.hp, double(static_cast<float>(camp.hp)));
    for (int slot = 0; slot < 2; ++slot) {
        if (required_slot >= 0 && slot != required_slot)
            continue;
        const auto &spell = actual.spells[slot];
        // Direct targeting avoids unpriced area wakes. In particular, an AoE
        // radius cannot turn an out-of-range center into a legal direct cast.
        if (!spell.camps || (spell.kind != 2 && spell.kind != 4) || spell.cooldown < 0 ||
            spell.recharge <= 0 || spell.range <= camp.range ||
            distance(stage, camp.pos) > spell.range || !std::isfinite(spell.amount) ||
            spell.amount <= 0)
            continue;
        const double ideal = spell.amount * (actual.monster ? 1.1 : 1.0);
        const double native =
            double(static_cast<float>(spell.amount) * (actual.monster ? 1.1f : 1.0f));
        const double raw = std::min(ideal, native);
        const auto product_ulp = camp_basic_f32_ulp(raw);
        if (!product_ulp)
            continue;
        // Match the sufficient-basic model's conservative f32 product and HP
        // subtraction allowance on every hit, never ideal double arithmetic.
        const double damage = raw - *hp_ulp - *product_ulp;
        if (!std::isfinite(damage) || damage <= 0)
            continue;
        const double shots_value = std::ceil(hp / damage);
        if (!std::isfinite(shots_value) || shots_value < 1 || shots_value > 2000)
            continue;
        const bool can_now = elapsed == 0 && stage == actual.pos && !actual.completed &&
                             actual.can_cast && spell.ready && spell.cooldown == 0 &&
                             (!spell.exclusive || exclusive_allowed);
        int first_delay = std::max(0, spell.cooldown - elapsed);
        if (elapsed == 0 && !can_now)
            first_delay = std::max(1, first_delay);
        const int shots = static_cast<int>(shots_value);
        const std::int64_t ticks =
            std::int64_t(first_delay) + 1 + std::int64_t(shots - 1) * spell.recharge;
        if (ticks < 1 || ticks > std::numeric_limits<int>::max())
            continue;
        CastOnlyCertificate quote;
        quote.actor = actual.id;
        quote.camp = camp.id;
        quote.origin = actual.pos;
        quote.stage = stage;
        quote.slot = slot;
        quote.shots = shots;
        quote.first_delay = first_delay;
        quote.clear_ticks = static_cast<int>(ticks);
        quote.damage_per_shot = damage;
        quote.remaining_hp = actual.hp; // No monster response can reach this fixed tile.
        quote.ready_now = can_now;
        quote.known = true;
        quote.feasible = ticks <= max_ticks && enemy_reply + 1 < .75 * actual.hp;
        if (!best.known || (quote.feasible != best.feasible && quote.feasible) ||
            (quote.feasible == best.feasible && quote.clear_ticks < best.clear_ticks))
            best = quote;
    }
    return best;
}
} // namespace tactics

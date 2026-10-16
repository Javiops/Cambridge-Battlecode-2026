#pragma once
#include "coordination.h"
#include "resource.h"

namespace tactics {
struct SoloClearCertificate {
    double clear_ticks = 0, remaining_hp = 0, damage_taken = 0;
    bool known = false, feasible = false;
};
struct SoloFarmQuote {
    int group = -1, route_length = 0, arrival_ticks = 0, capture_ticks = 0, bank_ticks = 0,
        recovery_ticks = 0, new_gems = 0, new_gold = 0;
    int owner = -1, round = -1, serial = -1;
    Pos origin{};
    Pos target{}, stage{}, capture{};
    std::array<Pos, 25> route{};
    double clear_ticks = 0, total_ticks = 0, rate = 0, remaining_hp = 0;
    bool known = false, feasible = false, ready_now = false, current_only = false;
};

// A proof of one explicitly selected reset's promised immediate basic. The
// receipt survives only that accepted self reset plus exactly one self refresh.
struct SoloResetReceipt {
    bool valid = false;
    int owner = -1, round = -1, serial = -1, group = -1, slot = -1;
    Actor actor{};
    Camp camp{};
};

// A prospective quote is not a first-hit permission. Only known elapsed owner
// ends restore cooldowns; arrival never adds a free cast to the current turn.
inline SoloClearCertificate certify_solo_clear(Actor actual, const Camp &camp, Pos stage,
                                               int elapsed, bool ready_now, double enemy_reply = 0,
                                               int max_work = 64, bool current_awake = false) {
    SoloClearCertificate out;
    if (!actual.alive || actual.channel != Channel::None || actual.stunned || elapsed < 0 ||
        !std::isfinite(enemy_reply) || enemy_reply < 0 || camp.hp <= 0 ||
        (camp.awake && (!current_awake || elapsed > 1 || stage != actual.pos)) ||
        !std::isfinite(actual.hp) || actual.hp <= 0 || !std::isfinite(actual.strength) ||
        actual.strength <= 0 || !std::isfinite(actual.camp_mitigation) ||
        actual.camp_mitigation <= 0 || !std::isfinite(camp.hp) || !std::isfinite(camp.strength) ||
        camp.strength < 0 || camp.range < 0 || (!ready_now && elapsed < 1))
        return out;
    const double initial_hp = actual.hp;
    actual.pos = stage;
    actual.shield = 0; // Expiry during travel/clear is not invented as durable health.
    if (!ready_now) {
        actual.completed = false;
        actual.can_attack = actual.can_cast = true;
        for (auto &spell : actual.spells) {
            if (spell.cooldown >= 0) {
                spell.cooldown = std::max(0, spell.cooldown - elapsed);
                spell.ready = spell.cooldown == 0;
            }
        }
    }
    const int d = distance(stage, camp.pos);
    const bool basic_range = d <= actual.range;
    bool future_hit = basic_range && actual.strength > 0;
    bool hit_now = basic_range && actual.can_attack && !actual.completed;
    for (const auto &spell : actual.spells) {
        future_hit |= coordination_detail::damage_spell(spell) && d <= spell.range &&
                      (spell.ready || spell.cooldown >= 0);
        hit_now |= actual.can_cast && !actual.completed && spell.ready &&
                   ((coordination_detail::damage_spell(spell) && d <= spell.range) ||
                    (spell.kind == 1 && spell.self && basic_range));
    }
    if (!future_hit || (ready_now && !hit_now))
        return out;
    std::array<int, 2> cooldown;
    for (int slot = 0; slot < 2; ++slot)
        cooldown[slot] = actual.spells[slot].cooldown >= 0
                             ? actual.spells[slot].cooldown
                             : (actual.spells[slot].ready ? 0 : unreachable);
    const double pressure = d <= camp.range ? camp.strength * actual.camp_mitigation : 0;
    // Waiting on a currently awake camp incurs the actual idle-owner reply;
    // future readiness never supplies a free pause while the monster attacks.
    if (camp.awake) {
        out.damage_taken = elapsed * pressure;
        out.remaining_hp = initial_hp - out.damage_taken;
        if (out.damage_taken + enemy_reply + 1 >= .75 * initial_hp) {
            out.known = true;
            return out;
        }
    }
    const double camp_damage = actual.monster ? 1.1 : 1.0;
    double hp = camp.hp;
    for (int tick = 0; tick < std::clamp(max_work, 0, 128); ++tick) {
        ++out.clear_ticks;
        out.damage_taken += pressure; // All responses, including cooldown waits.
        out.remaining_hp = initial_hp - out.damage_taken;
        if (out.damage_taken + enemy_reply + 1 >= .75 * initial_hp) {
            out.known = true; // A monotonic reserve failure, not a work-cap guess.
            return out;
        }
        if (basic_range && (tick > 0 || (actual.can_attack && !actual.completed)))
            hp -= actual.strength * camp_damage;
        if (hp <= 0) {
            out.known = out.feasible = true;
            return out;
        }
        if (tick > 0 || (actual.can_cast && !actual.completed)) {
            int damage_slot = -1, reset_slot = -1;
            double gain = 0;
            for (int slot = 0; slot < 2; ++slot) {
                const auto &spell = actual.spells[slot];
                if (cooldown[slot] != 0 || (tick == 0 && !spell.ready))
                    continue;
                // Match farm's actual direct CastCamp range. Area radius is
                // not a legal target-range extension in that implementation.
                if (coordination_detail::damage_spell(spell) && d <= spell.range &&
                    std::min(hp, spell.amount) > gain) {
                    gain = std::min(hp, spell.amount);
                    damage_slot = slot;
                }
                if (spell.kind == 1 && spell.self && basic_range)
                    reset_slot = slot;
            }
            // Same order as farm: ordinary basic, useful damage, then reset
            // only if no damaging cast was chosen. Never two successful casts.
            const int slot = damage_slot >= 0 ? damage_slot : reset_slot;
            if (slot >= 0) {
                hp -=
                    (damage_slot >= 0 ? actual.spells[slot].amount : actual.strength) * camp_damage;
                cooldown[slot] =
                    actual.spells[slot].recharge > 0 ? actual.spells[slot].recharge : unreachable;
            }
        }
        if (hp <= 0) {
            out.known = out.feasible = true;
            return out;
        }
        for (auto &timer : cooldown)
            if (timer > 0 && timer != unreachable)
                --timer;
    }
    // A known future cast may justify waiting, but a bounded unfinished
    // schedule remains unknown rather than an invented feasible full clear.
    return out;
}
} // namespace tactics

#ifndef TACTICS_SOLO_MODEL_ONLY
#include "assembly.h"
namespace tactics {
inline SoloFarmQuote quote_solo_farm(World &w, int gi) {
    SoloFarmQuote out;
    out.group = gi;
    out.owner = w.self.id;
    out.round = w.round;
    out.serial = w.serial;
    out.origin = w.self.pos;
    const bool incumbent = gi == w.memory.mission.group && w.memory.mission.phase == Phase::Clear;
    if (gi < 0 || gi >= static_cast<int>(w.geo.groups.size()) ||
        !resource_has_bank(w.geo.groups[gi].gems, w.self.gems))
        return out; // Gold-only growth needs a named complete investment itinerary.
    const bool single = gi >= 0 && gi < static_cast<int>(w.groups.size()) &&
                        gi < static_cast<int>(w.geo.groups.size()) && w.groups[gi].fresh(w.round) &&
                        w.groups[gi].state == Lifecycle::Alive &&
                        w.geo.groups[gi].spawns.size() == 1 && w.groups[gi].camps.size() == 1;
    if (!single || (!assembly_detail::simple_sleeping(w, gi) && !incumbent) ||
        (!incumbent && !assembly_detail::available(w.self)) || !w.self.alive || w.self.stunned ||
        w.self.hp <= 0 || w.self.channel != Channel::None ||
        bc::fuel_remaining() <
            ((single && incumbent &&
              distance(w.self.pos, w.groups[gi].camps.front().pos) <= w.self.range)
                 ? 32000u
                 : 44000u) ||
        w.round != static_cast<int>(bc::round_number()) || !w.enemies.empty())
        return out;
    for (const auto &sight : w.sightings)
        if (sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round))
            return out;
    const auto &group = w.geo.groups[gi];
    const auto &camp = w.groups[gi].camps.front();
    auto arrival = assembly_detail::contribution_arrival(w, w.self, camp.pos);
    if (!arrival.known || !w.free(arrival.at) || w.warning_near(arrival.at, 4))
        return out;
    if (arrival.route_length == 0) {
        arrival.route[0] = w.self.pos;
        arrival.route_length = 1;
    }
    // Do not certify an unmodeled collateral wake from a splash/area hit.
    int collateral = w.self.type == 10 ? 1 : 0;
    for (const auto &spell : w.self.spells)
        if (spell.kind == 3 && spell.camps)
            collateral = std::max(collateral, spell.radius);
    for (unsigned other = 0; other < w.groups.size(); ++other) {
        const auto &view = w.groups[other];
        for (const auto &monster : view.camps) {
            if (monster.id == camp.id || monster.hp <= 0)
                continue;
            if (collateral > 0 && distance(monster.pos, camp.pos) <= collateral)
                return out;
            if (monster.awake && monster.strength > 0)
                for (int k = 0; k < arrival.route_length; ++k)
                    if (distance(monster.pos, arrival.route[k]) <= monster.range)
                        return out;
        }
        if (collateral > 0 && other != static_cast<unsigned>(gi))
            for (const auto &spawn : w.geo.groups[other].spawns)
                if (distance(spawn.pos, camp.pos) <= collateral)
                    return out; // Hidden neighbor is not certified dead.
    }
    Actor actual = w.self;
    if (w.memory.moved_round == w.round)
        for (auto &spell : actual.spells)
            if (spell.exclusive)
                spell.ready = false;
    const std::array<CampClearMonster, 1> monster{{{camp, true}}};
    const bool now = arrival.at == w.self.pos && coordination_detail::useful_now(actual, monster);
    if (camp.awake && (!incumbent || arrival.at != w.self.pos))
        return out; // No future movement/assembly through an awake camp.
    const int elapsed = now ? 0 : std::max(1, arrival.turns + (w.self.can_move ? 0 : 1));
    if (elapsed > 3 ||
        bc::fuel_remaining() < (incumbent && arrival.at == w.self.pos ? 22000u : 32000u))
        return out;
    const double enemy_reply = combat_detail::incoming_for(w, w.self, arrival.at, 1, false);
    const auto certificate =
        certify_solo_clear(actual, camp, arrival.at, elapsed, now, enemy_reply, 64, incumbent);
    if (!certificate.known)
        return out;
    if (!certificate.feasible) {
        out.known = true;
        return out; // A proven reserve failure may override an optimistic coarse quote.
    }
    const Pos capture = group.spawns.front().pos;
    const int capture_steps = coordination_detail::cached_distance(w, arrival.at, capture);
    const int home = w.home_distance(capture), altar = w.altar_distance(capture);
    if (capture_steps < 0 || capture_steps == unreachable || home == unreachable ||
        ((group.gems > 0 || w.self.gems > 0) && altar == unreachable))
        return out;
    int recipients = 1;
    bool remainder = true;
    for (const auto &ally : w.allies)
        if (ally.id != w.self.id && ally.alive && w.on_group(gi, ally.pos)) {
            ++recipients;
            remainder &= ally.id > w.self.id;
        }
    const int gems = group.gems / recipients + (remainder ? group.gems % recipients : 0);
    const int gold = group.gold / recipients + (remainder ? group.gold % recipients : 0);
    const int speed = std::max(1, w.self.move_speed);
    out.new_gems = gems;
    out.new_gold = gold;
    out.target = camp.pos;
    out.stage = arrival.at;
    out.capture = capture;
    out.route = arrival.route;
    out.route_length = arrival.route_length;
    out.arrival_ticks = elapsed;
    out.capture_ticks = (capture_steps + speed - 1) / speed + bc::constants::capture_time + 1;
    out.bank_ticks =
        (gems > 0 || w.self.gems > 0)
            ? (altar + speed - 1) / speed +
                  tribute_ticks(w.self.gems + gems, bc::constants::submit_gem_duration_multiplier,
                                bc::constants::submit_gem_base_duration,
                                bc::constants::submit_gem_minimum_duration)
            : 0;
    if (certificate.remaining_hp < Settings::ordinary_heal * w.self.max_hp)
        out.recovery_ticks =
            (w.self.home ? 3 : int(bc::constants::recall_time)) + 1 + (home + speed - 1) / speed;
    out.clear_ticks = certificate.clear_ticks;
    out.remaining_hp = certificate.remaining_hp;
    out.total_ticks =
        elapsed + out.clear_ticks + out.capture_ticks + out.bank_ticks + out.recovery_ticks;
    out.rate =
        (w.self.gems + gems + (w.round < 600 ? .25 : .24) * score_resource_gold(group.gems, gold)) /
        std::max(1.0, out.total_ticks);
    if (w.round + out.total_ticks >= bc::constants::max_rounds ||
        w.round != static_cast<int>(bc::round_number()))
        return SoloFarmQuote{};
    out.known = out.feasible = true;
    // The consumer must still re-run native action legality at its mutation
    // gateway. A future endpoint/cooldown certificate is never ready now.
    out.ready_now = now;
    return out;
}
// Re-certify one already committed stationary clear without repricing its
// unchanged bank/home legs. This is not a new-job or movement certificate.
inline SoloFarmQuote quote_current_solo_clear(World &w, int gi) {
    SoloFarmQuote out;
    if (bc::fuel_remaining() < 24000 || w.round != static_cast<int>(bc::round_number()) || gi < 0 ||
        gi >= static_cast<int>(w.groups.size()) || gi >= static_cast<int>(w.geo.groups.size()) ||
        w.memory.mission.phase != Phase::Clear || w.memory.mission.group != gi || !w.self.alive ||
        w.self.stunned || w.self.channel != Channel::None || !w.enemies.empty())
        return out;
    const auto &view = w.groups[gi];
    if (!view.fresh(w.round) || view.state != Lifecycle::Alive || view.camps.size() != 1 ||
        w.geo.groups[gi].spawns.size() != 1)
        return out;
    const auto &camp = view.camps.front();
    if (camp.hp <= 0 || distance(w.self.pos, camp.pos) > w.self.range ||
        !packed_bit(w.visible_bytes, w.geo.index(camp.pos)) || w.warning_near(w.self.pos, 4))
        return out;
    for (const auto &sight : w.sightings)
        if (sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round))
            return out;
    int collateral = w.self.type == 10 ? 1 : 0;
    for (const auto &spell : w.spells)
        if (spell.kind == 3 && spell.camps)
            collateral = std::max(collateral, spell.radius);
    for (unsigned other = 0; other < w.groups.size(); ++other) {
        for (const auto &monster : w.groups[other].camps)
            if (monster.id != camp.id && monster.hp > 0 &&
                ((monster.awake && distance(monster.pos, w.self.pos) <= monster.range) ||
                 (collateral > 0 && distance(monster.pos, camp.pos) <= collateral)))
                return out;
        if (collateral > 0 && other != static_cast<unsigned>(gi))
            for (const auto &spawn : w.geo.groups[other].spawns)
                if (distance(spawn.pos, camp.pos) <= collateral)
                    return out;
    }
    // Under the quiet/collateral guards above there are no other credible
    // sources. Charge this monster's entire next reply to self, ignoring shield
    // and any ally tank. This is at least farm_safe's .25maxHP hard floor.
    const double reply =
        distance(w.self.pos, camp.pos) <= camp.range ? camp.strength * w.self.camp_mitigation : 0;
    if (w.self.hp - reply <= .25 * w.self.max_hp)
        return out;
    Actor actual = w.self;
    if (w.memory.moved_round == w.round)
        for (auto &spell : actual.spells)
            if (spell.exclusive)
                spell.ready = false;
    const std::array<CampClearMonster, 1> monsters{{{camp, true}}};
    const bool now = coordination_detail::useful_now(actual, monsters);
    const auto clear = certify_solo_clear(actual, camp, w.self.pos, now ? 0 : 1, now, 0, 64, true);
    if (!clear.known || !clear.feasible || bc::fuel_remaining() < 13000 ||
        w.round != static_cast<int>(bc::round_number()))
        return out;
    out.group = gi;
    out.owner = w.self.id;
    out.round = w.round;
    out.serial = w.serial;
    out.origin = out.stage = w.self.pos;
    out.target = camp.pos;
    out.clear_ticks = clear.clear_ticks;
    out.remaining_hp = clear.remaining_hp;
    out.rate = w.memory.mission.rate;
    out.known = out.feasible = out.current_only = true;
    out.ready_now = now;
    return out;
}
// A prepaid quote is valid for one unchanged personal snapshot only.
inline bool current_solo_quote(const World &w, const SoloFarmQuote &q, int gi) {
    return q.group == gi && q.owner == w.self.id && q.round == w.round && q.serial == w.serial &&
           q.origin == w.self.pos;
}
} // namespace tactics
#endif

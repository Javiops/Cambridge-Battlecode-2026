#pragma once
#include "awake_entry.h"
#include "coordination.h"
#include "resource.h"
#include "solo_poke.h"
#include "solo_routes.h"

namespace tactics {
struct SoloClearCertificate {
    double clear_ticks = 0, remaining_hp = 0, damage_taken = 0;
    bool known = false, feasible = false;
};
enum class AwakeEntryTiming { ActualCurrent, FutureOneOwner };
enum class SoloFarmMode { Combined, DirectCastOnly };
struct SoloFarmQuote {
    int group = -1, route_length = 0, arrival_ticks = 0, capture_ticks = 0, bank_ticks = 0,
        recovery_ticks = 0, new_gems = 0, new_gold = 0;
    int owner = -1, round = -1, serial = -1;
    Pos origin{};
    Pos target{}, stage{}, capture{};
    std::array<Pos, 25> route{}, capture_route{};
    int capture_route_length = 0;
    double clear_ticks = 0, total_ticks = 0, rate = 0, remaining_hp = 0;
    SoloFarmMode mode = SoloFarmMode::Combined;
    AwakeEntryTiming entry = AwakeEntryTiming::ActualCurrent;
    double awake_prefix_damage = 0;
    int slot = -1;
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

// Carries a paid current-clear certificate across exactly its selected basic.
// Only a quiet singleton whose schedule has no competing ready damage cast
// can spend this proof on the already priced immediate reset/basic pair.
struct SoloBasicReceipt {
    bool valid = false;
    int owner = -1, round = -1, serial = -1, group = -1, slot = -1;
    double expected_damage = 0;
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
        // The current personal snapshot is after this global camp phase.
        // Sleeping camps awaken only from our first real hit; awake camps'
        // current-phase damage is already reflected in actual.hp. Subsequent
        // owner opportunities pay every intervening response/cooldown wait.
        // An awake delayed arrival was charged separately above.
        if (tick > 0)
            out.damage_taken += pressure;
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

// A future arrival forecast is never a present-hit receipt.
namespace tactics {
struct AwakeOneOwnerForecast {
    SoloClearCertificate clear{};
    Pos actual_origin{}, projected_stage{};
    double prefix_damage = 0;
    bool known = false, feasible = false;
};
inline AwakeOneOwnerForecast forecast_one_owner_awake_entry(const Actor &actual, const Camp &camp,
                                                            std::span<const Pos> paid_path,
                                                            double enemy_reply = 0,
                                                            int max_work = 64) {
    AwakeOneOwnerForecast out;
    out.actual_origin = actual.pos;
    if (!actual.alive || actual.completed || actual.stunned || actual.channel != Channel::None ||
        !actual.can_move || !camp.awake || paid_path.size() < 2 || paid_path.size() > 25 ||
        actual.move_speed < 1 || actual.move_speed > 8 ||
        int(paid_path.size()) - 1 > actual.move_speed || paid_path.front() != actual.pos ||
        !std::isfinite(actual.hp) || actual.hp <= 0 || !std::isfinite(camp.strength) ||
        camp.strength < 0 || !std::isfinite(actual.camp_mitigation) ||
        actual.camp_mitigation <= 0 || !std::isfinite(enemy_reply) || enemy_reply < 0)
        return out;
    for (unsigned k = 1; k < paid_path.size(); ++k)
        if (distance(paid_path[k - 1], paid_path[k]) != 1)
            return out;
    const Pos stage = paid_path.back();
    if (stage == actual.pos || distance(stage, camp.pos) > actual.range)
        return out;
    out.projected_stage = stage;
    // One whole possible camp phase is charged to self. No nearest-tank,
    // current ally, shield or helper damage is credited during the prefix.
    out.prefix_damage = camp.strength * actual.camp_mitigation;
    if (out.prefix_damage + enemy_reply + 1 >= .75 * actual.hp) {
        out.known = true;
        return out;
    }
    // This object is a FUTURE forecast, never the World actor or present
    // readiness. At the next actual owner the public caller re-reads all facts.
    Actor forecast = actual;
    forecast.pos = stage;
    forecast.hp -= out.prefix_damage;
    forecast.shield = 0;
    forecast.enhanced = false;
    forecast.completed = false;
    forecast.can_attack = forecast.can_cast = true;
    for (auto &spell : forecast.spells) {
        if (spell.cooldown >= 0) {
            spell.cooldown = std::max(0, spell.cooldown - 1);
            spell.ready = spell.cooldown == 0;
        } else {
            // A current ready flag without a known clock cannot promise a
            // future special action. Ordinary basics may still prove the job.
            spell.ready = false;
        }
    }
    const auto after_prefix =
        certify_solo_clear(forecast, camp, stage, 0, true, enemy_reply, max_work, true);
    if (!after_prefix.known)
        return out;
    out.known = true;
    out.clear = after_prefix;
    out.clear.damage_taken += out.prefix_damage;
    out.clear.remaining_hp = actual.hp - out.clear.damage_taken;
    out.clear.feasible =
        after_prefix.feasible && out.clear.damage_taken + enemy_reply + 1 < .75 * actual.hp;
    out.feasible = out.clear.feasible;
    return out;
}
} // namespace tactics

#ifndef TACTICS_SOLO_MODEL_ONLY
#include "assembly.h"
namespace tactics {
inline SoloFarmQuote price_solo_cycle(World &w, int gi, const assembly_detail::Arrival &arrival,
                                      int elapsed, int capture_steps,
                                      const SoloClearCertificate &certificate, bool now) {
    SoloFarmQuote out;
    out.group = gi;
    out.owner = w.self.id;
    out.round = w.round;
    out.serial = w.serial;
    out.origin = w.self.pos;
    const auto &group = w.geo.groups[gi];
    const auto &camp = w.groups[gi].camps.front();
    const Pos capture = group.spawns.front().pos;
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
    out.rate = priced_cash_investment(w.memory, gi, w.round)
                   ? w.memory.cash_investment_rate
                   : (w.self.gems + gems +
                      (w.round < 600 ? .25 : .24) * score_resource_gold(group.gems, gold)) /
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
// Optional explicit geometry from the already priced capture leg. It never
// changes affordability or inserts a new/partial distance field. Consumers
// needing a concrete path must treat length0 as Unknown.
inline void retain_solo_capture_path(World &w, SoloFarmQuote &quote, const SoloLocalRoute &local) {
    if (!quote.known || !quote.feasible)
        return;
    if (local.known && local.stage == quote.stage && local.capture_length > 0 &&
        local.capture_length <= 25 &&
        local.capture_route[local.capture_length - 1] == quote.capture) {
        quote.capture_route = local.capture_route;
        quote.capture_route_length = local.capture_length;
        return;
    }
    if (bc::fuel_remaining() < 35000 || w.round != int(bc::round_number()))
        return;
    const std::vector<std::uint16_t> *field = nullptr;
    bool reverse = false;
    if (auto it = w.geo.goal_cache.find({w.geo.index(quote.capture), 0});
        it != w.geo.goal_cache.end())
        field = &it->second;
    else if (auto it = w.geo.route_cache.find(w.geo.index(quote.capture));
             it != w.geo.route_cache.end())
        field = &it->second;
    else if (auto it = w.geo.route_cache.find(w.geo.index(quote.stage));
             it != w.geo.route_cache.end()) {
        field = &it->second;
        reverse = true;
    }
    if (!field)
        return;
    Pos current = reverse ? quote.capture : quote.stage;
    const Pos target = reverse ? quote.stage : quote.capture;
    int remaining = w.geo.at(*field, current), length = 1;
    if (remaining == unreachable || remaining >= 25)
        return;
    std::array<Pos, 25> path;
    path[0] = current;
    while (current != target && length < 25) {
        if (bc::fuel_remaining() < 35000)
            return;
        Pos next;
        int best = remaining;
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                Pos p{current.x + dx, current.y + dy};
                if ((!dx && !dy) || w.geo.blocked(p) ||
                    !packed_bit(w.visible_bytes, w.geo.index(p)) ||
                    (p != quote.capture && !w.free(p)))
                    continue;
                const int d = w.geo.at(*field, p);
                if (d < best) {
                    best = d;
                    next = p;
                }
            }
        if (next.x < 0)
            return;
        path[length++] = next;
        current = next;
        remaining = best;
    }
    if (current != target || w.round != int(bc::round_number()))
        return;
    quote.capture_route_length = length;
    for (int k = 0; k < length; ++k)
        quote.capture_route[k] = path[reverse ? length - 1 - k : k];
}
inline SoloFarmQuote quote_solo_basic_farm(World &w, int gi) {
    SoloFarmQuote out;
    out.group = gi;
    out.owner = w.self.id;
    out.round = w.round;
    out.serial = w.serial;
    out.origin = w.self.pos;
    const bool incumbent = gi == w.memory.mission.group && w.memory.mission.phase == Phase::Clear;
    if (gi < 0 || gi >= static_cast<int>(w.geo.groups.size()) ||
        (!resource_has_bank(w.geo.groups[gi].gems, w.self.gems) &&
         !priced_cash_investment(w.memory, gi, w.round)))
        return out; // Gold-only growth needs a named complete investment itinerary.
    const bool single = gi >= 0 && gi < static_cast<int>(w.groups.size()) &&
                        gi < static_cast<int>(w.geo.groups.size()) && w.groups[gi].fresh(w.round) &&
                        w.groups[gi].state == Lifecycle::Alive &&
                        w.geo.groups[gi].spawns.size() == 1 && w.groups[gi].camps.size() == 1;
    // Isolated experiment: a NEW awake job must already have a real useful
    // current action at the actual basic-range endpoint. It pays a full new
    // cycle quote and cannot borrow the cheaper incumbent-only certificate.
    Actor current = w.self;
    if (w.memory.moved_round == w.round)
        for (auto &spell : current.spells)
            if (spell.exclusive)
                spell.ready = false;
    const bool stationary_awake_entry =
        single && w.groups[gi].camps.front().awake &&
        distance(w.self.pos, w.groups[gi].camps.front().pos) <= w.self.range &&
        coordination_detail::useful_now(
            current, std::array<CampClearMonster, 1>{{{w.groups[gi].camps.front(), true}}});
    const bool potential_one_owner_awake =
        single && w.groups[gi].camps.front().awake && w.self.can_move && !w.self.completed &&
        distance(w.self.pos, w.groups[gi].camps.front().pos) > w.self.range &&
        distance(w.self.pos, w.groups[gi].camps.front().pos) <=
            w.self.range + std::max(1, w.self.move_speed);
    if (!single ||
        (!assembly_detail::simple_sleeping(w, gi) && !incumbent && !stationary_awake_entry &&
         !potential_one_owner_awake) ||
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
    SoloLocalRoute local;
    const Pos capture = group.spawns.front().pos;
    int capture_steps =
        arrival.known ? coordination_detail::cached_distance(w, arrival.at, capture) : -1;
    if (!arrival.known || capture_steps < 0) {
        // A cold full-map cache may be unaffordable after the fresh snapshot.
        // Prove only this short visible singleton route, without publishing a
        // partial field or assuming that another body will vacate its square.
        if (bc::fuel_remaining() < 44000)
            return out;
        local = visible_solo_route(
            w.geo.width, w.geo.height, w.geo.terrain, w.occupied_bytes, w.visible_bytes, w.self.pos,
            camp.pos, w.self.range, std::max(1, w.self.move_speed), 128,
            [&] { return bc::fuel_remaining() >= 35000 && w.round == int(bc::round_number()); });
        if (!local.known || w.round != int(bc::round_number()))
            return out;
        arrival.at = local.stage;
        arrival.turns = (local.arrival_steps + std::max(1, w.self.move_speed) - 1) /
                        std::max(1, w.self.move_speed);
        arrival.known = true;
        arrival.route = local.route;
        arrival.route_length = local.route_length;
        capture_steps = local.capture_steps;
    }
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
            if (monster.awake && monster.strength > 0) {
                for (int k = 0; k < arrival.route_length; ++k)
                    if (distance(monster.pos, arrival.route[k]) <= monster.range)
                        return out;
                // The cold-cache substitute proves both concrete local legs;
                // it does not silently price damage while entering capture.
                if (local.known)
                    for (int k = 0; k < local.capture_length; ++k)
                        if (distance(monster.pos, local.capture_route[k]) <= monster.range)
                            return out;
            }
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
    const bool future_awake = camp.awake && arrival.at != w.self.pos;
    if (future_awake) {
        if (!future_awake_entry_available(w.memory, gi, w.round) || !potential_one_owner_awake ||
            arrival.turns != 1 || arrival.route_length < 2 ||
            arrival.route_length > std::max(1, w.self.move_speed) + 1 ||
            arrival.route[0] != w.self.pos || arrival.route[arrival.route_length - 1] != arrival.at)
            return out;
        if (!complete_awake_entry_route(w.self,
                                        std::span(arrival.route.data(), arrival.route_length),
                                        arrival.at, [&](Pos p) {
                                            return w.round == int(bc::round_number()) &&
                                                   w.free(p) &&
                                                   packed_bit(w.visible_bytes, w.geo.index(p));
                                        }))
            return out;
    } else if (camp.awake && ((!incumbent && !stationary_awake_entry) || arrival.at != w.self.pos ||
                              (!incumbent && !now)))
        return out;
    const int elapsed = future_awake ? 1
                        : now        ? 0
                                     : std::max(1, arrival.turns + (w.self.can_move ? 0 : 1));
    if (elapsed > 3 ||
        bc::fuel_remaining() < (incumbent && arrival.at == w.self.pos ? 22000u : 32000u))
        return out;
    const double enemy_reply = combat_detail::incoming_for(w, w.self, arrival.at, 1, false);
    SoloClearCertificate certificate;
    AwakeOneOwnerForecast future;
    if (future_awake) {
        future = forecast_one_owner_awake_entry(
            actual, camp, std::span(arrival.route.data(), arrival.route_length), enemy_reply, 64);
        certificate = future.clear;
        certificate.known = future.known;
        certificate.feasible = future.feasible;
    } else
        certificate = certify_solo_clear(actual, camp, arrival.at, elapsed, now, enemy_reply, 64,
                                         incumbent || stationary_awake_entry);
    if (!certificate.known)
        return out;
    if (!certificate.feasible) {
        if (awake_entry_active(w.memory.awake_entry) && w.memory.awake_entry.group == gi &&
            w.round == int(bc::round_number()))
            abandon_awake_entry(w.memory, w.round);
        out.known = true;
        return out; // A proven reserve failure may override an optimistic coarse quote.
    }
    auto priced =
        price_solo_cycle(w, gi, arrival, elapsed, capture_steps, certificate, !future_awake && now);
    if (future_awake) {
        priced.entry = AwakeEntryTiming::FutureOneOwner;
        priced.awake_prefix_damage = future.prefix_damage;
    }
    retain_solo_capture_path(w, priced, local);
    return priced;
}
// A separate stationary direct-cast controller is the only executor allowed
// to consume this certificate. In particular, a cooldown wait cannot fall
// through to an in-range basic, area cast or movement towards the monster.
inline SoloFarmQuote quote_solo_cast_farm(World &w, int gi, bool current_only = false) {
    SoloFarmQuote out;
    const bool incumbent = w.memory.mission.group == gi && w.memory.mission.phase == Phase::Clear;
    if (gi < 0 || gi >= int(w.groups.size()) || gi >= int(w.geo.groups.size()) || !w.self.alive ||
        w.self.stunned || w.self.channel != Channel::None || (current_only && !incumbent) ||
        (!resource_has_bank(w.geo.groups[gi].gems, w.self.gems) &&
         !priced_cash_investment(w.memory, gi, w.round)) ||
        bc::fuel_remaining() < (current_only ? 24000u : 44000u) ||
        w.round != int(bc::round_number()) || !w.enemies.empty())
        return out;
    const auto &view = w.groups[gi];
    if (!view.fresh(w.round) || view.state != Lifecycle::Alive || view.camps.size() != 1 ||
        w.geo.groups[gi].spawns.size() != 1 ||
        (!incumbent && !assembly_detail::simple_sleeping(w, gi)))
        return out;
    const auto &camp = view.camps.front();
    if (!w.geo.valid(camp.pos) || !packed_bit(w.visible_bytes, w.geo.index(camp.pos)))
        return out;
    for (const auto &sight : w.sightings)
        if (sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round))
            return out;
    int range = 0;
    for (const auto &spell : w.self.spells)
        if (spell.camps && (spell.kind == 2 || spell.kind == 4) && spell.amount > 0 &&
            spell.cooldown >= 0 && spell.recharge > 0 && spell.range > camp.range)
            range = std::max(range, spell.range);
    if (!range || range > 24 || w.warning_near(w.self.pos, 4))
        return out;
    SoloLocalRoute route;
    if (current_only) {
        route.known = true;
        route.stage = w.self.pos;
        route.route[0] = w.self.pos;
        route.route_length = 1;
        route.arrival_steps = 0;
    } else {
        route = visible_solo_annulus_route(
            w.geo.width, w.geo.height, w.geo.terrain, w.occupied_bytes, w.visible_bytes, w.self.pos,
            camp.pos, camp.range + 1, range, std::max(1, w.self.move_speed), 128,
            [&] { return bc::fuel_remaining() >= 35000 && w.round == int(bc::round_number()); });
        if (!route.known)
            return out;
    }
    if (distance(route.stage, camp.pos) <= camp.range || distance(route.stage, camp.pos) > range ||
        !w.free(route.stage) || w.warning_near(route.stage, 4) ||
        (camp.awake && (!incumbent || route.stage != w.self.pos)))
        return out;
    // Current sight says nothing about seeing around a wall/bush after moving.
    // Query exactly one shortlisted future endpoint, never every route tile.
    if (route.stage != w.self.pos) {
        if (bc::fuel_remaining() < 36000 ||
            !w.me.visible_tiles_from(sdk(route.stage)).is_set(sdk(camp.pos)))
            return out;
    }
    for (const auto &group : w.groups) {
        if (bc::fuel_remaining() < 22000 || w.round != int(bc::round_number()))
            return out;
        for (const auto &other : group.camps) {
            if (other.id == camp.id || other.hp <= 0 || !other.awake || other.strength <= 0)
                continue;
            for (int k = 0; k < route.route_length; ++k)
                if (distance(route.route[k], other.pos) <= other.range)
                    return out;
            for (int k = 0; k < route.capture_length; ++k)
                if (distance(route.capture_route[k], other.pos) <= other.range)
                    return out;
        }
    }
    const int speed = std::max(1, w.self.move_speed);
    const int elapsed = route.stage == w.self.pos
                            ? 0
                            : (route.arrival_steps + speed - 1) / speed + (w.self.can_move ? 0 : 1);
    if (elapsed > 3 || bc::fuel_remaining() < (current_only ? 16000u : 26000u))
        return out;
    const auto clear = certify_cast_only_clear(w.self, camp, route.stage, elapsed, {}, 0,
                                               int(bc::constants::max_rounds) - w.round,
                                               w.memory.moved_round != w.round);
    if (!clear.known || !clear.feasible)
        return out;
    if (current_only) {
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
        out.ready_now = clear.ready_now;
    } else {
        assembly_detail::Arrival arrival;
        arrival.at = route.stage;
        arrival.known = true;
        arrival.turns = elapsed;
        arrival.route = route.route;
        arrival.route_length = route.route_length;
        SoloClearCertificate certificate;
        certificate.known = certificate.feasible = true;
        certificate.clear_ticks = clear.clear_ticks;
        certificate.remaining_hp = clear.remaining_hp;
        out = price_solo_cycle(w, gi, arrival, elapsed, route.capture_steps, certificate,
                               clear.ready_now);
        retain_solo_capture_path(w, out, route);
    }
    out.mode = SoloFarmMode::DirectCastOnly;
    out.slot = clear.slot;
    if (bc::fuel_remaining() < 13000 || w.round != int(bc::round_number()))
        return SoloFarmQuote{};
    return out;
}

inline SoloFarmQuote quote_solo_farm(World &w, int gi) {
    // The cheap current outer tile gets its own funded chance before an
    // unsuccessful close-range quote can spend the remaining path budget.
    bool current_outer = false;
    if (gi >= 0 && gi < int(w.groups.size()) && w.groups[gi].camps.size() == 1) {
        const auto &camp = w.groups[gi].camps.front();
        const int d = distance(w.self.pos, camp.pos);
        for (const auto &spell : w.self.spells)
            current_outer |= d > camp.range && d <= spell.range && spell.camps &&
                             (spell.kind == 2 || spell.kind == 4) && spell.amount > 0 &&
                             spell.cooldown >= 0 && spell.recharge > 0;
    }
    SoloFarmQuote ranged;
    if (current_outer)
        ranged = quote_solo_cast_farm(w, gi);
    auto basic = quote_solo_basic_farm(w, gi);
    // At most one future annulus endpoint is considered, only after the
    // ordinary option had its funded chance. An optional route never hides
    // an already-known usable basic quote when its bounded work runs out.
    if (!current_outer && bc::fuel_remaining() >= 44000)
        ranged = quote_solo_cast_farm(w, gi);
    if (ranged.known && ranged.feasible &&
        (!basic.known || !basic.feasible || ranged.rate > basic.rate))
        return ranged;
    return basic;
}

// Re-certify one already committed stationary clear without repricing its
// unchanged bank/home legs. This is not a new-job or movement certificate.
inline SoloFarmQuote quote_current_solo_clear(World &w, int gi) {
    // This fixed-position proof stays valid through real cooldown waits;
    // generic two-turn farm stagnation is not a cast-only execution rule.
    if (auto ranged = quote_solo_cast_farm(w, gi, true); ranged.known && ranged.feasible)
        return ranged;
    SoloFarmQuote out;
    if (bc::fuel_remaining() < 24000 || w.round != static_cast<int>(bc::round_number()) || gi < 0 ||
        gi >= static_cast<int>(w.groups.size()) || gi >= static_cast<int>(w.geo.groups.size()) ||
        (!resource_has_bank(w.geo.groups[gi].gems, w.self.gems) &&
         !priced_cash_investment(w.memory, gi, w.round)) ||
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

#pragma once
#include "solo_bounds.h"
#include "types.h"
#include <bit>
#include <span>

namespace tactics {
// Pending assembly is an intention to obtain a real crew. It is never current
// readiness, an accepted remote role, or permission to wake a monster.
struct AssemblyCandidate {
    int group = -1, anchor_id = -1, helper_id = -1, start = -1, expiry = -1;
    Pos target{}, stage{};
    double rate = 0, clear_ticks = 0, total_ticks = 0;
    std::uint64_t signature = 0;
    bool known = false, clear_ready = false;
    std::array<Pos, 25> route{};
    int route_length = 0;
};
struct AssemblyMember {
    int id = -1, arrival = -1;
    bool visible = false, alive = false, available = false, current_kit = false;
    bool claim = false, route_known = false, alternative_known = false;
    double alternative_rate = 0;
};
struct AssemblyFacts {
    int group = -1, self_id = -1, now = 0, horizon = 0;
    int existing_group = -1, existing_start = -1, last_progress = -1;
    bool fresh_sleeping = false, safe_stage = false, warning = false;
    bool actual_ready = false, hypothesis_affordable = false, minimal_crew = false;
    bool alternative_known = false, can_move = true, unchanged_failure = false;
    double reward_once = 0, cycle_ticks = 0, alternative_rate = 0;
};
inline AssemblyCandidate price_assembly(const AssemblyFacts &f,
                                        std::span<const AssemblyMember> crew, int max_arrival = 3,
                                        int handshake = 3, int lease = Settings::assembly_wait) {
    AssemblyCandidate out;
    if (f.group < 0 || f.self_id < 0 || crew.size() < 2 || crew.size() > 6 || !f.fresh_sleeping ||
        !f.safe_stage || f.warning || f.actual_ready || !f.hypothesis_affordable ||
        !f.minimal_crew || !f.alternative_known || f.unchanged_failure ||
        !std::isfinite(f.alternative_rate) || f.alternative_rate < 0 ||
        !std::isfinite(f.reward_once) || f.reward_once <= 0 || !std::isfinite(f.cycle_ticks) ||
        f.cycle_ticks <= 0 || max_arrival < 0 || handshake < 1 || lease < 1)
        return out;
    const bool continuing = f.existing_group == f.group && f.existing_start >= 0;
    const int start = continuing ? f.existing_start : f.now;
    if (f.now >= start + lease ||
        (continuing && f.can_move && f.last_progress >= 0 && f.now - f.last_progress >= handshake))
        return out;
    int arrival = 0, anchor = -1, helper = -1;
    bool self = false, anchor_claim = false;
    double abandoned = 0;
    for (const auto &body : crew) {
        if (body.id < 0 || !body.visible || !body.alive || !body.available || !body.current_kit ||
            !body.route_known || body.arrival < 0 || body.arrival > max_arrival)
            return out;
        for (const auto &other : crew)
            if (&body != &other && body.id == other.id)
                return out;
        arrival = std::max(arrival, body.arrival);
        if (anchor < 0 || body.id < anchor) {
            anchor = body.id;
            anchor_claim = body.claim;
        }
        if (body.id == f.self_id)
            self = true;
        else {
            if (!body.alternative_known || !std::isfinite(body.alternative_rate) ||
                body.alternative_rate < 0)
                return out;
            abandoned += body.alternative_rate;
            helper = helper < 0 ? body.id : std::min(helper, body.id);
        }
    }
    if (!self || (anchor != f.self_id && !anchor_claim))
        return out;
    const double duration = arrival + handshake + f.cycle_ticks;
    const double rate = f.reward_once / duration - abandoned;
    if (f.now + duration >= f.horizon || !std::isfinite(rate) ||
        rate <= f.alternative_rate * Settings::switch_margin)
        return out;
    out.group = f.group;
    out.anchor_id = anchor;
    out.helper_id = helper;
    out.start = start;
    out.expiry = start + lease;
    out.rate = rate;
    out.total_ticks = duration;
    out.known = true;
    return out; // clear_ready deliberately stays false.
}
} // namespace tactics

#ifndef TACTICS_ASSEMBLY_MODEL_ONLY
#include "coordination.h"
namespace tactics {
namespace assembly_detail {
inline bool simple_sleeping(const World &w, int gi) {
    return gi >= 0 && gi < static_cast<int>(w.groups.size()) &&
           gi < static_cast<int>(w.geo.groups.size()) && w.groups[gi].fresh(w.round) &&
           w.groups[gi].state == Lifecycle::Alive && w.geo.groups[gi].spawns.size() == 1 &&
           w.groups[gi].camps.size() == 1 && w.groups[gi].camps.front().hp > 0 &&
           !w.groups[gi].camps.front().awake;
}
inline bool available(const Actor &a) {
    return a.alive && !a.stunned && a.channel == Channel::None && a.hp > .35 * a.max_hp &&
           a.strength > 0 && a.range > 0;
}
struct Arrival {
    Pos at{};
    int turns = -1;
    bool known = false;
    std::array<Pos, 25> route{};
    int route_length = 0;
};
inline Arrival contribution_arrival(const World &w, const Actor &body, Pos camp,
                                    Pos reserved = {}) {
    if (w.geo.terrain.empty() || w.occupied_bytes.empty() || w.visible_bytes.empty())
        return {};
    Pos at = body.pos;
    const auto legal = [&](Pos p) {
        return p != reserved && !w.geo.blocked(p) && packed_bit(w.visible_bytes, w.geo.index(p)) &&
               (p == body.pos || !packed_bit(w.occupied_bytes, w.geo.index(p)));
    };
    if (at != reserved && distance(at, camp) <= body.range)
        return {at, 0, true};
    const std::vector<std::uint16_t> *field = nullptr;
    if (auto i = w.geo.goal_cache.find({w.geo.index(camp), 0}); i != w.geo.goal_cache.end())
        field = &i->second;
    else if (auto i = w.geo.route_cache.find(w.geo.index(camp)); i != w.geo.route_cache.end())
        field = &i->second;
    if (!field || w.geo.at(*field, at) == unreachable)
        return {};
    const int speed = std::max(1, body.move_speed);
    if (speed > 8)
        return {};
    std::array<Pos, 25> route{};
    route[0] = at;
    for (int steps = 1; steps <= 3 * speed; ++steps) {
        Pos next{};
        int best = w.geo.at(*field, at);
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                Pos p{at.x + dx, at.y + dy};
                if (!legal(p))
                    continue;
                const int d = w.geo.at(*field, p);
                if (d < best) {
                    best = d;
                    next = p;
                }
            }
        if (!w.geo.valid(next))
            return {};
        at = next;
        route[steps] = at;
        if (distance(at, camp) <= body.range) {
            Arrival result{at, (steps + speed - 1) / speed, true};
            result.route = route;
            result.route_length = steps + 1;
            return result;
        }
    }
    return {};
}
inline bool safe_stage(const World &w, Pos at) {
    for (const auto &enemy : w.enemies)
        if (enemy.alive && distance(enemy.pos, at) <=
                               possible_contact_reach(enemy, 4) + 3 * std::max(1, enemy.move_speed))
            return false;
    for (const auto &sighting : w.sightings) {
        const int age = w.round - sighting.round;
        if (!sighting.actor.alive || !combat_detail::recent_sighting(age))
            continue;
        bool visible = false;
        for (const auto &enemy : w.enemies)
            visible |= enemy.id == sighting.actor.id;
        if (!visible && distance(sighting.actor.pos, at) <=
                            possible_contact_reach(sighting.actor, 4) +
                                (age + 3) * std::max(1, sighting.actor.move_speed))
            return false;
    }
    for (const auto &group : w.groups)
        if (group.fresh(w.round))
            for (const auto &camp : group.camps)
                if (camp.awake && camp.hp > 0 && camp.strength > 0 &&
                    distance(camp.pos, at) <= camp.range)
                    return false;
    return !w.warning_near(at, 4);
}
inline std::uint64_t fingerprint(int group, const Actor &a, const Actor &b, const Camp &camp,
                                 bool helper_claim) {
    std::uint64_t hash = 1469598103934665603ULL;
    const auto add = [&](std::uint64_t value) { hash = (hash ^ value) * 1099511628211ULL; };
    add(group + 1);
    add(std::min(a.id, b.id) + 1);
    add(std::max(a.id, b.id) + 1);
    for (const auto *body : {&a, &b}) {
        // A small real upgrade can cross an exact survival/kill boundary.
        // Coarse stat buckets must not keep an old failed opportunity closed.
        add(body->id + 1);
        add(body->type + 1);
        add(body->pos.x + 1);
        add(body->pos.y + 1);
        add(body->range);
        add(body->move_speed);
        add(body->gems);
        add(std::bit_cast<std::uint64_t>(body->strength));
        add(std::bit_cast<std::uint64_t>(body->focus));
        add(std::bit_cast<std::uint64_t>(body->max_hp));
        add(std::bit_cast<std::uint64_t>(body->hp));
        add(std::bit_cast<std::uint64_t>(body->camp_mitigation));
        add(body->alive);
        add(body->stunned);
        add(static_cast<unsigned>(body->channel));
        add(body->home);
        add(body->monster);
        for (const auto &spell : body->spells) {
            add(spell.kind);
            add(spell.slot + 1);
            add(spell.cooldown + 1);
            add(spell.recharge + 1);
            add(spell.range);
            add(spell.radius);
            add(spell.duration);
            add(std::bit_cast<std::uint64_t>(spell.amount));
            add(std::bit_cast<std::uint64_t>(spell.scale));
            add(spell.ready);
            add(spell.exclusive);
            add(spell.camps);
            add(spell.enemies);
            add(spell.allies);
            add(spell.self);
            add(spell.ground);
        }
    }
    add(camp.id + 1);
    add(camp.type + 1);
    add(camp.pos.x + 1);
    add(camp.pos.y + 1);
    add(camp.range);
    add(std::bit_cast<std::uint64_t>(camp.hp));
    add(std::bit_cast<std::uint64_t>(camp.strength));
    add(camp.awake);
    add(helper_claim);
    return hash;
}
} // namespace assembly_detail

// Shortlisting hint ONLY. No future DPS or certified route is inferred here.
// Prioritize a personally visible nearby claim; otherwise a local sleeping
// singleton with a second visible eligible body may invite one finite lease.
inline std::optional<int> nearby_assembly_group(const World &w, const Memory &m) {
    int best = -1, nearest = unreachable;
    bool best_claim = false;
    if (!assembly_detail::available(w.self))
        return std::nullopt;
    for (unsigned gi = 0; gi < w.groups.size(); ++gi) {
        if (!assembly_detail::simple_sleeping(w, gi) ||
            (m.failed_group == static_cast<int>(gi) && w.round < m.failed_until))
            continue;
        const Pos camp = w.groups[gi].camps.front().pos;
        const int d = distance(w.self.pos, camp);
        if (d > w.self.range + 3 * std::max(1, w.self.move_speed))
            continue;
        bool partner = false, claim = false;
        for (const auto &ally : w.allies)
            if (ally.id != w.self.id && assembly_detail::available(ally) &&
                distance(ally.pos, camp) <= ally.range + 3 * std::max(1, ally.move_speed)) {
                partner = true;
                claim |= w.matching_claim(ally.id, gi);
            }
        if (partner &&
            (best < 0 || (claim && !best_claim) ||
             (claim == best_claim && (d < nearest || (d == nearest && int(gi) < best))))) {
            best = gi;
            nearest = d;
            best_claim = claim;
        }
    }
    return best >= 0 ? std::optional<int>(best) : std::nullopt;
}

inline std::optional<AssemblyCandidate> local_assembly_candidate(World &w, const Memory &m, int gi,
                                                                 double alternative_rate,
                                                                 bool alternative_known = true) {
    if (!alternative_known || !assembly_detail::simple_sleeping(w, gi) ||
        !assembly_detail::available(w.self) || bc::fuel_remaining() < 56000)
        return std::nullopt;
    const auto &group = w.geo.groups[gi];
    const auto purpose = resource_job_purpose(group.gems, w.self.gems, w.geo.monolith_only);
    if (purpose == ResourcePurpose::Ineligible || purpose == ResourcePurpose::MonolithFallback)
        return std::nullopt; // No invented gem return from unpriced gold-only assembly.
    const auto &camp = w.groups[gi].camps.front();
    const auto arrival = assembly_detail::contribution_arrival(w, w.self, camp.pos);
    if (!arrival.known || !assembly_detail::safe_stage(w, arrival.at))
        return std::nullopt;
    const int altar = w.altar_distance(camp.pos), home = w.home_distance(camp.pos);
    if ((group.gems && altar == unreachable) || home == unreachable)
        return std::nullopt;
    std::optional<AssemblyCandidate> best;
    int hypotheses = 0;
    for (const auto &ally : w.allies) {
        if (ally.id == w.self.id || !assembly_detail::available(ally) ||
            distance(ally.pos, camp.pos) > ally.range + 3 * std::max(1, ally.move_speed))
            continue;
        const bool claim = w.matching_claim(ally.id, gi);
        if (ally.id < w.self.id && !claim)
            continue; // Never follow an unaccepted or higher-ID moving leader.
        if (hypotheses++ >= 2 || bc::fuel_remaining() < 44000)
            break;
        const auto help = assembly_detail::contribution_arrival(w, ally, camp.pos, arrival.at);
        if (!help.known || !assembly_detail::safe_stage(w, help.at))
            continue;
        bool known = false, bank = false;
        int other = -1;
        Pos target;
        const double helper_alternative =
            coordination_detail::alternative(w, ally, gi, known, other, target, bank);
        if (!known)
            continue;
        std::array<CampClearBody, 2> bodies;
        bodies[0].actor = w.self;
        bodies[0].actor.pos = arrival.at;
        bodies[1].actor = ally;
        bodies[1].actor.pos = help.at;
        for (auto &body : bodies) {
            // The quote occurs after arrival/handshake. Expiring current shield
            // is discarded; basic permissions are prospective, never actual.
            body.actor.shield = 0;
            body.actor.completed = false;
            body.actor.can_attack = true;
            body.actor.can_cast = true;
        }
        const std::array<CampClearMonster, 1> monsters{{{camp, true}}};
        const auto lower = optimistic_solo_impossibility(bodies[0].actor, camp, w.self.shield);
        if (!lower.impossible) {
            // Measured generic solo rollout can cost29k. Reserve that work
            // plus the unchanged44k pair admission; a65k owner opportunity
            // must not spend29k only to discover that its consumer is unfunded.
            if (bc::fuel_remaining() < 80000)
                continue;
            const auto solo =
                rollout_camp_clear(std::span(bodies.data(), 1), monsters, w.self.id, 128);
            if (w.round != static_cast<int>(bc::round_number()))
                return std::nullopt;
            if (solo.ready || solo.uncertain)
                continue; // Cap/unknown never proves a helper necessary.
        }
        if (bc::fuel_remaining() < 44000)
            break;
        const auto projected = rollout_camp_clear(bodies, monsters, w.self.id, 192);
        if (w.round != static_cast<int>(bc::round_number()))
            return std::nullopt;
        if (!projected.ready)
            continue;
        const int speed = std::max(1, w.self.move_speed);
        double recovery = 0;
        if (!projected.remaining_hp.empty() && projected.remaining_hp[0] < .55 * w.self.max_hp)
            recovery = (w.self.home ? 3 : int(bc::constants::recall_time)) + 2 +
                       (home + speed - 1) / speed;
        const double cycle =
            projected.ticks + bc::constants::capture_time + 1 + recovery +
            (group.gems ? (altar + speed - 1) / speed +
                              tribute_ticks(w.self.gems + group.gems,
                                            bc::constants::submit_gem_duration_multiplier,
                                            bc::constants::submit_gem_base_duration,
                                            bc::constants::submit_gem_minimum_duration)
                        : 0);
        const auto signature = assembly_detail::fingerprint(gi, w.self, ally, camp, claim);
        AssemblyFacts f;
        f.group = gi;
        f.self_id = w.self.id;
        f.now = w.round;
        f.horizon = bc::constants::max_rounds;
        if (m.mission.assembly_pending && m.mission.group == gi) {
            f.existing_group = gi;
            f.existing_start = m.mission.start;
            f.last_progress = m.mission.last_progress;
        }
        f.fresh_sleeping = f.safe_stage = f.hypothesis_affordable = f.minimal_crew = true;
        f.alternative_known = alternative_known;
        f.alternative_rate = alternative_rate;
        f.can_move = w.self.can_move;
        f.unchanged_failure =
            m.assembly_failed_group == gi && m.assembly_failed_signature == signature;
        f.reward_once =
            group.gems + (w.round < 600 ? .25 : .24) * score_resource_gold(group.gems, group.gold);
        f.cycle_ticks = cycle;
        const std::array<AssemblyMember, 2> members{
            {{w.self.id, arrival.turns, true, true, true, true, w.matching_claim(w.self.id, gi),
              true, true, alternative_rate},
             {ally.id, help.turns, true, true, true, true, claim, true, known,
              helper_alternative}}};
        auto candidate = price_assembly(f, members);
        if (!candidate.known)
            continue;
        candidate.target = camp.pos;
        candidate.stage = arrival.at;
        candidate.route = arrival.route;
        candidate.route_length = arrival.route_length;
        candidate.signature = signature;
        candidate.clear_ticks = projected.ticks;
        if (!best || candidate.rate > best->rate ||
            (candidate.rate == best->rate && candidate.helper_id < best->helper_id))
            best = candidate;
    }
    return best;
}
inline std::optional<Pos> assembly_step(const World &w, const Mission &job) {
    if (!w.self.can_move || !job.assembly_pending)
        return std::nullopt;
    int at = -1;
    for (int i = 0; i < job.assembly_route_length; ++i)
        if (job.assembly_route[i] == w.self.pos)
            at = i;
    if (at < 0)
        return std::nullopt;
    int next = at;
    for (int i = at + 1; i < job.assembly_route_length && i <= at + std::max(1, w.self.move_speed);
         ++i) {
        if (!w.free(job.assembly_route[i]))
            break;
        next = i;
    }
    return next > at ? std::optional<Pos>(job.assembly_route[next]) : std::nullopt;
}
} // namespace tactics
#endif

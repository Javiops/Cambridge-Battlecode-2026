#pragma once
#include "camp_actions.h"
#include "camp_collateral.h"
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
    std::array<int, 6> selected_ids{};
    int selected_count = 0;
    std::array<Pos, 25> exit_route{};
    int exit_length = 0;
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
    bool fresh_sleeping = false, fresh_observed = false, safe_stage = false, warning = false;
    bool actual_ready = false, hypothesis_affordable = false, priced_crew = false;
    bool alternative_known = false, can_move = true, unchanged_failure = false;
    double reward_once = 0, cycle_ticks = 0, alternative_rate = 0;
};
// Early setup may reserve a reversible rendezvous before elective planning.
// It cannot preempt a live clear, capture holder, survival exit or transaction.
inline bool early_assembly_eligible(const Actor &a, const Mission &job, int now, bool holder,
                                    bool hostile, bool transaction) {
    return a.alive && !a.stunned && a.channel == Channel::None && a.gems == 0 &&
           std::isfinite(a.hp) && std::isfinite(a.max_hp) && a.max_hp > 0 &&
           a.hp >= .75 * a.max_hp && !holder && !hostile && !transaction && job.group >= 0 &&
           job.phase != Phase::Clear && job.phase != Phase::Collect && job.sortie_length == 0 &&
           !job.assembly_pending && !job.chain_used && !job.bank_after_reward &&
           (job.rate > 0 || job.phase == Phase::Observe || job.phase == Phase::Assemble) &&
           job.expiry >= now;
}
inline AssemblyCandidate price_assembly(const AssemblyFacts &f,
                                        std::span<const AssemblyMember> crew, int max_arrival = 3,
                                        int handshake = 3, int lease = Settings::assembly_wait) {
    AssemblyCandidate out;
    if (f.group < 0 || f.self_id < 0 || (crew.size() < 2 && !f.fresh_observed) || crew.empty() ||
        crew.size() > 6 || (!f.fresh_sleeping && !f.fresh_observed) || !f.safe_stage || f.warning ||
        f.actual_ready || !f.hypothesis_affordable || !f.priced_crew || !f.alternative_known ||
        f.unchanged_failure || !std::isfinite(f.alternative_rate) || f.alternative_rate < 0 ||
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
// Conservative stationary approach exposure, before the first planned camp
// action. Initial shields and hypothetical support casts are not free HP.
inline std::optional<double> assembly_approach_damage(const Actor &body, std::span<const Pos> route,
                                                      int turns, int wait,
                                                      std::span<const Camp> awake) {
    if (route.empty() || route.size() > 25 || turns < 0 || wait < 0 || turns + wait > 6 ||
        awake.size() > 40 || body.move_speed < 1)
        return std::nullopt;
    double damage = 0;
    for (int tick = 0; tick < turns + wait; ++tick) {
        const Pos at = route[std::min<int>(route.size() - 1, tick * body.move_speed)];
        for (const auto &camp : awake)
            if (camp.hp > 0 && camp.awake && distance(camp.pos, at) <= camp.range)
                damage += camp.strength * body.camp_mitigation;
    }
    return std::isfinite(damage) ? std::optional<double>(damage) : std::nullopt;
}
// Find a real adjacent step that reduces exposure to stationary camps. A
// homeward gradient may run through the camp; home distance only breaks ties.
template <class Legal, class HomeDistance>
inline std::optional<Pos> assembly_exit_step(Pos at, std::span<const Camp> threats, Legal legal,
                                             HomeDistance home) {
    const auto penetration = [&](Pos p) {
        int score = 0;
        for (const auto &camp : threats)
            if (camp.hp > 0 && camp.strength > 0)
                score += std::max(0, camp.range + 1 - distance(p, camp.pos));
        return score;
    };
    const int current = penetration(at);
    int best = current, home_best = unreachable;
    std::optional<Pos> result;
    for (int dy = -1; dy <= 1; ++dy)
        for (int dx = -1; dx <= 1; ++dx) {
            if (!dx && !dy)
                continue;
            Pos p{at.x + dx, at.y + dy};
            const int exposure = penetration(p);
            if (exposure >= current || exposure > best || !legal(p))
                continue;
            const int home_distance = home(p);
            if (!result || exposure < best || home_distance < home_best) {
                result = p;
                best = exposure;
                home_best = home_distance;
            }
        }
    return result;
}
inline std::uint64_t assembly_group_signature(int group, std::span<const Actor *const> crew,
                                              std::span<const Camp> camps) {
    std::uint64_t hash = 1469598103934665603ULL;
    const auto add = [&](std::uint64_t value) { hash = (hash ^ value) * 1099511628211ULL; };
    const auto real = [&](double value) { add(std::bit_cast<std::uint64_t>(value)); };
    add(group + 1);
    add(crew.size());
    add(camps.size());
    for (const Actor *body : crew) {
        if (!body) {
            add(0);
            continue;
        }
        add(body->id + 1);
        add(body->type + 1);
        add(body->pos.x + 1);
        add(body->pos.y + 1);
        add(body->range);
        add(body->move_speed);
        add(body->gems);
        add(body->priority);
        real(body->hp);
        real(body->max_hp);
        real(body->strength);
        real(body->focus);
        real(body->shield);
        real(body->mitigation);
        real(body->camp_mitigation);
        add(body->shield_ticks + 1);
        add(body->stun_ticks + 1);
        add(body->channel_ticks + 1);
        add(body->alive);
        add(body->stunned);
        add(body->completed);
        add(body->enhanced);
        add(body->can_move);
        add(body->can_attack);
        add(body->can_cast);
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
            real(spell.amount);
            real(spell.scale);
            add(spell.ready);
            add(spell.exclusive);
            add(spell.camps);
            add(spell.enemies);
            add(spell.allies);
            add(spell.self);
            add(spell.ground);
        }
    }
    for (const auto &camp : camps) {
        add(camp.id + 1);
        add(camp.group + 1);
        add(camp.type + 1);
        add(camp.pos.x + 1);
        add(camp.pos.y + 1);
        add(camp.range);
        real(camp.hp);
        real(camp.max_hp);
        real(camp.strength);
        add(camp.awake);
    }
    return hash; // No round-only trigger: actual relevant state must change.
}
// Renew a continuing clear from observed work, before its finite lease gate.
// A hypothetical forecast, movement, claim or spent permission is not progress.
inline bool renew_crew_clear_lease(Mission &job, int now, int seen, bool fully_observed_live,
                                   double camp_hp) {
    if (job.phase != Phase::Clear || job.group < 0 || job.assembly_count < 1 ||
        job.assembly_count > 6 || seen != now || !fully_observed_live || !std::isfinite(camp_hp) ||
        camp_hp < 0 || !std::isfinite(job.last_camp_hp) || job.last_camp_hp < 0 ||
        camp_hp >= job.last_camp_hp)
        return false;
    job.last_progress = now;
    job.last_camp_hp = camp_hp;
    job.stagnant = 0;
    job.expiry = std::max(job.expiry, now + Settings::job_lease);
    return true;
}
inline bool assembly_quiet_path(std::span<const Pos> route, const Actor &enemy, int horizon) {
    if (route.empty())
        return false;
    if (!enemy.alive)
        return true;
    const int contact = camp_enemy_contact(enemy, horizon);
    return std::all_of(route.begin(), route.end(),
                       [&](Pos p) { return distance(enemy.pos, p) > contact; });
}
inline bool assembly_exit_unreserved(std::span<const Pos> route, Pos own_stage,
                                     std::span<const Pos> stages) {
    if (route.empty())
        return false;
    for (Pos p : route)
        for (Pos stage : stages)
            if (stage != own_stage && p == stage)
                return false;
    return true;
}
// A geometric hint is reusable only for the same actual body and stance.
// The 32-round TTL is a bounded cache lifetime, not a readiness guarantee.
inline bool assembly_hint_matches(const AssemblyPathHint &hint, int actor, Pos origin, Pos goal,
                                  Pos start, int range, int speed, int kind, int now) {
    return hint.actor == actor && hint.origin == origin && hint.goal == goal &&
           hint.start == start && hint.range == range && hint.speed == speed && hint.kind == kind &&
           hint.length > 0 && hint.length <= 25 && now >= hint.seen && now - hint.seen <= 32;
}
// Active route spans are pinned for one producer call. Failed alternative
// paths cannot evict a span that an earlier selected body is still borrowing.
inline int assembly_unborrowed_slot(std::span<const AssemblyPathHint> hints,
                                    std::uint32_t generation) {
    int best = -1;
    for (unsigned k = 0; k < hints.size(); ++k)
        if (hints[k].borrowed_generation != generation &&
            (best < 0 || hints[k].touched < hints[best].touched))
            best = k;
    return best;
}
template <class Legal> inline bool assembly_hint_legal(const AssemblyPathHint &hint, Legal legal) {
    if (hint.length < 1 || hint.length > 25 || hint.route[0] != hint.start)
        return false;
    for (int k = 0; k < hint.length; ++k)
        if (!legal(hint.route[k]) || (k && distance(hint.route[k - 1], hint.route[k]) != 1))
            return false;
    return true;
}
} // namespace tactics

#ifndef TACTICS_ASSEMBLY_MODEL_ONLY
#include "coordination.h"
namespace tactics {
namespace assembly_detail {
inline int prospective_range(const Actor &body, int elapsed);
inline bool simple_sleeping(const World &w, int gi) {
    return gi >= 0 && gi < static_cast<int>(w.groups.size()) &&
           gi < static_cast<int>(w.geo.groups.size()) && w.groups[gi].fresh(w.round) &&
           w.groups[gi].state == Lifecycle::Alive && w.geo.groups[gi].spawns.size() == 1 &&
           w.groups[gi].camps.size() == 1 && w.groups[gi].camps.front().hp > 0 &&
           !w.groups[gi].camps.front().awake;
}
inline bool observed_group(const World &w, int gi) {
    if (gi < 0 || gi >= static_cast<int>(w.groups.size()) ||
        gi >= static_cast<int>(w.geo.groups.size()) || !w.groups[gi].fresh(w.round) ||
        w.groups[gi].state != Lifecycle::Alive || w.groups[gi].camps.empty() ||
        w.groups[gi].camps.size() > 8)
        return false;
    const auto &view = w.groups[gi];
    for (const auto &spawn : w.geo.groups[gi].spawns)
        if (std::find(view.known_dead.begin(), view.known_dead.end(), spawn.id) ==
                view.known_dead.end() &&
            std::none_of(view.camps.begin(), view.camps.end(),
                         [&](const Camp &c) { return c.id == spawn.id && c.hp > 0; }))
            return false;
    return std::all_of(view.camps.begin(), view.camps.end(),
                       [](const Camp &c) { return c.hp > 0; });
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
inline bool basic_coverage(Pos at, int range, std::span<const Camp> targets) {
    if (range < 1 || targets.empty() || targets.size() > 8)
        return false;
    bool living = false;
    for (const auto &camp : targets) {
        if (camp.hp <= 0)
            continue;
        living = true;
        if (distance(at, camp.pos) > range)
            return false;
    }
    return living;
}
inline Arrival contribution_arrival(const World &w, const Actor &body, Pos camp, Pos reserved = {},
                                    std::span<const Camp> covered = {}) {
    if (w.geo.terrain.empty() || w.occupied_bytes.empty() || w.visible_bytes.empty())
        return {};
    Pos at = body.pos;
    const auto legal = [&](Pos p) {
        return p != reserved && !w.geo.blocked(p) && packed_bit(w.visible_bytes, w.geo.index(p)) &&
               (p == body.pos || !packed_bit(w.occupied_bytes, w.geo.index(p)));
    };
    const auto in_range = [&](Pos p) {
        return covered.empty() ? distance(p, camp) <= body.range
                               : basic_coverage(p, body.range, covered);
    };
    if (at != reserved && in_range(at))
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
                const int d = w.geo.at(*field, p);
                if (d >= best || !legal(p))
                    continue;
                if (d < best) {
                    best = d;
                    next = p;
                }
            }
        if (!w.geo.valid(next))
            return {};
        at = next;
        route[steps] = at;
        if (in_range(at)) {
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
        if (!assembly_detail::observed_group(w, gi) ||
            (m.failed_group == static_cast<int>(gi) && w.round < m.failed_until))
            continue;
        const Pos camp = w.groups[gi].camps.front().pos;
        const int d = distance(w.self.pos, camp);
        if (d > assembly_detail::prospective_range(w.self, 6) + 3 * std::max(1, w.self.move_speed))
            continue;
        bool partner = false, claim = false;
        for (const auto &ally : w.allies)
            if (ally.id != w.self.id && assembly_detail::available(ally) &&
                distance(ally.pos, camp) <= assembly_detail::prospective_range(ally, 6) +
                                                3 * std::max(1, ally.move_speed)) {
                partner = true;
                claim |= w.matching_claim(ally.id, gi);
            }
        if ((partner || w.groups[gi].camps.size() > 1 || w.groups[gi].camps.front().awake) &&
            (best < 0 || (claim && !best_claim) ||
             (claim == best_claim && (d < nearest || (d == nearest && int(gi) < best))))) {
            best = gi;
            nearest = d;
            best_claim = claim;
        }
    }
    return best >= 0 ? std::optional<int>(best) : std::nullopt;
}

inline std::optional<AssemblyCandidate>
singleton_assembly_candidate(World &w, const Memory &m, int gi, double alternative_rate,
                             bool alternative_known = true) {
    if (!alternative_known || !assembly_detail::simple_sleeping(w, gi) ||
        !assembly_detail::available(w.self) || bc::fuel_remaining() < 56000)
        return std::nullopt;
    const auto &group = w.geo.groups[gi];
    const auto purpose = resource_job_purpose(group.gems, w.self.gems, w.geo.monolith_only);
    if (purpose == ResourcePurpose::Ineligible || purpose == ResourcePurpose::MonolithFallback)
        return std::nullopt; // No invented gem return from unpriced gold-only
                             // assembly.
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
                rollout_camp_clear(std::span(bodies.data(), 1), monsters, w.self.id, 128, [&] {
                    return bc::fuel_remaining() >= 44000 &&
                           w.round == static_cast<int>(bc::round_number());
                });
            if (w.round != static_cast<int>(bc::round_number()))
                return std::nullopt;
            if (solo.ready || solo.uncertain)
                continue; // Cap/unknown never proves a helper necessary.
        }
        if (bc::fuel_remaining() < 44000)
            break;
        const auto projected = rollout_camp_clear(bodies, monsters, w.self.id, 192, [&] {
            return bc::fuel_remaining() >= 32000 && w.round == static_cast<int>(bc::round_number());
        });
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
        f.fresh_sleeping = f.safe_stage = f.hypothesis_affordable = f.priced_crew = true;
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

namespace assembly_detail {
// A future damage action's true targeting range. CastCamp does not acquire
// the area radius of a ground spell. Unknown cooldown cannot promise a cast.
inline int prospective_range(const Actor &body, int elapsed) {
    int range = body.range;
    for (const auto &spell : body.spells)
        if (camp_damage_ability(spell) &&
            (spell.ready || (spell.cooldown >= 0 && spell.cooldown <= elapsed)))
            range = std::max(range, spell.range);
    return range;
}
inline bool route_tile(const World &w, const Actor &body, Pos at, std::span<const Pos> reserved,
                       Pos allowed = {}) {
    if (!w.geo.valid(at) || w.geo.blocked(at) || !packed_bit(w.visible_bytes, w.geo.index(at)) ||
        (at != body.pos && packed_bit(w.occupied_bytes, w.geo.index(at))) ||
        (w.memory.blocked_round == w.round && w.memory.blocked_tile == at))
        return false;
    for (Pos slot : reserved)
        if (at == slot && at != allowed)
            return false;
    return true;
}
inline const AssemblyPathHint *remember_path(World &w, const Actor &body, Pos goal, Pos start,
                                             int range, int kind, const Arrival &arrival) {
    if (!arrival.known || arrival.route_length < 1 || arrival.route_length > 25)
        return nullptr;
    AssemblyPathHint *slot = nullptr;
    for (auto &hint : w.memory.assembly_paths)
        if (hint.actor == body.id && hint.origin == body.pos && hint.goal == goal &&
            hint.start == start && hint.range == range && hint.speed == body.move_speed &&
            hint.kind == kind) {
            slot = &hint;
            break;
        }
    if (slot && slot->borrowed_generation == w.memory.assembly_path_generation) {
        if (slot->length != arrival.route_length ||
            !std::equal(arrival.route.begin(), arrival.route.begin() + arrival.route_length,
                        slot->route.begin()))
            return nullptr;
        return slot;
    }
    if (!slot) {
        const int index =
            assembly_unborrowed_slot(w.memory.assembly_paths, w.memory.assembly_path_generation);
        if (index < 0)
            return nullptr;
        slot = &w.memory.assembly_paths[index];
    }
    const bool changed =
        slot->actor != body.id || slot->origin != body.pos || slot->goal != goal ||
        slot->start != start || slot->range != range || slot->speed != body.move_speed ||
        slot->kind != kind || slot->length != arrival.route_length ||
        !std::equal(arrival.route.begin(), arrival.route.begin() + arrival.route_length,
                    slot->route.begin());
    *slot = {body.id,  range, body.move_speed, kind,          w.round,
             body.pos, goal,  start,           arrival.route, arrival.route_length};
    slot->touched = ++w.memory.assembly_path_clock;
    slot->borrowed_generation = w.memory.assembly_path_generation;
    // Completed immutable geometry can unlock the next owner's bounded probe.
    // This is neither mission progress nor an extension of the assembly lease.
    if (changed)
        w.memory.assembly_probe_round = std::min(w.memory.assembly_probe_round, w.round - 3);
    return slot;
}
struct RouteView {
    Pos at{};
    int turns = -1;
    bool known = false;
    std::span<const Pos> route{};
    int route_length = 0;
};
inline RouteView route_view(const AssemblyPathHint &hint, int turns) {
    return {hint.route[hint.length - 1], turns, true, std::span(hint.route.data(), hint.length),
            hint.length};
}
inline RouteView group_arrival(World &w, const Actor &body, Pos anchor,
                               std::span<const Pos> reserved, bool basic_station = false,
                               std::span<const Camp> basic_targets = {}) {
    const int range = basic_station ? body.range : prospective_range(body, 6);
    const int kind = basic_targets.empty() ? 0 : 2;
    const int speed = std::max(1, body.move_speed);
    for (auto &hint : w.memory.assembly_paths) {
        if (!assembly_hint_matches(hint, body.id, body.pos, anchor, body.pos, range,
                                   body.move_speed, kind, w.round))
            continue;
        if (!assembly_hint_legal(hint, [&](Pos p) { return route_tile(w, body, p, reserved); }) ||
            distance(hint.route[hint.length - 1], anchor) > range ||
            (!basic_targets.empty() &&
             !basic_coverage(hint.route[hint.length - 1], body.range, basic_targets)))
            continue;
        auto result = route_view(hint, (hint.length - 1 + speed - 1) / speed);
        hint.seen = w.round;
        hint.touched = ++w.memory.assembly_path_clock;
        hint.borrowed_generation = w.memory.assembly_path_generation;
        if (result.turns > 0 && !body.can_move)
            ++result.turns;
        if (result.turns <= 3)
            return result;
    }
    Actor ranged = body;
    ranged.range = range;
    auto arrival = contribution_arrival(w, ranged, anchor, {}, basic_targets);
    if (!arrival.known)
        return {};
    for (const Pos p : reserved)
        if (arrival.at == p) {
            arrival = contribution_arrival(w, ranged, anchor, p, basic_targets);
            if (!arrival.known)
                return {};
        }
    if (arrival.route_length == 0) {
        arrival.route[0] = body.pos;
        arrival.route_length = 1;
    }
    for (int k = 0; k < arrival.route_length; ++k)
        if (!route_tile(w, body, arrival.route[k], reserved))
            return {};
    const auto *hint = remember_path(w, body, anchor, body.pos, range, kind, arrival);
    if (arrival.turns > 0 && !body.can_move)
        ++arrival.turns;
    return hint && arrival.turns <= 3 ? route_view(*hint, arrival.turns) : RouteView{};
}
inline RouteView known_exit(World &w, const Actor &body, const RouteView &entry, Pos anchor,
                            int action_range, std::span<const Camp> threats,
                            std::span<const Pos> reserved) {
    const auto safe = [&](Pos p) {
        for (const auto &camp : threats)
            if (camp.hp > 0 && camp.strength > 0 && distance(p, camp.pos) <= camp.range)
                return false;
        return true;
    };
    const auto legal = [&](Pos p) { return route_tile(w, body, p, reserved, entry.at); };
    const int speed = std::max(1, body.move_speed);
    for (auto &hint : w.memory.assembly_paths) {
        if (!assembly_hint_matches(hint, body.id, body.pos, anchor, entry.at, action_range,
                                   body.move_speed, 1, w.round))
            continue;
        if (!assembly_hint_legal(hint, legal) || !safe(hint.route[hint.length - 1]))
            continue;
        auto result = route_view(hint, (hint.length - 1 + speed - 1) / speed);
        hint.seen = w.round;
        hint.touched = ++w.memory.assembly_path_clock;
        hint.borrowed_generation = w.memory.assembly_path_generation;
        if (result.turns <= 3)
            return result;
    }
    Arrival result;
    result.route[0] = entry.at;
    result.route_length = 1;
    result.at = entry.at;
    if (!legal(result.at))
        return {};
    while (!safe(result.at) && result.route_length < std::min(25, 3 * speed + 1)) {
        if (bc::fuel_remaining() < 42000 || w.round != int(bc::round_number()))
            return {};
        const auto next = assembly_exit_step(result.at, threats, legal,
                                             [&](Pos p) { return w.geo.at(w.geo.home, p); });
        if (!next)
            return {};
        result.at = *next;
        result.route[result.route_length++] = *next;
    }
    result.turns = (result.route_length - 1 + speed - 1) / speed;
    result.known = safe(result.at) && result.turns <= 3;
    const auto *hint = remember_path(w, body, anchor, entry.at, action_range, 1, result);
    return hint ? route_view(*hint, result.turns) : RouteView{};
}
template <class Route> inline bool quiet_route(const World &w, const Route &arrival) {
    const auto route = std::span(arrival.route.data(), arrival.route_length);
    for (Pos at : route)
        if (w.warning_near(at, 4))
            return false;
    for (const auto &enemy : w.enemies)
        if (!assembly_quiet_path(route, enemy, 6))
            return false;
    for (const auto &seen : w.sightings) {
        const int age = w.round - seen.round;
        if (!seen.actor.alive || !combat_detail::recent_sighting(age))
            continue;
        if (std::any_of(w.enemies.begin(), w.enemies.end(),
                        [&](const Actor &a) { return a.id == seen.actor.id; }))
            continue; // Fresh personal observation outranks a remembered origin.
        if (!assembly_quiet_path(route, seen.actor, age + 6))
            return false;
    }
    return true;
}
} // namespace assembly_detail
inline std::optional<AssemblyCandidate> group_assembly_stage(World &w, const Memory &m, int gi,
                                                             double alternative_rate,
                                                             bool alternative_known,
                                                             bool basic_stage) {
    if (!alternative_known || !assembly_detail::observed_group(w, gi) ||
        !assembly_detail::available(w.self) || bc::fuel_remaining() < 56000)
        return std::nullopt;
    if (++w.memory.assembly_path_generation == 0) {
        for (auto &hint : w.memory.assembly_paths)
            hint.borrowed_generation = 0;
        ++w.memory.assembly_path_generation;
    }
    const auto &group = w.geo.groups[gi];
    if (!resource_has_bank(group.gems, w.self.gems))
        return std::nullopt;
    const auto &view = w.groups[gi];
    const Camp *anchor = nullptr;
    for (const auto &camp : view.camps) {
        const int index = w.geo.index(camp.pos);
        if (!w.geo.goal_cache.contains({index, 0}) && !w.geo.route_cache.contains(index))
            continue;
        if (!anchor || camp.hp < anchor->hp || (camp.hp == anchor->hp && camp.id < anchor->id))
            anchor = &camp;
    }
    if (!anchor)
        return std::nullopt; // Main's immutable route hint funds a later
                             // opportunity.
    const int altar = w.altar_distance(anchor->pos), home = w.home_distance(anchor->pos);
    if (altar == unreachable || home == unreachable)
        return std::nullopt;
    std::vector<Camp> awake;
    awake.reserve(3);
    int awake_count = 0;
    for (const auto &live : w.groups)
        if (live.fresh(w.round))
            for (const auto &camp : live.camps)
                if (camp.hp > 0 && camp.awake && camp.strength > 0) {
                    if (awake_count == 32)
                        return std::nullopt;
                    awake.push_back(camp);
                    ++awake_count;
                }
    std::vector<Camp> exit_threats = awake;
    exit_threats.reserve(awake_count + view.camps.size());
    int exit_threat_count = awake_count;
    for (const auto &camp : view.camps)
        if (std::none_of(exit_threats.begin(), exit_threats.begin() + exit_threat_count,
                         [&](const Camp &c) { return c.id == camp.id; })) {
            exit_threats.push_back(camp);
            exit_threats.back().awake = true;
            ++exit_threat_count;
        }
    std::array<const Actor *, 6> available{};
    int count = 1;
    available[0] = &w.self;
    for (const auto &ally : w.allies)
        if (count < 6 && ally.id != w.self.id && assembly_detail::available(ally) &&
            (ally.id > w.self.id || w.matching_claim(ally.id, gi)) &&
            distance(ally.pos, anchor->pos) <=
                assembly_detail::prospective_range(ally, 6) + 3 * std::max(1, ally.move_speed))
            available[count++] = &ally;
    if (count < 1)
        return std::nullopt;
    std::sort(available.begin() + 1, available.begin() + count,
              [&](const Actor *a, const Actor *b) {
                  const bool ac = w.matching_claim(a->id, gi), bc = w.matching_claim(b->id, gi);
                  if (ac != bc)
                      return ac;
                  const int ar = assembly_detail::prospective_range(*a, 6),
                            br = assembly_detail::prospective_range(*b, 6);
                  if (ar != br)
                      return ar > br;
                  return a->id < b->id;
              });
    int exposed_id = w.self.id;
    double durable = w.self.hp / std::max(.01, w.self.camp_mitigation);
    for (int i = 1; i < count; ++i)
        if (available[i]->hp / std::max(.01, available[i]->camp_mitigation) > durable) {
            durable = available[i]->hp / std::max(.01, available[i]->camp_mitigation);
            exposed_id = available[i]->id;
        }
    std::array<assembly_detail::RouteView, 6> arrivals{}, exits{};
    std::vector<CampClearBody> bodies;
    bodies.reserve(count);
    std::array<const Actor *, 6> selected_actual{};
    std::array<AssemblyMember, 6> members{};
    std::array<Pos, 6> reserved{};
    int selected = 0;
    for (int i = 0; i < count && bc::fuel_remaining() >= 47000; ++i) {
        const Actor &actual = *available[i];
        const auto route = assembly_detail::group_arrival(
            w, actual, anchor->pos, std::span(reserved.data(), selected),
            basic_stage || actual.id == exposed_id,
            basic_stage ? std::span<const Camp>(view.camps) : std::span<const Camp>{});
        if (!route.known || !assembly_detail::quiet_route(w, route)) {
            if (i == 0)
                return std::nullopt;
            continue;
        }
        bool known = actual.id == w.self.id;
        double alternative = actual.id == w.self.id ? alternative_rate : 0;
        if (!known) {
            int other = -1;
            Pos target;
            bool bank = false;
            alternative =
                coordination_detail::alternative(w, actual, gi, known, other, target, bank);
        }
        if (!known) {
            if (i == 0)
                return std::nullopt;
            continue;
        }
        const auto exit = assembly_detail::known_exit(
            w, actual, route, anchor->pos,
            basic_stage || actual.id == exposed_id ? actual.range
                                                   : assembly_detail::prospective_range(actual, 6),
            std::span(exit_threats.data(), exit_threat_count),
            std::span(reserved.data(), selected));
        if (!exit.known) {
            if (i == 0)
                return std::nullopt;
            continue;
        }
        const auto reserve = assembly_approach_damage(
            actual, std::span(exit.route.data(), exit.route_length), exit.turns, 0,
            std::span(exit_threats.data(), exit_threat_count));
        if (!reserve)
            return std::nullopt;
        bodies.emplace_back();
        Actor &future = bodies.back().actor;
        future = actual;
        future.pos = route.at;
        future.shield = 0; // Current temporary protection cannot be banked.
        future.completed = false;
        future.can_attack = future.can_cast = true;
        for (auto &spell : future.spells) {
            if (spell.cooldown >= 0)
                spell.cooldown = std::max(0, spell.cooldown - route.turns - 3);
            spell.ready = spell.cooldown == 0;
        }
        const auto index = selected++;
        selected_actual[index] = &actual;
        reserved[index] = route.at;
        arrivals[index] = route;
        exits[index] = exit;
        // The actual kit was projected once into the pre-reserved body slot.
        bodies[index].enemy_reply = *reserve;
        bodies[index].alternative_known = true;
        bodies[index].alternative_value = alternative;
        members[index] = {
            actual.id, route.turns, true,       true, true, true, w.matching_claim(actual.id, gi),
            true,      true,        alternative};
    }
    if (selected < 1 || bc::fuel_remaining() < 46000)
        return std::nullopt;
    for (int i = 0; i < selected; ++i)
        if (!assembly_exit_unreserved(exits[i].route, arrivals[i].at,
                                      std::span(reserved.data(), selected)))
            return std::nullopt; // No promise that a future teammate vacates an escape tile.
    std::array<CampClearMonster, 8> monsters{};
    for (unsigned i = 0; i < view.camps.size(); ++i)
        monsters[i] = {view.camps[i], true};
    // A fully priced sufficient crew is tried first. Smaller Unknown results
    // must not consume the full crew's admission budget or prove necessity.
    // This is a bounded opportunity comparison, not a minimal-crew theorem.
    std::array<int, 3> sizes{selected, 1, std::min(2, selected)};
    int previous_size = -1;
    for (int size : sizes) {
        if (size == previous_size)
            continue;
        previous_size = size;
        if (size == 1 && bc::fuel_remaining() < 62000)
            continue;
        if (bc::fuel_remaining() < 42000)
            break;
        const int floor =
            size < selected ? std::max(44000, int(bc::fuel_remaining()) - 7000) : 32000;
        bool external = false;
        for (int i = 0; i < size; ++i)
            external |= external_camp_collateral(bodies[i].actor, view.camps, w.geo.groups, gi,
                                                 w.groups, w.round);
        if (external)
            continue; // No unpriced collateral wake outside this contract.
        auto priced = bodies;
        int arrival = 0;
        for (int i = 0; i < size; ++i)
            arrival = std::max(arrival, arrivals[i].turns);
        bool approach_known = true;
        for (int i = 0; i < size; ++i) {
            const auto damage = assembly_approach_damage(
                *selected_actual[i], std::span(arrivals[i].route.data(), arrivals[i].route_length),
                arrivals[i].turns, arrival + 3 - arrivals[i].turns,
                std::span(awake.data(), awake_count));
            if (!damage || selected_actual[i]->hp - *damage <= .35 * selected_actual[i]->max_hp) {
                approach_known = false;
                break;
            }
            priced[i].actor.hp -= *damage;
            for (auto &spell : priced[i].actor.spells) {
                if (spell.cooldown >= 0)
                    spell.cooldown = std::max(0, spell.cooldown - arrival + arrivals[i].turns);
                spell.ready = spell.cooldown == 0;
            }
        }
        if (!approach_known)
            continue;
        auto fast = basic_clear_rollout(
            std::span(priced.data(), size), std::span(monsters.data(), view.camps.size()),
            w.self.id, [&] {
                return bc::fuel_remaining() >= static_cast<unsigned>(floor + 3000) &&
                       w.round == int(bc::round_number());
            });
        if (basic_stage && !fast)
            continue; // Unknown here reserves budget for the distinct legal-spell option.
        const auto forecast =
            fast ? std::move(*fast)
                 : rollout_camp_clear(std::span(priced.data(), size),
                                      std::span(monsters.data(), view.camps.size()), w.self.id,
                                      size == selected ? 4096 : 192, [&] {
                                          return bc::fuel_remaining() >=
                                                     static_cast<unsigned>(floor) &&
                                                 w.round == static_cast<int>(bc::round_number());
                                      });
        if (w.round != static_cast<int>(bc::round_number()))
            return std::nullopt;
        if (!forecast.ready)
            continue;
        if (!quiet_fixed_camp_window(w, std::span(priced.data(), size),
                                     int(std::ceil(forecast.ticks)) + arrival + 6))
            continue;

        AssemblyFacts facts;
        facts.group = gi;
        facts.self_id = w.self.id;
        facts.now = w.round;
        facts.horizon = bc::constants::max_rounds;
        facts.fresh_observed = facts.safe_stage = facts.hypothesis_affordable = facts.priced_crew =
            true;
        facts.alternative_known = true;
        facts.alternative_rate = alternative_rate;
        facts.can_move = w.self.can_move;
        facts.reward_once =
            group.gems + (w.round < 600 ? .25 : .24) * score_resource_gold(group.gems, group.gold);
        const int speed = std::max(1, w.self.move_speed);
        const int capture_walk =
            coordination_detail::cached_distance(w, arrivals[0].at, anchor->pos);
        if (capture_walk < 0 || capture_walk == unreachable)
            continue;
        facts.cycle_ticks = forecast.ticks + (capture_walk + speed - 1) / speed +
                            bc::constants::capture_time + 1 + (altar + speed - 1) / speed +
                            tribute_ticks(w.self.gems + group.gems);
        double recovery = 0;
        for (int i = 0; i < size && i < int(forecast.remaining_hp.size()); ++i)
            if (forecast.remaining_hp[i] < .55 * bodies[i].actor.max_hp)
                recovery = std::max(
                    recovery,
                    double((bodies[i].actor.home ? 3 : int(bc::constants::recall_time)) + 2 +
                           (home + std::max(1, bodies[i].actor.move_speed) - 1) /
                               std::max(1, bodies[i].actor.move_speed)));
        facts.cycle_ticks += recovery;
        std::uint64_t signature = assembly_group_signature(
            gi, std::span<const Actor *const>(selected_actual.data(), size), view.camps);
        const auto mix = [&](std::uint64_t value) {
            signature = (signature ^ value) * 1099511628211ULL;
        };
        for (int i = 0; i < size; ++i) {
            mix(w.matching_claim(selected_actual[i]->id, gi));
            mix(arrivals[i].route_length);
            mix(exits[i].route_length);
            for (Pos p : arrivals[i].route) {
                mix(p.x + 1);
                mix(p.y + 1);
            }
            for (Pos p : exits[i].route) {
                mix(p.x + 1);
                mix(p.y + 1);
            }
        }
        facts.unchanged_failure =
            m.assembly_failed_group == gi && m.assembly_failed_signature == signature;
        auto candidate = price_assembly(facts, std::span(members.data(), size));
        if (!candidate.known)
            continue;
        candidate.target = anchor->pos;
        candidate.stage = arrivals[0].at;
        std::copy(arrivals[0].route.begin(), arrivals[0].route.end(), candidate.route.begin());
        candidate.route_length = arrivals[0].route_length;
        candidate.signature = signature;
        candidate.clear_ticks = forecast.ticks;
        std::copy(exits[0].route.begin(), exits[0].route.end(), candidate.exit_route.begin());
        candidate.exit_length = exits[0].route_length;
        candidate.selected_count = size;
        for (int i = 0; i < size; ++i)
            candidate.selected_ids[i] = members[i].id;
        return candidate;
    }
    return std::nullopt;
}
inline std::optional<AssemblyCandidate> group_assembly_candidate(World &w, const Memory &m, int gi,
                                                                 double alternative_rate,
                                                                 bool alternative_known) {
    // At most two actual complete staging itineraries. Each stage invocation
    // owns a fresh path-cache borrow generation; returned candidates own their
    // copied self route. No span survives into the second geometry hypothesis.
    auto basic = group_assembly_stage(w, m, gi, alternative_rate, alternative_known, true);
    auto cast = group_assembly_stage(w, m, gi, alternative_rate, alternative_known, false);
    if (!basic)
        return cast;
    if (!cast)
        return basic;
    // Rates include actual approach, clear, capture, bank, recovery and each
    // helper's known abandoned job. Unquoted alternatives never get free zero.
    return cast->rate > basic->rate ? cast : basic;
}
inline std::optional<AssemblyCandidate> local_assembly_candidate(World &w, const Memory &m, int gi,
                                                                 double alternative_rate,
                                                                 bool alternative_known = true) {
    if (assembly_detail::simple_sleeping(w, gi))
        return singleton_assembly_candidate(w, m, gi, alternative_rate, alternative_known);
    return group_assembly_candidate(w, m, gi, alternative_rate, alternative_known);
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

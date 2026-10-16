#pragma once
#include "resource.h"
#include "solo_bounds.h"
#include "types.h"
#include <span>

namespace tactics {
enum class LocalRole { None, Clear, Tank, Collector, Protector, Split, Observe };
struct CampClearBody {
    Actor actor{};
    double enemy_reply = 0, alternative_value = 0;
    int alternative_group = -1;
    Pos alternative_target{};
    bool alternative_known = false, alternative_bank = false;
};
struct CampClearMonster {
    Camp camp{};
    bool observed = true;
};
struct CampRollout {
    std::vector<int> selected_ids;
    std::vector<double> remaining_hp, damage_taken;
    double ticks = 0, opportunity_cost = 0;
    bool ready = false, complete = false, uncertain = false;
};
namespace coordination_detail {
inline bool damage_spell(const Spell &s) {
    return s.camps && s.amount > 0 && (s.kind == 2 || s.kind == 3 || s.kind == 4);
}
inline bool useful_now(const Actor &a, std::span<const CampClearMonster> monsters) {
    if (!a.alive || a.stunned || a.completed || a.channel != Channel::None)
        return false;
    for (const auto &m : monsters) {
        if (!m.observed || m.camp.hp <= 0)
            continue;
        const int d = distance(a.pos, m.camp.pos);
        if (a.can_attack && a.strength > 0 && d <= a.range)
            return true;
        for (const auto &s : a.spells)
            if (a.can_cast && s.ready && s.kind == 1 && s.self && a.strength > 0 && d <= a.range)
                return true;
        for (const auto &s : a.spells)
            if (a.can_cast && s.ready && damage_spell(s) &&
                d <= s.range + (s.kind == 3 && s.ground ? s.radius : 0))
                return true;
    }
    return false;
}
inline bool essential_help_lost(bool awake, bool locally_ready, bool observed_help_lost) {
    return awake && !locally_ready && observed_help_lost;
}

inline bool finite_body(const CampClearBody &b) {
    const auto &a = b.actor;
    return a.id >= 0 && a.alive && a.channel == Channel::None && !a.stunned &&
           std::isfinite(a.hp) && a.hp > 0 && std::isfinite(a.strength) && a.strength > 0 &&
           std::isfinite(a.camp_mitigation) && a.camp_mitigation > 0 &&
           std::isfinite(b.enemy_reply) && b.enemy_reply >= 0;
}
inline std::array<double, 6> pressure(std::span<const Actor> bodies,
                                      std::span<const CampClearMonster> monsters,
                                      std::span<const double> hp, int self) {
    std::array<double, 6> raw{};
    for (unsigned j = 0; j < monsters.size(); ++j) {
        const auto &m = monsters[j];
        if (hp[j] <= 0)
            continue;
        if (!m.observed) {
            raw[self] += m.camp.strength;
            continue;
        }
        int nearest = unreachable;
        for (const auto &a : bodies)
            nearest = std::min(nearest, distance(a.pos, m.camp.pos));
        if (nearest > m.camp.range)
            continue;
        for (unsigned i = 0; i < bodies.size(); ++i)
            if (distance(bodies[i].pos, m.camp.pos) == nearest)
                raw[i] += m.camp.strength; // Every tie pays a full possible hit.
    }
    return raw;
}
} // namespace coordination_detail

// Bounded local forecast: at most six bodies and 32 living members, with at
// most six rounds per member. No paths, SDK calls, or hypothetical movement.
// One cast/body/round competes with heal/shield; a reset restores one basic.
// Camp responses are charged before the forecasted allied round, deliberately
// allowing enemy/camp interleaving rather than assuming a free combined burst.
inline CampRollout rollout_camp_clear(std::span<const CampClearBody> crew,
                                      std::span<const CampClearMonster> monsters, int self_id,
                                      int max_work = 512) {
    CampRollout out;
    if (crew.empty() || crew.size() > 6 || monsters.size() > 32)
        return out;
    std::array<Actor, 6> bodies{};
    std::array<double, 6> shields{}, injury{}, enemy{};
    std::array<std::array<int, 2>, 6> cooldown{};
    int self = -1;
    for (unsigned i = 0; i < crew.size(); ++i) {
        if (!coordination_detail::finite_body(crew[i]))
            return out;
        bodies[i] = crew[i].actor;
        for (unsigned k = 0; k < i; ++k)
            if (bodies[k].id == bodies[i].id)
                return out;
        self = bodies[i].id == self_id ? static_cast<int>(i) : self;
        shields[i] = std::max(0.0, bodies[i].shield);
        enemy[i] = crew[i].enemy_reply;
        for (int k = 0; k < 2; ++k) {
            const auto &sp = bodies[i].spells[k];
            cooldown[i][k] = sp.cooldown >= 0 ? sp.cooldown : (sp.ready ? 0 : unreachable);
        }
        out.selected_ids.push_back(bodies[i].id);
    }
    if (self < 0)
        return out;
    std::vector<double> hp;
    int living = 0;
    for (const auto &m : monsters) {
        if (!std::isfinite(m.camp.hp) || m.camp.hp < 0 || !std::isfinite(m.camp.strength) ||
            m.camp.strength < 0 || m.camp.range < 0)
            return CampRollout{};
        hp.push_back(m.camp.hp);
        living += m.camp.hp > 0;
        out.uncertain |= !m.observed && m.camp.hp > 0;
    }
    int work = 0;
    bool capped = false;
    auto target_for = [&](const Actor &a, int range) {
        int target = -1;
        double best = 1e30;
        for (unsigned j = 0; j < hp.size(); ++j) {
            if (++work > max_work) {
                capped = true;
                return -1;
            }
            if (hp[j] <= 0 || distance(a.pos, monsters[j].camp.pos) > range)
                continue;
            const double score = hp[j] / std::max(1.0, monsters[j].camp.strength);
            if (score < best ||
                (score == best && (target < 0 || monsters[j].camp.id < monsters[target].camp.id))) {
                best = score;
                target = j;
            }
        }
        return target;
    };
    double total_hp = 0, basic_dps = 0;
    for (const auto &m : monsters)
        total_hp += m.camp.hp;
    for (const auto &body : crew)
        basic_dps += body.actor.strength;
    const int horizon = std::min(
        128,
        std::max(6 * living, 2 + static_cast<int>(std::ceil(total_hp / std::max(1.0, basic_dps)))));
    for (int tick = 0; tick < horizon && living; ++tick) {
        const auto raw = coordination_detail::pressure(std::span(bodies.data(), crew.size()),
                                                       monsters, hp, self);
        // Reserve one real enemy reply separately for every selected body. A
        // larger headcount never divides away either monsters or enemy damage.
        for (unsigned i = 0; i < crew.size(); ++i) {
            auto &a = bodies[i];
            double harm = raw[i] * a.camp_mitigation;
            const double absorbed = std::min(harm, shields[i]);
            shields[i] -= absorbed;
            harm -= absorbed;
            a.hp -= harm;
            injury[i] += harm;
            if (a.hp + shields[i] <= enemy[i] + 1)
                return out;
        }
        bool acted = false;
        for (unsigned i = 0; i < crew.size(); ++i) {
            auto &a = bodies[i];
            const bool basic_ready = tick > 0 || (a.can_attack && !a.completed);
            const bool cast_ready = tick > 0 || (a.can_cast && !a.completed);
            int slot = -1, cast_target = -1, heal_target = -1;
            double cast_value = 0;
            if (cast_ready)
                for (int k = 0; k < 2; ++k) {
                    const auto &sp = a.spells[k];
                    if (cooldown[i][k] != 0 || (tick == 0 && !sp.ready))
                        continue;
                    const int range = sp.range + (sp.kind == 3 && sp.ground ? sp.radius : 0);
                    const int target =
                        coordination_detail::damage_spell(sp) ? target_for(a, range) : -1;
                    double value = target >= 0 ? std::min(hp[target], sp.amount) : 0;
                    if (sp.kind == 1 && target_for(a, a.range) >= 0)
                        value = a.strength; // One extra legal basic after the ordinary basic.
                    if (value > cast_value) {
                        cast_value = value;
                        slot = k;
                        cast_target = target;
                        heal_target = -1;
                    }
                    if ((sp.kind != 5 && sp.kind != 7) || sp.amount <= 0)
                        continue;
                    for (unsigned b = 0; b < crew.size(); ++b) {
                        if ((b == i ? !sp.self : !sp.allies) ||
                            distance(a.pos, bodies[b].pos) > sp.range)
                            continue;
                        const double next = raw[b] * bodies[b].camp_mitigation + enemy[b] + 1;
                        if (bodies[b].hp + shields[b] > next)
                            continue;
                        const double benefit =
                            sp.kind == 5 ? std::min(sp.amount,
                                                    std::max(0.0, bodies[b].max_hp - bodies[b].hp))
                                         : std::max(0.0, sp.amount - shields[b]);
                        if (benefit > 0) {
                            // A necessary survival cast takes precedence over
                            // optional offense. It does not supply both actions.
                            slot = k;
                            cast_target = -1;
                            heal_target = b;
                            cast_value = 1e30;
                        }
                    }
                }
            bool reset = false;
            auto hit = [&](int target, double amount) {
                if (target < 0 || amount <= 0)
                    return;
                acted = true;
                const bool alive = hp[target] > 0;
                hp[target] = std::max(0.0, hp[target] - amount);
                if (alive && hp[target] == 0)
                    --living;
            };
            if (slot >= 0) {
                const auto &sp = a.spells[slot];
                if (heal_target >= 0) {
                    if (sp.kind == 5)
                        bodies[heal_target].hp = std::min(bodies[heal_target].max_hp,
                                                          bodies[heal_target].hp + sp.amount);
                    else
                        shields[heal_target] = std::max(shields[heal_target], sp.amount);
                    acted = true;
                } else if (sp.kind == 1)
                    reset = true;
                else
                    hit(cast_target, sp.amount);
                cooldown[i][slot] = sp.recharge > 0 ? sp.recharge : unreachable;
            }
            // A cast kill never wastes the basic on the dead former target.
            if (basic_ready)
                hit(target_for(a, a.range), a.strength);
            if (reset)
                hit(target_for(a, a.range), a.strength);
            for (int k = 0; k < 2; ++k)
                if (cooldown[i][k] > 0 && cooldown[i][k] != unreachable)
                    --cooldown[i][k];
        }
        ++out.ticks;
        if (capped) {
            out.uncertain = true;
            return out;
        }
        for (unsigned i = 0; i < crew.size(); ++i)
            out.opportunity_cost +=
                crew[i].alternative_known ? std::max(0.0, crew[i].alternative_value) : 0;
        if (!acted) {
            out.uncertain = true; // Approach/expired readiness cannot become free DPS.
            return out;
        }
    }
    if (living) {
        out.uncertain = true; // Horizon exhausted means unknown, not impossible.
        return out;
    }
    for (unsigned i = 0; i < crew.size(); ++i) {
        out.remaining_hp.push_back(bodies[i].hp);
        out.damage_taken.push_back(injury[i]);
    }
    out.complete = true;
    out.ready = !out.uncertain;
    return out;
}

struct LocalAssignment {
    std::vector<int> selected_ids;
    int collector_id = -1, protector_id = -1;
    LocalRole self_role = LocalRole::None;
    bool ready = false, self_selected = false, locally_accepted = false, alternative_known = false,
         uncertain = false, essential_missing = false;
    double alternative_value = 0, mission_value = 0, marginal_value = 0, clear_ticks = 0;
    int alternative_group = -1;
    Pos alternative_target{};
    bool alternative_bank = false;
    CampRollout rollout{};
};
inline bool prefer_local_crew(const CampRollout &current, const CampRollout &next,
                              double current_value, double next_value,
                              bool added_alternatives_known) {
    if (!next.ready)
        return false;
    if (!current.ready)
        return true;
    // Unknown opportunity cost is not zero. A necessary larger crew remains
    // eligible, while optional unpriced crowding cannot displace a feasible job.
    if (next.selected_ids.size() > current.selected_ids.size() && !added_alternatives_known)
        return false;
    return next_value > current_value + 1e-9 ||
           (std::abs(next_value - current_value) <= 1e-9 &&
            next.selected_ids.size() < current.selected_ids.size());
}
inline bool stable_split_order(int self_id, std::span<const int> remaining) {
    return std::any_of(remaining.begin(), remaining.end(),
                       [&](int id) { return id >= 0 && id < self_id; });
}
} // namespace tactics

#ifndef TACTICS_COORDINATION_MODEL_ONLY
#include "combat.h"
namespace tactics {
namespace coordination_detail {
inline int cached_distance(const World &w, Pos from, Pos target) {
    if (!w.geo.valid(from) || !w.geo.valid(target))
        return unreachable;
    if (from == target)
        return 0;
    if (auto it = w.geo.goal_cache.find({w.geo.index(target), 0}); it != w.geo.goal_cache.end())
        return w.geo.at(it->second, from);
    if (auto it = w.geo.route_cache.find(w.geo.index(from)); it != w.geo.route_cache.end())
        return w.geo.at(it->second, target);
    if (auto it = w.geo.route_cache.find(w.geo.index(target)); it != w.geo.route_cache.end())
        return w.geo.at(it->second, from);
    return -1; // No field construction and no Euclidean reachability certificate.
}
inline double alternative(const World &w, const Actor &a, int excluded, bool &known,
                          int &selected_group, Pos &selected_target, bool &selected_bank) {
    double best = 0;
    known = false;
    const int altar = w.geo.at(w.geo.nearest_altar, a.pos);
    if (a.gems > 0 && altar != unreachable) {
        known = true;
        best = a.gems / std::max(1.0, static_cast<double>(altar / std::max(1, a.move_speed) +
                                                          tribute_ticks(a.gems) + 1));
        int nearest = unreachable;
        for (unsigned i = 0; i < w.geo.altars.size(); ++i) {
            const int d = w.geo.at(w.geo.altar_fields[i], a.pos);
            if (d < nearest) {
                nearest = d;
                selected_target = w.geo.altars[i];
            }
        }
        selected_group = -1;
        selected_bank = true;
    }
    int inspected = 0;
    // The scan does no native work; at most two cached reachable alternatives
    // receive a cycle value. An absent route remains unknown, never zero value.
    for (unsigned gi = 0; gi < w.geo.groups.size() && inspected < 2; ++gi) {
        if (static_cast<int>(gi) == excluded || w.geo.groups[gi].spawns.empty())
            continue;
        const auto &g = w.geo.groups[gi];
        const auto &v = w.groups[gi];
        const auto purpose = resource_job_purpose(
            g.gems, a.gems, w.geo.monolith_only,
            v.fresh(w.round) && v.state == Lifecycle::Reward && w.on_group(gi, a.pos));
        if (purpose == ResourcePurpose::Ineligible || purpose == ResourcePurpose::MonolithFallback)
            continue; // An unpriced gold detour is not a scored abandoned job.
        if (!v.fresh(w.round) || (v.state != Lifecycle::Alive && v.state != Lifecycle::Reward))
            continue;
        const Pos at = g.spawns.front().pos;
        const int d = cached_distance(w, a.pos, at);
        if (d < 0 || d == unreachable)
            continue;
        ++inspected;
        const int bank = w.geo.at(w.geo.nearest_altar, at);
        if ((g.gems || a.gems) && bank == unreachable)
            continue;
        if (v.state != Lifecycle::Reward) {
            bool complete = true;
            for (const auto &spawn : g.spawns)
                if (std::find(v.known_dead.begin(), v.known_dead.end(), spawn.id) ==
                        v.known_dead.end() &&
                    std::none_of(v.camps.begin(), v.camps.end(),
                                 [&](const Camp &c) { return c.id == spawn.id; }))
                    complete = false;
            if (!complete)
                continue; // A wandering visible member does not certify a cheap solo job.
        }
        double hp = 0, exposure = 0;
        for (const auto &c : v.camps) {
            hp += c.hp;
            exposure += c.strength;
        }
        const double clear = std::ceil(hp / std::max(1.0, a.strength));
        double enemy_reply = 0;
        for (const auto &e : w.enemies)
            enemy_reply += combat_detail::long_window_reply_upper(e, e.pos, at, 1);
        for (const auto &sight : w.sightings) {
            const int age = w.round - sight.round;
            bool visible = false;
            for (const auto &e : w.enemies)
                visible |= e.id == sight.actor.id;
            if (!visible && combat_detail::recent_sighting(age))
                enemy_reply += combat_detail::coarse_remembered_reply(sight.actor, age, at, 1);
        }
        const double harm = clear * exposure * a.camp_mitigation + enemy_reply * a.mitigation;
        if ((hp > 0 && v.camps.empty()) || harm + 1 >= a.hp + a.shield)
            continue; // Alternative must be affordable, not merely a rich icon.
        const double time = d / std::max(1, a.move_speed) + clear + 6 +
                            ((g.gems || a.gems) ? bank + tribute_ticks(a.gems + g.gems) : 0);
        known = true;
        const double value =
            (g.gems + (w.round < 600 ? .25 : .24) * score_resource_gold(g.gems, g.gold) + a.gems) /
            std::max(1.0, time);
        if (value > best) {
            best = value;
            selected_group = gi;
            selected_target = at;
            selected_bank = false;
        }
    }
    return best;
}
} // namespace coordination_detail
inline LocalAssignment propose_local_assignment(World &w, int group) {
    LocalAssignment out;
    if (bc::fuel_remaining() < 48000 || w.round != static_cast<int>(bc::round_number())) {
        out.uncertain = true;
        return out;
    }
    if (group < 0 || group >= static_cast<int>(w.groups.size()) ||
        group >= static_cast<int>(w.geo.groups.size()))
        return out;
    const auto &g = w.geo.groups[group];
    const auto &v = w.groups[group];
    std::vector<CampClearMonster> monsters;
    if (!(v.fresh(w.round) && v.state == Lifecycle::Reward))
        for (const auto &spawn : g.spawns) {
            if (v.fresh(w.round) &&
                std::find(v.known_dead.begin(), v.known_dead.end(), spawn.id) != v.known_dead.end())
                continue;
            auto seen = std::find_if(v.camps.begin(), v.camps.end(),
                                     [&](const Camp &c) { return c.id == spawn.id; });
            if (v.fresh(w.round) && seen != v.camps.end())
                monsters.push_back({*seen, true});
            else {
                Camp c;
                c.id = spawn.id;
                c.pos = spawn.pos;
                c.hp = spawn.hp;
                c.strength = spawn.strength;
                monsters.push_back({c, false});
            }
        }
    std::vector<CampClearBody> crew;
    auto add = [&](const Actor &a) {
        CampClearBody b;
        b.actor = a;
        double raw = 0;
        for (const auto &e : w.enemies)
            raw += combat_detail::long_window_reply_upper(e, e.pos, a.pos, 1);
        for (const auto &sight : w.sightings) {
            const int age = w.round - sight.round;
            if (!combat_detail::recent_sighting(age))
                continue;
            bool current = false;
            for (const auto &e : w.enemies)
                current |= e.id == sight.actor.id;
            if (!current)
                raw += combat_detail::coarse_remembered_reply(sight.actor, age, a.pos, 1);
        }
        b.enemy_reply = raw * a.mitigation; // Shield is a single shared budget in the rollout.
        b.alternative_value =
            coordination_detail::alternative(w, a, group, b.alternative_known, b.alternative_group,
                                             b.alternative_target, b.alternative_bank);
        crew.push_back(b);
    };
    add(w.self);
    for (const auto &a : w.allies)
        if (a.id != w.self.id && w.matching_claim(a.id, group) &&
            coordination_detail::useful_now(a, monsters) && crew.size() < 6)
            add(a);
    out.alternative_value = crew.front().alternative_value;
    out.alternative_known = crew.front().alternative_known;
    out.alternative_group = crew.front().alternative_group;
    out.alternative_target = crew.front().alternative_target;
    out.alternative_bank = crew.front().alternative_bank;
    if (w.round != static_cast<int>(bc::round_number())) {
        out.uncertain = true;
        return out;
    }
    const double reward = g.gems + (w.round < 600 ? .25 : .24) * g.gold;
    // Required cached crew/alternative setup has its own bounded cost. Reserve
    // the unchanged rollout slice AFTER that setup; otherwise it can consume
    // the entire slice before the first physically present pair is considered.
    const int planning_floor = std::max(32000, static_cast<int>(bc::fuel_remaining()) - 12000);
    auto consider = [&](const std::vector<CampClearBody> &selected) {
        if (bc::fuel_remaining() < static_cast<unsigned>(planning_floor + 6000)) {
            out.uncertain = true;
            return;
        }
        auto r = rollout_camp_clear(selected, monsters, w.self.id, 48);
        if (!r.ready) {
            out.uncertain |= r.uncertain;
            return;
        }
        // Team reward is priced once. Extra clearers are justified by the
        // secured-time improvement minus their actual known abandoned job.
        const double mission = reward / std::max(1.0, r.ticks + 6);
        const double value = mission - r.opportunity_cost / std::max(1.0, r.ticks + 6);
        bool added_known = true;
        for (const auto &b : selected)
            if (b.actor.id != w.self.id &&
                std::find(out.selected_ids.begin(), out.selected_ids.end(), b.actor.id) ==
                    out.selected_ids.end())
                added_known &= b.alternative_known;
        if (prefer_local_crew(out.rollout, r, out.marginal_value, value, added_known)) {
            out.ready = true;
            out.selected_ids = r.selected_ids;
            out.mission_value = mission;
            out.marginal_value = value;
            out.clear_ticks = r.ticks;
            out.rollout = std::move(r);
        }
    };
    // The current stationary singleton plan may have a sound optimistic
    // impossibility certificate. Do not spend its entire local budget rerunning
    // that failed solo before pricing the physically present, claimed helper.
    // Unknown/capped forecasts still run normally; no future helper grants DPS.
    const bool solo_impossible =
        monsters.size() == 1 && monsters.front().observed &&
        optimistic_solo_impossibility(w.self, monsters.front().camp, w.self.shield).impossible;
    if (!solo_impossible)
        consider({crew.front()});
    for (unsigned i = 1; i < crew.size(); ++i)
        consider({crew.front(), crew[i]});
    if (crew.size() > 2)
        consider(crew);
    out.self_selected = out.ready;
    if (out.ready && crew.size() > 1 && out.alternative_known &&
        bc::fuel_remaining() >= static_cast<unsigned>(planning_floor + 6000)) {
        std::vector<CampClearBody> remaining(crew.begin() + 1, crew.end());
        auto without = rollout_camp_clear(remaining, monsters, remaining.front().actor.id, 48);
        const double other_value = reward / std::max(1.0, without.ticks + 6) -
                                   without.opportunity_cost / std::max(1.0, without.ticks + 6);
        if (without.ready && stable_split_order(w.self.id, without.selected_ids) &&
            other_value + out.alternative_value > out.marginal_value) {
            out.selected_ids = without.selected_ids;
            out.self_selected = false;
            out.rollout = std::move(without);
            out.clear_ticks = out.rollout.ticks;
            out.self_role = LocalRole::Split;
        }
    }
    out.locally_accepted = out.ready && (!out.self_selected || monsters.empty() ||
                                         coordination_detail::useful_now(w.self, monsters));
    if (out.self_selected) {
        out.self_role = out.locally_accepted ? LocalRole::Clear : LocalRole::Observe;
        for (unsigned i = 0; i < out.rollout.selected_ids.size(); ++i)
            if (out.rollout.selected_ids[i] == w.self.id && i < out.rollout.damage_taken.size() &&
                out.rollout.damage_taken[i] > 0 && out.locally_accepted)
                out.self_role = LocalRole::Tank;
    }
    // Existing physical holders win over promises of a later handoff. Otherwise
    // select the earliest cached feasible occupant, with stable IDs for ties.
    int best_eta = unreachable;
    std::vector<const Actor *> role_candidates{&w.self};
    for (const auto &a : w.allies)
        if (a.id != w.self.id && (w.on_group(group, a.pos) || w.matching_claim(a.id, group)))
            role_candidates.push_back(&a);
    for (const auto *candidate : role_candidates) {
        const auto &a = *candidate;
        if (!a.alive || a.channel != Channel::None || a.stunned || a.health_fraction() < .35)
            continue;
        int eta = w.on_group(group, a.pos) ? 0 : unreachable;
        if (eta != 0)
            for (const auto &s : g.spawns) {
                const int d = coordination_detail::cached_distance(w, a.pos, s.pos);
                if (d >= 0)
                    eta = std::min(eta, d);
            }
        if (eta < best_eta || (eta == best_eta && eta != unreachable &&
                               (out.collector_id < 0 || a.id < out.collector_id))) {
            best_eta = eta;
            out.collector_id = a.id;
        }
    }
    if (out.collector_id == w.self.id && monsters.empty())
        out.self_role = LocalRole::Collector;
    const Actor *collector = nullptr;
    for (const auto *a : role_candidates)
        if (a->id == out.collector_id)
            collector = a;
    if (collector && !w.enemies.empty())
        for (const auto &b : crew) {
            const auto &a = b.actor;
            if (a.id == collector->id || !a.can_cast || a.completed || a.stunned)
                continue;
            bool useful = false;
            for (const auto &s : a.spells) {
                if (!s.ready)
                    continue;
                if ((s.kind == 5 || s.kind == 7) && s.allies &&
                    distance(a.pos, collector->pos) <= s.range)
                    for (const auto &enemy : w.enemies)
                        useful |=
                            distance(enemy.pos, collector->pos) <= enemy.range + enemy.move_speed;
                if (s.kind == 4 && s.enemies)
                    for (const auto &enemy : w.enemies)
                        useful |=
                            distance(a.pos, enemy.pos) <= s.range &&
                            distance(enemy.pos, collector->pos) <= enemy.range + enemy.move_speed;
            }
            if (useful && (out.protector_id < 0 || a.id < out.protector_id))
                out.protector_id = a.id;
        }
    if (out.protector_id == w.self.id)
        out.self_role = LocalRole::Protector;
    bool awake = false, lost_local_help = false;
    for (const auto &m : monsters)
        awake |= m.observed && m.camp.hp > 0 && m.camp.awake;
    for (const auto &a : w.allies)
        if (a.id != w.self.id && w.matching_claim(a.id, group) &&
            (!a.alive || a.channel != Channel::None || a.stunned ||
             !coordination_detail::useful_now(a, monsters)))
            lost_local_help = true;
    // Only personally observed loss of an intended local participant is an
    // essential-role loss. A hidden/distant claim is not proof of death/arrival.
    out.essential_missing =
        coordination_detail::essential_help_lost(awake, out.ready, lost_local_help);
    return out;
}

// A local slot proposal, not an assertion of future simultaneous formation.
// The gateway and fresh next-reply check remain responsible for actual movement.
// This function performs only arithmetic and cached packed-buffer lookups.
inline std::optional<Pos> squad_position(const World &w, const LocalAssignment &assignment,
                                         int group) {
    if (!w.self.alive || !w.self.can_move || w.self.channel != Channel::None || group < 0 ||
        group >= static_cast<int>(w.geo.groups.size()) ||
        group >= static_cast<int>(w.groups.size()) || w.occupied_bytes.empty())
        return std::nullopt;
    const auto &g = w.geo.groups[group];
    if (g.spawns.empty())
        return std::nullopt;
    const Actor *collector = nullptr;
    if (assignment.collector_id == w.self.id)
        collector = &w.self;
    for (const auto &a : w.allies)
        if (a.id == assignment.collector_id && a.alive)
            collector = &a;
    Pos objective = g.spawns.front().pos;
    for (const auto &s : g.spawns)
        if (distance(w.self.pos, s.pos) < distance(w.self.pos, objective))
            objective = s.pos;
    std::vector<int> ids = assignment.selected_ids;
    std::sort(ids.begin(), ids.end());
    const auto own = std::find(ids.begin(), ids.end(), w.self.id);
    const int rank =
        own == ids.end() ? std::max(0, w.self_index) : static_cast<int>(own - ids.begin());
    constexpr std::array<Pos, 8> offsets{
        {{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}}};
    const Pos slot{objective.x + offsets[rank % 8].x, objective.y + offsets[rank % 8].y};
    auto score = [&](Pos p) {
        double result = 0;
        bool camp_useful = false;
        for (const auto &c : w.groups[group].camps)
            if (c.hp > 0) {
                camp_useful |= distance(p, c.pos) <= w.self.range;
                for (const auto &s : w.self.spells)
                    camp_useful |= s.ready && coordination_detail::damage_spell(s) &&
                                   distance(p, c.pos) <= s.range;
            }
        result += camp_useful ? 20 : -2 * distance(p, objective);
        if (assignment.self_role == LocalRole::Collector)
            result += w.on_group(group, p) ? 30 : -3 * distance(p, objective);
        if (collector && collector->id != w.self.id) {
            const int d = distance(p, collector->pos);
            if (assignment.self_role == LocalRole::Protector) {
                bool useful = false;
                for (const auto &s : w.self.spells)
                    if (s.ready && s.allies && (s.kind == 5 || s.kind == 7))
                        useful |= d <= s.range;
                result += useful ? 15 : -2 * d;
            }
            // Preserve the carrier's current exit neighborhood rather than
            // stepping into its only open nearby tile to complete a formation.
            if (d <= 1)
                result -= 2;
        }
        const int home = w.geo.at(w.geo.home, p);
        const int current_home = w.geo.at(w.geo.home, w.self.pos);
        if (home == unreachable)
            result -= 100;
        else if (current_home != unreachable)
            result += std::clamp(current_home - home, -2, 2);
        for (const auto &e : w.enemies) {
            if (!e.alive)
                continue;
            result -= combat_detail::long_window_reply_upper(e, e.pos, p, 1) * w.self.mitigation /
                      std::max(1.0, w.self.hp) * 20;
            for (const auto &s : e.spells)
                if (s.kind == 3 && s.radius > 0 && combat_detail::plausible_ready(s, 1) &&
                    distance(e.pos, p) <= s.range + s.radius + e.move_speed)
                    for (const auto &a : w.allies)
                        if (a.alive && a.id != w.self.id)
                            result -= std::max(0, 2 * s.radius + 1 - distance(p, a.pos)) * 3;
        }
        result -= distance(p, slot) * .25; // Stable distinct preference, never a hard wall.
        return result;
    };
    const double staying = score(w.self.pos);
    double best = staying;
    std::optional<Pos> destination;
    for (auto delta : offsets) {
        Pos p{w.self.pos.x + delta.x, w.self.pos.y + delta.y};
        if (!w.geo.valid(p) || packed_bit(w.geo.terrain, w.geo.index(p)) ||
            packed_bit(w.occupied_bytes, w.geo.index(p)) ||
            (w.memory.blocked_round == w.round && w.memory.blocked_tile == p))
            continue;
        const double value = score(p);
        if (value > best + .01) {
            best = value;
            destination = p;
        }
    }
    return destination;
}
} // namespace tactics
#endif

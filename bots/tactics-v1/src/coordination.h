#pragma once
#include "camp_actions.h"
#include "camp_basic.h"
#include "camp_collateral.h"
#include "farm_readiness.h"
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
    ClearProofKind proof = ClearProofKind::None;
};
template <class Budget = CampBasicBudget>
inline std::optional<CampRollout> basic_clear_rollout(std::span<const CampClearBody> crew,
                                                      std::span<const CampClearMonster> monsters,
                                                      int self_id, Budget funded = {}) {
    if (!funded() || crew.size() > 6 || monsters.size() > 8)
        return std::nullopt;
    std::array<BasicCampBody, 6> bodies{};
    std::array<BasicCampMonster, 8> camps{};
    for (unsigned i = 0; i < crew.size(); ++i) {
        if (crew[i].alternative_known && !std::isfinite(crew[i].alternative_value))
            return std::nullopt;
        bodies[i] = {&crew[i].actor, crew[i].enemy_reply};
    }
    for (unsigned i = 0; i < monsters.size(); ++i)
        camps[i] = {&monsters[i].camp, monsters[i].observed};
    const auto proof =
        sufficient_basic_clear(std::span(bodies.data(), crew.size()),
                               std::span(camps.data(), monsters.size()), self_id, funded);
    if (!proof.ready)
        return std::nullopt;
    CampRollout out;
    out.ready = out.complete = true;
    out.proof = ClearProofKind::BasicOnly;
    out.ticks = proof.ticks;
    out.selected_ids.assign(proof.selected_ids.begin(), proof.selected_ids.begin() + proof.count);
    out.remaining_hp.assign(proof.remaining_hp.begin(), proof.remaining_hp.begin() + proof.count);
    out.damage_taken.assign(proof.damage_taken.begin(), proof.damage_taken.begin() + proof.count);
    for (const auto &body : crew)
        if (body.alternative_known)
            out.opportunity_cost += std::max(0.0, body.alternative_value) * proof.ticks;
    return out;
}
namespace coordination_detail {
inline bool damage_spell(const Spell &s) {
    return camp_damage_ability(s);
}
inline bool useful_now(const Actor &a, std::span<const CampClearMonster> monsters,
                       bool exclusive_allowed = true) {
    for (const auto &m : monsters) {
        if (!m.observed || m.camp.hp <= 0)
            continue;
        if (current_camp_contribution(a, std::span(&m.camp, 1), exclusive_allowed).ready)
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

// Bounded local forecast: at most six bodies, 32 living members and 128 owner
// opportunities. No paths, SDK calls, or hypothetical movement.
// One cast/body/round competes with heal/shield; a reset restores one basic.
// Current HP includes this round's camp phase. Later phases attack the actual
// nearest body (every distance tie), with only explicitly modeled control skipped.
struct CampRolloutBudget {
    bool operator()() const {
        return true;
    }
};
template <class Budget = CampRolloutBudget>
inline CampRollout rollout_camp_clear(std::span<const CampClearBody> crew,
                                      std::span<const CampClearMonster> monsters, int self_id,
                                      int max_work = 512, Budget funded = {}) {
    CampRollout out;
    bool capped = false;
    int work = 0;
    const auto step = [&] {
        if (capped || ++work > max_work || !funded()) {
            capped = true;
            out.uncertain = true;
            return false;
        }
        return true;
    };
    if (!step() || crew.empty() || crew.size() > 6 || monsters.size() > 32)
        return out;
    std::array<Actor, 6> bodies{};
    std::array<double, 6> injury{}, enemy{};
    std::array<int, 6> shield_ticks{};
    std::array<std::array<int, 2>, 6> cooldown{};
    int self = -1;
    for (unsigned i = 0; i < crew.size(); ++i) {
        if (!step() || !coordination_detail::finite_body(crew[i]))
            return out;
        bodies[i] = crew[i].actor;
        for (unsigned j = 0; j < i; ++j)
            if (bodies[i].id == bodies[j].id)
                return out;
        self = bodies[i].id == self_id ? static_cast<int>(i) : self;
        // Native camp phases precede champion-start zero-timer expiry. A
        // personally observed shield with D remaining owner-end ticks therefore
        // covers D future camp phases. Unknown/zero duration supplies no credit.
        if (std::isfinite(bodies[i].shield) && bodies[i].shield > 0 && bodies[i].shield_ticks > 0)
            shield_ticks[i] = bodies[i].shield_ticks;
        else
            bodies[i].shield = 0;
        enemy[i] = crew[i].enemy_reply;
        if (bodies[i].hp <= enemy[i] + .25 * bodies[i].max_hp + 1) {
            out.uncertain = true;
            return out;
        }
        for (int slot = 0; slot < 2; ++slot) {
            const auto &spell = bodies[i].spells[slot];
            cooldown[i][slot] =
                spell.cooldown >= 0 ? spell.cooldown : (spell.ready ? 0 : unreachable);
        }
        out.selected_ids.push_back(bodies[i].id);
    }
    if (self < 0)
        return out;
    std::vector<Camp> camps;
    std::vector<int> control(monsters.size());
    int living = 0;
    for (const auto &monster : monsters) {
        if (!step() || !std::isfinite(monster.camp.hp) || monster.camp.hp < 0 ||
            !std::isfinite(monster.camp.strength) || monster.camp.strength < 0 ||
            monster.camp.range < 0)
            return out;
        camps.push_back(monster.camp);
        living += monster.camp.hp > 0;
        out.uncertain |= !monster.observed && monster.camp.hp > 0;
    }
    if (out.uncertain)
        return out;
    const auto fail_health = [&] {
        // This bounded policy may omit useful movement, future purchases or
        // kill-triggered cooldown resets. Failure is never a global necessity
        // proof; a larger positively certified coalition may still be useful.
        out.uncertain = true;
    };
    for (int tick = 0; tick < 128 && living; ++tick) {
        if (!step())
            return out;
        if (tick > 0) {
            for (unsigned i = 0; i < crew.size(); ++i) {
                if (shield_ticks[i] <= 0)
                    bodies[i].shield = 0;
                else
                    --shield_ticks[i];
            }
            // Current HP already includes this round's camp phase. A new
            // first hit cannot incur an extra pre-hit monster response.
            for (unsigned j = 0; j < camps.size(); ++j) {
                if (!step())
                    return out;
                auto &camp = camps[j];
                if (control[j] > 0) {
                    --control[j];
                    continue;
                }
                if (camp.hp <= 0 || camp.strength <= 0)
                    continue;
                int nearest = unreachable;
                for (unsigned i = 0; i < crew.size(); ++i)
                    nearest = std::min(nearest, distance(bodies[i].pos, camp.pos));
                if (nearest > camp.range)
                    continue;
                for (unsigned i = 0; i < crew.size(); ++i) {
                    auto &body = bodies[i];
                    if (distance(body.pos, camp.pos) != nearest)
                        continue;
                    double harm = camp.strength * body.camp_mitigation;
                    const double absorbed = std::min(harm, body.shield);
                    body.shield -= absorbed;
                    harm -= absorbed;
                    body.hp -= harm;
                    injury[i] += harm;
                    // Native Ren returns 0.2Focus to each actual attacking
                    // camp. No unverified Monster multiplier is added here.
                    if (body.type == 9 && harm > 0 && camp.hp > 0) {
                        const double before = camp.hp;
                        camp.hp = std::max(0.0, camp.hp - .2 * body.focus);
                        if (before > 0 && camp.hp == 0)
                            --living;
                    }
                    if (body.hp + body.shield <= enemy[i] + .25 * body.max_hp + 1) {
                        fail_health();
                        return out;
                    }
                }
            }
        }
        if (!living) {
            ++out.ticks; // A real camp-phase retaliation kill precedes this turn.
            break;
        }
        for (unsigned i = 0; i < crew.size(); ++i) {
            if (!step())
                return out;
            auto &body = bodies[i];
            if (tick > 0) {
                body.completed = false;
                body.can_attack = body.can_cast = true;
                for (int slot = 0; slot < 2; ++slot)
                    body.spells[slot].ready = cooldown[i][slot] == 0;
            }
            // One ordinary basic, at most one successful cast, and only the
            // basic restored by that cast. Live continuation uses this selector.
            for (int action_index = 0; action_index < 3 && living; ++action_index) {
                if (!step())
                    return out;
                Action action = stationary_camp_support(
                    body, std::span<const Actor>(bodies.data(), crew.size()), camps, true, step);
                if (action.kind == Kind::None)
                    action = stationary_camp_action(body, camps, true, step);
                if (capped)
                    return out;
                if (action.kind == Kind::None)
                    break;
                if ((action.kind == Kind::CastSelf || action.kind == Kind::CastChampion) &&
                    action.slot >= 0 && body.spells[action.slot].kind != 1) {
                    const auto &spell = body.spells[action.slot];
                    for (unsigned target = 0; target < crew.size(); ++target)
                        if (bodies[target].id == action.target) {
                            if (spell.kind == 5)
                                bodies[target].hp = std::min(bodies[target].max_hp,
                                                             bodies[target].hp + spell.amount);
                            else if (spell.kind == 7 && spell.duration > 0) {
                                bodies[target].shield =
                                    std::max(bodies[target].shield, spell.amount);
                                shield_ticks[target] = spell.duration;
                            }
                        }
                } else if (action.kind == Kind::CastSelf) {
                    body.can_attack = true;
                    if (body.type == 7)
                        body.enhanced = true;
                } else {
                    for (unsigned j = 0; j < camps.size(); ++j) {
                        if (!step())
                            return out;
                        auto &camp = camps[j];
                        const double amount = camp_action_damage(body, action, camps, camp);
                        if (amount <= 0)
                            continue;
                        control[j] =
                            std::max(control[j], camp_action_control(body, action, camps, camp));
                        const double before = camp.hp;
                        camp.hp = std::max(0.0, camp.hp - amount);
                        if (before > 0 && camp.hp == 0)
                            --living;
                    }
                }
                if (action.kind == Kind::BasicCamp) {
                    body.can_attack = false;
                    body.enhanced = false;
                } else {
                    body.can_cast = false;
                    const auto &spell = body.spells[action.slot];
                    cooldown[i][action.slot] = spell.recharge > 0 ? spell.recharge : unreachable;
                    body.spells[action.slot].ready = false;
                }
            }
            for (int slot = 0; slot < 2; ++slot)
                if (cooldown[i][slot] > 0 && cooldown[i][slot] != unreachable)
                    --cooldown[i][slot];
        }
        ++out.ticks;
        for (unsigned i = 0; i < crew.size(); ++i)
            out.opportunity_cost +=
                crew[i].alternative_known ? std::max(0.0, crew[i].alternative_value) : 0;
        // Spent current permissions and known cooldown waits may consume real
        // owner turns. No action this tick does not prove a future clear impossible.
    }
    if (living || capped || !funded()) {
        out.uncertain = true;
        return out;
    }
    for (unsigned i = 0; i < crew.size(); ++i) {
        out.remaining_hp.push_back(bodies[i].hp);
        out.damage_taken.push_back(injury[i]);
    }
    out.complete = out.ready = true;
    out.proof = ClearProofKind::DetailedBundle;
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
inline bool current_crew_support_actionable(const Actor &self, std::span<const Actor> crew,
                                            std::span<const Camp> camps, bool exclusive_allowed) {
    return stationary_camp_support(self, crew, camps, exclusive_allowed).kind != Kind::None;
}
// Name only the freshly certified current physical crew. Proposal metadata
// becomes an active mission only after the ordinary action gateway accepts it.
inline bool name_current_crew(Mission &job, const LocalAssignment &assignment, int self_id) {
    if (!assignment.ready || !assignment.self_selected || !assignment.locally_accepted ||
        assignment.rollout.proof == ClearProofKind::None || assignment.selected_ids.empty() ||
        assignment.selected_ids.size() > 6)
        return false;
    bool self = false;
    for (unsigned i = 0; i < assignment.selected_ids.size(); ++i) {
        const int id = assignment.selected_ids[i];
        if (id < 0)
            return false;
        self |= id == self_id;
        for (unsigned j = 0; j < i; ++j)
            if (assignment.selected_ids[j] == id)
                return false;
    }
    if (!self)
        return false;
    job.assembly_count = assignment.selected_ids.size();
    std::copy(assignment.selected_ids.begin(), assignment.selected_ids.end(),
              job.assembly_ids.begin());
    job.assembly_anchor =
        *std::min_element(assignment.selected_ids.begin(), assignment.selected_ids.end());
    job.assembly_helper = -1;
    for (int id : assignment.selected_ids)
        if (id != self_id && (job.assembly_helper < 0 || id < job.assembly_helper))
            job.assembly_helper = id;
    return true;
}
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
    const int speed = std::max(1, a.move_speed);
    const auto walk_ticks = [speed](int steps) { return (steps + speed - 1) / speed; };
    const int altar = w.geo.at(w.geo.nearest_altar, a.pos);
    if (a.gems > 0 && altar != unreachable) {
        known = true;
        best = a.gems /
               std::max(1.0, static_cast<double>(walk_ticks(altar) + tribute_ticks(a.gems) + 1));
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
    int priced = 0, work = 0;
    constexpr int max_scan_work = 256;
    // Bound both rejected rows and nested member/threat inspection. Only a
    // fully priced positive alternative consumes one of the two useful slots;
    // two rich but unpriceable icons must not hide a later real task. No route
    // is constructed here. Exhausting the scan never proves a free alternative.
    for (unsigned gi = 0; gi < w.geo.groups.size() && priced < 2 && work < max_scan_work; ++gi) {
        ++work;
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
        const int bank = w.geo.at(w.geo.nearest_altar, at);
        if ((g.gems || a.gems) && bank == unreachable)
            continue;
        const std::size_t member_work =
            g.spawns.size() * (v.known_dead.size() + v.camps.size() + 1) + v.camps.size();
        const std::size_t threat_work =
            w.enemies.size() + w.sightings.size() * (w.enemies.size() + 1);
        if (member_work + threat_work > std::size_t(max_scan_work - work))
            continue; // A costly unresolved row need not hide a later cheap one.
        work += int(member_work + threat_work);
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
        const double time =
            walk_ticks(d) + clear + 6 +
            ((g.gems || a.gems) ? walk_ticks(bank) + tribute_ticks(a.gems + g.gems) : 0);
        const double value =
            (g.gems + (w.round < 600 ? .25 : .24) * score_resource_gold(g.gems, g.gold) + a.gems) /
            std::max(1.0, time);
        if (!std::isfinite(value) || value <= 0)
            continue;
        ++priced;
        known = true;
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
inline bool quiet_fixed_camp_window(const World &w, std::span<const CampClearBody> selected,
                                    int horizon) {
    for (const auto &enemy : w.enemies)
        if (enemy.alive)
            for (const auto &body : selected)
                if (distance(enemy.pos, body.actor.pos) <= camp_enemy_contact(enemy, horizon))
                    return false;
    for (const auto &seen : w.sightings) {
        const int age = w.round - seen.round;
        if (!seen.actor.alive || !combat_detail::recent_sighting(age))
            continue;
        bool visible = false;
        for (const auto &enemy : w.enemies)
            visible |= enemy.id == seen.actor.id;
        if (!visible)
            for (const auto &body : selected)
                if (distance(seen.actor.pos, body.actor.pos) <=
                    camp_enemy_contact(seen.actor, horizon + age))
                    return false;
    }
    return true;
}
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
    const auto &accepted = w.memory.mission;
    const bool named_entry = (accepted.assembly_pending || accepted.phase == Phase::Clear) &&
                             accepted.group == group && accepted.assembly_count > 0 &&
                             w.round < accepted.expiry;
    auto add = [&](const Actor &a) {
        CampClearBody b;
        b.actor = a;
        const bool exclusive_allowed =
            a.id == w.self.id ? w.memory.moved_round != w.round : a.can_move;
        for (auto &spell : b.actor.spells)
            if (spell.exclusive && !exclusive_allowed && spell.ready) {
                spell.ready = false;
                spell.cooldown = std::max(1, spell.cooldown);
            }
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
        if (named_entry) {
            // This is the already accepted current job's safety certificate,
            // not a new helper purchase or a free-zero alternative assumption.
            b.alternative_known = true;
        } else
            b.alternative_value = coordination_detail::alternative(
                w, a, group, b.alternative_known, b.alternative_group, b.alternative_target,
                b.alternative_bank);
        crew.push_back(b);
    };
    const auto named_member = [&](int id) {
        return named_entry &&
               std::find(accepted.assembly_ids.begin(),
                         accepted.assembly_ids.begin() + accepted.assembly_count,
                         id) != accepted.assembly_ids.begin() + accepted.assembly_count;
    };
    const auto current_support = [&](const Actor &a) {
        if (!a.alive || a.stunned || a.completed || !a.can_cast || a.channel != Channel::None)
            return false;
        for (const auto &spell : a.spells)
            if (spell.ready && (spell.kind == 5 || spell.kind == 7) && spell.allies &&
                distance(a.pos, w.self.pos) <= spell.range)
                return true;
        return false;
    };
    const auto named_station = [&](const Actor &a) {
        if (!named_member(a.id) || !a.alive || a.stunned || a.channel != Channel::None)
            return false;
        for (const auto &monster : monsters)
            if (monster.observed && monster.camp.hp > 0) {
                if (distance(a.pos, monster.camp.pos) <= a.range)
                    return true;
                for (const auto &spell : a.spells)
                    if (camp_damage_ability(spell) && (spell.ready || spell.cooldown >= 0) &&
                        distance(a.pos, monster.camp.pos) <= spell.range)
                        return true;
            }
        return current_support(a);
    };
    add(w.self);
    for (const auto &a : w.allies)
        if (a.id != w.self.id && w.matching_claim(a.id, group) &&
            (coordination_detail::useful_now(a, monsters, a.can_move) || named_station(a)) &&
            crew.size() < 6)
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
    const auto &pending = w.memory.mission;
    const bool committed_assembly = (pending.assembly_pending || named_entry) &&
                                    pending.group == group && pending.start >= 0 &&
                                    w.round < pending.expiry;
    // A real accepted rendezvous has already paid its travel/opportunity cost.
    // Give its fresh current-position certificate the available budget down to
    // the same hard action reserve. Ordinary uncommitted searches keep12k.
    // This changes funding only; no old projected crew is reused as readiness.
    const int planning_floor =
        committed_assembly ? 32000
                           : std::max(32000, static_cast<int>(bc::fuel_remaining()) - 12000);
    auto consider = [&](const std::vector<CampClearBody> &selected, int max_work = 48) {
        if (bc::fuel_remaining() < static_cast<unsigned>(planning_floor + 6000)) {
            out.uncertain = true;
            return;
        }
        for (const auto &body : selected)
            if (external_camp_collateral(body.actor, v.camps, w.geo.groups, group, w.groups,
                                         w.round)) {
                out.uncertain = true;
                return;
            }
        auto fast = basic_clear_rollout(selected, monsters, w.self.id, [&] {
            return bc::fuel_remaining() >= static_cast<unsigned>(planning_floor + 3000) &&
                   w.round == static_cast<int>(bc::round_number());
        });
        if (fast && !quiet_fixed_camp_window(w, selected, int(std::ceil(fast->ticks)) + 3))
            fast.reset();
        auto r = fast ? std::move(*fast)
                      : rollout_camp_clear(selected, monsters, w.self.id, max_work, [&] {
                            return bc::fuel_remaining() >= static_cast<unsigned>(planning_floor) &&
                                   w.round == static_cast<int>(bc::round_number());
                        });
        if (!r.ready) {
            out.uncertain |= r.uncertain;
            return;
        }
        if (named_entry && !quiet_fixed_camp_window(w, selected, int(std::ceil(r.ticks)) + 3)) {
            out.uncertain = true;
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
    if (named_entry) {
        // The finite accepted coalition gets the fresh actual certificate first.
        // No future member/DPS is imported: every named body must be personally
        // useful now and hold the current claim before this authorizes a hit.
        bool complete = true;
        std::vector<CampClearBody> named;
        for (int i = 0; i < accepted.assembly_count; ++i) {
            auto body = std::find_if(crew.begin(), crew.end(), [&](const CampClearBody &b) {
                return b.actor.id == accepted.assembly_ids[i];
            });
            if (body == crew.end()) {
                complete = false;
                break;
            }
            named.push_back(*body);
        }
        if (complete)
            consider(named, 4096);
        else
            out.uncertain = true;
    } else {
        if (!solo_impossible)
            consider({crew.front()});
        for (unsigned i = 1; i < crew.size(); ++i)
            consider({crew.front(), crew[i]});
        if (crew.size() > 2)
            consider(crew);
    }
    out.self_selected = out.ready;
    if (!named_entry && out.ready && crew.size() > 1 && out.alternative_known &&
        bc::fuel_remaining() >= static_cast<unsigned>(planning_floor + 6000)) {
        std::vector<CampClearBody> remaining(crew.begin() + 1, crew.end());
        auto without = rollout_camp_clear(remaining, monsters, remaining.front().actor.id, 48, [&] {
            return bc::fuel_remaining() >= static_cast<unsigned>(planning_floor) &&
                   w.round == static_cast<int>(bc::round_number());
        });
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
    bool action_now = monsters.empty() || coordination_detail::useful_now(
                                              w.self, monsters, w.memory.moved_round != w.round);
    if (out.ready && out.self_selected && !action_now && bc::fuel_remaining() >= 38000 &&
        w.round == static_cast<int>(bc::round_number())) {
        std::vector<Actor> actual;
        actual.reserve(out.selected_ids.size());
        for (int id : out.selected_ids)
            for (const auto &body : crew)
                if (body.actor.id == id) {
                    actual.push_back(body.actor);
                    break;
                }
        if (actual.size() == out.selected_ids.size())
            action_now = current_crew_support_actionable(w.self, actual, v.camps,
                                                         w.memory.moved_round != w.round);
    }
    out.locally_accepted = out.ready && (!out.self_selected || action_now);
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
             (!named_entry && !coordination_detail::useful_now(a, monsters, a.can_move))))
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

#pragma once
#include "combat.h"
#include "squads.h"
namespace tactics {
struct CycleCost {
    double new_gems = 0, new_gold = 0, time = 0;
    bool feasible = false;
};
inline double cycle_rate(int bag, const CycleCost &c, int round) {
    if (!c.feasible || !std::isfinite(c.time) || c.time < 0)
        return 0;
    return (bag + c.new_gems + (round < 600 ? .25 : .24) * c.new_gold) / std::max(1.0, c.time);
}
inline int current_recall_ticks(const Actor &a) {
    return a.home ? 3 : bc::constants::recall_time;
}
inline int current_tribute_ticks(int bag) {
    return tribute_ticks(bag, bc::constants::submit_gem_duration_multiplier,
                         bc::constants::submit_gem_base_duration,
                         bc::constants::submit_gem_minimum_duration);
}
inline bool channel_interruption_risk(World &w, int ticks, bool tribute) {
    if (ticks <= 0)
        return false; // No future owner-action window is fabricated after countdown expiry.
    const bool immune = w.self.type == combat_detail::marcella_type;
    auto threatens = [&](const Actor &e, std::span<const Pos> origins, std::span<const Pos> before,
                         std::span<const Pos> after) {
        if (!e.alive || origins.empty())
            return false;
        auto near = [&](std::span<const Pos> region, int range) {
            for (auto p : region)
                if (distance(p, w.self.pos) <= range)
                    return true;
            return false;
        };
        int prior_dash = 0;
        if (ticks > 1)
            for (const auto &s : e.spells)
                if (s.kind == 6 && combat_detail::plausible_ready(s, ticks - 1))
                    prior_dash = std::max(prior_dash, s.range);
        auto contact = [&](int range, bool compatible) {
            if (ticks > 8 || ticks * std::max(1, e.move_speed) > 8) {
                // The bounded native reach cache stops at eight steps. A long
                // channel instead retains a conservative geometric possibility;
                // this is not certified walking through a wall.
                const int moves = (ticks - (compatible ? 0 : 1)) * std::max(1, e.move_speed);
                return near(origins, range + std::max(0, moves) + prior_dash);
            }
            return near(compatible ? after : before, range + prior_dash);
        };
        bool reset = false;
        for (const auto &s : e.spells)
            if (s.kind == 1 && combat_detail::plausible_ready(s, ticks))
                reset = true;
        const bool basic = contact(e.range, e.range <= 1 || reset);
        if (!tribute && e.strength > 0 && basic)
            return true;
        // An already enhanced Marcella basic can stun without spending another
        // cast. A ready reset can prepare the same legal basic in this window.
        if (tribute && !immune && e.type == combat_detail::marcella_type && (e.enhanced || reset) &&
            basic)
            return true;
        for (const auto &s : e.spells) {
            if (!combat_detail::plausible_ready(s, ticks))
                continue;
            const bool control = s.kind == 4 && !immune;
            const bool damage = combat_detail::offensive(s) && s.amount > 0;
            if (tribute ? !control : !(control || damage))
                continue;
            // Earlier walking can precede an exclusive cast; a compatible cast
            // can also follow the last move. One cast alternative is sufficient
            // for this boolean risk, not summed as several simultaneous casts.
            if (contact(s.range + (s.kind == 3 ? s.radius : 0), !s.exclusive))
                return true;
        }
        return false;
    };
    auto coarse_threat = [&](const Actor &e, Pos from, int unseen_steps) {
        // Budget exhaustion widens uncertainty; it must not erase an enemy.
        // These are conservative risk hypotheses, never legal hidden targets.
        const Pos origin = combat_detail::geometric_approach(from, w.self.pos, unseen_steps);
        const int speed = std::max(1, e.move_speed);
        const std::array<Pos, 1> origins{origin};
        const std::array<Pos, 1> before{
            combat_detail::geometric_approach(origin, w.self.pos, std::max(0, ticks - 1) * speed)};
        const std::array<Pos, 1> after{
            combat_detail::geometric_approach(origin, w.self.pos, ticks * speed)};
        return threatens(e, origins, before, after);
    };
    for (const auto &e : w.enemies) {
        if (!fuel(18000)) {
            if (coarse_threat(e, e.pos, 0))
                return true;
            continue;
        }
        if (ticks > 8 || ticks * std::max(1, e.move_speed) > 8) {
            if (threatens(e, std::vector<Pos>{e.pos}, {}, {}))
                return true;
            continue;
        }
        const auto &before = combat_detail::enemy_positions(w, e, std::min(8, ticks - 1));
        const auto &after = combat_detail::enemy_positions(w, e, std::min(8, ticks));
        if (threatens(e, std::vector<Pos>{e.pos}, before, after))
            return true;
    }
    for (const auto &sight : w.sightings) {
        const int age = w.round - sight.round;
        if (!combat_detail::recent_sighting(age) || !sight.actor.alive)
            continue;
        bool visible = false;
        for (const auto &e : w.enemies)
            visible |= e.id == sight.actor.id;
        if (visible)
            continue; // A currently observed actor is never counted a second time.
        Actor e = sight.actor;
        for (auto &s : e.spells)
            if (s.cooldown >= 0)
                s.cooldown = std::max(0, s.cooldown - age);
        const int unseen_steps =
            age * std::max(1, e.move_speed) + combat_detail::plausible_dash(sight.actor, age);
        const int future_extent = (age + ticks) * std::max(1, e.move_speed) +
                                  combat_detail::plausible_dash(sight.actor, age + ticks);
        if (future_extent > 2 || !fuel(50000)) {
            if (coarse_threat(e, sight.actor.pos, unseen_steps))
                return true;
            continue;
        }
        const auto &origins = combat_detail::remembered_positions(w, sight, 0, false);
        if (origins.empty())
            continue; // Exact current personal visibility removed all possible origins.
        if (ticks > 8) {
            if (threatens(e, origins, {}, {}))
                return true;
            continue;
        }
        const auto &before =
            ticks == 1
                ? origins
                : combat_detail::remembered_positions(w, sight, std::min(8, ticks - 1), true);
        const auto &after = combat_detail::remembered_positions(w, sight, std::min(8, ticks), true);
        if (threatens(e, origins, before, after))
            return true;
    }
    return false;
}
inline bool safe_channel(World &w, int ticks, bool tribute) {
    if (w.self.stunned)
        return false;
    return incoming_damage(w, w.self.pos, std::max(1, ticks)) < w.self.hp &&
           !channel_interruption_risk(w, ticks, tribute);
}
inline Proposal economic(Action a, Mission m, Priority priority, double value) {
    Proposal p;
    p.action = a;
    p.mission = m;
    p.priority = priority;
    p.value = value;
    p.valid = true;
    return p;
}
inline Action moving(Pos p, const char *reason) {
    Action a;
    a.kind = Kind::Move;
    a.at = p;
    a.reason = reason;
    return a;
}
struct AltarPlan {
    int index = -1, distance = unreachable, extra = 0;
    double cost = 1e30;
    bool locked = false;
};
inline std::vector<AltarPlan> altar_plans(World &w) {
    struct Coarse {
        int i, d;
    };
    std::vector<Coarse> coarse;
    for (unsigned i = 0; i < w.geo.altars.size(); ++i) {
        int d = w.geo.at(w.geo.altar_fields[i], w.self.pos);
        if (d != unreachable)
            coarse.push_back({static_cast<int>(i), d});
    }
    std::sort(coarse.begin(), coarse.end(),
              [](auto a, auto b) { return a.d < b.d || (a.d == b.d && a.i < b.i); });
    std::vector<AltarPlan> plans;
    // Actual shortlist: two reachable legal approach sets, not two nearest centers.
    for (unsigned k = 0; k < std::min<std::size_t>(2, coarse.size()); ++k) {
        const auto c = coarse[k];
        const Pos altar = w.geo.altars[c.i];
        int hits = 0;
        bool locked = false;
        if (w.visible.is_set(sdk(altar))) {
            if (auto lock = w.enemy_lock(altar)) {
                locked = true;
                hits = lock->hits_remaining();
            }
        }
        double enemy_arrival = 1e9;
        for (const auto &e : w.enemies)
            enemy_arrival = std::min(
                enemy_arrival, static_cast<double>(std::max(0, distance(e.pos, altar) - e.range)));
        const int total = c.d + hits + current_tribute_ticks(w.self.gems);
        double exposure = enemy_arrival <= total ? std::min(30.0, total - enemy_arrival + 1) : 0;
        double cost = total + exposure;
        plans.push_back({c.i, c.d, hits, cost, locked});
    }
    std::sort(plans.begin(), plans.end(), [](const auto &a, const auto &b) {
        return a.cost < b.cost || (a.cost == b.cost && a.index < b.index);
    });
    return plans;
}
inline std::optional<Proposal> delivery_at(World &w, Memory &m, const AltarPlan &plan,
                                           bool force = false) {
    if (w.self.gems <= 0)
        return std::nullopt;
    if (plan.index < 0)
        return std::nullopt;
    const Pos altar = w.geo.altars[plan.index];
    const int ticks = current_tribute_ticks(w.self.gems);
    bool deciding = w.own_score + w.self.gems >= static_cast<int>(bc::constants::winning_gems);
    bool near_limit = w.round + plan.distance + plan.extra + ticks + 12 >=
                      static_cast<int>(bc::constants::max_rounds);
    bool requested = force || deciding || near_limit || m.mission.bank_after_reward ||
                     m.mission.phase == Phase::Deliver;
    requested |= w.self.gems >= 12 || (w.self.gems >= 10 && plan.distance <= 8) ||
                 (w.self.gems >= 5 && plan.distance <= 2) || w.round >= 1850;
    if (!requested ||
        !deadline_allows(w.round, plan.distance + plan.extra, ticks, bc::constants::max_rounds))
        return std::nullopt;
    Mission job = m.mission;
    job.phase = Phase::Deliver;
    job.group = -1;
    job.target = altar;
    if (m.mission.phase != Phase::Deliver) {
        job.start = w.round;
        job.expiry = w.round + Settings::job_lease;
    }
    job.latest = static_cast<int>(bc::constants::max_rounds) - ticks - 1;
    job.rate = w.self.gems / std::max(1.0, plan.cost);
    Priority rank = deciding || near_limit ? Priority::Deciding : Priority::Incumbent;
    Action a;
    if (distance(w.self.pos, altar) <= bc::constants::submit_gems_range) {
        if (plan.locked) {
            if (w.self.can_attack) {
                a.kind = Kind::BasicLock;
                a.at = altar;
                a.reason = "delivery-remove-lock";
            } else
                return economic(a, job, rank, job.rate);
        } else if (w.memory.channel_attempt_round != w.round && safe_channel(w, ticks, true)) {
            a.kind = Kind::Tribute;
            a.at = altar;
            a.reason = deciding ? "delivery-winning-bank" : "delivery-start-verified-channel";
        } else if (auto exit = escape_action(w))
            return economic(*exit, job, Priority::Survival, 1000);
        else
            return economic(a, job, rank, job.rate);
    } else if (auto step = w.toward(altar, bc::constants::submit_gems_range)) {
        // A deciding label is not permission to take a lethal approach step.
        if (incoming_damage(w, *step) >= w.self.hp)
            return std::nullopt;
        a = moving(*step, "delivery-legal-approach");
    } else
        return std::nullopt;
    return economic(a, job, rank, job.rate);
}
inline std::optional<Proposal> delivery(World &w, Memory &m, bool force = false) {
    if (w.self.gems <= 0)
        return std::nullopt;
    std::optional<Proposal> hold, escape;
    // The bounded two-altar shortlist is a set of proposals, not a promise that
    // its lowest static score has a legal, survivable action right now.
    for (const auto &plan : altar_plans(w)) {
        auto proposal = delivery_at(w, m, plan, force);
        if (!proposal)
            continue;
        if (proposal->priority == Priority::Survival) {
            if (!escape)
                escape = proposal;
        } else if (proposal->action.kind != Kind::None)
            return proposal;
        else if (!hold)
            hold = proposal;
    }
    return escape ? escape : hold;
}
inline bool needs_recovery(World &w) {
    return w.self.health_fraction() < Settings::ordinary_heal ||
           incoming_damage(w, w.self.pos) >= w.self.hp;
}
inline std::optional<Proposal> recovery(World &w, Memory &m, bool necessary = false) {
    if (!w.self.alive)
        return std::nullopt;
    if (w.in_spawn(w.self.pos)) {
        if (w.self.health_fraction() >= Settings::spawn_ready)
            return std::nullopt;
        Mission job = m.mission;
        job.phase = Phase::Recover;
        job.group = -1;
        job.target = w.self.pos;
        return economic(Action{}, job, Priority::Incumbent, 1);
    }
    if (!necessary && !needs_recovery(w))
        return std::nullopt;
    // An optional healthy-gold trip is never fabricated; field Tavi shopping is separate.
    const int home = w.home_distance(w.self.pos);
    Mission job = m.mission;
    job.phase = Phase::Recover;
    job.group = -1;
    job.expiry = w.round + Settings::job_lease;
    int best = unreachable;
    Pos target{};
    if (home != unreachable && w.self.can_move) {
        // One source-rooted field scores every spawn endpoint. A close tile
        // behind a wall or occupied by an ally is not the nearest legal home.
        w.geo.ensure_route(w.self.pos);
        for (auto p : w.geo.own_spawn.positions()) {
            Pos q = position(p);
            if (!w.free(q))
                continue;
            int d = w.walk(w.self.pos, q);
            if (d < best) {
                best = d;
                target = q;
            }
        }
    }
    job.target = target;
    const int ticks = current_recall_ticks(w.self);
    std::optional<Pos> step;
    if (best != unreachable)
        if (auto candidate = w.toward(target, 0, true))
            if (incoming_damage(w, *candidate) < w.self.hp)
                step = candidate;
    const int speed = std::max(1, w.self.move_speed);
    const int walk_ticks = best == unreachable ? unreachable : (best + speed - 1) / speed;
    const bool progressing = step && (w.in_spawn(*step) || w.home_distance(*step) < home);
    if (step && progressing && walk_ticks < ticks)
        return economic(moving(*step, "recovery-faster-safe-return-walk"), job,
                        necessary ? Priority::Survival : Priority::Incumbent, 10);
    // Recall remains available even when no ordinary walking connection exists.
    if (m.channel_attempt_round != w.round && safe_channel(w, ticks, false)) {
        Action a;
        a.kind = Kind::Recall;
        a.reason = "recovery-needed-safe-channel";
        return economic(a, job, necessary ? Priority::Survival : Priority::Incumbent, 10);
    }
    if (step)
        return economic(moving(*step, "recovery-safe-return-walk"), job,
                        necessary ? Priority::Survival : Priority::Incumbent, 10);
    return std::nullopt;
}
struct FarmCandidate {
    int group = -1;
    Pos target{};
    double rate = 0, clear_time = 0, total_time = 0;
    bool ready = false;
};
inline std::vector<Contributor> helpers_for(World &w, int gi, Pos target) {
    double dps = std::max(1.0, w.self.strength);
    for (const auto &s : w.spells)
        if (s.kind == 2 || s.kind == 3 || s.kind == 4)
            dps = std::max(dps, w.self.strength +
                                    s.amount / std::max(2, s.cooldown > 0 ? s.cooldown : 6));
    std::vector<Contributor> crew{{w.self.id, dps, 1, true}};
    for (const auto &a : w.allies)
        if (a.id != w.self.id && a.alive && a.channel == Channel::None && !a.stunned &&
            w.matching_claim(a.id, gi)) {
            // Ready actual local bodies, not a distant intention or a raw radius count.
            const bool basic = a.can_attack && distance(a.pos, target) <= a.range;
            bool cast = false;
            double useful = 0;
            for (const auto &s : a.spells)
                if (s.ready && s.camps && distance(a.pos, target) <= s.range) {
                    cast = true;
                    useful = std::max(useful, s.amount);
                }
            if (basic || cast) {
                crew.push_back({a.id, (basic ? a.strength : 0) + useful / 6, 1, true});
            }
        }
    return crew;
}
inline FarmCandidate evaluate_farm(World &w, int gi) {
    FarmCandidate out;
    out.group = gi;
    if (gi < 0 || gi >= static_cast<int>(w.geo.groups.size()))
        return out;
    const auto &g = w.geo.groups[gi];
    const auto &live = w.groups[gi];
    if (live.fresh(w.round) && live.state == Lifecycle::Respawning && live.respawn_ticks > 6)
        return out;
    double nearest = 1e30;
    Pos target{};
    for (const auto &s : g.spawns) {
        // Static self-rooted path field is reused across all coarse camp slots.
        int d = w.walk(w.self.pos, s.pos);
        if (d < nearest) {
            nearest = d;
            target = s.pos;
        }
    }
    if (nearest == unreachable || nearest >= 1e30)
        return out;
    double hp = g.initial_hp, strength = g.initial_strength;
    if (live.fresh(w.round) && live.state == Lifecycle::Reward) {
        hp = 0;
        strength = 0;
    } else if (live.fresh(w.round) && !live.camps.empty()) {
        // A wandering visible monster does not prove its hidden groupmates dead.
        hp = 0;
        strength = 0;
        for (const auto &spawn : g.spawns) {
            if (std::find(live.known_dead.begin(), live.known_dead.end(), spawn.id) !=
                live.known_dead.end())
                continue;
            const auto seen = std::find_if(live.camps.begin(), live.camps.end(),
                                           [&](const Camp &c) { return c.id == spawn.id; });
            if (seen != live.camps.end()) {
                hp += seen->hp;
                strength += seen->strength;
            } else {
                // Empty original spawn is not proof of death: monsters wander.
                hp += spawn.hp;
                strength += spawn.strength;
            }
        }
    }
    const double enemy_reply = incoming_damage(w, w.self.pos, 1, false);
    auto crew = helpers_for(w, gi, target);
    const double safe_ticks = strength > 0 ? std::max(0.0, (w.self.hp * .75 - enemy_reply - 1) /
                                                               (strength * w.self.camp_mitigation))
                                           : 1e9;
    auto squad = minimum_ready_squad(crew, w.self.id, hp, safe_ticks);
    double dps = 0;
    for (const auto &body : crew)
        dps += body.dps;
    if (squad.ready)
        dps = squad.dps;
    const int bodies = squad.ready ? squad.ids.size() : crew.size();
    const double clear = std::ceil(hp / std::max(1.0, dps));
    bool ready = squad.ready;
    // Persistent attrition is required in a monolith-only gem economy. It still
    // needs a real timely group and a safe next reply, never infinite solo wake.
    if (!ready && w.geo.monolith_only && g.monolith && bodies >= 2 &&
        w.self.hp > strength * w.self.camp_mitigation * 2 + enemy_reply)
        ready = true;
    int altar = w.altar_distance(target), home = w.home_distance(target);
    if ((g.gems > 0 || w.self.gems > 0) && altar == unreachable)
        return out;
    if (home == unreachable && strength > 0)
        return out;
    const double recover = strength == 0
                               ? 0
                               : std::min(3.0, clear * strength / std::max(1.0, w.self.max_hp)) *
                                     (current_recall_ticks(w.self) + 2 + std::min(home, 100));
    // Capture sharing prices actual present holders plus our planned arrival.
    int recipients = 1;
    for (const auto &a : w.allies)
        if (a.id != w.self.id && w.on_group(gi, a.pos) && a.channel == Channel::None)
            ++recipients;
    CycleCost cost;
    cost.new_gems = static_cast<double>(g.gems) / recipients;
    cost.new_gold = static_cast<double>(g.gold) / recipients;
    cost.time = nearest + clear + bc::constants::capture_time + 1 +
                ((g.gems || w.self.gems)
                     ? altar + current_tribute_ticks(w.self.gems + static_cast<int>(cost.new_gems))
                     : 0) +
                recover;
    cost.feasible = true;
    out.target = target;
    out.rate = cycle_rate(w.self.gems, cost, w.round);
    out.clear_time = clear;
    out.total_time = cost.time;
    out.ready = ready;
    // Exclude jobs that cannot convert before the horizon, without inventing
    // future gems from a gold-only investment candidate.
    if (g.gems && w.round + cost.time >= bc::constants::max_rounds)
        out.rate = 0;
    if (live.fresh(w.round) && live.state == Lifecycle::Respawning)
        out.rate /= 1 + std::max(0, live.respawn_ticks - static_cast<int>(nearest));
    return out;
}
inline std::optional<Proposal> farming(World &w, Memory &m) {
    if (w.geo.groups.empty())
        return std::nullopt;
    // A body left on an original tile can postpone the next spawn. Vacate it
    // immediately; a nearly ready timer is not permission to camp that tile.
    for (unsigned gi = 0; gi < w.groups.size(); ++gi)
        if (w.groups[gi].fresh(w.round) && w.groups[gi].state == Lifecycle::Respawning &&
            w.on_group(gi, w.self.pos)) {
            Mission wait = m.mission;
            wait.phase = Phase::Assemble;
            wait.group = -1;
            Action step;
            if (w.self.can_move) {
                auto blockers = w.geo.static_blocked | w.occupied;
                blockers.set(sdk(w.self.pos), false);
                double safest = 1e30;
                for (auto tile :
                     blockers.reachable_tiles(sdk(w.self.pos), w.self.move_speed).positions()) {
                    Pos p = position(tile);
                    if (p == w.self.pos || !w.free(p) || w.on_group(gi, p))
                        continue;
                    const double risk = incoming_damage(w, p);
                    if (risk < w.self.hp && risk < safest) {
                        safest = risk;
                        step = moving(p, "farm-vacate-respawn-region");
                    }
                }
            }
            return economic(step, wait, Priority::Incumbent, 1);
        }
    // Coarse static ranking then dynamic shortlist: incumbent, fresh reward,
    // best other. One native field from self covers every original group tile.
    w.geo.ensure_route(w.self.pos);
    struct Rank {
        int gi;
        double score;
    };
    std::vector<Rank> candidates;
    auto self_field = w.geo.route_cache.find(w.geo.index(w.self.pos));
    for (unsigned i = 0; i < w.geo.groups.size(); ++i) {
        if (m.failed_group == static_cast<int>(i) && w.round < m.failed_until)
            continue;
        const auto &g = w.geo.groups[i];
        int d = unreachable;
        if (self_field != w.geo.route_cache.end())
            for (auto s : g.spawns)
                d = std::min(d, w.geo.at(self_field->second, s.pos));
        if (d == unreachable)
            continue;
        // Live alternatives dominate waiting on a known unavailable reward.
        // Reconsider after the public lifecycle changes rather than idling.
        if (w.groups[i].fresh(w.round) && w.groups[i].state == Lifecycle::Respawning)
            continue;
        double value = g.gems + .25 * g.gold;
        double hp =
            w.groups[i].fresh(w.round) && w.groups[i].state == Lifecycle::Reward ? 0 : g.initial_hp;
        candidates.push_back(
            {static_cast<int>(i), value / (1 + d + hp / std::max(1.0, w.self.strength) + 6)});
    }
    std::sort(candidates.begin(), candidates.end(), [](auto a, auto b) {
        return a.score > b.score || (a.score == b.score && a.gi < b.gi);
    });
    std::vector<int> shortlist;
    const bool incumbent_suppressed = m.mission.group == m.failed_group && w.round < m.failed_until;
    if (!incumbent_suppressed && m.mission.group >= 0 &&
        m.mission.group < static_cast<int>(w.groups.size()) &&
        !(w.groups[m.mission.group].fresh(w.round) &&
          w.groups[m.mission.group].state == Lifecycle::Respawning))
        shortlist.push_back(m.mission.group);
    for (auto c : candidates)
        if (w.groups[c.gi].fresh(w.round) && w.groups[c.gi].state == Lifecycle::Reward) {
            if (std::find(shortlist.begin(), shortlist.end(), c.gi) == shortlist.end())
                shortlist.push_back(c.gi);
            break;
        }
    for (auto c : candidates)
        if (shortlist.size() < 3 &&
            std::find(shortlist.begin(), shortlist.end(), c.gi) == shortlist.end())
            shortlist.push_back(c.gi);
    FarmCandidate best, incumbent;
    for (int gi : shortlist)
        if (fuel(10000)) {
            auto c = evaluate_farm(w, gi);
            if (gi == m.mission.group)
                incumbent = c;
            if (c.rate > best.rate)
                best = c;
        }
    if (!incumbent_suppressed && incumbent.rate > 0 &&
        (w.round < m.mission.expiry || best.rate <= incumbent.rate * Settings::switch_margin))
        best = incumbent;
    // An expiring lease requests a new continuity check; it never releases the
    // last physical holder merely because another score became larger.
    for (unsigned i = 0; i < w.groups.size(); ++i)
        if (w.groups[i].fresh(w.round) && w.groups[i].state == Lifecycle::Reward &&
            w.on_group(i, w.self.pos) &&
            !(m.failed_group == static_cast<int>(i) && w.round < m.failed_until)) {
            best = evaluate_farm(w, i);
            break;
        }
    if (best.group < 0 || best.rate <= 0)
        return std::nullopt;
    const int gi = best.group;
    const auto &g = w.geo.groups[gi];
    const auto &view = w.groups[gi];
    Mission job = m.mission;
    if (job.group != gi) {
        job = {};
        job.start = w.round;
        job.expiry = w.round + Settings::job_lease;
        job.last_progress = w.round;
        job.last_pos = w.self.pos;
    }
    job.group = gi;
    job.target = best.target;
    job.rate = best.rate;
    const bool on = w.on_group(gi, w.self.pos);
    Action a;
    if (view.fresh(w.round) && view.state == Lifecycle::Reward) {
        job.phase = on ? Phase::Collect : Phase::Travel;
        if (on) {
            // Physical, acyclic local replacement. A near/off-region claim is
            // never accepted as a holder, and the lowest-ID holder cannot yield.
            bool replacement = false;
            for (const auto &ally : w.allies)
                if (ally.id != w.self.id &&
                    may_yield_holder(w.self.id, ally, w.on_group(gi, ally.pos),
                                     w.matching_claim(ally.id, gi)))
                    replacement = true;
            if (replacement && fuel(12000)) {
                for (auto rank : candidates)
                    if (rank.gi != gi) {
                        const auto &next = w.geo.groups[rank.gi];
                        if (next.spawns.empty())
                            continue;
                        if (auto exit = w.toward(next.spawns.front().pos, 1)) {
                            if (!w.on_group(gi, *exit) &&
                                incoming_damage(w, *exit) < w.self.hp * .65) {
                                job.phase = Phase::Reenter;
                                job.group = -1;
                                a = moving(*exit, "capture-actual-lower-id-holder-handoff");
                                return economic(a, job, Priority::Incumbent, best.rate);
                            }
                        }
                        break;
                    }
            }
            if (g.spawns.size() == 1 && m.hold_group == gi && m.hold_since >= 0 &&
                needs_recovery(w) &&
                w.round - m.hold_since >=
                    overlap_hold(bc::constants::capture_time, current_recall_ticks(w.self)) &&
                m.channel_attempt_round != w.round &&
                safe_channel(w, current_recall_ticks(w.self), false)) {
                a.kind = Kind::Recall;
                a.reason = "capture-single-tile-guarded-overlap";
            } else
                a.reason = "capture-retain-actual-holder";
            return economic(a, job, Priority::Incumbent, best.rate);
        }
        if (auto step = w.toward(best.target))
            a = moving(*step, "capture-enter-original-region");
        else
            return economic(a, job, Priority::Incumbent, best.rate);
        return economic(a, job, Priority::Incumbent, best.rate);
    }
    if (!view.fresh(w.round)) {
        job.phase = Phase::Observe;
        if (auto step = w.toward(best.target, 2))
            a = moving(*step, "farm-reversible-fresh-observation");
        else if (auto closer = w.toward(best.target))
            a = moving(*closer, "farm-inspect-occluded-original-region");
        else if (w.round - job.start >= Settings::assembly_wait) {
            m.failed_group = gi;
            m.failed_until = w.round + Settings::job_lease;
            return std::nullopt;
        }
        return economic(a, job, Priority::Routine, best.rate);
    }
    if (view.state != Lifecycle::Alive)
        return std::nullopt;
    if (!best.ready) {
        if (job.phase != Phase::Assemble)
            job.last_progress = w.round;
        job.phase = Phase::Assemble;
        if (w.round - job.last_progress >= Settings::assembly_wait) {
            m.failed_group = gi;
            m.failed_until = w.round + Settings::job_lease;
            return std::nullopt;
        }
        // Sleeping monsters are friendly until hit. Enter an actual contribution
        // tile without attacking, otherwise every helper waits outside its own
        // range and the ready-crew condition can never become true. An already
        // awake camp still requires a staging tile outside its real reply reach.
        int stage_range = std::max(1, w.self.range);
        for (const auto &monster : view.camps)
            if (monster.awake && monster.strength > 0)
                stage_range = std::max(stage_range, monster.range + 2);
        if (distance(w.self.pos, best.target) > stage_range)
            if (auto step = w.toward(best.target, stage_range)) {
                bool outside = true;
                for (const auto &monster : view.camps)
                    if (monster.awake && monster.strength > 0 &&
                        distance(*step, monster.pos) <= monster.range + 1)
                        outside = false;
                if (outside && incoming_damage(w, *step) < w.self.hp * .65)
                    a = moving(*step, "farm-stage-for-real-ready-help");
            }
        return economic(a, job, Priority::Routine, best.rate);
    }
    if (!farm_safe(w, gi)) {
        if (auto protect = combat_proposal(w, m, true))
            return protect;
        if (auto escape = escape_action(w)) {
            job.phase = Phase::Escape;
            job.group = -1;
            return economic(*escape, job, Priority::Survival, 1000);
        }
        return economic(Action{}, job, Priority::Incumbent, 0);
    }
    const bool continuing_clear = job.phase == Phase::Clear && job.last_camp_hp >= 0;
    job.phase = Phase::Clear;
    double hp = 0;
    for (const auto &c : view.camps)
        hp += c.hp;
    if (!continuing_clear || hp < job.last_camp_hp) {
        job.last_progress = w.round;
        job.stagnant = 0;
    } else if (job.last_progress >= 0 &&
               w.round - job.last_progress >= Settings::stagnation_limit &&
               distance(w.self.pos, best.target) <= w.self.range + 1) {
        m.failed_group = gi;
        m.failed_until = w.round + Settings::job_lease;
        return std::nullopt;
    }
    job.last_camp_hp = hp;
    const Camp *target = nullptr;
    for (const auto &c : view.camps)
        if (c.hp > 0 && w.self.can_attack && distance(w.self.pos, c.pos) <= w.self.range &&
            (!target || c.hp < target->hp))
            target = &c;
    if (target) {
        a.kind = Kind::BasicCamp;
        a.target = target->id;
        a.reason = "farm-live-in-range-basic";
        return economic(a, job, Priority::Routine, best.rate);
    }
    double cast_gain = 0;
    for (const auto &s : w.spells)
        if (s.ready && s.camps && (s.kind == 2 || s.kind == 3 || s.kind == 4))
            for (const auto &c : view.camps)
                if (c.hp > 0 && distance(w.self.pos, c.pos) <= s.range) {
                    double gain = std::min(c.hp, s.amount);
                    if (gain > cast_gain) {
                        cast_gain = gain;
                        a.kind = Kind::CastCamp;
                        a.target = c.id;
                        a.slot = s.slot;
                        a.reason = "farm-useful-ready-damage";
                    }
                }
    if (cast_gain > 0)
        return economic(a, job, Priority::Routine, best.rate);
    if (!w.self.can_attack)
        for (const auto &s : w.spells)
            if (s.ready && s.kind == 1 && s.self) {
                for (const auto &c : view.camps)
                    if (c.hp > 0 && distance(w.self.pos, c.pos) <= w.self.range) {
                        a.kind = Kind::CastSelf;
                        a.slot = s.slot;
                        a.target = c.id;
                        a.reason = "farm-reset-only-live-followup";
                        return economic(a, job, Priority::Routine, best.rate);
                    }
            }
    for (const auto &c : view.camps)
        if (c.hp > 0 &&
            (!target || distance(w.self.pos, c.pos) < distance(w.self.pos, target->pos)))
            target = &c;
    if (target && w.self.can_move)
        if (auto step = w.toward(target->pos, w.self.range)) {
            if (incoming_damage(w, *step) < w.self.hp * .75) {
                a = moving(*step, "farm-legal-contribution-tile");
                job.phase = Phase::Travel;
                return economic(a, job, Priority::Routine, best.rate);
            }
        }
    return economic(a, job, Priority::Routine, best.rate);
}
} // namespace tactics

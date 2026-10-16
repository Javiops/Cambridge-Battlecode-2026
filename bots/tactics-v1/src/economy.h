#pragma once
#include "assembly.h"
#include "combat.h"
#include "coordination.h"
#include "cycles.h"
#include "ranking.h"
#include "solo.h"
#include "squads.h"
#include "strategic.h"
#include <bit>
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
inline bool channel_interruption_risk(World &w, int ticks, bool tribute,
                                      std::optional<Pos> channel_at = std::nullopt) {
    if (ticks <= 0)
        return false;
    const bool immune = w.self.type == combat_detail::marcella_type;
    const Pos at = channel_at.value_or(w.self.pos);
    auto threatens = [&](const Actor &enemy, int age) {
        if (!enemy.alive || (enemy.stunned && enemy.stun_ticks > ticks + age))
            return false;
        const int speed = std::max(1, enemy.move_speed);
        const int dash = combat_detail::plausible_dash(enemy, ticks + age);
        auto contact = [&](int range, bool compatible) {
            const int moves = std::max(0, ticks + age - (compatible ? 0 : 1)) * speed;
            if (distance(enemy.pos, at) <= range)
                return true;
            if (distance(enemy.pos, at) > range + moves + dash)
                return false;
            // The exact enemy-walk approach ring respects terrain and spawn
            // ownership. A plausible dash retains uncertainty across holes.
            const int path = w.enemy_steps(enemy.pos, at, range);
            return path <= moves || (dash > 0 && distance(enemy.pos, at) <= range + moves + dash);
        };
        bool reset = false;
        for (const auto &spell : enemy.spells)
            reset |= spell.kind == 1 && combat_detail::plausible_ready(spell, ticks + age);
        const bool basic = contact(enemy.range, enemy.range <= 1 || reset);
        if (!tribute && enemy.strength > 0 && basic)
            return true;
        if (tribute && !immune && enemy.type == combat_detail::marcella_type &&
            (enemy.enhanced || reset) && basic)
            return true;
        for (const auto &spell : enemy.spells) {
            if (!combat_detail::plausible_ready(spell, ticks + age))
                continue;
            const bool control =
                !immune &&
                (spell.kind == 4 || (enemy.type == 0 && spell.kind == 3 && spell.duration > 0));
            const bool damage = combat_detail::offensive(spell) && spell.amount > 0;
            if ((tribute ? control : (control || damage)) &&
                contact(spell.range + (spell.kind == 3 ? spell.radius : 0), !spell.exclusive))
                return true;
        }
        return false;
    };
    for (const auto &enemy : w.enemies)
        if (threatens(enemy, 0))
            return true;
    for (const auto &sight : w.sightings) {
        const int age = w.round - sight.round;
        if (!combat_detail::recent_sighting(age))
            continue;
        bool visible = false;
        for (const auto &enemy : w.enemies)
            visible |= enemy.id == sight.actor.id;
        const int extent = age * std::max(1, sight.actor.move_speed) +
                           combat_detail::plausible_dash(sight.actor, age);
        if (!visible && extent <= 2 && fuel(50000) &&
            combat_detail::remembered_positions(w, sight, 0, false).empty())
            continue;
        if (!visible && threatens(sight.actor, age))
            return true;
    }
    return false;
}
inline bool safe_channel_at(World &w, Pos at, int ticks, bool tribute) {
    if (w.self.stunned)
        return false;
    if (!tribute)
        for (const auto &group : w.groups)
            for (const auto &camp : group.camps)
                if (camp.awake && camp.hp > 0 && distance(camp.pos, at) <= camp.range)
                    return false; // Any camp hit interrupts Recall, even when far from lethal.
    return incoming_damage(w, at, std::max(1, ticks)) < w.self.hp &&
           !channel_interruption_risk(w, ticks, tribute, at);
}
inline bool safe_channel(World &w, int ticks, bool tribute) {
    return safe_channel_at(w, w.self.pos, ticks, tribute);
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
inline std::optional<Proposal> peaceful_support(World &w, Memory &m) {
    const double harm = incoming_damage(w, w.self.pos);
    if (harm >= w.self.hp * .5)
        return combat_proposal(w, m, true, std::max(30000, int(bc::fuel_remaining()) - 8000));
    Action best;
    double gain = 0;
    for (const auto &s : w.spells) {
        if (!s.ready)
            continue;
        if (s.kind == 7 && s.self) {
            const double benefit = std::min(harm, std::max(0.0, s.amount - w.self.shield));
            if (benefit > gain) {
                gain = benefit;
                best.kind = Kind::CastSelf;
                best.slot = s.slot;
                best.reason = "camp-real-next-response-shield";
            }
        }
        if (s.kind == 5)
            for (const auto &ally : w.allies)
                if (ally.alive && (ally.id == w.self.id ? s.self : s.allies) &&
                    distance(w.self.pos, ally.pos) <= s.range) {
                    const double benefit = std::min(s.amount, std::max(0.0, ally.max_hp - ally.hp));
                    if (benefit > gain) {
                        gain = benefit;
                        best.kind = ally.id == w.self.id ? Kind::CastSelf : Kind::CastChampion;
                        best.target = ally.id;
                        best.slot = s.slot;
                        best.reason = "camp-effective-local-heal";
                    }
                }
    }
    if (gain <= 0)
        return std::nullopt;
    return economic(best, m.mission, Priority::Routine, gain);
}
struct AltarPlan {
    int index = -1, distance = unreachable, extra = 0;
    double cost = 1e30;
    bool locked = false;
    int next_group = -1;
    Pos next_target{};
    double next_rate = 0, continuation = 0;
    bool continuation_known = false;
};
inline std::uint64_t bank_power_signature(const Actor &a) {
    std::uint64_t value = 1469598103934665603ull;
    auto add = [&](std::uint64_t n) { value = (value ^ n) * 1099511628211ull; };
    add(a.type);
    add(a.range);
    add(a.move_speed);
    add(a.home);
    for (double n : {a.max_hp, a.strength, a.focus, a.mitigation, a.camp_mitigation})
        add(std::bit_cast<std::uint64_t>(n));
    return value; // HP, location and spent action allowances never clear this failure.
}
inline void note_failed_bank_window(World &w, Memory &m) {
    if (m.mission.phase != Phase::Deliver || w.in_spawn(w.self.pos) || w.self.gems <= 0)
        return;
    for (unsigned i = 0; i < w.geo.altars.size(); ++i)
        if (m.mission.target == w.geo.altars[i]) {
            m.failed_bank_altar = static_cast<int>(i);
            m.failed_bank_window = w.self.pos;
            m.failed_bank_power = bank_power_signature(w.self);
            // Initial backoff covers an actual Recall, healing phase and one
            // fresh lease. It is uncertainty about this trip, not unsafe proof.
            m.failed_bank_until = w.round + current_recall_ticks(w.self) + Settings::job_lease + 1;
            return;
        }
}
inline bool failed_bank_window_active(const World &w, int altar) {
    const auto &m = w.memory;
    if (m.failed_bank_altar != altar || w.round >= m.failed_bank_until ||
        m.failed_bank_power != bank_power_signature(w.self))
        return false;
    bool observed = w.geo.valid(m.failed_bank_window);
    for (int dy = -2; dy <= 2 && observed; ++dy)
        for (int dx = -2; dx <= 2; ++dx) {
            const Pos q{m.failed_bank_window.x + dx, m.failed_bank_window.y + dy};
            if (w.geo.valid(q) && !packed_bit(w.visible_bytes, w.geo.index(q))) {
                observed = false;
                break;
            }
        }
    const int ticks = current_tribute_ticks(w.self.gems) + 1;
    // Fresh personal absence at the RECORDED failure window may reopen it.
    // Empty vision around a distant spawn after Recall does not do so.
    return !(observed && observed_contact_eta(w, m.failed_bank_window, ticks) > ticks);
}
struct BankContinuation {
    int group = -1;
    Pos target{};
    double rate = 0;
};
inline BankContinuation named_bank_continuation(const World &w, const Mission &mission) {
    auto candidate = [&](int gi) -> BankContinuation {
        if (gi < 0 || gi >= static_cast<int>(w.geo.groups.size()) ||
            (w.memory.failed_group == gi && w.round < w.memory.failed_until))
            return {};
        const auto &g = w.geo.groups[gi];
        const auto &live = w.groups[gi];
        if (g.spawns.empty() || !live.fresh(w.round) ||
            (live.state != Lifecycle::Alive && live.state != Lifecycle::Reward))
            return {};
        // This job begins after actual banking: the current carried bag is
        // already converted and cannot make a pure-gold continuation scoreable.
        const auto purpose = resource_job_purpose(g.gems, 0, w.geo.monolith_only);
        if (purpose == ResourcePurpose::Ineligible || purpose == ResourcePurpose::MonolithFallback)
            return {};
        const Pos target = g.spawns.front().pos;
        const auto steps = w.geo.cached_steps(w.self.pos, target);
        if (!steps || *steps == unreachable || w.warning_near(target, 3))
            return {};
        const double clear = live.state == Lifecycle::Reward
                                 ? 0
                                 : std::ceil(g.initial_hp / std::max(1.0, w.self.strength));
        if (clear * g.initial_strength * w.self.camp_mitigation >= .75 * w.self.hp)
            return {};
        // This names a conservative solo continuation, never future helper DPS.
        return {gi, target,
                (g.gems + .25 * g.gold) /
                    std::max(1.0, *steps + clear + bc::constants::capture_time + 1)};
    };
    if (auto c = candidate(mission.bank_reentry_group); c.group >= 0)
        return c;
    if (auto c = candidate(mission.group); c.group >= 0)
        return c;
    // At most two already-cached nearby jobs get a viability check. No field
    // construction, promised respawn or hypothetical teammate enters this quote.
    std::array<std::pair<int, int>, 2> nearest{{{unreachable, -1}, {unreachable, -1}}};
    const int scan_floor = std::max(40000, int(bc::fuel_remaining()) - 4000);
    for (unsigned i = 0; i < w.geo.groups.size(); ++i) {
        if ((i & 7u) == 0 && int(bc::fuel_remaining()) < scan_floor)
            break; // Unscanned jobs remain unpriced; this is not a global best certificate.
        const auto &g = w.geo.groups[i];
        if (g.spawns.empty() || !w.groups[i].fresh(w.round))
            continue;
        if (w.groups[i].state != Lifecycle::Alive && w.groups[i].state != Lifecycle::Reward)
            continue;
        // Cheap geometric shortlist only. Exact cache queries are confined to
        // the two candidates below, rather than repeated across a large map.
        const std::pair<int, int> rank{distance(w.self.pos, g.spawns.front().pos),
                                       static_cast<int>(i)};
        if (rank < nearest[0]) {
            nearest[1] = nearest[0];
            nearest[0] = rank;
        } else if (rank < nearest[1])
            nearest[1] = rank;
    }
    for (auto [d, gi] : nearest)
        if (auto c = candidate(gi); c.group >= 0)
            return c;
    return {};
}
inline std::vector<AltarPlan> altar_plans(World &w, const Mission *mission = nullptr) {
    struct Coarse {
        int i, d;
    };
    std::vector<Coarse> coarse;
    const bool deciding = w.own_score + w.self.gems >= int(bc::constants::winning_gems);
    const bool final_window =
        w.round + current_tribute_ticks(w.self.gems) + Settings::job_lease + 12 >=
        int(bc::constants::max_rounds);
    for (unsigned i = 0; i < w.geo.altars.size(); ++i) {
        if (w.memory.failed_altar == static_cast<int>(i) && w.round < w.memory.failed_altar_until &&
            w.geo.altars.size() > 1)
            continue;
        if (!deciding && !final_window && w.geo.altars.size() > 1 &&
            failed_bank_window_active(w, i))
            continue;
        int d = w.geo.at(w.geo.altar_fields[i], w.self.pos);
        if (d != unreachable)
            coarse.push_back({static_cast<int>(i), d});
    }
    std::sort(coarse.begin(), coarse.end(),
              [](auto a, auto b) { return a.d < b.d || (a.d == b.d && a.i < b.i); });
    std::vector<AltarPlan> plans;
    const auto next = named_bank_continuation(w, mission ? *mission : w.memory.mission);
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
        const int walk_turns =
            (c.d + std::max(1, w.self.move_speed) - 1) / std::max(1, w.self.move_speed);
        const int total = walk_turns + hits + current_tribute_ticks(w.self.gems);
        double exposure = enemy_arrival <= total ? std::min(30.0, total - enemy_arrival + 1) : 0;
        double cost = total + exposure;
        if (w.warning_near(altar, 3))
            cost += 4; // Advisory route comparison, never a hidden legal target or hard veto.
        plans.push_back({c.i, walk_turns, hits, cost, locked});
        auto &plan = plans.back();
        if (next.group >= 0) {
            int worst = 0;
            bool known = true, any = false;
            for (int dy = -int(bc::constants::submit_gems_range);
                 dy <= int(bc::constants::submit_gems_range); ++dy)
                for (int dx = -int(bc::constants::submit_gems_range);
                     dx <= int(bc::constants::submit_gems_range); ++dx) {
                    const Pos q{altar.x + dx, altar.y + dy};
                    if (w.geo.blocked(q))
                        continue;
                    const auto d = w.geo.cached_steps(q, next.target);
                    if (!d || *d == unreachable) {
                        known = false;
                        continue;
                    }
                    worst = std::max(worst, *d);
                    any = true;
                }
            if (known && any) {
                plan.next_group = next.group;
                plan.next_target = next.target;
                plan.next_rate = next.rate;
                plan.continuation = std::ceil(double(worst) / std::max(1, w.self.move_speed));
                plan.continuation_known = true;
            }
        }
    }
    // A missing route is not a zero-cost exit. Use this common continuation
    // only when it is known for the whole bounded altar comparison.
    const bool complete =
        !plans.empty() && std::all_of(plans.begin(), plans.end(),
                                      [](const AltarPlan &p) { return p.continuation_known; });
    for (auto &p : plans)
        if (complete)
            p.cost += p.continuation;
        else {
            p.next_group = -1;
            p.continuation_known = false;
        }
    std::sort(plans.begin(), plans.end(), [](const auto &a, const auto &b) {
        return a.cost < b.cost || (a.cost == b.cost && a.index < b.index);
    });
    return plans;
}
inline std::optional<Action> bank_ring_reposition(World &w, Pos altar, int ticks) {
    if (!w.self.can_move || w.self.stunned || bc::fuel_remaining() < 55000 ||
        w.round != static_cast<int>(bc::round_number()))
        return std::nullopt;
    struct Candidate {
        Pos pos;
        double exposure;
        int home;
    };
    std::array<Candidate, 8> candidates{};
    unsigned count = 0;
    for (int dy = -1; dy <= 1; ++dy)
        for (int dx = -1; dx <= 1; ++dx) {
            const Pos p{w.self.pos.x + dx, w.self.pos.y + dy};
            if ((!dx && !dy) || distance(p, altar) > bc::constants::submit_gems_range || !w.free(p))
                continue;
            double exposure = w.exposure(p);
            for (const auto &group : w.groups)
                for (const auto &camp : group.camps)
                    if (camp.hp > 0 && camp.awake && distance(camp.pos, p) <= camp.range)
                        exposure += camp.strength * w.self.camp_mitigation;
            candidates[count++] = {p, exposure, w.home_distance(p)};
        }
    std::sort(candidates.begin(), candidates.begin() + count, [](const auto &a, const auto &b) {
        if (a.exposure != b.exposure)
            return a.exposure < b.exposure;
        if (a.home != b.home)
            return a.home < b.home;
        return a.pos.y < b.pos.y || (a.pos.y == b.pos.y && a.pos.x < b.pos.x);
    });
    const int floor = std::max(30000, int(bc::fuel_remaining()) - 10000);
    for (unsigned i = 0; i < std::min(2u, count); ++i) {
        if (int(bc::fuel_remaining()) < floor || w.round != int(bc::round_number()))
            return std::nullopt;
        const Pos p = candidates[i].pos;
        // One extra window covers a movement whose fresh snapshot may need the
        // next owner opportunity. The helper never changes World.self.
        if (!safe_channel_at(w, p, ticks + 1, true))
            continue;
        if (int(bc::fuel_remaining()) < floor || w.round != int(bc::round_number()))
            return std::nullopt;
        const auto exit = known_exit_prefix(w, p, false);
        const bool credible = observed_contact_eta(w, p, ticks + 1) != unreachable;
        if (credible &&
            (!exit.known || !exit.viable || exit.earliest_contact <= ticks + 1 + exit.owner_eta))
            continue;
        return moving(p, "delivery-reposition-verified-ring-window");
    }
    return std::nullopt;
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
    job.intent = Intent::Convert;
    job.group = -1;
    job.target = altar;
    job.bank_altar = plan.index;
    job.bank_reentry_group = plan.continuation_known ? plan.next_group : -1;
    job.bank_reentry_target = plan.next_target;
    job.bank_reentry_rate = plan.next_rate;
    if (m.mission.phase != Phase::Deliver) {
        job.start = w.round;
        job.expiry = w.round + Settings::job_lease;
    }
    job.latest = static_cast<int>(bc::constants::max_rounds) - ticks - 1;
    job.rate = w.self.gems / std::max(1.0, plan.cost);
    // Risk affects altar selection, but it is not elapsed time in schedules.
    job.completion_cost = plan.distance + plan.extra + ticks;
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
        } else if (auto reposition = bank_ring_reposition(w, altar, ticks))
            return economic(*reposition, job, rank, job.rate);
        else if (auto exit = escape_action(w))
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
    for (const auto &plan : altar_plans(w, &m.mission)) {
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
    const bool investment =
        m.upgrade_gem_unlock ||
        (m.upgrade_absence > 0 && m.upgrade_gain > m.upgrade_absence * Settings::switch_margin);
    if (!necessary && !needs_recovery(w) && !investment)
        return std::nullopt;
    // An optional healthy-gold trip is never fabricated; field Tavi shopping is separate.
    const int home = w.home_distance(w.self.pos);
    Mission job = m.mission;
    job.phase = Phase::Recover;
    job.intent = Intent::Recover;
    job.assembly_pending = false;
    job.group = -1;
    job.expiry = w.round + Settings::job_lease;
    int best = unreachable;
    Pos target{};
    if (home != unreachable && w.self.can_move) {
        // One source-rooted field scores every spawn endpoint. A close tile
        // behind a wall or occupied by an ally is not the nearest legal home.
        // The immutable multi-source home field already answers the route to
        // spawn. Rebuilding a self-rooted field on every low-HP owner turn
        // previously cost 19-28k and delayed the return itself.
        for (auto p : w.geo.own_spawn.positions()) {
            Pos q = position(p);
            if (!w.free(q))
                continue;
            int d = w.geo.estimate(w.self.pos, q);
            if (d < best) {
                best = d;
                target = q;
            }
        }
    }
    if (best != unreachable)
        best = home;
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
        a.reason =
            investment ? "recovery-priced-private-upgrade-return" : "recovery-needed-safe-channel";
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
    double new_gems = 0, recovery_time = 0;
    bool ready = false, route_known = false, prospective_feasible = false, gold_fallback = false;
    SoloFarmQuote solo{};
    bool eligible() const {
        return ready || prospective_feasible;
    }
};
inline std::vector<Contributor> helpers_for(World &w, int gi, Pos target) {
    (void)target; // Group membership, rather than one preferred spawn, defines useful help.
    double dps = std::max(1.0, w.self.strength);
    for (const auto &s : w.spells)
        if (s.kind == 2 || s.kind == 3 || s.kind == 4)
            dps = std::max(dps, w.self.strength +
                                    s.amount / std::max(1, s.recharge > 0 ? s.recharge : 8));
    std::vector<Contributor> crew{{w.self.id, dps, 1, true}};
    for (const auto &a : w.allies)
        if (a.id != w.self.id && a.alive && a.channel == Channel::None && !a.stunned &&
            w.matching_claim(a.id, gi)) {
            // Ready actual local bodies, not a distant intention or a raw radius count.
            bool basic = false;
            bool cast = false;
            double useful = 0;
            for (const auto &camp : w.groups[gi].camps)
                if (camp.hp > 0) {
                    basic |= a.can_attack && distance(a.pos, camp.pos) <= a.range;
                    for (const auto &s : a.spells)
                        if (s.ready && s.camps && (s.kind == 2 || s.kind == 3 || s.kind == 4) &&
                            s.amount > 0 && distance(a.pos, camp.pos) <= s.range) {
                            cast = true;
                            useful = std::max(useful, s.amount);
                        }
                }
            if (basic || cast) {
                crew.push_back({a.id, (basic ? a.strength : 0) + useful / 6, 1, true});
            }
        }
    return crew;
}
inline double coarse_farm_enemy_reply(const World &w, const Actor &body) {
    double raw = 0;
    for (const auto &enemy : w.enemies)
        raw += combat_detail::long_window_reply_upper(enemy, enemy.pos, body.pos, 1);
    for (const auto &sight : w.sightings) {
        const int age = w.round - sight.round;
        if (!combat_detail::recent_sighting(age))
            continue;
        bool visible = false;
        for (const auto &enemy : w.enemies)
            visible |= enemy.id == sight.actor.id;
        if (!visible)
            raw += combat_detail::coarse_remembered_reply(sight.actor, age, body.pos, 1);
    }
    return std::max(0.0, raw * body.mitigation - body.shield);
}
struct SortieExit {
    double floor = 0;
    std::array<Pos, 5> path{};
    int length = 0;
};
inline SortieExit monolith_sortie_exit(World &w, int gi) {
    if (!w.geo.monolith_only || !w.geo.groups[gi].monolith || !w.groups[gi].fresh(w.round) ||
        !w.enemies.empty() || w.warning_near(w.self.pos, 4) || bc::fuel_remaining() < 40000)
        return {};
    const auto crew = helpers_for(w, gi, w.self.pos);
    if (crew.size() < 2)
        return {};
    double pressure = 0;
    for (const auto &camp : w.groups[gi].camps)
        pressure += camp.strength * w.self.camp_mitigation;
    if (pressure <= 0)
        return {};
    std::array<Pos, 128> queue{};
    std::array<int, 128> depth{};
    std::array<int, 128> parent{};
    parent[0] = -1;
    std::array<bool, 81> visited{};
    visited[40] = true;
    int head = 0, tail = 1;
    queue[0] = w.self.pos;
    while (head < tail && bc::fuel_remaining() > 30000) {
        const int current = head++;
        const auto p = queue[current];
        const int steps = depth[current];
        bool outside = true;
        for (const auto &camp : w.groups[gi].camps)
            outside &= distance(p, camp.pos) > camp.range;
        if (outside && w.home_distance(p) != unreachable) {
            // The executed route below uses one explicit legal tile per owner
            // turn; do not price full-speed strides and then walk more slowly.
            const int turns = steps;
            const double floor =
                (turns + 1) * pressure + coarse_farm_enemy_reply(w, w.self) + .1 * w.self.max_hp;
            SortieExit out;
            out.floor = floor;
            out.length = steps + 1;
            for (int at = current, k = steps; at >= 0; at = parent[at], --k)
                out.path[k] = queue[at];
            return out;
        }
        if (steps >= 4)
            continue;
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                Pos q{p.x + dx, p.y + dy};
                const int rx = q.x - w.self.pos.x + 4, ry = q.y - w.self.pos.y + 4;
                if (rx < 0 || rx >= 9 || ry < 0 || ry >= 9 || visited[ry * 9 + rx])
                    continue;
                if (!w.free(q))
                    continue;
                if (tail < 128) {
                    visited[ry * 9 + rx] = true;
                    queue[tail] = q;
                    parent[tail] = current;
                    depth[tail++] = steps + 1;
                }
            }
    }
    return {}; // Unknown/blocked exit never certifies a short attrition sortie.
}
inline FarmCandidate evaluate_farm(World &w, int gi, const SoloFarmQuote *prepaid = nullptr) {
    FarmCandidate out;
    out.group = gi;
    if (gi < 0 || gi >= static_cast<int>(w.geo.groups.size()))
        return out;
    const auto &g = w.geo.groups[gi];
    const auto &live = w.groups[gi];
    const bool holder =
        live.fresh(w.round) && live.state == Lifecycle::Reward && w.on_group(gi, w.self.pos);
    const auto purpose = resource_job_purpose(g.gems, w.self.gems, w.geo.monolith_only, holder);
    if (purpose == ResourcePurpose::Ineligible)
        return out;
    out.gold_fallback = purpose == ResourcePurpose::MonolithFallback;
    if (live.fresh(w.round) && live.state == Lifecycle::Respawning && live.respawn_ticks > 6)
        return out;
    double nearest = 1e30;
    Pos target{};
    for (const auto &s : g.spawns) {
        // Static self-rooted path field is reused across all coarse camp slots.
        int d = w.geo.estimate(w.self.pos, s.pos);
        if (d < nearest) {
            nearest = d;
            target = s.pos;
        }
    }
    if (nearest == unreachable || nearest >= 1e30)
        return out;
    const SoloFarmQuote solo =
        prepaid && current_solo_quote(w, *prepaid, gi) ? *prepaid : quote_solo_farm(w, gi);
    if (solo.known && solo.feasible && !solo.current_only) {
        out.solo = solo;
        out.target = solo.target;
        out.rate = solo.rate;
        out.clear_time = solo.clear_ticks;
        out.total_time = solo.total_ticks;
        out.new_gems = solo.new_gems;
        out.recovery_time = solo.recovery_ticks;
        out.ready = solo.ready_now;
        out.prospective_feasible = true;
        out.route_known = true;
        return out;
    }
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
    std::vector<CampContributor> contributors;
    for (const auto &body : crew) {
        const Actor *actor = body.id == w.self.id ? &w.self : nullptr;
        for (const auto &ally : w.allies)
            if (ally.id == body.id)
                actor = &ally;
        if (actor)
            contributors.push_back(
                {body, actor->pos.x, actor->pos.y, actor->hp, actor->camp_mitigation,
                 actor->id == w.self.id ? enemy_reply : coarse_farm_enemy_reply(w, *actor)});
    }
    std::vector<CampPressure> monsters;
    if (!(live.fresh(w.round) && live.state == Lifecycle::Reward))
        for (const auto &spawn : g.spawns) {
            if (live.fresh(w.round) && std::find(live.known_dead.begin(), live.known_dead.end(),
                                                 spawn.id) != live.known_dead.end())
                continue;
            const auto seen = std::find_if(live.camps.begin(), live.camps.end(),
                                           [&](const Camp &c) { return c.id == spawn.id; });
            if (live.fresh(w.round) && seen != live.camps.end())
                monsters.push_back({seen->pos.x, seen->pos.y, seen->range, seen->strength, true});
            else
                monsters.push_back({spawn.pos.x, spawn.pos.y, 0, spawn.strength, false});
        }
    auto squad = minimum_ready_camp_squad(contributors, w.self.id, hp, monsters);
    double dps = 0;
    for (const auto &body : crew)
        dps += body.dps;
    if (squad.ready)
        dps = squad.dps;
    const int bodies = squad.ready ? squad.ids.size() : crew.size();
    const double clear = std::ceil(hp / std::max(1.0, dps));
    bool ready = squad.ready;
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
    cost.new_gold = score_resource_gold(g.gems, static_cast<double>(g.gold) / recipients);
    const int speed = std::max(1, w.self.move_speed);
    cost.time = std::ceil(nearest / speed) + clear + bc::constants::capture_time + 1 +
                ((g.gems || w.self.gems)
                     ? std::ceil(double(altar) / speed) +
                           current_tribute_ticks(w.self.gems + static_cast<int>(cost.new_gems))
                     : 0) +
                recover;
    const int enemy_home = w.geo.at(w.geo.enemy_home, target);
    if (home != unreachable && enemy_home != unreachable && enemy_home < home)
        cost.time += std::min(8.0, (home - enemy_home) / double(std::max(1, w.self.move_speed)));
    if (w.warning_near(target, 3))
        cost.time += 3;
    cost.feasible = true;
    out.target = target;
    const auto route_steps = w.geo.cached_steps(w.self.pos, target);
    out.route_known = route_steps && *route_steps != unreachable;
    out.rate = out.gold_fallback
                   ? (static_cast<double>(g.gold) / recipients) / std::max(1.0, cost.time)
                   : cycle_rate(w.self.gems, cost, w.round);
    out.clear_time = clear;
    out.total_time = cost.time;
    out.new_gems = cost.new_gems;
    out.recovery_time = recover;
    out.ready =
        ready &&
        !(solo.known && crew.size() == 1); // An accurate failed reserve proof overrides coarse DPS.
    // Exclude jobs that cannot convert before the horizon, without inventing
    // future gems from a gold-only investment candidate.
    if (resource_has_bank(g.gems, w.self.gems) && w.round + cost.time >= bc::constants::max_rounds)
        out.rate = 0;
    if (live.fresh(w.round) && live.state == Lifecycle::Respawning)
        out.rate /= 1 + std::max(0, live.respawn_ticks - static_cast<int>(nearest));
    return out;
}
// A committed singleton already has a complete kit/reserve certificate. Reusing
// it for one actual stationary action avoids another global ranking/crew search.
inline std::optional<Proposal> solo_clear_followup(World &w, Memory &m,
                                                   const SoloFarmQuote *prepaid = nullptr) {
    const int gi = m.mission.group;
    if (m.mission.phase != Phase::Clear || gi < 0 || gi >= static_cast<int>(w.groups.size()))
        return std::nullopt;
    const auto quote =
        prepaid && current_solo_quote(w, *prepaid, gi) ? *prepaid : quote_current_solo_clear(w, gi);
    if (!quote.known || !quote.feasible || quote.stage != w.self.pos ||
        !current_solo_quote(w, quote, gi) || !fuel(13000) ||
        (!quote.current_only && !farm_safe(w, gi)))
        return std::nullopt;
    const auto &view = w.groups[gi];
    if (!view.fresh(w.round) || view.state != Lifecycle::Alive || view.camps.size() != 1)
        return std::nullopt;
    const auto &camp = view.camps.front();
    Mission job = m.mission;
    job.target = camp.pos;
    job.rate = quote.rate;
    job.expiry = w.round + Settings::job_lease;
    job.assembly_pending = false;
    if (job.last_camp_hp < 0 || camp.hp < job.last_camp_hp) {
        job.last_progress = w.round;
        job.stagnant = 0;
    }
    job.last_camp_hp = camp.hp;
    Action action;
    if (w.self.can_attack && distance(w.self.pos, camp.pos) <= w.self.range) {
        action.kind = Kind::BasicCamp;
        action.target = camp.id;
        action.reason = "farm-certified-solo-live-basic";
    } else if (w.self.can_cast) {
        double gain = 0;
        for (const auto &spell : w.spells)
            if (spell.ready && spell.camps &&
                (spell.kind == 2 || spell.kind == 3 || spell.kind == 4) &&
                distance(w.self.pos, camp.pos) <= spell.range &&
                std::min(camp.hp, spell.amount) > gain) {
                gain = std::min(camp.hp, spell.amount);
                action.kind = Kind::CastCamp;
                action.slot = spell.slot;
                action.target = camp.id;
                action.reason = "farm-certified-solo-useful-damage";
            }
        if (gain <= 0 && !w.self.can_attack && distance(w.self.pos, camp.pos) <= w.self.range)
            for (const auto &spell : w.spells)
                if (spell.ready && spell.kind == 1 && spell.self && bc::fuel_remaining() >= 28000) {
                    action.kind = Kind::CastSelf;
                    action.slot = spell.slot;
                    action.target = camp.id;
                    action.reason = "farm-certified-solo-live-reset";
                    break;
                }
    }
    if (action.kind == Kind::None) {
        if (quote.ready_now)
            return std::nullopt;
        action.reason = "farm-certified-next-owner-hold";
    }
    return economic(action, job, Priority::Incumbent, quote.rate);
}
inline SoloResetReceipt make_solo_reset_receipt(World &w, const Mission &selected,
                                                const Action &action) {
    SoloResetReceipt out;
    if (action.kind != Kind::CastSelf || !action.reason ||
        std::string_view(action.reason) != "farm-certified-solo-live-reset" ||
        selected.phase != Phase::Clear || selected.group < 0 ||
        selected.group >= static_cast<int>(w.groups.size()) || action.slot < 0 || action.slot > 1 ||
        bc::fuel_remaining() < 26000 || w.round != static_cast<int>(bc::round_number()))
        return out;
    const auto &view = w.groups[selected.group];
    const auto &spell = w.spells[action.slot];
    if (!w.self.alive || w.self.can_attack || !w.self.can_cast || w.self.channel != Channel::None ||
        !view.fresh(w.round) || view.state != Lifecycle::Alive || view.camps.size() != 1 ||
        action.target != view.camps.front().id || !spell.ready || spell.kind != 1 || !spell.self ||
        distance(w.self.pos, view.camps.front().pos) > w.self.range)
        return out;
    out.valid = true;
    out.owner = w.self.id;
    out.round = w.round;
    out.serial = w.serial;
    out.group = selected.group;
    out.slot = action.slot;
    out.actor = w.self;
    out.camp = view.camps.front();
    return out;
}
inline std::optional<Proposal>
solo_reset_basic_followup(World &w, Memory &m, SoloResetReceipt &receipt, bool reset_accepted) {
    const bool was_valid = receipt.valid;
    receipt.valid = false; // No retry or second consumer, including rejected proof.
    if (!was_valid || !reset_accepted || bc::fuel_remaining() < 16000 ||
        w.round != static_cast<int>(bc::round_number()) || receipt.round != w.round ||
        receipt.owner != w.self.id || receipt.serial + 1 != w.serial ||
        m.mission.phase != Phase::Clear || m.mission.group != receipt.group || receipt.group < 0 ||
        receipt.group >= static_cast<int>(w.groups.size()))
        return std::nullopt;
    const auto &before = receipt.actor;
    const auto &after = w.self;
    const auto &view = w.groups[receipt.group];
    if (!after.alive || after.stunned || after.channel != Channel::None || !after.can_attack ||
        after.pos != before.pos || after.hp != before.hp || after.max_hp != before.max_hp ||
        after.type != before.type || after.strength != before.strength ||
        after.focus != before.focus || after.range != before.range ||
        after.monster != before.monster || after.camp_mitigation != before.camp_mitigation ||
        !view.fresh(w.round) || view.state != Lifecycle::Alive || view.camps.size() != 1)
        return std::nullopt;
    const auto &camp = view.camps.front();
    if (camp.id != receipt.camp.id || camp.hp != receipt.camp.hp || camp.pos != receipt.camp.pos ||
        camp.strength != receipt.camp.strength || camp.range != receipt.camp.range ||
        distance(after.pos, camp.pos) > after.range)
        return std::nullopt;
    for (int k = 0; k < 2; ++k) {
        const auto &a = before.spells[k];
        const auto &b = after.spells[k];
        if (a.kind != b.kind || a.amount != b.amount || a.range != b.range ||
            a.radius != b.radius || a.recharge != b.recharge || a.scale != b.scale ||
            a.camps != b.camps || a.self != b.self || a.exclusive != b.exclusive ||
            (k != receipt.slot && a.cooldown != b.cooldown))
            return std::nullopt;
    }
    // No other native owner or action intervened. Reset did not damage/heal or
    // move either participant, and the actual restored basic is exactly the
    // extra hit already charged in the selected reset's full-clear certificate.
    Action action;
    action.kind = Kind::BasicCamp;
    action.target = camp.id;
    action.reason = "farm-certified-reset-receipt-basic";
    return economic(action, m.mission, Priority::Incumbent, m.mission.rate);
}
inline std::optional<Proposal> farming(World &w, Memory &m,
                                       const SoloFarmQuote *prepaid = nullptr) {
    if (prepaid && current_solo_quote(w, *prepaid, m.mission.group))
        if (auto followup = solo_clear_followup(w, m, prepaid))
            return followup;
    if (w.geo.groups.empty())
        return std::nullopt;
    if (m.mission.assembly_pending) {
        const auto &job = m.mission;
        bool helper = false;
        for (const auto &a : w.allies)
            helper |= a.id == job.assembly_helper && assembly_detail::available(a);
        const bool invalid = w.round >= job.expiry || !helper || w.warning_near(job.target, 4) ||
                             (w.self.can_move && job.last_progress >= 0 &&
                              w.round - job.last_progress >= Settings::assembly_wait);
        if (invalid) {
            m.assembly_failed_group = job.group;
            m.assembly_failed_signature = job.assembly_signature;
            m.failed_group = job.group;
            m.failed_until = w.round + Settings::job_lease;
            m.mission = {};
        }
    }
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
    CampRanking ranking, gold_fallback_ranking;
    const bool continuing =
        m.mission.group >= 0 && m.mission.group < static_cast<int>(w.groups.size()) &&
        w.round < m.mission.expiry &&
        !(m.failed_group == m.mission.group && w.round < m.failed_until) &&
        !(w.groups[m.mission.group].fresh(w.round) &&
          w.groups[m.mission.group].state == Lifecycle::Respawning) &&
        resource_job_eligible(w.geo.groups[m.mission.group].gems, w.self.gems, w.geo.monolith_only,
                              w.groups[m.mission.group].fresh(w.round) &&
                                  w.groups[m.mission.group].state == Lifecycle::Reward &&
                                  w.on_group(m.mission.group, w.self.pos)) &&
        w.geo.estimate(w.self.pos, m.mission.target) != unreachable;
    auto offer = [&](int gi, double score) {
        const auto &g = w.geo.groups[gi];
        const double ticks = std::ceil(g.initial_hp / std::max(1.0, w.self.strength));
        const bool affordable =
            ticks * g.initial_strength * w.self.camp_mitigation + 1 < w.self.hp * .75;
        const bool reward = w.groups[gi].fresh(w.round) && w.groups[gi].state == Lifecycle::Reward;
        const auto purpose = resource_job_purpose(g.gems, w.self.gems, w.geo.monolith_only,
                                                  reward && w.on_group(gi, w.self.pos));
        if (purpose == ResourcePurpose::Ineligible)
            return;
        auto &destination =
            purpose == ResourcePurpose::MonolithFallback ? gold_fallback_ranking : ranking;
        destination.offer({gi, score}, reward, affordable);
    };
    if (continuing)
        offer(m.mission.group, m.mission.rate);
    if (!continuing && !w.prepare_farm_geometry_scores())
        return std::nullopt; // Partial immutable cache is not a full-map shortlist.
    for (unsigned i = 0; !continuing && i < w.geo.groups.size(); ++i) {
        if (m.failed_group == static_cast<int>(i) && w.round < m.failed_until)
            continue;
        const auto &cached = w.farm_geometry_scores[i];
        const int d = cached.distance;
        if (d == unreachable)
            continue;
        const auto &history = w.groups[i];
        if (history.state == Lifecycle::Respawning && history.seen >= 0 &&
            history.respawn_ticks - (w.round - history.seen) > d)
            continue; // Earliest possible respawn; hidden occupancy may only delay it.
        // Live alternatives dominate waiting on a known unavailable reward.
        // Reconsider after the public lifecycle changes rather than idling.
        if (w.groups[i].fresh(w.round) && w.groups[i].state == Lifecycle::Respawning)
            continue;
        const bool reward = w.groups[i].fresh(w.round) && w.groups[i].state == Lifecycle::Reward;
        const auto purpose =
            resource_job_purpose(w.geo.groups[i].gems, w.self.gems, w.geo.monolith_only,
                                 reward && w.on_group(i, w.self.pos));
        if (purpose == ResourcePurpose::Ineligible ||
            !resource_new_job_eligible(w.geo.groups[i].gems, w.self.gems, w.geo.monolith_only,
                                       reward && w.on_group(i, w.self.pos),
                                       static_cast<int>(i) == m.mission.group))
            continue;
        auto &destination =
            purpose == ResourcePurpose::MonolithFallback ? gold_fallback_ranking : ranking;
        destination.offer({static_cast<int>(i), reward ? cached.reward : cached.alive}, reward,
                          cached.damage < w.self.hp * .75);
    }
    const bool incumbent_suppressed = m.mission.group == m.failed_group && w.round < m.failed_until;
    const bool retain_incumbent =
        !incumbent_suppressed && m.mission.group >= 0 &&
        m.mission.group < static_cast<int>(w.groups.size()) &&
        !(w.groups[m.mission.group].fresh(w.round) &&
          w.groups[m.mission.group].state == Lifecycle::Respawning) &&
        resource_job_eligible(w.geo.groups[m.mission.group].gems, w.self.gems, w.geo.monolith_only,
                              w.groups[m.mission.group].fresh(w.round) &&
                                  w.groups[m.mission.group].state == Lifecycle::Reward &&
                                  w.on_group(m.mission.group, w.self.pos));
    // Exactly the prior full-sort shortlist: incumbent, best fresh reward,
    // best solo-affordable group, then best remaining entries until three.
    const auto candidates = ranking.candidates();
    auto shortlist = ranking.shortlist(retain_incumbent ? m.mission.group : -1);
    // Unpriced monolith growth gets one explicit fallback slot, never every
    // score slot. Raw gold/time is compared only within that fallback tier.
    const auto fallback = gold_fallback_ranking.shortlist();
    if (fallback.size() > 0) {
        const int gi = fallback.values[0];
        bool present = false;
        for (int selected : shortlist)
            present |= selected == gi;
        if (!present) {
            if (shortlist.count < shortlist.values.size())
                shortlist.values[shortlist.count++] = gi;
            else
                shortlist.values.back() = gi;
        }
    }
    FarmCandidate best, incumbent;
    for (int gi : shortlist)
        if (fuel(36000)) {
            auto c = evaluate_farm(w, gi, prepaid);
            if (gi == m.mission.group)
                incumbent = c;
            if (c.rate > 0 &&
                resource_candidate_before(c.eligible(), c.gold_fallback, c.rate, best.eligible(),
                                          best.gold_fallback, best.rate))
                best = c;
        }
    if (!incumbent_suppressed && incumbent.rate > 0) {
        const bool travel = m.mission.phase == Phase::Travel || m.mission.phase == Phase::Observe ||
                            m.mission.phase == Phase::Reenter;
        const bool progressing = travel && m.route_round == w.round && m.route_stall < 2;
        // A six-turn lease is a revalidation point, not a travel timeout.
        // An unprepared alternative has only an optimistic geometric bound;
        // it cannot beat a progressing, certified route on that bound alone.
        const bool score_beats_fallback =
            incumbent.gold_fallback && !best.gold_fallback && best.eligible();
        const bool same_currency = incumbent.gold_fallback == best.gold_fallback;
        if (!score_beats_fallback &&
            ((progressing && incumbent.route_known && !best.route_known) ||
             (w.round < m.mission.expiry) ||
             (same_currency && (incumbent.eligible() || !best.eligible() || progressing) &&
              best.rate <= incumbent.rate * Settings::switch_margin)))
            best = incumbent;
    }
    // An expiring lease requests a new continuity check; it never releases the
    // last physical holder merely because another score became larger.
    for (unsigned i = 0; i < w.groups.size(); ++i)
        if (w.groups[i].fresh(w.round) && w.groups[i].state == Lifecycle::Reward &&
            w.on_group(i, w.self.pos) &&
            !(m.failed_group == static_cast<int>(i) && w.round < m.failed_until)) {
            best = evaluate_farm(w, i);
            break;
        }
    const bool holding_cash_reward = best.group >= 0 && w.groups[best.group].fresh(w.round) &&
                                     w.groups[best.group].state == Lifecycle::Reward &&
                                     w.on_group(best.group, w.self.pos);
    if (best.group < 0 || (best.rate <= 0 && !holding_cash_reward))
        return std::nullopt;
    if (!fuel(16000))
        return std::nullopt;
    const int gi = best.group;
    const double best_value = best.gold_fallback ? 0 : best.rate;
    const auto &g = w.geo.groups[gi];
    const auto &view = w.groups[gi];
    // A future-position certificate authorizes only its verified reversible
    // route. It cannot be promoted to an immediate first hit by a second model.
    if (best.prospective_feasible && !best.ready) {
        Mission job = m.mission;
        if (job.group != gi) {
            job = {};
            job.start = job.last_progress = w.round;
            job.last_pos = w.self.pos;
        }
        job.group = gi;
        job.target = best.target; // The actual camp endpoint funds next owner's field.
        job.rate = best_value;
        job.expiry = w.round + Settings::job_lease;
        job.assembly_pending = false;
        Action action;
        if (best.solo.stage == w.self.pos) {
            const bool actual_clear = m.mission.group == gi && m.mission.phase == Phase::Clear;
            if (actual_clear && !farm_safe(w, gi))
                return std::nullopt;
            job.phase = actual_clear ? Phase::Clear : Phase::Travel;
            action.reason = actual_clear ? "farm-certified-next-owner-hold"
                                         : "farm-prospective-permission-wait";
            return economic(action, job, Priority::Incumbent, best_value);
        }
        job.phase = Phase::Travel;
        if (w.self.can_move && fuel(20000)) {
            int next = 0;
            for (int k = 1; k < best.solo.route_length && k <= std::max(1, w.self.move_speed);
                 ++k) {
                const Pos p = best.solo.route[k];
                if (!w.free(p) || !packed_bit(w.visible_bytes, w.geo.index(p)))
                    break;
                next = k;
            }
            if (next > 0 && incoming_damage(w, best.solo.route[next]) < .65 * w.self.hp)
                action = moving(best.solo.route[next], "farm-certified-solo-stage-only");
        }
        return economic(action, job, Priority::Routine, best_value);
    }
    const bool conservative_ready = best.ready;
    LocalAssignment assignment;
    const bool standalone_solo = best.solo.feasible && helpers_for(w, gi, best.target).size() == 1;
    if (!best.gold_fallback && !standalone_solo && view.fresh(w.round) &&
        (view.state == Lifecycle::Reward ||
         (view.state == Lifecycle::Alive &&
          distance(w.self.pos, best.target) <= w.self.range + 1)) &&
        bc::fuel_remaining() >= 48000) {
        assignment = propose_local_assignment(w, gi);
        best.ready = assignment.ready && assignment.self_selected && assignment.locally_accepted;
        if (!assignment.ready && (assignment.uncertain || best.solo.feasible) && conservative_ready)
            best.ready =
                true; // A bounded unknown does not overturn a stricter full-clear certificate.
        if (assignment.ready && assignment.self_selected && assignment.locally_accepted) {
            best.ready = true;
            best.clear_time = assignment.clear_ticks;
        }
        if (assignment.self_role == LocalRole::Split) {
            // Only our own accepted decision releases this job. The crew left
            // behind is actually ready now; no remote claim promises a future hit.
            if (assignment.alternative_bank) {
                if (auto bank = delivery(w, m, true))
                    if (bank->action.kind != Kind::None) {
                        m.failed_group = gi;
                        m.failed_until = w.round + Settings::job_lease;
                        return bank;
                    }
            } else if (assignment.alternative_group >= 0) {
                Mission split;
                split.phase = Phase::Reenter;
                split.target = assignment.alternative_target;
                split.start = w.round;
                split.expiry = w.round + Settings::job_lease;
                Action a;
                if (auto step = w.toward(split.target, w.self.range))
                    if (incoming_damage(w, *step) < w.self.hp * .65) {
                        a = moving(*step, "squad-marginal-helper-released-to-alternative");
                        m.failed_group = gi;
                        m.failed_until = w.round + Settings::job_lease;
                        return economic(a, split, Priority::Routine, assignment.alternative_value);
                    }
            }
            // A priced but dynamically rejected alternative is not a handoff.
            best.ready = conservative_ready;
        }
        if (assignment.self_role == LocalRole::Protector)
            if (auto protect = combat_proposal(w, m, true)) {
                if (protect->action.kind != Kind::None) {
                    protect->mission.phase = Phase::Protect;
                    protect->mission.group = gi;
                    return protect;
                }
            }
    }
    Mission job = m.mission;
    if (job.group != gi) {
        job = {};
        job.start = w.round;
        job.expiry = w.round + Settings::job_lease;
        job.last_progress = w.round;
        job.last_pos = w.self.pos;
    }
    job.group = gi;
    if (job.expiry <= w.round)
        job.expiry = w.round + Settings::job_lease;
    job.target = best.target;
    job.rate = best_value;
    const auto territory = route_context(w, best.target, gi);
    job.intent = territory.intent;
    const bool on = w.on_group(gi, w.self.pos);
    Action a;
    if (view.fresh(w.round) && view.state == Lifecycle::Reward) {
        job.assembly_pending = false;
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
                                return economic(a, job, Priority::Incumbent, best_value);
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
            return economic(a, job, Priority::Incumbent, best_value);
        }
        if (auto step = w.toward(best.target))
            a = moving(*step, "capture-enter-original-region");
        else
            return economic(a, job, Priority::Incumbent, best_value);
        return economic(a, job, Priority::Incumbent, best_value);
    }
    if (!view.fresh(w.round)) {
        job.phase = Phase::Observe;
        if (!w.self.can_move)
            return economic(a, job, Priority::Routine, best_value);
        if (auto step = w.toward(best.target, 2))
            a = moving(*step, "farm-reversible-fresh-observation");
        else if (auto closer = w.toward(best.target))
            a = moving(*closer, "farm-inspect-occluded-original-region");
        else if (w.round - job.last_progress >= Settings::assembly_wait) {
            m.failed_group = gi;
            m.failed_until = w.round + Settings::job_lease;
            return std::nullopt;
        }
        return economic(a, job, Priority::Routine, best_value);
    }
    if (view.state != Lifecycle::Alive)
        return std::nullopt;
    if (!best.ready) {
        const auto sortie = monolith_sortie_exit(w, gi);
        if (sortie.floor > 0 && w.self.hp > sortie.floor) {
            best.ready = true;
            job.sortie_floor = sortie.floor;
            job.sortie_path = sortie.path;
            job.sortie_length = sortie.length;
        }
    }
    if (!best.ready) {
        bool awake = assignment.essential_missing;
        for (const auto &camp : view.camps)
            awake |= camp.awake && camp.hp > 0 && distance(w.self.pos, camp.pos) <= camp.range;
        if (awake) {
            // Losing an essential real contributor while monsters are active
            // invalidates the clear now; it never starts a six-turn wait in fire.
            m.failed_group = gi;
            m.failed_until = w.round + Settings::job_lease;
            if (job.assembly_pending) {
                m.assembly_failed_group = gi;
                m.assembly_failed_signature = job.assembly_signature;
            }
            if (auto protect = combat_proposal(w, m, true))
                if (protect->priority >= Priority::Survival)
                    return protect;
            if (auto escape = escape_action(w)) {
                job.phase = Phase::Escape;
                job.group = -1;
                return economic(*escape, job, Priority::Survival, 1000);
            }
            return recovery(w, m, true);
        }
        if (job.phase != Phase::Assemble)
            job.last_progress = w.round;
        job.phase = Phase::Assemble;
        if (job.assembly_pending) {
            if (auto step = assembly_step(w, job))
                if (fuel(16000) && incoming_damage(w, *step) < w.self.hp * .65)
                    a = moving(*step, "assembly-follow-priced-contribution-route");
            return economic(a, job, Priority::Routine, best_value);
        }
        if (w.round - job.last_progress >= Settings::assembly_wait) {
            m.failed_group = gi;
            m.failed_until = w.round + Settings::job_lease;
            if (job.assembly_pending) {
                m.assembly_failed_group = gi;
                m.assembly_failed_signature = job.assembly_signature;
            }
            return std::nullopt;
        }
        // Enter an actual contribution tile without attacking. An awake camp
        // does not create an absolute geometric exclusion zone: joining a
        // useful range is allowed only when its real next reply is affordable.
        int stage_range = std::max(1, w.self.range);
        if (distance(w.self.pos, best.target) > stage_range)
            if (auto step = w.toward(best.target, stage_range)) {
                if (incoming_damage(w, *step) < w.self.hp * .65)
                    a = moving(*step, "farm-stage-for-real-ready-help");
            }
        return economic(a, job, Priority::Routine, best_value);
    }
    const bool exposed_commit = territory.cutoff_known &&
                                (!territory.exit_known || !territory.walkout) &&
                                territory.enemy_arrival <= best.clear_time + 6;
    if (!farm_safe(w, gi) || exposed_commit) {
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
    job.assembly_pending = false;
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
        return economic(a, job, Priority::Routine, best_value);
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
        return economic(a, job, Priority::Routine, best_value);
    if (!w.self.can_attack)
        for (const auto &s : w.spells)
            if (s.ready && s.kind == 1 && s.self) {
                for (const auto &c : view.camps)
                    if (c.hp > 0 && distance(w.self.pos, c.pos) <= w.self.range) {
                        a.kind = Kind::CastSelf;
                        a.slot = s.slot;
                        a.target = c.id;
                        a.reason = "farm-reset-only-live-followup";
                        return economic(a, job, Priority::Routine, best_value);
                    }
            }
    if (w.self.can_move && assignment.ready)
        if (auto slot = squad_position(w, assignment, gi))
            if (*slot != w.self.pos && incoming_damage(w, *slot) < w.self.hp * .65)
                return economic(moving(*slot, "squad-distinct-support-exit-slot"), job,
                                Priority::Routine, best_value);
    for (const auto &c : view.camps)
        if (c.hp > 0 &&
            (!target || distance(w.self.pos, c.pos) < distance(w.self.pos, target->pos)))
            target = &c;
    if (target && distance(w.self.pos, target->pos) > w.self.range) {
        // The surviving member can differ from the original group tile used
        // for coarse ranking. Persist the actual movement endpoint so that
        // next owner's fresh budget prepares this route, rather than retrying
        // an unfunded field after arbitration forever.
        job.target = target->pos;
        job.phase = Phase::Travel;
    }
    if (target && w.self.can_move)
        if (auto step = w.toward(target->pos, w.self.range)) {
            if (incoming_damage(w, *step) < w.self.hp * .75) {
                a = moving(*step, "farm-legal-contribution-tile");
                job.phase = Phase::Travel;
                return economic(a, job, Priority::Routine, best_value);
            }
        }
    if (!target) {
        // Fresh lifecycle visibility does not imply that a wandering member
        // is personally visible. Missing targets are observation work, never
        // a successful clear or an indefinitely renewed HP-progress event.
        job.phase = Phase::Observe;
        if (m.mission.group == gi)
            job.last_progress = m.mission.last_progress;
        for (const auto &spawn : g.spawns)
            if (!packed_bit(w.visible_bytes, w.geo.index(spawn.pos))) {
                job.target = spawn.pos;
                break;
            }
        if (w.self.can_move && w.round - job.last_progress >= Settings::assembly_wait) {
            m.failed_group = gi;
            m.failed_until = w.round + Settings::job_lease;
            return std::nullopt;
        }
        if (auto step = w.toward(job.target))
            a = moving(*step, "farm-inspect-missing-live-member");
    }
    return economic(a, job, Priority::Routine, best_value);
}
} // namespace tactics

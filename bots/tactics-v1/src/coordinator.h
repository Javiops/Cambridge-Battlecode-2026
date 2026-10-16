#pragma once
#include "deny.h"
#include "economy.h"
#include "log.h"
#include <iostream>
namespace tactics {
inline void observe_hold(World &w, Memory &m) {
    int held = -1;
    for (unsigned i = 0; i < w.groups.size(); ++i)
        if (w.groups[i].fresh(w.round) && w.groups[i].state == Lifecycle::Reward &&
            w.on_group(i, w.self.pos)) {
            held = i;
            break;
        }
    if (held >= 0) {
        if (m.hold_group != held || m.hold_since < 0 ||
            (m.hold_last != w.round && m.hold_last != w.round - 1))
            m.hold_since = w.round;
        for (const auto &e : w.enemies)
            if (w.on_group(held, e.pos))
                m.hold_since = -1; // Contest makes unsupported progress unknown.
        m.hold_group = held;
        m.hold_last = w.round;
    } else {
        m.hold_group = -1;
        m.hold_since = -1;
        m.hold_last = -1;
    }
}
inline void observe_progress(World &w, Memory &m) {
    observe_hold(w, m);
    if (m.observed_round == w.round)
        return;
    if (w.self.alive && w.self.can_move && w.self.channel == Channel::None &&
        route_phase(m.mission.phase) && w.geo.valid(m.mission.target)) {
        const std::vector<std::uint16_t> *field = nullptr;
        if (m.mission.phase == Phase::Recover)
            field = &w.geo.home;
        for (unsigned i = 0; i < w.geo.altars.size(); ++i)
            if (m.mission.target == w.geo.altars[i])
                field = &w.geo.altar_fields[i];
        if (!field)
            for (const auto &[key, candidate] : w.geo.goal_cache)
                if (key.first == w.geo.index(m.mission.target)) {
                    field = &candidate;
                    break;
                }
        if (field && update_route_progress(m, w.self.pos, m.mission.target,
                                           w.geo.at(*field, w.self.pos), w.round)) {
            if (m.mission.group >= 0) {
                m.failed_group = m.mission.group;
                m.failed_until = w.round + Settings::job_lease;
            }
            for (unsigned i = 0; i < w.geo.altars.size(); ++i)
                if (m.mission.target == w.geo.altars[i]) {
                    m.failed_altar = i;
                    m.failed_altar_until = w.round + Settings::job_lease;
                }
            m.mission = {};
            LogLine("T1P").field(w.round).field(w.self.id).field("route-replan-no-progress").emit();
        }
    }
    if (m.prior_alive && w.self.alive && w.self.hp < m.last_hp - .01)
        m.last_damage_round = w.round;
    if (!w.self.alive) {
        m.mission = {};
        m.hold_group = -1;
        m.hold_since = -1;
        w.publish_claim(-1);
    }
    if (m.prior_channel != Channel::None && w.self.channel == Channel::None) {
        const bool returned =
            m.prior_channel == Channel::Recall && w.self.alive && w.in_spawn(w.self.pos);
        const bool banked =
            m.prior_channel == Channel::Tribute && w.self.alive && w.self.gems < m.last_gems;
        LogLine("T1C")
            .field(w.round)
            .field(w.self.id)
            .field(returned || banked ? "completed" : "interrupted")
            .field(static_cast<int>(m.prior_channel))
            .emit();
        if (returned)
            m.last_recall = w.round;
        if (banked) {
            m.last_bank = w.round;
            m.mission = bank_completion_reentry(m.mission, w.round, true);
            if (m.mission.group >= static_cast<int>(w.geo.groups.size()) ||
                (m.failed_group == m.mission.group && w.round < m.failed_until))
                m.mission = {};
        }
    }
    if (m.mission.group >= 0 && m.mission.group < static_cast<int>(w.groups.size())) {
        auto &view = w.groups[m.mission.group];
        if (view.fresh(w.round) && view.state == Lifecycle::Respawning) {
            bool chain = m.mission.chain_used;
            LogLine("T1R")
                .field(w.round)
                .field(w.self.id)
                .field(m.mission.group)
                .field(std::max(0, w.self.gems - m.last_gems))
                .emit();
            m.mission = {};
            m.mission.chain_used = chain;
            m.mission.bank_after_reward = chain && w.self.gems > 0;
        }
    }
    m.observed_round = w.round;
}
inline bool useful_channel_cancel(World &w, int remaining) {
    if (w.self.stunned || remaining <= 0 || !fuel(30000) ||
        w.round != static_cast<int>(bc::round_number()))
        return false;
    auto blocked = w.geo.static_blocked | w.occupied;
    blocked.set(sdk(w.self.pos), false);
    const double staying = incoming_damage(w, w.self.pos, std::max(1, remaining));
    if (w.round != static_cast<int>(bc::round_number()))
        return false;
    for (auto p :
         blocked.reachable_tiles(sdk(w.self.pos), std::max(1, w.self.move_speed)).positions()) {
        if (!fuel(18000) || w.round != static_cast<int>(bc::round_number()))
            break;
        Pos q = position(p);
        if (q != w.self.pos && w.free(q)) {
            const double risk = incoming_damage(w, q);
            if (w.round != static_cast<int>(bc::round_number()))
                return false;
            if (risk < std::min(staying, w.self.hp))
                return true;
        }
    }
    return false;
}
inline Proposal channel_decision(World &w, Memory &m) {
    Mission job = m.mission;
    job.phase = Phase::Channel;
    Action a;
    a.reason = "channel-retain-pending-completion";
    if (w.self.channel == Channel::Teleport)
        return economic(a, job, Priority::ActiveChannel, 10000);
    int remaining = std::max(0, w.self.channel_ticks);
    bool lethal = incoming_damage(w, w.self.pos, std::max(1, remaining)) >= w.self.hp;
    bool interrupted = channel_interruption_risk(w, remaining, w.self.channel == Channel::Tribute);
    // Pending-zero finishes at our next owner start; it is not cancelled just
    // because an HP heuristic changed after the starting command.
    const bool wins = w.self.channel == Channel::Tribute &&
                      w.own_score + w.self.gems >= static_cast<int>(bc::constants::winning_gems);
    bool completes_first = remaining == 0 || (!interrupted && !lethal);
    // A safe retained channel needs no hypothetical escape enumeration. Fund
    // that optional search only when an actual risk can justify cancellation.
    bool cancel = (lethal || interrupted) && (!wins || !completes_first) &&
                  useful_channel_cancel(w, remaining);
    if (!retains_channel(w.self.channel, lethal, interrupted, cancel)) {
        a.kind = w.self.channel == Channel::Recall ? Kind::CancelRecall : Kind::CancelTribute;
        a.reason = "channel-cancel-for-useful-escape";
        job.phase = Phase::Escape;
        job.group = -1;
    }
    return economic(a, job, Priority::ActiveChannel, 10000);
}
inline std::optional<Proposal> choose_mission(World &w, Memory &m) {
    if (!w.self.alive)
        return std::nullopt;
    if (w.self.channel != Channel::None)
        return channel_decision(w, m);
    if (m.mission.sortie_length > 0) {
        const int gi = m.mission.group;
        const bool cleared = gi >= 0 && gi < int(w.groups.size()) && w.groups[gi].fresh(w.round) &&
                             w.groups[gi].state != Lifecycle::Alive;
        if (cleared) {
            m.mission.sortie_length = 0;
            m.mission.sortie_floor = 0;
        } else if (m.mission.sortie_exiting || w.self.hp <= m.mission.sortie_floor) {
            m.mission.sortie_exiting = true;
            int at = -1;
            for (int i = 0; i < m.mission.sortie_length; ++i)
                if (m.mission.sortie_path[i] == w.self.pos)
                    at = i;
            if (at < 0) {
                // A displacement invalidates the priced exit. Rebuild the
                // bounded local path, rather than recall toward a different
                // direction while still inside the monster's attack ring.
                const auto exit = gi >= 0 ? monolith_sortie_exit(w, gi) : SortieExit{};
                if (exit.length > 0) {
                    m.mission.sortie_path = exit.path;
                    m.mission.sortie_length = exit.length;
                    at = 0;
                }
            }
            if (at >= 0 && at + 1 < m.mission.sortie_length) {
                Mission job = m.mission;
                job.phase = Phase::Escape;
                if (w.self.can_move) {
                    const auto next = job.sortie_path[at + 1];
                    if (w.free(next) && incoming_damage(w, next) < w.self.hp)
                        return economic(moving(next, "monolith-follow-priced-exit"), job,
                                        Priority::Survival, 1000);
                }
                return economic(Action{}, job, Priority::Survival, 1000);
            }
            if (at >= 0) {
                m.mission.sortie_length = 0;
                m.mission.sortie_floor = 0;
            }
            if (auto return_now = recovery(w, m, true))
                return return_now;
        }
    }
    auto bank = delivery(w, m);
    if (bank && bank->priority == Priority::Deciding && bank->action.kind != Kind::None)
        return bank;
    // A bank commitment cannot override the phase that completes a real
    // return. Leaving spawn before its end-of-turn heal creates Recall loops
    // at the same HP. A safe ready tribute can finish before ordinary recovery;
    // an actual reward holder is handled by the capture contract below.
    if (w.in_spawn(w.self.pos) && w.self.health_fraction() < Settings::spawn_ready) {
        // A one-phase full spawn heal is normally cheaper than a weak trip.
        // Depart below the fallback threshold only for an affordable timed
        // mission whose contested window is lost by waiting that phase.
        if (w.self.health_fraction() >= Settings::ordinary_heal && bc::fuel_remaining() > 65000)
            if (auto timely = farming(w, m)) {
                const auto context =
                    route_context(w, timely->mission.target, timely->mission.group);
                if (timely->action.kind == Kind::Move &&
                    context.enemy_arrival <=
                        w.geo.estimate(w.self.pos, timely->mission.target) + 1 &&
                    timely->mission.phase != Phase::Assemble)
                    return timely;
            }
        return recovery(w, m, true);
    }
    if (m.hold_group < 0 && w.self.health_fraction() < Settings::ordinary_heal &&
        (!bank || bank->action.kind != Kind::Tribute)) {
        // The ordinary healing threshold is a fallback, not a mid-clear
        // cancellation of a freshly certified affordable singleton. Finish
        // only the actual incumbent at its current contribution tile, with
        // full reserve and hard next-reply safety; never use a future route.
        if (m.mission.phase == Phase::Clear && (!bank || bank->priority != Priority::Deciding) &&
            bc::fuel_remaining() >= 48000) {
            const int group = m.mission.group;
            const auto quote = quote_solo_farm(w, group);
            if (quote.known && quote.feasible && quote.stage == w.self.pos &&
                current_solo_quote(w, quote, group))
                if (auto finish = solo_clear_followup(w, m, &quote))
                    if (finish->mission.group == group && finish->mission.phase == Phase::Clear)
                        return finish;
        }
        if (auto heal = recovery(w, m, true)) {
            note_failed_bank_window(w, m);
            return heal;
        }
    }
    bool immediate_deciding_enemy = false;
    for (const auto &enemy : w.enemies)
        immediate_deciding_enemy |= enemy.channel == Channel::Tribute &&
                                    w.enemy_score + enemy.gems >= int(bc::constants::winning_gems);
    if (immediate_deciding_enemy || w.exposure(w.self.pos) >= w.self.hp + w.self.shield)
        if (auto urgent =
                combat_proposal(w, m, false, std::max(40000, int(bc::fuel_remaining()) - 8000)))
            if (urgent->priority >= Priority::Survival)
                return urgent;
    // Delivery is a committed complete-cycle job, not a proposal that must
    // survive another full farm search every owner turn. Its action has just
    // passed fresh route, bag, deadline and survival validation.
    if (bank && m.mission.phase == Phase::Deliver && bank->action.kind != Kind::None)
        return bank;
    if (bank && bc::fuel_remaining() < 60000)
        return bank;
    if (!fuel(26000))
        return bank;
    bool opposition = !w.enemies.empty();
    for (const auto &sight : w.sightings)
        opposition |= sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round);
    const int combat_floor = std::max(50000, int(bc::fuel_remaining()) - 10000);
    auto fight = opposition ? combat_proposal(w, m, false, combat_floor) : peaceful_support(w, m);
    if (fight && fight->priority >= Priority::Survival)
        return fight;
    // Each later phase needs its own budget. A declined expensive fight may
    // end this opportunity; it must not fall through to an unsafe farm helper.
    if (!fuel(34000))
        return fight ? fight : bank;
    // An ordinary HP recall must not empty a live capture. The camp policy
    // applies supported overlap or retains the real holder through payout.
    if (m.hold_group >= 0) {
        bool contest = false;
        for (const auto &e : w.enemies)
            contest |= w.on_group(m.hold_group, e.pos);
        if (contest && fight && fight->action.kind != Kind::None)
            return fight;
        if (contest && w.round - m.mission.start >= Settings::assembly_wait) {
            m.failed_group = m.hold_group;
            m.failed_until = w.round + Settings::job_lease;
        } else if (auto capture = farming(w, m)) {
            if (capture->mission.phase == Phase::Collect) {
                const auto kind = fight ? fight->action.kind : Kind::None;
                if (capture->action.kind == Kind::None && fight &&
                    (kind == Kind::BasicChampion || kind == Kind::CastChampion ||
                     kind == Kind::CastSelf)) {
                    fight->mission = capture->mission;
                    return fight;
                }
                return capture;
            }
        }
    }
    if (!fuel(34000))
        return fight ? fight : bank;
    if (auto heal = recovery(w, m)) {
        if (w.self.health_fraction() < Settings::ordinary_heal)
            note_failed_bank_window(w, m);
        return heal;
    }
    if (bank && bank->action.kind == Kind::Tribute)
        return bank; // Ready safe conversion before a discretionary volley.
    if (!fuel(34000))
        return fight ? fight : bank;
    // Price one local rendezvous before the global farm scan spends its
    // allowance. The quote is prospective; only farming's fresh, actual crew
    // check can authorize a first hit after the handshake.
    if (!m.mission.assembly_pending && !m.mission.chain_used && !m.mission.bank_after_reward &&
        m.mission.group >= 0 && m.mission.rate > 0 && m.mission.expiry >= w.round &&
        bc::fuel_remaining() >= 65000)
        if (auto gi = nearby_assembly_group(w, m)) {
            const bool probed =
                m.assembly_probe_group == *gi && w.round - m.assembly_probe_round < 3;
            const double alternative = std::max(m.mission.rate, bank ? bank->mission.rate : 0.0);
            std::optional<AssemblyCandidate> quote;
            if (!probed) {
                m.assembly_probe_group = *gi;
                m.assembly_probe_round = w.round;
                quote = local_assembly_candidate(w, m, *gi, alternative);
            }
            if (quote) {
                Mission job;
                job.phase = Phase::Assemble;
                job.group = quote->group;
                job.target = quote->target;
                job.start = quote->start;
                job.expiry = quote->expiry;
                job.last_progress = w.round;
                job.last_pos = w.self.pos;
                job.rate = quote->rate;
                job.assembly_pending = true;
                job.assembly_signature = quote->signature;
                job.assembly_anchor = quote->anchor_id;
                job.assembly_helper = quote->helper_id;
                job.assembly_route = quote->route;
                job.assembly_route_length = quote->route_length;
                Action action;
                action.reason = "assembly-finite-local-handshake";
                if (w.self.can_move && w.self.pos != quote->stage) {
                    if (auto step = assembly_step(w, job))
                        if (incoming_damage(w, *step) < w.self.hp * .65)
                            action = moving(*step, "assembly-join-observed-local-crew");
                }
                return economic(action, job, Priority::Incumbent, quote->rate);
            }
        }
    auto farm = farming(w, m);
    if (auto deny = denial_proposal(w, m, fight, bank, farm))
        return deny;
    if (bank) {
        if (m.mission.bank_after_reward)
            return bank;
        const bool continuing = m.mission.chain_used && m.mission.group >= 0 &&
                                (m.mission.latest < 0 || w.round < m.mission.latest) && farm &&
                                farm->mission.group == m.mission.group;
        if (continuing)
            return farm;
        if (fuel(18000) && !m.mission.chain_used && farm && farm->mission.group >= 0 &&
            farm->mission.phase != Phase::Assemble) {
            auto extra = evaluate_farm(w, farm->mission.group);
            ChainComparison schedule;
            for (unsigned i = 0; i < w.geo.altars.size(); ++i)
                if (extra.new_gems > 0 && bank->mission.target == w.geo.altars[i]) {
                    const int route = w.geo.at(w.geo.altar_fields[i], extra.target);
                    const auto to_job = w.geo.cached_steps(w.self.pos, extra.target);
                    if (route == unreachable || !to_job || *to_job == unreachable)
                        continue;
                    // The bank may finish at any legal point in this altar's
                    // approach ring. Price the worst cached return leg; never
                    // turn a Chebyshev shortlist bound into a certified trip.
                    int bank_to_job = 0;
                    bool known = true, any = false;
                    const auto altar = w.geo.altars[i];
                    for (int dy = -int(bc::constants::submit_gems_range);
                         dy <= int(bc::constants::submit_gems_range); ++dy)
                        for (int dx = -int(bc::constants::submit_gems_range);
                             dx <= int(bc::constants::submit_gems_range); ++dx) {
                            Pos q{altar.x + dx, altar.y + dy};
                            if (w.geo.blocked(q))
                                continue;
                            const auto d = w.geo.cached_steps(q, extra.target);
                            if (!d || *d == unreachable) {
                                known = false;
                                continue;
                            }
                            any = true;
                            bank_to_job = std::max(bank_to_job, *d);
                        }
                    if (!known || !any)
                        continue;
                    const int speed = std::max(1, w.self.move_speed);
                    schedule = compare_chain(
                        {bank->mission.completion_cost, std::ceil(double(*to_job) / speed),
                         std::ceil(double(bank_to_job) / speed),
                         extra.clear_time + bc::constants::capture_time + 1,
                         std::ceil(double(route) / speed),
                         double(current_tribute_ticks(int(extra.new_gems))),
                         double(current_tribute_ticks(w.self.gems + int(extra.new_gems))),
                         extra.recovery_time},
                        Settings::switch_margin);
                }
            if (extra.ready && schedule.prefer_job &&
                w.round + schedule.job_then_bank < bc::constants::max_rounds) {
                farm->mission.chain_used = true;
                farm->mission.bank_after_reward = false;
                farm->mission.latest =
                    w.round + static_cast<int>(std::ceil(schedule.job_then_bank));
                LogLine("T1J")
                    .field(w.round)
                    .field(w.self.id)
                    .field("one-reward-then-bank")
                    .field(farm->mission.group)
                    .emit();
                return farm;
            }
        }
        // Expired, completed or infeasible chain cannot renew onto another reward.
        return bank;
    }
    if (farm && farm->mission.phase == Phase::Collect) {
        if (farm->action.kind != Kind::None)
            return farm;
        if (fight && fight->action.kind != Kind::Move && fight->action.kind != Kind::CastGround &&
            fight->priority >= Priority::Incumbent) {
            // A stationary compatible protection hit may coexist with holding.
            fight->mission = farm->mission;
            return fight;
        }
        return farm;
    }
    if (fight && fight->priority >= Priority::Incumbent)
        return fight;
    if (farm && farm->valid && farm->action.kind == Kind::None && fight &&
        (fight->action.kind == Kind::CastSelf || fight->action.kind == Kind::CastChampion)) {
        fight->mission = farm->mission;
        return fight;
    }
    if (farm && farm->valid)
        return farm;
    if (bank)
        return bank;
    return fight;
}
inline void remember(World &w, Memory &m) {
    observe_hold(w, m);
    m.prior_alive = w.self.alive;
    m.prior_channel = w.self.channel;
    m.last_hp = w.self.hp;
    m.last_gold = w.gold;
    m.last_gems = w.self.gems;
    m.last_pos = w.self.pos;
}
} // namespace tactics

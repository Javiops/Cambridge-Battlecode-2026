#pragma once
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
    if (w.self.stunned || remaining <= 0)
        return false;
    auto blocked = w.geo.static_blocked | w.occupied;
    blocked.set(sdk(w.self.pos), false);
    const double staying = incoming_damage(w, w.self.pos, std::max(1, remaining));
    for (auto p :
         blocked.reachable_tiles(sdk(w.self.pos), std::max(1, w.self.move_speed)).positions()) {
        if (!fuel(18000))
            break;
        Pos q = position(p);
        if (q != w.self.pos && w.free(q) && incoming_damage(w, q) < std::min(staying, w.self.hp))
            return true;
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
    bool cancel = useful_channel_cancel(w, remaining) && (!wins || !completes_first);
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
    auto bank = delivery(w, m);
    if (bank && bank->priority == Priority::Deciding && bank->action.kind != Kind::None)
        return bank;
    if (!fuel(26000))
        return bank;
    if (w.in_spawn(w.self.pos) && w.self.health_fraction() < Settings::spawn_ready)
        return recovery(w, m, true);
    auto fight = combat_proposal(w, m);
    if (fight && fight->priority >= Priority::Survival)
        return fight;
    // Each later phase needs its own budget. A declined expensive fight may
    // end this opportunity; it must not fall through to an unsafe farm helper.
    if (!fuel(26000))
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
    if (!fuel(26000))
        return fight ? fight : bank;
    if (auto heal = recovery(w, m))
        return heal;
    if (bank && bank->action.kind == Kind::Tribute)
        return bank; // Ready safe conversion before a discretionary volley.
    if (!fuel(26000))
        return fight ? fight : bank;
    auto farm = farming(w, m);
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
            if (extra.ready && extra.rate > bank->mission.rate * Settings::switch_margin &&
                extra.total_time > 0 && w.round + extra.total_time < bc::constants::max_rounds) {
                farm->mission.chain_used = true;
                farm->mission.bank_after_reward = false;
                farm->mission.latest = w.round + static_cast<int>(std::ceil(extra.total_time));
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

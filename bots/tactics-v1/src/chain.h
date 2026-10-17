#pragma once
#include "camp_basic.h"
#include "cycles.h"
namespace tactics {
// These are finite action-plan bounds, not two executable future predictions.
// Bank-first may clear/capture/recover instantaneously when no positive lower
// bound is proved. Independent minimum walking legs may use different altars.
inline ChainComparison compare_chain_conservatively(const ChainSchedule &schedule,
                                                    double acquisition_lower, double recovery_lower,
                                                    double margin) {
    if (!std::isfinite(acquisition_lower) || !std::isfinite(recovery_lower) ||
        acquisition_lower < 0 || acquisition_lower > schedule.acquire || recovery_lower < 0 ||
        recovery_lower > schedule.recover || !std::isfinite(margin) || margin < 1)
        return {};
    auto result = compare_chain(schedule, margin);
    if (!result.known)
        return {};
    result.bank_then_job -= schedule.acquire - acquisition_lower;
    result.bank_then_job -= schedule.recover - recovery_lower;
    result.known = result.bank_then_job > 0 && result.job_then_bank > 0;
    result.prefer_job = result.known && result.job_then_bank * margin < result.bank_then_job;
    return result;
}
struct ChainState {
    int owner = -1, group = -1, altar = -1, initial_bag = 0, new_gems = 0, latest = -1;
    int capture_length = 0, bank_length = 0, probe_round = -1000;
    Pos stage{}, capture{};
    std::array<Pos, 25> capture_path{}, bank_path{};
    bool active() const {
        return owner >= 0 && group >= 0 && altar >= 0;
    }
    void release() {
        const int probe = probe_round;
        *this = {};
        probe_round = probe;
    }
};
inline bool bind_chain_contract(Proposal &proposal, const ChainState &state) {
    if (!proposal.valid || !state.active() || state.latest < 0 ||
        proposal.mission.group != state.group)
        return false;
    proposal.mission.chain_used = true;
    proposal.mission.bank_after_reward = false;
    proposal.mission.latest = state.latest;
    return true; // Never changes an action or its snapshot-local proof flags.
}
inline bool abort_declined_chain(const Actor &self, Memory &m, ChainState &state, Pos altar,
                                 bool actual_holder) {
    if (!state.active() || !m.mission.chain_used || m.mission.bank_after_reward ||
        m.mission.group != state.group || actual_holder || self.channel != Channel::None)
        return false;
    m.mission.phase = Phase::Deliver;
    m.mission.group = -1;
    m.mission.target = altar;
    state.release();
    return true; // This is abort intent, not an accepted bank or new receipt.
}
template <class Funded = CampBasicBudget>
inline BasicCampCertificate chain_basic_certificate(Actor actual, const Camp &camp, Pos stage,
                                                    int elapsed, Funded funded = {}) {
    if (elapsed < 0 || (camp.awake && (elapsed > 0 || stage != actual.pos)))
        return {};
    actual.pos = stage;
    if (elapsed > 0) {
        actual.can_attack = true;
        actual.completed = false;
    }
    const BasicCampBody body{&actual, 0};
    const BasicCampMonster monster{&camp, true};
    return sufficient_basic_clear(std::span(&body, 1), std::span(&monster, 1), actual.id, funded);
}
inline bool chain_capture_window(const ChainState &state, const Memory &m, int now,
                                 bool actual_holder, int capture_ticks, int bank_ticks, int limit) {
    if (now < state.latest)
        return true;
    if (!actual_holder)
        return false;
    const int held = m.hold_since >= 0 ? std::max(0, now - m.hold_since) : 0;
    return held < capture_ticks + 1 &&
           now + std::max(1, capture_ticks + 1 - held) + bank_ticks < limit;
}
inline bool chain_entry_eligible(const Actor &self, const Mission &job, int now, int own_score,
                                 int winning_score, bool holder, bool hostile, bool transaction,
                                 bool active) {
    if (self.id < 0 || !self.alive || self.completed || self.stunned ||
        self.channel != Channel::None || self.gems <= 0 || !std::isfinite(self.hp) ||
        !std::isfinite(self.max_hp) || self.max_hp <= 0 ||
        self.hp < Settings::ordinary_heal * self.max_hp || holder || hostile || transaction ||
        own_score + self.gems >= winning_score || job.phase == Phase::Recover ||
        job.phase == Phase::Channel || job.sortie_length > 0 || job.assembly_pending)
        return false;
    if (active)
        return job.chain_used && !job.bank_after_reward && job.group >= 0 && job.latest > now;
    return self.hp >= .75 * self.max_hp && !job.chain_used && !job.bank_after_reward &&
           job.phase != Phase::Clear && job.phase != Phase::Collect && job.phase != Phase::Deliver;
}
} // namespace tactics
#ifndef TACTICS_CHAIN_MODEL_ONLY
#include "economy.h"
#include "log.h"
namespace tactics {
inline bool chain_funded(const World &w, unsigned floor = 35000) {
    return bc::fuel_remaining() >= floor && w.round == int(bc::round_number());
}
inline bool chain_quiet(const World &w) {
    if (!w.enemies.empty() || w.warning_near(w.self.pos, 6))
        return false;
    for (const auto &sight : w.sightings)
        if (sight.actor.alive && combat_detail::recent_sighting(w.round - sight.round))
            return false;
    return true;
}
struct ChainDanger {
    Pos at{};
    int range = 0;
};
// All route work below is on captured buffers. Polling each neighbor makes
// the native query itself dominate this bounded search. At most16 small
// geometry/danger checks run between polls; every phase also checks epoch.
struct ChainRouteBudget {
    const World &world;
    int left = 0;
    bool valid = true;
    bool tick() {
        if (!valid)
            return false;
        if (left-- > 0)
            return true;
        left = 15;
        valid = chain_funded(world);
        return valid;
    }
};
inline std::optional<std::vector<ChainDanger>> chain_danger(const World &w, int selected) {
    if (!chain_funded(w))
        return std::nullopt;
    std::vector<ChainDanger> danger;
    for (int gi = 0; gi < int(w.groups.size()); ++gi) {
        if (bc::fuel_remaining() < 35000)
            return std::nullopt;
        if (gi == selected)
            continue;
        const auto &view = w.groups[gi];
        if (view.fresh(w.round) && view.state != Lifecycle::Alive)
            continue;
        for (const auto &s : w.geo.groups[gi].spawns)
            if (s.strength > 0) {
                if (danger.size() >= 128)
                    return std::nullopt;
                danger.push_back({s.pos, s.range});
            }
        for (const auto &c : view.camps)
            if (c.hp > 0 && c.strength > 0) {
                if (danger.size() >= 128)
                    return std::nullopt;
                danger.push_back({c.pos, c.range});
            }
    }
    return chain_funded(w) ? std::optional(std::move(danger)) : std::nullopt;
}
// A planned dead selected monster alone may unblock its capture tile. Other
// public or observed damaging camps stay a conservative route exclusion.
inline bool chain_route_square(const World &w, Pos at, int selected,
                               std::span<const ChainDanger> danger, ChainRouteBudget &budget) {
    if (!budget.tick() || !w.geo.valid(at) || w.geo.blocked(at) ||
        !packed_bit(w.visible_bytes, w.geo.index(at)) || w.warning_near(at, 3))
        return false;
    if (at != w.self.pos && !w.free(at)) {
        bool selected_camp = false;
        for (const auto &camp : w.groups[selected].camps)
            selected_camp |= camp.pos == at && camp.hp > 0;
        if (!selected_camp)
            return false;
    }
    for (const auto &source : danger) {
        if (!budget.tick())
            return false;
        if (distance(source.at, at) <= source.range)
            return false;
    }
    return true;
}
inline bool chain_paths_current(const World &w, const ChainState &state,
                                std::span<const ChainDanger> danger, bool include_bank = true) {
    if (state.capture_length < 1 || state.capture_length > 25 ||
        (include_bank && (state.bank_length < 1 || state.bank_length > 25)))
        return false;
    ChainRouteBudget budget{w};
    for (int k = 0; k < state.capture_length; ++k)
        if (!chain_route_square(w, state.capture_path[k], state.group, danger, budget))
            return false;
    for (int k = 0; include_bank && k < state.bank_length; ++k)
        if (!chain_route_square(w, state.bank_path[k], state.group, danger, budget))
            return false;
    return chain_funded(w);
}
inline BasicCampCertificate chain_basic_upper(World &w, const SoloFarmQuote &quote) {
    if (!chain_funded(w) || quote.mode != SoloFarmMode::Combined ||
        w.groups[quote.group].camps.size() != 1)
        return {};
    return chain_basic_certificate(w.self, w.groups[quote.group].camps.front(), quote.stage,
                                   quote.arrival_ticks,
                                   [&] { return bc::fuel_remaining() >= 35000; });
}
// Materialize one currently observed legal shortest gradient. Missing/blocked
// legs are Unknown. No partial route is inserted into the global field cache.
inline bool chain_bank_route(World &w, ChainState &state, int altar,
                             std::span<const ChainDanger> danger) {
    if (altar < 0 || altar >= int(w.geo.altar_fields.size()) || !chain_funded(w))
        return false;
    const auto &field = w.geo.altar_fields[altar];
    Pos current = state.capture;
    int remaining = w.geo.at(field, current);
    if (remaining == unreachable || remaining >= 25)
        return false;
    state.bank_length = 1;
    state.bank_path[0] = current;
    ChainRouteBudget budget{w};
    while (remaining > 0 && state.bank_length < 25) {
        if (!budget.tick())
            return false;
        Pos next;
        int best = remaining;
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                Pos p{current.x + dx, current.y + dy};
                if ((!dx && !dy) || !w.geo.valid(p))
                    continue;
                const int value = w.geo.at(field, p);
                if (value < best && chain_route_square(w, p, state.group, danger, budget)) {
                    next = p;
                    best = value;
                }
            }
        if (next.x < 0)
            return false;
        current = next;
        remaining = best;
        state.bank_path[state.bank_length++] = current;
    }
    if (remaining != 0 ||
        distance(current, w.geo.altars[altar]) > bc::constants::submit_gems_range ||
        !chain_funded(w))
        return false;
    state.altar = altar;
    return true;
}
inline std::optional<Proposal> chain_capture_proposal(World &w, Memory &m, ChainState &state) {
    if (!state.active() || state.owner != w.self.id || !m.mission.chain_used ||
        m.mission.bank_after_reward || m.mission.group != state.group || !chain_funded(w, 22000) ||
        !chain_quiet(w))
        return std::nullopt;
    const auto &view = w.groups[state.group];
    if (!view.fresh(w.round) || view.state != Lifecycle::Reward)
        return std::nullopt;
    const int speed = std::max(1, w.self.move_speed);
    const int bank_ticks = (state.bank_length - 1 + speed - 1) / speed +
                           current_tribute_ticks(w.self.gems + state.new_gems);
    if (!chain_capture_window(state, m, w.round, w.self.pos == state.capture,
                              bc::constants::capture_time, bank_ticks, bc::constants::max_rounds))
        return std::nullopt;
    Mission job = m.mission;
    job.phase = Phase::Collect;
    job.latest = state.latest;
    job.target = state.capture;
    Action action;
    action.reason = "chain-retain-actual-single-tile-capture";
    if (w.self.pos != state.capture) {
        const auto danger = chain_danger(w, state.group);
        if (!danger)
            return std::nullopt;
        int cursor = -1;
        for (int k = 0; k < state.capture_length; ++k)
            if (state.capture_path[k] == w.self.pos)
                cursor = k;
        if (cursor < 0 || !w.self.can_move)
            return std::nullopt;
        int next = cursor;
        ChainRouteBudget budget{w};
        for (int k = cursor + 1;
             k < state.capture_length && k <= cursor + std::max(1, w.self.move_speed); ++k) {
            if (!chain_route_square(w, state.capture_path[k], state.group, *danger, budget))
                break;
            next = k;
        }
        if (next == cursor)
            return std::nullopt;
        action = moving(state.capture_path[next], "chain-enter-actual-reward-region");
    }
    if (!chain_funded(w, 22000) ||
        incoming_damage(w, action.kind == Kind::Move ? action.at : w.self.pos) >= w.self.hp)
        return std::nullopt;
    return economic(action, job, Priority::Incumbent, job.rate);
}
inline std::optional<Proposal> completed_chain_bank(World &w, Memory &m, ChainState &state) {
    if (!state.active() || !m.mission.chain_used || !m.mission.bank_after_reward ||
        w.self.gems <= state.initial_bag || !chain_funded(w, 30000) || !chain_quiet(w))
        return std::nullopt;
    const Pos altar = w.geo.altars[state.altar];
    const int steps = w.geo.at(w.geo.altar_fields[state.altar], w.self.pos);
    if (steps == unreachable || !packed_bit(w.visible_bytes, w.geo.index(altar)))
        return std::nullopt;
    const auto lock = w.enemy_lock(altar);
    if (!chain_funded(w, 26000))
        return std::nullopt;
    const int hits = lock ? lock->hits_remaining() : 0;
    const int turns = (steps + std::max(1, w.self.move_speed) - 1) / std::max(1, w.self.move_speed);
    return delivery_at(w, m,
                       {state.altar, turns, hits,
                        double(turns + hits + current_tribute_ticks(w.self.gems)), bool(lock)},
                       true);
}
inline std::optional<Proposal> early_chain_proposal(World &w, Memory &m, ChainState &state,
                                                    bool transaction = false) {
    if (!w.self.alive || w.self.channel != Channel::None || w.self.stunned || transaction ||
        w.self.gems <= 0 || w.self.health_fraction() < Settings::ordinary_heal ||
        w.own_score + w.self.gems >= int(bc::constants::winning_gems) || !chain_quiet(w))
        return std::nullopt;
    if (m.mission.bank_after_reward)
        return completed_chain_bank(w, m, state);
    const bool active = state.active() && state.owner == w.self.id && m.mission.chain_used &&
                        m.mission.group == state.group;
    if (active && w.groups[state.group].fresh(w.round) &&
        w.groups[state.group].state == Lifecycle::Reward)
        return chain_capture_proposal(w, m, state);
    if (!chain_entry_eligible(w.self, m.mission, w.round, w.own_score,
                              int(bc::constants::winning_gems), m.hold_group >= 0, false,
                              transaction, active))
        return std::nullopt;
    if (active) {
        const auto danger = chain_danger(w, state.group);
        if (!danger)
            return std::nullopt;
        if (state.latest <= w.round ||
            !chain_funded(w, m.mission.phase == Phase::Clear ? 35000 : 44000) ||
            !chain_paths_current(w, state, *danger))
            return std::nullopt;
        auto quote = m.mission.phase == Phase::Clear ? quote_current_solo_clear(w, state.group)
                                                     : quote_solo_basic_farm(w, state.group);
        if (!quote.known || !quote.feasible || quote.stage != state.stage ||
            !current_solo_quote(w, quote, state.group))
            return std::nullopt;
        const auto basic = chain_basic_upper(w, quote);
        const int speed = std::max(1, w.self.move_speed);
        const double remaining =
            quote.arrival_ticks + basic.ticks + (state.capture_length - 1 + speed - 1) / speed +
            bc::constants::capture_time + 1 + (state.bank_length - 1 + speed - 1) / speed +
            current_tribute_ticks(w.self.gems + state.new_gems);
        if (!basic.ready || basic.remaining_hp[0] < Settings::ordinary_heal * w.self.max_hp ||
            w.round + remaining > state.latest)
            return std::nullopt;
        auto proposal = solo_farm_proposal(w, m, quote);
        if (proposal) {
            if (!bind_chain_contract(*proposal, state))
                return std::nullopt;
            if (proposal->action.kind == Kind::Move)
                proposal->action.reason = "chain-early-funded-stage-move";
        }
        return proposal;
    }
    if (m.mission.chain_used || state.probe_round > w.round - 3 || !chain_funded(w, 56000))
        return std::nullopt;
    std::array<int, 2> selected{-1, -1};
    for (int gi = 0; gi < int(w.groups.size()); ++gi) {
        if (bc::fuel_remaining() < 44000)
            break;
        if (!assembly_detail::simple_sleeping(w, gi) || w.geo.groups[gi].gems <= 0 ||
            w.geo.groups[gi].spawns.size() != 1 || w.groups[gi].camps.size() != 1 ||
            !(w.groups[gi].camps.front().pos == w.geo.groups[gi].spawns.front().pos) ||
            (m.failed_group == gi && w.round < m.failed_until))
            continue;
        const int d = distance(w.self.pos, w.groups[gi].camps.front().pos);
        if (d > std::max(1, w.self.range) + 3 * std::max(1, w.self.move_speed))
            continue;
        for (int slot = 0; slot < 2; ++slot)
            if (selected[slot] < 0 ||
                d < distance(w.self.pos, w.groups[selected[slot]].camps.front().pos)) {
                if (!slot)
                    selected[1] = selected[0];
                selected[slot] = gi;
                break;
            }
    }
    state.probe_round = w.round;
    for (int gi : selected) {
        if (gi < 0 || !chain_funded(w, 44000))
            break;
        const auto quote = quote_solo_basic_farm(w, gi);
        if (!quote.known || !quote.feasible || quote.current_only || quote.new_gems <= 0 ||
            !current_solo_quote(w, quote, gi))
            continue;
        const auto basic = chain_basic_upper(w, quote);
        if (!basic.ready || basic.remaining_hp[0] < Settings::ordinary_heal * w.self.max_hp ||
            !chain_funded(w))
            continue;
        ChainState plan;
        plan.owner = w.self.id;
        plan.group = gi;
        plan.initial_bag = w.self.gems;
        plan.new_gems = quote.new_gems;
        plan.stage = quote.stage;
        plan.capture = quote.capture;
        if (quote.capture_route_length < 1 || quote.capture_route_length > 25 ||
            quote.capture_route[0] != quote.stage ||
            quote.capture_route[quote.capture_route_length - 1] != quote.capture)
            continue;
        plan.capture_path = quote.capture_route;
        plan.capture_length = quote.capture_route_length;
        const auto danger = chain_danger(w, gi);
        if (!danger)
            continue;
        int altar = -1, best = unreachable;
        for (int i = 0; i < int(w.geo.altars.size()); ++i) {
            const int d = w.geo.at(w.geo.altar_fields[i], quote.capture);
            if (d < best && packed_bit(w.visible_bytes, w.geo.index(w.geo.altars[i]))) {
                best = d;
                altar = i;
            }
        }
        // The constructor validates every chosen bank square against this
        // same immutable snapshot. Do not immediately pay for that walk a
        // second time. Later owners revalidate both retained paths above.
        if (altar < 0 || !chain_paths_current(w, plan, *danger, false) ||
            !chain_bank_route(w, plan, altar, *danger) || !chain_funded(w))
            continue;
        if (w.enemy_lock(w.geo.altars[altar]) || !chain_funded(w))
            continue;
        const int speed = std::max(1, w.self.move_speed);
        const int direct = w.altar_distance(w.self.pos), back = w.altar_distance(quote.stage);
        if (direct == unreachable || back == unreachable)
            continue;
        ChainSchedule schedule;
        schedule.direct_bank =
            double((direct + speed - 1) / speed + current_tribute_ticks(w.self.gems));
        schedule.self_to_job = quote.arrival_ticks;
        schedule.bank_to_job = double((back + speed - 1) / speed);
        schedule.acquire = basic.ticks + double((plan.capture_length - 1 + speed - 1) / speed) +
                           bc::constants::capture_time + 1;
        schedule.job_to_bank = double((plan.bank_length - 1 + speed - 1) / speed);
        schedule.bank_new_bag = current_tribute_ticks(quote.new_gems);
        schedule.bank_combined_bag = current_tribute_ticks(w.self.gems + quote.new_gems);
        const auto comparison =
            compare_chain_conservatively(schedule, 0, 0, Settings::switch_margin);
        if (!comparison.prefer_job ||
            w.round + comparison.job_then_bank >= bc::constants::max_rounds || !chain_funded(w))
            continue;
        auto proposal = solo_farm_proposal(w, m, quote);
        if (!proposal || !chain_funded(w, 22000))
            continue;
        plan.latest = w.round + int(std::ceil(comparison.job_then_bank));
        plan.probe_round = state.probe_round;
        state = plan;
        if (!bind_chain_contract(*proposal, state))
            return std::nullopt;
        if (proposal->action.kind == Kind::Move)
            proposal->action.reason = "chain-early-funded-stage-move";
        LogLine("T1J")
            .field(w.round)
            .field(w.self.id)
            .field("one-reward-funded-early")
            .field(gi)
            .emit();
        return proposal;
    }
    return std::nullopt;
}
} // namespace tactics
#endif

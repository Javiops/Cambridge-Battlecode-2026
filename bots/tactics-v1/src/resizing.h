#pragma once
#include "economy.h"
#include "resizing_policy.h"

namespace tactics {
inline bool resize_funded(const World &w, unsigned floor = 32000) {
    return bc::fuel_remaining() >= floor && w.round == int(bc::round_number());
}
inline bool resize_bank_clear(World &w, Pos at) {
    if (!resize_funded(w) || !packed_bit(w.visible_bytes, w.geo.index(at)) || w.warning_near(at, 4))
        return false;
    const bool locked = bool(w.enemy_lock(at));
    return resize_funded(w) && resize_bank_certificate(true, false, locked);
}
inline bool resize_harmless_singleton(const World &w, int gi) {
    return gi >= 0 && gi < int(w.groups.size()) && gi < int(w.geo.groups.size()) &&
           w.groups[gi].fresh(w.round) && w.groups[gi].state == Lifecycle::Alive &&
           w.groups[gi].camps.size() == 1 && w.geo.groups[gi].spawns.size() == 1 &&
           w.groups[gi].camps.front().hp > 0 && w.groups[gi].camps.front().strength == 0 &&
           w.geo.groups[gi].gems > 0;
}
inline bool resize_gradient_safe(World &w, Pos from, Pos target,
                                 const std::vector<std::uint16_t> &field, int range,
                                 int moving_actor) {
    Pos current = from;
    int steps = w.geo.at(field, from);
    if (steps == unreachable || steps > 25)
        return false;
    for (int used = 0; used <= 25; ++used) {
        if (!resize_funded(w) || !packed_bit(w.visible_bytes, w.geo.index(current)) ||
            potential_camp_pressure(current, w.geo.groups, w.groups, w.round))
            return false;
        if (distance(current, target) <= range)
            return true;
        Pos next;
        int best = steps;
        for (int dy = -1; dy <= 1; ++dy)
            for (int dx = -1; dx <= 1; ++dx) {
                const Pos p{current.x + dx, current.y + dy};
                if ((!dx && !dy) || w.geo.blocked(p) ||
                    !packed_bit(w.visible_bytes, w.geo.index(p)) ||
                    (p != target && (!w.free(p) || (moving_actor != w.self.id && p == w.self.pos))))
                    continue;
                const int d = w.geo.at(field, p);
                if (d < best) {
                    next = p;
                    best = d;
                }
            }
        if (next.x < 0)
            return false;
        current = next;
        steps = best;
    }
    return false;
}
// Actual fixed-tile ordinary basics suffice. Optional casts/resets are not
// required to meet this price. The common controller may use paid, harmless
// extra damage, but the first mutation is the real ordinary basic.
inline std::optional<SoloFarmQuote> resize_basic_alternative(World &w, int gi) {
    if (!resize_funded(w, 44000) || !resize_harmless_singleton(w, gi))
        return std::nullopt;
    const auto &view = w.groups[gi];
    const auto &camp = view.camps.front();
    if (!resize_actor_current_basic(w.self, camp) || w.warning_near(camp.pos, 4) ||
        external_camp_collateral(w.self, view.camps, w.geo.groups, gi, w.groups, w.round))
        return std::nullopt;
    const int steps =
        coordination_detail::cached_distance(w, w.self.pos, w.geo.groups[gi].spawns.front().pos);
    if (steps < 0 || steps == unreachable || steps > 3 * std::max(1, w.self.move_speed))
        return std::nullopt;
    const auto hit = resize_basic_hit_lower(w.self, camp);
    if (!hit || !resize_funded(w))
        return std::nullopt;
    const double ticks = std::ceil(std::max(camp.hp, double(float(camp.hp))) / *hit);
    if (!std::isfinite(ticks) || ticks < 1 || ticks > bc::constants::max_rounds)
        return std::nullopt;
    // No cast, real HP restoration or future shopping is credited.
    SoloClearCertificate clear;
    clear.known = clear.feasible = true;
    clear.clear_ticks = ticks;
    clear.damage_taken = 0;
    clear.remaining_hp = w.self.hp;
    assembly_detail::Arrival arrival;
    arrival.known = true;
    arrival.at = w.self.pos;
    arrival.turns = 0;
    arrival.route[0] = w.self.pos;
    arrival.route_length = 1;
    auto quote = price_solo_cycle(w, gi, arrival, 0, steps, clear, true);
    if (!quote.known || !quote.feasible || !resize_funded(w))
        return std::nullopt;
    SoloLocalRoute none;
    retain_solo_capture_path(w, quote, none);
    if (quote.capture_route_length < 1)
        return std::nullopt;
    for (int k = 0; k < quote.capture_route_length; ++k)
        if (!resize_funded(w) ||
            potential_camp_pressure(quote.capture_route[k], w.geo.groups, w.groups, w.round))
            return std::nullopt;
    int chosen_bank = -1, bank_distance = unreachable;
    for (unsigned i = 0; i < w.geo.altars.size(); ++i) {
        const int d = w.geo.at(w.geo.altar_fields[i], quote.capture);
        if (d < bank_distance) {
            bank_distance = d;
            chosen_bank = int(i);
        }
    }
    if (chosen_bank < 0 || !resize_bank_clear(w, w.geo.altars[chosen_bank]) ||
        !resize_gradient_safe(w, quote.capture, w.geo.altars[chosen_bank],
                              w.geo.altar_fields[chosen_bank], bc::constants::submit_gems_range,
                              w.self.id))
        return std::nullopt;
    if (!resize_funded(w))
        return std::nullopt;
    return quote;
}
inline std::optional<CurrentResizeCycle>
resize_price_current(World &w, int gi, const Actor &collector, std::span<const int> crew_ids) {
    if (crew_ids.empty() || crew_ids.size() > 2 || !resize_funded(w) || w.ally_count < 1 ||
        w.ally_count > 6 || collector.gems > 0 || collector.move_speed != 1 ||
        !resize_harmless_singleton(w, gi))
        return std::nullopt;
    const auto &group = w.geo.groups[gi];
    const Pos capture = group.spawns.front().pos;
    const int capture_steps = coordination_detail::cached_distance(w, collector.pos, capture);
    int selected = -1, bank_steps = unreachable;
    for (unsigned i = 0; i < w.geo.altars.size(); ++i) {
        const int d = w.geo.at(w.geo.altar_fields[i], capture);
        if (d < bank_steps) {
            bank_steps = d;
            selected = int(i);
        }
    }
    if (capture_steps < 0 || capture_steps == unreachable || selected < 0 ||
        bank_steps == unreachable || w.warning_near(capture, 4) ||
        !resize_bank_clear(w, w.geo.altars[selected]))
        return std::nullopt;
    const auto goal = w.geo.goal_cache.find({w.geo.index(capture), 0});
    if (goal == w.geo.goal_cache.end() ||
        !resize_gradient_safe(w, collector.pos, capture, goal->second, 0, collector.id) ||
        !resize_gradient_safe(w, capture, w.geo.altars[selected], w.geo.altar_fields[selected],
                              bc::constants::submit_gems_range, collector.id))
        return std::nullopt;
    CurrentResizeCycle out;
    out.owner = w.self.id;
    out.group = gi;
    out.round = w.round;
    out.serial = w.serial;
    out.collector = collector.id;
    out.count = int(crew_ids.size());
    for (int k = 0; k < out.count; ++k)
        out.ids[k] = crew_ids[k];
    out.capture = capture;
    out.bank = w.geo.altars[selected];
    out.group_gems = group.gems;
    out.recipient_bound = w.ally_count;
    out.reward_scope = ResizeRewardScope::PersonalShareLowerBound;
    out.reward_once = out.collector_reward = group.gems / w.ally_count;
    out.recipients = 1;
    out.collector_conversion_priced = true;
    const int speed = std::max(1, collector.move_speed);
    out.clear_ticks = 1; // Caller proves a real current lethal ordinary basic.
    out.capture_ticks = (capture_steps + speed - 1) / speed + bc::constants::capture_time + 1;
    out.bank_ticks = (bank_steps + speed - 1) / speed + current_tribute_ticks(group.gems);
    out.recovery_ticks = 0; // Harmless quiet fixed clear; no recovery is manufactured.
    out.known = out.sufficient = out.complete = true;
    if (w.round + out.duration() >= bc::constants::max_rounds)
        return std::nullopt;
    return current_resize_valid(out) ? std::optional(out) : std::nullopt;
}
// Initial implementation: one local harmless singleton, selected self plus its
// actual planned lower-ID collector, and one different current-in-range basic
// alternative. Unknown comparisons retain the incumbent. This is a bounded
// personal-secured-rate heuristic, not a proof of total-team improvement.
inline std::optional<Proposal> current_resize_proposal(World &w, Memory &m,
                                                       bool protected_transaction) {
    const Mission &original = m.mission;
    const int gi = original.group;
    // Admit the fixed planning budget before bounded shape/route work.
    // Clearly unrelated owners incur no native budget query.
    if (protected_transaction || m.resizing_probe_round == w.round ||
        original.phase != Phase::Clear || original.assembly_count != 2 ||
        !resize_retained_job_active(original, w.round))
        return std::nullopt;
    if (!resize_funded(w, 65000))
        return std::nullopt;
    if (original.assembly_pending || original.sortie_length > 0 || original.chain_used ||
        original.bank_after_reward || m.hold_group >= 0 || awake_entry_active(m.awake_entry) ||
        w.self.gems > 0 || !w.enemies.empty() || !resize_harmless_singleton(w, gi) ||
        original.planned_collector < 0 || w.ally_count < 1 || w.ally_count > 6 ||
        w.self.move_speed != 1 || w.self.health_fraction() < Settings::ordinary_heal ||
        original.assembly_ids[0] == original.assembly_ids[1] ||
        (original.assembly_ids[0] != w.self.id && original.assembly_ids[1] != w.self.id))
        return std::nullopt;
    if (w.geo.groups.size() > 64)
        return std::nullopt;
    unsigned spawn_work = 0;
    for (unsigned i = 0; i < w.geo.groups.size(); ++i) {
        if (w.geo.groups[i].spawns.size() > 8 || w.groups[i].camps.size() > 8 ||
            w.groups[i].known_dead.size() > 8)
            return std::nullopt;
        spawn_work += w.geo.groups[i].spawns.size();
    }
    if (spawn_work > 128)
        return std::nullopt;
    for (const auto &seen : w.sightings)
        if (seen.actor.alive && combat_detail::recent_sighting(w.round - seen.round))
            return std::nullopt;
    const auto &camp = w.groups[gi].camps.front();
    if (!resize_current_basic_lethal(w.self, camp) || w.warning_near(w.self.pos, 4))
        return std::nullopt;
    const Actor *other = nullptr;
    for (int k = 0; k < 2; ++k) {
        const int id = original.assembly_ids[k];
        if (id == w.self.id)
            continue;
        for (const auto &a : w.allies)
            if (a.id == id)
                other = &a;
    }
    if (!other)
        return std::nullopt;
    // Concrete old named-crew dispatch may hold on a departed claim. The
    // remaining collector recertifies ITS OWN immediate lethal current basic;
    // it does not rely on another actor promising to leave or keep attacking.
    if (original.planned_collector == w.self.id && !w.matching_claim(other->id, gi)) {
        m.resizing_probe_round = w.round;
        auto quote = resize_basic_alternative(w, gi);
        if (!quote)
            return std::nullopt;
        auto p = solo_farm_proposal(w, m, *quote);
        if (p && p->action.kind == Kind::BasicCamp)
            p->action.reason = "resize-retained-collector-fresh-current-basic";
        return p;
    }
    if (original.planned_collector != other->id || other->id >= w.self.id ||
        !w.matching_claim(other->id, gi) || !resize_collector_current_basic(*other, camp) ||
        external_camp_collateral(w.self, w.groups[gi].camps, w.geo.groups, gi, w.groups, w.round) ||
        external_camp_collateral(*other, w.groups[gi].camps, w.geo.groups, gi, w.groups, w.round))
        return std::nullopt;
    m.resizing_probe_round = w.round;
    const std::array<int, 2> current{{w.self.id, other->id}};
    const auto old_price = resize_price_current(w, gi, *other, current);
    if (!old_price)
        return std::nullopt;
    auto new_price = *old_price;
    new_price.clear_ticks = 1;
    new_price.count = 1;
    new_price.ids.fill(-1);
    new_price.ids[0] = other->id;
    // Rank cheaply, then inspect at most two exact cached alternatives. No new
    // field search, projected participant or raw mission rate enters this pass.
    std::array<int, 2> candidates{{-1, -1}};
    for (unsigned i = 0; i < std::min<std::size_t>(64, w.groups.size()); ++i) {
        if (!(i % 8) && !resize_funded(w))
            return std::nullopt;
        if (int(i) == gi || !resize_harmless_singleton(w, int(i)) ||
            !resize_actor_current_basic(w.self, w.groups[i].camps.front()))
            continue;
        const auto before = [&](int a, int b) {
            return b < 0 || distance(w.self.pos, w.groups[a].camps.front().pos) <
                                distance(w.self.pos, w.groups[b].camps.front().pos);
        };
        if (before(int(i), candidates[0])) {
            candidates[1] = candidates[0];
            candidates[0] = int(i);
        } else if (before(int(i), candidates[1]))
            candidates[1] = int(i);
    }
    for (int next : candidates) {
        if (next < 0 || !resize_funded(w))
            break;
        auto quote = resize_basic_alternative(w, next);
        if (!quote)
            continue;
        CurrentResizeAlternative alt;
        alt.owner = alt.body = w.self.id;
        alt.group = next;
        alt.round = w.round;
        alt.serial = w.serial;
        alt.group_gems = w.geo.groups[next].gems;
        alt.recipient_bound = w.ally_count;
        alt.reward_scope = ResizeRewardScope::PersonalShareLowerBound;
        alt.reward_once = alt.group_gems / w.ally_count;
        alt.complete_ticks = quote->total_ticks;
        alt.known = alt.sufficient = alt.complete = true;
        const CurrentResizeOption option{CurrentResizeKind::ReleaseSelf, new_price, alt};
        const auto decision = compare_current_resize(*old_price, std::span(&option, 1));
        if (decision.kind != CurrentResizeKind::ReleaseSelf)
            continue;
        if (!resize_funded(w))
            return std::nullopt;
        auto proposal = solo_farm_proposal(w, m, *quote);
        if (proposal && proposal->action.kind == Kind::BasicCamp)
            proposal->action.reason = "resize-actual-marginal-self-release-basic";
        return proposal;
    }
    return std::nullopt;
}
} // namespace tactics

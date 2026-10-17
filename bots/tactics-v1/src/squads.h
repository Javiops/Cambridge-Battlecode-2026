#pragma once

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <limits>
#include <utility>
#include <vector>

namespace tactics {

// Callers supply only actual, personally observed, timely contributors. Their
// readiness, legal targets and commitment/arrival are checked before this pure
// selector. DPS is useful damage per clear tick, not nominal range membership.
struct Contributor {
    int id = -1;
    double dps = 0;
    double opportunity_cost = 1;
    bool ready = true;
};

struct ReadySquad {
    std::vector<int> ids;
    double dps = 0, clear_ticks = 0, person_turn_cost = 0;
    bool ready = false;
    // An interrupted exhaustive pass is Unknown, never its partial best or a
    // proof that no affordable coalition exists.
    bool interrupted = false;
};

// A physical, currently useful contributor and its own survival budget. Monster
// pressure is allocated geometrically to selected bodies, never divided by a
// nearby headcount. Coordinates are plain values so this remains SDK-free.
struct CampContributor {
    Contributor contribution;
    int x = -1, y = -1;
    double hp = 0, mitigation = 1, enemy_reply = 0;
};
struct CampPressure {
    int x = -1, y = -1, range = 0;
    double strength = 0;
    bool observed = false;
};

struct SquadAlwaysFunded {
    bool operator()() const {
        return true;
    }
};

template <class Funded = SquadAlwaysFunded>
inline ReadySquad
minimum_ready_camp_squad(const std::vector<CampContributor> &input, int self_id, double camp_hp,
                         const std::vector<CampPressure> &monsters, Funded funded = {}) {
    ReadySquad result;
    const auto unknown = [] {
        ReadySquad out;
        out.interrupted = true;
        return out;
    };
    if (!funded())
        return unknown();
    if (self_id < 0 || !std::isfinite(camp_hp) || camp_hp < 0)
        return result;
    std::array<CampContributor, 6> candidates;
    std::size_t count = 0;
    for (const auto &c : input) {
        if (!funded())
            return unknown();
        const auto &b = c.contribution;
        if (b.id < 0 || !b.ready || !std::isfinite(b.dps) || b.dps <= 0 ||
            !std::isfinite(b.opportunity_cost) || b.opportunity_cost < 0 || !std::isfinite(c.hp) ||
            c.hp <= 0 || !std::isfinite(c.mitigation) || c.mitigation <= 0 ||
            !std::isfinite(c.enemy_reply) || c.enemy_reply < 0)
            continue;
        if (count == candidates.size())
            return result;
        candidates[count++] = c;
    }
    if (count == 0)
        return result;
    std::sort(candidates.begin(), candidates.begin() + count,
              [](const auto &a, const auto &b) { return a.contribution.id < b.contribution.id; });
    int self_index = -1;
    for (unsigned i = 0; i < count; ++i) {
        if (i && candidates[i - 1].contribution.id == candidates[i].contribution.id)
            return result;
        if (candidates[i].contribution.id == self_id)
            self_index = i;
    }
    if (self_index < 0)
        return result;
    for (const auto &m : monsters) {
        if (!funded())
            return unknown();
        if (!std::isfinite(m.strength) || m.strength < 0 || m.range < 0)
            return result;
    }
    // Small groups reuse immutable pair distances across every subset. Larger
    // inputs retain the same calculation without imposing a new policy cap.
    std::array<std::array<int, 6>, 8> distance_cache;
    const bool cached_distances = monsters.size() <= distance_cache.size();
    if (cached_distances)
        for (unsigned m = 0; m < monsters.size(); ++m) {
            if (!funded())
                return unknown();
            for (unsigned i = 0; i < count; ++i)
                distance_cache[m][i] = std::max(std::abs(candidates[i].x - monsters[m].x),
                                                std::abs(candidates[i].y - monsters[m].y));
        }
    std::array<int, 6> best_ids{};
    unsigned best_count = 0;
    bool have_best = false;
    for (unsigned mask = 1; mask < (1u << count); ++mask) {
        if (!(mask & (1u << self_index)))
            continue;
        // Cardinality is the first exact objective. A larger coalition cannot
        // beat an already feasible smaller one, whatever its damage or cost.
        if (have_best && std::popcount(mask) > best_count)
            continue;
        if (!funded())
            return unknown();
        std::array<int, 6> ids{};
        unsigned selected = 0;
        double dps = 0;
        double cost_per_tick = 0;
        for (unsigned i = 0; i < count; ++i)
            if (mask & (1u << i)) {
                ids[selected++] = candidates[i].contribution.id;
                dps += candidates[i].contribution.dps;
                cost_per_tick += candidates[i].contribution.opportunity_cost;
            }
        const double clear_ticks = camp_hp == 0 ? 0 : std::ceil(camp_hp / dps);
        std::array<double, 6> pressure{};
        for (unsigned m = 0; m < monsters.size(); ++m) {
            if (!funded())
                return unknown();
            const auto &monster = monsters[m];
            if (!monster.observed) {
                // A hidden member is not certified out of range or shielded by
                // a helper. Preserve the pessimistic self exposure instead.
                pressure[self_index] += monster.strength;
                continue;
            }
            int nearest = std::numeric_limits<int>::max();
            const auto member_distance = [&](unsigned i) {
                return cached_distances ? distance_cache[m][i]
                                        : std::max(std::abs(candidates[i].x - monster.x),
                                                   std::abs(candidates[i].y - monster.y));
            };
            for (unsigned i = 0; i < count; ++i)
                if (mask & (1u << i))
                    nearest = std::min(nearest, member_distance(i));
            if (nearest > monster.range)
                continue; // Native camps do not chase or gain range with time.
            for (unsigned i = 0; i < count; ++i)
                if ((mask & (1u << i)) && member_distance(i) == nearest)
                    pressure[i] += monster.strength; // Full charge for every tie.
        }
        bool safe = true;
        for (unsigned i = 0; i < count; ++i)
            if (mask & (1u << i)) {
                const auto &body = candidates[i];
                // Full group clear duration is deliberately conservative: no
                // speculative early monster death, heal, or future tank swap.
                const double damage = clear_ticks * pressure[i] * body.mitigation;
                safe &= damage + body.enemy_reply + 1 < body.hp * .75;
            }
        if (!safe)
            continue;
        const double person_turn_cost = clear_ticks * cost_per_tick;
        const bool smaller = !have_best || selected < best_count;
        const bool same = have_best && selected == best_count;
        const bool cheaper = same && person_turn_cost < result.person_turn_cost - 1e-9;
        const bool tied = same && std::abs(person_turn_cost - result.person_turn_cost) <= 1e-9;
        const bool lexical =
            tied && std::lexicographical_compare(ids.begin(), ids.begin() + selected,
                                                 best_ids.begin(), best_ids.begin() + best_count);
        if (smaller || cheaper || lexical) {
            have_best = true;
            best_count = selected;
            best_ids = ids;
            result.dps = dps;
            result.clear_ticks = clear_ticks;
            result.person_turn_cost = person_turn_cost;
        }
    }
    if (!funded())
        return unknown();
    if (have_best) {
        result.ids.assign(best_ids.begin(), best_ids.begin() + best_count);
        result.ready = true;
    }
    return result;
}

inline ReadySquad minimum_ready_squad(std::vector<Contributor> candidates, int self_id,
                                      double camp_hp, double max_safe_clear_ticks) {
    ReadySquad result;
    if (self_id < 0 || !std::isfinite(camp_hp) || camp_hp < 0 ||
        !std::isfinite(max_safe_clear_ticks) || max_safe_clear_ticks < 0)
        return result;
    candidates.erase(std::remove_if(candidates.begin(), candidates.end(),
                                    [&](const Contributor &c) {
                                        return c.id < 0 || !c.ready || !std::isfinite(c.dps) ||
                                               c.dps < 0 || !std::isfinite(c.opportunity_cost) ||
                                               c.opportunity_cost < 0 ||
                                               (c.id != self_id && c.dps == 0);
                                    }),
                     candidates.end());
    std::sort(candidates.begin(), candidates.end(),
              [](const Contributor &a, const Contributor &b) { return a.id < b.id; });
    // Six is the current maximum physical roster (including Cassi/Issac). A
    // larger or duplicate input is a caller/model error, not extra firepower.
    if (candidates.empty() || candidates.size() > 6)
        return result;
    int self_index = -1;
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        if (i && candidates[i - 1].id == candidates[i].id)
            return result;
        if (candidates[i].id == self_id)
            self_index = static_cast<int>(i);
    }
    if (self_index < 0)
        return result;
    const unsigned combinations = 1u << candidates.size();
    for (unsigned mask = 1; mask < combinations; ++mask) {
        if (!(mask & (1u << self_index)))
            continue;
        ReadySquad current;
        double cost_per_tick = 0;
        for (std::size_t i = 0; i < candidates.size(); ++i)
            if (mask & (1u << i)) {
                current.ids.push_back(candidates[i].id);
                current.dps += candidates[i].dps;
                cost_per_tick += candidates[i].opportunity_cost;
            }
        if (camp_hp > 0 && current.dps <= 0)
            continue;
        current.clear_ticks = camp_hp == 0 ? 0 : std::ceil(camp_hp / current.dps);
        if (!std::isfinite(current.clear_ticks) || current.clear_ticks > max_safe_clear_ticks)
            continue;
        current.person_turn_cost = cost_per_tick * current.clear_ticks;
        current.ready = true;
        const bool smaller = !result.ready || current.ids.size() < result.ids.size();
        const bool same_size = result.ready && current.ids.size() == result.ids.size();
        const bool cheaper = same_size && current.person_turn_cost < result.person_turn_cost - 1e-9;
        const bool tied =
            same_size && std::abs(current.person_turn_cost - result.person_turn_cost) <= 1e-9;
        if (smaller || cheaper || (tied && current.ids < result.ids))
            result = std::move(current);
    }
    return result;
}

} // namespace tactics

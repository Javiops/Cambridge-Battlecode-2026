#pragma once

#include <algorithm>
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
};

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

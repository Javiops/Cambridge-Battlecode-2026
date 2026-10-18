#pragma once
#include "actions.h"
#include <span>
#include <string_view>

namespace foundation {
// Shared ordering from the decision contract. Feasibility belongs in the policy.
enum class Priority { fallback, ordinary, continue_job, survival, deciding };
struct Proposal {
    Request request;
    Priority priority;
};
struct PlanningContext {
    Snapshot actor;
    // Future observed world/mission views belong here, not in the cheap action read.
};
struct Policy {
    std::string_view id; // Stable tactic ID plus a name, e.g. "10.1.recover".
    std::optional<Proposal> (*propose)(const PlanningContext&);
};
enum class DecisionStatus { selected, idle, stale, fault };
struct Decision {
    DecisionStatus status;
    std::string_view policy;
    Request request;
};

// Pure selection: policies see one immutable snapshot and cannot spend actions.
// A stable ID breaks equal-priority ties; registration order never decides play.
inline Decision select(const PlanningContext& context, std::span<const Policy> policies) {
    const auto& snapshot = context.actor;
    const Request wait{Action::wait, snapshot.epoch};
    if (!snapshot.state.consistent || snapshot.state.round != snapshot.epoch.round)
        return {DecisionStatus::stale, {}, wait};
    if (!snapshot.state.alive || snapshot.state.channel != Channel::none)
        return {DecisionStatus::idle, {}, wait};
    constexpr std::size_t max_policies = 16; // Bound planning work; measure before raising.
    if (policies.size() > max_policies) return {DecisionStatus::fault, {}, wait};
    // Validate all registrations before invoking any policy.
    for (std::size_t i = 0; i < policies.size(); ++i) {
        if (policies[i].id.empty() || !policies[i].propose)
            return {DecisionStatus::fault, {}, wait};
        for (std::size_t j = 0; j < i; ++j)
            if (policies[i].id == policies[j].id)
                return {DecisionStatus::fault, {}, wait};
    }
    Decision decision{DecisionStatus::idle, {}, wait};
    Priority best = Priority::fallback;
    try {
        for (const auto& policy : policies) {
            const auto proposal = policy.propose(context);
            if (!proposal) continue;
            if (proposal->request.epoch != snapshot.epoch)
                return {DecisionStatus::stale, {}, wait};
            if (proposal->priority < Priority::fallback || proposal->priority > Priority::deciding)
                return {DecisionStatus::fault, {}, wait};
            if (decision.status != DecisionStatus::selected || proposal->priority > best ||
                (proposal->priority == best && policy.id < decision.policy)) {
                best = proposal->priority;
                decision = {DecisionStatus::selected, policy.id, proposal->request};
            }
        }
    } catch (...) { return {DecisionStatus::fault, {}, wait}; }
    return decision;
}
} // namespace foundation

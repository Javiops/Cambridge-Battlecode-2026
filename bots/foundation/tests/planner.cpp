#include "../src/policies/registry.h"
#include <cassert>
#include <cstdio>
#include <stdexcept>
using namespace foundation;

int calls = 0;
std::optional<Proposal> farm(const PlanningContext& context) {
    const auto& s = context.actor;
    ++calls;
    return Proposal{{Action::move, s.epoch, {3, 2}}, Priority::ordinary};
}
std::optional<Proposal> escape(const PlanningContext& context) {
    const auto& s = context.actor;
    ++calls;
    return Proposal{{Action::recall, s.epoch}, Priority::survival};
}
std::optional<Proposal> bank(const PlanningContext& context) {
    const auto& s = context.actor;
    return Proposal{{Action::tribute, s.epoch, {2, 3}}, Priority::deciding};
}
std::optional<Proposal> continuing(const PlanningContext& context) {
    const auto& s = context.actor;
    return Proposal{{Action::move, s.epoch, {4, 2}}, Priority::continue_job};
}
std::optional<Proposal> abstain(const PlanningContext&) { return std::nullopt; }
std::optional<Proposal> stale(const PlanningContext& context) {
    const auto& s = context.actor;
    auto epoch = s.epoch; ++epoch.sequence;
    return Proposal{{Action::recall, epoch}, Priority::survival};
}
std::optional<Proposal> broken(const PlanningContext&) { throw std::runtime_error("policy failed"); }
std::optional<Proposal> bad_priority(const PlanningContext& context) {
    const auto& s = context.actor;
    return Proposal{{Action::wait, s.epoch}, static_cast<Priority>(99)};
}

int main() {
    const Snapshot s{{3, true, true, {2, 2}, Channel::none}, {3, 0}};
    const PlanningContext context{s};
    int checks = 0;
    auto check = [&](bool ok) { ++checks; assert(ok); };
    const std::array normal{Policy{"08.1.farm", farm}, Policy{"10.1.escape", escape}};
    auto decision = select(context, normal);
    check(decision.status == DecisionStatus::selected && decision.policy == "10.1.escape" &&
          decision.request.action == Action::recall && decision.request.epoch == s.epoch);
    const std::array reversed{normal[1], normal[0]};
    check(select(context, reversed).policy == decision.policy);
    const std::array finish{normal[1], Policy{"09.1.bank", bank}};
    check(select(context, finish).policy == "09.1.bank");
    const std::array job{normal[0], Policy{"08.2.continue", continuing}};
    check(select(context, job).policy == "08.2.continue");
    const std::array tie{Policy{"08.2.second", farm}, Policy{"08.1.first", farm}};
    const std::array tie_reversed{tie[1], tie[0]};
    check(select(context, tie).policy == "08.1.first" && select(context, tie_reversed).policy == "08.1.first");
    const std::array quiet{Policy{"08.1.none", abstain}};
    decision = select(context, quiet);
    check(decision.status == DecisionStatus::idle && decision.request.action == Action::wait);
    check(select(context, {}).status == DecisionStatus::idle);
    decision = select(context, policies::registry);
    check(decision.policy == "12.5.hold" && decision.request.action == Action::wait);
    const std::array expired{normal[0], Policy{"10.1.old", stale}};
    check(select(context, expired).status == DecisionStatus::stale);
    calls = 0;
    const std::array duplicate{normal[0], normal[0]};
    check(select(context, duplicate).status == DecisionStatus::fault && calls == 0);
    const std::array unnamed{Policy{"", farm}};
    check(select(context, unnamed).status == DecisionStatus::fault && calls == 0);
    const std::array missing{Policy{"08.1.missing", nullptr}};
    check(select(context, missing).status == DecisionStatus::fault);
    const std::array throwing{Policy{"08.1.broken", broken}};
    check(select(context, throwing).status == DecisionStatus::fault);
    const std::array invalid{Policy{"08.1.invalid", bad_priority}};
    check(select(context, invalid).status == DecisionStatus::fault);
    const std::array<Policy, 17> too_many{};
    check(select(context, too_many).status == DecisionStatus::fault);
    auto changed = s; changed.state.consistent = false;
    check(select(PlanningContext{changed}, normal).status == DecisionStatus::stale && calls == 0);
    changed = s; ++changed.state.round;
    check(select(PlanningContext{changed}, normal).status == DecisionStatus::stale && calls == 0);
    changed = s; changed.state.alive = false;
    check(select(PlanningContext{changed}, normal).status == DecisionStatus::idle && calls == 0);
    for (const auto channel : {Channel::recall, Channel::tribute, Channel::teleport}) {
        changed = s; changed.state.channel = channel;
        check(select(PlanningContext{changed}, normal).status == DecisionStatus::idle && calls == 0);
    }
    std::printf("PASS %d planner checks\n", checks);
}

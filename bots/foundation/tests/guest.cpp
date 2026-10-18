// Runs the real SdkPort and Executor inside a metered Wasmtime guest.
#include <cambc.h>
#include <cstdio>
#include <stdexcept>
#include "sdk_actions.h"
#include "policies/registry.h"
using namespace foundation;

std::optional<Proposal> farm_proposal(const PlanningContext& context) {
    const auto& s = context.actor;
    return Proposal{{Action::move,s.epoch,{s.state.position.x+1,s.state.position.y}},Priority::ordinary};
}
std::optional<Proposal> recall_proposal(const PlanningContext& context) {
    const auto& s = context.actor;
    return Proposal{{Action::recall,s.epoch},Priority::survival};
}

void require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}
int main() {
    Executor executor;
    SdkPort port;
    bool tested = false;
    for (;;) {
        try {
            if (cambc::is_draft()) {
                auto chosen = cambc::draft::current_draft(cambc::team::ally);
                for (int i=0; i<11; ++i) {
                    auto pick = static_cast<cambc::champion_draft>(i);
                    if (std::find(chosen.begin(),chosen.end(),pick)==chosen.end()) {
                        cambc::draft::pick(pick); break;
                    }
                }
            } else if (!tested && cambc::round_number()>=2) {
                // The first play turn gets 2x fuel. Exercise the normal budget.
                tested = true;
                auto s = executor.observe(port);
                auto hold = select(PlanningContext{s},policies::registry);
                require(hold.status==DecisionStatus::selected && hold.policy=="12.5.hold" &&
                    hold.request.action==Action::wait,"production registry did not hold");
                auto old = s.epoch; ++old.round;
                require(executor.execute(port,{Action::recall,old}).outcome==Outcome::stale,"stale plan executed");
                auto rejected = executor.execute(port,{Action::move,s.epoch,{-1,-1}});
                require(rejected.outcome==Outcome::rejected && rejected.engine_error!=0,"lost SDK rejection");
                require(executor.execute(port,{Action::recall,s.epoch}).outcome==Outcome::stale,"reused sibling proposal");
                bool moved = false;
                const auto p = cambc::self().position();
                for (int dx=-1; dx<=1 && !moved; ++dx) {
                    for (int dy=-1; dy<=1 && !moved; ++dy) {
                        if (!dx && !dy) continue;
                        s = executor.observe(port);
                        auto r = executor.execute(port,{Action::move,s.epoch,{p.x+dx,p.y+dy}});
                        moved = r.outcome==Outcome::moved;
                    }
                }
                require(moved,"could not exercise a legal move");
                s = executor.observe(port);
                const std::array competing{Policy{"08.1.farm",farm_proposal},Policy{"10.1.recall",recall_proposal}};
                const auto chosen = select(PlanningContext{s},competing);
                require(chosen.policy=="10.1.recall","competing policies spent the wrong action");
                auto recall = executor.execute(port,chosen.request);
                require(recall.outcome==Outcome::recall_started,"recall start not confirmed");
                s = executor.observe(port);
                require(select(PlanningContext{s},competing).status==DecisionStatus::idle,"planner interrupted channel");
                require(executor.execute(port,{Action::move,s.epoch,{p.x,p.y}}).outcome==Outcome::channel_active,
                    "active channel overwritten");
                require(cambc::round_number()==2 && cambc::fuel_remaining()>=Executor::reserve,
                    "scenario suspended or exhausted execution reserve");
                // Test-only completion marker, visible in official statistics.
                cambc::self().cancel_recall();
                require(cambc::self().place_ward(cambc::self().position()),"completion marker failed");
                std::printf("FOUNDATION_GUEST_PASS round=%u fuel=%llu\n",cambc::round_number(),
                    static_cast<unsigned long long>(cambc::fuel_remaining()));
                std::fflush(stdout);
            }
        } catch (const std::exception& e) {
            std::printf("FOUNDATION_GUEST_FAIL %s\n",e.what()); std::fflush(stdout);
            return 1;
        } catch (...) { std::puts("FOUNDATION_GUEST_FAIL unknown"); std::fflush(stdout); return 1; }
        cambc::end_turn();
    }
}

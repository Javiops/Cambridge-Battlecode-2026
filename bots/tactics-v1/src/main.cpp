#include "actions.h"
#include "coordinator.h"
#include "draft.h"
#include "shopping.h"
#include "vision.h"
#include <memory>
#include <string_view>

namespace tactics {
class Bot {
    Geometry geometry_;
    Memory memory_;
    ShoppingState shopping_;
    WardState ward_;
    std::unique_ptr<World> world_;
    std::vector<int> rejected_draft_;

    // An accepted action may use the rest of this owner's budget. We may end
    // here without another snapshot, but must never decide from that old view.
    bool refresh_after(World &w, const Action &action, const Execution &result) {
        if (result.outcome == Outcome::Started)
            memory_.prior_channel =
                action.kind == Kind::Recall ? Channel::Recall : Channel::Tribute;
        if (action.kind == Kind::Buy || action.kind == Kind::Sell ||
            action.kind == Kind::BuyConsumable || action.kind == Kind::CastSelf) {
            w.refresh(true);
            remember(w, memory_);
            return fuel(30000);
        }
        if (!fuel(44000))
            return false;
        w.refresh();
        remember(w, memory_);
        return fuel(28000);
    }

    void draft_turn() {
        geometry_.initialize();
        std::vector<int> accepted;
        for (auto pick : bc::draft::current_draft(bc::team::ally))
            accepted.push_back(static_cast<int>(pick));
        const int cap = bc::draft::team_size();
        for (int choice : draft_preferences(cap, geometry_.spawn_walk, accepted)) {
            if (!fuel(5000))
                break;
            if (std::find(rejected_draft_.begin(), rejected_draft_.end(), choice) !=
                rejected_draft_.end())
                continue;
            // Freeze the prospective last choice before the accepting SDK call.
            std::array<std::byte, 32> plan{};
            plan[0] = std::byte(1);
            plan[1] = std::byte(cap);
            plan[2] = std::byte(accepted.size() + 1);
            for (unsigned i = 0; i < accepted.size() && i < 20; ++i)
                plan[3 + i] = std::byte(accepted[i]);
            if (accepted.size() < 20)
                plan[3 + accepted.size()] = std::byte(choice);
            bc::draft_memory = std::span<const std::byte>(plan);
            try {
                bc::draft::pick(static_cast<bc::champion_draft>(choice));
                return;
            } catch (const bc::error &) {
                rejected_draft_.push_back(choice);
            }
        }
    }
    void gameplay_turn() {
        geometry_.initialize();
        if (!world_)
            world_ = std::make_unique<World>(geometry_, memory_);
        World &w = *world_;
        w.refresh();
        observe_progress(w, memory_);
        int shops = 0, failures = 0, moves_failed = 0;
        for (int iteration = 0; iteration < Settings::max_actions && fuel(30000); ++iteration) {
            if (w.round != static_cast<int>(bc::round_number())) {
                w.refresh();
                observe_progress(w, memory_);
                break;
            }
            auto chosen = choose_mission(w, memory_);
            Mission intended = chosen ? chosen->mission : memory_.mission;
            if (!w.self.alive) {
                intended = {};
                w.publish_claim(-1);
            }
            // At most four free shop transactions preserve an iteration for the
            // chosen field action; a selected Tavi pair is always restored first.
            std::optional<Action> shop;
            if ((shops < 4 && iteration < Settings::max_actions - 2) || shopping_.pending_heal >= 0)
                shop = shopping_proposal(w, intended, shopping_);
            if (shop && fuel(20000) &&
                (!chosen || chosen->priority < Priority::Deciding || shopping_.pending_heal >= 0 ||
                 !w.self.alive)) {
                remember(w, memory_);
                auto result = execute(w, *shop);
                ++shops;
                if (result.outcome == Outcome::Stale)
                    return;
                w.refresh(true);
                shopping_after_action(w, *shop, result.success, shopping_);
                if (!result.success && ++failures >= 2)
                    break;
                remember(w, memory_);
                if (!fuel(30000))
                    return;
                continue;
            }
            if (!chosen)
                break;
            // Never insert ward placement before a required survival response.
            if (chosen->action.kind == Kind::None && chosen->priority < Priority::Survival &&
                iteration < Settings::max_actions - 1) {
                if (auto ward = ward_proposal(w, intended, ward_)) {
                    remember(w, memory_);
                    auto result = execute(w, *ward);
                    if (result.outcome == Outcome::Stale)
                        return;
                    if (!fuel(44000)) {
                        ward_after_action(w, *ward, result.success, ward_);
                        return;
                    }
                    w.refresh();
                    ward_after_action(w, *ward, result.success, ward_);
                    if (!result.success && ++failures >= 2)
                        break;
                    remember(w, memory_);
                    continue;
                }
            }
            Mission prior = memory_.mission;
            memory_.mission = chosen->mission;
            const bool camp_job =
                memory_.mission.group >= 0 &&
                (memory_.mission.phase == Phase::Travel ||
                 memory_.mission.phase == Phase::Assemble ||
                 memory_.mission.phase == Phase::Clear || memory_.mission.phase == Phase::Collect ||
                 memory_.mission.phase == Phase::Observe);
            if (chosen->action.kind == Kind::None) {
                // An intentional hold is already the selected job. An attempted
                // action, however, must not advertise a job it fails to enter.
                w.publish_claim(camp_job ? memory_.mission.group : -1);
                break;
            }
            remember(w, memory_);
            auto result = execute(w, chosen->action);
            if (result.outcome == Outcome::Stale) {
                memory_.mission = prior;
                return;
            }
            if (result.success) {
                w.publish_claim(camp_job ? memory_.mission.group : -1);
                const auto &a = chosen->action;
                if (a.target >= 0 &&
                    (a.kind == Kind::BasicChampion || a.kind == Kind::CastChampion)) {
                    memory_.focus = a.target;
                    memory_.focus_until = w.round + 2;
                }
                if (std::string_view(a.reason) == "capture-actual-lower-id-holder-handoff") {
                    memory_.failed_group = prior.group;
                    memory_.failed_until = w.round + Settings::job_lease;
                }
            } else {
                // A failed proposal does not advance a mission or a lease.
                memory_.mission = prior;
                w.publish_claim(-1);
                if (chosen->action.kind == Kind::Move && ++moves_failed >= 2)
                    break;
                if (++failures >= 2)
                    break;
            }
            if (!refresh_after(w, chosen->action, result))
                return;
            if (w.self.channel != Channel::None)
                break;
        }
        remember(w, memory_);
    }

  public:
    void turn() {
        if (bc::is_draft())
            draft_turn();
        else
            gameplay_turn();
    }
};
} // namespace tactics

int main() {
    tactics::Bot bot;
    while (true) {
        try {
            bot.turn();
        } catch (const std::exception &e) {
            std::cout << "TACTICS_ERROR " << e.what() << '\n';
        } catch (...) {
            std::cout << "TACTICS_ERROR unknown\n";
        }
        cambc::end_turn();
    }
}

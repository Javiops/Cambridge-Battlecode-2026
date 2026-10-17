#include "actions.h"
#include "coordinator.h"
#include "crew_sequence.h"
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
    ChainState chain_;
    std::unique_ptr<World> world_;
    std::vector<int> rejected_draft_;
    Pos fallback_route_{};
    int fallback_route_round_ = -1000, fallback_group_ = -1;
    void prepare_route(World &w) {
        if (!w.self.alive || !w.self.can_move || w.self.channel != Channel::None)
            return;
        Pos target = memory_.mission.target;
        const auto resource_eligible = [&](int gi) {
            if (gi < 0 || gi >= static_cast<int>(geometry_.groups.size()))
                return false;
            const bool holder =
                gi < static_cast<int>(w.groups.size()) && w.groups[gi].fresh(w.round) &&
                w.groups[gi].state == Lifecycle::Reward && w.on_group(gi, w.self.pos);
            if (!holder && memory_.failed_group == gi && w.round < memory_.failed_until)
                return false;
            return resource_new_job_eligible(
                geometry_.groups[gi].gems, w.self.gems, geometry_.monolith_only, holder,
                gi == memory_.mission.group, priced_cash_investment(memory_, gi, w.round));
        };
        if (memory_.mission.group >= 0 && !resource_eligible(memory_.mission.group) &&
            memory_.mission.phase != Phase::Deliver && memory_.mission.phase != Phase::Recover &&
            memory_.mission.phase != Phase::Channel)
            target = {};
        if (!geometry_.valid(target)) {
            if (geometry_.valid(fallback_route_) && resource_eligible(fallback_group_) &&
                w.round - fallback_route_round_ < 20)
                target = fallback_route_;
            else {
                double best = -1;
                int best_tier = -1;
                fallback_group_ = -1;
                for (unsigned gi = 0; gi < geometry_.groups.size(); ++gi) {
                    const auto &group = geometry_.groups[gi];
                    if (!resource_eligible(gi))
                        continue;
                    const bool priced = priced_cash_investment(memory_, gi, w.round);
                    const int tier = resource_has_bank(group.gems, w.self.gems) || priced ? 1 : 0;
                    for (const auto &spawn : group.spawns) {
                        const double clear = group.initial_hp / std::max(1.0, w.self.strength);
                        const bool affordable =
                            clear * group.initial_strength * w.self.camp_mitigation <
                            w.self.hp * .75;
                        const double reward =
                            tier ? group.gems + w.self.gems +
                                       .25 * score_resource_gold(group.gems, group.gold)
                                 : group.gold;
                        const double value =
                            priced ? memory_.cash_investment_rate
                                   : reward / (6 + distance(w.self.pos, spawn.pos) + clear) *
                                         (affordable ? 1 : .1);
                        if (tier > best_tier || (tier == best_tier && value > best)) {
                            best_tier = tier;
                            best = value;
                            target = spawn.pos;
                            fallback_group_ = gi;
                        }
                    }
                }
                fallback_route_ = target;
                fallback_route_round_ = w.round;
            }
        }
        if (geometry_.valid(target) && !geometry_.blocked(target) && !w.in_spawn(target))
            geometry_.goal_field(target, 0);
    }

    // An accepted action may use the rest of this owner's budget. We may end
    // here without another snapshot, but must never decide from that old view.
    bool refresh_after(World &w, const Action &action, const Execution &result) {
        if (result.outcome == Outcome::Started)
            memory_.prior_channel =
                action.kind == Kind::Recall ? Channel::Recall : Channel::Tribute;
        if (action.kind == Kind::Buy || action.kind == Kind::Sell ||
            action.kind == Kind::BuyConsumable || action.kind == Kind::CastSelf) {
            w.refresh(true);
            if (w.round != static_cast<int>(bc::round_number()))
                return false;
            remember(w, memory_);
            if (action.kind == Kind::CastSelf && memory_.mission.phase == Phase::Clear &&
                (std::string_view(action.reason) == "farm-certified-solo-live-reset" ||
                 std::string_view(action.reason) == "crew-paid-reset-with-basic"))
                return fuel(10000);
            return fuel(30000);
        }
        const bool stationary_effect =
            action.kind == Kind::BasicChampion || action.kind == Kind::CastChampion ||
            action.kind == Kind::BasicCamp || action.kind == Kind::CastCamp ||
            (action.kind == Kind::CastGround && action.slot >= 0 &&
             w.spells[action.slot].kind != 6);
        if (stationary_effect && bc::fuel_remaining() >= 30000) {
            w.refresh_local_effects(action);
            remember(w, memory_);
            return fuel(22000);
        }
        if (!fuel(44000))
            return false;
        w.refresh();
        remember(w, memory_);
        return fuel(28000);
    }

    void draft_turn() {
        geometry_.initialize(true);
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
        if (!geometry_.initialized)
            return;
        // Immutable selected-route work receives a fresh owner budget before
        // snapshot cost. Finish an older sliced search even if its job changed;
        // otherwise one abandoned field can block every future request.
        geometry_.resume_goal();
        if (geometry_.valid(memory_.mission.target) && !geometry_.blocked(memory_.mission.target) &&
            memory_.mission.phase != Phase::Channel && memory_.mission.phase != Phase::Recover)
            geometry_.goal_field(memory_.mission.target, 0);
        if (world_ && geometry_.valid(memory_.mission.target) &&
            memory_.mission.phase != Phase::Channel && memory_.mission.phase != Phase::Recover &&
            bc::fuel_remaining() >= 95000) {
            geometry_.goal_field(memory_.mission.target, ward_contact_range(*world_), true);
        }
        if (world_ && world_->self.alive && world_->self.channel == Channel::None &&
            memory_.mission.phase != Phase::Channel && memory_.mission.phase != Phase::Recover &&
            !memory_.mission.assembly_pending && bc::fuel_remaining() >= 80000)
            if (auto nearby = nearby_assembly_group(*world_, memory_))
                geometry_.goal_field(geometry_.groups[*nearby].spawns.front().pos, 0);
        if (world_ && world_->self.alive && world_->self.channel == Channel::None &&
            bc::fuel_remaining() >= 80000)
            if (auto hint = shopping_gem_route_hint(*world_, shopping_))
                geometry_.goal_field(*hint, 0);
        if (!world_ && bc::fuel_remaining() < 95000)
            return;
        if (!world_)
            world_ = std::make_unique<World>(geometry_, memory_);
        if (bc::fuel_remaining() < 45000)
            return;
        World &w = *world_;
        w.refresh();
        if (w.round != static_cast<int>(bc::round_number()))
            return;
        observe_progress(w, memory_);
        w.publish_warning();
        std::optional<Proposal> preselected;
        bool hostile = !w.enemies.empty();
        for (const auto &seen : w.sightings)
            hostile |= seen.actor.alive && combat_detail::recent_sighting(w.round - seen.round);
        const bool transaction = shopping_.cash.group >= 0 || shopping_.investment_item >= 0 ||
                                 shopping_.pending_heal >= 0 || shopping_.installed_gem.group >= 0;
        if (awake_entry_active(memory_.awake_entry))
            preselected = pending_awake_entry_proposal(w, memory_, transaction);
        if (w.round != int(bc::round_number()))
            return;
        if (chain_.active() &&
            (chain_.owner != w.self.id || w.self.gems <= 0 || !memory_.mission.chain_used))
            chain_.release();
        if (!preselected && bc::fuel_remaining() >= (chain_.active() ? 22000u : 56000u))
            preselected = early_chain_proposal(w, memory_, chain_, transaction);
        if (!preselected && chain_.active()) {
            const int failed_chain_group = chain_.group;
            if (abort_declined_chain(w.self, memory_, chain_, geometry_.altars[chain_.altar],
                                     memory_.hold_group >= 0)) {
                w.publish_claim(-1);
                LogLine("T1J")
                    .field(w.round)
                    .field(w.self.id)
                    .field("chain-abort-to-bank")
                    .field(failed_chain_group)
                    .emit();
            }
        }
        if (!preselected && shopping_.installed_gem.group >= 0)
            preselected = named_installed_gem_reentry_proposal(w, memory_, shopping_);
        if (!preselected && bc::fuel_remaining() >= 56000 &&
            early_solo_eligible(w.self, memory_.mission, w.round, memory_.hold_group >= 0, hostile,
                                transaction))
            preselected = early_solo_proposal(w, memory_);
        if (!preselected && bc::fuel_remaining() >= 56000 &&
            early_assembly_eligible(w.self, memory_.mission, w.round, memory_.hold_group >= 0,
                                    hostile, transaction))
            preselected = assembly_handshake_proposal(w, memory_, std::nullopt, 56000);
        if (w.round != static_cast<int>(bc::round_number()))
            return;
        if (preselected && preselected->mission.assembly_pending)
            preselected->action.reason = preselected->action.kind == Kind::Move
                                             ? "assembly-early-funded-rendezvous-move"
                                             : "assembly-early-funded-rendezvous-wait";
        if (!preselected)
            prepare_route(w);
        if (w.round != static_cast<int>(bc::round_number()))
            return;
        const int incumbent_group = memory_.mission.group;
        const bool deciding_bag =
            w.self.gems > 0 && w.own_score + w.self.gems >= int(bc::constants::winning_gems);
        const bool current_clear =
            !deciding_bag && memory_.mission.phase == Phase::Clear && incumbent_group >= 0 &&
            incumbent_group < static_cast<int>(w.groups.size()) && w.self.alive &&
            w.self.channel == Channel::None && w.groups[incumbent_group].fresh(w.round) &&
            w.groups[incumbent_group].state == Lifecycle::Alive &&
            w.groups[incumbent_group].camps.size() == 1 &&
            geometry_.groups[incumbent_group].spawns.size() == 1;
        // A live incumbent's paid fixed-position certificate gets its fresh
        // owner budget before optional investment/ranking work. It still
        // declines threats, collateral, changed position and unsafe reserves.
        // Existing cash receipts must be refreshed even during their Clear
        // leg: sharing, wallet or the named gem endpoint may have invalidated
        // the investment since the previous owner. This is maintenance, not
        // an elective replacement of a still-valid current gem clear.
        const bool current_crew_clear =
            !deciding_bag && w.self.alive && w.self.channel == Channel::None &&
            memory_.mission.phase == Phase::Clear && memory_.mission.assembly_count > 0 &&
            incumbent_group >= 0 && incumbent_group < static_cast<int>(w.groups.size()) &&
            assembly_detail::observed_group(w, incumbent_group);
        bool upgrade_deferred =
            preselected || ((current_clear || current_crew_clear) && shopping_.cash.group < 0);
        if (!upgrade_deferred) {
            plan_upgrade_return(w, memory_, shopping_);
            if (w.round != static_cast<int>(bc::round_number()))
                return;
            if (!preselected && shopping_.cash.group >= 0)
                preselected = named_cash_acquisition_proposal(w, memory_, shopping_);
            if (w.round != static_cast<int>(bc::round_number()))
                return;
        }
        int shops = 0, failures = 0, moves_failed = 0;
        bool clear_followup = current_clear || current_crew_clear;
        bool solo_entry_followup = false;
        // Disengaged storage does not initialize the large actor/camp receipt
        // payloads before a paid rendezvous can spend its ordinary move.
        std::optional<SoloBasicReceipt> basic_receipt;
        bool basic_accepted = false;
        std::optional<SoloResetReceipt> reset_receipt;
        bool reset_accepted = false;
        std::optional<CrewTurnReceipt> crew_receipt;
        bool crew_accepted = false;
        for (int iteration = 0; iteration < Settings::max_actions && fuel(10000); ++iteration) {
            if (w.round != static_cast<int>(bc::round_number())) {
                w.refresh();
                observe_progress(w, memory_);
                break;
            }
            Mission intended = memory_.mission;
            if (!w.self.alive) {
                intended = {};
                w.publish_claim(-1);
            }
            // Only an accepted stationary camp action opens this cheap path.
            // It recertifies the actual refreshed singleton and its whole clear
            // reserve; lower budgets never enter global arbitration or shopping.
            std::optional<Proposal> chosen = std::move(preselected);
            preselected.reset();
            if (!chosen && solo_entry_followup) {
                solo_entry_followup = false;
                // The actual accepted move changed position/permissions. Pay
                // one new snapshot quote before optional ranking; the prior
                // future route supplies no first-hit permission.
                if (bc::fuel_remaining() >= 44000 && memory_.mission.group >= 0) {
                    const auto quote = quote_solo_farm(w, memory_.mission.group);
                    chosen = solo_farm_proposal(w, memory_, quote);
                    if (chosen && chosen->action.kind == Kind::BasicCamp)
                        chosen->action.reason = "solo-early-funded-live-basic";
                }
            }
            if (!chosen && crew_receipt && crew_receipt->valid)
                chosen = crew_turn_followup(w, memory_, *crew_receipt, crew_accepted);
            crew_accepted = false;
            if (!chosen && reset_receipt && reset_receipt->valid)
                chosen = solo_reset_basic_followup(w, memory_, *reset_receipt, reset_accepted);
            reset_accepted = false;
            if (!chosen && basic_receipt && basic_receipt->valid)
                chosen = solo_basic_reset_followup(w, memory_, *basic_receipt, basic_accepted);
            basic_accepted = false;
            if (!chosen && clear_followup && memory_.mission.phase == Phase::Clear &&
                memory_.mission.assembly_count > 0 && fuel(48000))
                chosen = farming(w, memory_); // Current named coalition before unrelated planners.
            if (!chosen && clear_followup && memory_.mission.phase == Phase::Clear && fuel(18000))
                chosen = solo_clear_followup(w, memory_);
            // A real newly cleared reward must not be abandoned by the
            // ordinary low-budget banking shortcut after its capture move.
            if (!chosen && chain_.active() && memory_.mission.chain_used &&
                memory_.mission.group == chain_.group && chain_funded(w, 22000))
                chosen = chain_capture_proposal(w, memory_, chain_);
            if (!chosen && shopping_.installed_gem.group >= 0)
                chosen = named_installed_gem_reentry_proposal(w, memory_, shopping_);
            if (!chosen) {
                if (!fuel(30000))
                    break;
                if (upgrade_deferred) {
                    upgrade_deferred = false;
                    plan_upgrade_return(w, memory_, shopping_);
                    if (w.round != static_cast<int>(bc::round_number()))
                        return;
                    if (!fuel(30000))
                        break;
                }
                // Buying is free of gameplay allowances, but not of computation.
                // Use the incumbent mission before one expensive arbitration, and
                // refresh actual stats/inventory after each bounded bundle.
                std::optional<Action> shop;
                const bool deciding =
                    w.self.gems > 0 &&
                    w.own_score + w.self.gems >= static_cast<int>(bc::constants::winning_gems);
                const bool contact = w.self.alive && w.exposure(w.self.pos) >= w.self.hp * .5;
                if (shopping_.pending_heal >= 0 ||
                    (shops < 4 && !deciding && !contact && bc::fuel_remaining() >= 55000))
                    shop = shopping_proposal(w, intended, shopping_);
                if (w.round != static_cast<int>(bc::round_number()))
                    return;
                if (shop && fuel(20000)) {
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
                    continue;
                }
                chosen = choose_mission(w, memory_);
            }
            if (w.round != static_cast<int>(bc::round_number()))
                return;
            // A planner may exhaust its optional slice while still returning
            // a proposal. Receipt construction, mission copies, the mutation
            // gateway and final bookkeeping need the ordinary action reserve
            // too. Never spend that reserve on an unfunded returned proposal.
            if (!fuel(10000))
                return;
            if (chosen)
                intended = chosen->mission;
            if (!chosen)
                break;
            const bool certified_reset =
                chosen->action.kind == Kind::CastSelf &&
                std::string_view(chosen->action.reason) == "farm-certified-solo-live-reset";
            const bool crew_reset =
                chosen->crew_clear_certified && chosen->action.kind == Kind::CastSelf &&
                chosen->action.slot >= 0 && w.spells[chosen->action.slot].kind == 1;
            const bool receipt_basic =
                chosen->action.kind == Kind::BasicCamp &&
                std::string_view(chosen->action.reason) == "farm-certified-reset-receipt-basic";
            // An offensive reset is useful only if the charged extra basic can
            // still run during this owner opportunity, before every optional job.
            if (certified_reset && bc::fuel_remaining() < 34000)
                break;
            if (certified_reset && iteration + 1 >= Settings::max_actions)
                break;
            if (crew_reset &&
                (bc::fuel_remaining() < 36000 || iteration + 1 >= Settings::max_actions))
                break;
            // Never insert ward placement before a required survival response.
            if (!certified_reset && !receipt_basic && !chosen->solo_clear_certified &&
                !chosen->crew_clear_certified && bc::fuel_remaining() >= 70000 &&
                ward_opportunity(w, intended, chosen->action) &&
                chosen->priority < Priority::Survival && iteration < Settings::max_actions - 1) {
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
                if (std::string_view(chosen->action.reason) ==
                    "assembly-early-funded-rendezvous-wait")
                    LogLine("T1H")
                        .field(w.round)
                        .field(w.self.id)
                        .field(memory_.mission.group)
                        .field(chosen->action.reason)
                        .emit();
                break;
            }
            if (certified_reset)
                reset_receipt = make_solo_reset_receipt(w, chosen->mission, chosen->action);
            else
                reset_receipt.reset();
            if (chosen->solo_clear_certified && chosen->action.kind == Kind::BasicCamp)
                basic_receipt = make_solo_basic_receipt(w, *chosen);
            else
                basic_receipt.reset();
            bool crew_admission_failed = false;
            if (chosen->crew_clear_certified &&
                chosen->crew_clear_proof == ClearProofKind::BasicOnly) {
                // This fresh proof needs only the ordinary hit. Optional kit
                // availability must not impose a detailed bundle's62k budget.
                crew_receipt.reset();
                crew_admission_failed = !crew_basic_first_action_valid(w, *chosen);
            } else if (chosen->crew_clear_certified)
                crew_receipt = make_crew_turn_receipt(w, *chosen);
            else {
                // No paid coalition proof can be consumed for this action.
                // Avoid reconstructing the large unused actor/camp payload.
                crew_receipt.reset();
            }
            if (certified_reset && (!reset_receipt || !reset_receipt->valid))
                break;
            if (crew_admission_failed ||
                (chosen->crew_clear_certified && crew_receipt && crew_receipt->required &&
                 (!crew_receipt->valid ||
                  iteration + crew_receipt->continuations >= Settings::max_actions))) {
                memory_.mission = prior;
                break;
            }
            remember(w, memory_);
            auto result = execute(w, chosen->action);
            commit_awake_entry(memory_, *chosen, result.success, w.round);
            reset_accepted = certified_reset && result.success;
            basic_accepted = basic_receipt && basic_receipt->valid && result.success;
            crew_accepted = crew_receipt && crew_receipt->valid && result.success;
            if (result.outcome == Outcome::Stale) {
                memory_.mission = prior;
                return;
            }
            if (result.success) {
                w.publish_claim(camp_job ? memory_.mission.group : -1);
                const auto &a = chosen->action;
                clear_followup = memory_.mission.phase == Phase::Clear &&
                                 (chosen->crew_clear_certified || a.kind == Kind::BasicCamp ||
                                  a.kind == Kind::CastCamp ||
                                  (a.kind == Kind::CastSelf &&
                                   std::string_view(a.reason) == "farm-certified-solo-live-reset"));
                if (a.kind == Kind::Move) {
                    solo_entry_followup =
                        std::string_view(a.reason) == "solo-early-funded-stage-move" ||
                        std::string_view(a.reason) == "chain-early-funded-stage-move";
                    memory_.mission.last_progress = w.round;
                    memory_.mission.last_pos = a.at;
                }
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
                clear_followup = false;
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
            if (w.round != static_cast<int>(bc::round_number()))
                return;
            if (w.self.channel != Channel::None)
                break;
            if (clear_followup && (!reset_receipt || !reset_receipt->valid) &&
                (!crew_receipt || !crew_receipt->valid) && memory_.mission.phase == Phase::Clear &&
                memory_.mission.group >= 0 &&
                memory_.mission.group < static_cast<int>(w.groups.size())) {
                const auto &camps = w.groups[memory_.mission.group].camps;
                const auto contribution = current_camp_contribution(
                    w.self, std::span<const Camp>(camps), memory_.moved_round != w.round);
                if (!contribution.ready || contribution.dps <= 0) {
                    // Spent permissions do not turn a real completed hit into
                    // missing help. End this safe owner opportunity; threats
                    // still return to central survival arbitration when funded.
                    if (bc::fuel_remaining() < 32000)
                        break;
                    const double next_reply = incoming_damage(w, w.self.pos);
                    if (w.round != static_cast<int>(bc::round_number()))
                        return;
                    if (combat_detail::known_reply(next_reply) &&
                        next_reply + .25 * w.self.max_hp < w.self.hp)
                        break;
                }
            }
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
            std::cout << "TACTICS_ERROR [" << tactics::native_context << "] " << e.what() << '\n';
        } catch (...) {
            std::cout << "TACTICS_ERROR unknown\n";
        }
        cambc::end_turn();
    }
}

#pragma once
#include "camp_actions.h"
#ifndef TACTICS_CREW_SEQUENCE_MODEL_ONLY
#include "sdk_world.h"
#endif

namespace tactics {
// This receipt carries one paid fixed-position coalition proof across exactly
// one accepted stationary mutation and one actual refresh. It never authorizes
// a later owner, another participant's turn, movement, or a future allowance.
struct CrewTurnReceipt {
    bool valid = false, required = false;
    int owner = -1, round = -1, serial = -1, group = -1, count = 0, continuations = 0;
    Action action{};
    Actor actor{};
    std::array<Actor, 6> crew{};
    std::vector<Camp> camps;
};
inline bool crew_same_spell(const Spell &a, const Spell &b) {
    return a.kind == b.kind && a.slot == b.slot && a.recharge == b.recharge && a.range == b.range &&
           a.radius == b.radius && a.duration == b.duration && a.amount == b.amount &&
           a.scale == b.scale && a.exclusive == b.exclusive && a.camps == b.camps &&
           a.enemies == b.enemies && a.allies == b.allies && a.self == b.self &&
           a.ground == b.ground;
}
inline bool crew_same_body(const Actor &a, const Actor &b) {
    if (a.id != b.id || a.type != b.type || a.pos != b.pos || a.max_hp != b.max_hp ||
        a.strength != b.strength || a.focus != b.focus || a.range != b.range ||
        a.move_speed != b.move_speed || a.gems != b.gems || a.monster != b.monster ||
        a.home != b.home || a.mitigation != b.mitigation ||
        a.camp_mitigation != b.camp_mitigation || !b.alive || b.stunned ||
        b.channel != Channel::None)
        return false;
    return crew_same_spell(a.spells[0], b.spells[0]) && crew_same_spell(a.spells[1], b.spells[1]);
}
inline bool crew_body_effect_matches(const Actor &before, const Actor &after, const Actor &caster,
                                     const Action &action) {
    if (!crew_same_body(before, after))
        return false;
    double hp = before.hp, shield = before.shield;
    int shield_ticks = before.shield_ticks;
    if ((action.kind == Kind::CastSelf || action.kind == Kind::CastChampion) &&
        action.target == before.id && action.slot >= 0 && action.slot < 2) {
        const auto &spell = caster.spells[action.slot];
        if (spell.kind == 5)
            hp = std::min(before.max_hp, before.hp + spell.amount);
        else if (spell.kind == 7) {
            shield = std::max(before.shield, spell.amount);
            shield_ticks = spell.duration;
        }
    }
    return std::abs(after.hp - hp) <= .005 && std::abs(after.shield - shield) <= .005 &&
           after.shield_ticks == shield_ticks;
}
inline bool crew_same_action(const Action &a, const Action &b) {
    return a.kind == b.kind && a.target == b.target && a.slot == b.slot &&
           (a.kind != Kind::CastGround || a.at == b.at);
}
inline Action crew_stationary_choice(const Actor &actor, std::span<const Actor> crew,
                                     std::span<const Camp> camps, bool exclusive_allowed) {
    return certified_camp_first_action(actor, crew, camps, ClearProofKind::DetailedBundle,
                                       exclusive_allowed);
}
// The producing quote and this action must refer to the same immutable World
// snapshot. Basic-only proof authorizes one ordinary hit, never a follow-up
// cast/reset or the next owner's readiness. The native gateway still checks
// the actual permission, target and owner epoch immediately before mutation.
inline bool crew_basic_first_action_valid(World &w, const Proposal &selected) {
    const auto &mission = selected.mission;
    const int gi = mission.group;
    if (!selected.valid || !selected.crew_clear_certified ||
        selected.crew_clear_proof != ClearProofKind::BasicOnly ||
        selected.crew_proof_owner != w.self.id || selected.crew_proof_round != w.round ||
        selected.crew_proof_serial != w.serial || w.round != static_cast<int>(bc::round_number()) ||
        mission.phase != Phase::Clear || gi < 0 || gi >= static_cast<int>(w.groups.size()) ||
        mission.assembly_count < 1 || mission.assembly_count > 6)
        return false;
    const auto &view = w.groups[gi];
    if (!view.fresh(w.round) || view.state != Lifecycle::Alive || view.camps.empty() ||
        view.camps.size() > 8)
        return false;
    bool self_selected = false;
    for (int k = 0; k < mission.assembly_count; ++k) {
        const int id = mission.assembly_ids[k];
        if (id < 0)
            return false;
        for (int prior = 0; prior < k; ++prior)
            if (mission.assembly_ids[prior] == id)
                return false;
        const Actor *body = id == w.self.id ? &w.self : nullptr;
        if (!body)
            for (const auto &ally : w.allies)
                if (ally.id == id)
                    body = &ally;
        if (!body || !body->alive || body->hp <= 0 || body->stunned ||
            body->channel != Channel::None)
            return false;
        self_selected |= id == w.self.id;
    }
    const auto action = certified_camp_first_action(
        w.self, {}, view.camps, ClearProofKind::BasicOnly, w.memory.moved_round != w.round);
    return self_selected && action.kind == Kind::BasicCamp &&
           crew_same_action(selected.action, action);
}
inline void crew_project_effect(Actor &actor, std::vector<Camp> &camps, const Action &action) {
    const auto before = camps;
    for (auto &camp : camps)
        camp.hp = std::max(0.0, camp.hp - camp_action_damage(actor, action, before, camp));
    if (action.kind == Kind::BasicCamp) {
        actor.can_attack = false;
        actor.enhanced = false;
        if (actor.range > 1)
            actor.can_move = false;
    } else if (action.slot >= 0 && action.slot < 2) {
        auto &spell = actor.spells[action.slot];
        actor.can_cast = false;
        spell.ready = false;
        spell.cooldown = spell.recharge;
        if (action.kind == Kind::CastSelf && spell.kind == 1)
            actor.can_attack = true;
    }
}
inline CrewTurnReceipt make_crew_turn_receipt(World &w, const Proposal &selected) {
    CrewTurnReceipt out;
    // A paid action must not enter an incompletely funded modeled bundle.
    // Clear this only after proving that no actual continuation is needed.
    out.required = selected.valid && selected.crew_clear_certified;
    if (selected.crew_clear_proof == ClearProofKind::BasicOnly) {
        out.required = out.required && !crew_basic_first_action_valid(w, selected);
        return out;
    }
    const auto &mission = selected.mission;
    const int gi = mission.group;
    if (!selected.valid || !selected.crew_clear_certified ||
        selected.crew_clear_proof != ClearProofKind::DetailedBundle ||
        selected.crew_proof_owner != w.self.id || selected.crew_proof_round != w.round ||
        selected.crew_proof_serial != w.serial || mission.phase != Phase::Clear || gi < 0 ||
        gi >= static_cast<int>(w.groups.size()) || mission.assembly_count < 1 ||
        mission.assembly_count > 6 || bc::fuel_remaining() < 24000 ||
        w.round != static_cast<int>(bc::round_number()))
        return out;
    const auto &view = w.groups[gi];
    if (!view.fresh(w.round) || view.state != Lifecycle::Alive || view.camps.empty() ||
        view.camps.size() > 8 || !w.self.alive || w.self.completed || w.self.stunned ||
        w.self.channel != Channel::None)
        return out;
    bool self_selected = false;
    for (int k = 0; k < mission.assembly_count; ++k) {
        const int id = mission.assembly_ids[k];
        for (int prior = 0; prior < k; ++prior)
            if (mission.assembly_ids[prior] == id)
                return out;
        const Actor *body = id == w.self.id ? &w.self : nullptr;
        if (!body)
            for (const auto &ally : w.allies)
                if (ally.id == id)
                    body = &ally;
        if (!body || !body->alive || body->stunned || body->channel != Channel::None)
            return out;
        out.crew[k] = *body;
        self_selected |= id == w.self.id;
    }
    if (!self_selected)
        return out;
    const bool compatible = w.memory.moved_round != w.round;
    const auto crew = std::span<const Actor>(out.crew.data(), mission.assembly_count);
    if (!crew_same_action(selected.action,
                          crew_stationary_choice(w.self, crew, view.camps, compatible)))
        return out;
    Actor projected = w.self;
    auto remaining = view.camps;
    crew_project_effect(projected, remaining, selected.action);
    const Action following = crew_stationary_choice(projected, crew, remaining, compatible);
    out.required = following.kind != Kind::None;
    if (!out.required)
        return out;
    out.continuations = following.kind == Kind::CastSelf && following.slot >= 0 &&
                                projected.spells[following.slot].kind == 1
                            ? 2
                            : 1;
    const unsigned admission = selected.action.kind == Kind::BasicCamp ? 62000
                               : selected.action.kind == Kind::CastSelf &&
                                       selected.action.slot >= 0 &&
                                       w.spells[selected.action.slot].kind == 1
                                   ? 36000
                                   : 44000;
    if (bc::fuel_remaining() < admission)
        return out;
    out.valid = true;
    out.owner = w.self.id;
    out.round = w.round;
    out.serial = w.serial;
    out.group = gi;
    out.count = mission.assembly_count;
    out.action = selected.action;
    out.actor = w.self;
    out.camps = view.camps;
    return out;
}
inline std::optional<Proposal> crew_turn_followup(World &w, Memory &memory,
                                                  CrewTurnReceipt &receipt, bool accepted) {
    const bool valid = receipt.valid;
    receipt.valid = false; // One consumer, including all rejection paths.
    if (!valid || !accepted || bc::fuel_remaining() < 16000 ||
        w.round != static_cast<int>(bc::round_number()) || receipt.round != w.round ||
        receipt.serial + 1 != w.serial || receipt.owner != w.self.id ||
        memory.mission.phase != Phase::Clear || memory.mission.group != receipt.group ||
        memory.mission.assembly_count != receipt.count || receipt.group < 0 ||
        receipt.group >= static_cast<int>(w.groups.size()) ||
        !crew_body_effect_matches(receipt.actor, w.self, receipt.actor, receipt.action))
        return std::nullopt;
    const auto &view = w.groups[receipt.group];
    if (!view.fresh(w.round) || view.state != Lifecycle::Alive || w.self.completed)
        return std::nullopt;
    for (int k = 0; k < receipt.count; ++k) {
        const auto &before = receipt.crew[k];
        if (memory.mission.assembly_ids[k] != before.id)
            return std::nullopt;
        const Actor *after = before.id == w.self.id ? &w.self : nullptr;
        if (!after)
            for (const auto &ally : w.allies)
                if (ally.id == before.id)
                    after = &ally;
        if (!after || !crew_body_effect_matches(before, *after, receipt.actor, receipt.action))
            return std::nullopt;
    }
    bool killed = false;
    for (const auto &before : receipt.camps) {
        const double expected =
            std::max(0.0, before.hp - camp_action_damage(receipt.actor, receipt.action,
                                                         receipt.camps, before));
        const auto *after = camp_action_target(view.camps, before.id);
        if (expected <= .001) {
            killed = true;
            if (after && after->hp > .001)
                return std::nullopt;
            if (!after && std::find(view.known_dead.begin(), view.known_dead.end(), before.id) ==
                              view.known_dead.end())
                return std::nullopt;
        } else if (!after || after->pos != before.pos || after->strength != before.strength ||
                   after->range != before.range || std::abs(after->hp - expected) > .005)
            return std::nullopt;
    }
    for (const auto &camp : view.camps)
        if (!camp_action_target(receipt.camps, camp.id))
            return std::nullopt;
    const bool cast = receipt.action.kind != Kind::BasicCamp;
    if ((cast && w.self.can_cast) || (!cast && w.self.can_attack))
        return std::nullopt;
    for (int k = 0; k < 2; ++k) {
        const int expected = cast && k == receipt.action.slot ? receipt.actor.spells[k].recharge
                                                              : receipt.actor.spells[k].cooldown;
        if (w.self.spells[k].cooldown != expected &&
            !(receipt.actor.type == 2 && killed && w.self.spells[k].cooldown == 0))
            return std::nullopt;
    }
    std::array<Actor, 6> actual{};
    for (int k = 0; k < receipt.count; ++k) {
        if (receipt.crew[k].id == w.self.id)
            actual[k] = w.self;
        else
            for (const auto &ally : w.allies)
                if (ally.id == receipt.crew[k].id)
                    actual[k] = ally;
    }
    const auto action =
        crew_stationary_choice(w.self, std::span<const Actor>(actual.data(), receipt.count),
                               view.camps, memory.moved_round != w.round);
    const bool reset =
        action.kind == Kind::CastSelf && action.slot >= 0 && w.spells[action.slot].kind == 1;
    if (action.kind == Kind::None ||
        (action.kind != Kind::BasicCamp && bc::fuel_remaining() < (reset ? 38000u : 44000u)))
        return std::nullopt;
    Proposal proposal;
    proposal.action = action;
    proposal.mission = memory.mission;
    proposal.priority = Priority::Incumbent;
    proposal.value = memory.mission.rate;
    proposal.valid = proposal.crew_clear_certified = true;
    proposal.crew_clear_proof = ClearProofKind::DetailedBundle;
    proposal.crew_proof_owner = w.self.id;
    proposal.crew_proof_round = w.round;
    proposal.crew_proof_serial = w.serial;
    return proposal;
}
} // namespace tactics

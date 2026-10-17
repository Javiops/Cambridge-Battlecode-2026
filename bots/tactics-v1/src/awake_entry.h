#pragma once
#include "types.h"
#include <span>
namespace tactics {
inline bool awake_entry_active(const AwakeEntryContract &c) {
    return c.owner >= 0 && c.group >= 0 && c.camp >= 0 && c.round >= 0;
}
template <class FreshLegal>
inline bool complete_awake_entry_route(const Actor &actor, std::span<const Pos> route, Pos stage,
                                       FreshLegal legal) {
    if (!actor.alive || actor.completed || actor.stunned || actor.channel != Channel::None ||
        !actor.can_move || actor.move_speed < 1 || actor.move_speed > 8 || route.size() < 2 ||
        route.size() > std::size_t(actor.move_speed + 1) || route.front() != actor.pos ||
        route.back() != stage || stage == actor.pos)
        return false;
    for (unsigned k = 0; k < route.size(); ++k)
        if (!legal(route[k]) || (k && distance(route[k - 1], route[k]) != 1))
            return false;
    return true;
}
inline bool same_awake_entry(const AwakeEntryContract &a, const AwakeEntryContract &b) {
    return a.owner == b.owner && a.group == b.group && a.camp == b.camp && a.round == b.round &&
           a.stage == b.stage && a.target == b.target;
}
enum class AwakeEntryObservation { None, Stale, Pending, Protected, Invalid, Expired };
inline void abandon_awake_entry(Memory &m, int round) {
    const auto contract = m.awake_entry;
    m.awake_entry = {};
    m.mission.awake_entry = {};
    if (!awake_entry_active(contract))
        return;
    m.failed_group = contract.group;
    m.failed_until = round + Settings::job_lease;
    m.awake_entry_backoff_group = contract.group;
    m.awake_entry_backoff_until = round + Settings::job_lease;
    if (m.mission.group == contract.group &&
        (m.mission.phase == Phase::Travel || m.mission.phase == Phase::Observe ||
         m.mission.phase == Phase::Assemble))
        m.mission = {};
}
// fresh_epoch means the World round still matches native time, not camp
// visibility. A fresh World with a missing/null named camp invalidates the
// pending receipt; it does not defer its fixed deadline.
inline AwakeEntryObservation observe_awake_entry(Memory &m, const Actor &actual, int round,
                                                 bool fresh_epoch, const Camp *camp,
                                                 bool protected_work) {
    const auto contract = m.awake_entry;
    if (!awake_entry_active(contract))
        return AwakeEntryObservation::None;
    if (!fresh_epoch || round < contract.round)
        return AwakeEntryObservation::Stale;
    if (!actual.alive || protected_work) {
        m.awake_entry = {};
        m.mission.awake_entry = {};
        return AwakeEntryObservation::Protected;
    }
    if (round > contract.round + 1) {
        abandon_awake_entry(m, round);
        return AwakeEntryObservation::Expired;
    }
    if (actual.id != contract.owner || actual.pos != contract.stage || !camp || camp->hp <= 0 ||
        camp->id != contract.camp || camp->pos != contract.target) {
        abandon_awake_entry(m, round);
        return AwakeEntryObservation::Invalid;
    }
    return AwakeEntryObservation::Pending;
}
inline bool future_awake_entry_available(const Memory &m, int gi, int round) {
    return !awake_entry_active(m.awake_entry) &&
           !(m.awake_entry_backoff_group == gi && round < m.awake_entry_backoff_until) &&
           !(m.failed_group == gi && round < m.failed_until);
}
// Call only after the native gateway, never when selecting a hold/intention.
inline void commit_awake_entry(Memory &m, const Proposal &p, bool accepted, int round) {
    if (!accepted || p.action.kind == Kind::None)
        return;
    const auto offered = p.mission.awake_entry;
    if (p.action.kind == Kind::Move && awake_entry_active(offered)) {
        if (offered.round != round || p.action.at != offered.stage ||
            p.mission.group != offered.group)
            return;
        if (!awake_entry_active(m.awake_entry))
            m.awake_entry = offered;
        // Existing source round/deadline cannot be renewed by repeated input.
        return;
    }
    if (!awake_entry_active(m.awake_entry))
        return;
    const bool full_current =
        p.awake_entry_current_certified && p.mission.group == m.awake_entry.group &&
        p.mission.phase == Phase::Clear &&
        (p.action.kind == Kind::BasicCamp || p.action.kind == Kind::CastCamp ||
         p.action.kind == Kind::CastSelf || p.action.kind == Kind::CastGround);
    const bool protected_action = p.action.kind == Kind::Recall || p.action.kind == Kind::Tribute ||
                                  p.mission.phase == Phase::Deliver ||
                                  p.mission.phase == Phase::Recover ||
                                  p.mission.phase == Phase::Collect;
    const bool other_current_certificate =
        p.mission.group != m.awake_entry.group && p.mission.phase == Phase::Clear &&
        (p.solo_clear_certified || p.crew_clear_certified) &&
        (p.action.kind == Kind::BasicCamp || p.action.kind == Kind::CastCamp ||
         p.action.kind == Kind::CastGround || p.action.kind == Kind::CastSelf);
    // A raw positive rate, retargeted Move or None does not prove new work.
    if (full_current || protected_action || other_current_certificate) {
        m.awake_entry = {};
        m.mission.awake_entry = {};
    }
    (void)round;
}
} // namespace tactics

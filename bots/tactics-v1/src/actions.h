#pragma once
#include "log.h"
#include "sdk_world.h"
#include <iostream>
namespace tactics {
struct Execution {
    Outcome outcome = Outcome::Rejected;
    int error = 0;
    bool success = false;
};
inline bool any_basic_target(World &w) {
    if (w.restricted_continuation_snapshot) {
        const auto target = w.camp(w.restricted_continuation_camp);
        return target && distance(position(w.me.position()), position(target->position())) <=
                             w.me.attack_range();
    }

    for (const auto &e : w.enemies)
        if (e.alive && distance(e.pos, w.self.pos) <= w.self.range)
            return true;
    for (const auto &g : w.groups)
        if (g.fresh(w.round))
            for (const auto &c : g.camps)
                if (c.hp > 0 && distance(c.pos, w.self.pos) <= w.self.range)
                    return true;
    return false;
}
// The only gameplay mutation gateway. Planners never invoke an SDK action.
inline Execution execute(World &w, const Action &a) {
    Execution result;
    if (w.restricted_continuation_snapshot) {
        const bool ground_damage =
            a.kind == Kind::CastGround && a.slot >= 0 && a.slot < 2 && w.spells[a.slot].kind == 3 &&
            w.spells[a.slot].ground && std::isfinite(w.spells[a.slot].amount) &&
            w.spells[a.slot].amount > 0 && a.at == w.restricted_continuation_at;
        if (a.target != w.restricted_continuation_camp ||
            (a.kind != Kind::BasicCamp && a.kind != Kind::CastCamp && a.kind != Kind::CastSelf &&
             !ground_damage)) {
            result.outcome = Outcome::Stale;
            return result;
        }
    }

    if (!fuel(1600) || w.round != static_cast<int>(bc::round_number())) {
        result.outcome = Outcome::Stale;
        return result;
    }
    // Queries can consume an owner budget and resume in a later round. Check
    // again immediately before each SDK mutation, funding the atomic action
    // and compact audit records without making cheap actions pay dash costs.
    auto mutation_ready = [&]() {
        if (bc::fuel_remaining() < 12000 || w.round != static_cast<int>(bc::round_number())) {
            result.outcome = Outcome::Stale;
            return false;
        }
        return true;
    };
    try {
        const bool alive = w.me.is_alive();
        if (!alive && a.kind != Kind::Buy && a.kind != Kind::Sell && a.kind != Kind::BuyConsumable)
            return result;
        if (a.kind == Kind::None)
            return result;
        bool ok = true;
        switch (a.kind) {
        case Kind::Move:
            if (!w.me.can_move() || !w.free(a.at))
                return result;
            if (!mutation_ready())
                return result;
            ok = w.me.move_absolute(sdk(a.at));
            if (ok)
                w.memory.moved_round = w.round;
            break;
        case Kind::BasicChampion: {
            auto c = w.champion(a.target);
            if (!c || !c->is_alive() || !w.me.can_attack() ||
                distance(position(w.me.position()), position(c->position())) > w.me.attack_range())
                return result;
            if (!mutation_ready())
                return result;
            w.me.attack(*c);
            break;
        }
        case Kind::BasicCamp: {
            auto c = w.camp(a.target);
            if (!c || !w.me.can_attack() ||
                distance(position(w.me.position()), position(c->position())) > w.me.attack_range())
                return result;
            if (!mutation_ready())
                return result;
            w.me.attack(*c);
            break;
        }
        case Kind::BasicLock: {
            if (!w.me.can_attack())
                return result;
            auto lock = w.enemy_lock(a.at);
            if (!lock)
                return result;
            if (distance(position(w.me.position()), position(lock->position())) >
                w.me.attack_range())
                return result;
            if (!mutation_ready())
                return result;
            w.me.attack(*lock);
            result.outcome = Outcome::LockHit;
            break;
        }
        case Kind::CastSelf:
        case Kind::CastChampion:
        case Kind::CastCamp:
        case Kind::CastGround: {
            if (a.slot < 0 || a.slot > 1)
                return result;
            const auto spell = w.me.abilities()[a.slot];
            if (!spell.is_ready())
                return result;
            if (w.spells[a.slot].exclusive && w.memory.moved_round == w.round)
                return result;
            if (spell.is_attack_reset() && !any_basic_target(w))
                return result;
            if (a.kind == Kind::CastSelf) {
                if (!mutation_ready())
                    return result;
                ok = spell.use();
            } else if (a.kind == Kind::CastChampion) {
                auto c = w.champion(a.target);
                if (!c || !c->is_alive())
                    return result;
                if (!mutation_ready())
                    return result;
                ok = spell.use(*c);
            } else if (a.kind == Kind::CastCamp) {
                auto c = w.camp(a.target);
                if (!c)
                    return result;
                if (!mutation_ready())
                    return result;
                ok = spell.use(*c);
            } else {
                if (!w.geo.valid(a.at))
                    return result;
                if (spell.is_dash()) {
                    if (bc::fuel_remaining() < 24000 ||
                        w.round != static_cast<int>(bc::round_number())) {
                        result.outcome = Outcome::Stale;
                        return result;
                    }
                    // Dash traversal is distinct from legal landing. Keep
                    // ground AoE casts free to target their normal terrain.
                    if (!w.free(a.at) || !spell.valid_tiles().is_set(sdk(a.at)))
                        return result;
                    const auto info = spell.info();
                    const auto *dash = info ? std::get_if<bc::ability_dash>(&*info) : nullptr;
                    if (!dash)
                        return result;
                    // A two-step diagonal has one unique intermediate tile.
                    // Visible units block that path even with an empty landing.
                    // Native range masks alone do not express this constraint.
                    const auto origin = w.me.position();
                    const auto occupied = bc::vision::champion_tiles() | bc::vision::camp_tiles() |
                                          bc::vision::teleport_tiles();
                    if (occupied.is_set(sdk(a.at)))
                        return result;
                    auto path_blockers = bc::map::walls() | w.geo.enemy_spawn | occupied;
                    path_blockers.set(origin, false);
                    const auto reachable = path_blockers.reachable_tiles(
                        origin, static_cast<std::uint16_t>(dash->range));
                    if (!reachable.is_set(sdk(a.at)))
                        return result;
                }
                if (!mutation_ready())
                    return result;
                ok = spell.use(sdk(a.at));
            }
            break;
        }
        case Kind::Recall:
            if (w.memory.channel_attempt_round == w.round)
                return result;
            if (!mutation_ready())
                return result;
            w.memory.channel_attempt_round = w.round;
            w.me.recall();
            result.outcome = w.me.is_recalling() ? Outcome::Started : Outcome::Rejected;
            ok = result.outcome == Outcome::Started;
            break;
        case Kind::Tribute: {
            if (w.memory.channel_attempt_round == w.round || w.me.gem_count() == 0)
                return result;
            const bool lock_hit_possible = w.me.can_attack() && w.enemy_lock(a.at).has_value();
            if (!mutation_ready())
                return result;
            w.memory.channel_attempt_round = w.round;
            w.me.submit_gems(sdk(a.at));
            result.outcome = w.me.is_submitting_gems() ? Outcome::Started : Outcome::Rejected;
            if (result.outcome != Outcome::Started && lock_hit_possible && !w.me.can_attack())
                result.outcome = Outcome::LockHit;
            ok = result.outcome == Outcome::Started || result.outcome == Outcome::LockHit;
            break;
        }
        case Kind::CancelRecall:
            if (!w.me.is_recalling())
                return result;
            if (!mutation_ready())
                return result;
            w.me.cancel_recall();
            result.outcome = Outcome::Interrupted;
            break;
        case Kind::CancelTribute:
            if (!w.me.is_submitting_gems())
                return result;
            if (!mutation_ready())
                return result;
            w.me.cancel_submit_gems();
            result.outcome = Outcome::Interrupted;
            break;
        case Kind::Ward:
            if (w.me.ward_cooldown() > 0)
                return result;
            if (!mutation_ready())
                return result;
            ok = w.me.place_ward(sdk(a.at));
            break;
        case Kind::Buy: {
            auto item = static_cast<bc::item_type>(a.item);
            if (!w.me.can_buy(item, a.count))
                return result;
            if (!mutation_ready())
                return result;
            w.me.buy(item, a.count);
            break;
        }
        case Kind::Sell:
            if (!w.me.can_sell())
                return result;
            if (!mutation_ready())
                return result;
            w.me.sell(static_cast<bc::item_type>(a.item), a.count);
            break;
        case Kind::BuyConsumable: {
            auto item = static_cast<bc::consumable_type>(a.item);
            if (!w.me.can_buy(item))
                return result;
            if (!mutation_ready())
                return result;
            w.me.buy(item);
            break;
        }
        case Kind::UseConsumable:
            if (!mutation_ready())
                return result;
            ok = w.me.consumables()[static_cast<bc::consumable_type>(a.item)].use(sdk(a.at));
            break;
        default:
            return result;
        }
        result.success = ok;
        if (!ok)
            result.outcome = Outcome::Blocked;
        else if (result.outcome == Outcome::Rejected)
            result.outcome = Outcome::Applied;
    } catch (const bc::error &e) {
        result.error = static_cast<int>(e.code());
        result.outcome = Outcome::Rejected;
    } catch (const std::exception &) {
        result.error = -1;
        result.outcome = Outcome::Rejected;
    }
    if (!result.success && (a.kind == Kind::Move || a.kind == Kind::CastGround)) {
        w.memory.blocked_tile = a.at;
        w.memory.blocked_round = w.round;
    }
    // One compact record per accepted/rejected action, sufficient for behavior audits.
    LogLine("T1")
        .field(w.round)
        .field(w.self.id)
        .field(phase_name(w.memory.mission.phase))
        .field(static_cast<int>(a.kind))
        .field(static_cast<int>(result.outcome))
        .field(result.error)
        .field(a.reason)
        .emit();
    LogLine("T1X")
        .field(w.round)
        .field(w.self.id)
        .field(w.serial)
        .field(w.memory.mission.group)
        .field(a.target)
        .field(a.at.x)
        .field(a.at.y)
        .field(w.self.gems)
        .field(w.gold)
        .field(static_cast<std::int64_t>(bc::fuel_remaining()))
        .emit();
    return result;
}
} // namespace tactics

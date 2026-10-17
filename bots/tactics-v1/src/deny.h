#pragma once
#include "combat.h"

namespace tactics {
struct DenialEffect {
    double hp_damage = 0;
    int control_ticks = 0;
    bool applicable = false, lethal = false, controls = false;
};
// Only the selected FIRST action receives denial credit. A move/reset or a
// cast+basic sequence does not claim its eventual kill has already happened.
inline DenialEffect denial_effect(const Actor &self, const Actor &target, const Action &action,
                                  double native_spell_hp = -1) {
    DenialEffect out;
    if (!self.alive || !target.alive || self.stunned || self.channel != Channel::None)
        return out;
    double raw = 0;
    if (action.kind == Kind::BasicChampion && action.target == target.id && self.can_attack &&
        distance(self.pos, target.pos) <= self.range) {
        out.applicable = true;
        raw = self.strength;
        if (self.type == combat_detail::marcella_type && self.enhanced)
            out.control_ticks = 1;
    } else if ((action.kind == Kind::CastChampion || action.kind == Kind::CastGround) &&
               action.slot >= 0 && action.slot < 2 && self.can_cast) {
        const auto &spell = self.spells[action.slot];
        const bool hits = action.kind == Kind::CastChampion
                              ? action.target == target.id && spell.enemies &&
                                    distance(self.pos, target.pos) <= spell.range
                              : spell.ground && spell.enemies && spell.radius >= 0 &&
                                    distance(self.pos, action.at) <= spell.range &&
                                    distance(action.at, target.pos) <= spell.radius;
        if (!spell.ready || !combat_detail::offensive(spell) || !hits)
            return out;
        out.applicable = true;
        raw = spell.amount;
        if (combat_detail::applies_control(self, spell))
            out.control_ticks = std::max(0, spell.duration);
    }
    if (!out.applicable || !combat_detail::direct_hit_survives(self, target))
        return {};
    out.hp_damage = std::min(target.hp, std::max(0.0, raw * target.mitigation - target.shield));
    if (action.kind == Kind::CastChampion && native_spell_hp >= 0)
        out.hp_damage = std::min(target.hp, native_spell_hp);
    out.lethal = out.hp_damage >= target.hp - .001;
    out.controls = target.type != combat_detail::marcella_type && out.control_ticks > 0;
    return out;
}
inline double denied_conversion_value(int bag, int remaining, int new_channel_ticks,
                                      const DenialEffect &effect) {
    if (bag <= 0 || remaining < 0 || new_channel_ticks <= 0 || !effect.applicable ||
        (!effect.lethal && !effect.controls))
        return 0;
    // This is the current conversion window, not permanent destruction of an
    // unseen wallet. Early interruption earns only the observable reset delay;
    // it cannot repeatedly count the same still-running channel as a full bag.
    if (effect.lethal)
        return bag;
    const int delay = std::max(0, 1 + effect.control_ticks + new_channel_ticks - remaining);
    return bag * std::min(1.0, double(delay) / new_channel_ticks);
}
inline bool denial_beats_trade(double credit, double response_turns, bool alternative_known,
                               double alternative_rate, double margin = Settings::switch_margin) {
    return alternative_known && std::isfinite(credit) && credit > 0 &&
           std::isfinite(response_turns) && response_turns > 0 && std::isfinite(alternative_rate) &&
           alternative_rate >= 0 && credit > alternative_rate * response_turns * margin;
}
} // namespace tactics

#ifndef TACTICS_COMBAT_MODEL_ONLY
namespace tactics {
inline std::optional<Proposal> denial_proposal(World &w, Memory &memory,
                                               const std::optional<Proposal> &fight,
                                               const std::optional<Proposal> &bank,
                                               const std::optional<Proposal> &farm) {
    if (!fight || !fight->valid || !w.self.alive || w.self.channel != Channel::None ||
        bc::fuel_remaining() < 32000 ||
        (bank && bank->priority >= Priority::Survival && bank->action.kind != Kind::None) ||
        (farm && farm->priority >= Priority::Survival && farm->action.kind != Kind::None))
        return std::nullopt;
    const auto &action = fight->action;
    if (action.kind != Kind::BasicChampion && action.kind != Kind::CastChampion &&
        action.kind != Kind::CastGround)
        return std::nullopt;
    double alternative = 0;
    bool alternative_known = false;
    for (const auto *proposal : {&bank, &farm})
        if (*proposal && (*proposal)->valid && (*proposal)->mission.rate > 0) {
            alternative = std::max(alternative, (*proposal)->mission.rate);
            alternative_known = true;
        }
    if (!alternative_known && memory.mission.rate > 0 && memory.mission.expiry >= w.round) {
        alternative = memory.mission.rate;
        alternative_known = true;
    }
    std::optional<Proposal> best;
    auto offer = [&](double credit, double turns, bool deciding, const char *reason,
                     int group = -1) {
        if (!deciding && !denial_beats_trade(credit, turns, alternative_known, alternative))
            return;
        Proposal p = *fight;
        p.action.reason = reason;
        p.mission.intent = Intent::Deny;
        p.mission.phase = Phase::Fight;
        p.mission.group = group;
        if (farm && farm->mission.phase == Phase::Collect &&
            w.on_group(farm->mission.group, w.self.pos)) {
            p.mission = farm->mission; // A stationary action keeps a real holder.
            p.mission.intent = Intent::Deny;
        }
        p.mission.rate = credit / std::max(1.0, turns);
        p.priority = deciding ? Priority::Deciding : Priority::Incumbent;
        p.value = p.mission.rate;
        if (!best || p.priority > best->priority ||
            (p.priority == best->priority && p.value > best->value))
            best = p;
    };
    std::vector<std::pair<int, DenialEffect>> effects;
    effects.reserve(w.enemies.size());
    bool native_checked = false;
    for (const auto &enemy : w.enemies) {
        auto effect = denial_effect(w.self, enemy, action);
        if (effect.lethal && action.kind == Kind::CastChampion && !native_checked &&
            bc::fuel_remaining() >= 36000) {
            native_checked = true;
            effect = denial_effect(w.self, enemy, action,
                                   combat_detail::spell_hp_damage(w, w.spells[action.slot], enemy));
        }
        if (action.kind == Kind::CastChampion && effect.lethal && !native_checked)
            effect.lethal = false; // No fuel for the selected native lethal check.
        if (action.kind == Kind::CastGround)
            effect.lethal =
                false; // Area control can be credited without invented per-target kills.
        effects.push_back({enemy.id, effect});
        if (enemy.channel != Channel::Tribute)
            continue;
        const int ticks = tribute_ticks(enemy.gems, bc::constants::submit_gem_duration_multiplier,
                                        bc::constants::submit_gem_base_duration,
                                        bc::constants::submit_gem_minimum_duration);
        const double credit =
            denied_conversion_value(enemy.gems, enemy.channel_ticks, ticks, effect);
        if (credit > 0)
            offer(credit, 1, w.enemy_score + enemy.gems >= int(bc::constants::winning_gems),
                  "deny-visible-tribute-actual-first-action");
    }
    // One actual immediate kill can secure a contested reward when every enemy
    // holder is visible and removed, and a viable friendly collector is already
    // physically present. No remote intention substitutes for either role.
    if (farm && farm->mission.group >= 0 &&
        farm->mission.group < static_cast<int>(w.groups.size())) {
        const int gi = farm->mission.group;
        const auto &view = w.groups[gi];
        const auto &group = w.geo.groups[gi];
        if (view.fresh(w.round) && view.state == Lifecycle::Reward && group.gems > 0) {
            bool all_visible = true, collector = false, enemy_holder = false, all_removed = true;
            for (const auto &spawn : group.spawns)
                all_visible &= packed_bit(w.visible_bytes, w.geo.index(spawn.pos));
            for (const auto &ally : w.allies)
                collector |= ally.alive && ally.channel == Channel::None && !ally.stunned &&
                             ally.health_fraction() >= .35 && w.on_group(gi, ally.pos);
            for (const auto &enemy : w.enemies)
                if (w.on_group(gi, enemy.pos)) {
                    enemy_holder = true;
                    bool removed = false;
                    for (const auto &[id, effect] : effects)
                        removed |= id == enemy.id && effect.lethal;
                    all_removed &= removed;
                }
            bool timely = true;
            for (const auto &enemy : w.enemies) {
                bool removed = false;
                for (const auto &[id, effect] : effects)
                    removed |= id == enemy.id && effect.lethal;
                if (removed)
                    continue;
                for (const auto &spawn : group.spawns)
                    timely &= distance(enemy.pos, spawn.pos) >
                              possible_contact_reach(enemy) +
                                  (bc::constants::capture_time + 1) * std::max(1, enemy.move_speed);
            }
            for (const auto &sight : w.sightings) {
                const int age = w.round - sight.round;
                if (!sight.actor.alive || !combat_detail::recent_sighting(age))
                    continue;
                bool current = false;
                for (const auto &enemy : w.enemies)
                    current |= enemy.id == sight.actor.id;
                if (current)
                    continue;
                for (const auto &spawn : group.spawns)
                    timely &= distance(sight.actor.pos, spawn.pos) >
                              possible_contact_reach(sight.actor) +
                                  (age + bc::constants::capture_time + 1) *
                                      std::max(1, sight.actor.move_speed);
            }
            timely &= !w.warning_near(farm->mission.target, 4);
            const int altar = w.altar_distance(farm->mission.target);
            if (all_visible && collector && enemy_holder && all_removed && timely &&
                altar != unreachable) {
                const int speed = std::max(1, w.self.move_speed);
                const int ticks =
                    tribute_ticks(group.gems, bc::constants::submit_gem_duration_multiplier,
                                  bc::constants::submit_gem_base_duration,
                                  bc::constants::submit_gem_minimum_duration);
                offer(group.gems,
                      1 + bc::constants::capture_time + 1 + (altar + speed - 1) / speed + ticks,
                      false, "deny-contested-reward-actual-kill-and-collector", gi);
            }
        }
    }
    return best;
}
} // namespace tactics
#endif

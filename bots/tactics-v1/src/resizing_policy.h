#pragma once
#include "camp_basic.h"
#include "types.h"
#include <span>

namespace tactics {
inline bool resize_actor_current_basic(const Actor &a, const Camp &camp) {
    return a.alive && !a.completed && !a.stunned && a.channel == Channel::None && a.can_attack &&
           a.gems == 0 && std::isfinite(a.hp) && a.hp > 0 && std::isfinite(a.strength) &&
           a.strength > 0 && distance(a.pos, camp.pos) <= a.range;
}
inline std::optional<double> resize_basic_hit_lower(const Actor &a, const Camp &camp) {
    if (a.id < 0 || camp.id < 0 || !std::isfinite(camp.hp) || camp.hp <= 0 ||
        !std::isfinite(a.strength) || a.strength <= 0)
        return std::nullopt;
    const double raw = std::min(a.strength * (a.monster ? 1.1 : 1.),
                                double(float(a.strength) * (a.monster ? 1.1f : 1.f)));
    const auto hp_ulp = camp_basic_f32_ulp(camp.hp), product_ulp = camp_basic_f32_ulp(raw);
    if (!hp_ulp || !product_ulp)
        return std::nullopt;
    const double lower = raw - *hp_ulp - *product_ulp;
    return std::isfinite(lower) && lower > 0 ? std::optional(lower) : std::nullopt;
}
inline bool resize_current_basic_lethal(const Actor &a, const Camp &camp) {
    const auto hit = resize_basic_hit_lower(a, camp);
    return resize_actor_current_basic(a, camp) && camp.strength == 0 && hit &&
           *hit >= std::max(camp.hp, double(float(camp.hp)));
}

// The retained collector must also be admissible to its own ordinary current
// continuation. A mandatory-heal owner cannot promise this no-delay handoff.
inline bool resize_collector_current_basic(const Actor &a, const Camp &camp) {
    return a.health_fraction() >= Settings::ordinary_heal && resize_current_basic_lethal(a, camp);
}

inline bool resize_retained_job_active(const Mission &job, int round) {
    return round >= 0 && job.start >= 0 && job.start <= round && job.expiry > round;
}
inline bool resize_bank_certificate(bool personally_visible, bool warned, bool enemy_locked) {
    return personally_visible && !warned && !enemy_locked;
}

enum class ResizeRewardScope { SoleRecipient, PersonalShareLowerBound };
// Pricing facts only. The producer must pay independent fresh readiness,
// geometry/conversion and actual-counterpart certificates before constructing
// these inputs. A comparison result never grants attack/cast/move permission.
struct CurrentResizeCycle {
    int owner = -1, group = -1, round = -1, serial = -1, collector = -1, count = 0;
    std::array<int, 6> ids{{-1, -1, -1, -1, -1, -1}};
    Pos capture{}, bank{};
    double reward_once = 0, clear_ticks = 0, capture_ticks = 0, bank_ticks = 0, recovery_ticks = 0;
    // Exactly one recipient's conversion is priced. Credit is the entire
    // reward only for an independently proved sole-recipient plan; runtime
    // may instead use a personal-share lower bound and credit all others zero.
    int recipients = 0;
    double collector_reward = 0;
    int group_gems = 0, recipient_bound = 0;
    ResizeRewardScope reward_scope = ResizeRewardScope::SoleRecipient;
    bool known = false, sufficient = false, complete = false, collector_conversion_priced = false;
    double duration() const { return clear_ticks + capture_ticks + bank_ticks + recovery_ticks; }
};
struct CurrentResizeAlternative {
    int owner = -1, body = -1, group = -1, round = -1, serial = -1;
    double reward_once = 0, complete_ticks = 0;
    int group_gems = 0, recipient_bound = 0;
    ResizeRewardScope reward_scope = ResizeRewardScope::SoleRecipient;
    bool known = false, sufficient = false, complete = false;
    double rate() const { return reward_once / complete_ticks; }
};
enum class CurrentResizeKind { Keep, AddOne, ReleaseSelf };
struct CurrentResizeOption {
    CurrentResizeKind kind = CurrentResizeKind::Keep;
    CurrentResizeCycle cycle{};
    CurrentResizeAlternative alternative{};
};
struct CurrentResizeDecision {
    int option = -1;
    CurrentResizeKind kind = CurrentResizeKind::Keep;
    double keep_value = 0, changed_value = 0;
    bool baseline_known = false;
};
inline bool current_resize_share_valid(double credit, int total, int bound,
                                       ResizeRewardScope scope) {
    if (total < 1 || bound < 1 || bound > 6)
        return false;
    if (scope == ResizeRewardScope::SoleRecipient)
        return bound == 1 && credit == total;
    return scope == ResizeRewardScope::PersonalShareLowerBound && credit == total / bound &&
           credit > 0;
}
inline bool current_resize_contains(const CurrentResizeCycle &p, int id) {
    return std::find(p.ids.begin(), p.ids.begin() + std::clamp(p.count, 0, 6), id) !=
           p.ids.begin() + std::clamp(p.count, 0, 6);
}
inline bool current_resize_valid(const CurrentResizeCycle &p) {
    if (!p.known || !p.sufficient || !p.complete || p.owner < 0 || p.group < 0 || p.round < 0 ||
        p.serial < 0 || p.collector < 0 || p.count < 1 || p.count > 6 || p.capture.x < 0 ||
        p.capture.y < 0 || p.bank.x < 0 || p.bank.y < 0 || !std::isfinite(p.reward_once) ||
        p.reward_once <= 0 || !std::isfinite(p.clear_ticks) || p.clear_ticks < 1 ||
        !std::isfinite(p.capture_ticks) || p.capture_ticks < 0 || !std::isfinite(p.bank_ticks) ||
        p.bank_ticks <= 0 || !std::isfinite(p.recovery_ticks) || p.recovery_ticks < 0 ||
        !std::isfinite(p.duration()) || p.duration() <= 0 ||
        !current_resize_contains(p, p.collector) || !p.collector_conversion_priced ||
        p.recipients != 1 || p.collector_reward != p.reward_once ||
        !current_resize_share_valid(p.reward_once, p.group_gems, p.recipient_bound, p.reward_scope))
        return false;
    for (int k = 0; k < p.count; ++k) {
        if (p.ids[k] < 0)
            return false;
        for (int j = 0; j < k; ++j)
            if (p.ids[k] == p.ids[j])
                return false;
    }
    return true;
}
inline bool current_resize_same_job(const CurrentResizeCycle &a, const CurrentResizeCycle &b) {
    return a.owner == b.owner && a.group == b.group && a.round == b.round && a.serial == b.serial &&
           a.collector == b.collector && a.capture == b.capture && a.bank == b.bank &&
           a.reward_once == b.reward_once && a.group_gems == b.group_gems &&
           a.recipient_bound == b.recipient_bound && a.reward_scope == b.reward_scope;
}
inline bool current_resize_alternative_valid(const CurrentResizeCycle &baseline,
                                             const CurrentResizeAlternative &a, int body) {
    return a.known && a.sufficient && a.complete && a.owner == baseline.owner && a.body == body &&
           a.group >= 0 && a.group != baseline.group && a.round == baseline.round &&
           a.serial == baseline.serial && a.reward_scope == baseline.reward_scope &&
           a.recipient_bound == baseline.recipient_bound && std::isfinite(a.reward_once) &&
           a.reward_once > 0 && std::isfinite(a.complete_ticks) && a.complete_ticks > 0 &&
           std::isfinite(a.rate()) && a.rate() > 0 &&
           current_resize_share_valid(a.reward_once, a.group_gems, a.recipient_bound,
                                      a.reward_scope);
}
inline CurrentResizeDecision compare_current_resize(const CurrentResizeCycle &baseline,
                                                    std::span<const CurrentResizeOption> options,
                                                    double margin = Settings::switch_margin) {
    CurrentResizeDecision out;
    if (!current_resize_valid(baseline) || !current_resize_contains(baseline, baseline.owner) ||
        !std::isfinite(margin) || margin < 1)
        return out;
    out.baseline_known = true;
    const double incumbent_rate = baseline.reward_once / baseline.duration();
    out.keep_value = out.changed_value = incumbent_rate;
    double best_ratio = margin;
    // The producer supplies only a bounded add/self-release pair. Extra
    // options are deliberately ignored; this is not a partition optimizer.
    for (unsigned i = 0; i < std::min<std::size_t>(2, options.size()); ++i) {
        const auto &o = options[i];
        const auto &next = o.cycle;
        if (!current_resize_valid(next) || !current_resize_same_job(baseline, next))
            continue;
        double keep = incumbent_rate, changed = next.reward_once / next.duration();
        if (o.kind == CurrentResizeKind::AddOne) {
            if (next.count != baseline.count + 1)
                continue;
            bool superset = true;
            for (int k = 0; k < baseline.count; ++k)
                superset &= current_resize_contains(next, baseline.ids[k]);
            if (!superset)
                continue;
            int added = -1;
            for (int k = 0; k < next.count; ++k)
                if (!current_resize_contains(baseline, next.ids[k]))
                    added = next.ids[k];
            if (!current_resize_alternative_valid(baseline, o.alternative, added))
                continue;
            keep += o.alternative.rate();
        } else if (o.kind == CurrentResizeKind::ReleaseSelf) {
            if (next.count != baseline.count - 1 || current_resize_contains(next, baseline.owner) ||
                baseline.collector == baseline.owner || next.clear_ticks > baseline.clear_ticks ||
                next.capture_ticks > baseline.capture_ticks ||
                next.bank_ticks > baseline.bank_ticks ||
                next.recovery_ticks > baseline.recovery_ticks ||
                !current_resize_alternative_valid(baseline, o.alternative, baseline.owner))
                continue;
            bool subset = true, lower = false;
            for (int k = 0; k < next.count; ++k) {
                subset &= current_resize_contains(baseline, next.ids[k]);
                lower |= next.ids[k] < baseline.owner;
            }
            if (!subset || !lower)
                continue;
            changed += o.alternative.rate();
        } else
            continue;
        if (!std::isfinite(keep) || !std::isfinite(changed) || keep <= 0)
            continue;
        const double ratio = changed / keep;
        if (ratio > best_ratio) {
            best_ratio = ratio;
            out.option = int(i);
            out.kind = o.kind;
            out.keep_value = keep;
            out.changed_value = changed;
        }
    }
    return out;
}
} // namespace tactics

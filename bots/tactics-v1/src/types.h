#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <optional>
#include <vector>

// Policy data deliberately has no SDK dependency. Tests exercise the same
// rules.
namespace tactics {
struct Pos {
    int x = -1, y = -1;
    bool operator==(const Pos &) const = default;
};
inline int distance(Pos a, Pos b) {
    return std::max(std::abs(a.x - b.x), std::abs(a.y - b.y));
}
inline constexpr int unreachable = 65535;
inline bool packed_bit(const std::vector<std::uint8_t> &bytes, int index) {
    // SDK2.2.2 linear_buffer_size()/native export use packed row-major LSB bits.
    // Some export comments incorrectly say one byte per tile. The native
    // all-tile equivalence fixture, not those comments, pins this contract.
    return index >= 0 && index / 8 < static_cast<int>(bytes.size()) &&
           (bytes[index / 8] & (1u << (index % 8))) != 0;
}
enum class Phase {
    Unassigned,
    Travel,
    Assemble,
    Clear,
    Collect,
    Deliver,
    Channel,
    Recover,
    Reenter,
    Protect,
    Fight,
    Escape,
    Observe
};
enum class Channel { None, Recall, Tribute, Teleport };
enum class Lifecycle { Unknown, Alive, Reward, Respawning };
// Snapshot-local proof dependency. A sufficient basic-only certificate never
// borrows a heal/cast/reset that happens to be available in the current kit.
enum class ClearProofKind { None, BasicOnly, DetailedBundle };
enum class Intent { Farm, Convert, Recover, Contest, Deny, Invade, Escort };
enum class Kind {
    None,
    Move,
    BasicChampion,
    BasicCamp,
    BasicLock,
    CastSelf,
    CastChampion,
    CastCamp,
    CastGround,
    Recall,
    Tribute,
    CancelRecall,
    CancelTribute,
    Ward,
    Buy,
    Sell,
    BuyConsumable,
    UseConsumable
};
enum class Outcome { Rejected, Blocked, Applied, Started, Interrupted, Completed, Stale, LockHit };
enum class Priority { Routine = 0, Incumbent = 1, Survival = 2, Deciding = 3, ActiveChannel = 4 };
struct Action {
    Kind kind = Kind::None;
    Pos at{};
    int target = -1, slot = -1, item = -1, count = 1;
    const char *reason = "no-action";
};
struct Spell {
    int kind = 0, slot = -1, cooldown = -1, recharge = -1, range = 0, radius = 0, duration = 0;
    double amount = 0, scale = 0;
    bool ready = false, exclusive = false, camps = false, enemies = false, allies = false,
         self = false, ground = false;
};
struct Actor {
    int id = -1, type = -1, range = 0, gems = 0, move_speed = 1, priority = 0;
    Pos pos{};
    double hp = 0, max_hp = 1, strength = 0, focus = 0, shield = 0, mitigation = 1,
           camp_mitigation = 1;
    bool home = false, monster = false;
    bool alive = false, can_move = false, can_attack = false, can_cast = false, stunned = false,
         enhanced = false, completed = false;
    Channel channel = Channel::None;
    int channel_ticks = -1, stun_ticks = -1, shield_ticks = -1;
    std::array<Spell, 2> spells{};
    double health_fraction() const {
        return hp / std::max(1.0, max_hp);
    }
};
struct Spawn {
    int id = -1, type = -1;
    Pos pos{};
    double hp = 0, strength = 0;
    int range = 1;
};
struct Group {
    int id = -1, index = -1, gold = 0, gems = 0, respawn = 0;
    std::vector<Spawn> spawns;
    double initial_hp = 0, initial_strength = 0;
    bool monolith = false;
};
struct Camp {
    int id = -1, group = -1, type = -1, range = 1;
    Pos pos{};
    double hp = 0, max_hp = 0, strength = 0;
    bool awake = false;
};
struct GroupView {
    Lifecycle state = Lifecycle::Unknown;
    int seen = -1, respawn_ticks = -1;
    std::vector<Camp> camps;
    std::vector<int> known_dead;
    bool fresh(int round) const {
        return seen == round;
    }
};
// Conservative earliest contact: one possible dash and the widest plausible
// damage/control reach. Combining them can be optimistic for the enemy (one
// cast budget), which is safe for a warning/commit veto, never proof of safety.
inline int possible_contact_reach(const Actor &enemy, int horizon = 8) {
    int reach = enemy.range, dash = 0;
    for (const auto &s : enemy.spells)
        if (s.cooldown < 0 || s.cooldown <= horizon) {
            if (s.kind == 6)
                dash = std::max(dash, s.range);
            if (s.kind == 2 || s.kind == 3 || s.kind == 4)
                reach = std::max(reach, s.range + s.radius);
        }
    return reach + dash;
}
struct Mission {
    Phase phase = Phase::Unassigned;
    Intent intent = Intent::Farm;
    int group = -1, start = -1, expiry = -1, latest = -1, stagnant = 0, last_progress = -1;
    Pos target{}, last_pos{};
    double rate = 0, last_camp_hp = -1;
    double completion_cost = 0;
    double sortie_floor = 0;
    std::array<Pos, 5> sortie_path{};
    int sortie_length = 0;
    bool sortie_exiting = false;
    bool assembly_pending = false;
    std::uint64_t assembly_signature = 0;
    int assembly_anchor = -1, assembly_helper = -1;
    std::array<Pos, 25> assembly_route{};
    int assembly_route_length = 0;
    std::array<int, 6> assembly_ids{};
    int assembly_count = 0;
    std::array<Pos, 25> assembly_exit{};
    int assembly_exit_length = 0;
    bool chain_used = false, bank_after_reward = false;
    // Named continuation survives a bank START; it is entered only after an
    // observed completed conversion, then revalidated by the normal farm gate.
    int bank_altar = -1, bank_reentry_group = -1;
    Pos bank_reentry_target{};
    double bank_reentry_rate = 0;
};
struct Proposal {
    Action action{};
    Mission mission{};
    Priority priority = Priority::Routine;
    double value = 0;
    bool valid = false;
    // Set only by a paid fresh fixed-position solo-clear certificate. This
    // carries its next basic's proof through one accepted native mutation.
    bool solo_clear_certified = false;
    bool crew_clear_certified = false;
    ClearProofKind crew_clear_proof = ClearProofKind::None;
    int crew_proof_owner = -1, crew_proof_round = -1, crew_proof_serial = -1;
};
// Geometry only: no HP, cooldown, quote or future readiness survives here.
struct AssemblyPathHint {
    int actor = -1, range = 0, speed = 0, kind = 0, seen = -1000;
    Pos origin{}, goal{}, start{};
    std::array<Pos, 25> route{};
    int length = 0, touched = 0;
    std::uint32_t borrowed_generation = 0;
};
struct Memory {
    Mission mission{};
    int observed_round = -1, hold_group = -1, hold_since = -1, hold_last = -1;
    int last_damage_round = -1000, last_action_round = -1, last_action_serial = 0;
    int focus = -1, focus_until = -1, channel_attempt_round = -1, ward_attempt_round = -1;
    int last_gold = 0, last_gems = 0, last_bank = -1, last_recall = -1, failed_group = -1,
        failed_until = -1;
    Pos last_pos{}, blocked_tile{};
    int blocked_round = -1, moved_round = -1;
    double last_hp = 0;
    Channel prior_channel = Channel::None;
    bool prior_alive = false;
    // Owner-local route history never certifies another body's future action.
    std::array<Pos, 4> route_history{};
    Pos route_goal{};
    int route_samples = 0, route_round = -1, route_best = unreachable, route_stall = 0;
    int failed_altar = -1, failed_altar_until = -1;
    int failed_bank_altar = -1, failed_bank_until = -1;
    Pos failed_bank_window{};
    std::uint64_t failed_bank_power = 0;
    double upgrade_gain = 0, upgrade_absence = 0;
    bool upgrade_gem_unlock = false;
    int cash_investment_group = -1, cash_investment_until = -1;
    double cash_investment_rate = 0;
    int assembly_failed_group = -1;
    std::uint64_t assembly_failed_signature = 0;
    int assembly_probe_group = -1, assembly_probe_round = -1000;
    std::array<AssemblyPathHint, 12> assembly_paths{};
    int assembly_path_clock = 0;
    std::uint32_t assembly_path_generation = 0;
};
struct Settings {
    // Declared v1 fallbacks/test settings, not fitted performance optima.
    static constexpr int fuel_reserve = 6000, planning_reserve = 24000, max_actions = 10;
    static constexpr int job_lease = 6, assembly_wait = 6, stagnation_limit = 2;
    static constexpr double switch_margin = 1.25, ordinary_heal = .55, spawn_ready = .95;
};
using ClaimBytes = std::array<std::uint8_t, 5>;
inline int decode_claim(const ClaimBytes &bytes, int slot, int roster_size, int group_count) {
    if (slot < 0 || slot >= roster_size)
        return -1;
    int value = 0;
    if (roster_size == 6 && group_count <= 63) {
        std::uint64_t bits = 0;
        for (int k = 0; k < 5; ++k)
            bits |= std::uint64_t(bytes[k]) << (8 * k);
        value = (bits >> (slot * 6)) & 63;
    } else if (slot < 5)
        value = bytes[slot];
    return value > 0 && value <= group_count ? value - 1 : -1;
}
inline std::optional<ClaimBytes> encode_claim(ClaimBytes bytes, int slot, int roster_size,
                                              int group_count, int group) {
    if (slot < 0 || slot >= roster_size)
        return std::nullopt;
    if (roster_size == 6 && group_count <= 63) {
        int value = group >= 0 && group < group_count ? group + 1 : 0;
        std::uint64_t bits = 0;
        for (int k = 0; k < 5; ++k)
            bits |= std::uint64_t(bytes[k]) << (8 * k);
        auto mask = std::uint64_t(63) << (slot * 6);
        bits = (bits & ~mask) | (std::uint64_t(value) << (slot * 6));
        for (int k = 0; k < 5; ++k)
            bytes[k] = (bits >> (8 * k)) & 255;
    } else if (slot < 5)
        bytes[slot] = group >= 0 && group < group_count && group < 255 ? group + 1 : 0;
    else
        return std::nullopt;
    return bytes;
}
inline int tribute_ticks(int bag, double multiplier = .1, int base = 0, int minimum = 1) {
    return std::max(minimum, base + static_cast<int>(std::ceil(bag * multiplier)));
}
inline int overlap_hold(int capture_ticks, int recall_ticks) {
    return std::max(0, capture_ticks + 1 - recall_ticks);
}
inline bool deadline_allows(int round, int walk_turns, int ticks, int limit) {
    return round + walk_turns + ticks < limit; // zero countdown resolves on next owner start.
}
inline bool is_attack(Kind k) {
    return k == Kind::BasicChampion || k == Kind::BasicCamp || k == Kind::BasicLock;
}
inline bool is_cast(Kind k) {
    return k == Kind::CastSelf || k == Kind::CastChampion || k == Kind::CastCamp ||
           k == Kind::CastGround;
}
inline bool is_channel(Kind k) {
    return k == Kind::Recall || k == Kind::Tribute;
}
inline bool choose_new_job(const Mission &old, const Mission &next, int round, bool hard_invalid) {
    if (hard_invalid || old.phase == Phase::Unassigned)
        return true;
    if (old.group == next.group && old.phase == next.phase && old.target == next.target)
        return true;
    if (round < old.expiry)
        return false;
    return next.rate > old.rate * Settings::switch_margin;
}
inline Mission bank_completion_reentry(const Mission &bank, int round, bool completed) {
    Mission next;
    if (!completed || bank.bank_reentry_group < 0 || bank.bank_reentry_target.x < 0 ||
        bank.bank_reentry_target.y < 0 || bank.bank_reentry_rate <= 0)
        return next;
    next.phase = Phase::Reenter;
    next.intent = Intent::Farm;
    next.group = bank.bank_reentry_group;
    next.target = bank.bank_reentry_target;
    next.rate = bank.bank_reentry_rate;
    next.start = next.last_progress = round;
    next.expiry = round + Settings::job_lease;
    return next; // A fresh farm/route/crew check still owns the first action.
}
inline bool retains_channel(Channel channel, bool lethal_before_completion,
                            bool interrupt_before_completion, bool useful_cancel) {
    if (channel == Channel::Teleport)
        return true;
    return !(useful_cancel && (lethal_before_completion || interrupt_before_completion));
}
inline bool may_yield_holder(int self_id, const Actor &other, bool on_region, bool matching_claim) {
    return on_region && matching_claim && other.alive && other.id < self_id &&
           other.channel == Channel::None && other.health_fraction() >= .35;
}
inline const char *phase_name(Phase p) {
    constexpr const char *n[] = {"unassigned", "travel",  "assemble", "clear",   "collect",
                                 "deliver",    "channel", "recover",  "reenter", "protect",
                                 "fight",      "escape",  "observe"};
    return n[static_cast<int>(p)];
}
} // namespace tactics

#pragma once
#include "types.h"
#include <span>

namespace tactics {
// Completing observation resolves missing information, never missing physical
// help. Every original tile and every live member must be in the current
// personal mask; a fresh group lifecycle alone only proves one spawn is seen.
inline bool fully_personally_observed_camp(const Group &group, const GroupView &live,
                                           std::span<const std::uint8_t> visible, int width,
                                           int height, int now) {
    if (now < 0 || !live.fresh(now) || live.state != Lifecycle::Alive || group.spawns.empty() ||
        width <= 0 || height <= 0 || width > 65535 / height ||
        visible.size() < std::size_t((width * height + 7) / 8))
        return false;
    const auto observed = [&](Pos p) {
        if (p.x < 0 || p.y < 0 || p.x >= width || p.y >= height)
            return false;
        const int index = p.y * width + p.x;
        return (visible[std::size_t(index) >> 3] & (1u << (index & 7))) != 0;
    };
    for (const auto &spawn : group.spawns) {
        if (spawn.id < 0 || !observed(spawn.pos))
            return false;
        if (std::find(live.known_dead.begin(), live.known_dead.end(), spawn.id) !=
            live.known_dead.end())
            continue;
        const auto member = std::find_if(live.camps.begin(), live.camps.end(),
                                         [&](const Camp &camp) { return camp.id == spawn.id; });
        if (member == live.camps.end() || member->hp <= 0 || !observed(member->pos))
            return false;
    }
    return true;
}
} // namespace tactics

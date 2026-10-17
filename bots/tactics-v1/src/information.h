#pragma once
#include "types.h"
namespace tactics {
// Version 2 uses only the existing eight shared bytes. Claims keep bytes0..4;
// bytes5..7 are ONE advisory report, never an accepted role/ETA promise.
// x/y each4 normalized-zone bits, absolute round11 bits, severity2, writer3.
// Absolute rounds (match limit2000) cannot alias a stale report on modulo wrap.
struct Warning {
    int x = 0, y = 0, round = -1, severity = 0, writer = -1;
    bool fresh(int now) const {
        return severity > 0 && round >= 0 && now >= round && now - round <= 2;
    }
};
inline std::array<std::uint8_t, 3> encode_warning(Warning w) {
    if (w.round < 0 || w.round > 2047 || w.writer < 0 || w.writer > 5 || w.severity < 1 ||
        w.severity > 3 || w.x < 0 || w.x > 15 || w.y < 0 || w.y > 15)
        return {};
    const std::uint32_t bits =
        w.x | (w.y << 4) | (w.round << 8) | (w.severity << 19) | (w.writer << 21);
    return {std::uint8_t(bits), std::uint8_t(bits >> 8), std::uint8_t(bits >> 16)};
}
inline Warning decode_warning(std::array<std::uint8_t, 3> bytes) {
    const std::uint32_t bits =
        bytes[0] | (std::uint32_t(bytes[1]) << 8) | (std::uint32_t(bytes[2]) << 16);
    return {int(bits & 15), int((bits >> 4) & 15), int((bits >> 8) & 2047), int((bits >> 19) & 3),
            int((bits >> 21) & 7)};
}
inline bool route_phase(Phase phase) {
    return phase == Phase::Travel || phase == Phase::Observe || phase == Phase::Deliver ||
           phase == Phase::Recover || phase == Phase::Reenter;
}
inline bool update_route_progress(Memory &m, Pos current, Pos goal, int remaining, int round) {
    if (m.route_round == round)
        return false;
    if (m.route_goal != goal || !route_phase(m.mission.phase)) {
        m.route_goal = goal;
        m.route_samples = 0;
        m.route_best = remaining;
        m.route_stall = 0;
    }
    const bool progressing = remaining < m.route_best;
    if (progressing) {
        m.route_best = remaining;
        m.route_stall = 0;
    } else
        ++m.route_stall;
    const bool loop = m.route_samples >= 3 && current == m.route_history[1] &&
                      m.route_history[0] == m.route_history[2] && current != m.route_history[0];
    for (int i = 3; i > 0; --i)
        m.route_history[i] = m.route_history[i - 1];
    m.route_history[0] = current;
    ++m.route_samples;
    m.route_round = round;
    return !progressing && (loop || m.route_stall >= 5) && remaining > 0;
}
} // namespace tactics

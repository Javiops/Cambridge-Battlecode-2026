#pragma once
#include <cambc.h>
#include "actions.h"

namespace foundation {
class SdkPort {
    template<class F> static auto call(F function) {
        try { return function(); }
        catch (const cambc::error& e) { throw EngineError{static_cast<int>(e.code())}; }
    }
public:
    std::uint64_t fuel() const { return cambc::fuel_remaining(); }
    std::uint32_t round() const { return cambc::round_number(); }
    Observation read() const {
        const auto start = round();
        auto& self = cambc::self();
        Observation result;
        result.round = start;
        result.alive = self.is_alive();
        if (result.alive) {
            const auto p = self.position();
            result.position = {p.x, p.y};
            const auto flags = self.state();
            if (flags.contains(cambc::champion_state::recalling)) result.channel = Channel::recall;
            else if (flags.contains(cambc::champion_state::submitting_gems)) result.channel = Channel::tribute;
            else if (flags.contains(cambc::champion_state::teleporting)) result.channel = Channel::teleport;
        }
        result.consistent = start == round();
        return result;
    }
    bool move(Tile target) {
        return call([&] { return cambc::self().move_absolute({target.x, target.y}); });
    }
    void recall() { call([] { cambc::self().recall(); }); }
    void tribute(Tile altar) {
        call([&] { cambc::self().submit_gems({altar.x, altar.y}); });
    }
};
} // namespace foundation

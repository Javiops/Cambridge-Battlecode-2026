#pragma once
#include "../planner.h"

namespace foundation::policies {
// 12.5 Action validation and fallbacks: no enabled strategy means hold position.
inline std::optional<Proposal> hold(const Snapshot& snapshot) {
    return Proposal{{Action::wait, snapshot.epoch}, Priority::fallback};
}
} // namespace foundation::policies

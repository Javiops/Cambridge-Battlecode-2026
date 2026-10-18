#pragma once
#include <array>
#include "hold.h"

namespace foundation::policies {
// Add one include and one entry per policy; keep implementations in their own files.
inline constexpr std::array registry{Policy{"12.5.hold", hold}};
} // namespace foundation::policies

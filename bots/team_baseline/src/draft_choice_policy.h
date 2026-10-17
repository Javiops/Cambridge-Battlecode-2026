#pragma once
#include <string_view>
#include <vector>

#ifndef P_DP_PRISM_SWAP
#define P_DP_PRISM_SWAP 0
#endif
static_assert(P_DP_PRISM_SWAP >= 0 && P_DP_PRISM_SWAP <= 2,
              "P_DP_PRISM_SWAP must be 0 (baseline), 1 (Cassi), or 2 (Willow)");

namespace draftchoice {
// Applied after geometry recipes so every recipe has the same final policy.
inline void replace_prism(std::vector<const char*>& preferences) {
#if P_DP_PRISM_SWAP
    for (auto& name : preferences)
        if (std::string_view(name) == "prism")
            name = P_DP_PRISM_SWAP == 1 ? "cassi" : "willow";
#else
    (void)preferences;
#endif
}

// Filter discovered fallbacks too: rejecting/unavailable replacements must not
// silently restore Prism. Names are already normalized by run_draft().
inline bool allowed(std::string_view normalized_name) {
#if P_DP_PRISM_SWAP
    return normalized_name != "prism";
#else
    (void)normalized_name;
    return true;
#endif
}
} // namespace draftchoice
